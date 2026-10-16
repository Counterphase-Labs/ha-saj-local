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

CLOUD_FAST_EXPONENT = 3
STRING_JITTER_PERIOD_S = 45
PERCENT = 100.0
SEED_MAXIMUM = 65_535

LOAD_SPIKE_BUCKET_S = 300
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
CENTRE = 0.5

GROUP_SOLAR = "Solar"
GROUP_LOAD = "Load"
GROUP_GRID = "Grid"
LOAD_BASE = "base_w"
LOAD_PEAK = "peak_w"


@dataclasses.dataclass(frozen=True, slots=True)
class LoadConfig:
    base_w: int
    peak_w: int


@dataclasses.dataclass(frozen=True, slots=True)
class ParameterSpec:
    name: str
    label: str
    group: str
    minimum: float
    maximum: float
    step: float
    unit: str
    integer: bool = False


@dataclasses.dataclass(frozen=True, slots=True)
class Variation:
    """Shape, bounds and speed of the random generators; defaults are the baseline."""

    peak_scale_percent: float = 100.0
    cloud_depth: float = 0.35
    cloud_period_s: int = 3_600
    passing_cloud_depth: float = 0.5
    passing_cloud_period_s: int = 90
    string_jitter_depth: float = 0.06
    drift_depth: float = 0.08
    drift_period_s: int = 600
    spike_chance: float = 0.1
    spike_size: float = 0.3
    spike_duration_s: int = 120
    nominal_voltage_v: float = 230.0
    voltage_swing_v: float = 4.0
    voltage_period_s: int = 300
    nominal_frequency_hz: float = 50.0
    frequency_swing_hz: float = 0.08
    frequency_period_s: int = 120
    phase_imbalance: float = 0.2


def _real(
    *,
    name: str,
    label: str,
    group: str,
    limits: tuple[float, float, float],
    unit: str = "",
) -> ParameterSpec:
    minimum, maximum, step = limits
    return ParameterSpec(
        name=name,
        label=label,
        group=group,
        minimum=minimum,
        maximum=maximum,
        step=step,
        unit=unit,
    )


def _whole(
    *,
    name: str,
    label: str,
    group: str,
    limits: tuple[int, int, int],
    unit: str,
) -> ParameterSpec:
    spec = _real(name=name, label=label, group=group, limits=limits, unit=unit)
    return dataclasses.replace(spec, integer=True)


FRACTION = (0, 1)
PERIOD_BOUNDS = (5, 3_600)
VARIATION_PARAMETERS = (
    _real(
        name="peak_scale_percent",
        label="Peak scale",
        group=GROUP_SOLAR,
        limits=(0, 200, 1),
        unit="%",
    ),
    _real(
        name="cloud_depth",
        label="Cloud cover depth",
        group=GROUP_SOLAR,
        limits=(*FRACTION, 0.01),
    ),
    _whole(
        name="cloud_period_s",
        label="Cloud cover period",
        group=GROUP_SOLAR,
        limits=(10, 14_400, 10),
        unit="s",
    ),
    _real(
        name="passing_cloud_depth",
        label="Passing cloud depth",
        group=GROUP_SOLAR,
        limits=(*FRACTION, 0.01),
    ),
    _whole(
        name="passing_cloud_period_s",
        label="Passing cloud period",
        group=GROUP_SOLAR,
        limits=(*PERIOD_BOUNDS, 5),
        unit="s",
    ),
    _real(
        name="string_jitter_depth",
        label="String jitter depth",
        group=GROUP_SOLAR,
        limits=(*FRACTION, 0.01),
    ),
    _whole(
        name=LOAD_BASE,
        label="Base load",
        group=GROUP_LOAD,
        limits=(0, 30_000, 50),
        unit="W",
    ),
    _whole(
        name=LOAD_PEAK,
        label="Peak load",
        group=GROUP_LOAD,
        limits=(0, 50_000, 100),
        unit="W",
    ),
    _real(
        name="drift_depth",
        label="Drift depth",
        group=GROUP_LOAD,
        limits=(*FRACTION, 0.01),
    ),
    _whole(
        name="drift_period_s",
        label="Drift period",
        group=GROUP_LOAD,
        limits=(10, 7_200, 10),
        unit="s",
    ),
    _real(
        name="spike_chance",
        label="Spike chance",
        group=GROUP_LOAD,
        limits=(*FRACTION, 0.01),
    ),
    _real(
        name="spike_size",
        label="Spike size",
        group=GROUP_LOAD,
        limits=(*FRACTION, 0.01),
    ),
    _whole(
        name="spike_duration_s",
        label="Spike duration",
        group=GROUP_LOAD,
        limits=(10, LOAD_SPIKE_BUCKET_S, 10),
        unit="s",
    ),
    _real(
        name="nominal_voltage_v",
        label="Nominal voltage",
        group=GROUP_GRID,
        limits=(100, 300, 1),
        unit="V",
    ),
    _real(
        name="voltage_swing_v",
        label="Voltage swing",
        group=GROUP_GRID,
        limits=(0, 50, 0.5),
        unit="V",
    ),
    _whole(
        name="voltage_period_s",
        label="Voltage period",
        group=GROUP_GRID,
        limits=(*PERIOD_BOUNDS, 5),
        unit="s",
    ),
    _real(
        name="nominal_frequency_hz",
        label="Nominal frequency",
        group=GROUP_GRID,
        limits=(45, 65, 0.1),
        unit="Hz",
    ),
    _real(
        name="frequency_swing_hz",
        label="Frequency swing",
        group=GROUP_GRID,
        limits=(0, 5, 0.01),
        unit="Hz",
    ),
    _whole(
        name="frequency_period_s",
        label="Frequency period",
        group=GROUP_GRID,
        limits=(*PERIOD_BOUNDS, 5),
        unit="s",
    ),
    _real(
        name="phase_imbalance",
        label="Phase imbalance",
        group=GROUP_GRID,
        limits=(*FRACTION, 0.01),
    ),
)
SEED = "seed"
SEED_PARAMETER = _whole(
    name=SEED, label="Seed", group="Seed", limits=(0, SEED_MAXIMUM, 1), unit=""
)
PARAMETERS_BY_NAME = {
    spec.name: spec for spec in (*VARIATION_PARAMETERS, SEED_PARAMETER)
}


class ParameterError(Exception):
    """A parameter value that is not a number inside its bounds."""


def checked_parameter(*, spec: ParameterSpec, value: object) -> float:
    """The value as a number inside the parameter's bounds, else the reason."""
    if isinstance(value, bool) or not isinstance(value, int | float):
        message = "must be a number"
        raise ParameterError(message)
    if spec.integer and value != int(value):
        message = "must be an integer"
        raise ParameterError(message)
    if not spec.minimum <= value <= spec.maximum:
        message = f"must be {spec.minimum:g}..{spec.maximum:g}"
        raise ParameterError(message)
    return int(value) if spec.integer else float(value)


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


def cloud_factor(*, seed: int, second: int, variation: Variation) -> float:
    slow = smooth_noise(
        seed=seed,
        stream=STREAM_CLOUD_SLOW,
        second=second,
        period_s=variation.cloud_period_s,
    )
    fast = smooth_noise(
        seed=seed,
        stream=STREAM_CLOUD_FAST,
        second=second,
        period_s=variation.passing_cloud_period_s,
    )
    return (1 - variation.cloud_depth * slow) * (
        1 - variation.passing_cloud_depth * fast**CLOUD_FAST_EXPONENT
    )


def _gauss(*, hour: float, centre: float, width: float) -> float:
    return math.exp(-(((hour - centre) / width) ** GAUSS_EXPONENT))


def household_load_w(
    *,
    seed: int,
    moment: datetime,
    second: int,
    load: LoadConfig,
    variation: Variation,
) -> float:
    base_w, peak_w = load.base_w, load.peak_w
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
    drift = variation.drift_depth * smooth_noise(
        seed=seed,
        stream=STREAM_LOAD_SLOW,
        second=second,
        period_s=variation.drift_period_s,
    )
    bucket, offset = divmod(second, LOAD_SPIKE_BUCKET_S)
    spike_draw = unit_noise(seed=seed, stream=STREAM_LOAD_SPIKE, bucket=bucket)
    spiking = (
        spike_draw < variation.spike_chance and offset < variation.spike_duration_s
    )
    spike = variation.spike_size if spiking else 0.0
    return min(peak_w, base_w + span * (shape + drift + spike))


def grid_voltage_v(
    *, seed: int, second: int, phase: int, variation: Variation
) -> float:
    swing = smooth_noise(
        seed=seed,
        stream=STREAM_VOLTAGE + phase * STREAM_PHASE_STRIDE,
        second=second,
        period_s=variation.voltage_period_s,
    )
    return (
        variation.nominal_voltage_v
        + (swing - CENTRE) * SWING_SPAN_FACTOR * variation.voltage_swing_v
    )


def grid_frequency_hz(*, seed: int, second: int, variation: Variation) -> float:
    swing = smooth_noise(
        seed=seed,
        stream=STREAM_FREQUENCY,
        second=second,
        period_s=variation.frequency_period_s,
    )
    return (
        variation.nominal_frequency_hz
        + (swing - CENTRE) * SWING_SPAN_FACTOR * variation.frequency_swing_hz
    )


def phase_weights(*, seed: int, phases: int, variation: Variation) -> tuple[float, ...]:
    raw = [
        1
        + (unit_noise(seed=seed, stream=STREAM_PHASE_WEIGHT, bucket=index) - CENTRE)
        * variation.phase_imbalance
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
        load: LoadConfig,
        variation: Variation,
    ) -> None:
        self._seed = seed
        self._string_peaks_w = string_peaks_w
        self._load = load
        self._variation = variation

    def _string_power(self, *, index: int, second: int, sky: float) -> float:
        variation = self._variation
        jitter = smooth_noise(
            seed=self._seed,
            stream=STREAM_STRING_JITTER + index * STREAM_STRING_STRIDE,
            second=second,
            period_s=STRING_JITTER_PERIOD_S,
        )
        factor = 1 - variation.string_jitter_depth * jitter
        peak_w = self._string_peaks_w[index] * variation.peak_scale_percent / PERCENT
        return peak_w * sky * factor

    def sample(self, *, moment: datetime, second: int) -> EnvironmentSample:
        variation = self._variation
        daylight = daylight_fraction(moment=moment)
        sky = daylight * cloud_factor(
            seed=self._seed, second=second, variation=variation
        )
        strings = tuple(
            self._string_power(index=index, second=second, sky=sky)
            for index in range(len(self._string_peaks_w))
        )
        external_noise = unit_noise(
            seed=self._seed,
            stream=STREAM_EXTERNAL_PV,
            bucket=second // variation.passing_cloud_period_s,
        )
        return EnvironmentSample(
            string_powers_w=strings,
            load_w=household_load_w(
                seed=self._seed,
                moment=moment,
                second=second,
                load=self._load,
                variation=variation,
            ),
            external_pv_w=EXTERNAL_PV_PEAK_W
            * sky
            * (1 - variation.string_jitter_depth * external_noise),
        )
