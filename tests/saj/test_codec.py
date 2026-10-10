from datetime import UTC, date, datetime, time

import pytest

from saj.codec import (
    BitRange,
    Encoding,
    Format,
    Range,
    combine_words,
    decode,
    option_name,
    scaled,
)


def _text_words(text: bytes, *, words: int) -> list[int]:
    padded = text.ljust(words * 2, b"\0")
    return [
        int.from_bytes(padded[index : index + 2], "big")
        for index in range(0, len(padded), 2)
    ]


@pytest.mark.parametrize(
    ("encoding", "words", "expected"),
    [
        (Encoding.U16, [0], 0),
        (Encoding.U16, [0xFFFF], 65535),
        (Encoding.I16, [0x7FFF], 32767),
        (Encoding.I16, [0x8000], -32768),
        (Encoding.I16, [0xFFFF], -1),
        (Encoding.U32, [0x0001, 0x0002], 65538),
        (Encoding.U32, [0xFFFF, 0xFFFF], 4294967295),
        (Encoding.I32, [0x7FFF, 0xFFFF], 2147483647),
        (Encoding.I32, [0x8000, 0x0000], -2147483648),
        (Encoding.I32, [0xFFFF, 0xFFFE], -2),
    ],
)
def test_integers_are_read_most_significant_word_first_with_sign(
    encoding: Encoding, words: list[int], expected: int
):
    assert decode(words=words, encoding_format=Format(encoding=encoding)) == expected


@pytest.mark.parametrize(
    ("encoding", "words", "scale", "expected"),
    [
        (Encoding.U16, [989], 0.001, 0.989),
        (Encoding.U16, [7250], 0.01, 72.5),
        (Encoding.U16, [2305], 0.1, 230.5),
        (Encoding.I16, [0xFFF6], 0.1, -1.0),
        (Encoding.U32, [0x0001, 0x0002], 0.01, 655.38),
        (Encoding.I32, [0xFFFF, 0xFFFE], 0.01, -0.02),
        (Encoding.U16, [100], 1, 100),
    ],
)
def test_scale_multiplies_the_raw_value_without_float_noise(
    encoding: Encoding, words: list[int], scale: float, expected: float
):
    value = decode(words=words, encoding_format=Format(encoding=encoding, scale=scale))

    assert value == expected
    assert type(value) is type(expected)


@pytest.mark.parametrize(
    ("raw", "scale", "expected"),
    [(5, 1, 5), (5, 0.5, 2.5), (-3, 0.1, -0.3)],
)
def test_scaled_keeps_unscaled_values_whole(raw: int, scale: float, expected: float):
    assert scaled(raw=raw, scale=scale) == expected


@pytest.mark.parametrize(
    ("words", "invalid", "expected"),
    [
        ([0xFFFF], {0xFFFF}, None),
        ([0xFFFE], {0xFFFF}, 65534),
        ([0], {0}, None),
        ([1], {0, 0xFFFF}, 1),
        ([0xFFFF], set(), 65535),
    ],
)
def test_a_value_equal_to_an_invalid_marker_is_unknown(
    words: list[int], invalid: set[int], expected: int | None
):
    format_ = Format(encoding=Encoding.U16, invalid=frozenset(invalid))

    assert decode(words=words, encoding_format=format_) == expected


@pytest.mark.parametrize(
    ("text", "invalid", "expected"),
    [
        (b"SERIAL-1", {0}, "SERIAL-1"),
        (b"", {0}, None),
        (b"", set(), None),
        (b"  padded  ", set(), "padded"),
        (b"\xff\xfe", set(), None),
    ],
)
def test_text_drops_padding_and_unreadable_or_empty_text_is_unknown(
    text: bytes, invalid: set[int], expected: str | None
):
    format_ = Format(encoding=Encoding.TEXT, invalid=frozenset(invalid), words=5)

    assert decode(words=_text_words(text, words=5), encoding_format=format_) == expected


@pytest.mark.parametrize(
    ("word", "field", "expected"),
    [
        (0b0000000000000101, BitRange(first=0, last=0), 1),
        (0b0000000000000101, BitRange(first=1, last=1), 0),
        (0b0000000000000101, BitRange(first=0, last=2), 5),
        (0x7F32, BitRange(first=8, last=14), 127),
        (0xFF32, BitRange(first=8, last=14), 127),
        (0x7F32, BitRange(first=0, last=7), 0x32),
    ],
)
def test_a_bit_field_is_read_from_its_bits_only(
    word: int, field: BitRange, expected: int
):
    format_ = Format(encoding=Encoding.U16, field=field)

    assert decode(words=[word], encoding_format=format_) == expected


def test_a_bit_field_applies_the_invalid_marker_to_the_field_value():
    format_ = Format(
        encoding=Encoding.U16,
        field=BitRange(first=0, last=1),
        invalid=frozenset({3}),
    )

    assert decode(words=[0b111], encoding_format=format_) is None
    assert decode(words=[0b110], encoding_format=format_) == 2


@pytest.mark.parametrize(
    ("words", "expected"),
    [
        ([10000], 100.0),
        ([0], 0.0),
        ([10001], None),
        ([7250], 72.5),
    ],
)
def test_a_value_outside_its_valid_range_is_unknown(
    words: list[int], expected: float | None
):
    format_ = Format(
        encoding=Encoding.U16,
        scale=0.01,
        valid_range=Range(minimum=0, maximum=100),
    )

    assert decode(words=words, encoding_format=format_) == expected


def test_a_negative_value_below_the_valid_range_is_unknown():
    format_ = Format(encoding=Encoding.I16, valid_range=Range(minimum=0, maximum=100))

    assert decode(words=[0xFFFF], encoding_format=format_) is None


@pytest.mark.parametrize(
    ("words", "expected"),
    [
        (
            [2025, (3 << 8) | 9, (14 << 8) | 5, 59 << 8],
            datetime.combine(date(2025, 3, 9), time(14, 5, 59)),
        ),
        ([2025, (13 << 8) | 9, (14 << 8) | 5, 0], None),
        ([2025, (3 << 8) | 9, (25 << 8) | 5, 0], None),
    ],
)
def test_a_clock_is_year_month_day_hour_minute_second_and_invalid_dates_are_unknown(
    words: list[int], expected: datetime | None
):
    assert (
        decode(words=words, encoding_format=Format(encoding=Encoding.CLOCK)) == expected
    )


@pytest.mark.parametrize(
    ("words", "expected"),
    [
        ([(6 << 8) | 30], time(hour=6, minute=30)),
        ([0], time(hour=0, minute=0)),
        ([(23 << 8) | 59], time(hour=23, minute=59)),
        ([(24 << 8)], None),
        ([(6 << 8) | 60], None),
    ],
)
def test_a_time_of_day_is_hour_in_the_high_byte_and_minute_in_the_low_byte(
    words: list[int], expected: time | None
):
    format_ = Format(encoding=Encoding.TIME_OF_DAY)

    assert decode(words=words, encoding_format=format_) == expected


@pytest.mark.parametrize(
    ("words", "expected"),
    [
        ([0, 0], datetime(1970, 1, 1, tzinfo=UTC)),
        ([0, 86400], datetime(1970, 1, 2, tzinfo=UTC)),
        ([0x0001, 0x0000], datetime.fromtimestamp(65536, tz=UTC)),
    ],
)
def test_unix_time_is_seconds_since_the_epoch_in_utc(
    words: list[int], expected: datetime
):
    assert (
        decode(words=words, encoding_format=Format(encoding=Encoding.UNIX_TIME))
        == expected
    )


def test_a_mac_address_is_six_bytes_in_hex():
    words = [0x0011, 0x2233, 0xAABB]

    assert (
        decode(words=words, encoding_format=Format(encoding=Encoding.MAC))
        == "00:11:22:33:aa:bb"
    )


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (b"192.168.1.10", "192.168.1.10"),
        (b"10.0.0.1", "10.0.0.1"),
        (b"not an address", None),
        (b"999.1.1.1", None),
        (b"", None),
    ],
)
def test_an_address_is_ipv4_text_and_anything_else_is_unknown(
    text: bytes, expected: str | None
):
    format_ = Format(encoding=Encoding.ADDRESS_TEXT, words=8)

    assert decode(words=_text_words(text, words=8), encoding_format=format_) == expected


@pytest.mark.parametrize(
    ("encoding", "count"),
    [
        (Encoding.U16, 2),
        (Encoding.I32, 1),
        (Encoding.CLOCK, 3),
        (Encoding.MAC, 2),
        (Encoding.TIME_OF_DAY, 0),
        (Encoding.UNIX_TIME, 1),
    ],
)
def test_a_fixed_width_encoding_rejects_the_wrong_number_of_words(
    encoding: Encoding, count: int
):
    with pytest.raises(ValueError, match="needs"):
        decode(words=[0] * count, encoding_format=Format(encoding=encoding))


@pytest.mark.parametrize(
    ("code", "expected"),
    [(0, "standby"), (2, "operating"), (2.0, "operating"), (7, None), (-1, None)],
)
def test_an_enumeration_code_has_a_name_only_when_it_is_listed(
    code: float, expected: str | None
):
    options = {0: "standby", 2: "operating"}

    assert option_name(code=code, options=options) == expected


@pytest.mark.parametrize(
    ("encoding", "declared", "expected"),
    [
        (Encoding.U16, None, 1),
        (Encoding.I32, None, 2),
        (Encoding.CLOCK, None, 4),
        (Encoding.TEXT, 10, 10),
        (Encoding.ADDRESS_TEXT, 8, 8),
    ],
)
def test_a_formats_width_is_declared_for_variable_encodings_and_fixed_otherwise(
    encoding: Encoding, declared: int | None, expected: int
):
    assert Format(encoding=encoding, words=declared).word_count == expected


@pytest.mark.parametrize(
    ("words", "expected"),
    [([], 0), ([5], 5), ([1, 2], 65538), ([0xFFFF, 0xFFFF, 1], 0xFFFFFFFF0001)],
)
def test_words_combine_most_significant_first(words: list[int], expected: int):
    assert combine_words(words=words) == expected


@pytest.mark.parametrize(
    ("first", "last", "width", "mask"),
    [(0, 0, 1, 0b1), (0, 7, 8, 0xFF), (8, 14, 7, 0x7F)],
)
def test_a_bit_range_knows_its_width_and_mask(
    first: int, last: int, width: int, mask: int
):
    field = BitRange(first=first, last=last)

    assert (field.width, field.mask) == (width, mask)


@pytest.mark.parametrize(
    ("value", "expected"),
    [(0, True), (100, True), (50.5, True), (-0.1, False), (100.1, False)],
)
def test_a_range_contains_its_limits(value: float, *, expected: bool):
    assert Range(minimum=0, maximum=100).contains(value=value) is expected
