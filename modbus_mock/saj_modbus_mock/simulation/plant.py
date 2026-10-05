import dataclasses
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from saj_modbus_mock.registers import EPOCH

from . import control
from .balance import BalanceInput, BalanceResult, solve_balance
from .battery import BatteryBank
from .control import Controller, Settings, SiteContext
from .environment import (
    Environment,
    EnvironmentSample,
    grid_frequency_hz,
    grid_voltage_v,
    phase_weights,
)
from .ev_charger import EvCharger
from .ledger import EnergyLedger

if TYPE_CHECKING:
    from saj_modbus_mock.scenario import Scenario

# Integrated state moves in steps this long, aligned to the simulated clock.
INTEGRATION_STEP_S = 10
AVERAGE_WINDOW_S = 300
PERCENT = 100.0
RESTART_SECONDS = 30
SHED_RECOVERY_MARGIN = 0.02
INITIAL_TOTAL_BASE_WH = 800_000.0
INITIAL_TOTAL_SPREAD_WH = 1_200_000.0
# Spread flows over distinct lifetime totals without a random source.
TOTAL_SPREAD_MULTIPLIER = 37
TOTAL_SPREAD_STEPS = 11
ENERGY_FLOWS = (
    "pv",
    "bat_charge",
    "bat_discharge",
    "load",
    "backup_load",
    "sell",
    "feed_in",
    "ext_pv",
    "ev",
    "pv_hours",
    "pv_1",
    "pv_2",
    "pv_3",
    "pv_4",
)
MAX_STRINGS = 4
# Integrating 1000 W for one second adds 1/3600 kWh, so this flow counts hours.
GENERATING_HOUR_RATE = 1000.0


def epoch_seconds(*, moment: datetime) -> int:
    return int((moment - EPOCH).total_seconds())


@dataclasses.dataclass(frozen=True, slots=True)
class Evaluation:
    """What the plant does at one instant, given the integrated state."""

    sample: dict[str, float]
    ev_w: float
    shedding: bool


def _aligned(*, second: int) -> int:
    return second - second % INTEGRATION_STEP_S


class Plant:
    def __init__(self, *, scenario: Scenario, settings: Settings) -> None:
        self.scenario = scenario
        self.settings = settings
        spec = scenario.device.model
        site = scenario.site
        self.second = epoch_seconds(moment=scenario.simulation.start)
        self.weights = phase_weights(seed=scenario.simulation.seed, phases=spec.phases)
        self.environment = Environment(
            seed=scenario.simulation.seed,
            string_peaks_w=site.pv_strings,
            load_base_w=site.load.base_w,
            load_peak_w=site.load.peak_w,
        )
        battery = scenario.battery
        self.battery = BatteryBank(
            modules=battery.modules,
            module_capacity_ah=battery.module_capacity_ah,
            pack_voltage_v=spec.battery_pack_voltage_v,
            initial_soc=battery.initial_soc_percent / PERCENT,
        )
        self.controller = Controller(
            settings=settings,
            context=SiteContext(
                rated_power_w=float(scenario.device.rated_power_w),
                grid_connected=site.grid_connected,
                has_meter_a=scenario.meters.meter_a,
                inverters=scenario.parallel.inverters,
            ),
        )
        self.ev = EvCharger(config=scenario.ev_charger, settings=settings)
        self.ledger = EnergyLedger(
            initial_totals_wh={
                flow: INITIAL_TOTAL_BASE_WH
                + INITIAL_TOTAL_SPREAD_WH
                * ((index * TOTAL_SPREAD_MULTIPLIER) % TOTAL_SPREAD_STEPS)
                / TOTAL_SPREAD_STEPS
                for index, flow in enumerate(ENERGY_FLOWS)
            },
            moment=self.moment(),
        )
        self.fault_bits = scenario.faults.inverter_fault_bits
        self.restart_until = 0
        self.shedding = False
        self.sample: dict[str, float]
        self._rated_power_w = float(scenario.device.rated_power_w)
        self._boundary = 0
        self._pending: Evaluation | None = None
        self._published: dict[str, float] | None = None
        self._window_sum: dict[str, float] = {}
        self._window_count = 0

    def moment(self) -> datetime:
        return EPOCH + timedelta(seconds=self.second)

    def _online_at(self, *, second: int) -> bool:
        return not self.fault_bits and second >= self.restart_until

    @property
    def online(self) -> bool:
        return self._online_at(second=self.second)

    @property
    def restart_remaining_s(self) -> int:
        return max(0, self.restart_until - self.second)

    def restart(self) -> None:
        self.restart_until = self.second + RESTART_SECONDS

    def jump_to(self, *, moment: datetime) -> None:
        self.second = epoch_seconds(moment=moment)
        self.ledger.align(moment=moment)
        self._pending = None
        self._published = None
        self._window_sum = {}
        self._window_count = 0

    def advance(self, *, moment: datetime) -> None:
        """Integrate to the last step boundary, then report the exact instant."""
        target = epoch_seconds(moment=moment)
        if self._pending is None:
            self._boundary = _aligned(second=self.second)
            self._pending = self._evaluate(second=self._boundary, commit=True)
        last_boundary = _aligned(second=target)
        while self._boundary < last_boundary:
            self._pending = self._integrate_step(evaluation=self._pending)
        self.second = target
        self.sample = self._evaluate(second=target, commit=False).sample

    @property
    def averaged(self) -> dict[str, float]:
        """Mean of the previous complete window, or of the steps so far."""
        if self._published is not None:
            return self._published
        if not self._window_count:
            return self.sample
        return self._window_mean()

    def _window_mean(self) -> dict[str, float]:
        return {
            key: value / self._window_count for key, value in self._window_sum.items()
        }

    def _shedding_at(self, *, pv_w: float, load_w: float) -> bool:
        floor = control.DISCHARGE_FLOOR_OFF_GRID
        lower = float(self.settings.get(floor, 0)) / PERCENT
        if not self.battery.modules:
            return pv_w < load_w
        if self.battery.soc <= lower and pv_w < load_w:
            return True
        if self.battery.soc > lower + SHED_RECOVERY_MARGIN:
            return False
        return self.shedding

    def _evaluate(self, *, second: int, commit: bool) -> Evaluation:
        moment = EPOCH + timedelta(seconds=second)
        site = self.scenario.site
        env = self.environment.sample(moment=moment, second=second)
        pv_available = sum(env.string_powers_w)
        external = (
            env.external_pv_w
            if self.scenario.meters.meter_b and site.grid_connected
            else 0.0
        )
        ev_w = self.ev.evaluate(
            moment=moment,
            surplus_w=max(0.0, pv_available - env.load_w),
            step_s=INTEGRATION_STEP_S,
        )
        demand = env.load_w + ev_w
        command = self.controller.command(
            moment=moment, second=second, soc=self.battery.soc
        )
        shedding = not site.grid_connected and self._shedding_at(
            pv_w=pv_available, load_w=demand
        )
        if commit and not site.grid_connected:
            self.shedding = shedding
        result = solve_balance(
            inputs=BalanceInput(
                pv_available_w=pv_available,
                external_pv_w=external,
                demand_w=demand,
                command=command,
                grid_connected=site.grid_connected,
                online=self._online_at(second=second),
                max_charge_w=self.battery.max_charge_w(
                    ceiling_soc=command.ceiling_soc,
                    rated_power_w=self._rated_power_w,
                    dt_s=INTEGRATION_STEP_S,
                ),
                max_discharge_w=self.battery.max_discharge_w(
                    floor_soc=command.floor_soc,
                    rated_power_w=self._rated_power_w,
                    dt_s=INTEGRATION_STEP_S,
                ),
                pack_voltage_v=self.battery.pack_voltage_v(),
                shedding=shedding,
            ),
        )
        return Evaluation(
            sample=self._sample_of(
                second=second,
                env=env,
                external=external,
                ev_w=ev_w,
                result=result,
            ),
            ev_w=ev_w,
            shedding=shedding,
        )

    def _sample_of(
        self,
        *,
        second: int,
        env: EnvironmentSample,
        external: float,
        ev_w: float,
        result: BalanceResult,
    ) -> dict[str, float]:
        seed = self.scenario.simulation.seed
        env_strings = env.string_powers_w
        pv_available = sum(env_strings)
        share = result.pv_w / pv_available if pv_available else 0.0
        sample = {
            "pv_w": result.pv_w,
            "ext_pv_w": external,
            "load_w": result.load_w,
            "battery_w": result.battery_w,
            "grid_w": result.grid_w,
            "inverter_w": result.pv_w + result.battery_w,
            "ev_w": ev_w,
            "backup_w": (
                result.load_w if not self.scenario.site.grid_connected else 0.0
            ),
            "soc": self.battery.soc,
            "curtailed_w": result.curtailed_w,
            "shed_w": result.shed_w,
            "frequency_hz": grid_frequency_hz(seed=seed, second=second),
        }
        for index in range(1, MAX_STRINGS + 1):
            installed = index <= len(env_strings)
            sample[f"pv{index}_w"] = (
                env_strings[index - 1] * share if installed else 0.0
            )
        for phase in range(len(self.weights)):
            sample[f"voltage_{phase}_v"] = grid_voltage_v(
                seed=seed, second=second, phase=phase
            )
        return sample

    def _integrate_step(self, *, evaluation: Evaluation) -> Evaluation:
        """Apply the step that starts at the boundary and evaluate the next one."""
        sample = evaluation.sample
        moment = EPOCH + timedelta(seconds=self._boundary)
        self.battery.apply(power_w=sample["battery_w"], dt_s=INTEGRATION_STEP_S)
        self.ev.integrate(power_w=evaluation.ev_w, step_s=INTEGRATION_STEP_S)
        self.ledger.add(
            flows_w=self._ledger_flows(sample=sample),
            dt_s=INTEGRATION_STEP_S,
            moment=moment,
        )
        for key, value in sample.items():
            self._window_sum[key] = self._window_sum.get(key, 0.0) + value
        self._window_count += 1
        self._boundary += INTEGRATION_STEP_S
        if self._boundary % AVERAGE_WINDOW_S == 0:
            self._published = self._window_mean()
            self._window_sum = {}
            self._window_count = 0
        return self._evaluate(second=self._boundary, commit=True)

    @staticmethod
    def _ledger_flows(*, sample: dict[str, float]) -> dict[str, float]:
        flows = {
            "pv": sample["pv_w"],
            "bat_charge": max(-sample["battery_w"], 0.0),
            "bat_discharge": max(sample["battery_w"], 0.0),
            "load": sample["load_w"],
            "backup_load": sample["backup_w"],
            "sell": max(-sample["grid_w"], 0.0),
            "feed_in": max(sample["grid_w"], 0.0),
            "ext_pv": sample["ext_pv_w"],
            "ev": sample["ev_w"],
            "pv_hours": GENERATING_HOUR_RATE if sample["pv_w"] > 0 else 0.0,
        }
        for index in range(1, MAX_STRINGS + 1):
            flows[f"pv_{index}"] = sample[f"pv{index}_w"]
        return flows
