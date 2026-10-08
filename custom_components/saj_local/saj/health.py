from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

REFUSAL_THRESHOLD = 3
RETEST_PERIOD = 24 * 60 * 60


@dataclass(frozen=True)
class Refusal:
    count: int
    code: int
    retest_at: float | None


class ReadHealth:
    def __init__(self) -> None:
        self._refusals: dict[str, Refusal] = {}

    @property
    def refusals(self) -> Mapping[str, Refusal]:
        return dict(self._refusals)

    def refused(self) -> frozenset[str]:
        return frozenset(self._refusals)

    def suspended(self) -> frozenset[str]:
        return frozenset(
            key
            for key, refusal in self._refusals.items()
            if refusal.retest_at is not None
        )

    def retests_due(self, *, now: float) -> frozenset[str]:
        return frozenset(
            key
            for key, refusal in self._refusals.items()
            if refusal.retest_at is not None and refusal.retest_at <= now
        )

    def record_refusal(self, *, key: str, code: int, now: float) -> bool:
        previous = self._refusals.get(key)
        count = 1 if previous is None else previous.count + 1
        suspended = count >= REFUSAL_THRESHOLD
        self._refusals[key] = Refusal(
            count=count,
            code=code,
            retest_at=now + RETEST_PERIOD if suspended else None,
        )
        return suspended and (previous is None or previous.retest_at is None)

    def record_success(self, *, key: str) -> bool:
        previous = self._refusals.pop(key, None)
        return previous is not None and previous.retest_at is not None
