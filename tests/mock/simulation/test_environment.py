import dataclasses
import itertools
from datetime import UTC, datetime

import pytest

from saj_local_mock.simulation import environment as env

SUMMER_NOON = datetime(2026, 6, 21, 12, 0, tzinfo=UTC)
SUMMER_NIGHT = datetime(2026, 6, 21, 1, 0, tzinfo=UTC)
WINTER_NOON = datetime(2026, 12, 21, 12, 0, tzinfo=UTC)
SECOND = 1_782_000_000


def make(*, seed=1, strings=(6000, 4000), base=300, peak=6000, **shape):
    return env.Environment(
        seed=seed,
        string_peaks_w=strings,
        load=env.LoadConfig(base_w=base, peak_w=peak),
        variation=env.Variation(**shape),
    )


DEFAULTS = env.Variation()


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
    factors = [
        env.cloud_factor(seed=2, second=SECOND + s * 37, variation=DEFAULTS)
        for s in range(200)
    ]

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
        env.grid_voltage_v(seed=1, second=SECOND + s, phase=0, variation=DEFAULTS)
        for s in range(0, 2000, 13)
    ]

    assert all(225 < v < 235 for v in volts)
    assert env.grid_voltage_v(
        seed=1, second=SECOND, phase=0, variation=DEFAULTS
    ) != env.grid_voltage_v(seed=1, second=SECOND, phase=1, variation=DEFAULTS)
    assert (
        49.9 < env.grid_frequency_hz(seed=1, second=SECOND, variation=DEFAULTS) < 50.1
    )


def test_phase_weights_sum_to_one_with_a_small_imbalance():
    weights = env.phase_weights(seed=4, phases=3, variation=DEFAULTS)

    assert sum(weights) == pytest.approx(1.0)
    assert len(set(weights)) == 3
    assert all(0.3 < weight < 0.37 for weight in weights)
    assert env.phase_weights(seed=4, phases=1, variation=DEFAULTS) == (1.0,)


def steepest_step(*, series):
    return max(abs(after - before) for before, after in itertools.pairwise(series))


def test_the_defaults_reproduce_the_baseline_formulas():
    seed, second = 3, SECOND + 1234
    slow = env.smooth_noise(seed=seed, stream=1, second=second, period_s=3600)
    fast = env.smooth_noise(seed=seed, stream=2, second=second, period_s=90)
    voltage = env.smooth_noise(seed=seed, stream=7, second=second, period_s=300)
    frequency = env.smooth_noise(seed=seed, stream=8, second=second, period_s=120)

    assert env.cloud_factor(
        seed=seed, second=second, variation=DEFAULTS
    ) == pytest.approx((1 - 0.35 * slow) * (1 - 0.5 * fast**3))
    assert env.grid_voltage_v(
        seed=seed, second=second, phase=0, variation=DEFAULTS
    ) == pytest.approx(230 + (voltage - 0.5) * 2 * 4)
    assert env.grid_frequency_hz(
        seed=seed, second=second, variation=DEFAULTS
    ) == pytest.approx(50 + (frequency - 0.5) * 2 * 0.08)


@pytest.mark.parametrize("scale", [0, 50, 200])
def test_the_peak_scale_is_a_percentage_of_the_configured_string_peaks(scale):
    reference = sample(environment=make(), moment=SUMMER_NOON).string_powers_w
    scaled = sample(
        environment=make(peak_scale_percent=scale), moment=SUMMER_NOON
    ).string_powers_w

    assert scaled == pytest.approx(tuple(power * scale / 100 for power in reference))


@pytest.mark.parametrize(
    ("shape", "low", "high"),
    [
        ({"cloud_depth": 0, "passing_cloud_depth": 0}, 1.0, 1.0),
        ({"cloud_depth": 1, "passing_cloud_depth": 0}, 0.0, 1.0),
        ({"cloud_depth": 0, "passing_cloud_depth": 1}, 0.0, 1.0),
    ],
)
def test_cloud_depths_set_how_much_cloud_can_take_off(shape, low, high):
    factors = [
        env.cloud_factor(
            seed=2, second=SECOND + s * 41, variation=env.Variation(**shape)
        )
        for s in range(300)
    ]

    assert low <= min(factors)
    assert max(factors) <= high
    assert (min(factors) < max(factors)) is (
        shape != {"cloud_depth": 0, "passing_cloud_depth": 0}
    )


def read_cloud(*, variation, second):
    return env.cloud_factor(seed=5, second=second, variation=variation)


def read_voltage(*, variation, second):
    return env.grid_voltage_v(seed=5, second=second, phase=0, variation=variation)


def read_frequency(*, variation, second):
    return env.grid_frequency_hz(seed=5, second=second, variation=variation)


def read_load(*, variation, second):
    environment = env.Environment(
        seed=5,
        string_peaks_w=(1000,),
        load=env.LoadConfig(base_w=300, peak_w=6000),
        variation=variation,
    )
    return sample(environment=environment, moment=SUMMER_NOON, second=second).load_w


@pytest.mark.parametrize(
    ("period", "depths", "read"),
    [
        ("cloud_period_s", {"cloud_depth": 1, "passing_cloud_depth": 0}, read_cloud),
        (
            "passing_cloud_period_s",
            {"cloud_depth": 0, "passing_cloud_depth": 1},
            read_cloud,
        ),
        ("voltage_period_s", {"voltage_swing_v": 20}, read_voltage),
        ("frequency_period_s", {"frequency_swing_hz": 2}, read_frequency),
        ("drift_period_s", {"drift_depth": 1, "spike_chance": 0}, read_load),
    ],
)
def test_a_longer_period_changes_the_value_more_slowly(period, depths, read):
    def series(*, seconds):
        variation = env.Variation(**depths, **{period: seconds})
        return [read(variation=variation, second=SECOND + s) for s in range(0, 900, 5)]

    rapid, calm = series(seconds=20), series(seconds=800)

    assert steepest_step(series=rapid) > 3 * steepest_step(series=calm)


def test_without_jitter_every_string_follows_the_same_sky():
    day = sample(
        environment=make(strings=(6000, 3000), string_jitter_depth=0),
        moment=SUMMER_NOON,
    )

    assert day.string_powers_w[0] == pytest.approx(2 * day.string_powers_w[1])


def test_without_drift_or_spikes_the_load_ignores_the_seed():
    quiet = {"drift_depth": 0, "spike_chance": 0}

    assert sample(
        environment=make(seed=1, **quiet), moment=SUMMER_NOON
    ).load_w == pytest.approx(
        sample(environment=make(seed=99, **quiet), moment=SUMMER_NOON).load_w
    )


@pytest.mark.parametrize(
    ("changes", "second_in_bucket", "spiking"),
    [
        ({}, 10, True),
        ({"spike_chance": 0}, 10, False),
        ({}, 200, False),
        ({"spike_duration_s": 250}, 200, True),
    ],
)
def test_a_spike_adds_its_size_for_its_duration_at_the_start_of_each_bucket(
    changes, second_in_bucket, spiking
):
    quiet = {"drift_depth": 0, "spike_chance": 1.0, "spike_size": 0.2, **changes}
    reference = {**quiet, "spike_chance": 0}
    second = SECOND - SECOND % 300 + second_in_bucket
    load = {"base": 0, "peak": 100_000}

    with_spike = sample(
        environment=make(**load, **quiet), moment=SUMMER_NOON, second=second
    ).load_w
    without = sample(
        environment=make(**load, **reference), moment=SUMMER_NOON, second=second
    ).load_w

    assert (with_spike - without) == pytest.approx(20_000 if spiking else 0)


@pytest.mark.parametrize(
    ("changes", "expected"),
    [
        ({"nominal_voltage_v": 120, "voltage_swing_v": 0}, 120),
        ({"nominal_voltage_v": 230, "voltage_swing_v": 0}, 230),
    ],
)
def test_without_a_swing_the_voltage_sits_at_its_nominal(changes, expected):
    variation = env.Variation(**changes)

    voltages = {
        env.grid_voltage_v(seed=1, second=SECOND + s, phase=0, variation=variation)
        for s in range(0, 900, 50)
    }

    assert voltages == {expected}


def test_a_wider_voltage_swing_reaches_further_from_the_nominal():
    def reach(*, swing):
        variation = env.Variation(voltage_swing_v=swing)
        return max(
            abs(
                env.grid_voltage_v(
                    seed=1, second=SECOND + s, phase=0, variation=variation
                )
                - 230
            )
            for s in range(0, 3000, 11)
        )

    assert reach(swing=20) > 2 * reach(swing=4)


def test_the_frequency_follows_its_nominal_and_swing():
    variation = env.Variation(nominal_frequency_hz=60, frequency_swing_hz=0)

    assert env.grid_frequency_hz(seed=1, second=SECOND, variation=variation) == 60
    assert env.grid_frequency_hz(
        seed=1, second=SECOND, variation=env.Variation(frequency_swing_hz=2)
    ) != env.grid_frequency_hz(seed=1, second=SECOND, variation=DEFAULTS)


def test_without_imbalance_the_phases_share_equally():
    weights = env.phase_weights(
        seed=4, phases=3, variation=env.Variation(phase_imbalance=0)
    )

    assert weights == pytest.approx((1 / 3, 1 / 3, 1 / 3))


@pytest.mark.parametrize(
    ("name", "value", "expected"),
    [
        ("cloud_depth", 0.5, 0.5),
        ("cloud_depth", 1, 1.0),
        ("cloud_period_s", 600, 600),
        ("cloud_period_s", 600.0, 600),
        ("seed", 0, 0),
    ],
)
def test_a_parameter_inside_its_bounds_is_accepted_as_its_own_kind_of_number(
    name, value, expected
):
    checked = env.checked_parameter(spec=env.PARAMETERS_BY_NAME[name], value=value)

    assert checked == expected
    assert isinstance(checked, int) is env.PARAMETERS_BY_NAME[name].integer


@pytest.mark.parametrize(
    ("name", "value", "reason"),
    [
        ("cloud_depth", "high", "must be a number"),
        ("cloud_depth", True, "must be a number"),
        ("cloud_depth", None, "must be a number"),
        ("cloud_period_s", 600.5, "must be an integer"),
        ("cloud_depth", 1.5, "must be 0..1"),
        ("cloud_depth", -0.1, "must be 0..1"),
        ("nominal_voltage_v", 99, "must be 100..300"),
    ],
)
def test_a_parameter_outside_its_bounds_is_refused_with_the_reason(name, value, reason):
    with pytest.raises(env.ParameterError, match=reason):
        env.checked_parameter(spec=env.PARAMETERS_BY_NAME[name], value=value)


def test_every_variation_field_and_the_seed_can_be_tuned_and_nothing_else():
    fields = {field.name for field in dataclasses.fields(env.Variation)}
    tunable = {spec.name for spec in env.VARIATION_PARAMETERS}

    assert tunable == fields | {env.LOAD_BASE, env.LOAD_PEAK}
    assert set(env.PARAMETERS_BY_NAME) == tunable | {env.SEED}
    assert all(spec.minimum < spec.maximum for spec in env.PARAMETERS_BY_NAME.values())
