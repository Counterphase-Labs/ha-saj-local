import dataclasses
import enum
from datetime import UTC, datetime, timedelta

FieldValue = int | float | str

WORD_BITS = 16
WORD_MODULUS = 1 << WORD_BITS
WORD_MASK = WORD_MODULUS - 1
BYTES_PER_WORD = 2
BYTE_BITS = 8
BYTE_MASK = 0xFF
TEXT_PAD = b"\x00"
TEXT_CODEC = "ascii"
CLOCK_WORDS = 4
SINGLE_WORD = 1
DOUBLE_WORD = 2
SECONDS_BYTE_SHIFT = BYTE_BITS


EPOCH = datetime.fromtimestamp(0, tz=UTC)


class Encoding(enum.Enum):
    U16 = enum.auto()
    I16 = enum.auto()
    U32 = enum.auto()
    I32 = enum.auto()
    TEXT = enum.auto()
    CLOCK = enum.auto()
    HEX = enum.auto()


class Access(enum.Enum):
    READ_ONLY = enum.auto()
    READ_WRITE = enum.auto()
    WRITE_ONLY = enum.auto()


_FIXED_WORDS = {
    Encoding.U16: SINGLE_WORD,
    Encoding.I16: SINGLE_WORD,
    Encoding.U32: DOUBLE_WORD,
    Encoding.I32: DOUBLE_WORD,
    Encoding.CLOCK: CLOCK_WORDS,
}
_SIGNED = frozenset({Encoding.I16, Encoding.I32})


@dataclasses.dataclass(frozen=True, slots=True)
class Field:
    address: int
    name: str
    encoding: Encoding = Encoding.U16
    scale: float = 1.0
    access: Access = Access.READ_ONLY
    source: str | None = None
    initial: FieldValue = 0
    length: int = 0
    minimum: int | None = None
    maximum: int | None = None
    options: frozenset[int] | None = None
    keepalive_bit: int = 0
    labels: tuple[tuple[int, str], ...] = ()

    @property
    def words(self) -> int:
        return _FIXED_WORDS.get(self.encoding, self.length)

    @property
    def last_address(self) -> int:
        return self.address + self.words - 1

    @property
    def readable(self) -> bool:
        return self.access is not Access.WRITE_ONLY

    @property
    def writable(self) -> bool:
        return self.access is not Access.READ_ONLY

    @property
    def is_text(self) -> bool:
        return self.encoding is Encoding.TEXT

    @property
    def is_clock(self) -> bool:
        return self.encoding is Encoding.CLOCK


def _bit_width(*, field: Field) -> int:
    return field.words * WORD_BITS


def raw_range(*, field: Field) -> tuple[int, int]:
    width = _bit_width(field=field)
    if field.encoding in _SIGNED:
        return -(1 << (width - 1)), (1 << (width - 1)) - 1
    return 0, (1 << width) - 1


def _split_words(*, raw: int, count: int) -> list[int]:
    unsigned = raw % (1 << (count * WORD_BITS))
    return [
        (unsigned >> (WORD_BITS * (count - 1 - index))) & WORD_MASK
        for index in range(count)
    ]


def _join_words(*, words: list[int]) -> int:
    raw = 0
    for word in words:
        raw = (raw << WORD_BITS) | word
    return raw


def _encode_text(*, field: Field, text: str) -> list[int]:
    data = text.encode(TEXT_CODEC)[: field.words * BYTES_PER_WORD]
    data = data.ljust(field.words * BYTES_PER_WORD, TEXT_PAD)
    return [
        int.from_bytes(data[index : index + BYTES_PER_WORD], "big")
        for index in range(0, len(data), BYTES_PER_WORD)
    ]


def _decode_text(*, words: list[int]) -> str:
    data = b"".join(word.to_bytes(BYTES_PER_WORD, "big") for word in words)
    return data.rstrip(TEXT_PAD).decode(TEXT_CODEC, errors="replace")


def _encode_clock(*, epoch_seconds: float) -> list[int]:
    moment = EPOCH + timedelta(seconds=epoch_seconds)
    return [
        moment.year,
        (moment.month << BYTE_BITS) | moment.day,
        (moment.hour << BYTE_BITS) | moment.minute,
        moment.second << SECONDS_BYTE_SHIFT,
    ]


def _decode_clock(*, words: list[int]) -> float:
    year, month_day, hour_minute, second = words
    moment = datetime(
        year=year,
        month=month_day >> BYTE_BITS,
        day=month_day & BYTE_MASK,
        hour=hour_minute >> BYTE_BITS,
        minute=hour_minute & BYTE_MASK,
        second=second >> SECONDS_BYTE_SHIFT,
        tzinfo=UTC,
    )
    return (moment - EPOCH).total_seconds()


def encode(*, field: Field, value: FieldValue) -> list[int]:
    if field.is_text:
        return _encode_text(field=field, text=str(value))
    if field.is_clock:
        return _encode_clock(epoch_seconds=float(value))
    low, high = raw_range(field=field)
    raw = min(max(round(float(value) / field.scale), low), high)
    return _split_words(raw=raw, count=field.words)


def decode_raw(*, field: Field, words: list[int]) -> int:
    raw = _join_words(words=words)
    if field.encoding in _SIGNED and raw >= 1 << (_bit_width(field=field) - 1):
        raw -= 1 << _bit_width(field=field)
    return raw


def decode(*, field: Field, words: list[int]) -> FieldValue:
    if field.is_text:
        return _decode_text(words=words)
    if field.is_clock:
        return _decode_clock(words=words)
    raw = decode_raw(field=field, words=words)
    if field.scale == 1.0:
        return raw
    return raw * field.scale
