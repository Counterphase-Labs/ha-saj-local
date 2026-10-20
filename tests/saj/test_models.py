from dataclasses import replace

import pytest

from saj.models import (
    ALL_EQUIPMENT,
    METER_A_PROBE,
    PARALLEL_PROBE,
    Comparison,
    Condition,
    EnableBitMethod,
    Equipment,
    Evidence,
    FamilyPlacement,
    OperatingModeMethod,
    Placement,
    PowerFunction,
    Probe,
    Profile,
    Shape,
    Span,
    ems_rows,
    placements_by_evidence,
)

ENABLE = EnableBitMethod(
    enable_key="grid_enable",
    target_key="grid_target",
    alternate_keys=("grid_enable_alt",),
    timeout_key="grid_timeout",
    limit_keys=("grid_limit_a", "grid_limit_b"),
)
BARE = EnableBitMethod(enable_key="battery_enable", target_key="battery_target")
MODE = OperatingModeMethod(
    mode_key="mode",
    passive_mode=7,
    default_mode=1,
    direction_key="direction",
    standby=0,
    discharge=1,
    charge=2,
    charge_power_key="charge_power",
    discharge_power_key="discharge_power",
)
SHAPE = Shape(phases=3, strings=2)
RECOGNISED_TYPE = 0x10
UNRECOGNISED_TYPE = 0x99


def _profile(**changes) -> Profile:
    base = Profile(
        key="unit",
        display_name="Unit",
        device_types={RECOGNISED_TYPE: Shape(phases=1, strings=1)},
        hand_verified=True,
        maximum_shape=SHAPE,
    )
    return replace(base, **changes)


@pytest.mark.parametrize("function", list(PowerFunction))
def test_a_power_function_builds_its_switch_and_target_keys_from_its_value(
    function: PowerFunction,
):
    assert function.switch_key == f"{function.value}_power_control"
    assert function.target_key == f"{function.value}_power_target"


def test_an_enable_bit_method_lists_its_enable_key_before_its_alternates():
    assert ENABLE.forms == ("grid_enable", "grid_enable_alt")
    assert BARE.forms == ("battery_enable",)


def test_an_enable_bit_method_stops_on_any_of_its_forms():
    assert ENABLE.stop_keys == {"grid_enable", "grid_enable_alt"}


def test_an_enable_bit_method_owns_its_enable_and_target_rows():
    assert ENABLE.row_keys == {"grid_enable", "grid_target"}


@pytest.mark.parametrize(
    ("key", "value", "accepted"),
    [
        ("grid_enable", 0, True),
        ("grid_enable_alt", 0, True),
        ("grid_enable", 1, False),
        ("grid_target", 0, False),
    ],
)
def test_an_enable_bit_method_accepts_a_stop_only_as_zero_in_a_form(
    key: str, value: int, *, accepted: bool
):
    assert ENABLE.accepts_stop(key=key, value=value) is accepted


def test_an_operating_mode_method_stops_on_its_mode_or_direction_key():
    assert MODE.stop_keys == {"mode", "direction"}


def test_an_operating_mode_method_owns_its_mode_direction_and_power_rows():
    assert MODE.row_keys == {"mode", "direction", "charge_power", "discharge_power"}


@pytest.mark.parametrize(
    ("key", "value", "accepted"),
    [
        ("direction", MODE.standby, True),
        ("direction", MODE.charge, False),
        ("mode", MODE.default_mode, True),
        ("mode", MODE.passive_mode, False),
        ("charge_power", MODE.default_mode, False),
    ],
)
def test_an_operating_mode_method_accepts_standby_or_leaving_passive_as_a_stop(
    key: str, value: int, *, accepted: bool
):
    assert MODE.accepts_stop(key=key, value=value) is accepted


def test_ems_rows_only_describe_functions_that_use_enable_bits():
    profile = _profile(
        power_control={
            PowerFunction.GRID: ENABLE,
            PowerFunction.BATTERY: BARE,
            PowerFunction.INVERTER: MODE,
        }
    )

    rows = ems_rows(profile=profile)

    assert rows.functions == {
        "grid_enable": PowerFunction.GRID,
        "grid_enable_alt": PowerFunction.GRID,
        "battery_enable": PowerFunction.BATTERY,
    }
    assert rows.forms["grid_enable_alt"] == ENABLE.forms
    assert rows.forms["battery_enable"] == BARE.forms
    assert rows.targets == {
        PowerFunction.GRID: "grid_target",
        PowerFunction.BATTERY: "battery_target",
    }
    assert rows.timeouts == {"grid_timeout"}
    assert rows.limits == {"grid_limit_a", "grid_limit_b"}


def test_ems_rows_map_each_target_key_back_to_its_function():
    profile = _profile(power_control={PowerFunction.GRID: ENABLE})

    assert ems_rows(profile=profile).target_functions == {
        "grid_target": PowerFunction.GRID
    }


def test_ems_rows_of_a_profile_without_power_control_are_empty():
    rows = ems_rows(profile=_profile())

    assert rows.functions == {}
    assert rows.timeouts == frozenset()
    assert rows.target_functions == {}


def test_a_probe_lists_each_condition_key_once_in_order():
    probe = Probe(
        equipment=Equipment.PARALLEL,
        conditions=(
            Condition(key="a", comparison=Comparison.EQUALS, reference=1),
            Condition(key="b", comparison=Comparison.ABOVE, reference=1),
            Condition(key="a", comparison=Comparison.DIFFERS, reference=0),
        ),
        unanswered=False,
    )

    assert probe.keys == ("a", "b")


def test_a_profile_fits_the_equipment_its_probes_detect():
    profile = _profile(probes=(METER_A_PROBE, PARALLEL_PROBE))

    assert profile.equipment == {Equipment.METER_A, Equipment.PARALLEL}
    assert profile.equipment <= ALL_EQUIPMENT


def test_a_profile_without_probes_fits_no_optional_equipment():
    assert _profile().equipment == frozenset()


def test_a_recognised_device_type_uses_its_own_shape():
    assert _profile().shape_of(device_type=RECOGNISED_TYPE) == Shape(
        phases=1, strings=1
    )


def test_an_unrecognised_device_type_assumes_the_maximum_shape():
    shape = _profile().shape_of(device_type=UNRECOGNISED_TYPE)

    assert (shape.phases, shape.strings) == (SHAPE.phases, SHAPE.strings)
    assert shape.assumed is True


@pytest.mark.parametrize(
    ("address", "words", "contains", "overlaps"),
    [
        (10, 5, True, True),
        (10, 1, True, True),
        (14, 1, True, True),
        (14, 2, False, True),
        (9, 2, False, True),
        (8, 2, False, False),
        (15, 1, False, False),
        (5, 20, False, True),
    ],
)
def test_a_span_distinguishes_containing_from_overlapping_a_request(
    address: int, words: int, *, contains: bool, overlaps: bool
):
    span = Span(name="span", first=10, last=14)

    assert span.contains(address=address, words=words) is contains
    assert span.overlaps(address=address, words=words) is overlaps


def test_placements_are_flattened_with_the_evidence_of_their_group():
    placements = placements_by_evidence(
        groups={
            Evidence.VERIFIED: {"a": 1, "b": None},
            Evidence.DOCUMENTED: {"c": 3},
        }
    )

    assert placements == (
        Placement(key="a", address=1, evidence=Evidence.VERIFIED),
        Placement(key="b", address=None, evidence=Evidence.VERIFIED),
        Placement(key="c", address=3, evidence=Evidence.DOCUMENTED),
    )


def test_no_evidence_groups_give_no_placements():
    assert placements_by_evidence(groups={}) == ()


def test_a_family_placement_has_no_exceptions_unless_given_and_does_not_share_them():
    first = FamilyPlacement(family="f", evidence=Evidence.VERIFIED)
    second = FamilyPlacement(family="f", evidence=Evidence.VERIFIED)

    assert first.exceptions == {}
    assert first.exceptions is not second.exceptions
