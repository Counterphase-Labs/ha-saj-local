from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, time
from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum
from ipaddress import AddressValueError, IPv4Address
from math import isfinite
from typing import TYPE_CHECKING

from .errors import InvalidValueError, ValueProblem

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence

WORD_BITS = 16
WORD_MASK = 0xFFFF
BYTE_BITS = 8
BYTE_MASK = 0xFF
UNSCALED = 1
MAC_SEPARATOR = ":"
TEXT_PADDING = "\x00 "


class Encoding(StrEnum):
    U16 = "u16"
    I16 = "i16"
    U32 = "u32"
    I32 = "i32"
    TEXT = "text"
    CLOCK = "clock"
    UNIX_TIME = "unix_time"
    TIME_OF_DAY = "time_of_day"
    MAC = "mac"
    ADDRESS_TEXT = "address_text"


FIXED_WORD_COUNTS: dict[Encoding, int] = {
    Encoding.U16: 1,
    Encoding.I16: 1,
    Encoding.U32: 2,
    Encoding.I32: 2,
    Encoding.CLOCK: 4,
    Encoding.UNIX_TIME: 2,
    Encoding.TIME_OF_DAY: 1,
    Encoding.MAC: 3,
}
SIGNED_ENCODINGS = frozenset({Encoding.I16, Encoding.I32})
NUMERIC_ENCODINGS = frozenset({Encoding.U16, Encoding.I16, Encoding.U32, Encoding.I32})
WRITABLE_ENCODINGS = NUMERIC_ENCODINGS | {
    Encoding.TIME_OF_DAY,
    Encoding.CLOCK,
    Encoding.ADDRESS_TEXT,
    Encoding.TEXT,
}

type Value = int | float | str | datetime | time | None


@dataclass(frozen=True)
class BitRange:
    first: int
    last: int

    @property
    def width(self) -> int:
        return self.last - self.first + 1

    @property
    def mask(self) -> int:
        return (1 << self.width) - 1


@dataclass(frozen=True)
class Range:
    minimum: float
    maximum: float

    def contains(self, *, value: float) -> bool:
        return self.minimum <= value <= self.maximum


@dataclass(frozen=True)
class Format:
    encoding: Encoding
    scale: float = UNSCALED
    invalid: frozenset[int] = frozenset()
    field: BitRange | None = None
    valid_range: Range | None = None
    words: int | None = None

    @property
    def word_count(self) -> int:
        if self.words is not None:
            return self.words
        return FIXED_WORD_COUNTS[self.encoding]


def combine_words(*, words: Sequence[int]) -> int:
    combined = 0
    for word in words:
        combined = (combined << WORD_BITS) | word
    return combined


def option_name(*, code: float, options: Mapping[int, str]) -> str | None:
    return options.get(int(code))


def scaled(*, raw: int, scale: float) -> int | float:
    if scale == UNSCALED:
        return raw
    return float(Decimal(raw) * Decimal(repr(scale)))


def decode(*, words: Sequence[int], encoding_format: Format) -> Value:
    expected = FIXED_WORD_COUNTS.get(encoding_format.encoding)
    if expected is not None and len(words) != expected:
        message = f"{encoding_format.encoding} needs {expected} words, got {len(words)}"
        raise ValueError(message)
    if encoding_format.encoding in NUMERIC_ENCODINGS:
        return _decode_number(words=words, encoding_format=encoding_format)
    if combine_words(words=words) in encoding_format.invalid:
        return None
    return _STRUCTURED_DECODERS[encoding_format.encoding](words)


def _decode_number(*, words: Sequence[int], encoding_format: Format) -> Value:
    raw = combine_words(words=words)
    bit_count = WORD_BITS * len(words)
    if encoding_format.field is not None:
        raw = (raw >> encoding_format.field.first) & encoding_format.field.mask
        bit_count = encoding_format.field.width
    if raw in encoding_format.invalid:
        return None
    if encoding_format.encoding in SIGNED_ENCODINGS and raw >> (bit_count - 1):
        raw -= 1 << bit_count
    value = scaled(raw=raw, scale=encoding_format.scale)
    if (
        encoding_format.valid_range is not None
        and not encoding_format.valid_range.contains(value=value)
    ):
        return None
    return value


def _bytes_of(*, words: Sequence[int]) -> bytes:
    return b"".join(word.to_bytes(2, "big") for word in words)


def _decode_text(words: Sequence[int]) -> str | None:
    try:
        text = _bytes_of(words=words).decode("ascii").strip(TEXT_PADDING)
    except UnicodeDecodeError:
        return None
    return text or None


def _decode_address_text(words: Sequence[int]) -> str | None:
    text = _decode_text(words)
    if text is None:
        return None
    try:
        return str(IPv4Address(text))
    except AddressValueError:
        return None


def _decode_mac(words: Sequence[int]) -> str:
    return MAC_SEPARATOR.join(f"{byte:02x}" for byte in _bytes_of(words=words))


def _decode_unix_time(words: Sequence[int]) -> datetime:
    return datetime.fromtimestamp(combine_words(words=words), tz=UTC)


def _decode_time_of_day(words: Sequence[int]) -> time | None:
    (word,) = words
    try:
        return time(hour=word >> BYTE_BITS, minute=word & BYTE_MASK)
    except ValueError:
        return None


def _decode_clock(words: Sequence[int]) -> datetime | None:
    year, month_and_day, hour_and_minute, second = words
    try:
        return datetime(  # noqa: DTZ001
            year=year,
            month=month_and_day >> BYTE_BITS,
            day=month_and_day & BYTE_MASK,
            hour=hour_and_minute >> BYTE_BITS,
            minute=hour_and_minute & BYTE_MASK,
            second=second >> BYTE_BITS,
        )
    except ValueError:
        return None


_STRUCTURED_DECODERS: dict[Encoding, Callable[[Sequence[int]], Value]] = {
    Encoding.TEXT: _decode_text,
    Encoding.ADDRESS_TEXT: _decode_address_text,
    Encoding.MAC: _decode_mac,
    Encoding.UNIX_TIME: _decode_unix_time,
    Encoding.TIME_OF_DAY: _decode_time_of_day,
    Encoding.CLOCK: _decode_clock,
}


def split_words(*, raw: int, word_count: int) -> tuple[int, ...]:
    return tuple(
        (raw >> (WORD_BITS * (word_count - 1 - position))) & WORD_MASK
        for position in range(word_count)
    )


def replace_bits(
    *, current: Sequence[int], bits: Sequence[int], field: BitRange
) -> tuple[int, ...]:
    mask = field.mask << field.first
    replaced = (combine_words(words=current) & ~mask) | combine_words(words=bits)
    return split_words(raw=replaced, word_count=len(current))


def require_number(*, value: Value) -> int | float:
    if not isinstance(value, int | float) or (
        isinstance(value, float) and not isfinite(value)
    ):
        raise InvalidValueError(ValueProblem.NOT_A_NUMBER)
    return value


def raw_step(*, value: Value, scale: float) -> int:
    number = require_number(value=value)
    exact = Decimal(number) if isinstance(number, int) else Decimal(repr(number))
    return int((exact / Decimal(repr(scale))).to_integral_value(ROUND_HALF_UP))


def encode(*, value: Value, encoding_format: Format) -> tuple[int, ...]:
    if encoding_format.encoding in NUMERIC_ENCODINGS:
        return _encode_number(value=value, encoding_format=encoding_format)
    encoder = _STRUCTURED_ENCODERS.get(encoding_format.encoding)
    if encoder is None:
        raise InvalidValueError(ValueProblem.UNSUPPORTED_ENCODING)
    return encoder(value)


def _encode_number(*, value: Value, encoding_format: Format) -> tuple[int, ...]:
    raw = raw_step(value=value, scale=encoding_format.scale)
    field = encoding_format.field
    bit_count = WORD_BITS * encoding_format.word_count
    if field is not None:
        bit_count = field.width
    if encoding_format.encoding in SIGNED_ENCODINGS:
        lowest, highest = -(1 << (bit_count - 1)), (1 << (bit_count - 1)) - 1
    else:
        lowest, highest = 0, (1 << bit_count) - 1
    if not lowest <= raw <= highest:
        raise InvalidValueError(ValueProblem.DOES_NOT_FIT)
    raw &= (1 << bit_count) - 1
    if field is not None:
        raw <<= field.first
    return split_words(raw=raw, word_count=encoding_format.word_count)


def _encode_time_of_day(value: Value) -> tuple[int, ...]:
    if not isinstance(value, time):
        raise InvalidValueError(ValueProblem.NOT_A_TIME)
    return ((value.hour << BYTE_BITS) | value.minute,)


def _encode_clock(value: Value) -> tuple[int, ...]:
    if not isinstance(value, datetime):
        raise InvalidValueError(ValueProblem.NOT_A_CLOCK)
    return (
        value.year,
        (value.month << BYTE_BITS) | value.day,
        (value.hour << BYTE_BITS) | value.minute,
        value.second << BYTE_BITS,
    )


_STRUCTURED_ENCODERS: dict[Encoding, Callable[[Value], tuple[int, ...]]] = {
    Encoding.TIME_OF_DAY: _encode_time_of_day,
    Encoding.CLOCK: _encode_clock,
}
