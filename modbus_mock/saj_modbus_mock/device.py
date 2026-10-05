from typing import TYPE_CHECKING, Protocol

from .exceptions import ExceptionCode, ModbusError
from .registers import (
    BYTE_BITS,
    Field,
    FieldValue,
    decode,
    decode_raw,
    encode,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, MutableMapping

ASCII_LIMIT = 0x80
RESERVED_WORD = 0


class DeviceObserver(Protocol):
    def field_read(self, *, field: Field) -> None: ...

    def field_written(self, *, field: Field, value: FieldValue) -> None: ...


class Block:
    """A contiguous span of addresses; words without a field read as zero."""

    def __init__(
        self,
        *,
        start: int,
        end: int,
        fields: tuple[Field, ...],
        unavailable: ExceptionCode | None = None,
    ) -> None:
        self.start = start
        self.end = end
        self.fields = fields
        self.unavailable = unavailable
        self._by_word: dict[int, Field] = {}
        for field in fields:
            self._claim(field=field)

    def _claim(self, *, field: Field) -> None:
        if field.address < self.start or field.last_address > self.end:
            message = f"{field.name} lies outside block {self.start:#06x}"
            raise ValueError(message)
        for address in range(field.address, field.last_address + 1):
            if address in self._by_word:
                message = f"{field.name} overlaps {self._by_word[address].name}"
                raise ValueError(message)
            self._by_word[address] = field

    def contains(self, *, address: int) -> bool:
        return self.start <= address <= self.end

    def field_at(self, *, address: int) -> Field | None:
        return self._by_word.get(address)


def initial_settings(*, blocks: tuple[Block, ...]) -> dict[str, FieldValue]:
    return {
        field.name: field.initial
        for block in blocks
        for field in block.fields
        if field.source is None and field.readable
    }


class Device:
    def __init__(
        self,
        *,
        blocks: tuple[Block, ...],
        overrun_code: ExceptionCode,
        telemetry: Callable[[], Mapping[str, float]],
        settings: MutableMapping[str, FieldValue],
        observer: DeviceObserver,
    ) -> None:
        self._blocks = blocks
        self._overrun_code = overrun_code
        self._telemetry = telemetry
        self._settings = settings
        self._observer = observer

    def _locate(self, *, start: int, count: int) -> Block:
        for block in self._blocks:
            if block.contains(address=start):
                if block.unavailable is not None:
                    raise ModbusError(code=block.unavailable)
                if start + count - 1 > block.end:
                    raise ModbusError(code=self._overrun_code)
                return block
        raise ModbusError(code=ExceptionCode.ILLEGAL_DATA_ADDRESS)

    def _value(self, *, field: Field, telemetry: Mapping[str, float]) -> FieldValue:
        if field.source is not None:
            return telemetry[field.source]
        return self._settings[field.name]

    def read(self, *, start: int, count: int) -> list[int]:
        block = self._locate(start=start, count=count)
        telemetry = self._telemetry()
        end = start + count
        words: list[int] = []
        touched: list[Field] = []
        address = start
        while address < end:
            field = block.field_at(address=address)
            if field is None:
                words.append(RESERVED_WORD)
                address += 1
                continue
            if not field.readable:
                raise ModbusError(code=ExceptionCode.ILLEGAL_DATA_ADDRESS)
            encoded = encode(
                field=field, value=self._value(field=field, telemetry=telemetry)
            )
            offset = address - field.address
            taken = encoded[offset : offset + (end - address)]
            words.extend(taken)
            address += len(taken)
            touched.append(field)
        for field in touched:
            self._observer.field_read(field=field)
        return words

    def write(self, *, start: int, words: list[int]) -> None:
        block = self._locate(start=start, count=len(words))
        self._telemetry()
        plan = self._plan_write(block=block, start=start, words=words)
        for field, value in plan:
            if field.source is None and field.readable:
                self._settings[field.name] = value
        for field, value in plan:
            self._observer.field_written(field=field, value=value)

    def _plan_write(
        self,
        *,
        block: Block,
        start: int,
        words: list[int],
    ) -> list[tuple[Field, FieldValue]]:
        end = start + len(words)
        plan: list[tuple[Field, FieldValue]] = []
        address = start
        while address < end:
            field = block.field_at(address=address)
            if field is None or not field.writable:
                raise ModbusError(code=ExceptionCode.ILLEGAL_DATA_ADDRESS)
            if address != field.address or field.last_address >= end:
                raise ModbusError(code=ExceptionCode.ILLEGAL_DATA_VALUE)
            chunk = words[address - start : address - start + field.words]
            plan.append((field, self._validated(field=field, chunk=chunk)))
            address += field.words
        return plan

    def _validated(self, *, field: Field, chunk: list[int]) -> FieldValue:
        try:
            self._check_range(field=field, chunk=chunk)
            return decode(field=field, words=chunk)
        except ValueError as error:
            raise ModbusError(code=ExceptionCode.ILLEGAL_DATA_VALUE) from error

    @staticmethod
    def _check_range(*, field: Field, chunk: list[int]) -> None:
        if field.is_text:
            for word in chunk:
                if max(word >> BYTE_BITS, word & ((1 << BYTE_BITS) - 1)) >= ASCII_LIMIT:
                    message = "text must be ASCII"
                    raise ValueError(message)
            return
        if field.is_clock:
            return
        raw = decode_raw(field=field, words=chunk)
        if field.options is not None and raw not in field.options:
            message = "value outside enumeration"
            raise ValueError(message)
        if field.minimum is not None and raw < field.minimum:
            message = "value below minimum"
            raise ValueError(message)
        if field.maximum is not None and raw > field.maximum:
            message = "value above maximum"
            raise ValueError(message)

    def reset_settings(self, *, initial: Mapping[str, FieldValue]) -> None:
        self._settings.update(initial)
