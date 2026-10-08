import pytest

from saj.health import REFUSAL_THRESHOLD, RETEST_PERIOD, ReadHealth


def _refuse(
    health: ReadHealth, *, key: str = "pv", count: int, now: float = 0
) -> list[bool]:
    return [health.record_refusal(key=key, code=2, now=now) for _ in range(count)]


def test_a_fresh_tracker_has_nothing_refused_or_suspended():
    health = ReadHealth()

    assert health.refused() == frozenset()
    assert health.suspended() == frozenset()
    assert health.retests_due(now=10**9) == frozenset()
    assert health.refusals == {}


def test_the_first_refusal_isolates_the_key_without_suspending_it():
    health = ReadHealth()

    suspended_now = health.record_refusal(key="pv", code=2, now=5)

    assert not suspended_now
    assert health.refused() == {"pv"}
    assert health.suspended() == frozenset()
    assert health.refusals["pv"].code == 2
    assert health.refusals["pv"].count == 1


def test_consecutive_refusals_suspend_the_key_exactly_once_at_the_threshold():
    health = ReadHealth()

    outcomes = _refuse(health, count=REFUSAL_THRESHOLD + 2)

    assert outcomes == [False] * (REFUSAL_THRESHOLD - 1) + [True, False, False]
    assert health.suspended() == {"pv"}


def test_a_success_resets_the_count_so_refusals_must_be_consecutive():
    health = ReadHealth()
    _refuse(health, count=REFUSAL_THRESHOLD - 1)

    lifted = health.record_success(key="pv")
    outcomes = _refuse(health, count=REFUSAL_THRESHOLD - 1)

    assert not lifted
    assert outcomes == [False] * (REFUSAL_THRESHOLD - 1)
    assert health.suspended() == frozenset()


def test_a_success_on_a_suspended_key_lifts_the_suspension_and_reports_it():
    health = ReadHealth()
    _refuse(health, count=REFUSAL_THRESHOLD)

    lifted = health.record_success(key="pv")

    assert lifted
    assert health.refused() == frozenset()
    assert health.suspended() == frozenset()


def test_a_success_on_an_untracked_key_changes_nothing():
    health = ReadHealth()

    assert not health.record_success(key="pv")
    assert health.refused() == frozenset()


@pytest.mark.parametrize(
    ("now", "due"),
    [
        (100, False),
        (100 + RETEST_PERIOD - 1, False),
        (100 + RETEST_PERIOD, True),
        (100 + RETEST_PERIOD * 3, True),
    ],
)
def test_a_suspended_key_is_due_for_a_retest_after_the_retest_period(
    now: float, *, due: bool
):
    health = ReadHealth()
    _refuse(health, count=REFUSAL_THRESHOLD, now=100)

    assert (health.retests_due(now=now) == {"pv"}) is due


def test_a_key_that_is_only_isolated_is_never_due_for_a_retest():
    health = ReadHealth()
    _refuse(health, count=REFUSAL_THRESHOLD - 1)

    assert health.retests_due(now=10**9) == frozenset()


def test_a_failed_retest_keeps_the_suspension_and_schedules_the_next_retest():
    health = ReadHealth()
    _refuse(health, count=REFUSAL_THRESHOLD, now=0)
    retest_time = RETEST_PERIOD

    reported_again = health.record_refusal(key="pv", code=3, now=retest_time)

    assert not reported_again
    assert health.suspended() == {"pv"}
    assert health.refusals["pv"].code == 3
    assert health.retests_due(now=retest_time) == frozenset()
    assert health.retests_due(now=retest_time + RETEST_PERIOD) == {"pv"}


def test_keys_are_tracked_independently():
    health = ReadHealth()
    _refuse(health, key="pv", count=REFUSAL_THRESHOLD)
    _refuse(health, key="grid", count=1)

    assert health.suspended() == {"pv"}
    assert health.refused() == {"pv", "grid"}


def test_the_exposed_refusals_are_a_copy():
    health = ReadHealth()
    _refuse(health, count=1)

    health.refusals.clear()

    assert health.refused() == {"pv"}
