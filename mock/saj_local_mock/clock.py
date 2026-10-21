from datetime import datetime, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


class Clock:
    """Simulated time, driven by an injected monotonic source so tests control it."""

    def __init__(
        self,
        *,
        start: datetime,
        speed: float,
        monotonic: Callable[[], float],
    ) -> None:
        self._speed = speed
        self._monotonic = monotonic
        self._anchor_time = start
        self._anchor_monotonic = monotonic()

    def now(self) -> datetime:
        elapsed = self._monotonic() - self._anchor_monotonic
        return self._anchor_time + timedelta(seconds=elapsed * self._speed)

    @property
    def speed(self) -> float:
        return self._speed

    def set_speed(self, *, speed: float) -> None:
        """Change the speed without moving the simulated time."""
        self.set(moment=self.now())
        self._speed = speed

    def set(self, *, moment: datetime) -> None:
        self._anchor_time = moment
        self._anchor_monotonic = self._monotonic()
