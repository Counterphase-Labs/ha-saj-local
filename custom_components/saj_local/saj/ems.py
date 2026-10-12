from __future__ import annotations

from typing import TYPE_CHECKING

from .codec import require_number
from .control import Inspection
from .errors import EmsTimeoutError
from .models import PowerFunction

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence

    from .codec import Value
    from .models import EmsRows

DEFAULT_HEARTBEAT_INTERVAL = 60
MIN_HEARTBEAT_INTERVAL = 30
MAX_HEARTBEAT_INTERVAL = 3600
NO_TIMEOUT = 0xFFFF
TIMEOUT_WORDS = 1


def valid_heartbeat_interval(*, seconds: int) -> bool:
    return MIN_HEARTBEAT_INTERVAL <= seconds <= MAX_HEARTBEAT_INTERVAL


def check_timeout(*, timeout: int, interval: int) -> None:
    if timeout != NO_TIMEOUT and timeout <= interval:
        raise EmsTimeoutError(timeout=timeout, interval=interval)


def timeout_check(*, interval: int) -> Callable[[Value], None]:
    def check(value: Value) -> None:
        check_timeout(timeout=round(require_number(value=value)), interval=interval)

    return check


def timeout_inspection(*, interval: int) -> Inspection:
    def check(words: Sequence[int]) -> None:
        (timeout,) = words
        check_timeout(timeout=timeout, interval=interval)

    return Inspection(extra_words=TIMEOUT_WORDS, check=check)


def switch_changes(*, rows: EmsRows, key: str, on: bool) -> dict[str, int]:
    partners = rows.forms.get(key, ()) if on else ()
    return {**dict.fromkeys(partners, 0), key: int(on)}


def clearing_changes(*, rows: EmsRows, key: str) -> dict[str, int]:
    return dict.fromkeys(rows.forms.get(key, (key,)), 0)


class EmsOwnership:
    def __init__(self) -> None:
        self._owned: dict[PowerFunction, str | None] = {}
        self._failing: set[PowerFunction] = set()

    @property
    def owned(self) -> frozenset[PowerFunction]:
        return frozenset(self._owned)

    def acquire(self, *, function: PowerFunction, key: str | None = None) -> None:
        self._owned[function] = key

    def release_function(
        self, *, function: PowerFunction, key: str | None = None
    ) -> None:
        if key is None or self._owned.get(function, key) in {None, key}:
            self._owned.pop(function, None)
            self._failing.discard(function)

    def found_off(
        self, *, states: Mapping[PowerFunction, bool | None]
    ) -> frozenset[PowerFunction]:
        off = frozenset(
            function for function in self._owned if states.get(function) is False
        )
        for function in off:
            self.release_function(function=function)
        return off

    def release(self) -> None:
        self._owned.clear()
        self._failing.clear()

    def beat_dropped(self, *, function: PowerFunction) -> bool:
        first = function not in self._failing
        self._failing.add(function)
        return first

    def beat_succeeded(self, *, function: PowerFunction) -> bool:
        recovered = function in self._failing
        self._failing.discard(function)
        return recovered

    def beat_keys(self, *, targets: Mapping[PowerFunction, str]) -> tuple[str, ...]:
        return tuple(
            targets[function]
            for function in PowerFunction
            if function in self._owned and function in targets
        )
