from typing import TYPE_CHECKING

from .ev_charger import (
    CONTROL_PILOT_CHARGING_V,
    CONTROL_PILOT_IDLE_V,
    CONTROL_PILOT_READY_V,
    MAX_CURRENT_A,
    NOMINAL_VOLTAGE_V,
    PILOT_DUTY_PERCENT_PER_A,
    ChargerReadout,
    ChargerState,
)
from .faults import (
    MAX_PACKS,
    REGISTERS,
    Equipment,
    FaultState,
    fault_word_key,
    pack_key,
)
from .ledger import PERIODS, EnergyLedger
from .plant import ENERGY_FLOWS, MAX_STRINGS, Plant

if TYPE_CHECKING:
    from collections.abc import Mapping

PHASE_NAMES = ("r", "s", "t")
POWER_FACTOR = 0.989
PV_VOLTAGE_V = 290.0
PERCENT = 100.0
SECONDS_PER_MINUTE = 60
FULL_HEALTH = 100.0
SINK_TEMP_BASE_C = 35.0
SINK_TEMP_RISE_C = 15.0
AMBIENT_TEMP_C = 28.0
BUS_VOLTAGE_V = 700.0
MAX_MODULES = 4
BATTERY_BASE_TEMP_C = 24.0
BATTERY_TEMP_RISE_C = 8.0
SECOND_PHASE_NUMBER = 2
FIRST_PHASE_ONLY = 1
GRID_SIDE_GROUPS = frozenset({"grid", "side", "gridload"})
PARALLEL_FLOWS = (
    "pv_w",
    "battery_w",
    "grid_export_w",
    "load_w",
    "backup_w",
    "grid_load_w",
)
MODE_RUNNING = 2
MODE_WAITING = 1
MODE_OFF_GRID = 3
MODE_FAULT = 5
MIN_EV_CURRENT_A = 6.0


def _sign(*, value: float) -> float:
    return float(value > 0) - float(value < 0)


def _amps(*, power_w: float, volts: float) -> float:
    return power_w / volts if volts else 0.0


def _phase_values(
    *,
    prefix: str,
    sample: Mapping[str, float],
    weights: tuple[float, ...],
    grid_connected: bool,
) -> dict[str, float]:
    out: dict[str, float] = {}
    sources = {
        "grid": sample["grid_w"],
        "inv": sample["inverter_w"],
        "out": sample["backup_w"],
        "side": max(sample["inverter_w"], 0.0),
        "load": sample["load_w"],
        "gridload": max(sample["grid_w"], 0.0),
        "meter_a": sample["grid_w"],
        "meter_b": sample["ext_pv_w"],
    }
    for index, weight in enumerate(weights):
        name = PHASE_NAMES[index]
        for group, total in sources.items():
            energised = grid_connected or group not in GRID_SIDE_GROUPS
            volts = sample[f"voltage_{index}_v"] if energised else 0.0
            watts = total * weight if energised else 0.0
            out[f"{prefix}{group}_{name}_w"] = watts
            out[f"{prefix}{group}_{name}_v"] = volts
            out[f"{prefix}{group}_{name}_a"] = _amps(power_w=watts, volts=volts)
            out[f"{prefix}{group}_{name}_va"] = abs(watts) / POWER_FACTOR
            out[f"{prefix}{group}_{name}_hz"] = (
                sample["frequency_hz"] if energised else 0.0
            )
            out[f"{prefix}{group}_{name}_pf"] = POWER_FACTOR if energised else 0.0
            out[f"{prefix}{group}_{name}_dc"] = 0.0
    return out


def _totals(
    *, prefix: str, sample: Mapping[str, float], soc: float, pack_v: float, rated: float
) -> dict[str, float]:
    battery_w = sample["battery_w"]
    out = {
        f"{prefix}pv_w": sample["pv_w"],
        f"{prefix}load_w": sample["load_w"],
        f"{prefix}battery_w": battery_w,
        f"{prefix}grid_w": sample["grid_w"],
        f"{prefix}inverter_w": sample["inverter_w"],
        f"{prefix}ext_pv_w": sample["ext_pv_w"],
        f"{prefix}backup_w": sample["backup_w"],
        f"{prefix}grid_load_w": max(sample["grid_w"], 0.0),
        f"{prefix}soc_percent": soc * PERCENT,
        f"{prefix}battery_v": pack_v,
        f"{prefix}battery_a": _amps(power_w=battery_w, volts=pack_v),
        f"{prefix}battery_temp_c": BATTERY_BASE_TEMP_C
        + BATTERY_TEMP_RISE_C * min(1.0, abs(battery_w) / rated),
    }
    for index in range(1, MAX_STRINGS + 1):
        watts = sample[f"pv{index}_w"]
        voltage = PV_VOLTAGE_V if watts > 0 else 0.0
        out[f"{prefix}pv{index}_w"] = watts
        out[f"{prefix}pv{index}_v"] = voltage
        out[f"{prefix}pv{index}_a"] = _amps(power_w=watts, volts=voltage)
    return out


def _energy(
    *, ledger: EnergyLedger, weights: tuple[float, ...], inverters: int
) -> dict[str, float]:
    out: dict[str, float] = {}
    for flow in ENERGY_FLOWS:
        for period in PERIODS:
            kwh = ledger.kwh(flow=flow, period=period)
            out[f"{flow}_{period}_kwh"] = kwh
            out[f"parallel_{flow}_{period}_kwh"] = kwh * inverters
    for period in PERIODS:
        for flow in ("sell", "feed_in"):
            kwh = ledger.kwh(flow=flow, period=period)
            out[f"sum_{flow}_{period}_kwh"] = kwh
            for index, weight in enumerate(weights[1:], start=SECOND_PHASE_NUMBER):
                out[f"{flow}_phase{index}_{period}_kwh"] = kwh * weight
    return out


def _modules(*, plant: Plant, battery_w: float) -> dict[str, float]:
    bank = plant.battery
    out: dict[str, float] = {}
    for index in range(1, MAX_MODULES + 1):
        present = index <= bank.modules
        share = battery_w / bank.modules if present else 0.0
        voltage = bank.pack_voltage_v() if present else 0.0
        out[f"module{index}_soc_percent"] = bank.soc * PERCENT if present else 0.0
        out[f"module{index}_soh_percent"] = FULL_HEALTH if present else 0.0
        out[f"module{index}_v"] = voltage
        out[f"module{index}_a"] = _amps(power_w=share, volts=voltage)
        out[f"module{index}_temp_c"] = (
            bank.temperature_c(
                power_w=share, rated_power_w=float(plant.scenario.device.rated_power_w)
            )
            if present
            else 0.0
        )
        out[f"module{index}_cycles"] = float(bank.cycles()) if present else 0.0
        discharged_kwh = int(
            plant.ledger.kwh(flow="bat_discharge", period="total")
            / max(bank.modules, 1)
        )
        out[f"module{index}_discharge_kwh_high"] = (
            float(discharged_kwh >> HIGH_WORD_SHIFT) if present else 0.0
        )
        out[f"module{index}_discharge_kwh_low"] = (
            float(discharged_kwh & LOW_WORD_MASK) if present else 0.0
        )
    return out


def _ev(*, readout: ChargerReadout, installed: bool) -> dict[str, float]:
    state = readout.state
    amps = readout.power_w / (NOMINAL_VOLTAGE_V * readout.phases)
    pilot = {
        ChargerState.CHARGING: CONTROL_PILOT_CHARGING_V,
        ChargerState.IDLE: CONTROL_PILOT_IDLE_V,
    }.get(state, CONTROL_PILOT_READY_V)
    out = {
        "ev_state": float(state),
        "ev_power_w": readout.power_w,
        "ev_session_wh": readout.session_energy_wh,
        "ev_total_wh": readout.total_energy_wh,
        "ev_session_start_s": float(readout.session_start_s),
        "ev_session_end_s": float(readout.session_end_s),
        "ev_session_minutes": float(readout.session_seconds // SECONDS_PER_MINUTE),
        "ev_cp_v": pilot,
        "ev_duty_percent": min(amps, MAX_CURRENT_A) * PILOT_DUTY_PERCENT_PER_A,
        "ev_set_current_a": readout.max_power_w / (NOMINAL_VOLTAGE_V * readout.phases),
        "ev_on": float(state is ChargerState.CHARGING),
        "ev_installed": float(installed),
    }
    for index, name in enumerate(PHASE_NAMES):
        active = index < readout.phases
        out[f"ev_{name}_v"] = NOMINAL_VOLTAGE_V if active else 0.0
        out[f"ev_{name}_a"] = amps if active else 0.0
    return out


def _silence_absent_meters(
    *, out: dict[str, float], meter_a: bool, meter_b: bool
) -> None:
    for name, present in (("meter_a_", meter_a), ("meter_b_", meter_b)):
        if present:
            continue
        for key in out:
            if key.startswith(name):
                out[key] = 0.0


def operating_mode(*, plant: Plant) -> float:
    if plant.stopped:
        return float(MODE_FAULT)
    if not plant.online:
        return float(MODE_WAITING)
    return float(MODE_RUNNING if plant.grid_connected else MODE_OFF_GRID)


def _fault_words(*, faults: FaultState) -> dict[str, float]:
    """Every fault register and pack word, from the equipment's fault state."""
    out = {
        fault_word_key(register=register): float(faults.word(register=register))
        for registers in REGISTERS.values()
        for register in registers
    }
    for number in range(1, MAX_PACKS + 1):
        codes = faults.pack(number=number)
        out[pack_key(pack=number, kind="fault")] = float(codes.fault)
        out[pack_key(pack=number, kind="warning")] = float(codes.warning)
    out["fault_count"] = float(len(faults.bits(equipment=Equipment.INVERTER)))
    return out


def build_telemetry(*, plant: Plant) -> dict[str, float]:
    scenario = plant.scenario
    rated = float(scenario.device.rated_power_w)
    soc = plant.battery.soc
    pack_v = plant.battery.pack_voltage_v() if plant.battery.modules else 0.0
    sample = plant.sample
    out = _totals(prefix="", sample=sample, soc=soc, pack_v=pack_v, rated=rated)
    grid_connected = plant.grid_connected
    out.update(
        _phase_values(
            prefix="",
            sample=sample,
            weights=plant.weights,
            grid_connected=grid_connected,
        )
    )
    out.update(
        _phase_values(
            prefix="avg_",
            sample=plant.averaged,
            weights=plant.weights,
            grid_connected=grid_connected,
        )
    )
    out.update(
        _totals(
            prefix="avg_",
            sample=plant.averaged,
            soc=plant.averaged["soc"],
            pack_v=pack_v,
            rated=rated,
        )
    )
    meter_a = plant.meter_a_online
    _silence_absent_meters(out=out, meter_a=meter_a, meter_b=scenario.meters.meter_b)
    out["meter_a_status"] = float(meter_a)
    out["meter_b_status"] = float(scenario.meters.meter_b)
    out["ct_grid_w"] = sample["grid_w"] if meter_a else 0.0
    out["grid_export_w"] = -sample["grid_w"]
    out.update(
        _energy(
            ledger=plant.ledger,
            weights=plant.weights,
            inverters=scenario.parallel.inverters,
        )
    )
    out.update(_modules(plant=plant, battery_w=sample["battery_w"]))
    out.update(_ev(readout=plant.ev.readout(), installed=scenario.ev_charger.installed))
    inverters = scenario.parallel.inverters
    for name in PARALLEL_FLOWS:
        out[f"parallel_{name}"] = out[name] * inverters
    out["parallel_soc_percent"] = out["soc_percent"]
    out["parallel_capacity_ah"] = float(plant.battery.capacity_ah * inverters)
    out["battery_capacity_ah"] = float(plant.battery.capacity_ah)
    out["direction_pv"] = float(sample["pv_w"] > 0)
    out["direction_battery"] = _sign(value=sample["battery_w"])
    out["direction_grid"] = _sign(value=out["grid_export_w"])
    out["direction_output"] = 1.0
    out["clock_s"] = float(plant.second)
    out["operating_mode"] = operating_mode(plant=plant)
    out["conn_time_s"] = float(plant.restart_remaining_s)
    out["sink_temp_c"] = SINK_TEMP_BASE_C + SINK_TEMP_RISE_C * min(
        1.0, abs(sample["inverter_w"]) / rated
    )
    out["ambient_temp_c"] = AMBIENT_TEMP_C
    out["bus_v"] = BUS_VOLTAGE_V
    out.update(_fault_words(faults=plant.faults))
    out["frequency_hz"] = sample["frequency_hz"]
    out["ac_phase_count"] = float(len(plant.weights))
    out["zero"] = 0.0
    out.update(_derived_keys(plant=plant, out=out))
    return out


LOW_WORD_MASK = 0xFFFF
BATTERY_CONTROLLERS = 2
HIGH_WORD_SHIFT = 16
PROTECT_HIGH_RATIO = 1.1
WARN_LOW_RATIO = 0.85
CHARGE_RATIO = 1.05
CUTOFF_RATIO = 0.8
USABLE_RATIO = 0.9


def _derived_keys(*, plant: Plant, out: Mapping[str, float]) -> dict[str, float]:
    bank = plant.battery
    derived: dict[str, float] = {}
    for name in PARALLEL_FLOWS:
        value = int(out[f"parallel_{name}"])
        derived[f"parallel_{name}_low"] = float(value & LOW_WORD_MASK)
        derived[f"parallel_{name}_high"] = float(value >> HIGH_WORD_SHIFT)
    nominal = bank.pack_voltage_v() if bank.modules else 0.0
    rated = float(plant.scenario.device.rated_power_w)
    derived["battery_modules"] = float(bank.modules)
    derived["battery_half_a"] = out["battery_a"] / BATTERY_CONTROLLERS
    derived["battery_user_capacity_ah"] = bank.capacity_ah * USABLE_RATIO
    derived["battery_online_mask"] = float((1 << bank.modules) - 1)
    derived["battery_protect_high_v"] = nominal * PROTECT_HIGH_RATIO
    derived["battery_warn_low_v"] = nominal * WARN_LOW_RATIO
    derived["battery_charge_v"] = nominal * CHARGE_RATIO
    derived["battery_cutoff_v"] = nominal * CUTOFF_RATIO
    derived["battery_current_limit_a"] = (
        bank.power_limit_w(rated_power_w=rated) / nominal if nominal else 0.0
    )
    charger = plant.scenario.ev_charger
    derived["ev_phases"] = float(charger.phases)
    derived["ev_min_power_w"] = MIN_EV_CURRENT_A * NOMINAL_VOLTAGE_V * charger.phases
    derived["ev_max_power_w"] = float(charger.max_power_w)
    return derived
