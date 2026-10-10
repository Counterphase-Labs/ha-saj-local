import pytest

from saj.definitions import EMS_CONTROL_BITS, EMS_TARGET_KEYS
from saj.ems import (
    FUNCTION_BY_ENABLE_KEY,
    FUNCTIONS,
    MAX_HEARTBEAT_INTERVAL,
    MIN_HEARTBEAT_INTERVAL,
    NO_TIMEOUT,
    EmsFunction,
    EmsOwnership,
    FunctionSpec,
    check_timeout,
    switch_changes,
    timeout_check,
    timeout_inspection,
    valid_heartbeat_interval,
)
from saj.errors import EmsTimeoutError, InvalidValueError

INTERVAL = 60
INVERTER_KEYS = FUNCTIONS[EmsFunction.INVERTER].enable_keys
INVERTER_TARGET = FUNCTIONS[EmsFunction.INVERTER].target_key
BATTERY_KEY = FUNCTIONS[EmsFunction.BATTERY].enable_keys[0]
BATTERY_TARGET = FUNCTIONS[EmsFunction.BATTERY].target_key
GRID_KEY = FUNCTIONS[EmsFunction.GRID].enable_keys[0]
GRID_TARGET = FUNCTIONS[EmsFunction.GRID].target_key


def test_a_function_reports_the_bits_of_its_enable_keys_in_order():
    spec = FunctionSpec(enable_keys=tuple(EMS_CONTROL_BITS), target_key="target")

    assert spec.enable_bits == tuple(EMS_CONTROL_BITS.values())


def test_every_enable_key_belongs_to_exactly_one_function_with_a_distinct_target():
    owners = [key for spec in FUNCTIONS.values() for key in spec.enable_keys]
    targets = [spec.target_key for spec in FUNCTIONS.values()]

    assert len(owners) == len(set(owners)) == len(FUNCTION_BY_ENABLE_KEY)
    assert len(targets) == len(set(targets))
    assert set(owners) <= set(EMS_CONTROL_BITS)


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

    assert switch_changes(key=first, on=True) == {first: 1, second: 0}
    assert switch_changes(key=second, on=True) == {second: 1, first: 0}


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
    assert switch_changes(key=key, on=on) == {key: int(on)}


def test_an_installation_that_switched_nothing_on_owns_nothing_and_beats_nothing():
    ownership = EmsOwnership()

    assert ownership.owned == frozenset()
    assert ownership.owned_enable_keys == ()
    assert ownership.beat_keys() == ()


def test_the_keep_alive_targets_are_exactly_the_targets_of_the_functions():
    assert {spec.target_key for spec in FUNCTIONS.values()} == EMS_TARGET_KEYS


def test_a_function_is_owned_from_the_moment_it_is_switched_on_until_it_is_off():
    ownership = EmsOwnership()

    ownership.switched(key=BATTERY_KEY, on=True)
    assert ownership.owned == {EmsFunction.BATTERY}
    assert ownership.owned_enable_keys == (BATTERY_KEY,)

    ownership.switched(key=BATTERY_KEY, on=False)
    assert ownership.owned == frozenset()
    assert ownership.owned_enable_keys == ()


def test_the_two_forms_of_the_inverter_function_are_one_ownership():
    first, second = INVERTER_KEYS
    ownership = EmsOwnership()

    ownership.switched(key=first, on=True)
    ownership.switched(key=second, on=True)

    assert ownership.owned == {EmsFunction.INVERTER}
    assert ownership.owned_enable_keys == (second,)


def test_a_key_that_is_not_an_enable_key_changes_nothing():
    ownership = EmsOwnership()

    ownership.switched(key=BATTERY_TARGET, on=True)

    assert ownership.owned == frozenset()


def test_each_owned_function_beats_its_own_target_without_any_value_having_been_set():
    ownership = EmsOwnership()
    ownership.switched(key=BATTERY_KEY, on=True)
    assert ownership.beat_keys() == (BATTERY_TARGET,)

    ownership.switched(key=INVERTER_KEYS[0], on=True)
    ownership.switched(key=GRID_KEY, on=True)

    assert set(ownership.beat_keys()) == {
        INVERTER_TARGET,
        BATTERY_TARGET,
        GRID_TARGET,
    }


def test_switching_a_function_off_stops_its_beat():
    ownership = EmsOwnership()
    ownership.switched(key=BATTERY_KEY, on=True)
    ownership.switched(key=GRID_KEY, on=True)

    ownership.switched(key=BATTERY_KEY, on=False)

    assert ownership.beat_keys() == (GRID_TARGET,)


def test_switching_off_one_form_of_a_function_still_owned_keeps_its_beat():
    first, second = INVERTER_KEYS
    ownership = EmsOwnership()
    ownership.switched(key=first, on=True)

    ownership.switched(key=second, on=False)

    assert ownership.beat_keys() == (INVERTER_TARGET,)


def test_releasing_ends_every_ownership_and_beat():
    ownership = EmsOwnership()
    ownership.switched(key=BATTERY_KEY, on=True)
    ownership.switched(key=GRID_KEY, on=True)

    ownership.release()

    assert ownership.owned == frozenset()
    assert ownership.beat_keys() == ()


def test_a_freshly_read_off_switch_ends_only_that_ownership():
    ownership = EmsOwnership()
    ownership.switched(key=BATTERY_KEY, on=True)
    ownership.switched(key=GRID_KEY, on=True)

    ended = ownership.found_off(values={BATTERY_KEY: 0, GRID_KEY: 1})

    assert ended == {EmsFunction.BATTERY}
    assert ownership.owned == {EmsFunction.GRID}


def test_a_switch_that_was_not_read_or_reads_on_keeps_its_ownership():
    ownership = EmsOwnership()
    ownership.switched(key=BATTERY_KEY, on=True)
    ownership.switched(key=GRID_KEY, on=True)

    ended = ownership.found_off(values={GRID_KEY: 1, "other": 0})

    assert ended == frozenset()
    assert ownership.owned == {EmsFunction.BATTERY, EmsFunction.GRID}


def test_a_switch_that_is_not_owned_is_not_affected_by_reading_it_off():
    first, second = INVERTER_KEYS
    ownership = EmsOwnership()
    ownership.switched(key=first, on=True)

    ended = ownership.found_off(values={second: 0})

    assert ended == frozenset()
    assert ownership.owned == {EmsFunction.INVERTER}


def test_reading_the_owned_form_of_the_inverter_function_off_ends_it():
    first, second = INVERTER_KEYS
    ownership = EmsOwnership()
    ownership.switched(key=second, on=True)

    ended = ownership.found_off(values={first: 1, second: 0})

    assert ended == {EmsFunction.INVERTER}
    assert ownership.owned == frozenset()


def test_only_the_first_of_consecutive_dropped_beats_is_new():
    ownership = EmsOwnership()
    ownership.switched(key=BATTERY_KEY, on=True)

    assert ownership.beat_dropped(target_key=BATTERY_TARGET)
    assert not ownership.beat_dropped(target_key=BATTERY_TARGET)


def test_a_beat_that_succeeds_after_a_drop_is_a_recovery_once():
    ownership = EmsOwnership()
    ownership.switched(key=BATTERY_KEY, on=True)
    assert not ownership.beat_succeeded(target_key=BATTERY_TARGET)
    ownership.beat_dropped(target_key=BATTERY_TARGET)

    assert ownership.beat_succeeded(target_key=BATTERY_TARGET)
    assert not ownership.beat_succeeded(target_key=BATTERY_TARGET)
    assert ownership.beat_dropped(target_key=BATTERY_TARGET)


def test_functions_fail_and_recover_independently():
    ownership = EmsOwnership()
    ownership.switched(key=BATTERY_KEY, on=True)
    ownership.switched(key=GRID_KEY, on=True)

    assert ownership.beat_dropped(target_key=BATTERY_TARGET)
    assert ownership.beat_dropped(target_key=GRID_TARGET)
    assert not ownership.beat_dropped(target_key=BATTERY_TARGET)
    assert ownership.beat_succeeded(target_key=GRID_TARGET)
    assert not ownership.beat_succeeded(target_key=GRID_TARGET)
    assert not ownership.beat_dropped(target_key=BATTERY_TARGET)


def test_a_failing_state_ends_with_the_ownership_of_its_function():
    ownership = EmsOwnership()
    ownership.switched(key=BATTERY_KEY, on=True)
    ownership.switched(key=GRID_KEY, on=True)
    ownership.beat_dropped(target_key=BATTERY_TARGET)
    ownership.beat_dropped(target_key=GRID_TARGET)

    ownership.switched(key=BATTERY_KEY, on=False)
    ownership.switched(key=BATTERY_KEY, on=True)

    assert ownership.beat_dropped(target_key=BATTERY_TARGET)
    assert not ownership.beat_dropped(target_key=GRID_TARGET)


def test_a_failing_state_does_not_survive_a_release():
    ownership = EmsOwnership()
    ownership.switched(key=GRID_KEY, on=True)
    ownership.beat_dropped(target_key=GRID_TARGET)

    ownership.release()
    ownership.switched(key=GRID_KEY, on=True)

    assert ownership.beat_dropped(target_key=GRID_TARGET)
