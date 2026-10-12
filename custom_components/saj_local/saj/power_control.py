from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum
from typing import TYPE_CHECKING, ClassVar

from .catalogue import device_registers
from .codec import Range, scaled
from .control import Write
from .errors import (
    AnotherFunctionRunningError,
    NoPowerTargetError,
    UnusablePowerError,
)
from .models import (
    EnableBitMethod,
    Equipment,
    OperatingModeMethod,
    PowerFunction,
)

if TYPE_CHECKING:
    from collections.abc import Collection, Mapping

    from .catalogue import Fit, Register
    from .codec import Value
    from .device import Device
    from .models import PowerMethod

PERCENT = 100
NO_RANGE = Range(minimum=0, maximum=0)
FUNCTION_EQUIPMENT: Mapping[PowerFunction, Equipment] = {
    PowerFunction.BATTERY: Equipment.BATTERY,
    PowerFunction.GRID: Equipment.METER_A,
}


@dataclass(frozen=True)
class Start:
    writes: tuple[Write, ...]
    remember: int | None = None


class FunctionControl[Method: PowerMethod](ABC):
    method_name: ClassVar[str]

    def __init__(
        self,
        *,
        function: PowerFunction,
        method: Method,
        rated_power: int,
        registers: Mapping[str, Register],
    ) -> None:
        self.function = function
        self._method = method
        self._rated_power = rated_power
        self._registers = registers

    @property
    @abstractmethod
    def state_keys(self) -> frozenset[str]: ...

    @property
    @abstractmethod
    def target_range(self) -> Range: ...

    @property
    def prior_key(self) -> str | None:
        return None

    @property
    def beat_key(self) -> str | None:
        return None

    @abstractmethod
    def running(self, *, values: Mapping[str, Value]) -> bool | None: ...

    @abstractmethod
    def held(self, *, values: Mapping[str, Value]) -> int | None: ...

    @abstractmethod
    def start(self, *, watts: int, prior: Value) -> Start: ...

    @abstractmethod
    def change(
        self, *, watts: int, values: Mapping[str, Value]
    ) -> tuple[Write, ...]: ...

    @abstractmethod
    def stop(self, *, remembered: int | None) -> tuple[Write, ...]: ...

    def usable(self, *, raw: object) -> int | None:
        if isinstance(raw, bool):
            return None
        if isinstance(raw, int):
            watts = raw
        elif isinstance(raw, float) and raw.is_integer():
            watts = int(raw)
        else:
            return None
        return watts if self.target_range.contains(value=watts) else None

    def require_usable(self, *, raw: object) -> int:
        watts = self.usable(raw=raw)
        if watts is None:
            span = self.target_range
            raise UnusablePowerError(
                minimum=int(span.minimum), maximum=int(span.maximum)
            )
        return watts

    def _share(self, *, key: str, watts: int) -> Value:
        scale = self._registers[key].scale
        raw = (
            Decimal(watts)
            * PERCENT
            / (Decimal(self._rated_power) * Decimal(repr(scale)))
        )
        return scaled(raw=int(raw.to_integral_value(ROUND_HALF_UP)), scale=scale)

    def _watts(self, *, share: float) -> int:
        return round(share * self._rated_power / PERCENT)

    def _percent_range(self, *, key: str) -> Range:
        return self._registers[key].definition.settable_range or NO_RANGE

    def _limit(self, *, percent: float) -> int:
        return int(Decimal(repr(percent)) * self._rated_power / PERCENT)


def _number(*, values: Mapping[str, Value], key: str) -> float | None:
    value = values.get(key)
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    return value


class EnableBitControl(FunctionControl[EnableBitMethod]):
    method_name = "enable_bit"

    @property
    def state_keys(self) -> frozenset[str]:
        return frozenset(self._method.forms)

    @property
    def beat_key(self) -> str:
        return self._method.target_key

    @property
    def target_range(self) -> Range:
        settable = self._percent_range(key=self._method.target_key)
        return Range(
            minimum=self._limit(percent=settable.minimum),
            maximum=self._limit(percent=settable.maximum),
        )

    def running(self, *, values: Mapping[str, Value]) -> bool | None:
        forms = [_number(values=values, key=key) for key in self._method.forms]
        if any(form for form in forms):
            return True
        return None if None in forms else False

    def held(self, *, values: Mapping[str, Value]) -> int | None:
        share = _number(values=values, key=self._method.target_key)
        return None if share is None else self._watts(share=share)

    def start(self, *, watts: int, prior: Value) -> Start:
        del prior
        enable_key = self._method.enable_key
        return Start(
            writes=(
                *self.change(watts=watts, values={}),
                Write(
                    key=enable_key,
                    value=1,
                    also=dict.fromkeys(self._method.alternate_keys, 0),
                    inspect_timeout=True,
                ),
            )
        )

    def change(self, *, watts: int, values: Mapping[str, Value]) -> tuple[Write, ...]:
        del values
        key = self._method.target_key
        return (Write(key=key, value=self._share(key=key, watts=watts)),)

    def stop(self, *, remembered: int | None) -> tuple[Write, ...]:
        del remembered
        enable_key = self._method.enable_key
        return (
            Write(
                key=enable_key,
                value=0,
                also=dict.fromkeys(self._method.alternate_keys, 0),
            ),
        )


class OperatingModeControl(FunctionControl[OperatingModeMethod]):
    method_name = "operating_mode"

    @property
    def state_keys(self) -> frozenset[str]:
        return self._method.row_keys

    @property
    def prior_key(self) -> str:
        return self._method.mode_key

    @property
    def target_range(self) -> Range:
        return Range(
            minimum=-self._reach(key=self._method.charge_power_key),
            maximum=self._reach(key=self._method.discharge_power_key),
        )

    def running(self, *, values: Mapping[str, Value]) -> bool | None:
        mode = _number(values=values, key=self._method.mode_key)
        return None if mode is None else mode == self._method.passive_mode

    def held(self, *, values: Mapping[str, Value]) -> int | None:
        direction = _number(values=values, key=self._method.direction_key)
        if direction == self._method.standby:
            return 0
        if direction == self._method.charge:
            share = _number(values=values, key=self._method.charge_power_key)
            return None if share is None else -self._watts(share=share)
        if direction == self._method.discharge:
            share = _number(values=values, key=self._method.discharge_power_key)
            return None if share is None else self._watts(share=share)
        return None

    def start(self, *, watts: int, prior: Value) -> Start:
        method = self._method
        remember = None if prior == method.passive_mode else _mode(prior=prior)
        return Start(
            writes=(
                *self._power_writes(watts=watts),
                Write(key=method.mode_key, value=method.passive_mode),
                Write(key=method.direction_key, value=self._direction(watts=watts)),
            ),
            remember=remember,
        )

    def change(self, *, watts: int, values: Mapping[str, Value]) -> tuple[Write, ...]:
        direction = self._direction(watts=watts)
        current = values.get(self._method.direction_key)
        direction_write = (
            ()
            if current == direction
            else (Write(key=self._method.direction_key, value=direction),)
        )
        return (*self._power_writes(watts=watts), *direction_write)

    def stop(self, *, remembered: int | None) -> tuple[Write, ...]:
        method = self._method
        return (
            Write(key=method.direction_key, value=method.standby),
            Write(
                key=method.mode_key,
                value=method.default_mode if remembered is None else remembered,
            ),
        )

    def _power_writes(self, *, watts: int) -> tuple[Write, ...]:
        if watts == 0:
            return ()
        key = (
            self._method.charge_power_key
            if watts < 0
            else self._method.discharge_power_key
        )
        return (Write(key=key, value=self._share(key=key, watts=abs(watts))),)

    def _direction(self, *, watts: int) -> int:
        if watts == 0:
            return self._method.standby
        return self._method.discharge if watts > 0 else self._method.charge

    def _reach(self, *, key: str) -> int:
        return self._limit(percent=self._percent_range(key=key).maximum)


def _mode(*, prior: Value) -> int | None:
    return int(prior) if isinstance(prior, int | float) else None


def _control_of(
    *,
    function: PowerFunction,
    method: PowerMethod,
    rated_power: int,
    registers: Mapping[str, Register],
) -> FunctionControl[PowerMethod]:
    if isinstance(method, EnableBitMethod):
        return EnableBitControl(
            function=function,
            method=method,
            rated_power=rated_power,
            registers=registers,
        )
    return OperatingModeControl(
        function=function, method=method, rated_power=rated_power, registers=registers
    )


def power_functions(*, fit: Fit) -> tuple[PowerFunction, ...]:
    return tuple(
        function
        for function in _constructible(fit=fit)
        if FUNCTION_EQUIPMENT.get(function, None) in {None, *fit.equipment}
    )


def _constructible(*, fit: Fit) -> tuple[PowerFunction, ...]:
    keys = {register.key for register in device_registers(fit=fit)}
    return tuple(
        function
        for function in PowerFunction
        if function in fit.profile.power_control
        and fit.profile.power_control[function].row_keys <= keys
    )


def power_controls(
    *, device: Device
) -> dict[PowerFunction, FunctionControl[PowerMethod]]:
    registers = {
        register.key: register for register in device_registers(fit=device.fit)
    }
    return {
        function: _control_of(
            function=function,
            method=device.profile.power_control[function],
            rated_power=device.rated_power,
            registers=registers,
        )
        for function in _constructible(fit=device.fit)
    }


def require_target(
    *, function: PowerFunction, targets: Mapping[PowerFunction, int]
) -> int:
    watts = targets.get(function)
    if watts is None:
        raise NoPowerTargetError(function=function)
    return watts


def require_none_running(
    *, function: PowerFunction, running: Collection[PowerFunction]
) -> None:
    for other in PowerFunction:
        if other != function and other in running:
            raise AnotherFunctionRunningError(running=other)


class Blocker(StrEnum):
    NO_TARGET = "no_target"
    ANOTHER_RUNNING = "another_running"
    UNUSABLE_POWER = "unusable_power"


class ActionKind(StrEnum):
    START = "start"
    TAKE_OVER = "take_over"
    CHANGE_POWER = "change_power"
    STOP = "stop"
    FORGET = "forget"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class Wish:
    on: bool
    power: object = None


@dataclass(frozen=True)
class Action:
    kind: ActionKind
    function: PowerFunction
    watts: int | None = None
    blocker: Blocker | None = None


@dataclass(frozen=True)
class Situation:
    controls: Mapping[PowerFunction, FunctionControl[PowerMethod]]
    running: Collection[PowerFunction]
    owned: Collection[PowerFunction]
    started: Mapping[PowerFunction, int | None]
    targets: Mapping[PowerFunction, int]


def decide(
    *, wishes: Mapping[PowerFunction, Wish], situation: Situation
) -> tuple[Action, ...]:
    engaged: set[PowerFunction] = set()
    actions: list[Action] = []
    for function in PowerFunction:
        wish = wishes.get(function)
        if wish is None or function not in situation.controls:
            continue
        action = _decide_function(
            function=function, wish=wish, situation=situation, engaged=engaged
        )
        if action is not None:
            actions.append(action)
            if action.kind in {ActionKind.START, ActionKind.TAKE_OVER}:
                engaged.add(function)
    return tuple(actions)


def _decide_function(
    *,
    function: PowerFunction,
    wish: Wish,
    situation: Situation,
    engaged: Collection[PowerFunction],
) -> Action | None:
    if not wish.on:
        return _decide_unwanted(function=function, situation=situation)
    watts = (
        None
        if wish.power is None
        else situation.controls[function].usable(raw=wish.power)
    )
    if wish.power is not None and watts is None:
        return Action(ActionKind.BLOCKED, function, blocker=Blocker.UNUSABLE_POWER)
    if function in situation.started:
        return _decide_started(function=function, watts=watts, situation=situation)
    return _decide_unstarted(
        function=function, watts=watts, situation=situation, engaged=engaged
    )


def _decide_started(
    *, function: PowerFunction, watts: int | None, situation: Situation
) -> Action | None:
    changed = watts is not None and watts != situation.started[function]
    if changed and function in situation.running:
        return Action(ActionKind.CHANGE_POWER, function, watts=watts)
    return None


def _decide_unstarted(
    *,
    function: PowerFunction,
    watts: int | None,
    situation: Situation,
    engaged: Collection[PowerFunction],
) -> Action:
    if function in situation.running:
        return Action(ActionKind.TAKE_OVER, function, watts=watts)
    if set(situation.running) - {function} or engaged:
        return Action(ActionKind.BLOCKED, function, blocker=Blocker.ANOTHER_RUNNING)
    if watts is None and function not in situation.targets:
        return Action(ActionKind.BLOCKED, function, blocker=Blocker.NO_TARGET)
    return Action(ActionKind.START, function, watts=watts)


def _decide_unwanted(*, function: PowerFunction, situation: Situation) -> Action | None:
    if function not in situation.started:
        return None
    kind = ActionKind.STOP if function in situation.owned else ActionKind.FORGET
    return Action(kind, function)
