import pytest

from saj_modbus_mock.profiles.fields import (
    ZERO,
    Shape,
    blob,
    command,
    counter_group,
    fixed,
    live,
    phase_key,
    setting,
    text,
)
from saj_modbus_mock.registers import Access, Encoding


def test_a_live_field_reads_a_telemetry_source_and_is_read_only():
    field = live(address=0x10, name="volts", source="grid_v", scale=0.1)

    assert (field.source, field.scale, field.access) == (
        "grid_v",
        0.1,
        Access.READ_ONLY,
    )


def test_a_fixed_field_holds_its_value_and_has_no_source():
    field = fixed(address=0x10, name="version", value=1002, scale=0.001)

    assert field.source is None
    assert field.initial == 1002
    assert not field.writable


def test_text_and_blob_fields_take_their_width_from_the_given_length():
    assert text(address=0x10, name="serial", value="ABC", length=10).words == 10
    assert (
        text(address=0x10, name="serial", value="ABC", length=10).encoding
        is Encoding.TEXT
    )
    assert blob(address=0x10, name="mac", value=5, length=3).words == 3
    assert blob(address=0x10, name="mac", value=5, length=3).encoding is Encoding.HEX


def test_a_setting_is_writable_and_carries_its_shape():
    shape = Shape(
        enc=Encoding.I16,
        scale=0.1,
        minimum=1,
        maximum=9,
        options=frozenset({1, 2}),
        keepalive_bit=4,
    )

    field = setting(address=0x10, name="limit", value=5, shape=shape)

    assert field.writable
    assert field.readable
    assert (field.encoding, field.scale, field.minimum, field.maximum) == (
        Encoding.I16,
        0.1,
        1,
        9,
    )
    assert field.options == {1, 2}
    assert field.keepalive_bit == 4


def test_a_setting_without_a_shape_is_a_plain_unsigned_word():
    field = setting(address=0x10, name="plain")

    assert (field.encoding, field.scale, field.minimum, field.maximum) == (
        Encoding.U16,
        1.0,
        None,
        None,
    )


def test_a_command_can_be_written_but_not_read():
    field = command(address=0x10, name="restart", options=frozenset({1}))

    assert field.writable
    assert not field.readable
    assert field.options == {1}


@pytest.mark.parametrize(
    ("phase", "expected"),
    [(0, "grid_r_v"), (1, "grid_s_v"), (2, "grid_t_v")],
)
def test_phase_keys_name_the_phase_when_the_model_has_it(phase, expected):
    assert phase_key(group="grid", phase=phase, suffix="v", phases=3) == expected


@pytest.mark.parametrize("phase", [1, 2])
def test_phases_beyond_the_model_read_the_zero_source(phase):
    assert phase_key(group="grid", phase=phase, suffix="v", phases=1) == ZERO


def test_a_counter_group_is_four_consecutive_two_word_kwh_counters():
    fields = counter_group(start=0x40, base="pv", name="pv_energy")

    assert [field.address for field in fields] == [0x40, 0x42, 0x44, 0x46]
    assert [field.source for field in fields] == [
        f"pv_{period}_kwh" for period in ("today", "month", "year", "total")
    ]
    assert {(field.words, field.scale) for field in fields} == {(2, 0.01)}
    assert fields[0].name == "pv_energy_today"


def test_a_counter_group_can_be_absent_or_describe_the_parallel_system():
    absent = counter_group(start=0, base="pv", name="x", present=False)
    parallel = counter_group(start=0, base="pv", name="x", parallel=True)

    assert {field.source for field in absent} == {ZERO}
    assert parallel[0].source == "parallel_pv_today_kwh"
