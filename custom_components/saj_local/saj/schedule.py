from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Collection, Iterable

MIN_INTERVAL = 10


class DuplicateKeyError(Exception):
    def __init__(self, keys: Collection[str]) -> None:
        super().__init__(f"Sensors claimed by more than one cadence: {sorted(keys)}")
        self.keys = frozenset(keys)


@dataclass(frozen=True)
class Cadence:
    interval: int
    keys: frozenset[str]
    default: bool = False


def build_cadences(
    *,
    default_interval: int,
    groups: Iterable[Cadence],
    supported: Collection[str],
) -> tuple[Cadence, ...]:
    available = frozenset(supported)
    claimed: set[str] = set()
    grouped: list[Cadence] = []
    for group in groups:
        if duplicated := claimed & group.keys:
            raise DuplicateKeyError(duplicated)
        claimed |= group.keys
        if keys := available & group.keys:
            grouped.append(Cadence(interval=group.interval, keys=keys))
    remainder = available - claimed
    if remainder:
        return (
            Cadence(interval=default_interval, keys=remainder, default=True),
            *grouped,
        )
    return tuple(grouped)


class Schedule:
    def __init__(self, *, cadences: Iterable[Cadence], origin: float) -> None:
        self.cadences = tuple(cadences)
        self._origin = origin
        self._served = [-1] * len(self.cadences)
        self.shortest_interval = min(
            (cadence.interval for cadence in self.cadences), default=MIN_INTERVAL
        )
        self._full_read = False

    def due_cadences(self, *, now: float) -> tuple[Cadence, ...]:
        return tuple(
            cadence
            for index, cadence in enumerate(self.cadences)
            if self._full_read
            or self._tick(cadence=cadence, now=now) > self._served[index]
        )

    def due(self, *, now: float) -> frozenset[str]:
        return frozenset().union(
            *(cadence.keys for cadence in self.due_cadences(now=now))
        )

    def mark_read(self, *, now: float) -> None:
        self._full_read = False
        for index, cadence in enumerate(self.cadences):
            self._served[index] = max(
                self._served[index], self._tick(cadence=cadence, now=now)
            )

    def next_due(self, *, now: float, enabled: Collection[str]) -> float | None:
        targets = [
            self._origin + (self._served[index] + 1) * cadence.interval
            for index, cadence in enumerate(self.cadences)
            if not cadence.keys.isdisjoint(enabled)
        ]
        if not targets:
            return None
        return max(now, min(targets))

    def require_full_read(self) -> None:
        self._full_read = True

    def _tick(self, *, cadence: Cadence, now: float) -> int:
        return math.floor((now - self._origin) / cadence.interval)
