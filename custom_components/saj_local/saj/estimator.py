from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .learner import Learner, Poll

if TYPE_CHECKING:
    from collections.abc import Collection, Mapping

    from .codec import Value
    from .models import Profile

BATTERY_POWER = "battery_power"
BATTERY_SOC = "battery_soc"
BATTERY_VOLTAGE = "battery_voltage"
USABLE_CAPACITY = "battery_usable_capacity"
CHARGE_LIMIT = "battery_charge_soc_limit"
BACKUP_RESERVE = "backup_reserve_soc"
ON_GRID_LIMIT = "battery_discharge_soc_limit_on_grid"
OFF_GRID_LIMIT = "battery_discharge_soc_limit_off_grid"
APPLICATION_MODE = "application_mode"
OPERATING_MODE = "operating_mode"
BACKUP_APPLICATION_MODE = 2
OFF_GRID_OPERATING_MODE = 3
COMMON_SOURCES = (
    BATTERY_POWER,
    BATTERY_SOC,
    CHARGE_LIMIT,
    BACKUP_RESERVE,
    ON_GRID_LIMIT,
    APPLICATION_MODE,
    OPERATING_MODE,
)
SMOOTHING_SECONDS = 10 * 60
LONGEST_ESTIMATE_MINUTES = 48 * 60
MINUTES_PER_HOUR = 60
WATTS_PER_KILOWATT = 1000
PERCENT = 100
ENERGY_DECIMALS = 2


def estimate_sources(*, profile: Profile) -> tuple[str, ...]:
    return (
        *COMMON_SOURCES,
        *((USABLE_CAPACITY, BATTERY_VOLTAGE) if profile.usable_capacity else ()),
        *((OFF_GRID_LIMIT,) if profile.off_grid_discharge_limit else ()),
    )


def _number(*, values: Mapping[str, Value], key: str) -> float | None:
    value = values.get(key)
    return float(value) if isinstance(value, int | float) else None


@dataclass(frozen=True)
class BatteryReading:
    power: float | None = None
    soc: float | None = None
    voltage: float | None = None
    usable_capacity: float | None = None
    full_limit: float | None = None
    backup_reserve: float | None = None
    on_grid_limit: float | None = None
    off_grid_limit: float | None = None
    application_mode: float | None = None
    operating_mode: float | None = None
    soc_read: bool = True

    @classmethod
    def of(
        cls, *, values: Mapping[str, Value], read: Collection[str] = ()
    ) -> BatteryReading:
        return cls(
            soc_read=BATTERY_SOC in read,
            power=_number(values=values, key=BATTERY_POWER),
            soc=_number(values=values, key=BATTERY_SOC),
            voltage=_number(values=values, key=BATTERY_VOLTAGE),
            usable_capacity=_number(values=values, key=USABLE_CAPACITY),
            full_limit=_number(values=values, key=CHARGE_LIMIT),
            backup_reserve=_number(values=values, key=BACKUP_RESERVE),
            on_grid_limit=_number(values=values, key=ON_GRID_LIMIT),
            off_grid_limit=_number(values=values, key=OFF_GRID_LIMIT),
            application_mode=_number(values=values, key=APPLICATION_MODE),
            operating_mode=_number(values=values, key=OPERATING_MODE),
        )


@dataclass(frozen=True)
class Estimates:
    time_to_full: int | None = None
    time_to_empty: int | None = None
    stored_energy: float | None = None
    available_energy: float | None = None


def _minutes_until(*, remaining: float, power: float) -> int | None:
    if remaining <= 0:
        return 0
    minutes = remaining / (abs(power) / WATTS_PER_KILOWATT) * MINUTES_PER_HOUR
    if minutes > LONGEST_ESTIMATE_MINUTES:
        return None
    return round(minutes)


class BatteryEstimator:
    def __init__(self, *, profile: Profile, learner: Learner | None = None) -> None:
        self._usable_capacity = profile.usable_capacity
        self._off_grid_limit = profile.off_grid_discharge_limit
        self.learner = None if self._usable_capacity else learner or Learner()
        self._average: float | None = None
        self._averaged_at = 0.0

    def update(self, *, reading: BatteryReading, time: float) -> Estimates:
        average = self._smoothed(power=reading.power, time=time)
        energy = self._energy(reading=reading, time=time)
        soc = reading.soc
        if energy is None or soc is None:
            return Estimates()
        empty = self._empty_limit(reading=reading)
        available = (
            None if empty is None else max(0.0, (soc - empty) / PERCENT * energy)
        )
        return Estimates(
            time_to_full=_time_to_full(
                full=reading.full_limit, soc=soc, energy=energy, average=average
            ),
            time_to_empty=_time_to_empty(
                empty=empty, soc=soc, energy=energy, average=average
            ),
            stored_energy=round(soc / PERCENT * energy, ENERGY_DECIMALS),
            available_energy=None
            if available is None
            else round(available, ENERGY_DECIMALS),
        )

    def _smoothed(self, *, power: float | None, time: float) -> float | None:
        if power is None:
            return self._average
        if self._average is None:
            self._average = power
        else:
            seconds = max(0.0, time - self._averaged_at)
            weight = 1 - math.exp(-seconds / SMOOTHING_SECONDS)
            self._average += weight * (power - self._average)
        self._averaged_at = time
        return self._average

    def _energy(self, *, reading: BatteryReading, time: float) -> float | None:
        if self.learner is None:
            if reading.usable_capacity is None or reading.voltage is None:
                return None
            energy = reading.usable_capacity * reading.voltage / WATTS_PER_KILOWATT
            return energy if energy > 0 else None
        soc = reading.soc if reading.soc_read else None
        if reading.power is not None or soc is not None:
            self.learner.observe(poll=Poll(time=time, power=reading.power, soc=soc))
        return self.learner.capacity

    def _empty_limit(self, *, reading: BatteryReading) -> float | None:
        if reading.application_mode == BACKUP_APPLICATION_MODE:
            return reading.backup_reserve
        if reading.operating_mode == OFF_GRID_OPERATING_MODE and self._off_grid_limit:
            return reading.off_grid_limit
        return reading.on_grid_limit


def _time_to_full(
    *, full: float | None, soc: float, energy: float, average: float | None
) -> int | None:
    if average is None or average >= 0 or full is None:
        return None
    return _minutes_until(remaining=(full - soc) / PERCENT * energy, power=average)


def _time_to_empty(
    *, empty: float | None, soc: float, energy: float, average: float | None
) -> int | None:
    if average is None or average <= 0 or empty is None:
        return None
    return _minutes_until(remaining=(soc - empty) / PERCENT * energy, power=average)
