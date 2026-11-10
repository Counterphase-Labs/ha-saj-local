import pytest

from saj.learner import (
    Learner,
    LearnerState,
    LearnerStateError,
    Poll,
    PowerReading,
    Run,
    SocReading,
)

MINUTE = 60
CHARGING = -4990
_VALID: dict[str, object] = {
    "energy_total": 1,
    "soc_total": 1,
    "run": None,
    "power": None,
    "reading": None,
    "pending": 0,
}


def _drive(
    learner: Learner, *, start: float, end: float, power: float, during: range
) -> None:
    for step, minute in enumerate(during):
        soc = round(start + (end - start) * step / (len(during) - 1), 2)
        learner.observe(poll=Poll(time=minute * MINUTE, power=power, soc=soc))


@pytest.mark.parametrize(
    ("start", "end", "minutes", "capacity"),
    [(40.94, 44.79, 15, 32.40), (40.94, 42.21, 5, 32.74)],
)
def test_a_constant_charge_gives_the_capacity_of_its_energy_over_its_soc_change(
    start: float, end: float, minutes: int, capacity: float
):
    learner = Learner()

    _drive(learner, start=start, end=end, power=CHARGING, during=range(minutes + 1))

    assert learner.capacity == pytest.approx(capacity, abs=0.005)


def test_the_capacity_exists_from_the_second_poll():
    learner = Learner()
    learner.observe(poll=Poll(time=0, power=-4000, soc=50.0))
    learner.observe(poll=Poll(time=MINUTE, power=-4000, soc=50.5))

    assert learner.capacity == pytest.approx(13.33, abs=0.005)


def test_the_capacity_is_unknown_until_the_soc_changes():
    learner = Learner()

    assert learner.capacity is None
    learner.observe(poll=Poll(time=0, power=-4000, soc=50.0))
    assert learner.capacity is None
    learner.observe(poll=Poll(time=MINUTE, power=-4000, soc=50.0))
    assert learner.capacity is None


def test_a_charge_then_a_discharge_both_add_to_the_totals():
    learner = Learner()

    _drive(learner, start=50, end=60, power=-2000, during=range(31))
    _drive(learner, start=60, end=50, power=2000, during=range(31, 62))

    assert learner.capacity == pytest.approx(10.0, rel=0.01)
    assert learner.state.run is not None
    assert not learner.state.run.charging
    assert learner.state.soc_total == pytest.approx(10.0)
    assert learner.state.energy_total == pytest.approx(1.0, rel=0.01)


def test_a_movement_back_of_less_than_a_tenth_of_a_point_keeps_the_charge_going():
    learner = Learner()
    _drive(learner, start=50, end=51, power=-2000, during=range(4))

    for minute, soc in enumerate((50.95, 51.0, 50.95, 51.05), start=4):
        learner.observe(poll=Poll(time=minute * MINUTE, power=-2000, soc=soc))

    run = learner.state.run
    assert run is not None
    assert run.charging
    assert run.extreme_soc == 51.05
    assert learner.state.soc_total == 0


def test_a_movement_back_of_a_tenth_of_a_point_starts_a_discharge_at_the_peak():
    learner = Learner()
    _drive(learner, start=50, end=51, power=-2000, during=range(4))

    learner.observe(poll=Poll(time=4 * MINUTE, power=2000, soc=50.9))

    run = learner.state.run
    assert run is not None
    assert not run.charging
    assert run.start_soc == 51
    assert learner.state.soc_total == pytest.approx(1.0)


def test_a_gap_over_ten_minutes_ends_the_run_and_leaves_the_pair_out():
    learner = Learner()
    _drive(learner, start=50, end=52, power=-2000, during=range(5))
    before = learner.capacity

    learner.observe(poll=Poll(time=15 * MINUTE, power=-2000, soc=60.0))

    assert learner.state.run is None
    assert learner.state.soc_total == pytest.approx(2.0)
    assert learner.capacity == pytest.approx(before)
    assert learner.state.power == PowerReading(time=15 * MINUTE, power=-2000)
    assert learner.state.reading == SocReading(time=15 * MINUTE, soc=60.0)


def test_a_jump_of_more_than_five_points_ends_the_run_and_leaves_the_pair_out():
    learner = Learner()
    _drive(learner, start=50, end=52, power=-2000, during=range(5))

    learner.observe(poll=Poll(time=5 * MINUTE, power=-2000, soc=58.0))

    assert learner.state.run is None
    assert learner.state.soc_total == pytest.approx(2.0)


def test_a_gap_without_a_run_in_progress_changes_no_total():
    learner = Learner()
    learner.observe(poll=Poll(time=0, power=0, soc=50.0))

    learner.observe(poll=Poll(time=20 * MINUTE, power=0, soc=51.0))

    assert learner.state == LearnerState(
        power=PowerReading(time=20 * MINUTE, power=0),
        reading=SocReading(time=20 * MINUTE, soc=51.0),
    )


def test_the_energy_before_the_first_soc_change_counts_with_a_slow_soc():
    learner = Learner()
    learner.observe(poll=Poll(time=0, power=1170, soc=17.01))
    for second in range(10, 61, 10):
        learner.observe(poll=Poll(time=second, power=1170))

    learner.observe(poll=Poll(time=61, power=1170, soc=16.82))

    assert learner.capacity == pytest.approx(10.4, abs=0.1)


def test_a_slow_soc_keeps_the_capacity_between_two_soc_readings():
    learner = Learner()
    learner.observe(poll=Poll(time=0, power=-2000, soc=50.0))
    learner.observe(poll=Poll(time=60, power=-2000, soc=50.5))
    capacity = learner.capacity

    for second in range(70, 120, 10):
        learner.observe(poll=Poll(time=second, power=-2000))
        assert learner.capacity == capacity
    learner.observe(poll=Poll(time=120, power=-2000, soc=51.0))

    assert learner.capacity == pytest.approx(capacity)
    assert learner.state.run is not None
    assert learner.state.run.energy == pytest.approx(-4 / 60)


def test_a_poll_with_a_soc_and_no_power_moves_only_the_soc():
    learner = Learner()
    learner.observe(poll=Poll(time=0, power=-2000, soc=50.0))

    learner.observe(poll=Poll(time=MINUTE, soc=50.5))

    assert learner.state.power == PowerReading(time=0, power=-2000)
    assert learner.state.reading == SocReading(time=MINUTE, soc=50.5)
    assert learner.state.pending == 0


def test_a_power_gap_between_two_soc_readings_leaves_the_pair_out():
    learner = Learner()
    learner.observe(poll=Poll(time=0, power=-2000, soc=50.0))
    learner.observe(poll=Poll(time=MINUTE, power=-2000, soc=50.5))
    learner.observe(poll=Poll(time=2 * MINUTE, power=-2000))
    learner.observe(poll=Poll(time=15 * MINUTE, power=-2000))
    assert learner.state.pending is None

    learner.observe(poll=Poll(time=16 * MINUTE, power=-2000, soc=51.0))

    assert learner.state.run is None
    assert learner.state.pending == 0
    assert learner.state.soc_total == pytest.approx(0.5)


def test_a_soc_gap_without_a_power_gap_ends_the_run():
    learner = Learner()
    learner.observe(poll=Poll(time=0, power=-2000, soc=50.0))
    learner.observe(poll=Poll(time=MINUTE, power=-2000, soc=50.5))
    for minute in range(2, 13):
        learner.observe(poll=Poll(time=minute * MINUTE, power=-2000))

    learner.observe(poll=Poll(time=13 * MINUTE, power=-2000, soc=51.0))

    assert learner.state.run is None


def test_a_poll_that_is_not_later_than_the_last_one_is_ignored():
    learner = Learner()
    learner.observe(poll=Poll(time=MINUTE, power=-2000, soc=50.0))
    state = learner.state

    learner.observe(poll=Poll(time=MINUTE, power=-2000, soc=55.0))

    assert learner.state == state


def test_a_restart_in_the_middle_of_a_charge_continues_the_same_run():
    continuous = Learner()
    _drive(continuous, start=40, end=45, power=CHARGING, during=range(11))
    restarted = Learner()
    _drive(restarted, start=40, end=42.5, power=CHARGING, during=range(6))

    resumed = Learner(state=LearnerState.from_mapping(restarted.state.to_mapping()))
    _drive(resumed, start=42.5, end=45, power=CHARGING, during=range(5, 11))

    assert resumed.capacity == pytest.approx(continuous.capacity)


@pytest.mark.parametrize(("downtime_minutes", "kept_in_run"), [(9, True), (11, False)])
def test_a_restart_after_a_crash_joins_the_run_only_when_the_gap_is_short(
    downtime_minutes: int, *, kept_in_run: bool
):
    crashed = Learner()
    _drive(crashed, start=40, end=42, power=CHARGING, during=range(5))
    resumed = Learner(state=LearnerState.from_mapping(crashed.state.to_mapping()))

    resumed.observe(
        poll=Poll(time=(4 + downtime_minutes) * MINUTE, power=CHARGING, soc=42.5)
    )

    assert (resumed.state.run is not None) is kept_in_run
    assert resumed.capacity is not None


def test_a_state_survives_the_stored_form():
    learner = Learner()
    _drive(learner, start=50, end=60, power=-2000, during=range(31))
    _drive(learner, start=60, end=58, power=2000, during=range(31, 38))

    stored = learner.state.to_mapping()

    assert LearnerState.from_mapping(stored) == learner.state
    assert LearnerState.from_mapping(LearnerState().to_mapping()) == LearnerState()


def test_the_stored_form_of_a_run_in_progress_holds_its_figures():
    state = LearnerState(
        energy_total=1.0,
        soc_total=2.0,
        run=Run(
            charging=True,
            start_soc=1.0,
            extreme_soc=3.0,
            extreme_energy=0.5,
            energy=0.6,
        ),
        power=PowerReading(time=9.0, power=-1.0),
        reading=SocReading(time=8.0, soc=2.9),
        pending=0.25,
    )

    assert state.to_mapping() == {
        "energy_total": 1.0,
        "soc_total": 2.0,
        "run": {
            "charging": True,
            "start_soc": 1.0,
            "extreme_soc": 3.0,
            "extreme_energy": 0.5,
            "energy": 0.6,
        },
        "power": {"time": 9.0, "power": -1.0},
        "reading": {"time": 8.0, "soc": 2.9},
        "pending": 0.25,
    }


@pytest.mark.parametrize(
    "stored",
    [
        {},
        {"energy_total": 1, "soc_total": 1, "run": None},
        {**_VALID, "energy_total": "many"},
        {**_VALID, "run": {"charging": True}},
        {**_VALID, "power": {"time": 1, "power": 1, "extra": 1}},
        {**_VALID, "reading": {"time": 1}},
        {**_VALID, "run": 5},
        {**_VALID, "pending": "soon"},
    ],
)
def test_a_malformed_stored_form_is_rejected(stored: dict[str, object]):
    with pytest.raises(LearnerStateError):
        LearnerState.from_mapping(stored)
