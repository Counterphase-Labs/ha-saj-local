from __future__ import annotations

from .budget import RequestBudget, WriteAllowance

BACKOFF_CAP = 300


class EndpointGuard:
    def __init__(self) -> None:
        self.budget = RequestBudget()
        self.allowance = WriteAllowance()
        self.consecutive_failures = 0
        self.backoff_delay = 0.0
        self._next_attempt = 0.0
        self._failing_since: float | None = None

    def failed(self, *, now: float, base_delay: float) -> float:
        delay = min(base_delay * 2**self.consecutive_failures, BACKOFF_CAP)
        self.consecutive_failures += 1
        if self._failing_since is None:
            self._failing_since = now
        self.backoff_delay = delay
        self._next_attempt = now + delay
        return delay

    def succeeded(self) -> None:
        self.consecutive_failures = 0
        self.backoff_delay = 0.0
        self._next_attempt = 0.0
        self._failing_since = None

    def failing_for(self, *, now: float) -> float | None:
        if self._failing_since is None:
            return None
        return now - self._failing_since

    def retry_in(self, *, now: float) -> float:
        return max(0.0, self._next_attempt - now)
