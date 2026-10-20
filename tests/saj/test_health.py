import pytest

from saj.catalogue import Row
from saj.health import (
    REFUSAL_THRESHOLD,
    RETEST_PERIOD,
    Break,
    ReadHealth,
    Region,
    tracked_refusals,
)


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


def _rows(*addresses: int) -> tuple[Row, ...]:
    return tuple(Row(address=address, words=1) for address in addresses)


def _regions(*groups: tuple[int, ...]) -> tuple[Region, ...]:
    return tuple(Region(rows=_rows(*group)) for group in groups)


def _refuse_request(
    health: ReadHealth, rows: tuple[Row, ...], *, now: float = 0
) -> frozenset[str]:
    keys = {f"k{row.address}" for row in rows}
    return health.record_request_refused(rows=rows, keys=keys, code=2, now=now)


@pytest.mark.parametrize(
    ("addresses", "lower", "upper"),
    [
        ((10, 11), (10,), (11,)),
        ((10, 11, 12, 13), (10, 11), (12, 13)),
        ((10, 11, 12), (10,), (11, 12)),
        ((10, 11, 30), (10, 11), (30,)),
        ((10, 40, 41, 42), (10,), (40, 41, 42)),
    ],
)
def test_a_refused_request_is_halved_at_the_row_boundary_nearest_the_middle(
    addresses: tuple[int, ...], lower: tuple[int, ...], upper: tuple[int, ...]
):
    health = ReadHealth()

    _refuse_request(health, _rows(*addresses))

    assert health.narrowing == _regions(lower, upper)


def test_the_rows_of_a_refused_request_are_unavailable_but_not_counted():
    health = ReadHealth()

    outcomes = [
        _refuse_request(health, _rows(10, 11)) for _ in range(REFUSAL_THRESHOLD)
    ]

    assert outcomes == [frozenset()] * REFUSAL_THRESHOLD
    assert health.refused() == {"k10", "k11"}
    assert health.suspended() == frozenset()
    assert health.refusals["k10"].count == 0
    assert health.refusals["k10"].code == 2


def test_a_half_that_reads_returns_to_normal_planning():
    health = ReadHealth()
    _refuse_request(health, _rows(10, 11, 12, 13))

    health.record_request_read(rows=_rows(10, 11))

    assert health.narrowing == _regions((12, 13))
    assert health.breaks == frozenset()


def test_a_half_that_is_refused_is_halved_again_until_one_row_remains():
    health = ReadHealth()
    _refuse_request(health, _rows(10, 11, 12, 13))

    _refuse_request(health, _rows(10, 11))
    _refuse_request(health, _rows(10))

    assert health.narrowing == _regions((12, 13), (11,), (10,))
    assert health.refusals["k10"].count == 1


def test_both_halves_reading_records_a_break_in_the_gap_between_them():
    health = ReadHealth()
    _refuse_request(health, _rows(10, 11, 30, 31))

    health.record_request_read(rows=_rows(10, 11))
    health.record_request_read(rows=_rows(30, 31))

    assert health.breaks == {Break(before=12, after=30)}
    assert health.narrowing == ()


def test_a_break_is_found_when_the_halves_read_in_different_cycles_and_orders():
    health = ReadHealth()
    _refuse_request(health, _rows(10, 20))

    health.record_request_read(rows=_rows(20))
    assert health.breaks == frozenset()
    health.record_request_read(rows=_rows(10))

    assert health.breaks == {Break(before=11, after=20)}


@pytest.mark.parametrize("refused_half", [(10, 11), (12, 13)])
def test_no_break_is_recorded_when_a_half_is_refused(refused_half: tuple[int, ...]):
    health = ReadHealth()
    _refuse_request(health, _rows(10, 11, 12, 13))
    other = (12, 13) if refused_half == (10, 11) else (10, 11)

    _refuse_request(health, _rows(*refused_half))
    health.record_request_read(rows=_rows(*other))

    assert health.breaks == frozenset()
    assert health.narrowing == _regions(*[(address,) for address in refused_half])


def test_a_half_read_in_part_stays_narrowed_for_the_rows_not_yet_read():
    health = ReadHealth()
    _refuse_request(health, _rows(10, 11, 12, 13))

    health.record_request_read(rows=_rows(12))

    assert health.narrowing == _regions((10, 11), (13,))


def test_reading_rows_that_are_not_narrowed_changes_nothing():
    health = ReadHealth()
    _refuse_request(health, _rows(10, 11))

    health.record_request_read(rows=_rows(50))

    assert health.narrowing == _regions((10,), (11,))


def test_a_single_row_refusal_counts_and_the_third_suspends_it():
    health = ReadHealth()

    outcomes = [
        _refuse_request(health, _rows(10)) for _ in range(REFUSAL_THRESHOLD + 1)
    ]

    assert outcomes == [frozenset()] * (REFUSAL_THRESHOLD - 1) + [
        frozenset({"k10"}),
        frozenset(),
    ]
    assert health.suspended() == {"k10"}


def test_a_suspended_row_stays_narrowed_so_nothing_is_planned_across_it():
    health = ReadHealth()
    for _ in range(REFUSAL_THRESHOLD):
        _refuse_request(health, _rows(10))

    assert health.narrowing == _regions((10,))


def test_a_row_with_several_packed_keys_counts_every_key():
    health = ReadHealth()

    suspended = frozenset().union(
        *(
            health.record_request_refused(
                rows=_rows(10), keys={"flag_a", "flag_b"}, code=2, now=0
            )
            for _ in range(REFUSAL_THRESHOLD)
        )
    )

    assert suspended == {"flag_a", "flag_b"}


def test_a_row_that_reads_again_is_no_longer_narrowed():
    health = ReadHealth()
    _refuse_request(health, _rows(10))

    health.record_request_read(rows=_rows(10))

    assert health.narrowing == ()
    assert health.breaks == frozenset()


def test_a_refusal_after_unavailable_keys_keeps_a_suspension_in_force():
    health = ReadHealth()
    for _ in range(REFUSAL_THRESHOLD):
        health.record_refusal(key="k10", code=2, now=0)

    _refuse_request(health, _rows(10, 11))

    assert health.refusals["k10"].retest_at == RETEST_PERIOD
    assert health.refusals["k10"].count == REFUSAL_THRESHOLD


def test_the_exposed_narrowing_and_breaks_are_copies():
    health = ReadHealth()
    _refuse_request(health, _rows(10, 11))

    snapshot = health.narrowing
    health.record_request_read(rows=_rows(10, 11))

    assert snapshot == _regions((10,), (11,))
    assert health.narrowing == ()


def test_a_refused_part_of_a_narrowed_half_leaves_the_other_rows_narrowed():
    health = ReadHealth()
    _refuse_request(health, _rows(10, 11, 12, 13))

    _refuse_request(health, _rows(10))
    health.record_request_read(rows=_rows(11))

    assert health.narrowing == _regions((12, 13), (10,))
    assert health.breaks == frozenset()


@pytest.mark.parametrize(
    ("tracked", "suspended", "enabled", "answered", "expected"),
    [
        (set(), set(), {"a"}, set(), set()),
        (set(), {"a"}, {"a"}, set(), {"a"}),
        ({"a"}, set(), {"a"}, set(), {"a"}),
        ({"a"}, {"a"}, {"a"}, set(), {"a"}),
        ({"a"}, set(), {"a"}, {"a"}, set()),
        ({"a", "b"}, set(), {"a"}, set(), {"a"}),
        ({"a"}, {"b"}, {"a", "b"}, {"a"}, {"b"}),
        (set(), {"a"}, set(), set(), set()),
    ],
)
def test_a_key_stays_tracked_until_it_answers_or_stops_being_read(
    tracked, suspended, enabled, answered, expected
):
    assert tracked_refusals(
        tracked=tracked, suspended=suspended, enabled=enabled, answered=answered
    ) == frozenset(expected)


@pytest.mark.parametrize(
    ("start", "end", "crossed"),
    [
        (0, 10, False),
        (5, 20, True),
        (15, 40, True),
        (5, 40, True),
        (10, 30, False),
        (12, 18, False),
        (40, 60, False),
    ],
)
def test_a_break_is_crossed_only_by_a_request_that_spans_a_side_of_it_strictly(
    start: int, end: int, *, crossed: bool
):
    gap = Break(before=10, after=30)

    assert gap.crossed_by(start=start, end=end) is crossed


def test_a_region_hull_runs_from_its_lowest_address_to_its_highest_end():
    region = Region(rows=(Row(address=30, words=2), Row(address=10, words=1)))

    assert region.hull == Break(before=10, after=32)
