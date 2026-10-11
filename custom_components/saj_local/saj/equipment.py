from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

from .models import Comparison

if TYPE_CHECKING:
    from collections.abc import Collection, Mapping

    from .codec import Value
    from .models import Condition, Equipment, Probe


BATTERY_PACK_COUNT = "battery_pack_count"


class Setting(StrEnum):
    AUTOMATIC = "automatic"
    FITTED = "fitted"
    NOT_FITTED = "not_fitted"


@dataclass(frozen=True)
class Detection:
    equipment: Equipment
    fitted: bool
    answered: bool
    values: Mapping[str, Value]


@dataclass(frozen=True)
class Outcome:
    fitted: frozenset[Equipment]
    remembered: frozenset[Equipment]
    lapsed: frozenset[Equipment]


def met(*, condition: Condition, value: Value) -> bool:
    if not isinstance(value, int | float):
        return False
    if condition.comparison is Comparison.EQUALS:
        return value == condition.reference
    if condition.comparison is Comparison.DIFFERS:
        return value != condition.reference
    return value > condition.reference


def evaluate(*, probe: Probe, values: Mapping[str, Value]) -> Detection:
    answered = [
        condition
        for condition in probe.conditions
        if isinstance(values.get(condition.key), int | float)
    ]
    if not answered:
        return Detection(
            equipment=probe.equipment,
            fitted=probe.unanswered,
            answered=False,
            values=values,
        )
    return Detection(
        equipment=probe.equipment,
        fitted=any(
            met(condition=condition, value=values[condition.key])
            for condition in answered
        ),
        answered=True,
        values=values,
    )


def valid_pack_count(*, reading: Value, maximum: int) -> int | None:
    if isinstance(reading, int) and 1 <= reading <= maximum:
        return reading
    return None


def next_pack_limit(
    *, stored: int | None, reading: Value, maximum: int, battery: Setting
) -> int | None:
    if battery is Setting.NOT_FITTED:
        return None
    counted = valid_pack_count(reading=reading, maximum=maximum)
    if counted is None:
        return stored
    return max(stored or 0, counted)


def to_probe(
    *, settings: Mapping[Equipment, Setting], equipment: Collection[Equipment]
) -> frozenset[Equipment]:
    return frozenset(
        item
        for item in equipment
        if settings.get(item, Setting.AUTOMATIC) is Setting.AUTOMATIC
    )


def stored_fitted(
    *,
    equipment: Collection[Equipment],
    settings: Mapping[Equipment, Setting],
    resolved: Collection[Equipment],
) -> frozenset[Equipment]:
    return frozenset(
        item
        for item in equipment
        if _setting_of(settings=settings, item=item) is Setting.FITTED
        or (
            _setting_of(settings=settings, item=item) is Setting.AUTOMATIC
            and item in resolved
        )
    )


def resolve(
    *,
    equipment: Collection[Equipment],
    settings: Mapping[Equipment, Setting],
    remembered: Collection[Equipment],
    detections: Mapping[Equipment, Detection],
) -> Outcome:
    fitted: set[Equipment] = set()
    kept: set[Equipment] = set(remembered) & set(equipment)
    lapsed: set[Equipment] = set()
    for item in equipment:
        setting = _setting_of(settings=settings, item=item)
        if setting is Setting.NOT_FITTED:
            kept.discard(item)
        elif setting is Setting.FITTED:
            fitted.add(item)
        elif detections[item].fitted:
            fitted.add(item)
            if detections[item].answered:
                kept.add(item)
        elif item in kept:
            fitted.add(item)
            lapsed.add(item)
    return Outcome(
        fitted=frozenset(fitted),
        remembered=frozenset(kept),
        lapsed=frozenset(lapsed),
    )


def _setting_of(*, settings: Mapping[Equipment, Setting], item: Equipment) -> Setting:
    return settings.get(item, Setting.AUTOMATIC)
