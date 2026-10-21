"""Ready-made states for quick smoke testing, and when each one makes sense."""

import dataclasses
import enum
from typing import TYPE_CHECKING

from .simulation.faults import Equipment

if TYPE_CHECKING:
    from collections.abc import Mapping

    from .simulation.faults import FaultMap

HIGH_SPIKE_CHANCE = 0.6
LARGE_SPIKE_SIZE = 0.6
LONG_SPIKE_DURATION_S = 240
EV_PRESET_ENERGY_WH = 20_000
EV_STANDARD_MODE = 1
SLOW_LATENCY_MS = 800
SLOW_JITTER_MS = 400
FLAKY_NO_ANSWER_PERCENT = 5
FLAKY_DROPPED_PERCENT = 2
BUSY_PERCENT = 10
ALWAYS_PERCENT = 100
LOCKOUT_REQUESTS = 120
LOCKOUT_WINDOW_S = 60


class Needs(enum.Enum):
    """The equipment a preset is about."""

    NOTHING = enum.auto()
    BATTERY = enum.auto()
    METER_A = enum.auto()
    METER_B = enum.auto()
    EV_CHARGER = enum.auto()


@dataclasses.dataclass(frozen=True, slots=True)
class Fitted:
    battery: bool
    meter_a: bool
    meter_b: bool
    ev_charger: bool

    def has(self, *, needs: Needs) -> bool:
        return {
            Needs.NOTHING: True,
            Needs.BATTERY: self.battery,
            Needs.METER_A: self.meter_a,
            Needs.METER_B: self.meter_b,
            Needs.EV_CHARGER: self.ev_charger,
        }[needs]


@dataclasses.dataclass(frozen=True, slots=True)
class Preset:
    """Changes applied after a reset to the scenario.

    Faults are named, not numbered: the model's fault map says which bits report
    each condition, and a model whose map lacks the name does not offer the preset.
    """

    key: str
    name: str
    description: str
    needs: Needs = Needs.NOTHING
    variation: Mapping[str, float] = dataclasses.field(default_factory=dict)
    settings: Mapping[str, int] = dataclasses.field(default_factory=dict)
    faults: tuple[tuple[Equipment, str], ...] = ()
    packs: Mapping[str, Mapping[str, int]] = dataclasses.field(default_factory=dict)
    soc_percent: float | None = None
    ev_energy_wh: int | None = None
    link: Mapping[str, object] = dataclasses.field(default_factory=dict)


PRESETS = (
    Preset(
        key="clear-sky",
        name="Clear sky",
        description="No cloud cover and no passing cloud",
        variation={"cloud_depth": 0, "passing_cloud_depth": 0},
    ),
    Preset(
        key="overcast",
        name="Overcast",
        description="30% of peak, deep cloud cover and frequent passing cloud",
        variation={
            "peak_scale_percent": 30,
            "cloud_depth": 0.9,
            "passing_cloud_depth": 0.8,
            "passing_cloud_period_s": 20,
        },
    ),
    Preset(
        key="high-load",
        name="High load",
        description="Base 1500 W, peak 9000 W and frequent large spikes",
        variation={
            "base_w": 1500,
            "peak_w": 9000,
            "spike_chance": HIGH_SPIKE_CHANCE,
            "spike_size": LARGE_SPIKE_SIZE,
            "spike_duration_s": LONG_SPIKE_DURATION_S,
        },
    ),
    Preset(
        key="low-load",
        name="Low load",
        description="Base 150 W, peak 1000 W and no spikes",
        variation={"base_w": 150, "peak_w": 1000, "spike_chance": 0},
    ),
    Preset(
        key="unstable-grid",
        name="Unstable grid",
        description="Wide voltage and frequency swing with a short period",
        variation={
            "voltage_swing_v": 20,
            "voltage_period_s": 20,
            "frequency_swing_hz": 1,
            "frequency_period_s": 15,
        },
    ),
    Preset(
        key="grid-lost",
        name="Grid lost",
        description="Grid lost fault on both bits that report it",
        faults=((Equipment.INVERTER, "Grid lost"),),
    ),
    Preset(
        key="inverter-over-temperature",
        name="Inverter over temperature",
        description="Inverter over temperature fault",
        faults=((Equipment.INVERTER, "Over temperature"),),
    ),
    Preset(
        key="battery-empty",
        name="Battery empty",
        description="State of charge 5%",
        needs=Needs.BATTERY,
        soc_percent=5,
    ),
    Preset(
        key="battery-full",
        name="Battery full",
        description="State of charge 100%",
        needs=Needs.BATTERY,
        soc_percent=100,
    ),
    Preset(
        key="battery-too-hot-to-charge",
        name="Battery too hot to charge",
        description="Battery too hot to charge fault, so charging stops",
        needs=Needs.BATTERY,
        faults=((Equipment.BATTERY, "Battery too hot to charge"),),
    ),
    Preset(
        key="battery-pack-fault",
        name="Battery pack fault",
        description="Pack 1 fault code 1",
        needs=Needs.BATTERY,
        packs={"1": {"fault": 1}},
    ),
    Preset(
        key="meter-communication-lost",
        name="Meter communication lost",
        description="Meter communication fault on both bits that report it",
        needs=Needs.METER_A,
        faults=((Equipment.INVERTER, "Meter communication lost"),),
    ),
    Preset(
        key="ev-charging",
        name="EV charging",
        description="Car plugged in needing 20 kWh, charger in standard mode",
        needs=Needs.EV_CHARGER,
        settings={"ev_mode": EV_STANDARD_MODE},
        ev_energy_wh=EV_PRESET_ENERGY_WH,
    ),
    Preset(
        key="slow-link",
        name="Slow link",
        description="Answers take 800 ms, give or take 400 ms",
        link={"latency_ms": SLOW_LATENCY_MS, "jitter_ms": SLOW_JITTER_MS},
    ),
    Preset(
        key="flaky-link",
        name="Flaky link",
        description="5% of requests get no answer and 2% lose the connection",
        link={
            "no_answer_percent": FLAKY_NO_ANSWER_PERCENT,
            "dropped_connection_percent": FLAKY_DROPPED_PERCENT,
        },
    ),
    Preset(
        key="busy-module",
        name="Busy module",
        description="10% of requests get a busy answer and a late duplicate",
        link={
            "busy_percent": BUSY_PERCENT,
            "late_duplicate_percent": ALWAYS_PERCENT,
        },
    ),
    Preset(
        key="module-offline",
        name="Module offline",
        description="The module stops listening and closes every connection",
        link={"offline": True},
    ),
    Preset(
        key="module-locked-out",
        name="Module locked out",
        description="More than 120 requests in 60 seconds lock out the whole port",
        link={
            "lockout_requests": LOCKOUT_REQUESTS,
            "lockout_window_seconds": LOCKOUT_WINDOW_S,
            "lockout_whole_port": True,
        },
    ),
)


def available_presets(*, fitted: Fitted, fault_map: FaultMap) -> tuple[Preset, ...]:
    """Presets whose equipment is fitted and whose faults the model names."""
    return tuple(
        preset
        for preset in PRESETS
        if fitted.has(needs=preset.needs)
        and all(
            fault_map.find(equipment=equipment, name=name)
            for equipment, name in preset.faults
        )
    )
