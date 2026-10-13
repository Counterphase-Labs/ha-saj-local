import pytest

from saj.client import ClientEnvironment, ModbusTcpClient
from saj.guard import BACKOFF_CAP, EndpointGuard


@pytest.mark.parametrize(
    ("base", "expected"),
    [
        (10, [10, 20, 40, 80, 160, BACKOFF_CAP, BACKOFF_CAP]),
        (60, [60, 120, 240, BACKOFF_CAP, BACKOFF_CAP]),
        (400, [BACKOFF_CAP, BACKOFF_CAP]),
    ],
)
def test_failures_back_off_from_the_base_up_to_the_cap(
    base: float, expected: list[float]
):
    guard = EndpointGuard()

    delays = [guard.failed(now=0, base_delay=base) for _ in expected]

    assert delays == expected
    assert guard.consecutive_failures == len(expected)
    assert guard.backoff_delay == expected[-1]


def test_the_earliest_next_attempt_follows_the_latest_failure():
    guard = EndpointGuard()
    assert guard.retry_in(now=0) == 0

    guard.failed(now=100, base_delay=10)
    assert guard.retry_in(now=100) == 10
    assert guard.retry_in(now=104) == 6
    assert guard.retry_in(now=110) == 0
    assert guard.retry_in(now=500) == 0

    guard.failed(now=110, base_delay=10)
    assert guard.retry_in(now=110) == 20


def test_a_success_resets_the_count_the_delay_and_the_wait():
    guard = EndpointGuard()
    guard.failed(now=0, base_delay=10)
    guard.failed(now=10, base_delay=10)

    guard.succeeded()

    assert guard.consecutive_failures == 0
    assert guard.backoff_delay == 0
    assert guard.retry_in(now=10) == 0
    assert guard.failed(now=20, base_delay=10) == 10


async def test_a_second_client_on_the_same_guard_inherits_budget_and_failures():
    guard = EndpointGuard()
    guard.failed(now=0, base_delay=10)
    first = ClientEnvironment(budget=guard.budget)
    second = ClientEnvironment(budget=guard.budget)
    for _ in range(guard.budget.limit):
        first.budget.record(now=0)

    assert second.budget is first.budget
    assert second.budget.delay(now=1) > 0
    assert guard.consecutive_failures == 1
    assert ModbusTcpClient("h", 502, 1, environment=second) is not None


def test_each_guard_has_its_own_budget():
    one, other = EndpointGuard(), EndpointGuard()
    for _ in range(one.budget.limit):
        one.budget.record(now=0)

    assert one.budget.delay(now=1) > 0
    assert other.budget.delay(now=1) == 0


def test_each_guard_has_its_own_write_allowance():
    one, other = EndpointGuard(), EndpointGuard()
    for _ in range(one.allowance.limit):
        one.allowance.record(now=0)

    assert not one.allowance.has_room(now=1)
    assert other.allowance.has_room(now=1)


def test_the_write_allowance_survives_a_second_client_and_failures():
    guard = EndpointGuard()
    for _ in range(guard.allowance.limit - 1):
        guard.allowance.record(now=0)
    guard.failed(now=0, base_delay=10)
    guard.succeeded()

    assert guard.allowance.has_room(now=1)
    guard.allowance.record(now=1)
    assert not guard.allowance.has_room(now=2)
    assert guard.allowance.has_room(now=guard.allowance.window + 1)


def test_writes_are_counted_apart_from_the_request_budget():
    guard = EndpointGuard()
    for _ in range(guard.allowance.limit):
        guard.allowance.record(now=0)

    assert guard.budget.delay(now=1) == 0


def test_the_failing_time_runs_from_the_first_failure_of_a_run_to_a_success():
    guard = EndpointGuard()
    assert guard.failing_for(now=50) is None

    guard.failed(now=100, base_delay=10)
    guard.failed(now=130, base_delay=10)
    assert guard.failing_for(now=400) == 300

    guard.succeeded()
    assert guard.failing_for(now=400) is None

    guard.failed(now=500, base_delay=10)
    assert guard.failing_for(now=520) == 20
