from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping
    from datetime import date, datetime

SECONDS_PER_HOUR = 3_600
WH_PER_KWH = 1_000.0
PERIODS = ("today", "month", "year", "total")


class EnergyLedger:
    """Lifetime energy per flow; shorter periods are deltas from period starts."""

    def __init__(
        self, *, initial_totals_wh: Mapping[str, float], moment: datetime
    ) -> None:
        self._totals = dict(initial_totals_wh)
        self._starts = {period: dict(self._totals) for period in PERIODS[:-1]}
        self._date = moment.date()

    def _roll(self, *, today: date) -> None:
        if today == self._date:
            return
        self._starts["today"] = dict(self._totals)
        if (today.year, today.month) != (self._date.year, self._date.month):
            self._starts["month"] = dict(self._totals)
        if today.year != self._date.year:
            self._starts["year"] = dict(self._totals)
        self._date = today

    def add(
        self, *, flows_w: Mapping[str, float], dt_s: float, moment: datetime
    ) -> None:
        self._roll(today=moment.date())
        for flow, power_w in flows_w.items():
            self._totals[flow] += power_w * dt_s / SECONDS_PER_HOUR

    def align(self, *, moment: datetime) -> None:
        self._starts = {period: dict(self._totals) for period in PERIODS[:-1]}
        self._date = moment.date()

    def kwh(self, *, flow: str, period: str) -> float:
        total = self._totals[flow]
        if period == "total":
            return total / WH_PER_KWH
        return (total - self._starts[period][flow]) / WH_PER_KWH

    def clear(self) -> None:
        for flow in self._totals:
            self._totals[flow] = 0.0
        self._starts = {period: dict(self._totals) for period in PERIODS[:-1]}
