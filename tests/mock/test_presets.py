import pytest

from saj_local_mock import presets
from saj_local_mock.presets import Fitted, Needs
from saj_local_mock.simulation.environment import PARAMETERS_BY_NAME, checked_parameter
from saj_local_mock.simulation.faults import Equipment

EVERYTHING = Fitted(battery=True, meter_a=True, meter_b=True, ev_charger=True)
NOTHING = Fitted(battery=False, meter_a=False, meter_b=False, ev_charger=False)


class StubFaultMap:
    """Answers `find` for the named conditions it has."""

    def __init__(self, *, names):
        self._names = names

    def find(self, *, equipment, name):
        return (1,) if (equipment, name) in self._names else ()


FULL_MAP = StubFaultMap(
    names={
        (Equipment.INVERTER, "Grid lost"),
        (Equipment.INVERTER, "Over temperature"),
        (Equipment.INVERTER, "Meter communication lost"),
        (Equipment.BATTERY, "Battery too hot to charge"),
    }
)
NO_BATTERY_TABLE = StubFaultMap(
    names={
        (Equipment.INVERTER, "Grid lost"),
        (Equipment.INVERTER, "Over temperature"),
        (Equipment.INVERTER, "Meter communication lost"),
    }
)


def keys(*, fitted, fault_map):
    return {
        preset.key
        for preset in presets.available_presets(fitted=fitted, fault_map=fault_map)
    }


ALWAYS = {
    "clear-sky",
    "overcast",
    "high-load",
    "low-load",
    "unstable-grid",
    "grid-lost",
    "inverter-over-temperature",
    "slow-link",
    "flaky-link",
    "busy-module",
    "module-offline",
    "module-locked-out",
}


def test_every_preset_is_offered_when_everything_is_fitted_and_named():
    assert keys(fitted=EVERYTHING, fault_map=FULL_MAP) == {
        preset.key for preset in presets.PRESETS
    }


def test_with_nothing_fitted_only_the_presets_that_need_no_equipment_remain():
    assert keys(fitted=NOTHING, fault_map=FULL_MAP) == ALWAYS


@pytest.mark.parametrize(
    ("fitted", "fault_map", "expected"),
    [
        (
            Fitted(battery=True, meter_a=False, meter_b=False, ev_charger=False),
            FULL_MAP,
            {
                "battery-empty",
                "battery-full",
                "battery-too-hot-to-charge",
                "battery-pack-fault",
            },
        ),
        (
            Fitted(battery=True, meter_a=False, meter_b=False, ev_charger=False),
            NO_BATTERY_TABLE,
            {"battery-empty", "battery-full", "battery-pack-fault"},
        ),
        (
            Fitted(battery=False, meter_a=True, meter_b=True, ev_charger=False),
            FULL_MAP,
            {"meter-communication-lost"},
        ),
        (
            Fitted(battery=False, meter_a=False, meter_b=False, ev_charger=True),
            FULL_MAP,
            {"ev-charging"},
        ),
    ],
)
def test_equipment_presets_need_their_equipment_and_a_fault_the_model_names(
    fitted, fault_map, expected
):
    assert keys(fitted=fitted, fault_map=fault_map) - ALWAYS == expected


def test_a_preset_whose_fault_the_model_does_not_name_is_not_offered_even_when_fitted():
    empty = StubFaultMap(names=set())

    assert (
        keys(fitted=EVERYTHING, fault_map=empty)
        & {
            "grid-lost",
            "inverter-over-temperature",
            "meter-communication-lost",
            "battery-too-hot-to-charge",
        }
        == set()
    )


@pytest.mark.parametrize(
    ("needs", "fitted", "expected"),
    [
        (Needs.NOTHING, NOTHING, True),
        (Needs.BATTERY, NOTHING, False),
        (
            Needs.BATTERY,
            Fitted(battery=True, meter_a=False, meter_b=False, ev_charger=False),
            True,
        ),
        (
            Needs.METER_A,
            Fitted(battery=False, meter_a=True, meter_b=True, ev_charger=False),
            True,
        ),
        (Needs.METER_A, NOTHING, False),
        (
            Needs.EV_CHARGER,
            Fitted(battery=False, meter_a=False, meter_b=False, ev_charger=True),
            True,
        ),
        (Needs.EV_CHARGER, NOTHING, False),
    ],
)
def test_a_preset_needs_the_equipment_it_is_about(needs, fitted, expected):
    assert fitted.has(needs=needs) is expected


def test_preset_keys_and_names_are_unique():
    keys_ = [preset.key for preset in presets.PRESETS]
    names = [preset.name for preset in presets.PRESETS]

    assert len(set(keys_)) == len(keys_)
    assert len(set(names)) == len(names)


@pytest.mark.parametrize("preset", presets.PRESETS, ids=lambda preset: preset.key)
def test_every_variation_a_preset_sets_is_a_parameter_within_its_bounds(preset):
    for name, value in preset.variation.items():
        checked_parameter(spec=PARAMETERS_BY_NAME[name], value=value)
    if "peak_w" in preset.variation:
        assert preset.variation["peak_w"] >= preset.variation["base_w"]


LINK_PRESETS = {
    "slow-link": {"latency_ms": 800, "jitter_ms": 400},
    "flaky-link": {"no_answer_percent": 5, "dropped_connection_percent": 2},
    "busy-module": {"busy_percent": 10, "late_duplicate_percent": 100},
    "module-offline": {"offline": True},
    "module-locked-out": {
        "lockout_requests": 120,
        "lockout_window_seconds": 60,
        "lockout_whole_port": True,
    },
}


@pytest.mark.parametrize(("key", "link"), LINK_PRESETS.items())
def test_each_link_preset_sets_the_link_settings_the_plan_names(key, link):
    preset = next(known for known in presets.PRESETS if known.key == key)

    assert preset.link == link
    assert preset.needs is Needs.NOTHING
