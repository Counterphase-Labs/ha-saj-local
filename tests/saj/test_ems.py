from types import SimpleNamespace

import pytest

from saj.ems import (
    MAX_HEARTBEAT_INTERVAL,
    MIN_HEARTBEAT_INTERVAL,
    NO_TIMEOUT,
    EmsOwnership,
    check_timeout,
    clearing_changes,
    switch_changes,
    timeout_check,
    timeout_inspection,
    valid_heartbeat_interval,
)
from saj.errors import EmsTimeoutError, InvalidValueError
from saj.models import EnableBitMethod, PowerFunction, ems_rows

INTERVAL = 60
MAIN = "x_main"
ALTERNATE = "x_alternate"
INVERTER_KEYS = (MAIN, ALTERNATE)
INVERTER_TARGET = "x_target"
BATTERY_KEY = "y_on"
BATTERY_TARGET = "y_target"
GRID_KEY = "z_on"
GRID_TARGET = "z_target"
TIMEOUT = "x_timeout"
LIMITS = ("x_limit_a", "x_limit_b")
ROWS = ems_rows(
    profile=SimpleNamespace(
        power_control={
            PowerFunction.INVERTER: EnableBitMethod(
                enable_key=MAIN,
                alternate_keys=(ALTERNATE,),
                target_key=INVERTER_TARGET,
                timeout_key=TIMEOUT,
                limit_keys=LIMITS,
            ),
            PowerFunction.BATTERY: EnableBitMethod(
                enable_key=BATTERY_KEY, target_key=BATTERY_TARGET, limit_keys=LIMITS[:1]
            ),
            PowerFunction.GRID: EnableBitMethod(
                enable_key=GRID_KEY, target_key=GRID_TARGET
            ),
        }
    )
)
BEAT_TARGETS = {
    PowerFunction.BATTERY: BATTERY_TARGET,
    PowerFunction.GRID: GRID_TARGET,
    PowerFunction.INVERTER: INVERTER_TARGET,
}


def test_the_rows_of_a_model_come_from_its_enable_bit_statements_alone():
    assert ROWS.functions == {
        MAIN: PowerFunction.INVERTER,
        ALTERNATE: PowerFunction.INVERTER,
        BATTERY_KEY: PowerFunction.BATTERY,
        GRID_KEY: PowerFunction.GRID,
    }
    assert ROWS.targets == BEAT_TARGETS
    assert ROWS.target_functions == {
        target: function for function, target in BEAT_TARGETS.items()
    }
    assert ROWS.timeouts == {TIMEOUT}
    assert ROWS.limits == set(LIMITS)


def test_a_model_without_a_statement_or_with_another_method_has_no_ems_rows():
    rows = ems_rows(profile=SimpleNamespace(power_control={}))

    assert (rows.functions, rows.forms, rows.targets) == ({}, {}, {})
    assert (rows.timeouts, rows.limits) == (frozenset(), frozenset())


@pytest.mark.parametrize(
    ("seconds", "valid"),
    [
        (MIN_HEARTBEAT_INTERVAL - 1, False),
        (MIN_HEARTBEAT_INTERVAL, True),
        (INTERVAL, True),
        (MAX_HEARTBEAT_INTERVAL, True),
        (MAX_HEARTBEAT_INTERVAL + 1, False),
        (0, False),
    ],
)
def test_the_heartbeat_interval_is_held_to_its_limits(seconds: int, *, valid: bool):
    assert valid_heartbeat_interval(seconds=seconds) is valid


@pytest.mark.parametrize(
    ("timeout", "passes"),
    [
        (INTERVAL - 1, False),
        (INTERVAL, False),
        (INTERVAL + 1, True),
        (0, False),
        (5, False),
        (65534, True),
        (NO_TIMEOUT, True),
    ],
)
def test_the_device_timeout_must_outlast_the_heartbeat_unless_there_is_none(
    timeout: int, *, passes: bool
):
    if passes:
        check_timeout(timeout=timeout, interval=INTERVAL)
        return
    with pytest.raises(EmsTimeoutError) as caught:
        check_timeout(timeout=timeout, interval=INTERVAL)

    assert (caught.value.timeout, caught.value.interval) == (timeout, INTERVAL)


def test_the_timeout_inspection_reads_one_extra_word_and_applies_the_check():
    inspection = timeout_inspection(interval=INTERVAL)

    assert inspection.extra_words == 1
    inspection.check([INTERVAL + 1])
    with pytest.raises(EmsTimeoutError):
        inspection.check([INTERVAL])
    inspection.check([NO_TIMEOUT])


@pytest.mark.parametrize(
    ("value", "refused"),
    [
        (INTERVAL - 1, True),
        (INTERVAL, True),
        (INTERVAL - 0.4, True),
        (INTERVAL + 1, False),
        (NO_TIMEOUT, False),
    ],
)
def test_the_timeout_value_check_refuses_a_value_at_or_below_the_interval(
    value: float, *, refused: bool
):
    check = timeout_check(interval=INTERVAL)

    if refused:
        with pytest.raises(EmsTimeoutError):
            check(value)
    else:
        check(value)


@pytest.mark.parametrize("value", ["soon", None, float("nan")])
def test_the_timeout_value_check_leaves_a_non_number_to_the_value_rules(value):
    with pytest.raises(InvalidValueError):
        timeout_check(interval=INTERVAL)(value)


def test_switching_an_inverter_form_on_clears_the_other_form_in_the_same_write():
    first, second = INVERTER_KEYS

    assert switch_changes(rows=ROWS, key=first, on=True) == {first: 1, second: 0}
    assert switch_changes(rows=ROWS, key=second, on=True) == {second: 1, first: 0}


@pytest.mark.parametrize(
    ("key", "on"),
    [
        (INVERTER_KEYS[0], False),
        (BATTERY_KEY, True),
        (GRID_KEY, False),
        ("other", True),
    ],
)
def test_nothing_else_is_changed_with_a_switch(key: str, *, on: bool):
    assert switch_changes(rows=ROWS, key=key, on=on) == {key: int(on)}


@pytest.mark.parametrize(
    ("key", "cleared"),
    [
        (INVERTER_KEYS[0], set(INVERTER_KEYS)),
        (INVERTER_KEYS[1], set(INVERTER_KEYS)),
        (BATTERY_KEY, {BATTERY_KEY}),
        ("other", {"other"}),
    ],
)
def test_clearing_a_function_clears_every_form_of_it(key: str, cleared: set[str]):
    assert clearing_changes(rows=ROWS, key=key) == dict.fromkeys(cleared, 0)


def test_an_installation_that_switched_nothing_on_owns_nothing_and_beats_nothing():
    ownership = EmsOwnership()

    assert ownership.owned == frozenset()
    assert ownership.beat_keys(targets=BEAT_TARGETS) == ()


def test_a_function_is_owned_from_the_moment_it_is_acquired_until_it_is_released():
    ownership = EmsOwnership()

    ownership.acquire(function=PowerFunction.BATTERY)
    assert ownership.owned == {PowerFunction.BATTERY}

    ownership.release_function(function=PowerFunction.BATTERY)
    assert ownership.owned == frozenset()


def test_each_owned_function_with_a_target_beats_it_in_function_order():
    ownership = EmsOwnership()
    ownership.acquire(function=PowerFunction.BATTERY)
    assert ownership.beat_keys(targets=BEAT_TARGETS) == (BATTERY_TARGET,)

    ownership.acquire(function=PowerFunction.INVERTER)
    ownership.acquire(function=PowerFunction.GRID)

    assert ownership.beat_keys(targets=BEAT_TARGETS) == (
        BATTERY_TARGET,
        GRID_TARGET,
        INVERTER_TARGET,
    )


def test_an_owned_function_that_has_no_target_to_beat_is_not_beaten():
    ownership = EmsOwnership()
    ownership.acquire(function=PowerFunction.BATTERY)
    ownership.acquire(function=PowerFunction.GRID)

    assert ownership.beat_keys(targets={PowerFunction.GRID: GRID_TARGET}) == (
        GRID_TARGET,
    )


def test_releasing_a_function_stops_its_beat():
    ownership = EmsOwnership()
    ownership.acquire(function=PowerFunction.BATTERY)
    ownership.acquire(function=PowerFunction.GRID)

    ownership.release_function(function=PowerFunction.BATTERY)

    assert ownership.beat_keys(targets=BEAT_TARGETS) == (GRID_TARGET,)


def test_releasing_everything_ends_every_ownership_and_beat():
    ownership = EmsOwnership()
    ownership.acquire(function=PowerFunction.BATTERY)
    ownership.acquire(function=PowerFunction.GRID)

    ownership.release()

    assert ownership.owned == frozenset()
    assert ownership.beat_keys(targets=BEAT_TARGETS) == ()


def test_only_an_owned_function_read_not_running_is_found_off_and_ended():
    ownership = EmsOwnership()
    ownership.acquire(function=PowerFunction.BATTERY)
    ownership.acquire(function=PowerFunction.GRID)
    ownership.acquire(function=PowerFunction.INVERTER)

    ended = ownership.found_off(
        states={
            PowerFunction.BATTERY: False,
            PowerFunction.GRID: True,
            PowerFunction.INVERTER: None,
        }
    )

    assert ended == {PowerFunction.BATTERY}
    assert ownership.owned == {PowerFunction.GRID, PowerFunction.INVERTER}


def test_a_function_that_is_not_owned_is_not_affected_by_reading_it_off():
    ownership = EmsOwnership()
    ownership.acquire(function=PowerFunction.INVERTER)

    ended = ownership.found_off(states={PowerFunction.BATTERY: False})

    assert ended == frozenset()
    assert ownership.owned == {PowerFunction.INVERTER}


def test_only_the_first_of_consecutive_dropped_beats_is_new():
    ownership = EmsOwnership()
    ownership.acquire(function=PowerFunction.BATTERY)

    assert ownership.beat_dropped(function=PowerFunction.BATTERY)
    assert not ownership.beat_dropped(function=PowerFunction.BATTERY)


def test_a_beat_that_succeeds_after_a_drop_is_a_recovery_once():
    ownership = EmsOwnership()
    ownership.acquire(function=PowerFunction.BATTERY)
    assert not ownership.beat_succeeded(function=PowerFunction.BATTERY)
    ownership.beat_dropped(function=PowerFunction.BATTERY)

    assert ownership.beat_succeeded(function=PowerFunction.BATTERY)
    assert not ownership.beat_succeeded(function=PowerFunction.BATTERY)
    assert ownership.beat_dropped(function=PowerFunction.BATTERY)


def test_functions_fail_and_recover_independently():
    ownership = EmsOwnership()
    ownership.acquire(function=PowerFunction.BATTERY)
    ownership.acquire(function=PowerFunction.GRID)

    assert ownership.beat_dropped(function=PowerFunction.BATTERY)
    assert ownership.beat_dropped(function=PowerFunction.GRID)
    assert not ownership.beat_dropped(function=PowerFunction.BATTERY)
    assert ownership.beat_succeeded(function=PowerFunction.GRID)
    assert not ownership.beat_succeeded(function=PowerFunction.GRID)
    assert not ownership.beat_dropped(function=PowerFunction.BATTERY)


def test_a_failing_state_ends_with_the_ownership_of_its_function():
    ownership = EmsOwnership()
    ownership.acquire(function=PowerFunction.BATTERY)
    ownership.acquire(function=PowerFunction.GRID)
    ownership.beat_dropped(function=PowerFunction.BATTERY)
    ownership.beat_dropped(function=PowerFunction.GRID)

    ownership.release_function(function=PowerFunction.BATTERY)
    ownership.acquire(function=PowerFunction.BATTERY)

    assert ownership.beat_dropped(function=PowerFunction.BATTERY)
    assert not ownership.beat_dropped(function=PowerFunction.GRID)


def test_a_failing_state_does_not_survive_a_release():
    ownership = EmsOwnership()
    ownership.acquire(function=PowerFunction.GRID)
    ownership.beat_dropped(function=PowerFunction.GRID)

    ownership.release()
    ownership.acquire(function=PowerFunction.GRID)

    assert ownership.beat_dropped(function=PowerFunction.GRID)


def test_the_two_forms_of_a_function_are_one_ownership():
    ownership = EmsOwnership()

    ownership.acquire(function=PowerFunction.INVERTER, key=MAIN)
    ownership.acquire(function=PowerFunction.INVERTER, key=ALTERNATE)

    assert ownership.owned == {PowerFunction.INVERTER}


def test_clearing_a_form_that_is_not_the_owned_one_keeps_the_ownership_and_its_beat():
    ownership = EmsOwnership()
    ownership.acquire(function=PowerFunction.INVERTER, key=ALTERNATE)

    ownership.release_function(function=PowerFunction.INVERTER, key=MAIN)

    assert ownership.owned == {PowerFunction.INVERTER}
    assert ownership.beat_keys(targets=BEAT_TARGETS) == (INVERTER_TARGET,)


def test_clearing_the_owned_form_ends_the_ownership():
    ownership = EmsOwnership()
    ownership.acquire(function=PowerFunction.INVERTER, key=ALTERNATE)

    ownership.release_function(function=PowerFunction.INVERTER, key=ALTERNATE)

    assert ownership.owned == frozenset()


def test_reading_the_owned_function_not_running_ends_only_that_ownership():
    ownership = EmsOwnership()
    ownership.acquire(function=PowerFunction.INVERTER, key=ALTERNATE)
    ownership.acquire(function=PowerFunction.GRID, key=GRID_KEY)

    ended = ownership.found_off(
        states={PowerFunction.INVERTER: False, PowerFunction.GRID: True}
    )

    assert ended == {PowerFunction.INVERTER}
    assert ownership.owned == {PowerFunction.GRID}
