import dataclasses
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from saj_modbus_mock.registers import EPOCH

from . import control
from .balance import BalanceInput, BalanceResult, solve_balance
from .battery import BatteryBank
from .control import Command, Controller, Settings, SiteContext
from .environment import (
    Environment,
    EnvironmentSample,
    LoadConfig,
    ParameterSpec,
    Variation,
    grid_frequency_hz,
    grid_voltage_v,
    phase_weights,
)
from .ev_charger import EvCharger, HandState
from .faults import Effect, FaultBit, FaultState, active_effects
from .ledger import EnergyLedger

if TYPE_CHECKING:
    from collections.abc import Mapping

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
HOLD_PV = "pv_w"
HOLD_LOAD = "load_w"
HOLD_VOLTAGE = "voltage_v"
HOLD_FREQUENCY = "frequency_hz"
HOLD_PARAMETERS = (
    ParameterSpec(HOLD_PV, "PV power", "Holds", 0, 50_000, 100, "W"),
    ParameterSpec(HOLD_LOAD, "Household load", "Holds", 0, 50_000, 100, "W"),
    ParameterSpec(HOLD_VOLTAGE, "Grid voltage", "Holds", 100, 300, 1, "V"),
    ParameterSpec(HOLD_FREQUENCY, "Grid frequency", "Holds", 45, 65, 0.1, "Hz"),
)
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


def _split_pv(*, strings: tuple[float, ...], held_w: float) -> tuple[float, ...]:
    """Spread a held total over the strings in the proportions they would produce."""
    if not strings:
        return strings
    total = sum(strings)
    if not total:
        return tuple(held_w / len(strings) for _ in strings)
    return tuple(power * held_w / total for power in strings)


class Plant:
    def __init__(
        self,
        *,
        scenario: Scenario,
        settings: Settings,
        fault_effects: Mapping[FaultBit, frozenset[Effect]],
    ) -> None:
        self.scenario = scenario
        self.settings = settings
        spec = scenario.device.model
        self._fault_effects = fault_effects
        self.second = epoch_seconds(moment=scenario.simulation.start)
        self.seed = scenario.simulation.seed
        self.variation = scenario.variation
        self.load = scenario.site.load
        self.holds: dict[str, float] = {}
        self.faults = scenario.faults
        self.weights: tuple[float, ...]
        self.environment: Environment
        self._rebuild_environment()
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

    def _rebuild_environment(self) -> None:
        scenario = self.scenario
        self.weights = phase_weights(
            seed=self.seed,
            phases=scenario.device.model.phases,
            variation=self.variation,
        )
        self.environment = Environment(
            seed=self.seed,
            string_peaks_w=scenario.site.pv_strings,
            load=self.load,
            variation=self.variation,
        )

    def _invalidate(self) -> None:
        """Evaluate again from the current second, so a change shows at once."""
        self._pending = None

    @property
    def effects(self) -> frozenset[Effect]:
        return active_effects(state=self.faults, effects=self._fault_effects)

    @property
    def stopped(self) -> bool:
        return Effect.INVERTER_STOP in self.effects

    @property
    def grid_connected(self) -> bool:
        return self.scenario.site.grid_connected and (
            Effect.GRID_LOST not in self.effects
        )

    @property
    def meter_a_online(self) -> bool:
        return (
            self.scenario.meters.meter_a
            and self.grid_connected
            and Effect.METER_A_LOST not in self.effects
        )

    def _online_at(self, *, second: int) -> bool:
        return not self.stopped and second >= self.restart_until

    @property
    def online(self) -> bool:
        return self._online_at(second=self.second)

    def tune(self, *, seed: int, variation: Variation, load: LoadConfig) -> None:
        """Change the random generators. The battery, counters and clock carry on."""
        self.seed = seed
        self.variation = variation
        self.load = load
        self._rebuild_environment()
        self._invalidate()

    def hold(self, *, holds: Mapping[str, float]) -> None:
        self.holds = dict(holds)
        self._invalidate()

    def set_faults(self, *, faults: FaultState) -> None:
        self.faults = faults
        self._invalidate()

    def set_soc(self, *, soc: float) -> None:
        self.battery.soc = soc
        self._invalidate()

    def plug_ev(self, *, energy_needed_wh: int) -> None:
        self.ev.plug_in(energy_needed_wh=energy_needed_wh, moment=self.moment())
        self._invalidate()

    def unplug_ev(self) -> None:
        self.ev.unplug(moment=self.moment())
        self._invalidate()

    def restore_ev(self, *, state: HandState) -> None:
        self.ev.restore_hand_state(state=state, moment=self.moment())
        self._invalidate()

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

    def _held(self, *, env: EnvironmentSample) -> EnvironmentSample:
        """Replace the generated readings the user holds, before the balance."""
        strings = env.string_powers_w
        if HOLD_PV in self.holds:
            strings = _split_pv(strings=strings, held_w=self.holds[HOLD_PV])
        return dataclasses.replace(
            env,
            string_powers_w=strings,
            load_w=self.holds.get(HOLD_LOAD, env.load_w),
        )

    def _battery_limits(self, *, command: Command) -> tuple[float, float]:
        effects = self.effects
        charge_w = 0.0
        if Effect.NO_CHARGE not in effects:
            charge_w = self.battery.max_charge_w(
                ceiling_soc=command.ceiling_soc,
                rated_power_w=self._rated_power_w,
                dt_s=INTEGRATION_STEP_S,
            )
        discharge_w = 0.0
        if Effect.NO_DISCHARGE not in effects:
            discharge_w = self.battery.max_discharge_w(
                floor_soc=command.floor_soc,
                rated_power_w=self._rated_power_w,
                dt_s=INTEGRATION_STEP_S,
            )
        return charge_w, discharge_w

    def _evaluate(self, *, second: int, commit: bool) -> Evaluation:
        moment = EPOCH + timedelta(seconds=second)
        grid_connected = self.grid_connected
        env = self._held(env=self.environment.sample(moment=moment, second=second))
        pv_available = sum(env.string_powers_w)
        external = (
            env.external_pv_w
            if self.scenario.meters.meter_b and grid_connected
            else 0.0
        )
        ev_w = self.ev.evaluate(
            moment=moment,
            surplus_w=max(0.0, pv_available - env.load_w),
            step_s=INTEGRATION_STEP_S,
            stopped=Effect.EV_STOP in self.effects,
        )
        demand = env.load_w + ev_w
        command = self.controller.command(
            moment=moment,
            second=second,
            soc=self.battery.soc,
            grid_connected=grid_connected,
            meter_a_online=self.meter_a_online,
        )
        shedding = not grid_connected and self._shedding_at(
            pv_w=pv_available, load_w=demand
        )
        if commit and not grid_connected:
            self.shedding = shedding
        max_charge_w, max_discharge_w = self._battery_limits(command=command)
        result = solve_balance(
            inputs=BalanceInput(
                pv_available_w=pv_available,
                external_pv_w=external,
                demand_w=demand,
                command=command,
                grid_connected=grid_connected,
                online=self._online_at(second=second),
                max_charge_w=max_charge_w,
                max_discharge_w=max_discharge_w,
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
            "backup_w": result.load_w if not self.grid_connected else 0.0,
            "soc": self.battery.soc,
            "curtailed_w": result.curtailed_w,
            "shed_w": result.shed_w,
            "frequency_hz": self.holds.get(
                HOLD_FREQUENCY,
                grid_frequency_hz(
                    seed=self.seed, second=second, variation=self.variation
                ),
            ),
        }
        for index in range(1, MAX_STRINGS + 1):
            installed = index <= len(env_strings)
            sample[f"pv{index}_w"] = (
                env_strings[index - 1] * share if installed else 0.0
            )
        for phase in range(len(self.weights)):
            sample[f"voltage_{phase}_v"] = self.holds.get(
                HOLD_VOLTAGE,
                grid_voltage_v(
                    seed=self.seed,
                    second=second,
                    phase=phase,
                    variation=self.variation,
                ),
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
