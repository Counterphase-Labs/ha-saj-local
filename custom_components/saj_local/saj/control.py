from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol

from .catalogue import Register, Row, device_registers, private_rows
from .client import ModbusError, RegisterReader, RegisterWriter
from .codec import (
    Value,
    decode,
    encode,
    replace_bits,
    require_number,
    split_words,
)
from .definitions import (
    PROTECTED_KEYS,
    Access,
    Definition,
    EntityKind,
)
from .errors import (
    ControlDisabledError,
    InvalidValueError,
    LinkUnavailableError,
    ModelUnverifiedError,
    ProtectedSettingError,
    SeparateRegistersError,
    UnknownSettingError,
    ValueProblem,
    WriteAllowanceError,
    WriteMismatchError,
    WriteRejectedError,
    WriteUnconfirmedError,
)
from .log import LabelledLogger
from .models import ems_rows
from .telemetry import decode_values

if TYPE_CHECKING:
    from collections.abc import Callable, Collection, Mapping, Sequence

    from .device import Device
    from .guard import EndpointGuard


_LOGGER = logging.getLogger(__name__)
PRIVATE_WORDS = "[private]"
WRITE_SINGLE_FUNCTION = 0x06
WRITE_MULTIPLE_FUNCTION = 0x10


class ControlLink(RegisterReader, RegisterWriter, Protocol):
    def is_connected(self) -> bool: ...


@dataclass(frozen=True)
class ControlEnvironment:
    clock: Callable[[], float]
    label: str


@dataclass(frozen=True)
class Inspection:
    extra_words: int
    check: Callable[[Sequence[int]], None]


@dataclass(frozen=True)
class Write:
    key: str
    value: Value
    also: Mapping[str, Value] = field(default_factory=dict)
    inspect_timeout: bool = False


@dataclass(frozen=True)
class RequestPlan:
    reads_before: bool
    reads_back: bool


@dataclass(frozen=True)
class WriteResult:
    values: Mapping[str, Value]
    assumed: bool
    written: bool


@dataclass(frozen=True)
class _Target:
    register: Register
    row: Row


@dataclass(frozen=True)
class _Edit:
    target: _Target
    bits: tuple[int, ...]


def request_plan(*, register: Register) -> RequestPlan:
    if register.access is Access.WRITE_ONLY:
        return RequestPlan(reads_before=False, reads_back=False)
    return RequestPlan(reads_before=register.field is not None, reads_back=True)


def validate_value(*, definition: Definition, value: Value) -> None:
    if definition.options is not None:
        number = require_number(value=value)
        if number != int(number) or int(number) not in definition.options:
            raise InvalidValueError(ValueProblem.NOT_AN_OPTION)
        return
    settable = definition.settable_range
    if settable is not None and not settable.contains(
        value=require_number(value=value)
    ):
        raise InvalidValueError(ValueProblem.OUT_OF_RANGE)


class Control:
    def __init__(
        self,
        *,
        link: ControlLink,
        device: Device,
        guard: EndpointGuard,
        enabled: bool,
        environment: ControlEnvironment,
    ) -> None:
        self._log = LabelledLogger(logger=_LOGGER, label=environment.label)
        self._link = link
        self._device = device
        self._guard = guard
        self._enabled = enabled
        self._clock = environment.clock
        registers = device_registers(fit=device.fit)
        self._private_rows = private_rows(registers=registers)
        self._targets = {
            register.key: _Target(register=register, row=register.row)
            for register in registers
            if register.writable and register.row is not None
        }
        self._ems = ems_rows(profile=device.profile)
        self._limit_requests = _adjacent_groups(
            targets=tuple(
                _Target(register=register, row=register.row)
                for register in registers
                if register.key in self._ems.limits and register.row is not None
            )
        )
        self._methods = tuple(device.profile.power_control.values())
        self._readable = {
            register.key: _Target(register=register, row=register.row)
            for register in registers
            if register.readable and register.row is not None
        }
        self._sharing: dict[Row, list[Register]] = {}
        for register in registers:
            if register.readable and register.row is not None:
                self._sharing.setdefault(register.row, []).append(register)

    async def write(
        self,
        *,
        key: str,
        value: Value,
        also: Mapping[str, Value] | None = None,
        inspection: Inspection | None = None,
        check: Callable[[Value], None] | None = None,
    ) -> WriteResult:
        changes = {key: value, **(also or {})}
        edits = self._edits(changes=changes)
        if check is not None:
            check(value)
        self._require_reachable()
        self._require_allowance()
        return await self._execute(edits=edits, inspection=inspection)

    async def switch_off(self, *, write: Write) -> WriteResult:
        changes = {write.key: write.value, **write.also}
        for key, value in changes.items():
            self._require_stop_write(key=key, value=value)
        edits = self._edits(changes=changes)
        self._require_reachable()
        return await self._execute(edits=edits, inspection=None)

    def _require_stop_write(self, *, key: str, value: Value) -> None:
        owners = [method for method in self._methods if key in method.stop_keys]
        if not owners:
            raise UnknownSettingError(key)
        if not any(method.accepts_stop(key=key, value=value) for method in owners):
            raise InvalidValueError(ValueProblem.OUT_OF_RANGE)

    async def read_states(self, *, keys: Collection[str]) -> dict[str, Value]:
        self._admit(keys=())
        targets = [self._readable_target(key=key) for key in keys]
        self._require_reachable()
        values: dict[str, Value] = {}
        for row in dict.fromkeys(target.row for target in targets):
            words = await self._read_before(row=row, inspection=None)
            values.update(self._values(row=row, words=words))
        return {key: values[key] for key in keys}

    def _readable_target(self, *, key: str) -> _Target:
        target = self._readable.get(key)
        if target is None:
            raise UnknownSettingError(key)
        return target

    def require_admitted(self) -> None:
        self._admit(keys=())

    async def read_setting(self, *, key: str) -> Value:
        (target,) = self._admit(keys=(key,))
        if not target.register.readable:
            raise UnknownSettingError(key)
        self._require_reachable()
        return await self._read_row(target=target)

    async def keep_alive_read_ems(self, *, key: str) -> Value:
        if key not in self._ems.target_functions:
            raise UnknownSettingError(key)
        (target,) = self._admit(keys=(key,))
        self._require_reachable()
        return await self._read_row(target=target)

    async def _read_row(self, *, target: _Target) -> Value:
        try:
            words = await self._link.read_holding_registers(
                address=target.row.address, count=target.row.words
            )
        except ModbusError as err:
            if err.exception_code is not None:
                raise WriteRejectedError(exception_code=err.exception_code) from err
            raise LinkUnavailableError(cause=err) from err
        return decode(words=words, encoding_format=target.register.format)

    async def read_ems_limits(self) -> dict[str, Value]:
        self._admit(keys=())
        self._require_reachable()
        values: dict[str, Value] = {}
        for group in self._limit_requests:
            start = group[0].row.address
            try:
                words = await self._link.read_holding_registers(
                    address=start, count=sum(target.row.words for target in group)
                )
            except ModbusError as err:
                if err.exception_code is None:
                    raise LinkUnavailableError(cause=err) from err
                self._log.debug(
                    "EMS limits at %#06x refused with exception %s",
                    start,
                    err.exception_code,
                )
                continue
            for target in group:
                offset = target.row.address - start
                values[target.register.key] = decode(
                    words=words[offset : offset + target.row.words],
                    encoding_format=target.register.format,
                )
        return values

    def _edits(self, *, changes: Mapping[str, Value]) -> tuple[_Edit, ...]:
        targets = self._admit(keys=tuple(changes))
        return tuple(
            _Edit(target=target, bits=_bits(register=target.register, value=sent))
            for sent, target in zip(changes.values(), targets, strict=True)
        )

    def _admit(self, *, keys: Sequence[str]) -> tuple[_Target, ...]:
        if not self._enabled:
            raise ControlDisabledError
        if not self._device.detected:
            raise ModelUnverifiedError
        for key in keys:
            if key in PROTECTED_KEYS:
                raise ProtectedSettingError(key)
        targets = tuple(self._target(key=key) for key in keys)
        if len(targets) > 1 and not _packed_together(targets=targets):
            raise SeparateRegistersError
        return targets

    def _target(self, *, key: str) -> _Target:
        target = self._targets.get(key)
        if target is None:
            raise UnknownSettingError(key)
        return target

    def _require_reachable(self) -> None:
        if self._guard.retry_in(now=self._clock()) > 0 or not self._link.is_connected():
            raise LinkUnavailableError

    def _require_allowance(self) -> None:
        allowance = self._guard.allowance
        if not allowance.has_room(now=self._clock()):
            raise WriteAllowanceError(limit=allowance.limit, window=allowance.window)

    async def _execute(
        self, *, edits: Sequence[_Edit], inspection: Inspection | None
    ) -> WriteResult:
        register = edits[0].target.register
        row = edits[0].target.row
        plan = request_plan(register=register)
        words = edits[0].bits
        if plan.reads_before:
            current = await self._read_before(row=row, inspection=inspection)
            words = _merged(current=current, edits=edits)
            if words == current:
                return WriteResult(
                    values=self._values(row=row, words=current),
                    assumed=False,
                    written=False,
                )
        await self._send(key=register.key, row=row, words=words)
        if not plan.reads_back:
            return WriteResult(
                values=_sent_values(register=register, words=words),
                assumed=True,
                written=True,
            )
        read_back = await self._read_back(row=row)
        self._log.debug(
            "Write to %s read back %s from %#06x",
            register.key,
            self._shown(row=row, words=read_back),
            row.address,
        )
        values = self._values(row=row, words=read_back)
        if _merged(current=read_back, edits=edits) != read_back:
            raise WriteMismatchError(read_back=values)
        return WriteResult(values=values, assumed=False, written=True)

    async def _read_before(
        self, *, row: Row, inspection: Inspection | None
    ) -> tuple[int, ...]:
        extra = 0 if inspection is None else inspection.extra_words
        try:
            words = tuple(
                await self._link.read_holding_registers(
                    address=row.address, count=row.words + extra
                )
            )
        except ModbusError as err:
            if err.exception_code is not None:
                raise WriteRejectedError(exception_code=err.exception_code) from err
            raise LinkUnavailableError(cause=err) from err
        if inspection is not None:
            inspection.check(words[row.words :])
        return words[: row.words]

    async def _send(self, *, key: str, row: Row, words: Sequence[int]) -> None:
        self._guard.allowance.record(now=self._clock())
        function = WRITE_SINGLE_FUNCTION if len(words) == 1 else WRITE_MULTIPLE_FUNCTION
        self._log.debug(
            "Write to %s: function %#04x at %#06x with %s",
            key,
            function,
            row.address,
            self._shown(row=row, words=words),
        )
        try:
            if function == WRITE_SINGLE_FUNCTION:
                await self._link.write_single_register(
                    address=row.address, value=words[0]
                )
            else:
                await self._link.write_multiple_registers(
                    address=row.address, values=words
                )
        except ModbusError as err:
            if err.exception_code is not None:
                raise WriteRejectedError(exception_code=err.exception_code) from err
            raise WriteUnconfirmedError(cause=err, acknowledged=False) from err

    def _shown(self, *, row: Row, words: Sequence[int]) -> str | tuple[int, ...]:
        if row in self._private_rows:
            return PRIVATE_WORDS
        return tuple(words)

    async def _read_back(self, *, row: Row) -> tuple[int, ...]:
        try:
            return tuple(
                await self._link.read_holding_registers(
                    address=row.address, count=row.words
                )
            )
        except ModbusError as err:
            raise WriteUnconfirmedError(cause=err, acknowledged=True) from err

    def _values(self, *, row: Row, words: Sequence[int]) -> dict[str, Value]:
        sharing = self._sharing.get(row, [])
        return decode_values(
            registers=sharing, raw={register.key: words for register in sharing}
        )


def _adjacent_groups(*, targets: Sequence[_Target]) -> tuple[tuple[_Target, ...], ...]:
    groups: list[list[_Target]] = []
    for target in sorted(targets, key=lambda target: target.row.address):
        if groups and _ends_at(target=groups[-1][-1], address=target.row.address):
            groups[-1].append(target)
        else:
            groups.append([target])
    return tuple(tuple(group) for group in groups)


def _ends_at(*, target: _Target, address: int) -> bool:
    return target.row.address + target.row.words == address


def _packed_together(*, targets: Sequence[_Target]) -> bool:
    return (
        all(target.register.field is not None for target in targets)
        and len({target.row for target in targets}) == 1
    )


def _bits(*, register: Register, value: Value) -> tuple[int, ...]:
    if register.command_value is not None:
        return split_words(raw=register.command_value, word_count=register.words)
    validate_value(definition=register.definition, value=value)
    return encode(value=value, encoding_format=register.format)


def _merged(*, current: Sequence[int], edits: Sequence[_Edit]) -> tuple[int, ...]:
    words = tuple(current)
    for edit in edits:
        field = edit.target.register.field
        if field is None:
            return edit.bits
        words = replace_bits(current=words, bits=edit.bits, field=field)
    return words


def _sent_values(*, register: Register, words: Sequence[int]) -> dict[str, Value]:
    if register.kind is EntityKind.BUTTON:
        return {}
    return {register.key: decode(words=words, encoding_format=register.format)}
