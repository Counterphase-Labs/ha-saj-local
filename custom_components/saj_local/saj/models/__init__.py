from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

SINGLE_WORD_REQUEST = 1


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


@dataclass(frozen=True)
class Span:
    name: str
    first: int
    last: int

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


@dataclass(frozen=True)
class Profile:
    key: str
    display_name: str
    device_types: Mapping[int, Shape]
    hand_verified: bool
    maximum_shape: Shape = SINGLE_PHASE_SINGLE_STRING
    largest_request: int = SINGLE_WORD_REQUEST
    spans: tuple[Span, ...] = field(default_factory=tuple)
    placements: tuple[Placement, ...] = field(default_factory=tuple)
    families: tuple[FamilyPlacement, ...] = field(default_factory=tuple)
    replacements: tuple[Replacement, ...] = field(default_factory=tuple)
    probes: tuple[Probe, ...] = field(default_factory=tuple)

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
