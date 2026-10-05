import dataclasses
import functools
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

SECONDS_PER_DAY = 86_400
SECONDS_PER_HOUR = 3_600
SECONDS_PER_MINUTE = 60
SMOOTHSTEP_LINEAR = 3
SMOOTHSTEP_CUBIC = 2
DAYLIGHT_SPAN_FACTOR = 2
GAUSS_EXPONENT = 2
SWING_SPAN_FACTOR = 2
STREAM_PHASE_STRIDE = 100
STREAM_STRING_STRIDE = 100
HOURS_PER_DAY = 24
DAYS_PER_YEAR = 365
SOLSTICE_DAY_OF_YEAR = 172
MID_DAY_HOUR = 12.0
BASE_HALF_DAY_HOURS = 6.0
HALF_DAY_SWING_HOURS = 2.0
DAYLIGHT_SHAPE = 1.2

# Noise is a pure function of its inputs, so neighbouring steps can share it.
NOISE_CACHE_ENTRIES = 1 << 16
MASK_64 = (1 << 64) - 1
MIX_SEED = 0x9E3779B97F4A7C15
MIX_STREAM = 0xD1B54A32D192ED03
MIX_BUCKET = 0xAEF17502108EF2D9
MIX_ROUND_ONE = 0xBF58476D1CE4E5B9
MIX_ROUND_TWO = 0x94D049BB133111EB
MIX_SHIFT_ONE = 30
MIX_SHIFT_TWO = 27
MIX_SHIFT_THREE = 31
UNIT_DIVISOR = float(1 << 53)
UNIT_SHIFT = 11

STREAM_CLOUD_SLOW = 1
STREAM_CLOUD_FAST = 2
STREAM_STRING_JITTER = 3
STREAM_LOAD_SLOW = 4
STREAM_LOAD_SPIKE = 5
STREAM_EXTERNAL_PV = 6
STREAM_VOLTAGE = 7
STREAM_FREQUENCY = 8
STREAM_PHASE_WEIGHT = 9

CLOUD_SLOW_PERIOD_S = 3_600
CLOUD_FAST_PERIOD_S = 90
CLOUD_SLOW_DEPTH = 0.35
CLOUD_FAST_DEPTH = 0.5
CLOUD_FAST_EXPONENT = 3
STRING_JITTER_PERIOD_S = 45
STRING_JITTER_DEPTH = 0.06

LOAD_SLOW_PERIOD_S = 600
LOAD_SLOW_DEPTH = 0.08
LOAD_SPIKE_BUCKET_S = 300
LOAD_SPIKE_DURATION_S = 120
LOAD_SPIKE_CHANCE = 0.1
LOAD_SPIKE_SHARE = 0.3
MORNING_PEAK_HOUR = 7.5
MORNING_WIDTH_H = 1.0
MORNING_SHARE = 0.2
EVENING_PEAK_HOUR = 19.0
EVENING_WIDTH_H = 2.0
EVENING_SHARE = 0.6
DAYTIME_SHARE = 0.1
DAYTIME_PEAK_HOUR = 13.0
DAYTIME_WIDTH_H = 3.0

EXTERNAL_PV_PEAK_W = 3_000.0
NOMINAL_VOLTAGE_V = 230.0
VOLTAGE_SWING_V = 4.0
VOLTAGE_PERIOD_S = 300
NOMINAL_FREQUENCY_HZ = 50.0
FREQUENCY_SWING_HZ = 0.08
FREQUENCY_PERIOD_S = 120
PHASE_IMBALANCE = 0.2
CENTRE = 0.5


def mix(*, seed: int, stream: int, bucket: int) -> int:
    value = (
        seed * MIX_SEED + stream * MIX_STREAM + bucket * MIX_BUCKET + MIX_SEED
    ) & MASK_64
    value = ((value ^ (value >> MIX_SHIFT_ONE)) * MIX_ROUND_ONE) & MASK_64
    value = ((value ^ (value >> MIX_SHIFT_TWO)) * MIX_ROUND_TWO) & MASK_64
    return value ^ (value >> MIX_SHIFT_THREE)


@functools.lru_cache(maxsize=NOISE_CACHE_ENTRIES)
def _cached_noise(*, seed: int, stream: int, bucket: int) -> float:
    return (mix(seed=seed, stream=stream, bucket=bucket) >> UNIT_SHIFT) / UNIT_DIVISOR


def unit_noise(*, seed: int, stream: int, bucket: int) -> float:
    return _cached_noise(seed=seed, stream=stream, bucket=bucket)


def smooth_noise(*, seed: int, stream: int, second: int, period_s: int) -> float:
    bucket, offset = divmod(second, period_s)
    fraction = offset / period_s
    eased = fraction * fraction * (SMOOTHSTEP_LINEAR - SMOOTHSTEP_CUBIC * fraction)
    low = unit_noise(seed=seed, stream=stream, bucket=bucket)
    high = unit_noise(seed=seed, stream=stream, bucket=bucket + 1)
    return low + (high - low) * eased


def seconds_of_day(*, moment: datetime) -> int:
    return (
        moment.hour * SECONDS_PER_HOUR
        + moment.minute * SECONDS_PER_MINUTE
        + moment.second
    )


def daylight_fraction(*, moment: datetime) -> float:
    swing = math.cos(
        2
        * math.pi
        * (moment.timetuple().tm_yday - SOLSTICE_DAY_OF_YEAR)
        / DAYS_PER_YEAR,
    )
    half_day = BASE_HALF_DAY_HOURS + HALF_DAY_SWING_HOURS * swing
    hour = seconds_of_day(moment=moment) / SECONDS_PER_HOUR
    position = (hour - (MID_DAY_HOUR - half_day)) / (DAYLIGHT_SPAN_FACTOR * half_day)
    if not 0 < position < 1:
        return 0.0
    return math.sin(math.pi * position) ** DAYLIGHT_SHAPE


def cloud_factor(*, seed: int, second: int) -> float:
    slow = smooth_noise(
        seed=seed,
        stream=STREAM_CLOUD_SLOW,
        second=second,
        period_s=CLOUD_SLOW_PERIOD_S,
    )
    fast = smooth_noise(
        seed=seed,
        stream=STREAM_CLOUD_FAST,
        second=second,
        period_s=CLOUD_FAST_PERIOD_S,
    )
    return (1 - CLOUD_SLOW_DEPTH * slow) * (
        1 - CLOUD_FAST_DEPTH * fast**CLOUD_FAST_EXPONENT
    )


def _gauss(*, hour: float, centre: float, width: float) -> float:
    return math.exp(-(((hour - centre) / width) ** GAUSS_EXPONENT))


def household_load_w(
    *, seed: int, moment: datetime, second: int, base_w: float, peak_w: float
) -> float:
    hour = seconds_of_day(moment=moment) / SECONDS_PER_HOUR
    span = peak_w - base_w
    shape = (
        MORNING_SHARE
        * _gauss(hour=hour, centre=MORNING_PEAK_HOUR, width=MORNING_WIDTH_H)
        + EVENING_SHARE
        * _gauss(hour=hour, centre=EVENING_PEAK_HOUR, width=EVENING_WIDTH_H)
        + DAYTIME_SHARE
        * _gauss(hour=hour, centre=DAYTIME_PEAK_HOUR, width=DAYTIME_WIDTH_H)
    )
    drift = LOAD_SLOW_DEPTH * smooth_noise(
        seed=seed,
        stream=STREAM_LOAD_SLOW,
        second=second,
        period_s=LOAD_SLOW_PERIOD_S,
    )
    bucket, offset = divmod(second, LOAD_SPIKE_BUCKET_S)
    spike_draw = unit_noise(seed=seed, stream=STREAM_LOAD_SPIKE, bucket=bucket)
    spiking = spike_draw < LOAD_SPIKE_CHANCE and offset < LOAD_SPIKE_DURATION_S
    spike = LOAD_SPIKE_SHARE if spiking else 0.0
    return min(peak_w, base_w + span * (shape + drift + spike))


def grid_voltage_v(*, seed: int, second: int, phase: int) -> float:
    swing = smooth_noise(
        seed=seed,
        stream=STREAM_VOLTAGE + phase * STREAM_PHASE_STRIDE,
        second=second,
        period_s=VOLTAGE_PERIOD_S,
    )
    return NOMINAL_VOLTAGE_V + (swing - CENTRE) * SWING_SPAN_FACTOR * VOLTAGE_SWING_V


def grid_frequency_hz(*, seed: int, second: int) -> float:
    swing = smooth_noise(
        seed=seed,
        stream=STREAM_FREQUENCY,
        second=second,
        period_s=FREQUENCY_PERIOD_S,
    )
    return (
        NOMINAL_FREQUENCY_HZ + (swing - CENTRE) * SWING_SPAN_FACTOR * FREQUENCY_SWING_HZ
    )


def phase_weights(*, seed: int, phases: int) -> tuple[float, ...]:
    raw = [
        1
        + (unit_noise(seed=seed, stream=STREAM_PHASE_WEIGHT, bucket=index) - CENTRE)
        * PHASE_IMBALANCE
        for index in range(phases)
    ]
    total = sum(raw)
    return tuple(value / total for value in raw)


@dataclasses.dataclass(frozen=True, slots=True)
class EnvironmentSample:
    string_powers_w: tuple[float, ...]
    load_w: float
    external_pv_w: float


class Environment:
    """PV and household demand as pure functions of the seed and the instant."""

    def __init__(
        self,
        *,
        seed: int,
        string_peaks_w: tuple[int, ...],
        load_base_w: int,
        load_peak_w: int,
    ) -> None:
        self._seed = seed
        self._string_peaks_w = string_peaks_w
        self._load_base_w = load_base_w
        self._load_peak_w = load_peak_w

    def _string_power(self, *, index: int, second: int, sky: float) -> float:
        jitter = smooth_noise(
            seed=self._seed,
            stream=STREAM_STRING_JITTER + index * STREAM_STRING_STRIDE,
            second=second,
            period_s=STRING_JITTER_PERIOD_S,
        )
        factor = 1 - STRING_JITTER_DEPTH * jitter
        return self._string_peaks_w[index] * sky * factor

    def sample(self, *, moment: datetime, second: int) -> EnvironmentSample:
        daylight = daylight_fraction(moment=moment)
        sky = daylight * cloud_factor(seed=self._seed, second=second)
        strings = tuple(
            self._string_power(index=index, second=second, sky=sky)
            for index in range(len(self._string_peaks_w))
        )
        external_noise = unit_noise(
            seed=self._seed,
            stream=STREAM_EXTERNAL_PV,
            bucket=second // CLOUD_FAST_PERIOD_S,
        )
        return EnvironmentSample(
            string_powers_w=strings,
            load_w=household_load_w(
                seed=self._seed,
                moment=moment,
                second=second,
                base_w=self._load_base_w,
                peak_w=self._load_peak_w,
            ),
            external_pv_w=EXTERNAL_PV_PEAK_W
            * sky
            * (1 - STRING_JITTER_DEPTH * external_noise),
        )
