from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Mapping

LONGEST_GAP_SECONDS = 10 * 60
LARGEST_STEP_POINTS = 5
DIRECTION_CHANGE_POINTS = 0.1
SOC_DECIMALS = 2
SECONDS_PER_HOUR = 3600
WATTS_PER_KILOWATT = 1000
PERCENT = 100


class LearnerStateError(ValueError):
    pass


@dataclass(frozen=True)
class Poll:
    time: float
    power: float | None = None
    soc: float | None = None


@dataclass(frozen=True)
class PowerReading:
    time: float
    power: float


@dataclass(frozen=True)
class SocReading:
    time: float
    soc: float


@dataclass(frozen=True)
class Run:
    charging: bool
    start_soc: float
    extreme_soc: float
    extreme_energy: float
    energy: float


@dataclass(frozen=True)
class LearnerState:
    energy_total: float = 0.0
    soc_total: float = 0.0
    run: Run | None = None
    power: PowerReading | None = None
    reading: SocReading | None = None
    pending: float | None = 0.0

    @property
    def last_time(self) -> float | None:
        times = [item.time for item in (self.power, self.reading) if item is not None]
        return max(times, default=None)

    def to_mapping(self) -> dict[str, Any]:
        return {
            "energy_total": self.energy_total,
            "soc_total": self.soc_total,
            "run": None if self.run is None else asdict(self.run),
            "power": None if self.power is None else asdict(self.power),
            "reading": None if self.reading is None else asdict(self.reading),
            "pending": self.pending,
        }

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> LearnerState:
        try:
            run = mapping["run"]
            power = mapping["power"]
            reading = mapping["reading"]
            pending = mapping["pending"]
            return cls(
                energy_total=float(mapping["energy_total"]),
                soc_total=float(mapping["soc_total"]),
                run=None if run is None else _run_of(run),
                power=None if power is None else PowerReading(**_floats(power)),
                reading=None if reading is None else SocReading(**_floats(reading)),
                pending=None if pending is None else float(pending),
            )
        except (AttributeError, KeyError, TypeError, ValueError) as error:
            message = "The stored battery totals are malformed"
            raise LearnerStateError(message) from error


def _floats(mapping: Mapping[str, Any]) -> dict[str, float]:
    return {key: float(value) for key, value in mapping.items()}


def _run_of(mapping: Mapping[str, Any]) -> Run:
    measures = {key: value for key, value in mapping.items() if key != "charging"}
    return Run(charging=bool(mapping["charging"]), **_floats(measures))


class Learner:
    def __init__(self, *, state: LearnerState | None = None) -> None:
        self.state = LearnerState() if state is None else state

    @property
    def capacity(self) -> float | None:
        state = self.state
        energy, soc = state.energy_total, state.soc_total
        if state.run is not None and state.reading is not None:
            energy += abs(state.run.energy)
            soc += abs(state.reading.soc - state.run.start_soc)
        if energy <= 0 or soc <= 0:
            return None
        return energy / soc * PERCENT

    def observe(self, *, poll: Poll) -> None:
        state = self.state
        last_time = state.last_time
        if last_time is not None and poll.time <= last_time:
            return
        if poll.power is not None:
            state = _powered(state=state, time=poll.time, power=poll.power)
        if poll.soc is not None:
            state = _read(state=state, time=poll.time, soc=poll.soc)
        self.state = state


def _powered(*, state: LearnerState, time: float, power: float) -> LearnerState:
    previous = state.power
    current = PowerReading(time=time, power=power)
    if previous is None or state.pending is None:
        return replace(state, power=current)
    if time - previous.time > LONGEST_GAP_SECONDS:
        return replace(state, power=current, pending=None)
    energy = _pair_energy(previous=previous, current=current)
    return replace(state, power=current, pending=state.pending + energy)


def _read(*, state: LearnerState, time: float, soc: float) -> LearnerState:
    previous = state.reading
    current = SocReading(time=time, soc=soc)
    if (
        previous is None
        or state.pending is None
        or time - previous.time > LONGEST_GAP_SECONDS
        or abs(soc - previous.soc) > LARGEST_STEP_POINTS
    ):
        return replace(_banked(state=state), run=None, reading=current, pending=0.0)
    return replace(
        _stepped(state=state, previous=previous, soc=soc, energy=state.pending),
        reading=current,
        pending=0.0,
    )


def _pair_energy(*, previous: PowerReading, current: PowerReading) -> float:
    seconds = current.time - previous.time
    mean_power = (previous.power + current.power) / 2
    return mean_power / WATTS_PER_KILOWATT * seconds / SECONDS_PER_HOUR


def _banked(*, state: LearnerState) -> LearnerState:
    run = state.run
    if run is None:
        return state
    return replace(
        state,
        energy_total=state.energy_total + abs(run.extreme_energy),
        soc_total=state.soc_total + abs(run.extreme_soc - run.start_soc),
    )


def _stepped(
    *, state: LearnerState, previous: SocReading, soc: float, energy: float
) -> LearnerState:
    run = state.run
    if run is None:
        return replace(state, run=_opened(previous=previous, soc=soc, energy=energy))
    progress = soc - run.extreme_soc if run.charging else run.extreme_soc - soc
    energy_now = run.energy + energy
    if progress > 0:
        return replace(
            state,
            run=replace(
                run, extreme_soc=soc, extreme_energy=energy_now, energy=energy_now
            ),
        )
    if round(-progress, SOC_DECIMALS) >= DIRECTION_CHANGE_POINTS:
        return replace(
            _banked(state=state),
            run=Run(
                charging=not run.charging,
                start_soc=run.extreme_soc,
                extreme_soc=soc,
                extreme_energy=energy_now - run.extreme_energy,
                energy=energy_now - run.extreme_energy,
            ),
        )
    return replace(state, run=replace(run, energy=energy_now))


def _opened(*, previous: SocReading, soc: float, energy: float) -> Run | None:
    if soc == previous.soc:
        return None
    return Run(
        charging=soc > previous.soc,
        start_soc=previous.soc,
        extreme_soc=soc,
        extreme_energy=energy,
        energy=energy,
    )
