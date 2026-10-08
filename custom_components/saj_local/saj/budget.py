from __future__ import annotations

import math
from collections import deque
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

REQUEST_BUDGET = 40
BUDGET_WINDOW = 60.0
SECONDS_PER_MINUTE = 60
BUDGET_PER_MINUTE = REQUEST_BUDGET * SECONDS_PER_MINUTE / BUDGET_WINDOW


class RequestBudget:
    def __init__(
        self, *, limit: int = REQUEST_BUDGET, window: float = BUDGET_WINDOW
    ) -> None:
        self.limit = limit
        self.window = window
        self._sent: deque[float] = deque()

    def delay(self, *, now: float) -> float:
        self._expire(now=now)
        if len(self._sent) < self.limit:
            return 0.0
        return self._sent[len(self._sent) - self.limit] + self.window - now

    def record(self, *, now: float) -> None:
        self._expire(now=now)
        self._sent.append(now)

    def worst_case_delay(self, *, requests: int) -> float:
        return math.ceil(requests / self.limit) * self.window

    def _expire(self, *, now: float) -> None:
        while self._sent and self._sent[0] <= now - self.window:
            self._sent.popleft()


def requests_per_minute(*, reads: Iterable[tuple[int, int]]) -> float:
    return sum(requests * SECONDS_PER_MINUTE / interval for interval, requests in reads)
