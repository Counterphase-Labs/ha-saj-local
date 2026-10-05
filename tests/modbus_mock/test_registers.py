import pytest

from saj_modbus_mock.registers import (
    Access,
    Encoding,
    Field,
    decode,
    decode_raw,
    encode,
)


@pytest.mark.parametrize(
    ("encoding", "scale", "value"),
    [
        (Encoding.U16, 1.0, 0),
        (Encoding.U16, 0.1, 6553.5),
        (Encoding.I16, 1.0, -1),
        (Encoding.I16, 0.01, -327.68),
        (Encoding.U32, 0.01, 123456.78),
        (Encoding.I32, 1.0, -70000),
        (Encoding.I32, 1.0, 2147483647),
    ],
)
def test_numeric_values_survive_a_round_trip(encoding, scale, value):
    field = Field(address=0, name="x", encoding=encoding, scale=scale)

    words = encode(field=field, value=value)

    assert len(words) == field.words
    assert decode(field=field, words=words) == pytest.approx(value)


@pytest.mark.parametrize(
    ("encoding", "value", "expected"),
    [
        (Encoding.U16, -5, 0),
        (Encoding.U16, 70000, 0xFFFF),
        (Encoding.I16, 40000, 32767),
        (Encoding.I16, -40000, -32768),
    ],
)
def test_values_beyond_the_register_saturate(encoding, value, expected):
    field = Field(address=0, name="x", encoding=encoding)

    assert decode(field=field, words=encode(field=field, value=value)) == expected


def test_thirty_two_bit_values_put_the_high_word_first():
    field = Field(address=0, name="x", encoding=Encoding.U32)

    assert encode(field=field, value=0x00010002) == [1, 2]
    assert decode_raw(field=field, words=[1, 2]) == 0x00010002


def test_hex_fields_carry_unsigned_words_of_the_declared_length():
    field = Field(address=0, name="mac", encoding=Encoding.HEX, length=3)

    words = encode(field=field, value=0x02AA4A000001)

    assert words == [0x02AA, 0x4A00, 0x0001]
    assert field.words == 3
    assert decode(field=field, words=words) == 0x02AA4A000001


@pytest.mark.parametrize("text", ["", "HS3", "SERIAL0123456789ABC"])
def test_text_is_padded_and_trimmed_to_the_field_width(text):
    field = Field(address=0, name="x", encoding=Encoding.TEXT, length=10)

    words = encode(field=field, value=text)

    assert len(words) == 10
    assert decode(field=field, words=words) == text


def test_text_longer_than_the_field_is_truncated():
    field = Field(address=0, name="x", encoding=Encoding.TEXT, length=2)

    assert decode(field=field, words=encode(field=field, value="ABCDEF")) == "ABCD"


def test_clock_packs_date_and_time_into_four_words():
    field = Field(address=0, name="x", encoding=Encoding.CLOCK)
    seconds = 1_781_000_000.0

    words = encode(field=field, value=seconds)

    assert field.words == 4
    assert decode(field=field, words=words) == seconds
    assert words[0] == 2026


def test_clock_with_an_impossible_date_is_rejected():
    field = Field(address=0, name="x", encoding=Encoding.CLOCK)

    with pytest.raises(ValueError, match="month"):
        decode(field=field, words=[2026, (13 << 8) | 1, 0, 0])


@pytest.mark.parametrize(
    ("access", "readable", "writable"),
    [
        (Access.READ_ONLY, True, False),
        (Access.READ_WRITE, True, True),
        (Access.WRITE_ONLY, False, True),
    ],
)
def test_access_decides_what_a_field_allows(access, readable, writable):
    field = Field(address=0, name="x", access=access)

    assert (field.readable, field.writable) == (readable, writable)


def test_a_field_reports_its_last_address_from_its_width():
    field = Field(address=0x10, name="x", encoding=Encoding.U32)

    assert field.last_address == 0x11
