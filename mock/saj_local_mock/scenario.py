import dataclasses
import re
from collections.abc import Mapping
from datetime import UTC, datetime, time
from typing import TYPE_CHECKING, Any

import yaml

from .link import (
    ADDRESS_BOUNDS,
    CODE_BOUNDS,
    LINK_PARAMETERS,
    REFUSED_BLOCKS,
    Kind,
    LinkSettings,
    RefusedBlock,
    check_combination,
    link_values,
)
from .models import MAX_PV_STRINGS, MODELS, ModelSpec
from .simulation.environment import (
    LOAD_BASE,
    LOAD_PEAK,
    SEED_MAXIMUM,
    VARIATION_PARAMETERS,
    LoadConfig,
    ParameterError,
    ParameterSpec,
    Variation,
    checked_parameter,
)
from .simulation.faults import (
    BITS_PER_REGISTER,
    REGISTERS,
    WORD_MAXIMUM,
    Equipment,
    FaultBit,
    FaultState,
    PackCodes,
    hex_address,
)

if TYPE_CHECKING:
    from pathlib import Path

MAX_PORT = 65535
MAX_UNIT_ID = 247
PERCENT_MAX = 100
TIME_OF_DAY_PATTERN = re.compile(r"\d{2}:\d{2}")
TIME_OF_DAY_FORMAT = "%H:%M"
DEFAULT_PORT = 502
DEFAULT_PANEL_PORT = 8080
DEFAULT_MAX_CLIENTS = 2
DEFAULT_STRING_SHARE_DIVISOR = 2
DEFAULT_SEED = 1
DEFAULT_START = "2026-06-21T05:00:00"
DEFAULT_LOAD_BASE_W = 350
DEFAULT_LOAD_PEAK_W = 6000
DEFAULT_BATTERY_MODULES = 2
DEFAULT_MODULE_CAPACITY_AH = 100
DEFAULT_INITIAL_SOC_PERCENT = 50
DEFAULT_EV_MAX_POWER_W = 11000
DEFAULT_EV_PHASES = 3
DEFAULT_PV_STRINGS = 2
PARALLEL_INVERTERS = (1, 2)
EV_PHASE_COUNTS = (1, 3)


class ScenarioError(Exception):
    def __init__(self, *, key: str, reason: str) -> None:
        super().__init__(f"{key}: {reason}")
        self.key = key
        self.reason = reason


@dataclasses.dataclass(frozen=True, slots=True)
class DeviceConfig:
    model: ModelSpec
    rated_power_w: int
    serial_number: str


@dataclasses.dataclass(frozen=True, slots=True)
class ServerConfig:
    port: int
    unit_id: int
    max_clients: int
    panel_port: int


@dataclasses.dataclass(frozen=True, slots=True)
class SimulationConfig:
    seed: int
    start: datetime
    speed: float


@dataclasses.dataclass(frozen=True, slots=True)
class SiteConfig:
    grid_connected: bool
    pv_strings: tuple[int, ...]
    load: LoadConfig


@dataclasses.dataclass(frozen=True, slots=True)
class BatteryConfig:
    modules: int
    module_capacity_ah: int
    initial_soc_percent: int


@dataclasses.dataclass(frozen=True, slots=True)
class MetersConfig:
    meter_a: bool
    meter_b: bool


@dataclasses.dataclass(frozen=True, slots=True)
class EvSession:
    plug_in: time
    unplug: time
    energy_needed_wh: int


@dataclasses.dataclass(frozen=True, slots=True)
class EvChargerConfig:
    installed: bool
    phases: int
    max_power_w: int
    sessions: tuple[EvSession, ...]


@dataclasses.dataclass(frozen=True, slots=True)
class ParallelConfig:
    inverters: int


@dataclasses.dataclass(frozen=True, slots=True)
class Scenario:
    device: DeviceConfig
    server: ServerConfig
    simulation: SimulationConfig
    site: SiteConfig
    battery: BatteryConfig
    meters: MetersConfig
    ev_charger: EvChargerConfig
    parallel: ParallelConfig
    variation: Variation
    faults: FaultState
    link: LinkSettings


class Section:
    """Typed reads from one mapping that reject keys the schema does not name."""

    def __init__(self, *, path: str, data: object) -> None:
        if data is None:
            data = {}
        if not isinstance(data, Mapping):
            raise ScenarioError(key=path, reason="must be a mapping")
        self._path = path
        self._data: Mapping[str, Any] = data
        self._seen: set[str] = set()

    def key(self, *, name: str) -> str:
        return f"{self._path}.{name}" if self._path else name

    def _raw(self, *, name: str, default: object) -> object:
        self._seen.add(name)
        return self._data.get(name, default)

    def integer(
        self,
        *,
        name: str,
        default: int,
        minimum: int,
        maximum: int | None = None,
    ) -> int:
        value = self._raw(name=name, default=default)
        if isinstance(value, bool) or not isinstance(value, int):
            raise ScenarioError(key=self.key(name=name), reason="must be an integer")
        if value < minimum or (maximum is not None and value > maximum):
            bound = f">= {minimum}" if maximum is None else f"{minimum}..{maximum}"
            raise ScenarioError(key=self.key(name=name), reason=f"must be {bound}")
        return value

    def required_integer(
        self, *, name: str, minimum: int, maximum: int | None = None
    ) -> int:
        if name not in self._data:
            raise ScenarioError(key=self.key(name=name), reason="is required")
        return self.integer(
            name=name, default=minimum, minimum=minimum, maximum=maximum
        )

    def number(
        self,
        *,
        name: str,
        default: float,
        minimum: float,
        maximum: float | None = None,
    ) -> float:
        value = self._raw(name=name, default=default)
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise ScenarioError(key=self.key(name=name), reason="must be a number")
        if maximum is not None and not minimum <= value <= maximum:
            raise ScenarioError(
                key=self.key(name=name), reason=f"must be {minimum}..{maximum}"
            )
        if value < minimum:
            raise ScenarioError(key=self.key(name=name), reason=f"must be >= {minimum}")
        return float(value)

    def parameter(self, *, spec: ParameterSpec, default: float) -> float:
        value = self._raw(name=spec.name, default=default)
        try:
            return checked_parameter(spec=spec, value=value)
        except ParameterError as error:
            raise ScenarioError(
                key=self.key(name=spec.name), reason=str(error)
            ) from error

    def boolean(self, *, name: str, default: bool) -> bool:
        value = self._raw(name=name, default=default)
        if not isinstance(value, bool):
            raise ScenarioError(key=self.key(name=name), reason="must be true or false")
        return value

    def text(self, *, name: str, default: str) -> str:
        value = self._raw(name=name, default=default)
        if not isinstance(value, str) or not value:
            raise ScenarioError(
                key=self.key(name=name), reason="must be non-empty text"
            )
        return value

    def required_text(self, *, name: str) -> str:
        if name not in self._data:
            raise ScenarioError(key=self.key(name=name), reason="is required")
        return self.text(name=name, default="")

    def items(self, *, name: str, default: list[Any]) -> list[Any]:
        value = self._raw(name=name, default=default)
        if not isinstance(value, list):
            raise ScenarioError(key=self.key(name=name), reason="must be a list")
        return value

    def section(self, *, name: str) -> Section:
        return Section(path=self.key(name=name), data=self._raw(name=name, default={}))

    def finish(self) -> None:
        unknown = sorted(str(name) for name in set(self._data) - self._seen)
        if unknown:
            raise ScenarioError(key=self.key(name=unknown[0]), reason="unknown key")


def _time_of_day(*, key: str, value: object) -> time:
    if not isinstance(value, str) or not TIME_OF_DAY_PATTERN.fullmatch(value):
        raise ScenarioError(key=key, reason="must be a time of day as HH:MM")
    try:
        return time.fromisoformat(value)
    except ValueError as error:
        raise ScenarioError(key=key, reason="must be a time of day as HH:MM") from error


def _parse_device(*, root: Section) -> DeviceConfig:
    section = root.section(name="device")
    model_name = section.required_text(name="model")
    if model_name not in MODELS:
        raise ScenarioError(key="device.model", reason="must be one of hs3, h2")
    model = MODELS[model_name]
    rated = section.integer(
        name="rated_power_w", default=model.default_rated_power_w, minimum=1
    )
    if rated not in model.rated_powers_w:
        allowed = ", ".join(str(power) for power in model.rated_powers_w)
        raise ScenarioError(
            key="device.rated_power_w",
            reason=f"{model.name} exists in {allowed}",
        )
    serial = section.text(name="serial_number", default=model.default_serial_number)
    section.finish()
    return DeviceConfig(model=model, rated_power_w=rated, serial_number=serial)


def _parse_server(*, root: Section) -> ServerConfig:
    section = root.section(name="server")
    config = ServerConfig(
        port=section.integer(
            name="port", default=DEFAULT_PORT, minimum=0, maximum=MAX_PORT
        ),
        unit_id=section.integer(
            name="unit_id", default=1, minimum=0, maximum=MAX_UNIT_ID
        ),
        max_clients=section.integer(
            name="max_clients", default=DEFAULT_MAX_CLIENTS, minimum=1
        ),
        panel_port=section.integer(
            name="panel_port", default=DEFAULT_PANEL_PORT, minimum=0, maximum=MAX_PORT
        ),
    )
    section.finish()
    return config


def _parse_simulation(*, root: Section) -> SimulationConfig:
    section = root.section(name="simulation")
    seed = section.integer(
        name="seed", default=DEFAULT_SEED, minimum=0, maximum=SEED_MAXIMUM
    )
    start_text = section.text(name="start", default=DEFAULT_START)
    speed = section.number(name="speed", default=1.0, minimum=0.0)
    section.finish()
    try:
        start = datetime.fromisoformat(start_text)
    except ValueError as error:
        raise ScenarioError(
            key="simulation.start",
            reason="must be an ISO 8601 date and time",
        ) from error
    start = start.astimezone(UTC) if start.tzinfo else start.replace(tzinfo=UTC)
    return SimulationConfig(seed=seed, start=start, speed=speed)


def _parse_pv_strings(
    *, site: Section, model: ModelSpec, rated: int
) -> tuple[int, ...]:
    default = [
        {"peak_power_w": rated // DEFAULT_STRING_SHARE_DIVISOR}
    ] * DEFAULT_PV_STRINGS
    entries = site.items(name="pv_strings", default=default)
    if len(entries) > MAX_PV_STRINGS:
        raise ScenarioError(
            key="site.pv_strings",
            reason=f"{model.name} supports at most {MAX_PV_STRINGS} strings",
        )
    peaks = []
    for index, entry in enumerate(entries):
        string = Section(path=f"site.pv_strings[{index}]", data=entry)
        peaks.append(
            string.integer(
                name="peak_power_w",
                default=rated // DEFAULT_STRING_SHARE_DIVISOR,
                minimum=1,
            )
        )
        string.finish()
    return tuple(peaks)


def _parse_site(*, root: Section, device: DeviceConfig) -> SiteConfig:
    section = root.section(name="site")
    grid_connected = section.boolean(name="grid_connected", default=True)
    peaks = _parse_pv_strings(
        site=section,
        model=device.model,
        rated=device.rated_power_w,
    )
    load_section = section.section(name="load")
    base = load_section.integer(name="base_w", default=DEFAULT_LOAD_BASE_W, minimum=0)
    peak = load_section.integer(name="peak_w", default=DEFAULT_LOAD_PEAK_W, minimum=0)
    load_section.finish()
    section.finish()
    if peak < base:
        raise ScenarioError(key="site.load.peak_w", reason="must be >= base_w")
    return SiteConfig(
        grid_connected=grid_connected,
        pv_strings=peaks,
        load=LoadConfig(base_w=base, peak_w=peak),
    )


def _parse_battery(*, root: Section, device: DeviceConfig) -> BatteryConfig:
    section = root.section(name="battery")
    modules = section.integer(
        name="modules",
        default=DEFAULT_BATTERY_MODULES,
        minimum=0,
        maximum=device.model.max_battery_modules,
    )
    config = BatteryConfig(
        modules=modules,
        module_capacity_ah=section.integer(
            name="module_capacity_ah", default=DEFAULT_MODULE_CAPACITY_AH, minimum=1
        ),
        initial_soc_percent=section.integer(
            name="initial_soc_percent",
            default=DEFAULT_INITIAL_SOC_PERCENT,
            minimum=0,
            maximum=PERCENT_MAX,
        ),
    )
    section.finish()
    return config


def _parse_meters(*, root: Section) -> MetersConfig:
    section = root.section(name="meters")
    config = MetersConfig(
        meter_a=section.boolean(name="meter_a", default=True),
        meter_b=section.boolean(name="meter_b", default=False),
    )
    section.finish()
    return config


def _parse_sessions(*, charger: Section) -> tuple[EvSession, ...]:
    sessions = []
    for index, entry in enumerate(charger.items(name="sessions", default=[])):
        path = f"ev_charger.sessions[{index}]"
        session = Section(path=path, data=entry)
        plug_in = _time_of_day(
            key=f"{path}.plug_in",
            value=session.required_text(name="plug_in"),
        )
        unplug = _time_of_day(
            key=f"{path}.unplug",
            value=session.required_text(name="unplug"),
        )
        energy = session.integer(name="energy_needed_wh", default=0, minimum=1)
        session.finish()
        sessions.append(
            EvSession(plug_in=plug_in, unplug=unplug, energy_needed_wh=energy)
        )
    return tuple(sessions)


def _parse_ev_charger(*, root: Section, device: DeviceConfig) -> EvChargerConfig:
    section = root.section(name="ev_charger")
    installed = section.boolean(name="installed", default=False)
    config = EvChargerConfig(
        installed=installed,
        phases=section.integer(name="phases", default=DEFAULT_EV_PHASES, minimum=1),
        max_power_w=section.integer(
            name="max_power_w", default=DEFAULT_EV_MAX_POWER_W, minimum=1
        ),
        sessions=_parse_sessions(charger=section),
    )
    section.finish()
    if installed and not device.model.supports_ev_charger:
        raise ScenarioError(
            key="ev_charger.installed",
            reason=f"not available on {device.model.name}",
        )
    if config.phases not in EV_PHASE_COUNTS:
        raise ScenarioError(key="ev_charger.phases", reason="must be 1 or 3")
    return config


def _parse_parallel(*, root: Section) -> ParallelConfig:
    section = root.section(name="parallel")
    inverters = section.integer(name="inverters", default=1, minimum=1)
    section.finish()
    if inverters not in PARALLEL_INVERTERS:
        raise ScenarioError(key="parallel.inverters", reason="must be 1 or 2")
    return ParallelConfig(inverters=inverters)


def _parse_variation(*, root: Section) -> Variation:
    section = root.section(name="variation")
    defaults = Variation()
    values: dict[str, Any] = {
        spec.name: section.parameter(spec=spec, default=getattr(defaults, spec.name))
        for spec in VARIATION_PARAMETERS
        if spec.name not in (LOAD_BASE, LOAD_PEAK)
    }
    section.finish()
    return Variation(**values)


def _parse_fault_bits(
    *, faults: Section, equipment: Equipment, fitted: bool
) -> frozenset[FaultBit]:
    name = equipment.value
    entries = faults.items(name=name, default=[])
    if entries and not fitted:
        raise ScenarioError(key=faults.key(name=name), reason="equipment is not fitted")
    registers = REGISTERS[equipment]
    bits = set()
    for index, entry in enumerate(entries):
        item = Section(path=f"{faults.key(name=name)}[{index}]", data=entry)
        register = item.required_integer(name="register", minimum=0)
        bit = item.required_integer(
            name="bit", minimum=0, maximum=BITS_PER_REGISTER - 1
        )
        item.finish()
        if register not in registers:
            allowed = ", ".join(hex_address(address=known) for known in registers)
            raise ScenarioError(
                key=item.key(name="register"), reason=f"must be one of {allowed}"
            )
        bits.add(FaultBit(register=register, bit=bit))
    return frozenset(bits)


def _parse_packs(*, faults: Section, pack_count: int) -> tuple[PackCodes, ...]:
    entries = faults.items(name="packs", default=[])
    if entries and not pack_count:
        raise ScenarioError(key=faults.key(name="packs"), reason="no battery fitted")
    codes = []
    for index, entry in enumerate(entries):
        item = Section(path=f"{faults.key(name='packs')}[{index}]", data=entry)
        pack = item.required_integer(name="pack", minimum=1, maximum=pack_count)
        fault = item.integer(name="fault", default=0, minimum=0, maximum=WORD_MAXIMUM)
        warning = item.integer(
            name="warning", default=0, minimum=0, maximum=WORD_MAXIMUM
        )
        item.finish()
        codes.append(PackCodes(pack=pack, fault=fault, warning=warning))
    return tuple(sorted(codes))


def _parse_faults(
    *,
    root: Section,
    device: DeviceConfig,
    battery: BatteryConfig,
    ev_charger: EvChargerConfig,
) -> FaultState:
    section = root.section(name="faults")
    pack_count = min(battery.modules, device.model.max_fault_packs)
    state = FaultState(
        inverter=_parse_fault_bits(
            faults=section, equipment=Equipment.INVERTER, fitted=True
        ),
        battery=_parse_fault_bits(
            faults=section, equipment=Equipment.BATTERY, fitted=bool(battery.modules)
        ),
        ev_charger=_parse_fault_bits(
            faults=section, equipment=Equipment.EV_CHARGER, fitted=ev_charger.installed
        ),
        packs=_parse_packs(faults=section, pack_count=pack_count),
    )
    section.finish()
    return state


def _parse_refused_blocks(*, section: Section) -> tuple[RefusedBlock, ...]:
    blocks = []
    for index, entry in enumerate(section.items(name=REFUSED_BLOCKS, default=[])):
        item = Section(path=f"{section.key(name=REFUSED_BLOCKS)}[{index}]", data=entry)
        start = item.required_integer(
            name="start", minimum=ADDRESS_BOUNDS[0], maximum=ADDRESS_BOUNDS[1]
        )
        end = item.required_integer(
            name="end", minimum=ADDRESS_BOUNDS[0], maximum=ADDRESS_BOUNDS[1]
        )
        code = item.required_integer(
            name="code", minimum=CODE_BOUNDS[0], maximum=CODE_BOUNDS[1]
        )
        item.finish()
        if end < start:
            raise ScenarioError(key=item.key(name="end"), reason="must be >= start")
        blocks.append(RefusedBlock(start=start, end=end, code=code))
    return tuple(blocks)


def _parse_link(*, root: Section) -> LinkSettings:
    section = root.section(name="link")
    values: dict[str, Any] = {}
    for parameter in LINK_PARAMETERS:
        if parameter.kind is Kind.FLAG:
            values[parameter.name] = section.boolean(name=parameter.name, default=False)
        elif parameter.kind is Kind.PERCENT:
            values[parameter.name] = section.number(
                name=parameter.name,
                default=0,
                minimum=parameter.minimum or 0,
                maximum=parameter.maximum,
            )
        else:
            values[parameter.name] = section.integer(
                name=parameter.name,
                default=0,
                minimum=parameter.minimum or 0,
                maximum=parameter.maximum,
            )
    values[REFUSED_BLOCKS] = _parse_refused_blocks(section=section)
    section.finish()
    settings = LinkSettings(**values)
    problem = check_combination(settings=settings)
    if problem is not None:
        raise ScenarioError(key=f"link.{problem[0]}", reason=problem[1])
    return settings


def parse_scenario(*, data: object) -> Scenario:
    root = Section(path="", data=data)
    device = _parse_device(root=root)
    battery = _parse_battery(root=root, device=device)
    ev_charger = _parse_ev_charger(root=root, device=device)
    scenario = Scenario(
        device=device,
        server=_parse_server(root=root),
        simulation=_parse_simulation(root=root),
        site=_parse_site(root=root, device=device),
        battery=battery,
        meters=_parse_meters(root=root),
        ev_charger=ev_charger,
        parallel=_parse_parallel(root=root),
        variation=_parse_variation(root=root),
        faults=_parse_faults(
            root=root, device=device, battery=battery, ev_charger=ev_charger
        ),
        link=_parse_link(root=root),
    )
    root.finish()
    return scenario


def load_scenario(*, path: Path) -> Scenario:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ScenarioError(key=str(path), reason="cannot be read") from error
    except yaml.YAMLError as error:
        raise ScenarioError(key=str(path), reason="is not valid YAML") from error
    return parse_scenario(data=data)


class _Register(int):
    """A register address, written in hex like the fault tables print it."""


class _ScenarioDumper(yaml.SafeDumper):
    pass


def _represent_register(dumper: yaml.SafeDumper, value: _Register) -> yaml.ScalarNode:
    return dumper.represent_scalar("tag:yaml.org,2002:int", hex_address(address=value))


_ScenarioDumper.add_representer(_Register, _represent_register)


def _bit_entries(*, bits: frozenset[FaultBit]) -> list[dict[str, int]]:
    return [
        {"register": _Register(fault.register), "bit": fault.bit}
        for fault in sorted(bits)
    ]


def _dump_faults(*, faults: FaultState) -> dict[str, Any]:
    return {
        Equipment.INVERTER.value: _bit_entries(bits=faults.inverter),
        Equipment.BATTERY.value: _bit_entries(bits=faults.battery),
        Equipment.EV_CHARGER.value: _bit_entries(bits=faults.ev_charger),
        "packs": [
            {"pack": codes.pack, "fault": codes.fault, "warning": codes.warning}
            for codes in faults.packs
        ],
    }


def _dump_sections(*, scenario: Scenario) -> dict[str, Any]:
    server = scenario.server
    simulation = scenario.simulation
    site = scenario.site
    return {
        "device": {
            "model": scenario.device.model.name,
            "rated_power_w": scenario.device.rated_power_w,
            "serial_number": scenario.device.serial_number,
        },
        "server": {
            "port": server.port,
            "unit_id": server.unit_id,
            "max_clients": server.max_clients,
            "panel_port": server.panel_port,
        },
        "simulation": {
            "seed": simulation.seed,
            "start": simulation.start.replace(tzinfo=None).isoformat(),
            "speed": simulation.speed,
        },
        "site": {
            "grid_connected": site.grid_connected,
            "pv_strings": [{"peak_power_w": peak} for peak in site.pv_strings],
            "load": dataclasses.asdict(site.load),
        },
        "battery": dataclasses.asdict(scenario.battery),
        "meters": dataclasses.asdict(scenario.meters),
        "ev_charger": {
            "installed": scenario.ev_charger.installed,
            "phases": scenario.ev_charger.phases,
            "max_power_w": scenario.ev_charger.max_power_w,
            "sessions": [
                {
                    "plug_in": session.plug_in.strftime(TIME_OF_DAY_FORMAT),
                    "unplug": session.unplug.strftime(TIME_OF_DAY_FORMAT),
                    "energy_needed_wh": session.energy_needed_wh,
                }
                for session in scenario.ev_charger.sessions
            ],
        },
        "parallel": dataclasses.asdict(scenario.parallel),
        "variation": dataclasses.asdict(scenario.variation),
        "faults": _dump_faults(faults=scenario.faults),
        "link": link_values(settings=scenario.link),
    }


def dump_scenario(*, scenario: Scenario) -> str:
    """The scenario as YAML that `parse_scenario` reads back to the same scenario."""
    return yaml.dump(
        _dump_sections(scenario=scenario),
        Dumper=_ScenarioDumper,
        sort_keys=False,
    )
