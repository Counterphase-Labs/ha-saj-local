import math

import pytest

from saj.estimator import (
    BatteryEstimator,
    BatteryReading,
    Estimates,
    estimate_sources,
)
from saj.learner import Learner, LearnerState, PowerReading, SocReading
from saj.models.h2 import PROFILE as H2
from saj.models.hs3 import PROFILE as HS3

MINUTE = 60
TEN_KWH = LearnerState(energy_total=10.0, soc_total=100.0)


def _learned_estimator() -> BatteryEstimator:
    return BatteryEstimator(profile=HS3, learner=Learner(state=TEN_KWH))


def _reading(**changes: float | None) -> BatteryReading:
    figures: dict[str, float | None] = {
        "power": 1000.0,
        "soc": 50.0,
        "voltage": 100.0,
        "usable_capacity": 100.0,
        "full_limit": 100.0,
        "backup_reserve": 30.0,
        "on_grid_limit": 10.0,
        "off_grid_limit": 20.0,
        "application_mode": 0,
        "operating_mode": 2,
    }
    return BatteryReading(**{**figures, **changes})


def test_the_first_reading_is_the_average():
    estimator = _learned_estimator()

    estimates = estimator.update(reading=_reading(power=2000.0), time=0)

    assert estimates.time_to_empty == round(4 / 2 * 60)


def test_a_later_reading_moves_the_average_by_the_time_since_the_one_before():
    estimator = _learned_estimator()
    estimator.update(reading=_reading(power=1000.0), time=0)

    estimates = estimator.update(reading=_reading(power=3000.0), time=10 * MINUTE)

    average = 1000 + (1 - math.exp(-1)) * 2000
    assert estimates.time_to_empty == round(4 / (average / 1000) * 60)


def test_the_average_does_not_depend_on_how_often_the_battery_is_read():
    often = _learned_estimator()
    rarely = _learned_estimator()
    often.update(reading=_reading(power=1000.0), time=0)
    rarely.update(reading=_reading(power=1000.0), time=0)

    for minute in range(1, 11):
        often_estimates = often.update(
            reading=_reading(power=3000.0), time=minute * MINUTE
        )
    rarely_estimates = rarely.update(reading=_reading(power=3000.0), time=10 * MINUTE)

    assert often_estimates.time_to_empty == rarely_estimates.time_to_empty


def test_a_reading_without_power_keeps_the_average():
    estimator = _learned_estimator()
    estimator.update(reading=_reading(power=2000.0), time=0)

    estimates = estimator.update(reading=_reading(power=None), time=MINUTE)

    assert estimates.time_to_empty == round(4 / 2 * 60)


def test_a_reading_at_the_same_moment_or_earlier_does_not_move_the_average():
    estimator = _learned_estimator()
    estimator.update(reading=_reading(power=2000.0), time=10)

    estimates = estimator.update(reading=_reading(power=9000.0), time=5)

    assert estimates.time_to_empty == round(4 / 2 * 60)


@pytest.mark.parametrize(
    ("power", "to_full", "to_empty"),
    [
        (-2000.0, round(5 / 2 * 60), None),
        (2000.0, None, round(4 / 2 * 60)),
        (0.0, None, None),
    ],
)
def test_each_time_has_a_value_only_while_the_average_goes_that_way(
    power: float, to_full: int | None, to_empty: int | None
):
    estimator = _learned_estimator()

    estimates = estimator.update(reading=_reading(power=power), time=0)

    assert (estimates.time_to_full, estimates.time_to_empty) == (to_full, to_empty)


def test_a_charge_that_turns_into_a_discharge_swaps_which_time_has_a_value():
    estimator = _learned_estimator()
    estimator.update(reading=_reading(power=-2000.0), time=0)

    estimates = estimator.update(reading=_reading(power=6000.0), time=120 * MINUTE)

    assert estimates.time_to_full is None
    assert estimates.time_to_empty is not None


@pytest.mark.parametrize(
    ("power", "field"),
    [(1.0, "time_to_empty"), (-1.0, "time_to_full")],
)
def test_a_time_over_48_hours_is_unknown(power: float, field: str):
    estimator = _learned_estimator()

    estimates = estimator.update(reading=_reading(power=power), time=0)

    assert getattr(estimates, field) is None


def test_a_time_just_inside_48_hours_has_a_value():
    estimator = _learned_estimator()

    estimates = estimator.update(reading=_reading(power=-110.0), time=0)

    assert estimates.time_to_full == round(5 / 0.11 * 60)


@pytest.mark.parametrize(
    ("changes", "field"),
    [
        ({"power": -500.0, "soc": 100.0}, "time_to_full"),
        ({"power": -500.0, "soc": 101.0}, "time_to_full"),
        ({"power": 500.0, "soc": 10.0}, "time_to_empty"),
        ({"power": 500.0, "soc": 9.0}, "time_to_empty"),
    ],
)
def test_a_time_is_zero_when_the_soc_is_at_or_past_its_limit(
    changes: dict[str, float], field: str
):
    estimator = _learned_estimator()

    estimates = estimator.update(reading=_reading(**changes), time=0)

    assert getattr(estimates, field) == 0


@pytest.mark.parametrize(
    ("profile", "changes", "limit"),
    [
        (HS3, {"application_mode": 2}, 30),
        (HS3, {"application_mode": 0}, 10),
        (HS3, {"application_mode": 1}, 10),
        (HS3, {"operating_mode": 3}, 10),
        (H2, {"operating_mode": 3}, 20),
        (H2, {"operating_mode": 2}, 10),
        (H2, {"application_mode": 2, "operating_mode": 3}, 30),
        (HS3, {"application_mode": 2, "operating_mode": 3}, 30),
    ],
)
def test_the_empty_limit_follows_the_application_mode_and_the_operating_mode(
    profile, changes: dict[str, float], limit: int
):
    estimator = BatteryEstimator(profile=profile, learner=Learner(state=TEN_KWH))

    estimates = estimator.update(reading=_reading(**changes), time=0)

    assert estimates.available_energy == round((50 - limit) / 100 * 10, 2)


def test_the_available_energy_is_never_below_zero():
    estimator = _learned_estimator()

    estimates = estimator.update(reading=_reading(soc=5.0), time=0)

    assert estimates.available_energy == 0
    assert estimates.stored_energy == 0.5


def test_a_usable_capacity_gives_the_battery_energy_with_the_live_voltage():
    estimator = BatteryEstimator(profile=H2)

    estimates = estimator.update(
        reading=_reading(usable_capacity=200.0, voltage=51.2, power=-1024.0), time=0
    )

    assert estimates.stored_energy == 5.12
    assert estimates.time_to_full == round(5.12 / 1.024 * 60)
    assert estimator.learner is None


@pytest.mark.parametrize(
    "changes",
    [
        {"usable_capacity": None},
        {"voltage": None},
        {"usable_capacity": 0.0},
        {"voltage": 0.0},
        {"soc": None},
    ],
)
def test_a_missing_or_zero_input_leaves_every_estimate_unknown(
    changes: dict[str, float | None],
):
    estimator = BatteryEstimator(profile=H2)

    estimates = estimator.update(reading=_reading(**changes), time=0)

    assert estimates == Estimates()


@pytest.mark.parametrize(
    ("changes", "known"),
    [
        ({"on_grid_limit": None}, {"time_to_full", "stored_energy"}),
        ({"full_limit": None}, {"time_to_empty", "stored_energy", "available_energy"}),
        (
            {"power": None},
            {"stored_energy", "available_energy"},
        ),
    ],
)
def test_a_missing_limit_or_power_leaves_only_the_estimates_that_need_it_unknown(
    changes: dict[str, float | None], known: set[str]
):
    estimator = _learned_estimator()
    power = 2000.0 if "full_limit" in changes else -2000.0
    if "power" in changes:
        power = None

    estimates = estimator.update(
        reading=_reading(**{"power": power, **changes}), time=0
    )

    assert {
        name for name, value in vars(estimates).items() if value is not None
    } == known


def test_a_learned_capacity_is_unknown_until_the_soc_changes_between_two_polls():
    estimator = BatteryEstimator(profile=HS3)

    first = estimator.update(reading=_reading(power=-4000.0, soc=50.0), time=0)
    second = estimator.update(reading=_reading(power=-4000.0, soc=50.5), time=MINUTE)

    assert first == Estimates()
    assert second.stored_energy == pytest.approx(6.73, abs=0.01)
    assert estimator.learner is not None
    assert estimator.learner.capacity == pytest.approx(13.33, abs=0.01)


def test_a_reading_without_power_or_soc_is_not_shown_to_the_learner():
    estimator = BatteryEstimator(profile=HS3)

    estimator.update(reading=_reading(power=None, soc=None), time=0)
    estimator.update(reading=_reading(power=None, soc_read=False), time=MINUTE)

    assert estimator.learner is not None
    assert estimator.learner.state == LearnerState()


def test_a_soc_that_a_poll_did_not_read_moves_no_soc_in_the_learner():
    estimator = BatteryEstimator(profile=HS3)

    estimator.update(reading=_reading(power=-4000.0, soc=50.0), time=0)
    estimator.update(
        reading=_reading(power=-4000.0, soc=50.0, soc_read=False), time=MINUTE
    )

    assert estimator.learner is not None
    assert estimator.learner.state.reading == SocReading(time=0, soc=50.0)
    assert estimator.learner.state.power == PowerReading(time=MINUTE, power=-4000.0)


def test_the_capacity_changes_only_when_a_soc_reading_arrives():
    estimator = BatteryEstimator(profile=HS3)
    estimator.update(reading=_reading(power=1000.0, soc=50.0), time=0)
    estimator.update(reading=_reading(power=1000.0, soc=49.0), time=60)
    assert estimator.learner is not None
    capacity = estimator.learner.capacity

    for second in range(70, 121, 10):
        estimator.update(
            reading=_reading(power=1000.0, soc=49.0, soc_read=False), time=second
        )
        assert estimator.learner.capacity == capacity
    estimator.update(reading=_reading(power=1000.0, soc=48.0), time=180)

    assert estimator.learner.capacity != capacity


def test_the_energy_at_the_start_of_a_discharge_counts_with_a_slow_soc():
    estimator = BatteryEstimator(profile=HS3)
    estimator.update(reading=_reading(power=1170.0, soc=17.01), time=0)
    for second in range(10, 61, 10):
        estimator.update(
            reading=_reading(power=1170.0, soc=17.01, soc_read=False), time=second
        )

    estimator.update(reading=_reading(power=1170.0, soc=16.82), time=61)

    assert estimator.learner is not None
    assert estimator.learner.capacity == pytest.approx(10.4, abs=0.1)


def test_a_soc_among_the_values_that_a_poll_did_not_read_is_marked_unread():
    values = {"battery_power": -120, "battery_soc": 55.5}

    reading = BatteryReading.of(values=values, read=("battery_power",))

    assert not reading.soc_read
    assert reading.soc == 55.5


def test_the_sources_follow_what_the_model_gives():
    common = set(estimate_sources(profile=HS3))

    assert {"battery_power", "battery_soc"} <= common
    assert not common & {
        "battery_usable_capacity",
        "battery_discharge_soc_limit_off_grid",
    }
    assert set(estimate_sources(profile=H2)) - common == {
        "battery_usable_capacity",
        "battery_voltage",
        "battery_discharge_soc_limit_off_grid",
    }


def test_a_reading_is_built_from_the_numbers_among_the_values():
    reading = BatteryReading.of(
        values={
            "battery_power": -120,
            "battery_soc": 55.5,
            "battery_voltage": 51.2,
            "battery_usable_capacity": 100,
            "battery_charge_soc_limit": 95,
            "backup_reserve_soc": 20,
            "battery_discharge_soc_limit_on_grid": 10,
            "battery_discharge_soc_limit_off_grid": 5,
            "application_mode": 2,
            "operating_mode": "off_grid",
        },
        read=("battery_power", "battery_soc"),
    )

    assert reading == BatteryReading(
        soc_read=True,
        power=-120.0,
        soc=55.5,
        voltage=51.2,
        usable_capacity=100.0,
        full_limit=95.0,
        backup_reserve=20.0,
        on_grid_limit=10.0,
        off_grid_limit=5.0,
        application_mode=2.0,
        operating_mode=None,
    )
