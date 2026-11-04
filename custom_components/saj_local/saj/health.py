from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .models import FunctionCode

if TYPE_CHECKING:
    from collections.abc import Collection, Mapping, Sequence

    from .catalogue import Row

REFUSAL_THRESHOLD = 3
RETEST_PERIOD = 24 * 60 * 60


def tracked_refusals(
    *,
    tracked: Collection[str],
    suspended: Collection[str],
    enabled: Collection[str],
    answered: Collection[str],
) -> frozenset[str]:
    return frozenset(
        key for key in (*tracked, *suspended) if key in enabled and key not in answered
    )


@dataclass(frozen=True)
class Refusal:
    count: int
    code: int
    retest_at: float | None
    function: FunctionCode = FunctionCode.HOLDING


@dataclass(frozen=True)
class Break:
    before: int
    after: int

    def crossed_by(self, *, start: int, end: int) -> bool:
        return start < self.before < end or start < self.after < end


@dataclass(frozen=True)
class Region:
    rows: tuple[Row, ...]

    @property
    def hull(self) -> Break:
        return Break(
            before=min(row.address for row in self.rows),
            after=max(row.end for row in self.rows),
        )


@dataclass
class _Link:
    gap: Break
    cleared: bool = False
    dead: bool = False


@dataclass
class _Narrowing:
    rows: list[Row]
    link: _Link | None


def halves(rows: Collection[Row]) -> tuple[list[Row], list[Row]]:
    ordered = sorted(rows, key=lambda row: (row.address, row.words))
    middle = (ordered[0].address + ordered[-1].end) / 2
    index = min(
        range(1, len(ordered)),
        key=lambda candidate: abs(
            (ordered[candidate - 1].end + ordered[candidate].address) / 2 - middle
        ),
    )
    return ordered[:index], ordered[index:]


class ReadHealth:
    def __init__(self) -> None:
        self._refusals: dict[str, Refusal] = {}
        self._narrowing: list[_Narrowing] = []
        self._breaks: set[Break] = set()

    @property
    def narrowing(self) -> tuple[Region, ...]:
        return tuple(
            Region(rows=tuple(narrowing.rows)) for narrowing in self._narrowing
        )

    @property
    def breaks(self) -> frozenset[Break]:
        return frozenset(self._breaks)

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

    def record_refusal(
        self,
        *,
        key: str,
        code: int,
        now: float,
        function: FunctionCode = FunctionCode.HOLDING,
    ) -> bool:
        previous = self._refusals.get(key)
        count = 1 if previous is None else previous.count + 1
        suspended = count >= REFUSAL_THRESHOLD
        self._refusals[key] = Refusal(
            count=count,
            code=code,
            retest_at=now + RETEST_PERIOD if suspended else None,
            function=function,
        )
        return suspended and (previous is None or previous.retest_at is None)

    def record_success(self, *, key: str) -> bool:
        previous = self._refusals.pop(key, None)
        return previous is not None and previous.retest_at is not None

    def record_request_refused(
        self,
        *,
        rows: Sequence[Row],
        keys: Collection[str],
        code: int,
        now: float,
    ) -> frozenset[str]:
        self._detach(rows=rows)
        function = rows[0].function
        if len(rows) > 1:
            for key in keys:
                self._mark_unavailable(key=key, code=code, function=function)
            lower, upper = halves(rows)
            link = _Link(gap=Break(before=lower[-1].end, after=upper[0].address))
            self._narrowing.extend(
                [_Narrowing(rows=lower, link=link), _Narrowing(rows=upper, link=link)]
            )
            return frozenset()
        self._narrowing.append(_Narrowing(rows=list(rows), link=None))
        return frozenset(
            key
            for key in keys
            if self.record_refusal(key=key, code=code, now=now, function=function)
        )

    def record_request_read(self, *, rows: Sequence[Row]) -> None:
        read = set(rows)
        for narrowing in tuple(self._narrowing):
            if read.isdisjoint(narrowing.rows):
                continue
            narrowing.rows = [row for row in narrowing.rows if row not in read]
            if not narrowing.rows:
                self._clear(narrowing=narrowing)

    def _clear(self, *, narrowing: _Narrowing) -> None:
        self._narrowing.remove(narrowing)
        link = narrowing.link
        if link is None or link.dead:
            return
        if link.cleared:
            self._breaks.add(link.gap)
        link.cleared = True

    def _detach(self, *, rows: Sequence[Row]) -> None:
        detached = set(rows)
        for narrowing in tuple(self._narrowing):
            if detached.isdisjoint(narrowing.rows):
                continue
            narrowing.rows = [row for row in narrowing.rows if row not in detached]
            if narrowing.link is not None:
                narrowing.link.dead = True
            if not narrowing.rows:
                self._narrowing.remove(narrowing)

    def _mark_unavailable(self, *, key: str, code: int, function: FunctionCode) -> None:
        previous = self._refusals.get(key)
        self._refusals[key] = Refusal(
            count=0 if previous is None else previous.count,
            code=code,
            retest_at=None if previous is None else previous.retest_at,
            function=function,
        )
