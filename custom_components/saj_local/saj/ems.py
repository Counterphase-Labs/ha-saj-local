from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

from .codec import require_number
from .control import Inspection
from .definitions import EMS_CONTROL_BITS
from .errors import EmsTimeoutError

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence

    from .codec import Value

DEFAULT_HEARTBEAT_INTERVAL = 60
MIN_HEARTBEAT_INTERVAL = 30
MAX_HEARTBEAT_INTERVAL = 3600
NO_TIMEOUT = 0xFFFF
TIMEOUT_WORDS = 1


class EmsFunction(StrEnum):
    INVERTER = "inverter"
    BATTERY = "battery"
    GRID = "grid"


@dataclass(frozen=True)
class FunctionSpec:
    enable_keys: tuple[str, ...]
    target_key: str

    @property
    def enable_bits(self) -> tuple[int, ...]:
        return tuple(EMS_CONTROL_BITS[key] for key in self.enable_keys)


FUNCTIONS: dict[EmsFunction, FunctionSpec] = {
    EmsFunction.INVERTER: FunctionSpec(
        enable_keys=("ems_inverter_control", "ems_inverter_control_with_timeout_exit"),
        target_key="ems_inverter_power_target",
    ),
    EmsFunction.BATTERY: FunctionSpec(
        enable_keys=("ems_battery_control",), target_key="ems_battery_power_target"
    ),
    EmsFunction.GRID: FunctionSpec(
        enable_keys=("ems_grid_control",), target_key="ems_grid_power_target"
    ),
}
FUNCTION_BY_ENABLE_KEY: dict[str, EmsFunction] = {
    key: function for function, spec in FUNCTIONS.items() for key in spec.enable_keys
}
FUNCTION_BY_TARGET_KEY: dict[str, EmsFunction] = {
    spec.target_key: function for function, spec in FUNCTIONS.items()
}


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


def switch_changes(*, key: str, on: bool) -> dict[str, int]:
    changes = {key: int(on)}
    function = FUNCTION_BY_ENABLE_KEY.get(key)
    if on and function is not None:
        for partner in FUNCTIONS[function].enable_keys:
            if partner != key:
                changes[partner] = 0
    return changes


class EmsOwnership:
    def __init__(self) -> None:
        self._on: set[str] = set()
        self._failing: set[EmsFunction] = set()

    @property
    def owned(self) -> frozenset[EmsFunction]:
        return frozenset(FUNCTION_BY_ENABLE_KEY[key] for key in self._on)

    @property
    def owned_enable_keys(self) -> tuple[str, ...]:
        return tuple(sorted(self._on))

    def switched(self, *, key: str, on: bool) -> None:
        function = FUNCTION_BY_ENABLE_KEY.get(key)
        if function is None:
            return
        if not on:
            self._on.discard(key)
            self._forget_failing()
            return
        self._on.difference_update(FUNCTIONS[function].enable_keys)
        self._on.add(key)

    def found_off(self, *, values: Mapping[str, Value]) -> frozenset[EmsFunction]:
        before = self.owned
        for key in self.owned_enable_keys:
            if key in values and not values[key]:
                self.switched(key=key, on=False)
        return before - self.owned

    def release(self) -> None:
        self._on.clear()
        self._failing.clear()

    def beat_dropped(self, *, target_key: str) -> bool:
        function = FUNCTION_BY_TARGET_KEY[target_key]
        first = function not in self._failing
        self._failing.add(function)
        return first

    def beat_succeeded(self, *, target_key: str) -> bool:
        function = FUNCTION_BY_TARGET_KEY[target_key]
        recovered = function in self._failing
        self._failing.discard(function)
        return recovered

    def beat_keys(self) -> tuple[str, ...]:
        return tuple(
            FUNCTIONS[function].target_key
            for function in EmsFunction
            if function in self.owned
        )

    def _forget_failing(self) -> None:
        self._failing.intersection_update(self.owned)
