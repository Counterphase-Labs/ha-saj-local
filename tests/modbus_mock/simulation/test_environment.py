import itertools
from datetime import UTC, datetime

import pytest

from saj_modbus_mock.simulation import environment as env

SUMMER_NOON = datetime(2026, 6, 21, 12, 0, tzinfo=UTC)
SUMMER_NIGHT = datetime(2026, 6, 21, 1, 0, tzinfo=UTC)
WINTER_NOON = datetime(2026, 12, 21, 12, 0, tzinfo=UTC)
SECOND = 1_782_000_000


def make(*, seed=1, strings=(6000, 4000), base=300, peak=6000):
    return env.Environment(
        seed=seed, string_peaks_w=strings, load_base_w=base, load_peak_w=peak
    )


def sample(*, environment, moment, second=SECOND):
    return environment.sample(moment=moment, second=second)


def test_noise_is_a_pure_function_of_seed_stream_and_bucket():
    first = env.unit_noise(seed=5, stream=1, bucket=10)

    assert env.unit_noise(seed=5, stream=1, bucket=10) == first
    assert env.unit_noise(seed=6, stream=1, bucket=10) != first
    assert env.unit_noise(seed=5, stream=2, bucket=10) != first
    assert env.unit_noise(seed=5, stream=1, bucket=11) != first
    assert 0 <= first < 1


def test_smooth_noise_interpolates_between_its_buckets_without_jumps():
    values = [
        env.smooth_noise(seed=3, stream=1, second=s, period_s=100) for s in range(300)
    ]

    assert all(0 <= value <= 1 for value in values)
    assert max(abs(a - b) for a, b in itertools.pairwise(values)) < 0.1
    assert values[0] == env.unit_noise(seed=3, stream=1, bucket=0)


def test_daylight_is_zero_at_night_and_peaks_around_noon():
    assert env.daylight_fraction(moment=SUMMER_NIGHT) == 0.0
    assert env.daylight_fraction(moment=SUMMER_NOON) == pytest.approx(1.0, abs=0.01)


def test_summer_days_are_longer_than_winter_days():
    early = datetime(2026, 6, 21, 5, 0, tzinfo=UTC)
    winter_early = datetime(2026, 12, 21, 5, 0, tzinfo=UTC)

    assert env.daylight_fraction(moment=early) > 0
    assert env.daylight_fraction(moment=winter_early) == 0.0
    assert env.daylight_fraction(moment=WINTER_NOON) > 0


def test_cloud_factor_stays_within_zero_and_one():
    factors = [env.cloud_factor(seed=2, second=SECOND + s * 37) for s in range(200)]

    assert all(0 < factor <= 1 for factor in factors)
    assert len(set(factors)) > 50


def test_string_power_scales_with_the_string_peak_and_is_zero_at_night():
    environment = make(strings=(6000, 3000))

    day = sample(environment=environment, moment=SUMMER_NOON)
    night = sample(environment=environment, moment=SUMMER_NIGHT)

    assert day.string_powers_w[0] == pytest.approx(2 * day.string_powers_w[1], rel=0.15)
    assert 0 < day.string_powers_w[0] <= 6000
    assert night.string_powers_w == (0.0, 0.0)
    assert night.external_pv_w == 0.0


def test_load_stays_between_base_and_peak():
    environment = make(base=300, peak=2000)

    loads = [
        sample(
            environment=environment, moment=SUMMER_NOON, second=SECOND + 60 * s
        ).load_w
        for s in range(0, 600, 7)
    ]

    assert all(300 <= load <= 2000 for load in loads)
    assert len(set(loads)) > 10


def test_the_same_seed_and_instant_give_the_same_sample_in_any_call_order():
    first = make(seed=11)
    second = make(seed=11)
    sample(environment=first, moment=SUMMER_NOON, second=SECOND + 500)

    assert sample(environment=first, moment=SUMMER_NOON) == sample(
        environment=second, moment=SUMMER_NOON
    )


def test_a_different_seed_gives_a_different_sample():
    assert sample(environment=make(seed=1), moment=SUMMER_NOON) != sample(
        environment=make(seed=2), moment=SUMMER_NOON
    )


def test_grid_voltage_and_frequency_stay_near_nominal_and_differ_per_phase():
    volts = [
        env.grid_voltage_v(seed=1, second=SECOND + s, phase=0)
        for s in range(0, 2000, 13)
    ]

    assert all(225 < v < 235 for v in volts)
    assert env.grid_voltage_v(seed=1, second=SECOND, phase=0) != env.grid_voltage_v(
        seed=1,
        second=SECOND,
        phase=1,
    )
    assert 49.9 < env.grid_frequency_hz(seed=1, second=SECOND) < 50.1


def test_phase_weights_sum_to_one_with_a_small_imbalance():
    weights = env.phase_weights(seed=4, phases=3)

    assert sum(weights) == pytest.approx(1.0)
    assert len(set(weights)) == 3
    assert all(0.3 < weight < 0.37 for weight in weights)
    assert env.phase_weights(seed=4, phases=1) == (1.0,)
