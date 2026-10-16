import dataclasses
import math
import time
from datetime import UTC, date, datetime, timedelta
from typing import TYPE_CHECKING, Any

from . import profiles
from .clock import Clock
from .description import (
    EV_DEFAULT_ENERGY_WH,
    EV_ENERGY_BOUNDS,
    HOUSEHOLD_LOAD,
    OPERATING_MODES,
    SOC_BOUNDS,
    SPEED_BOUNDS,
    LastRead,
    applicable_cards,
    available_fields,
    card_readings,
    changed_settings,
    changed_variation,
    describe_cards,
    describe_commands,
    describe_faults,
    describe_holds,
    describe_link,
    describe_model,
    describe_nodes,
    describe_presets,
    describe_settings,
    describe_variation,
    fault_counts,
    faults_state,
    held_names,
    hold_readings,
    hold_values,
    is_setting,
    never_read,
    node_readings,
    register_snapshot,
    rounded,
    settings_state,
    variation_values,
    with_household_load,
)
from .device import Device, initial_settings
from .exceptions import ControlError
from .link import (
    ADDRESS_BOUNDS,
    CODE_BOUNDS,
    LINK_PARAMETERS,
    REFUSED_BLOCKS,
    Kind,
    Link,
    LinkSettings,
    LockoutState,
    RefusedBlock,
    changed_link,
    check_combination,
    link_values,
)
from .presets import Fitted, Needs, Preset, available_presets
from .profiles.common import CLEAR_CURRENT_FAULT
from .registers import EPOCH, Field, FieldValue
from .scenario import PERCENT_MAX, dump_scenario
from .simulation import control as ctl
from .simulation.environment import (
    LOAD_BASE,
    LOAD_PEAK,
    PARAMETERS_BY_NAME,
    SEED,
    SEED_PARAMETER,
    VARIATION_PARAMETERS,
    LoadConfig,
    ParameterError,
    Variation,
    checked_parameter,
)
from .simulation.ev_charger import ChargerState, HandState
from .simulation.faults import (
    WORD_MAXIMUM,
    Equipment,
    FaultBit,
    FaultState,
    PackCodes,
)
from .simulation.ledger import STARTED_PERIODS
from .simulation.plant import HOLD_PARAMETERS, PERCENT, Plant
from .simulation.telemetry import build_telemetry

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from .device import Block
    from .scenario import BatteryConfig, Scenario

COMMAND_CLEAR_FAULTS = "cmd_clear_faults"
COMMAND_RESTART = "cmd_restart"
COMMAND_CLEAR_POWER_HISTORY = "cmd_clear_power_history"
COMMAND_FACTORY_RESET = "cmd_factory_reset"
COMMAND_SET_CLOCK = "cmd_set_clock"
STANDARD_EMS_BIT = 1
PACKS = "packs"
PACK_FAULT = "fault"
PACK_WARNING = "warning"
EV_HAND = "ev"
LEDGER_PERIODS = "ledger_periods"
LEDGER_DAY = "day"
LEDGER_STARTS = "starts_wh"
EV_REMAINING = "remaining_wh"
EV_SUPPRESSED_UNTIL = "suppressed_until_s"
EPOCH_SECOND_MAXIMUM = 1 << 40
LINK = "link"
LOCKOUT = "lockout"
LOCKOUT_ADDRESSES = "addresses"
LOCKOUT_WHOLE_PORT = "whole_port"
BLOCK_KEYS = ("start", "end", "code")
READINGS = (
    ("PV power", "pv_w", "W", 0, Needs.NOTHING),
    ("Household load", HOUSEHOLD_LOAD, "W", 0, Needs.NOTHING),
    ("Grid power", "grid_w", "W", 0, Needs.NOTHING),
    ("Battery power", "battery_w", "W", 0, Needs.BATTERY),
    ("Battery state of charge", "soc_percent", "%", 1, Needs.BATTERY),
    ("EV charger power", "ev_power_w", "W", 0, Needs.EV_CHARGER),
    ("Grid voltage", "grid_r_v", "V", 1, Needs.NOTHING),
    ("Grid frequency", "frequency_hz", "Hz", 2, Needs.NOTHING),
)


def _no_action() -> None:
    """The default for a hook nobody listens to."""


def _mapping(*, key: str, value: object) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise ControlError(key=key, reason="must be a mapping")
    return value


def _only(*, request: Mapping[str, object], allowed: tuple[str, ...]) -> None:
    for name in request:
        if name not in allowed:
            raise ControlError(key=name, reason="unknown key")


def _number(*, key: str, value: object, bounds: tuple[float, float]) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ControlError(key=key, reason="must be a number")
    if not bounds[0] <= value <= bounds[1]:
        raise ControlError(key=key, reason=f"must be {bounds[0]:g}..{bounds[1]:g}")
    return float(value)


def _whole(*, key: str, value: object, bounds: tuple[int, int]) -> int:
    number = _number(key=key, value=value, bounds=bounds)
    if not number.is_integer():
        raise ControlError(key=key, reason="must be an integer")
    return int(number)


def _flag(*, key: str, value: object) -> bool:
    if not isinstance(value, bool):
        raise ControlError(key=key, reason="must be true or false")
    return value


def _moment(*, value: object) -> datetime:
    reason = "must be an ISO 8601 date and time"
    if not isinstance(value, str):
        raise ControlError(key="time", reason=reason)
    try:
        moment = datetime.fromisoformat(value)
    except ValueError as error:
        raise ControlError(key="time", reason=reason) from error
    return moment.astimezone(UTC) if moment.tzinfo else moment.replace(tzinfo=UTC)


def _link_parameter(
    *, key: str, value: object, kind: Kind, bounds: tuple[int, int]
) -> float | int:
    if kind is Kind.PERCENT:
        return _number(key=key, value=value, bounds=bounds)
    return _whole(key=key, value=value, bounds=bounds)


def _refused_block(*, key: str, value: object) -> RefusedBlock:
    entry = _mapping(key=key, value=value)
    _only(request=entry, allowed=BLOCK_KEYS)
    for name in BLOCK_KEYS:
        if name not in entry:
            raise ControlError(key=f"{key}.{name}", reason="is required")
    start = _whole(key=f"{key}.start", value=entry["start"], bounds=ADDRESS_BOUNDS)
    end = _whole(key=f"{key}.end", value=entry["end"], bounds=ADDRESS_BOUNDS)
    if end < start:
        raise ControlError(key=f"{key}.end", reason="must be >= start")
    return RefusedBlock(
        start=start,
        end=end,
        code=_whole(key=f"{key}.code", value=entry["code"], bounds=CODE_BOUNDS),
    )


def _refused_blocks(*, key: str, value: object) -> tuple[RefusedBlock, ...]:
    if not isinstance(value, list):
        raise ControlError(key=key, reason="must be a list")
    return tuple(
        _refused_block(key=f"{key}[{index}]", value=entry)
        for index, entry in enumerate(value)
    )


def _link_settings(
    *, current: LinkSettings, values: Mapping[str, object]
) -> LinkSettings:
    parameters = {parameter.name: parameter for parameter in LINK_PARAMETERS}
    changes: dict[str, Any] = {}
    for name, value in values.items():
        if name == REFUSED_BLOCKS:
            changes[name] = _refused_blocks(key=name, value=value)
        elif name not in parameters:
            raise ControlError(key=name, reason="unknown key")
        elif parameters[name].kind is Kind.FLAG:
            changes[name] = _flag(key=name, value=value)
        else:
            parameter = parameters[name]
            changes[name] = _link_parameter(
                key=name,
                value=value,
                kind=parameter.kind,
                bounds=(parameter.minimum or 0, parameter.maximum or 0),
            )
    settings = dataclasses.replace(current, **changes)
    problem = check_combination(settings=settings)
    if problem is not None:
        raise ControlError(key=problem[0], reason=problem[1])
    return settings


def _saved_setting(*, name: str, saved: object, current: FieldValue) -> FieldValue:
    """A saved setting is text where the field is text, and a number otherwise."""
    if (
        isinstance(saved, bool)
        or not isinstance(saved, int | float | str)
        or isinstance(saved, str) != isinstance(current, str)
    ):
        raise ControlError(key=name, reason="has the wrong type")
    return saved


def _saved_periods(
    *, periods: object, totals: Mapping[str, float]
) -> tuple[dict[str, dict[str, float]], date]:
    """Period starts and the day they belong to; no start may be past its total."""
    saved = _mapping(key=LEDGER_PERIODS, value=periods)
    _only(request=saved, allowed=(LEDGER_DAY, LEDGER_STARTS))
    day_key = f"{LEDGER_PERIODS}.{LEDGER_DAY}"
    try:
        day = date.fromisoformat(str(saved.get(LEDGER_DAY)))
    except ValueError as error:
        raise ControlError(key=day_key, reason="must be an ISO 8601 date") from error
    saved_starts = _mapping(
        key=f"{LEDGER_PERIODS}.{LEDGER_STARTS}", value=saved.get(LEDGER_STARTS)
    )
    _only(request=saved_starts, allowed=STARTED_PERIODS)
    starts: dict[str, dict[str, float]] = {}
    for period in STARTED_PERIODS:
        key = f"{LEDGER_PERIODS}.{LEDGER_STARTS}.{period}"
        flows = _mapping(key=key, value=saved_starts.get(period))
        starts[period] = {
            flow: _number(
                key=f"{key}.{flow}",
                value=start,
                bounds=(0, totals.get(flow, math.inf)),
            )
            for flow, start in flows.items()
        }
    return starts, day


def _parameter(*, name: str, value: object) -> float:
    try:
        return checked_parameter(spec=PARAMETERS_BY_NAME[name], value=value)
    except ParameterError as error:
        raise ControlError(key=name, reason=str(error)) from error


@dataclasses.dataclass(frozen=True, slots=True)
class Wiring:
    on_change: Callable[[], None] = _no_action
    on_reset: Callable[[], None] = _no_action
    last_read: LastRead = never_read
    link: Link | None = None
    wall_clock: Callable[[], float] = time.time


class Machine:
    """One simulated inverter: clock, physics, settings and the register map."""

    def __init__(
        self,
        *,
        scenario: Scenario,
        monotonic: Callable[[], float],
        wiring: Wiring | None = None,
    ) -> None:
        wiring = wiring or Wiring()
        self.scenario = scenario
        self._last_read = wiring.last_read
        self._wall_clock = wiring.wall_clock
        self._link = wiring.link or Link(seed=scenario.simulation.seed)
        self._monotonic = monotonic
        self._on_change = wiring.on_change
        self._on_reset = wiring.on_reset
        self._blocks = profiles.build_blocks(scenario=scenario)
        self._fault_map = profiles.build_fault_map(scenario=scenario)
        self._initial = initial_settings(blocks=self._blocks)
        self.settings: dict[str, FieldValue] = dict(self._initial)
        self._setting_fields = [
            field
            for _block, field in available_fields(blocks=self._blocks)
            if is_setting(field=field)
        ]
        self._setting_names = frozenset(
            field.name for field in self._setting_fields if field.name in self._initial
        )
        self.device = Device(
            blocks=self._blocks,
            overrun_code=profiles.overrun_code(scenario=scenario),
            telemetry=self.telemetry,
            settings=self.settings,
            observer=self,
        )
        self._initialise()

    def _initialise(self) -> None:
        """Everything the scenario defines, as at start."""
        scenario = self.scenario
        self.settings.clear()
        self.settings.update(self._initial)
        self.clock = Clock(
            start=scenario.simulation.start,
            speed=scenario.simulation.speed,
            monotonic=self._monotonic,
        )
        self.plant = Plant(
            scenario=scenario,
            settings=self.settings,
            fault_effects=self._fault_map.effects(),
        )
        self._ems_enable = 0
        self._settings_changes = 0
        self._saved_app_mode: FieldValue = 0
        self._link.replace_settings(settings=scenario.link)
        self._link.reset_module()
        self._follow_seed()

    def _follow_seed(self) -> None:
        self._link.set_seed(seed=self.plant.seed)

    def _setting(self, *, key: str) -> float:
        value = self.settings.get(key, 0)
        return 0.0 if isinstance(value, str) else float(value)

    def _mirrors(self) -> dict[str, float]:
        ems = int(self._setting(key=ctl.EMS_ENABLE))
        running = ctl.MODE_EMS if ems else self._setting(key=ctl.APP_MODE)
        return {
            "running_mode": float(running),
            "mirror_charge_ceiling": self._setting(key=ctl.CHARGE_CEILING),
            "mirror_discharge_floor": self._setting(key=ctl.DISCHARGE_FLOOR_ON_GRID),
            "mirror_reserve": self._setting(key=ctl.BACKUP_RESERVE),
            "mirror_meter_mode": self._setting(key="meter_enable"),
            "mirror_ev_mode": self._setting(key="ev_mode"),
        }

    def telemetry(self) -> dict[str, float]:
        self._sync()
        self._sync_ems()
        data = build_telemetry(plant=self.plant)
        data.update(self._mirrors())
        data["settings_change_serial"] = float(self._settings_changes)
        return data

    def _sync(self) -> None:
        self.plant.advance(moment=self.clock.now())

    def _sync_ems(self) -> None:
        enable = int(self._setting(key=ctl.EMS_ENABLE))
        previous = self._ems_enable
        if enable == previous:
            return
        if enable & STANDARD_EMS_BIT and not previous & STANDARD_EMS_BIT:
            self._saved_app_mode = self.settings[ctl.APP_MODE]
            self.settings[ctl.APP_MODE] = ctl.MODE_EMS
        if previous & STANDARD_EMS_BIT and not enable & STANDARD_EMS_BIT:
            self.settings[ctl.APP_MODE] = self._saved_app_mode
        if enable and not previous:
            self.plant.controller.keepalive(second=self.plant.second)
        self._ems_enable = enable

    def _touch(self, *, field: Field) -> None:
        if (
            field.keepalive_bit
            and int(self._setting(key=ctl.EMS_ENABLE)) & field.keepalive_bit
        ):
            self.plant.controller.keepalive(second=self.plant.second)

    def field_read(self, *, field: Field) -> None:
        self._touch(field=field)

    def field_written(self, *, field: Field, value: FieldValue) -> None:
        if field.readable:
            self._settings_changes += 1
        self._touch(field=field)
        self._sync_ems()
        self._run_command(name=field.name, value=value)
        self._on_change()

    def _run_command(self, *, name: str, value: FieldValue) -> None:
        if name == COMMAND_CLEAR_FAULTS:
            if value == CLEAR_CURRENT_FAULT:
                self.plant.set_faults(faults=FaultState())
        elif name == COMMAND_RESTART:
            self.plant.restart()
        elif name == COMMAND_CLEAR_POWER_HISTORY:
            self.plant.ledger.clear()
        elif name == COMMAND_FACTORY_RESET:
            self.settings.update(self._initial)
            self._ems_enable = 0
        elif name == COMMAND_SET_CLOCK:
            moment = EPOCH + timedelta(seconds=float(value))
            self.clock.set(moment=moment)
            self.plant.jump_to(moment=moment)

    def _fitted(self) -> Fitted:
        scenario = self.scenario
        return Fitted(
            battery=bool(scenario.battery.modules),
            meter_a=scenario.meters.meter_a,
            meter_b=scenario.meters.meter_b,
            ev_charger=scenario.ev_charger.installed,
        )

    def presets(self) -> tuple[Preset, ...]:
        return available_presets(fitted=self._fitted(), fault_map=self._fault_map)

    def describe(self) -> dict[str, object]:
        scenario = self.scenario
        return {
            "model": describe_model(
                scenario=scenario, pack_count=self._fault_map.pack_count
            ),
            "settings": describe_settings(blocks=self._blocks, initial=self._initial),
            "commands": describe_commands(blocks=self._blocks),
            "faults": describe_faults(
                fault_map=self._fault_map,
                clear_command=COMMAND_CLEAR_FAULTS,
                clear_value=CLEAR_CURRENT_FAULT,
            ),
            "variation": describe_variation(
                seed=scenario.simulation.seed,
                variation=scenario.variation,
                load=scenario.site.load,
            ),
            "holds": describe_holds(),
            "presets": describe_presets(presets=self.presets()),
            "cards": describe_cards(fitted=self._fitted()),
            "nodes": describe_nodes(fitted=self._fitted()),
            LINK: describe_link(scenario=scenario.link),
        }

    def _readings(self, *, data: Mapping[str, float]) -> list[dict[str, object]]:
        fitted = self._fitted()
        readings: list[dict[str, object]] = [
            {
                "label": label,
                "value": rounded(value=data[key], places=places),
                "unit": unit,
            }
            for label, key, unit, places, needs in READINGS
            if fitted.has(needs=needs)
        ]
        texts = self._texts(data=data)
        readings.extend(
            {"label": label, "value": texts[name], "unit": ""}
            for label, name in (
                ("Operating mode", "operating_mode"),
                ("Application mode", "application_mode"),
            )
        )
        return readings

    def _texts(self, *, data: Mapping[str, float]) -> dict[str, str]:
        operating = int(data["operating_mode"])
        running = int(data["running_mode"])
        application = self._application_mode_name(code=running)
        plugged = data["ev_state"] != float(ChargerState.IDLE)
        return {
            "operating_mode": (
                f"{operating} {OPERATING_MODES.get(operating, '')}".strip()
            ),
            "application_mode": f"{running} {application}".strip(),
            "car": "Plugged in" if plugged else "Not plugged in",
        }

    def _application_mode_name(self, *, code: int) -> str:
        field = self.device.field_named(name=ctl.APP_MODE)
        return dict(field.labels).get(code, "") if field is not None else ""

    def _scenario_variation(self) -> dict[str, float]:
        scenario = self.scenario
        return variation_values(
            seed=scenario.simulation.seed,
            variation=scenario.variation,
            load=scenario.site.load,
        )

    def _changes(self) -> dict[str, object]:
        plant = self.plant
        return {
            "holds": held_names(holds=plant.holds),
            "faults": fault_counts(faults=plant.faults),
            "settings": changed_settings(
                fields=self._setting_fields,
                settings=self.settings,
                initial=self._initial,
            ),
            "variation": changed_variation(
                variation=variation_values(
                    seed=plant.seed, variation=plant.variation, load=plant.load
                ),
                scenario=self._scenario_variation(),
            ),
            LINK: changed_link(
                settings=self._link.settings, scenario=self.scenario.link
            ),
        }

    def _link_refusal(self, *, block: Block) -> int | None:
        return self._link.refused_code(
            start=block.start, count=block.end - block.start + 1
        )

    def registers(self) -> dict[str, object]:
        """Every register as a client would read it, without being a client read."""
        return register_snapshot(
            blocks=self._blocks,
            words=self.device.peek_fields(),
            last_read=self._last_read,
            link_refusal=self._link_refusal,
        )

    def state(self) -> dict[str, object]:
        data = with_household_load(data=self.telemetry())
        plant = self.plant
        return {
            "time": self.clock.now().replace(tzinfo=None).isoformat(timespec="seconds"),
            "speed": self.clock.speed,
            "settings": settings_state(
                fields=self._setting_fields, settings=self.settings
            ),
            "changes": self._changes(),
            LINK: link_values(settings=self._link.settings),
            "module": self._link.module_state(now=self._wall_clock()).to_json(),
            "faults": faults_state(faults=plant.faults),
            "variation": variation_values(
                seed=plant.seed, variation=plant.variation, load=plant.load
            ),
            "holds": hold_values(holds=plant.holds),
            "hold_readings": hold_readings(data=data),
            "readings": self._readings(data=data),
            "node_readings": node_readings(fitted=self._fitted(), data=data),
            "card_readings": card_readings(
                fitted=self._fitted(), data=data, texts=self._texts(data=data)
            ),
            "battery": {"soc_percent": data["soc_percent"]},
            "ev_charger": {"plugged": data["ev_state"] != float(ChargerState.IDLE)},
        }

    def set_settings(self, *, values: Mapping[str, object]) -> None:
        for name in values:
            field = self.device.field_named(name=name)
            if field is not None and not field.readable:
                raise ControlError(key=name, reason="is not a setting")
        self.device.write_named(values=values)

    def run_command(self, *, values: Mapping[str, object]) -> None:
        name = values.get("name")
        field = self.device.field_named(name=name) if isinstance(name, str) else None
        if field is None or field.readable or field.is_clock:
            raise ControlError(key="name", reason="is not a command")
        self.device.write_named(values={field.name: values.get("value")})

    def set_faults(self, *, values: Mapping[str, object]) -> None:
        self._sync()
        faults = self.plant.faults
        for name, entries in values.items():
            if name == PACKS:
                faults = self._with_packs(faults=faults, entries=entries)
            else:
                faults = self._with_bits(faults=faults, name=name, entries=entries)
        self.plant.set_faults(faults=faults)
        self._on_change()

    def _with_bits(
        self, *, faults: FaultState, name: str, entries: object
    ) -> FaultState:
        try:
            equipment = Equipment(name)
        except ValueError as error:
            raise ControlError(key=name, reason="unknown key") from error
        known = {
            entry.bit.key: entry.bit
            for entry in self._fault_map.for_equipment(equipment=equipment)
        }
        active = set(faults.bits(equipment=equipment))
        for bit_key, on in _mapping(key=name, value=entries).items():
            key = f"{name}.{bit_key}"
            bit: FaultBit | None = known.get(bit_key)
            if bit is None:
                raise ControlError(key=key, reason="is not a fault of this device")
            if _flag(key=key, value=on):
                active.add(bit)
            else:
                active.discard(bit)
        return faults.with_bits(equipment=equipment, bits=active)

    def _with_packs(self, *, faults: FaultState, entries: object) -> FaultState:
        requested = _mapping(key=PACKS, value=entries)
        if requested and not self._fault_map.pack_count:
            raise ControlError(key=PACKS, reason="no battery fitted")
        for pack_text, codes in requested.items():
            key = f"{PACKS}.{pack_text}"
            pack = _whole(
                key=key,
                value=int(pack_text) if pack_text.isdigit() else None,
                bounds=(1, self._fault_map.pack_count),
            )
            request = _mapping(key=key, value=codes)
            _only(request=request, allowed=(PACK_FAULT, PACK_WARNING))
            known = faults.pack(number=pack)
            faults = faults.with_pack(
                codes=PackCodes(
                    pack=pack,
                    fault=self._code(
                        key=f"{key}.{PACK_FAULT}",
                        request=request,
                        name=PACK_FAULT,
                        current=known.fault,
                    ),
                    warning=self._code(
                        key=f"{key}.{PACK_WARNING}",
                        request=request,
                        name=PACK_WARNING,
                        current=known.warning,
                    ),
                )
            )
        return faults

    @staticmethod
    def _code(
        *, key: str, request: Mapping[str, object], name: str, current: int
    ) -> int:
        if name not in request:
            return current
        return _whole(key=key, value=request[name], bounds=(0, WORD_MAXIMUM))

    def set_variation(self, *, values: Mapping[str, object]) -> None:
        self._sync()
        plant = self.plant
        known = variation_values(
            seed=plant.seed, variation=plant.variation, load=plant.load
        )
        for name, value in values.items():
            if name not in known:
                raise ControlError(key=name, reason="unknown key")
            known[name] = _parameter(name=name, value=value)
        if known[LOAD_PEAK] < known[LOAD_BASE]:
            raise ControlError(key=LOAD_PEAK, reason="must be >= base_w")
        shape: dict[str, Any] = {
            name: known[name] for name in dataclasses.asdict(plant.variation)
        }
        plant.tune(
            seed=int(known[SEED]),
            variation=Variation(**shape),
            load=LoadConfig(base_w=int(known[LOAD_BASE]), peak_w=int(known[LOAD_PEAK])),
        )
        self._follow_seed()
        self._on_change()

    def set_link(self, *, values: Mapping[str, object]) -> None:
        self._link.replace_settings(
            settings=_link_settings(current=self._link.settings, values=values)
        )
        self._on_change()

    def drop_connections(self) -> None:
        self._link.drop_connections_now()

    def reset_module(self) -> None:
        self._link.reset_module()
        self._on_change()

    def set_holds(self, *, values: Mapping[str, object]) -> None:
        self._sync()
        specs = {spec.name: spec for spec in HOLD_PARAMETERS}
        holds = dict(self.plant.holds)
        for name, value in values.items():
            if name not in specs:
                raise ControlError(key=name, reason="unknown key")
            if value is None:
                holds.pop(name, None)
                continue
            holds[name] = _number(
                key=name, value=value, bounds=(specs[name].minimum, specs[name].maximum)
            )
        self.plant.hold(holds=holds)
        self._on_change()

    def set_battery(self, *, values: Mapping[str, object]) -> None:
        _only(request=values, allowed=("soc_percent",))
        if not self.scenario.battery.modules:
            raise ControlError(key="soc_percent", reason="no battery fitted")
        percent = _number(
            key="soc_percent", value=values.get("soc_percent"), bounds=SOC_BOUNDS
        )
        self._sync()
        self.plant.set_soc(soc=percent / PERCENT)
        self._on_change()

    def set_ev(self, *, values: Mapping[str, object]) -> None:
        _only(request=values, allowed=("plugged", "energy_needed_wh"))
        if not self.scenario.ev_charger.installed:
            raise ControlError(key="plugged", reason="no EV charger fitted")
        plugged = _flag(key="plugged", value=values.get("plugged"))
        energy = _whole(
            key="energy_needed_wh",
            value=values.get("energy_needed_wh", EV_DEFAULT_ENERGY_WH),
            bounds=EV_ENERGY_BOUNDS,
        )
        self._sync()
        if plugged:
            self.plant.plug_ev(energy_needed_wh=energy)
        else:
            self.plant.unplug_ev()
        self._on_change()

    def set_clock(self, *, values: Mapping[str, object]) -> None:
        _only(request=values, allowed=("time", "speed"))
        moment = _moment(value=values["time"]) if "time" in values else None
        speed = (
            _number(key="speed", value=values["speed"], bounds=SPEED_BOUNDS)
            if "speed" in values
            else None
        )
        self._sync()
        if moment is not None:
            self.clock.set(moment=moment)
            self.plant.jump_to(moment=moment)
        if speed is not None:
            self.clock.set_speed(speed=speed)
        self._on_change()

    def reset_ledger(self) -> None:
        self._sync()
        self.plant.ledger.reset(moment=self.plant.moment())
        self._on_change()

    def reset(self) -> None:
        """Back to the scenario, and forget what was saved."""
        self._initialise()
        self._on_reset()

    def apply_preset(self, *, key: str) -> None:
        preset = next((known for known in self.presets() if known.key == key), None)
        if preset is None:
            raise ControlError(key=key, reason="is not a preset of this device")
        self._return_to_scenario_settings()
        if preset.link:
            self.set_link(values=preset.link)
        if preset.variation:
            self.set_variation(values=preset.variation)
        if preset.settings:
            self.set_settings(values=preset.settings)
        if preset.faults or preset.packs:
            self.set_faults(values=self._preset_faults(preset=preset))
        if preset.soc_percent is not None:
            self.set_battery(values={"soc_percent": preset.soc_percent})
        if preset.ev_energy_wh is not None:
            self.set_ev(
                values={"plugged": True, "energy_needed_wh": preset.ev_energy_wh}
            )

    def reset_card(self, *, key: str) -> None:
        """Return one card's variation, holds and fault bits to the scenario.

        Settings, the charge, the car, the clock and the energy counters carry on.
        """
        card = next(
            (
                known
                for known in applicable_cards(fitted=self._fitted())
                if known.key == key
            ),
            None,
        )
        if card is None:
            raise ControlError(key=key, reason="is not a card of this device")
        if card.group is not None:
            scenario_values = self._scenario_variation()
            self.set_variation(
                values={
                    spec.name: scenario_values[spec.name]
                    for spec in (*VARIATION_PARAMETERS, SEED_PARAMETER)
                    if spec.group == card.group
                }
            )
        if card.holds:
            self.set_holds(values=dict.fromkeys(card.holds))
        if card.equipment is not None:
            self._reset_faults(equipment=card.equipment)

    def _reset_faults(self, *, equipment: Equipment) -> None:
        self._sync()
        scenario_faults = self.scenario.faults
        faults = self.plant.faults.with_bits(
            equipment=equipment, bits=scenario_faults.bits(equipment=equipment)
        )
        if equipment is Equipment.BATTERY:
            faults = dataclasses.replace(faults, packs=scenario_faults.packs)
        self.plant.set_faults(faults=faults)
        self._on_change()

    def _return_to_scenario_settings(self) -> None:
        """Settings, variation, seed, faults and holds as the scenario has them.
        The clock, the energy counters and the battery carry on."""
        scenario = self.scenario
        self.settings.clear()
        self.settings.update(self._initial)
        self._ems_enable = 0
        self._saved_app_mode = 0
        self.plant.tune(
            seed=scenario.simulation.seed,
            variation=scenario.variation,
            load=scenario.site.load,
        )
        self._follow_seed()
        self.plant.set_faults(faults=scenario.faults)
        self.plant.hold(holds={})
        self._link.replace_settings(settings=scenario.link)
        self._link.reset_module()
        self._on_change()

    def _preset_faults(self, *, preset: Preset) -> dict[str, object]:
        request: dict[str, dict[str, bool]] = {}
        for equipment, name in preset.faults:
            bits = self._fault_map.find(equipment=equipment, name=name)
            request.setdefault(equipment.value, {}).update(
                {bit.key: True for bit in bits}
            )
        return {**request, PACKS: dict(preset.packs)}

    def export_scenario(self) -> str:
        """The running state the scenario can express, as scenario YAML."""
        self._sync()
        plant = self.plant
        scenario = self.scenario
        running = dataclasses.replace(
            scenario,
            simulation=dataclasses.replace(
                scenario.simulation,
                seed=plant.seed,
                start=self.clock.now().replace(microsecond=0),
                speed=self.clock.speed,
            ),
            site=dataclasses.replace(scenario.site, load=plant.load),
            variation=plant.variation,
            faults=plant.faults,
            battery=self._exported_battery(),
            link=self._link.settings,
        )
        return dump_scenario(scenario=running)

    def _exported_battery(self) -> BatteryConfig:
        battery = self.scenario.battery
        if not battery.modules:
            return battery
        percent = round(self.plant.battery.soc * PERCENT)
        return dataclasses.replace(
            battery, initial_soc_percent=min(max(percent, 0), PERCENT_MAX)
        )

    def snapshot(self) -> dict[str, object]:
        """What a restart keeps."""
        self._sync()
        plant = self.plant
        return {
            "settings": {
                name: self.settings[name] for name in sorted(self._setting_names)
            },
            "saved_app_mode": self._saved_app_mode,
            "faults": faults_state(faults=plant.faults),
            "variation": variation_values(
                seed=plant.seed, variation=plant.variation, load=plant.load
            ),
            "holds": dict(plant.holds),
            "soc_percent": plant.battery.soc * PERCENT,
            "ledger_wh": plant.ledger.totals_wh(),
            LEDGER_PERIODS: {
                LEDGER_DAY: plant.ledger.day.isoformat(),
                LEDGER_STARTS: plant.ledger.starts_wh(),
            },
            EV_HAND: self._ev_snapshot(),
            "clock": {"time": self.clock.now().isoformat(), "speed": self.clock.speed},
            LINK: link_values(settings=self._link.settings),
            LOCKOUT: self._lockout_snapshot(),
        }

    def _lockout_snapshot(self) -> dict[str, object]:
        state = self._link.lockout_state()
        return {
            LOCKOUT_ADDRESSES: list(state.addresses),
            LOCKOUT_WHOLE_PORT: state.whole_port,
        }

    def _ev_snapshot(self) -> dict[str, int | None]:
        hand = self.plant.ev.hand_state()
        return {
            EV_REMAINING: hand.remaining_wh,
            EV_SUPPRESSED_UNTIL: hand.suppressed_until_s,
        }

    def restore(self, *, snapshot: Mapping[str, object]) -> None:
        """Take a saved snapshot. A snapshot that cannot be read leaves the scenario."""
        try:
            self._restore(snapshot=snapshot)
        except ControlError:
            self._initialise()
            raise

    def _restore(self, *, snapshot: Mapping[str, object]) -> None:
        self.set_clock(values=_mapping(key="clock", value=snapshot.get("clock")))
        self._restore_settings(
            values=_mapping(key="settings", value=snapshot.get("settings")),
            saved_app_mode=snapshot.get("saved_app_mode"),
        )
        self.set_variation(
            values=_mapping(key="variation", value=snapshot.get("variation"))
        )
        self.set_holds(values=_mapping(key="holds", value=snapshot.get("holds")))
        self.plant.set_faults(faults=FaultState())
        self.set_faults(values=_mapping(key="faults", value=snapshot.get("faults")))
        if self.scenario.battery.modules:
            self.set_battery(values={"soc_percent": snapshot.get("soc_percent")})
        self._restore_ledger(
            totals=_mapping(key="ledger_wh", value=snapshot.get("ledger_wh")),
            periods=snapshot.get(LEDGER_PERIODS),
        )
        self._restore_ev(values=_mapping(key=EV_HAND, value=snapshot.get(EV_HAND, {})))
        self._restore_link(
            values=_mapping(key=LINK, value=snapshot.get(LINK)),
            lockout=_mapping(key=LOCKOUT, value=snapshot.get(LOCKOUT)),
        )
        # A restored EMS gets its full timeout from the restored moment.
        self.plant.controller.keepalive(second=self.plant.second)

    def _restore_link(
        self, *, values: Mapping[str, object], lockout: Mapping[str, object]
    ) -> None:
        _only(request=lockout, allowed=(LOCKOUT_ADDRESSES, LOCKOUT_WHOLE_PORT))
        addresses = lockout.get(LOCKOUT_ADDRESSES)
        if not isinstance(addresses, list) or not all(
            isinstance(address, str) for address in addresses
        ):
            raise ControlError(
                key=f"{LOCKOUT}.{LOCKOUT_ADDRESSES}", reason="must be a list of text"
            )
        whole_port = _flag(
            key=f"{LOCKOUT}.{LOCKOUT_WHOLE_PORT}",
            value=lockout.get(LOCKOUT_WHOLE_PORT),
        )
        self.set_link(values=values)
        self._link.restore_lockout(
            state=LockoutState(addresses=tuple(addresses), whole_port=whole_port)
        )

    def _restore_settings(
        self, *, values: Mapping[str, object], saved_app_mode: object
    ) -> None:
        for name in values:
            if name not in self.settings:
                raise ControlError(key=name, reason="is not a setting")
        checked = {
            name: _saved_setting(name=name, saved=saved, current=self.settings[name])
            for name, saved in values.items()
            if name in self._setting_names
        }
        for name, value in checked.items():
            self.device.check_stored(name=name, value=value)
        self.settings.update(checked)
        self._ems_enable = int(self._setting(key=ctl.EMS_ENABLE))
        if isinstance(saved_app_mode, int | float | str):
            self._saved_app_mode = saved_app_mode

    def _restore_ledger(self, *, totals: Mapping[str, object], periods: object) -> None:
        checked = {
            flow: _number(key=flow, value=total, bounds=(0, math.inf))
            for flow, total in totals.items()
        }
        starts, day = (
            (None, None)
            if periods is None
            else _saved_periods(periods=periods, totals=checked)
        )
        self.plant.ledger.restore(
            totals_wh=checked, moment=self.plant.moment(), starts_wh=starts, day=day
        )
        self._on_change()

    def _restore_ev(self, *, values: Mapping[str, object]) -> None:
        _only(request=values, allowed=(EV_REMAINING, EV_SUPPRESSED_UNTIL))
        remaining = values.get(EV_REMAINING)
        state = HandState(
            remaining_wh=(
                None
                if remaining is None
                else _whole(
                    key=f"{EV_HAND}.{EV_REMAINING}",
                    value=remaining,
                    bounds=(0, EV_ENERGY_BOUNDS[1]),
                )
            ),
            suppressed_until_s=_whole(
                key=f"{EV_HAND}.{EV_SUPPRESSED_UNTIL}",
                value=values.get(EV_SUPPRESSED_UNTIL, 0),
                bounds=(0, EPOCH_SECOND_MAXIMUM),
            ),
        )
        hand_used = state.remaining_wh is not None or state.suppressed_until_s
        if hand_used and not self.scenario.ev_charger.installed:
            raise ControlError(key=EV_HAND, reason="no EV charger fitted")
        self.plant.restore_ev(state=state)
