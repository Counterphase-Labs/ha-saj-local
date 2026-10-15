import pytest

from saj_modbus_mock.profiles import parallel
from saj_modbus_mock.registers import Encoding
from tests.modbus_mock.builders import by_address, make_scenario
from tests.modbus_mock.profiles.fakes import isolate


@pytest.fixture(autouse=True)
def stubbed_helpers(monkeypatch):
    isolate(monkeypatch, parallel)


def fields_of(*, extended=True, **changes):
    return by_address(
        fields=parallel.parallel_fields(
            scenario=make_scenario(model="hs3", **changes), extended=extended
        )
    )


def test_the_block_reports_the_installed_inverter_count():
    fields = fields_of(parallel={"inverters": 2})

    assert fields[0x4202].initial == fields[0x4203].initial == 2
    assert fields[0x420B].source == "parallel_capacity_ah"


def test_powers_split_into_a_low_word_and_a_signed_high_word():
    fields = fields_of()

    assert fields[0x4206].encoding is Encoding.U16
    assert fields[0x420E].encoding is Encoding.I16
    assert fields[0x420C].encoding is Encoding.U16
    assert fields[0x4206].source == "parallel_grid_w_low"
    assert fields[0x420E].source == "parallel_grid_w_high"


def test_state_of_charge_is_in_whole_percent():
    assert fields_of()[0x4209].scale == 1.0


def test_energy_counters_describe_the_whole_system_where_a_quantity_exists():
    fields = fields_of()

    assert fields[0x4215].source == "counter:pv:True:True"
    assert fields[0x4235].source == "counter::False:True"


def test_the_h2_layout_serves_each_power_as_one_signed_or_unsigned_register():
    fields = fields_of(extended=False)

    powers = {
        field.name: field
        for field in fields.values()
        if field.name.startswith("parallel_") and (field.source or "").endswith("_w")
    }
    assert powers
    assert all(field.source == field.name for field in powers.values())
    assert not any(name.endswith(("_low", "_high")) for name in powers)
    assert powers["parallel_grid_w"].encoding is Encoding.I16
    assert powers["parallel_pv_w"].encoding is Encoding.U16


def test_the_h2_layout_leaves_the_high_word_registers_unserved():
    base = fields_of(extended=False)
    extended = fields_of(extended=True)

    high_words = {
        address for address, field in extended.items() if field.name.endswith("_high")
    }
    assert high_words
    assert not high_words & base.keys()


def test_the_extended_layout_adds_the_meter_b_power_and_the_trailing_counters():
    extended = fields_of(extended=True)
    base = fields_of(extended=False)

    assert not any(field.name == "parallel_meter_b_power" for field in base.values())
    assert any(field.name == "parallel_meter_b_power" for field in extended.values())
    assert max(extended) > max(base)
