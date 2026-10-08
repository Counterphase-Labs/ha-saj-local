import pytest

from saj.schedule import (
    MIN_INTERVAL,
    Cadence,
    DuplicateKeyError,
    Schedule,
    build_cadences,
)

FAST = Cadence(interval=10, keys=frozenset({"fast"}))
SLOW = Cadence(interval=60, keys=frozenset({"slow"}), default=True)
EVERYTHING = frozenset({"fast", "slow"})


def _walk(schedule: Schedule, moments: list[float]) -> dict[float, frozenset[str]]:
    served: dict[float, frozenset[str]] = {}
    for now in moments:
        due = schedule.due(now=now)
        if due:
            served[now] = due
            schedule.mark_read(now=now)
    return served


@pytest.mark.parametrize(
    ("origin", "moments", "expected_reads"),
    [
        (0, [0, 3, 9, 10, 12, 20], [0, 10, 20]),
        (100, [100, 105, 110, 111, 120], [100, 110, 120]),
        (0, [0, 7, 14, 21, 28, 35, 42], [0, 14, 21, 35, 42]),
        (50, [40, 49, 50], [50]),
    ],
)
def test_a_cadence_is_due_once_at_the_origin_and_at_each_multiple_of_its_interval(
    origin: float, moments: list[float], expected_reads: list[float]
):
    schedule = Schedule(cadences=[FAST], origin=origin)

    assert list(_walk(schedule, moments)) == expected_reads


def test_nothing_is_due_until_the_origin():
    schedule = Schedule(cadences=[FAST], origin=100)

    assert schedule.due(now=99.9) == frozenset()


def test_cadences_share_one_grid_and_coincide_on_common_multiples():
    schedule = Schedule(cadences=[FAST, SLOW], origin=0)

    served = _walk(schedule, [0, 10, 20, 30, 40, 50, 60, 70])

    assert served == {
        0: EVERYTHING,
        10: {"fast"},
        20: {"fast"},
        30: {"fast"},
        40: {"fast"},
        50: {"fast"},
        60: EVERYTHING,
        70: {"fast"},
    }


@pytest.mark.parametrize(
    ("overrun_until", "next_reads"),
    [(15, [15, 20, 30]), (35, [35, 40]), (95, [95, 100])],
)
def test_missed_ticks_are_dropped_and_the_cadence_continues_on_the_grid(
    overrun_until: float, next_reads: list[float]
):
    schedule = Schedule(cadences=[FAST], origin=0)
    schedule.mark_read(now=0)

    moments = [overrun_until, overrun_until + 1, *next_reads]
    served = _walk(schedule, sorted(set(moments)))

    assert list(served) == next_reads


@pytest.mark.parametrize(
    ("now", "enabled", "expected"),
    [
        (0, EVERYTHING, 10),
        (4, EVERYTHING, 10),
        (10, EVERYTHING, 10),
        (35, EVERYTHING, 35),
        (0, {"slow"}, 60),
        (0, {"fast"}, 10),
        (0, {"unknown"}, None),
        (0, set(), None),
    ],
)
def test_next_due_is_the_earliest_grid_time_of_a_cadence_with_enabled_keys(
    now: float, enabled: set[str], expected: float | None
):
    schedule = Schedule(cadences=[FAST, SLOW], origin=0)
    schedule.mark_read(now=0)

    assert schedule.next_due(now=now, enabled=enabled) == expected


def test_next_due_advances_with_each_read():
    schedule = Schedule(cadences=[FAST], origin=0)
    targets = []
    for now in (0, 10, 20):
        schedule.mark_read(now=now)
        targets.append(schedule.next_due(now=now, enabled={"fast"}))

    assert targets == [10, 20, 30]


def test_a_full_read_is_due_everywhere_until_it_is_served():
    schedule = Schedule(cadences=[FAST, SLOW], origin=0)
    schedule.mark_read(now=0)
    assert schedule.due(now=1) == frozenset()

    schedule.require_full_read()

    assert schedule.due(now=1) == EVERYTHING
    schedule.mark_read(now=1)
    assert schedule.due(now=2) == frozenset()


def test_a_schedule_without_cadences_has_nothing_due_and_no_wakeup():
    schedule = Schedule(cadences=[], origin=0)

    assert schedule.due(now=100) == frozenset()
    assert schedule.next_due(now=100, enabled={"fast"}) is None


@pytest.mark.parametrize(
    ("cadences", "expected"),
    [([FAST, SLOW], 10), ([SLOW], 60), ([], MIN_INTERVAL)],
)
def test_the_shortest_interval_is_the_back_off_base(
    cadences: list[Cadence], expected: int
):
    assert Schedule(cadences=cadences, origin=0).shortest_interval == expected


def test_requiring_a_full_read_after_a_failure_makes_everything_due_next():
    schedule = Schedule(cadences=[FAST, SLOW], origin=0)
    schedule.mark_read(now=0)

    schedule.require_full_read()

    assert schedule.due(now=1) == EVERYTHING


def _group(interval: int, *keys: str) -> Cadence:
    return Cadence(interval=interval, keys=frozenset(keys))


def test_without_groups_one_default_cadence_holds_every_supported_key():
    cadences = build_cadences(default_interval=60, groups=[], supported={"a", "b"})

    assert cadences == (Cadence(interval=60, keys=frozenset({"a", "b"}), default=True),)


def test_ungrouped_keys_fall_to_the_default_cadence():
    cadences = build_cadences(
        default_interval=60, groups=[_group(10, "a")], supported={"a", "b", "c"}
    )

    assert cadences == (
        Cadence(interval=60, keys=frozenset({"b", "c"}), default=True),
        Cadence(interval=10, keys=frozenset({"a"})),
    )


def test_unsupported_keys_are_dropped_from_a_group():
    cadences = build_cadences(
        default_interval=60, groups=[_group(10, "a", "gone")], supported={"a", "b"}
    )

    assert cadences[1] == Cadence(interval=10, keys=frozenset({"a"}))


def test_a_group_left_with_no_supported_keys_disappears():
    cadences = build_cadences(
        default_interval=60, groups=[_group(10, "gone")], supported={"a"}
    )

    assert cadences == (Cadence(interval=60, keys=frozenset({"a"}), default=True),)


def test_the_default_cadence_disappears_when_groups_claim_every_key():
    cadences = build_cadences(
        default_interval=60,
        groups=[_group(10, "a"), _group(30, "b")],
        supported={"a", "b"},
    )

    assert [cadence.interval for cadence in cadences] == [10, 30]
    assert not any(cadence.default for cadence in cadences)


def test_no_supported_keys_means_no_cadences():
    assert build_cadences(default_interval=60, groups=[], supported=set()) == ()


@pytest.mark.parametrize(
    ("groups", "duplicated"),
    [
        ([_group(10, "a", "b"), _group(20, "b", "c")], {"b"}),
        ([_group(10, "gone"), _group(20, "gone")], {"gone"}),
    ],
)
def test_a_key_claimed_by_two_groups_is_rejected(
    groups: list[Cadence], duplicated: set[str]
):
    with pytest.raises(DuplicateKeyError) as error:
        build_cadences(default_interval=60, groups=groups, supported={"a", "b", "c"})

    assert error.value.keys == duplicated
