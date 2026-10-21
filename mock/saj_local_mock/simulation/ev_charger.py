import dataclasses
import enum
import math
from datetime import datetime, time, timedelta
from typing import TYPE_CHECKING

from saj_local_mock.registers import EPOCH
from saj_local_mock.scenario import EvSession

if TYPE_CHECKING:
    from saj_local_mock.scenario import EvChargerConfig

    from .control import Settings

SECONDS_PER_HOUR = 3_600
SECONDS_PER_DAY = 86_400
SECONDS_PER_MINUTE = 60
BYTE_BITS = 8
BYTE_MASK = 0xFF
WEEKDAY_MASK = 0x7F
SLOTS = 7
NOMINAL_VOLTAGE_V = 230.0
MIN_CURRENT_A = 6.0
MAX_CURRENT_A = 32.0
MIN_CURRENT_FUNCTION_BIT = 0b100
EMS_OFF_BIT = 0b1
MINUTES_PER_HOUR = 60
CONTROL_PILOT_IDLE_V = 12.0
CONTROL_PILOT_READY_V = 9.0
CONTROL_PILOT_CHARGING_V = 6.0
PILOT_DUTY_PERCENT_PER_A = 1 / 0.6

EV_ENABLED = "ev_enabled"
EV_MODE = "ev_mode"
EV_CHARGE_POWER = "ev_charge_power_w"
EV_FUNCTION = "ev_function"
EV_EMS_COMMAND = "ev_ems_command"
EV_EMS_CURRENT = "ev_ems_current"

MODE_DISABLED = 0
MODE_FORCED = 1
MODE_TIME_BASED = 2
MODE_PV_SURPLUS = 3
MODE_EMS = 4


def slot_key(*, index: int, part: str) -> str:
    return f"ev_slot_{index}_{part}"


class ChargerState(enum.IntEnum):
    IDLE = 1
    READY = 2
    CHARGING = 3
    CHARGER_SUSPENDED = 4
    EV_SUSPENDED = 5
    COMPLETE = 6


@dataclasses.dataclass(frozen=True, slots=True)
class ChargerReadout:
    state: ChargerState
    power_w: float
    session_energy_wh: float
    total_energy_wh: float
    session_start_s: int
    session_end_s: int
    session_seconds: int
    phases: int
    max_power_w: int


@dataclasses.dataclass(frozen=True, slots=True)
class HandState:
    """A car plugged in by hand (None for no car, 0 for one that is complete), and
    the end of a scenario window kept shut."""

    remaining_wh: int | None
    suppressed_until_s: int


def _number(*, settings: Settings, key: str) -> int:
    value = settings.get(key, 0)
    return 0 if isinstance(value, str) else int(value)


def _within(*, now: time, start: time, end: time) -> bool:
    if start <= end:
        return start <= now < end
    return now >= start or now < end


def _epoch_second(*, moment: datetime) -> int:
    return int((moment - EPOCH).total_seconds())


def _latest_occurrence(*, moment: datetime, at: time) -> int:
    """Epoch second of the most recent time of day `at` that is not after `moment`."""
    candidate = moment.replace(hour=at.hour, minute=at.minute, second=0, microsecond=0)
    if candidate > moment:
        candidate -= timedelta(days=1)
    return _epoch_second(moment=candidate)


def _slot_power_w(*, settings: Settings, moment: datetime) -> float:
    for index in range(1, SLOTS + 1):
        date = _number(settings=settings, key=slot_key(index=index, part="date"))
        if not ((date >> BYTE_BITS) & WEEKDAY_MASK) >> moment.weekday() & 1:
            continue
        start = _number(settings=settings, key=slot_key(index=index, part="start"))
        end = _number(settings=settings, key=slot_key(index=index, part="end"))
        window_start = time(hour=start >> BYTE_BITS, minute=start & BYTE_MASK)
        window_end = time(hour=end >> BYTE_BITS, minute=end & BYTE_MASK)
        in_window = window_start != window_end and _within(
            now=moment.time(),
            start=window_start,
            end=window_end,
        )
        if in_window:
            return float(
                _number(settings=settings, key=slot_key(index=index, part="power_w"))
            )
    return 0.0


class EvCharger:
    """Charging sessions. Plug state follows the clock to the second; energy only
    changes when the plant integrates a step."""

    def __init__(self, *, config: EvChargerConfig, settings: Settings) -> None:
        self._config = config
        self._settings = settings
        self._plugged = False
        self._session: EvSession | None = None
        self._manual: EvSession | None = None
        self._suppressed_until_s = 0
        self._manual_start_s = 0
        self._state = ChargerState.IDLE
        self._power_w = 0.0
        self._session_energy_wh = 0.0
        self._total_energy_wh = 0.0
        self._session_start_s = 0
        self._session_end_s = 0
        self._charging_seconds = 0

    def plug_in(self, *, energy_needed_wh: int, moment: datetime) -> None:
        """Plug a car in by hand. It stays until unplugged, complete or not."""
        plugged_at = moment.time().replace(second=0, microsecond=0)
        self._manual = EvSession(
            plug_in=plugged_at, unplug=plugged_at, energy_needed_wh=energy_needed_wh
        )
        self._manual_start_s = _epoch_second(moment=moment.replace(second=0))
        self._suppressed_until_s = 0
        self._plugged = False

    def unplug(self, *, moment: datetime) -> None:
        """End the current session; an open scenario window stays shut until it ends."""
        self._manual = None
        self._session = None
        window = self._scenario_session(moment=moment)
        if window is not None:
            self._suppressed_until_s = (
                _latest_occurrence(moment=moment, at=window.unplug) + SECONDS_PER_DAY
            )
        if self._plugged:
            self._session_end_s = _epoch_second(moment=moment)

    def hand_state(self) -> HandState:
        remaining = (
            None
            if self._manual is None
            else max(
                0, math.ceil(self._manual.energy_needed_wh - self._session_energy_wh)
            )
        )
        return HandState(
            remaining_wh=remaining, suppressed_until_s=self._suppressed_until_s
        )

    def restore_hand_state(self, *, state: HandState, moment: datetime) -> None:
        self._manual = None
        if state.remaining_wh is not None:
            self.plug_in(energy_needed_wh=state.remaining_wh, moment=moment)
        self._suppressed_until_s = state.suppressed_until_s

    def _scenario_session(self, *, moment: datetime) -> EvSession | None:
        for session in self._config.sessions:
            if _within(now=moment.time(), start=session.plug_in, end=session.unplug):
                return session
        return None

    def _active_session(self, *, moment: datetime) -> EvSession | None:
        if self._manual is not None:
            return self._manual
        if _epoch_second(moment=moment) < self._suppressed_until_s:
            return None
        return self._scenario_session(moment=moment)

    def _requested_power_w(self, *, moment: datetime, surplus_w: float) -> float:
        cap = float(self._config.max_power_w)
        mode = _number(settings=self._settings, key=EV_MODE)
        if not self._enabled():
            return 0.0
        if mode == MODE_FORCED:
            return min(
                cap, float(_number(settings=self._settings, key=EV_CHARGE_POWER))
            )
        if mode == MODE_TIME_BASED:
            return min(cap, _slot_power_w(settings=self._settings, moment=moment))
        if mode == MODE_PV_SURPLUS:
            return self._surplus_power_w(surplus_w=surplus_w)
        return self._ems_power_w()

    def _enabled(self) -> bool:
        mode = _number(settings=self._settings, key=EV_MODE)
        return bool(_number(settings=self._settings, key=EV_ENABLED)) and (
            mode != MODE_DISABLED
        )

    def _minimum_power_w(self) -> float:
        return MIN_CURRENT_A * NOMINAL_VOLTAGE_V * self._config.phases

    def _surplus_power_w(self, *, surplus_w: float) -> float:
        cap = float(self._config.max_power_w)
        if surplus_w >= self._minimum_power_w():
            return min(cap, surplus_w)
        keep_minimum = (
            _number(settings=self._settings, key=EV_FUNCTION) & MIN_CURRENT_FUNCTION_BIT
        )
        return self._minimum_power_w() if keep_minimum else 0.0

    def _ems_power_w(self) -> float:
        if _number(settings=self._settings, key=EV_EMS_COMMAND) & EMS_OFF_BIT:
            return 0.0
        current_a = float(self._settings.get(EV_EMS_CURRENT, 0))
        power = current_a * NOMINAL_VOLTAGE_V * self._config.phases
        return min(float(self._config.max_power_w), power)

    def _sync_plug(self, *, moment: datetime) -> None:
        """Apply plug-in and unplug at their scheduled seconds, idempotently."""
        session = self._active_session(moment=moment)
        if session is not None:
            started = (
                self._manual_start_s
                if session is self._manual
                else _latest_occurrence(moment=moment, at=session.plug_in)
            )
            if not self._plugged or started != self._session_start_s:
                self._session_energy_wh = 0.0
                self._charging_seconds = 0
                self._session_start_s = started
                self._session_end_s = 0
            self._session = session
        elif self._plugged and self._session is not None:
            self._session_end_s = _latest_occurrence(
                moment=moment, at=self._session.unplug
            )
        self._plugged = session is not None

    def evaluate(
        self,
        *,
        moment: datetime,
        surplus_w: float,
        step_s: float,
        stopped: bool,
    ) -> float:
        """Power the charger draws at this instant; nothing is integrated."""
        self._power_w = 0.0
        if not self._config.installed:
            return 0.0
        self._sync_plug(moment=moment)
        if not self._plugged or self._session is None:
            self._state = ChargerState.IDLE
            return 0.0
        remaining_wh = self._session.energy_needed_wh - self._session_energy_wh
        if remaining_wh <= 0:
            self._state = ChargerState.COMPLETE
            return 0.0
        if stopped:
            self._state = ChargerState.CHARGER_SUSPENDED
            return 0.0
        requested = self._requested_power_w(moment=moment, surplus_w=surplus_w)
        if requested <= 0:
            self._state = (
                ChargerState.CHARGER_SUSPENDED
                if self._enabled()
                else ChargerState.READY
            )
            return 0.0
        self._power_w = min(requested, remaining_wh * SECONDS_PER_HOUR / step_s)
        self._state = ChargerState.CHARGING
        return self._power_w

    def integrate(self, *, power_w: float, step_s: float) -> None:
        if power_w <= 0:
            return
        energy_wh = power_w * step_s / SECONDS_PER_HOUR
        self._session_energy_wh += energy_wh
        self._total_energy_wh += energy_wh
        self._charging_seconds += int(step_s)

    def readout(self) -> ChargerReadout:
        return ChargerReadout(
            state=self._state,
            power_w=self._power_w,
            session_energy_wh=self._session_energy_wh,
            total_energy_wh=self._total_energy_wh,
            session_start_s=self._session_start_s,
            session_end_s=self._session_end_s,
            session_seconds=self._charging_seconds,
            phases=self._config.phases,
            max_power_w=self._config.max_power_w,
        )
