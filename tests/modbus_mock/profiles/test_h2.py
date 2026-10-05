import itertools
from types import SimpleNamespace

import pytest

from saj_modbus_mock.exceptions import ExceptionCode
from saj_modbus_mock.profiles import h2
from saj_modbus_mock.registers import Field
from tests.modbus_mock.builders import arguments_of, block_at, by_name, make_scenario
from tests.modbus_mock.profiles.fakes import fake_fixed, fake_text

COMMON_BUILDERS = {
    "information_fields": 0x8F00,
    "realtime_energy_fields": 0x4000,
    "settings_fields": 0x3604,
    "battery_fields": 0xA000,
    "meter_fields": 0xA03C,
    "factory_command_fields": 0x8015,
}
EXTRAS = {"realtime_fields": 0x4010, "settings_fields": 0x3610}


@pytest.fixture
def calls(monkeypatch):
    recorded = []

    def stub(name, address, prefix):
        def build(**arguments):
            recorded.append((f"{prefix}.{name}", arguments))
            return [Field(address=address, name=f"{prefix}.{name}")]

        return build

    common = SimpleNamespace(
        FACTORY_BLOCK_START=0x8015,
        FACTORY_BLOCK_END=0x8023,
        SOFTWARE_VERSION=1002,
        **{name: stub(name, a, "common") for name, a in COMMON_BUILDERS.items()},
    )
    extras = SimpleNamespace(
        **{name: stub(name, a, "extras") for name, a in EXTRAS.items()}
    )
    monkeypatch.setattr(h2, "common", common)
    monkeypatch.setattr(h2, "h2_extras", extras)
    monkeypatch.setattr(h2, "fixed", fake_fixed)
    monkeypatch.setattr(h2, "text", fake_text)
    return recorded


def build(**changes):
    return h2.build_blocks(scenario=make_scenario(model="h2", **changes))


def test_the_block_ranges_follow_the_protocol_and_do_not_overlap(calls):
    spans = sorted((block.start, block.end) for block in build())

    assert set(spans) == {
        (0x3604, 0x367C),
        (0x4000, 0x4166),
        (0x8E00, 0x8E63),
        (0x8F00, 0x8F1C),
        (0x8015, 0x8023),
        (0xA000, 0xA037),
        (0xA03C, 0xA065),
    }
    for (_, end), (start, _) in itertools.pairwise(spans):
        assert end < start


def test_the_realtime_and_settings_blocks_hold_the_common_and_the_extra_fields(calls):
    blocks = build()

    realtime = {f.name for f in block_at(blocks=blocks, address=0x4000).fields}
    settings = {f.name for f in block_at(blocks=blocks, address=0x3604).fields}
    assert realtime == {"common.realtime_energy_fields", "extras.realtime_fields"}
    assert settings == {"common.settings_fields", "extras.settings_fields"}


def test_the_common_builders_are_asked_for_the_single_phase_layout(calls):
    scenario = make_scenario(model="h2")

    h2.build_blocks(scenario=scenario)

    assert arguments_of(calls=calls, name="common.realtime_energy_fields") == {
        "scenario": scenario,
        "phases": 1,
        "extended": False,
    }
    assert arguments_of(calls=calls, name="common.settings_fields") == {
        "scenario": scenario,
        "modes": frozenset({0, 1, 2, 3, 14}),
        "extended": False,
    }
    assert arguments_of(calls=calls, name="common.meter_fields") == {
        "phases": 1,
        "with_meter_b": False,
        "extended": False,
    }
    assert arguments_of(calls=calls, name="common.battery_fields") == {
        "populated": True
    }
    assert arguments_of(calls=calls, name="extras.settings_fields") == {
        "scenario": scenario
    }


def test_reads_past_a_block_use_the_ordinary_address_error(calls):
    assert h2.OVERRUN_CODE is ExceptionCode.ILLEGAL_DATA_ADDRESS


def test_the_device_has_no_hs3_equipment_blocks(calls):
    blocks = build()

    for address in (0x8400, 0x4B04, 0x3024, 0x4200, 0x513E, 0x0F00):
        assert not any(block.contains(address=address) for block in blocks)


def test_every_installed_module_is_described_and_absent_ones_read_unused(calls):
    fields = by_name(
        fields=h2.peripheral_fields(
            scenario=make_scenario(model="h2", battery={"modules": 3})
        )
    )

    assert [fields[f"bms{n}_type"].initial for n in range(1, 6)] == [1, 1, 1, 0, 0]
    assert fields["bms1_serial"].initial != fields["battery1_serial"].initial
    assert fields["bms4_serial"].initial == ""
    assert fields["bms1_serial"].words == 8
    assert fields["bms1_software"].initial == 1002
    assert fields["bms4_software"].initial == 0


def test_peripheral_modules_are_twenty_words_apart(calls):
    fields = by_name(fields=h2.peripheral_fields(scenario=make_scenario(model="h2")))

    assert fields["bms2_type"].address - fields["bms1_type"].address == 20
    assert fields["bms5_type"].address == 0x8E50


def test_the_peripheral_block_holds_the_module_descriptions(calls):
    peripheral = block_at(blocks=build(battery={"modules": 2}), address=0x8E00)

    assert {f.name for f in peripheral.fields} >= {"bms1_type", "battery5_serial"}


@pytest.mark.parametrize("modules", [0, 4])
def test_the_blocks_build_for_any_battery_size(calls, modules):
    assert build(battery={"modules": modules})
