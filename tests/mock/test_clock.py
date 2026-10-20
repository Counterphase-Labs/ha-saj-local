from datetime import UTC, datetime, timedelta

import pytest

from saj_modbus_mock.clock import Clock

START = datetime(2026, 6, 21, 5, 0, tzinfo=UTC)


class FakeTime:
    def __init__(self, *, now=100.0):
        self.now = now

    def __call__(self):
        return self.now


@pytest.mark.parametrize(
    ("speed", "elapsed", "expected"),
    [(1, 0, 0), (1, 90, 90), (60, 5, 300), (0, 1000, 0), (0.5, 10, 5)],
)
def test_simulated_time_is_the_start_plus_speed_times_elapsed_time(
    speed, elapsed, expected
):
    time = FakeTime()
    clock = Clock(start=START, speed=speed, monotonic=time)

    time.now += elapsed

    assert clock.now() == START + timedelta(seconds=expected)


def test_setting_the_clock_moves_time_and_restarts_counting_from_there():
    time = FakeTime()
    clock = Clock(start=START, speed=1, monotonic=time)
    time.now += 50
    target = datetime(2030, 1, 1, tzinfo=UTC)

    clock.set(moment=target)
    assert clock.now() == target
    time.now += 10

    assert clock.now() == target + timedelta(seconds=10)


def test_changing_the_speed_keeps_the_time_reached_and_counts_faster_from_there():
    time = FakeTime()
    clock = Clock(start=START, speed=1, monotonic=time)
    time.now += 50

    clock.set_speed(speed=60)

    assert clock.speed == 60
    assert clock.now() == START + timedelta(seconds=50)
    time.now += 2
    assert clock.now() == START + timedelta(seconds=50 + 120)
