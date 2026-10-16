from types import SimpleNamespace

import pytest

from saj_modbus_mock import description
from saj_modbus_mock.device import Block
from saj_modbus_mock.exceptions import ExceptionCode
from saj_modbus_mock.registers import Access, Encoding, Field
from saj_modbus_mock.simulation.environment import LoadConfig, Variation
from saj_modbus_mock.simulation.faults import (
    Effect,
    Equipment,
    FaultBit,
    FaultEntry,
    FaultMap,
    FaultState,
    PackCodes,
)
from tests.modbus_mock.builders import make_scenario

SETTING = Field(
    address=0x3647,
    name="app_mode",
    access=Access.READ_WRITE,
    options=frozenset({6, 0}),
    labels=((0, "Self-use"),),
    initial=0,
)
SCALED = Field(
    address=0x3639,
    name="share",
    access=Access.READ_WRITE,
    scale=0.1,
    maximum=1100,
    initial=4.2,
)
SIGNED = Field(
    address=0x10, name="signed", encoding=Encoding.I16, access=Access.READ_WRITE
)
TEXT = Field(
    address=0x20,
    name="label",
    encoding=Encoding.TEXT,
    length=4,
    access=Access.READ_WRITE,
    initial="abc",
)
COMMAND = Field(
    address=0x8015,
    name="cmd_restart",
    access=Access.WRITE_ONLY,
    options=frozenset({1}),
    labels=((1, "Restart"),),
)
CLOCK_COMMAND = Field(
    address=0x8020,
    name="cmd_set_clock",
    encoding=Encoding.CLOCK,
    access=Access.WRITE_ONLY,
)
READING = Field(address=0x4000, name="reading", source="pv_w")
FIXED = Field(address=0x8F00, name="device_type", initial=0x1610)
BLOCKS = (
    Block(start=0x3600, end=0x36EF, fields=(SETTING, SCALED), name="Settings"),
    Block(start=0x10, end=0x2F, fields=(SIGNED, TEXT)),
    Block(start=0x8000, end=0x8023, fields=(COMMAND, CLOCK_COMMAND), name="Commands"),
    Block(start=0x4000, end=0x4001, fields=(READING,), name="Live"),
    Block(start=0x8F00, end=0x8F01, fields=(FIXED,), name="Identity"),
    Block(
        start=0x3024,
        end=0x3025,
        fields=(Field(address=0x3024, name="hidden", access=Access.READ_WRITE),),
        unavailable=ExceptionCode.CHARGER_UNAVAILABLE,
        name="Refused",
    ),
)


def by_name(*, entries):
    return {entry["name"]: entry for entry in entries}


def test_only_the_writable_stored_fields_of_available_blocks_are_settings():
    settings = by_name(entries=description.describe_settings(blocks=BLOCKS))

    assert set(settings) == {"app_mode", "share", "signed", "label"}


def test_only_the_write_only_fields_that_are_not_the_clock_are_commands():
    commands = by_name(entries=description.describe_commands(blocks=BLOCKS))

    assert set(commands) == {"cmd_restart"}
    assert commands["cmd_restart"]["options"] == [{"value": 1, "label": "Restart"}]


def test_a_setting_describes_its_place_encoding_scale_bounds_and_named_options():
    settings = by_name(entries=description.describe_settings(blocks=BLOCKS))

    assert settings["app_mode"] == {
        "name": "app_mode",
        "address": "0x3647",
        "group": "Settings",
        "encoding": "U16",
        "scale": 1.0,
        "minimum": 0,
        "maximum": 65535,
        "text": False,
        "max_length": None,
        "options": [
            {"value": 0, "label": "Self-use"},
            {"value": 6, "label": None},
        ],
    }
    assert settings["share"]["scale"] == 0.1
    assert (settings["share"]["minimum"], settings["share"]["maximum"]) == (0, 1100)
    assert settings["share"]["options"] is None
    assert (settings["signed"]["minimum"], settings["signed"]["maximum"]) == (
        -32768,
        32767,
    )


def test_a_text_setting_has_a_length_instead_of_bounds_and_an_unnamed_block_its_range():
    settings = by_name(entries=description.describe_settings(blocks=BLOCKS))

    assert settings["label"]["text"] is True
    assert settings["label"]["max_length"] == 8
    assert (settings["label"]["minimum"], settings["label"]["maximum"]) == (None, None)
    assert settings["label"]["group"] == "0x0010-0x002F"


def fault_map():
    inverter = FaultBit(register=0x4005, bit=23)
    reserved = FaultBit(register=0x4005, bit=22)
    return FaultMap(
        entries=(
            FaultEntry(
                Equipment.INVERTER, inverter, "Grid lost", frozenset({Effect.GRID_LOST})
            ),
            FaultEntry(
                Equipment.INVERTER,
                reserved,
                "0x4005 bit 22 reserved",
                frozenset(),
                reserved=True,
            ),
        ),
        pack_count=2,
    )


def test_faults_are_listed_by_equipment_with_their_bit_name_and_reserved_flag():
    faults = description.describe_faults(
        fault_map=fault_map(), clear_command="cmd_clear", clear_value=1
    )

    assert faults["inverter"] == [
        {
            "key": "0x4005:23",
            "register": "0x4005",
            "bit": 23,
            "name": "Grid lost",
            "reserved": False,
        },
        {
            "key": "0x4005:22",
            "register": "0x4005",
            "bit": 22,
            "name": "0x4005 bit 22 reserved",
            "reserved": True,
        },
    ]
    assert faults["battery"] == []
    assert faults["ev_charger"] == []
    assert faults["packs"] == [1, 2]
    assert faults["clear_all"] == {"command": "cmd_clear", "value": 1}


def test_a_variation_parameter_offers_its_bounds_and_the_scenarios_value_as_default():
    parameters = by_name(
        entries=description.describe_variation(
            seed=9,
            variation=Variation(cloud_depth=0.9),
            load=LoadConfig(base_w=111, peak_w=2222),
        )
    )

    assert parameters["cloud_depth"] == {
        "name": "cloud_depth",
        "label": "Cloud cover depth",
        "group": "Solar",
        "minimum": 0,
        "maximum": 1,
        "step": 0.01,
        "unit": "",
        "default": 0.9,
        "slider": True,
    }
    assert parameters["base_w"]["default"] == 111
    assert parameters["peak_w"]["default"] == 2222
    assert parameters["seed"]["default"] == 9
    assert parameters["seed"]["group"] == "Seed"
    assert {parameter["group"] for parameter in parameters.values()} == {
        "Solar",
        "Load",
        "Grid",
        "Seed",
    }


def test_only_parameters_with_a_useful_number_of_steps_get_a_slider():
    parameters = by_name(
        entries=description.describe_variation(
            seed=9, variation=Variation(), load=LoadConfig(base_w=111, peak_w=2222)
        )
    )

    assert parameters["seed"]["slider"] is False
    assert parameters["spike_chance"]["slider"] is True
    assert all(
        parameter["slider"]
        == (
            (parameter["maximum"] - parameter["minimum"]) / parameter["step"]
            <= description.SLIDER_MAXIMUM_STEPS
        )
        for parameter in parameters.values()
    )


def test_the_holdable_readings_are_pv_load_voltage_and_frequency_with_ranges():
    holds = by_name(entries=description.describe_holds())

    assert set(holds) == {"pv_w", "load_w", "voltage_v", "frequency_hz"}
    assert all(
        hold["minimum"] < hold["maximum"] and hold["unit"] for hold in holds.values()
    )


def test_presets_are_described_by_key_name_and_text():
    preset = SimpleNamespace(key="a-b", name="A b", description="Does it")

    assert description.describe_presets(presets=[preset]) == [
        {"key": "a-b", "name": "A b", "description": "Does it"}
    ]


@pytest.mark.parametrize(
    ("changes", "battery", "charger"),
    [
        ({}, True, False),
        ({"battery": {"modules": 0}}, False, False),
        ({"ev_charger": {"installed": True}}, True, True),
    ],
)
def test_the_model_description_reports_what_is_fitted(changes, battery, charger):
    scenario = make_scenario(model="hs3", **changes)

    model = description.describe_model(scenario=scenario, pack_count=1)

    assert model["name"] == "hs3"
    assert model["serial_number"] == "SN123"
    assert model["phases"] == 3
    equipment = model["equipment"]
    assert equipment["battery"]["fitted"] is battery
    assert equipment["battery"]["packs"] == 1
    assert equipment["ev_charger"]["fitted"] is charger
    assert equipment["meter_a"] is True
    assert equipment["meter_b"] is False
    assert equipment["parallel_inverters"] == 1


@pytest.mark.parametrize(
    ("field", "value", "raw"),
    [
        (SETTING, 6, 6),
        (SCALED, 4.2, 42),
        (SCALED, 0.30000000000000004, 3),
        (TEXT, "abc", "abc"),
    ],
)
def test_a_raw_value_is_what_the_register_holds(field, value, raw):
    assert description.raw_value(field=field, value=value) == raw


def test_the_settings_state_pairs_each_raw_value_with_its_scaled_value():
    state = description.settings_state(
        fields=[SETTING, SCALED, COMMAND],
        settings={"app_mode": 6, "share": 4.2},
    )

    assert state == {
        "app_mode": {"raw": 6, "value": 6},
        "share": {"raw": 42, "value": 4.2},
    }


def test_the_faults_state_lists_only_the_active_faults_in_the_shape_of_a_request():
    faults = FaultState(
        inverter=frozenset(
            {FaultBit(register=0x4009, bit=1), FaultBit(register=0x4005, bit=3)}
        ),
        packs=(PackCodes(pack=2, fault=5, warning=1),),
    )

    assert description.faults_state(faults=faults) == {
        "inverter": {"0x4005:3": True, "0x4009:1": True},
        "battery": {},
        "ev_charger": {},
        "packs": {"2": {"fault": 5, "warning": 1}},
    }


def test_a_hold_that_is_not_set_reads_as_none():
    assert description.hold_values(holds={"pv_w": 3000.0}) == {
        "pv_w": 3000.0,
        "load_w": None,
        "voltage_v": None,
        "frequency_hz": None,
    }


@pytest.mark.parametrize(
    ("value", "places", "expected"),
    [(-0.04, 1, "0.0"), (-0.0, 0, "0.0"), (12.345, 1, "12.3"), (-2.5, 0, "-2.0")],
)
def test_a_rounded_value_never_shows_a_negative_zero(value, places, expected):
    assert str(description.rounded(value=value, places=places)) == expected


def test_each_hold_reports_the_telemetry_reading_it_fixes():
    data = {"pv_w": 10.4, "load_w": 20.6, "grid_r_v": 230.04, "frequency_hz": 49.987}

    assert description.hold_readings(data=data) == {
        "pv_w": 10,
        "load_w": 21,
        "voltage_v": 230.0,
        "frequency_hz": 49.99,
    }
