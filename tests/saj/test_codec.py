from datetime import UTC, date, datetime, time

import pytest

from saj.codec import (
    BitRange,
    Encoding,
    Format,
    Range,
    combine_words,
    decode,
    encode,
    option_name,
    raw_step,
    replace_bits,
    require_number,
    scaled,
    split_words,
)
from saj.errors import InvalidValueError, ValueProblem


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


@pytest.mark.parametrize(
    ("encoding", "scale", "value", "words"),
    [
        (Encoding.U16, 1, 0, [0]),
        (Encoding.U16, 1, 1, [1]),
        (Encoding.U16, 1, 65535, [0xFFFF]),
        (Encoding.U16, 0.1, 230.5, [2305]),
        (Encoding.U16, 0.001, 0.989, [989]),
        (Encoding.I16, 1, -1, [0xFFFF]),
        (Encoding.I16, 1, -32768, [0x8000]),
        (Encoding.I16, 0.01, -1.0, [0xFF9C]),
        (Encoding.U32, 1, 65538, [1, 2]),
        (Encoding.U32, 0.01, 655.38, [1, 2]),
        (Encoding.I32, 1, -2, [0xFFFF, 0xFFFE]),
        (Encoding.I32, 1, -2147483648, [0x8000, 0]),
    ],
)
def test_a_number_encodes_to_the_words_that_decode_back_to_it(
    encoding: Encoding, scale: float, value: float, words: list[int]
):
    format_ = Format(encoding=encoding, scale=scale)

    assert list(encode(value=value, encoding_format=format_)) == words
    assert decode(words=words, encoding_format=format_) == value


@pytest.mark.parametrize(
    ("scale", "value", "expected"),
    [
        (0.1, 4.2, 42),
        (0.1, 4.24, 42),
        (0.1, 4.25, 43),
        (0.1, 4.26, 43),
        (0.1, -4.25, -43),
        (0.01, 0.07, 7),
        (0.001, 1.0005, 1001),
        (1, 7.5, 8),
        (1, 7, 7),
        (5, 12, 2),
    ],
)
def test_a_value_is_rounded_to_the_nearest_raw_step_without_float_drift(
    scale: float, value: float, expected: int
):
    assert raw_step(value=value, scale=scale) == expected


@pytest.mark.parametrize(
    "value", ["1", None, float("nan"), float("inf"), float("-inf"), time(1, 2), []]
)
def test_a_non_number_cannot_be_encoded_as_a_number(value: object):
    with pytest.raises(InvalidValueError) as caught:
        encode(value=value, encoding_format=Format(encoding=Encoding.U16))

    assert caught.value.problem is ValueProblem.NOT_A_NUMBER


@pytest.mark.parametrize(
    ("encoding", "scale", "value"),
    [
        (Encoding.U16, 1, 65536),
        (Encoding.U16, 1, -1),
        (Encoding.U16, 0.1, 6553.6),
        (Encoding.I16, 1, 32768),
        (Encoding.I16, 1, -32769),
        (Encoding.U32, 1, 4294967296),
        (Encoding.I32, 1, -2147483649),
        (Encoding.U16, 1, 10**400),
    ],
)
def test_a_number_outside_what_the_encoding_holds_is_refused(
    encoding: Encoding, scale: float, value: float
):
    with pytest.raises(InvalidValueError) as caught:
        encode(value=value, encoding_format=Format(encoding=encoding, scale=scale))

    assert caught.value.problem is ValueProblem.DOES_NOT_FIT


@pytest.mark.parametrize(
    ("field", "encoding", "value", "words"),
    [
        (BitRange(first=0, last=0), Encoding.U16, 1, [0b1]),
        (BitRange(first=3, last=3), Encoding.U16, 1, [0b1000]),
        (BitRange(first=8, last=14), Encoding.U16, 127, [0x7F00]),
        (BitRange(first=0, last=7), Encoding.U16, 100, [100]),
        (BitRange(first=2, last=3), Encoding.I16, -1, [0b1100]),
    ],
)
def test_a_packed_field_encodes_to_its_bits_in_position(
    field: BitRange, encoding: Encoding, value: int, words: list[int]
):
    format_ = Format(encoding=encoding, field=field)

    assert list(encode(value=value, encoding_format=format_)) == words


@pytest.mark.parametrize(
    ("field", "value"),
    [
        (BitRange(first=0, last=0), 2),
        (BitRange(first=8, last=14), 128),
        (BitRange(first=0, last=0), -1),
    ],
)
def test_a_value_wider_than_its_packed_field_is_refused(field: BitRange, value: int):
    with pytest.raises(InvalidValueError) as caught:
        encode(
            value=value,
            encoding_format=Format(encoding=Encoding.U16, field=field),
        )

    assert caught.value.problem is ValueProblem.DOES_NOT_FIT


@pytest.mark.parametrize(
    ("current", "bits", "field", "expected"),
    [
        ([0xFFFF], [0], BitRange(first=0, last=0), [0xFFFE]),
        ([0x0000], [0x0008], BitRange(first=3, last=3), [0x0008]),
        ([0x8003], [0x0100], BitRange(first=8, last=14), [0x8103]),
        ([0xFFFF], [0x0000], BitRange(first=8, last=14), [0x80FF]),
        ([0x1234, 0x5678], [0, 0x0F00], BitRange(first=8, last=11), [0x1234, 0x5F78]),
    ],
)
def test_replacing_a_field_leaves_every_other_bit_as_it_was(
    current: list[int], bits: list[int], field: BitRange, expected: list[int]
):
    assert list(replace_bits(current=current, bits=bits, field=field)) == expected


@pytest.mark.parametrize(
    ("raw", "count", "expected"),
    [(5, 1, (5,)), (0x00010002, 2, (1, 2)), (1, 4, (0, 0, 0, 1))],
)
def test_a_raw_number_splits_into_words_most_significant_first(
    raw: int, count: int, expected: tuple[int, ...]
):
    assert split_words(raw=raw, word_count=count) == expected


@pytest.mark.parametrize(
    ("value", "word"),
    [
        (time(0, 0), 0x0000),
        (time(6, 30), 0x061E),
        (time(23, 59), 0x173B),
        (time(6, 30, 59), 0x061E),
        (time(6, 30, 0, 999999), 0x061E),
    ],
)
def test_a_time_of_day_is_hours_then_minutes_and_drops_the_seconds(
    value: time, word: int
):
    format_ = Format(encoding=Encoding.TIME_OF_DAY)

    assert encode(value=value, encoding_format=format_) == (word,)
    assert decode(words=[word], encoding_format=format_) == value.replace(
        second=0, microsecond=0
    )


@pytest.mark.parametrize(
    "value", ["06:30", 630, None, datetime(2024, 1, 1, 6, 30, tzinfo=UTC)]
)
def test_only_a_time_can_be_encoded_as_a_time_of_day(value: object):
    with pytest.raises(InvalidValueError) as caught:
        encode(value=value, encoding_format=Format(encoding=Encoding.TIME_OF_DAY))

    assert caught.value.problem is ValueProblem.NOT_A_TIME


@pytest.mark.parametrize(
    ("value", "words"),
    [
        (datetime(2024, 3, 9, 14, 5, 59, tzinfo=UTC), (2024, 0x0309, 0x0E05, 0x3B00)),
        (datetime(2031, 12, 31, 0, 0, 0, tzinfo=UTC), (2031, 0x0C1F, 0x0000, 0x0000)),
    ],
)
def test_the_clock_is_year_month_day_hour_minute_second_with_a_zero_byte(
    value: datetime, words: tuple[int, ...]
):
    format_ = Format(encoding=Encoding.CLOCK)

    assert encode(value=value, encoding_format=format_) == words
    assert decode(words=words, encoding_format=format_) == value.replace(tzinfo=None)


@pytest.mark.parametrize("value", [time(1, 2), date(2024, 1, 1), 5, None])
def test_only_a_date_and_time_can_be_encoded_as_the_clock(value: object):
    with pytest.raises(InvalidValueError) as caught:
        encode(value=value, encoding_format=Format(encoding=Encoding.CLOCK))

    assert caught.value.problem is ValueProblem.NOT_A_CLOCK


@pytest.mark.parametrize(
    "encoding",
    [Encoding.TEXT, Encoding.ADDRESS_TEXT, Encoding.MAC, Encoding.UNIX_TIME],
)
def test_text_address_mac_and_unix_time_can_only_be_decoded(encoding: Encoding):
    with pytest.raises(InvalidValueError) as caught:
        encode(value="x", encoding_format=Format(encoding=encoding, words=8))

    assert caught.value.problem is ValueProblem.UNSUPPORTED_ENCODING


def test_a_value_that_cannot_be_encoded_is_not_the_value_error_of_bad_device_data():
    with pytest.raises(InvalidValueError) as caught:
        encode(value=-1, encoding_format=Format(encoding=Encoding.U16))

    assert not isinstance(caught.value, ValueError)


@pytest.mark.parametrize(("value", "expected"), [(True, 1), (False, 0)])
def test_a_boolean_encodes_as_the_number_it_is(*, value: bool, expected: int):
    assert encode(value=value, encoding_format=Format(encoding=Encoding.U16)) == (
        expected,
    )


@pytest.mark.parametrize("value", [0, -3, 2.5, 10**400])
def test_a_finite_number_is_accepted_as_it_is(value: float):
    assert require_number(value=value) == value
