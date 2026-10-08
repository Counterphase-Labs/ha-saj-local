import pytest

from saj.budget import RequestBudget, requests_per_minute

LIMIT = 3
WINDOW = 10.0


def _budget() -> RequestBudget:
    return RequestBudget(limit=LIMIT, window=WINDOW)


def test_a_burst_up_to_the_limit_passes_without_waiting():
    budget = _budget()

    delays = []
    for _ in range(LIMIT):
        delays.append(budget.delay(now=0))
        budget.record(now=0)

    assert delays == [0] * LIMIT


@pytest.mark.parametrize(
    ("now", "expected_delay"),
    [(0, WINDOW), (4, WINDOW - 4), (9.5, 0.5), (WINDOW, 0), (WINDOW + 5, 0)],
)
def test_the_next_request_waits_exactly_until_the_oldest_leaves_the_window(
    now: float, expected_delay: float
):
    budget = _budget()
    for _ in range(LIMIT):
        budget.record(now=0)

    assert budget.delay(now=now) == expected_delay


def test_the_window_slides_so_old_requests_stop_counting_one_by_one():
    budget = _budget()
    for sent_at in (0, 4, 8):
        budget.record(now=sent_at)

    assert budget.delay(now=9) == 1
    budget.record(now=10)
    assert budget.delay(now=10) == 4
    budget.record(now=14)
    assert budget.delay(now=14) == 4


def test_waiting_then_recording_never_exceeds_the_limit_in_any_window():
    budget = _budget()
    now = 0.0
    sent: list[float] = []
    for _ in range(10):
        now += budget.delay(now=now)
        budget.record(now=now)
        sent.append(now)

    assert all(
        len([moment for moment in sent if start <= moment < start + WINDOW]) <= LIMIT
        for start in sent
    )


@pytest.mark.parametrize(
    ("requests", "expected_windows"), [(1, 1), (LIMIT, 1), (LIMIT + 1, 2), (7, 3)]
)
def test_worst_case_delay_grows_by_one_window_per_started_limit_of_requests(
    requests: int, expected_windows: int
):
    assert _budget().worst_case_delay(requests=requests) == expected_windows * WINDOW


@pytest.mark.parametrize(
    ("reads", "expected"),
    [
        ([], 0),
        ([(60, 4)], 4),
        ([(10, 1)], 6),
        ([(60, 4), (10, 1)], 10),
        ([(30, 3), (30, 3)], 12),
    ],
)
def test_steady_state_load_sums_requests_per_minute_of_every_cadence(
    reads: list[tuple[int, int]], expected: float
):
    assert requests_per_minute(reads=reads) == expected
