from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import IntEnum, StrEnum
from typing import TYPE_CHECKING

from .faults import FaultMap

if TYPE_CHECKING:
    from collections.abc import Mapping

SINGLE_WORD_REQUEST = 1
DERIVED_PLACEMENTS: Mapping[str, None] = dict.fromkeys(
    (
        "battery_time_to_full",
        "battery_time_to_empty",
        "battery_stored_energy",
        "battery_available_energy",
        "self_sufficiency_today",
        "self_consumption_today",
        "solar_surplus_power",
        "battery_round_trip_efficiency",
    )
)


class Equipment(StrEnum):
    BATTERY = "battery"
    METER_A = "meter_a"
    METER_B = "meter_b"
    EV_CHARGER = "ev_charger"
    PARALLEL = "parallel"


ALL_EQUIPMENT = frozenset(Equipment)
ENABLED_WITHOUT_EVIDENCE = frozenset(
    {
        Equipment.METER_A,
        Equipment.METER_B,
        Equipment.EV_CHARGER,
        Equipment.PARALLEL,
    }
)


class PowerFunction(StrEnum):
    BATTERY = "battery"
    GRID = "grid"
    INVERTER = "inverter"

    @property
    def switch_key(self) -> str:
        return f"{self.value}_power_control"

    @property
    def target_key(self) -> str:
        return f"{self.value}_power_target"


@dataclass(frozen=True)
class EnableBitMethod:
    enable_key: str
    target_key: str
    alternate_keys: tuple[str, ...] = ()
    timeout_key: str | None = None
    limit_keys: tuple[str, ...] = ()

    @property
    def forms(self) -> tuple[str, ...]:
        return (self.enable_key, *self.alternate_keys)

    @property
    def stop_keys(self) -> frozenset[str]:
        return frozenset(self.forms)

    @property
    def row_keys(self) -> frozenset[str]:
        return frozenset({self.enable_key, self.target_key})

    def accepts_stop(self, *, key: str, value: object) -> bool:
        return key in self.forms and value == 0


@dataclass(frozen=True)
class OperatingModeMethod:
    mode_key: str
    passive_mode: int
    default_mode: int
    direction_key: str
    standby: int
    discharge: int
    charge: int
    charge_power_key: str
    discharge_power_key: str

    @property
    def stop_keys(self) -> frozenset[str]:
        return frozenset({self.mode_key, self.direction_key})

    def accepts_stop(self, *, key: str, value: object) -> bool:
        if key == self.direction_key:
            return value == self.standby
        return key == self.mode_key and value != self.passive_mode

    @property
    def row_keys(self) -> frozenset[str]:
        return frozenset(
            {
                self.mode_key,
                self.direction_key,
                self.charge_power_key,
                self.discharge_power_key,
            }
        )


PowerMethod = EnableBitMethod | OperatingModeMethod


@dataclass(frozen=True)
class EmsRows:
    functions: Mapping[str, PowerFunction]
    forms: Mapping[str, tuple[str, ...]]
    targets: Mapping[PowerFunction, str]
    timeouts: frozenset[str]
    limits: frozenset[str]

    @property
    def target_functions(self) -> dict[str, PowerFunction]:
        return {key: function for function, key in self.targets.items()}


def ems_rows(*, profile: Profile) -> EmsRows:
    methods = {
        function: method
        for function, method in profile.power_control.items()
        if isinstance(method, EnableBitMethod)
    }
    return EmsRows(
        functions={
            key: function
            for function, method in methods.items()
            for key in method.forms
        },
        forms={
            key: method.forms for method in methods.values() for key in method.forms
        },
        targets={function: method.target_key for function, method in methods.items()},
        timeouts=frozenset(
            method.timeout_key for method in methods.values() if method.timeout_key
        ),
        limits=frozenset(
            key for method in methods.values() for key in method.limit_keys
        ),
    )


class Comparison(StrEnum):
    EQUALS = "equals"
    DIFFERS = "differs"
    ABOVE = "above"


@dataclass(frozen=True)
class Condition:
    key: str
    comparison: Comparison
    reference: int


@dataclass(frozen=True)
class Probe:
    equipment: Equipment
    conditions: tuple[Condition, ...]
    unanswered: bool

    @property
    def keys(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(condition.key for condition in self.conditions))


METER_A_PROBE = Probe(
    equipment=Equipment.METER_A,
    conditions=(
        Condition(key="meter_a_status", comparison=Comparison.EQUALS, reference=1),
    ),
    unanswered=True,
)
METER_B_PROBE = Probe(
    equipment=Equipment.METER_B,
    conditions=(
        Condition(key="meter_b_status", comparison=Comparison.EQUALS, reference=1),
    ),
    unanswered=False,
)
PARALLEL_PROBE = Probe(
    equipment=Equipment.PARALLEL,
    conditions=(
        Condition(key="parallel_mode", comparison=Comparison.DIFFERS, reference=0),
        Condition(
            key="parallel_online_count", comparison=Comparison.ABOVE, reference=1
        ),
    ),
    unanswered=False,
)


class Evidence(StrEnum):
    VERIFIED = "verified"
    RESPONDS_UNCHECKED = "responds_unchecked"
    RESPONDS_UNDOCUMENTED = "responds_undocumented"
    DOCUMENTED = "documented"
    IMPLEMENTED = "implemented"


ENABLING_EVIDENCE = frozenset({Evidence.VERIFIED, Evidence.IMPLEMENTED})


@dataclass(frozen=True)
class Shape:
    phases: int
    strings: int
    assumed: bool = False


SINGLE_PHASE_SINGLE_STRING = Shape(phases=1, strings=1)


class FunctionCode(IntEnum):
    HOLDING = 0x03
    INPUT = 0x04


@dataclass(frozen=True)
class Span:
    name: str
    first: int
    last: int
    function: FunctionCode = FunctionCode.HOLDING

    def contains(self, *, address: int, words: int) -> bool:
        return self.first <= address and address + words - 1 <= self.last

    def overlaps(self, *, address: int, words: int) -> bool:
        return address <= self.last and self.first <= address + words - 1


@dataclass(frozen=True)
class Placement:
    key: str
    address: int | None
    evidence: Evidence


@dataclass(frozen=True)
class FamilyPlacement:
    family: str
    evidence: Evidence
    count: int | None = None
    base: int | None = None
    exceptions: Mapping[str, Evidence] = field(default_factory=dict)


@dataclass(frozen=True)
class Replacement:
    key: str
    range: tuple[float, float] | None = None
    options: Mapping[int, str] | None = None
    encoding: str | None = None
    scale: float | None = None
    uncombined: bool = False
    sum_of: tuple[str, ...] = ()
    equipment: Equipment | None = None


@dataclass(frozen=True)
class Profile:
    key: str
    display_name: str
    device_types: Mapping[int, Shape]
    hand_verified: bool
    usable_capacity: bool = False
    off_grid_discharge_limit: bool = False
    maximum_shape: Shape = SINGLE_PHASE_SINGLE_STRING
    largest_request: int = SINGLE_WORD_REQUEST
    spans: tuple[Span, ...] = field(default_factory=tuple)
    placements: tuple[Placement, ...] = field(default_factory=tuple)
    families: tuple[FamilyPlacement, ...] = field(default_factory=tuple)
    replacements: tuple[Replacement, ...] = field(default_factory=tuple)
    probes: tuple[Probe, ...] = field(default_factory=tuple)
    power_control: Mapping[PowerFunction, PowerMethod] = field(default_factory=dict)
    faults: FaultMap = field(default_factory=FaultMap)

    @property
    def equipment(self) -> frozenset[Equipment]:
        return frozenset(probe.equipment for probe in self.probes)

    def shape_of(self, *, device_type: int) -> Shape:
        recognised = self.device_types.get(device_type)
        if recognised is not None:
            return recognised
        return replace(self.maximum_shape, assumed=True)


def placements_by_evidence(
    *, groups: Mapping[Evidence, Mapping[str, int | None]]
) -> tuple[Placement, ...]:
    return tuple(
        Placement(key=key, address=address, evidence=evidence)
        for evidence, addresses in groups.items()
        for key, address in addresses.items()
    )
