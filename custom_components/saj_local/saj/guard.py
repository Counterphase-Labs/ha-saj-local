from __future__ import annotations

from .budget import RequestBudget

BACKOFF_CAP = 300


class EndpointGuard:
    def __init__(self) -> None:
        self.budget = RequestBudget()
        self.consecutive_failures = 0
        self.backoff_delay = 0.0
        self._next_attempt = 0.0

    def failed(self, *, now: float, base_delay: float) -> float:
        delay = min(base_delay * 2**self.consecutive_failures, BACKOFF_CAP)
        self.consecutive_failures += 1
        self.backoff_delay = delay
        self._next_attempt = now + delay
        return delay

    def succeeded(self) -> None:
        self.consecutive_failures = 0
        self.backoff_delay = 0.0
        self._next_attempt = 0.0

    def retry_in(self, *, now: float) -> float:
        return max(0.0, self._next_attempt - now)
