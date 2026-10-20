from types import SimpleNamespace

import pytest

from saj_modbus_mock import description
from saj_modbus_mock.device import Block
from saj_modbus_mock.exceptions import ExceptionCode
from saj_modbus_mock.link import LinkSettings, RefusedBlock
from saj_modbus_mock.presets import Fitted
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
from tests.mock.builders import make_scenario

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


INITIAL = {"app_mode": 0, "share": 4.2, "signed": -3, "label": "abc"}
FITTED_ALL = Fitted(battery=True, meter_a=True, meter_b=True, ev_charger=True)
FITTED_NONE = Fitted(battery=False, meter_a=False, meter_b=False, ev_charger=False)


def by_name(*, entries):
    return {entry["name"]: entry for entry in entries}


def test_only_the_writable_stored_fields_of_available_blocks_are_settings():
    settings = by_name(
        entries=description.describe_settings(blocks=BLOCKS, initial=INITIAL)
    )

    assert set(settings) == {"app_mode", "share", "signed", "label"}


def test_only_the_write_only_fields_that_are_not_the_clock_are_commands():
    commands = by_name(entries=description.describe_commands(blocks=BLOCKS))

    assert set(commands) == {"cmd_restart"}
    assert commands["cmd_restart"]["options"] == [{"value": 1, "label": "Restart"}]


def test_a_setting_describes_its_place_encoding_scale_bounds_and_named_options():
    settings = by_name(
        entries=description.describe_settings(blocks=BLOCKS, initial=INITIAL)
    )

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
        "card": "inverter",
        "primary": True,
        "scenario": {"raw": 0, "value": 0},
    }
    assert settings["share"]["card"] is None
    assert settings["share"]["primary"] is False
    assert settings["share"]["scenario"] == {"raw": 42, "value": 4.2}
    assert settings["label"]["scenario"] == {"raw": "abc", "value": "abc"}
    assert settings["share"]["scale"] == 0.1
    assert (settings["share"]["minimum"], settings["share"]["maximum"]) == (0, 1100)
    assert settings["share"]["options"] is None
    assert (settings["signed"]["minimum"], settings["signed"]["maximum"]) == (
        -32768,
        32767,
    )


def test_a_text_setting_has_a_length_instead_of_bounds_and_an_unnamed_block_its_range():
    settings = by_name(
        entries=description.describe_settings(blocks=BLOCKS, initial=INITIAL)
    )

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
            "effect": "Runs off-grid",
        },
        {
            "key": "0x4005:22",
            "register": "0x4005",
            "bit": 22,
            "name": "0x4005 bit 22 reserved",
            "reserved": True,
            "effect": "Bit only",
        },
    ]
    assert faults["battery"] == []
    assert faults["ev_charger"] == []
    assert faults["packs"] == [1, 2]
    assert faults["clear_all"] == {"command": "cmd_clear", "value": 1}
    assert faults["cards"] == {
        "inverter": "inverter",
        "battery": "battery",
        "ev_charger": "ev_charger",
        "packs": "battery",
    }


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
        "scenario": 0.9,
        "slider": True,
        "card": "solar",
        "primary": True,
    }
    assert parameters["base_w"]["scenario"] == 111
    assert parameters["peak_w"]["scenario"] == 2222
    assert parameters["seed"]["scenario"] == 9
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
    data = {
        "pv_w": 10.4,
        "household_load_w": 20.6,
        "grid_r_v": 230.04,
        "frequency_hz": 49.987,
    }

    assert description.hold_readings(data=data) == {
        "pv_w": 10,
        "load_w": 21,
        "voltage_v": 230.0,
        "frequency_hz": 49.99,
    }


@pytest.mark.parametrize(
    ("name", "card", "primary"),
    [
        ("peak_scale_percent", "solar", True),
        ("cloud_depth", "solar", True),
        ("cloud_period_s", "solar", False),
        ("base_w", "house", True),
        ("peak_w", "house", True),
        ("spike_chance", "house", False),
        ("nominal_voltage_v", "grid", True),
        ("nominal_frequency_hz", "grid", True),
        ("phase_imbalance", "grid", False),
        ("seed", "inverter", False),
    ],
)
def test_each_variation_parameter_names_its_card_and_whether_it_is_primary(
    name, card, primary
):
    parameters = by_name(
        entries=description.describe_variation(
            seed=9, variation=Variation(), load=LoadConfig(base_w=1, peak_w=2)
        )
    )

    assert (parameters[name]["card"], parameters[name]["primary"]) == (card, primary)


@pytest.mark.parametrize(
    ("hold", "card"),
    [
        ("pv_w", "solar"),
        ("load_w", "house"),
        ("voltage_v", "grid"),
        ("frequency_hz", "grid"),
    ],
)
def test_each_hold_names_its_card(hold, card):
    assert by_name(entries=description.describe_holds())[hold]["card"] == card


@pytest.mark.parametrize(
    ("effects", "label"),
    [
        (frozenset(), "Bit only"),
        (frozenset({Effect.INVERTER_STOP}), "Inverter stops"),
        (frozenset({Effect.GRID_LOST}), "Runs off-grid"),
        (frozenset({Effect.METER_A_LOST}), "Meter A lost"),
        (frozenset({Effect.NO_CHARGE}), "No charging"),
        (frozenset({Effect.NO_DISCHARGE}), "No discharging"),
        (
            frozenset({Effect.NO_CHARGE, Effect.NO_DISCHARGE}),
            "No charging or discharging",
        ),
        (frozenset({Effect.EV_STOP}), "Charger stops"),
        (
            frozenset({Effect.INVERTER_STOP, Effect.NO_CHARGE, Effect.NO_DISCHARGE}),
            "Inverter stops, No charging or discharging",
        ),
    ],
)
def test_a_fault_bit_says_what_it_does(effects, label):
    assert description.fault_effect(effects=effects) == label


@pytest.mark.parametrize(
    ("fitted", "cards"),
    [
        (
            FITTED_ALL,
            [
                "solar",
                "external_pv",
                "house",
                "grid",
                "battery",
                "ev_charger",
                "inverter",
            ],
        ),
        (FITTED_NONE, ["solar", "house", "grid", "inverter"]),
        (
            Fitted(battery=True, meter_a=False, meter_b=False, ev_charger=False),
            ["solar", "house", "grid", "battery", "inverter"],
        ),
    ],
)
def test_only_the_cards_of_fitted_equipment_apply(fitted, cards):
    described = description.describe_cards(fitted=fitted)

    assert [card["key"] for card in described] == cards
    assert described[0] == {
        "key": "solar",
        "label": "Solar",
        "hub": False,
        "controls": [],
        "readings": [{"name": "pv_w", "label": "PV power", "unit": "W"}],
    }


def test_each_card_names_its_readings_its_special_controls_and_whether_it_is_the_hub():
    cards = {
        card["key"]: card for card in description.describe_cards(fitted=FITTED_ALL)
    }

    assert [reading["name"] for reading in cards["grid"]["readings"]] == [
        "grid_export_w",
        "grid_r_v",
        "frequency_hz",
    ]
    assert cards["battery"]["controls"] == ["state_of_charge"]
    assert cards["ev_charger"]["controls"] == ["car"]
    assert [key for key, card in cards.items() if card["hub"]] == ["inverter"]
    assert [reading["name"] for reading in cards["inverter"]["readings"]] == [
        "operating_mode",
        "application_mode",
    ]


def test_external_pv_has_a_node_and_a_card_only_where_meter_b_is_fitted():
    meter_b_only = Fitted(battery=False, meter_a=False, meter_b=True, ev_charger=False)

    nodes = by_name_kind(entries=description.describe_nodes(fitted=meter_b_only))
    cards = [card["key"] for card in description.describe_cards(fitted=meter_b_only)]
    without = by_name_kind(entries=description.describe_nodes(fitted=FITTED_NONE))

    assert nodes["external_pv"]["card"] == "external_pv"
    assert nodes["external_pv"]["readings"] == [
        {"name": "ext_pv_w", "label": "External PV power", "unit": "W"}
    ]
    assert "external_pv" in cards
    assert "external_pv" not in without


def test_the_household_load_is_the_plant_load_without_the_chargers_power():
    data = {"load_w": 11_700.0, "ev_power_w": 11_000.0}

    assert description.with_household_load(data=data)["household_load_w"] == 700.0
    assert description.with_household_load(data=data)["load_w"] == 11_700.0


def test_the_household_load_is_never_negative():
    data = {"load_w": 100.0, "ev_power_w": 150.0}

    assert description.with_household_load(data=data)["household_load_w"] == 0.0


def test_the_state_gives_each_card_reading_by_the_name_the_description_gives_it():
    data = {
        "pv_w": 10.4,
        "ext_pv_w": 2.6,
        "household_load_w": 700.0,
        "grid_export_w": -5.5,
        "grid_r_v": 230.04,
        "frequency_hz": 49.987,
        "battery_w": -0.04,
        "soc_percent": 55.54,
        "ev_power_w": 3.0,
    }
    texts = {
        "car": "Plugged in",
        "operating_mode": "2 Operating",
        "application_mode": "0 Self-use",
    }

    shown = description.card_readings(fitted=FITTED_ALL, data=data, texts=texts)
    named = {
        reading["name"]
        for card in description.describe_cards(fitted=FITTED_ALL)
        for reading in card["readings"]
    }

    assert set(shown) == named
    assert shown["frequency_hz"] == 49.99
    assert shown["car"] == "Plugged in"
    assert shown["application_mode"] == "0 Self-use"
    assert "soc_percent" not in description.card_readings(
        fitted=FITTED_NONE, data=data, texts=texts
    )


def test_the_nodes_of_fitted_equipment_name_their_card_and_the_readings_they_show():
    nodes = by_name_kind(entries=description.describe_nodes(fitted=FITTED_ALL))

    assert list(nodes) == [
        "solar",
        "external_pv",
        "grid",
        "house",
        "battery",
        "ev_charger",
    ]
    assert nodes["battery"] == {
        "kind": "battery",
        "label": "Battery",
        "card": "battery",
        "readings": [
            {"name": "battery_w", "label": "Battery power", "unit": "W"},
            {"name": "soc_percent", "label": "Battery state of charge", "unit": "%"},
        ],
    }
    assert list(
        by_name_kind(entries=description.describe_nodes(fitted=FITTED_NONE))
    ) == [
        "solar",
        "grid",
        "house",
    ]


def by_name_kind(*, entries):
    return {entry["kind"]: entry for entry in entries}


def test_the_state_gives_each_node_reading_by_the_name_the_description_gives_it():
    data = {
        "pv_w": 10.4,
        "ext_pv_w": 2.6,
        "grid_export_w": -5.5,
        "household_load_w": 7.0,
        "battery_w": -0.04,
        "soc_percent": 55.54,
        "ev_power_w": 3.0,
    }

    shown = description.node_readings(fitted=FITTED_ALL, data=data)
    named = {
        reading["name"]
        for node in description.describe_nodes(fitted=FITTED_ALL)
        for reading in node["readings"]
    }

    assert set(shown) == named
    assert shown["pv_w"] == 10
    assert str(shown["battery_w"]) == "0.0"
    assert shown["soc_percent"] == 55.5
    assert "ev_power_w" not in description.node_readings(fitted=FITTED_NONE, data=data)


@pytest.mark.parametrize(
    ("scale", "places"), [(1.0, 0), (0.1, 1), (0.01, 2), (0.0001, 4), (10.0, 0)]
)
def test_a_scale_has_as_many_places_as_its_smallest_step(scale, places):
    assert description.scale_places(scale=scale) == places


@pytest.mark.parametrize(
    ("field", "value", "shown"),
    [
        (Field(address=1, name="a", scale=0.0001), 65535 * 0.0001, 6.5535),
        (Field(address=1, name="a", scale=0.1), 0.30000000000000004, 0.3),
        (Field(address=1, name="a"), 7, 7),
        (TEXT, "abc", "abc"),
    ],
)
def test_a_stored_value_is_shown_without_floating_point_noise(field, value, shown):
    assert description.display_value(field=field, value=value) == shown


def test_the_settings_state_shows_a_scaled_value_to_its_scales_decimals():
    field = Field(
        address=1, name="limit", access=Access.READ_WRITE, scale=0.0001, initial=0
    )

    state = description.settings_state(
        fields=[field], settings={"limit": 65535 * 0.0001}
    )

    assert state == {"limit": {"raw": 65535, "value": 6.5535}}


def test_a_pack_with_codes_counts_each_non_zero_code_on_the_battery():
    faults = FaultState(
        inverter=frozenset({FaultBit(register=0x4005, bit=3)}),
        ev_charger=frozenset(
            {FaultBit(register=0x30AB, bit=1), FaultBit(register=0x30AB, bit=2)}
        ),
        packs=(PackCodes(pack=1, fault=2), PackCodes(pack=2, fault=1, warning=4)),
    )

    assert description.fault_counts(faults=faults) == {
        "inverter": 1,
        "battery": 3,
        "ev_charger": 2,
    }


def test_only_stored_settings_that_differ_from_the_scenario_are_changed():
    changed = description.changed_settings(
        fields=[SETTING, SCALED, COMMAND, READING],
        settings={"app_mode": 6, "share": 4.2},
        initial={"app_mode": 0, "share": 4.2},
    )

    assert changed == ["app_mode"]


def test_only_variation_parameters_that_differ_from_the_scenario_are_changed():
    assert description.changed_variation(
        variation={"a": 1, "b": 2, "c": 3}, scenario={"a": 1, "b": 5, "c": 3}
    ) == ["b"]


def test_holds_in_force_are_named_in_the_order_the_description_lists_them():
    assert description.held_names(holds={"frequency_hz": 50.0, "pv_w": 1.0}) == [
        "pv_w",
        "frequency_hz",
    ]


class ReadTimes:
    def __init__(self, times):
        self.times = times

    def __call__(self, *, address):
        return self.times.get(address)


def snapshot(*, last_read=description.never_read, link_refusal=None, blocks=BLOCKS):
    words = {
        "app_mode": [0],
        "share": [42],
        "signed": [0xFFFD],
        "label": [0x6162, 0x6300, 0, 0],
        "reading": [1500],
        "device_type": [0x1610],
    }
    options = {} if link_refusal is None else {"link_refusal": link_refusal}
    return description.register_snapshot(
        blocks=blocks, words=words, last_read=last_read, **options
    )["blocks"]


def block_named(*, blocks, name):
    return next(block for block in blocks if block["name"] == name)


def test_every_block_is_listed_with_its_range_and_name():
    blocks = snapshot()

    assert [(block["start"], block["end"], block["name"]) for block in blocks] == [
        ("0x3600", "0x36EF", "Settings"),
        ("0x0010", "0x002F", "0x0010-0x002F"),
        ("0x8000", "0x8023", "Commands"),
        ("0x4000", "0x4001", "Live"),
        ("0x8F00", "0x8F01", "Identity"),
        ("0x3024", "0x3025", "Refused"),
    ]


def test_a_block_the_model_refuses_has_its_code_and_no_fields():
    refused = block_named(blocks=snapshot(), name="Refused")

    assert refused["refusal"] == {"code": 0x30, "model": True, "link": False}
    assert refused["fields"] == []
    assert block_named(blocks=snapshot(), name="Live")["refusal"] is None


def test_a_block_a_link_fault_refuses_says_so_and_keeps_its_fields():
    def refuse_live(*, block):
        return 0 if block.name == "Live" else None

    live = block_named(blocks=snapshot(link_refusal=refuse_live), name="Live")

    assert live["refusal"] == {"code": 0, "model": False, "link": True}
    assert [field["name"] for field in live["fields"]] == ["reading"]


def test_a_block_refused_by_model_and_link_reports_both_with_the_model_code():
    def refuse_all(*, block):
        return 4

    refused = block_named(blocks=snapshot(link_refusal=refuse_all), name="Refused")

    assert refused["refusal"] == {"code": 0x30, "model": True, "link": True}


def test_a_field_reports_its_place_encoding_access_words_value_and_label():
    settings = block_named(blocks=snapshot(), name="Settings")["fields"]

    assert settings[0] == {
        "address": "0x3647",
        "last_address": "0x3647",
        "name": "app_mode",
        "encoding": "U16",
        "scale": 1.0,
        "access": "writable",
        "words": [0],
        "value": 0,
        "label": "Self-use",
        "last_read": None,
    }
    assert settings[1]["value"] == 4.2
    assert settings[1]["words"] == [42]


def test_a_multi_word_text_field_decodes_and_has_no_label():
    field = block_named(blocks=snapshot(), name="0x0010-0x002F")["fields"][1]

    assert (field["value"], field["label"], field["last_address"]) == (
        "abc",
        None,
        "0x0023",
    )


def test_a_signed_field_decodes_negative():
    field = block_named(blocks=snapshot(), name="0x0010-0x002F")["fields"][0]

    assert field["value"] == -3


def test_a_command_has_no_words_or_value_and_a_read_only_field_says_so():
    commands = block_named(blocks=snapshot(), name="Commands")["fields"]
    live = block_named(blocks=snapshot(), name="Live")["fields"]

    assert [(c["access"], c["words"], c["value"], c["label"]) for c in commands] == [
        ("command", None, None, None),
        ("command", None, None, None),
    ]
    assert live[0]["access"] == "read-only"


def test_a_clock_register_decodes_to_its_date_and_time():
    clock = Field(address=0x10, name="clock", encoding=Encoding.CLOCK)
    block = Block(start=0x10, end=0x13, fields=(clock,))

    (shown,) = description.register_snapshot(
        blocks=[block], words={"clock": [2026, 0x070A, 0x0930, 0x1500]}
    )["blocks"]

    assert shown["fields"][0]["value"] == "2026-07-10T09:48:21+00:00"


def test_the_last_read_of_a_field_is_the_latest_of_its_words_or_none():
    last_read = ReadTimes({0x3647: 10.0, 0x4000: 99.5, 0x0010: 5.0, 0x0011: 8.0})

    blocks = snapshot(last_read=last_read)

    assert block_named(blocks=blocks, name="Settings")["fields"][0]["last_read"] == 10.0
    assert block_named(blocks=blocks, name="Settings")["fields"][1]["last_read"] is None
    assert block_named(blocks=blocks, name="Live")["fields"][0]["last_read"] == 99.5
    assert (
        block_named(blocks=blocks, name="0x0010-0x002F")["fields"][1]["last_read"]
        is None
    )
    multi = Field(address=0x20, name="wide", encoding=Encoding.U32)
    wide = Block(start=0x20, end=0x21, fields=(multi,))
    shown = description.register_snapshot(
        blocks=[wide],
        words={"wide": [0, 1]},
        last_read=ReadTimes({0x20: 3.0, 0x21: 7.0}),
    )
    assert shown["blocks"][0]["fields"][0]["last_read"] == 7.0


def test_the_link_description_lists_each_setting_with_its_bounds_and_scenario_value():
    scenario = LinkSettings(
        latency_ms=7, refused_blocks=(RefusedBlock(start=1, end=2, code=3),)
    )

    settings = description.describe_link(scenario=scenario)["settings"]

    names = [setting["name"] for setting in settings]
    assert names[0] == "latency_ms"
    assert names[-1] == "refused_blocks"
    assert settings[0] == {
        "name": "latency_ms",
        "kind": "whole",
        "minimum": 0,
        "maximum": 60_000,
        "unit": "ms",
        "scenario": 7,
    }
    assert settings[-1]["scenario"] == [{"start": 1, "end": 2, "code": 3}]
    assert settings[-1]["address_bounds"] == [0, 65535]
    assert settings[-1]["code_bounds"] == [0, 255]


def test_the_decoder_decodes_every_field_the_words_cover_and_none_cut_short():
    decoder = description.DeviceFieldDecoder(
        blocks=[Block(start=0x10, end=0x30, fields=(SIGNED, TEXT))]
    )

    covered = decoder.decode(start=0x10, words=(0xFFFF, 0))

    assert [(field.address, field.name, field.words) for field in covered] == [
        (0x10, "signed", (0xFFFF,))
    ]
    assert covered[0].value == -1
    assert decoder.decode(start=0x11, words=(1, 2)) == []


def test_the_decoder_reports_the_label_and_scaled_value_of_a_field():
    decoder = description.DeviceFieldDecoder(
        blocks=[Block(start=0x3639, end=0x3647, fields=(SCALED, SETTING))]
    )

    labelled, scaled = decoder.decode(start=0x3639, words=[42] + [0] * 14)[::-1]

    assert (labelled.name, labelled.value, labelled.label) == (
        "app_mode",
        0,
        "Self-use",
    )
    assert (scaled.name, scaled.value, scaled.label) == ("share", 4.2, None)
