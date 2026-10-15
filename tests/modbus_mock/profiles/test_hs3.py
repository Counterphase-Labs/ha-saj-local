import itertools
from types import SimpleNamespace

import pytest

from saj_modbus_mock.exceptions import ExceptionCode
from saj_modbus_mock.profiles import hs3
from saj_modbus_mock.registers import Field
from tests.modbus_mock.builders import arguments_of, block_at, by_address, make_scenario
from tests.modbus_mock.profiles.fakes import fake_fixed

COMMON_BUILDERS = {
    "information_fields": 0x8F00,
    "realtime_energy_fields": 0x4000,
    "settings_fields": 0x3604,
    "battery_fields": 0xA000,
    "meter_fields": 0xA03C,
    "factory_command_fields": 0x8015,
}
EQUIPMENT_BUILDERS = {
    "ethernet_fields": 0x0F00,
    "ev_settings_fields": 0x4B00,
    "ev_data_fields": 0x3024,
    "average_fields": 0x513E,
    "ems_fields": 0x8400,
}
UNDOCUMENTED = ((0x3661, 0x3662, 7), (0x3670, 0x3670, 9))


@pytest.fixture
def calls(monkeypatch):
    recorded = []

    def stub(name, address):
        def build(**arguments):
            recorded.append((name, arguments))
            return [Field(address=address, name=name)]

        return build

    common = SimpleNamespace(
        FACTORY_BLOCK_START=0x8015,
        FACTORY_BLOCK_END=0x8023,
        **{name: stub(name, address) for name, address in COMMON_BUILDERS.items()},
    )
    equipment = SimpleNamespace(
        **{name: stub(name, address) for name, address in EQUIPMENT_BUILDERS.items()},
    )
    monkeypatch.setattr(hs3, "common", common)
    monkeypatch.setattr(hs3, "hs3_equipment", equipment)
    monkeypatch.setattr(
        hs3,
        "parallel",
        SimpleNamespace(parallel_fields=stub("parallel_fields", 0x4200)),
    )
    monkeypatch.setattr(hs3, "fixed", fake_fixed)
    monkeypatch.setattr(hs3, "UNDOCUMENTED_SETTINGS", UNDOCUMENTED)
    return recorded


def build(*, calls, **changes):
    return hs3.build_blocks(scenario=make_scenario(model="hs3", **changes))


def test_every_builder_fills_the_block_of_its_address_range(calls):
    blocks = build(calls=calls)

    for name, address in {
        **COMMON_BUILDERS,
        **EQUIPMENT_BUILDERS,
        "parallel_fields": 0x4200,
    }.items():
        assert any(
            field.name == name
            for field in block_at(blocks=blocks, address=address).fields
        )


def test_blocks_do_not_overlap(calls):
    spans = sorted((block.start, block.end) for block in build(calls=calls))

    for (_, end), (start, _) in itertools.pairwise(spans):
        assert end < start


def test_the_block_ranges_follow_the_protocol(calls):
    spans = {(block.start, block.end) for block in build(calls=calls)}

    assert spans == {
        (0x8F00, 0x8F1C),
        (0x4000, 0x4176),
        (0x3600, 0x36EF),
        (0x0F00, 0x0F2F),
        (0x4B00, 0x4B47),
        (0x3024, 0x30BB),
        (0x4200, 0x427C),
        (0x513E, 0x51BE),
        (0xA000, 0xA077),
        (0x8400, 0x8412),
        (0x8015, 0x8023),
    }


def test_the_common_builders_are_asked_for_the_hs3_layout(calls):
    scenario = make_scenario(model="hs3")

    hs3.build_blocks(scenario=scenario)

    assert arguments_of(calls=calls, name="information_fields") == {
        "scenario": scenario,
        "spec": hs3.SPEC,
    }
    assert arguments_of(calls=calls, name="realtime_energy_fields") == {
        "scenario": scenario,
        "phases": 3,
        "extended": True,
    }
    assert arguments_of(calls=calls, name="settings_fields") == {
        "scenario": scenario,
        "modes": frozenset({0, 1, 2, 6, 11}),
        "extended": True,
    }
    assert arguments_of(calls=calls, name="meter_fields") == {
        "phases": 3,
        "extended": True,
    }
    assert arguments_of(calls=calls, name="battery_fields") == {"populated": False}


def test_the_equipment_builders_receive_the_scenario_where_they_need_it(calls):
    scenario = make_scenario(model="hs3")

    hs3.build_blocks(scenario=scenario)

    assert arguments_of(calls=calls, name="ev_settings_fields") == {
        "scenario": scenario
    }
    assert arguments_of(calls=calls, name="parallel_fields") == {
        "scenario": scenario,
        "extended": True,
    }
    assert arguments_of(calls=calls, name="ethernet_fields") == {}


@pytest.mark.parametrize(
    ("installed", "gate"),
    [(True, None), (False, ExceptionCode.CHARGER_UNAVAILABLE)],
)
def test_only_the_charger_data_block_is_gated_on_the_installation(
    calls, installed, gate
):
    blocks = build(calls=calls, ev_charger={"installed": installed})

    assert [block.start for block in blocks if block.unavailable is gate and gate] == (
        [0x3024] if gate else []
    )
    assert block_at(blocks=blocks, address=0x4B00).unavailable is None
    assert block_at(blocks=blocks, address=0x3024).unavailable is gate


def test_hs3_refuses_reads_past_a_block_with_its_own_exception(calls):
    assert hs3.OVERRUN_CODE is ExceptionCode.BLOCK_OVERRUN


def test_the_settings_block_starts_with_a_header_declaring_its_length(calls):
    fields = by_address(
        fields=block_at(blocks=build(calls=calls), address=0x3600).fields
    )

    assert fields[0x3600].initial == hs3.SETTINGS_CHECKSUM
    assert fields[0x3601].initial == 0x36EF - 0x3600 + 1


def test_undocumented_ranges_become_one_recorded_value_per_address(calls):
    fields = by_address(
        fields=block_at(blocks=build(calls=calls), address=0x3661).fields
    )

    assert [fields[a].initial for a in (0x3661, 0x3662, 0x3670)] == [7, 7, 9]
    assert fields[0x3661].name == "undocumented_3661"


def test_the_mirrors_report_the_device_type_and_the_scenario_rating(calls):
    fields = by_address(
        fields=block_at(
            blocks=build(calls=calls, device={"rated_power_w": 10000}), address=0x366C
        ).fields
    )

    assert fields[0x366C].initial == hs3.SPEC.device_type
    assert fields[0x366D].initial == 10000
