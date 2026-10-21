from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping
    from datetime import date, datetime

SECONDS_PER_HOUR = 3_600
WH_PER_KWH = 1_000.0
PERIODS = ("today", "month", "year", "total")
STARTED_PERIODS = PERIODS[:-1]


class EnergyLedger:
    """Lifetime energy per flow; shorter periods are deltas from period starts."""

    def __init__(
        self, *, initial_totals_wh: Mapping[str, float], moment: datetime
    ) -> None:
        self._initial = dict(initial_totals_wh)
        self._totals = dict(initial_totals_wh)
        self._starts = {period: dict(self._totals) for period in STARTED_PERIODS}
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
        self._starts = {period: dict(self._totals) for period in STARTED_PERIODS}
        self._date = moment.date()

    def kwh(self, *, flow: str, period: str) -> float:
        total = self._totals[flow]
        if period == "total":
            return total / WH_PER_KWH
        return (total - self._starts[period][flow]) / WH_PER_KWH

    def totals_wh(self) -> dict[str, float]:
        return dict(self._totals)

    def starts_wh(self) -> dict[str, dict[str, float]]:
        return {period: dict(starts) for period, starts in self._starts.items()}

    @property
    def day(self) -> date:
        return self._date

    def restore(
        self,
        *,
        totals_wh: Mapping[str, float],
        moment: datetime,
        starts_wh: Mapping[str, Mapping[str, float]] | None = None,
        day: date | None = None,
    ) -> None:
        """Take saved totals for the flows this ledger counts.

        Saved period starts keep today, month and year running across a restart;
        without them the periods start from the restored totals.
        """
        for flow in self._totals:
            self._totals[flow] = float(totals_wh.get(flow, self._totals[flow]))
        if starts_wh is None or day is None:
            self.align(moment=moment)
            return
        self._starts = {
            period: {
                flow: float(starts_wh[period].get(flow, total))
                for flow, total in self._totals.items()
            }
            for period in STARTED_PERIODS
        }
        self._date = day

    def reset(self, *, moment: datetime) -> None:
        """Back to the start values the ledger was created with."""
        self._totals = dict(self._initial)
        self.align(moment=moment)

    def clear(self) -> None:
        for flow in self._totals:
            self._totals[flow] = 0.0
        self._starts = {period: dict(self._totals) for period in STARTED_PERIODS}
