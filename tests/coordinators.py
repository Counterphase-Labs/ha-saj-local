from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import TYPE_CHECKING

from custom_components.saj_local.coordinator import (
    SajCoordinator,
    WriteStatistics,
)
from custom_components.saj_local.saj.codec import Range
from custom_components.saj_local.saj.control import Write, WriteResult
from custom_components.saj_local.saj.ems import EmsOwnership
from custom_components.saj_local.saj.models import (
    EnableBitMethod,
    PowerFunction,
    ems_rows,
)
from custom_components.saj_local.saj.poller import CycleFailedError, CycleResult
from custom_components.saj_local.saj.power_control import Start
from custom_components.saj_local.saj.telemetry import Telemetry

if TYPE_CHECKING:
    from collections.abc import Mapping

NOW = 100.4
WAKEUP = NOW + 30
INTERVAL = 60
READ_KEYS = {"backup_reserve_soc", "backup_reserve_soc_active"}
POWER_RANGE = Range(minimum=-1000, maximum=1000)
ENABLE_KEYS = {
    PowerFunction.BATTERY: "ems_battery_control",
    PowerFunction.GRID: "ems_grid_control",
    PowerFunction.INVERTER: "ems_inverter_control_with_timeout_exit",
}
TARGET_KEYS = {
    PowerFunction.BATTERY: "ems_battery_power_target",
    PowerFunction.GRID: "ems_grid_power_target",
    PowerFunction.INVERTER: "ems_inverter_power_target",
}
ALTERNATE_KEYS = {PowerFunction.INVERTER: ("ems_inverter_control",)}
TIMEOUT_KEY = "ems_timeout"
LIMIT_KEYS = ("ems_pv_power_limit",)
MODE_KEY = "application_mode"
DIRECTION_KEY = "passive_mode"
PASSIVE = 3
STANDBY = 0
CHARGING = 2


class FakeControl:
    def __init__(self) -> None:
        self.calls: list[dict] = []
        self.switch_offs: list[Write] = []
        self.outcomes: list = []
        self.switch_off_outcomes: list = []
        self.keep_alives: list[str] = []
        self.keep_alive_outcomes: list = []
        self.settings_read: list[str] = []
        self.states_read: list[frozenset[str]] = []
        self.state_outcomes: list = []
        self.setting_outcomes: list = []
        self.admission: BaseException | None = None
        self.limit_reads = 0
        self.limit_outcomes: list = []
        self.hold: asyncio.Event | None = None
        self.entered = asyncio.Event()

    async def write(self, *, key, value, also=None, inspection=None, check=None):
        self.calls.append(
            {
                "key": key,
                "value": value,
                "also": also,
                "inspection": inspection,
                "check": check,
            }
        )
        self.entered.set()
        if self.hold is not None:
            await self.hold.wait()
        return self._outcome(self.outcomes)

    async def keep_alive_read_ems(self, *, key):
        self.keep_alives.append(key)
        outcome = self.keep_alive_outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome

    async def read_setting(self, *, key):
        self.settings_read.append(key)
        outcome = self.setting_outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome

    async def read_states(self, *, keys):
        self.states_read.append(frozenset(keys))
        outcome = self.state_outcomes.pop(0) if self.state_outcomes else {}
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome

    def require_admitted(self):
        if self.admission is not None:
            raise self.admission

    async def read_ems_limits(self):
        self.limit_reads += 1
        if not self.limit_outcomes:
            return {}
        outcome = self.limit_outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome

    async def switch_off(self, *, write):
        self.switch_offs.append(write)
        self.entered.set()
        if self.hold is not None:
            await self.hold.wait()
        return self._outcome(self.switch_off_outcomes or self.outcomes)

    @staticmethod
    def _outcome(outcomes):
        outcome = outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


class FakePoller:
    def __init__(self) -> None:
        self.link_failures = 0
        self.behaviour = None
        self.outcomes = []

    async def link_failed(self) -> float:
        self.link_failures += 1
        return WAKEUP

    async def run(self, *, enabled):
        del enabled
        if self.outcomes:
            outcome = self.outcomes.pop(0)
            if isinstance(outcome, BaseException):
                raise outcome
            return outcome
        return await self.behaviour()


class FakeStore:
    def __init__(self, stored=None) -> None:
        self.stored = stored
        self.saved: list[dict] = []

    async def async_load(self):
        return self.stored

    async def async_save(self, data) -> None:
        self.saved.append(data)


class FakeFunctionControl:
    method_name = "fake"

    def __init__(
        self,
        function: PowerFunction,
        *,
        prior_key: str | None = None,
        remember: int | None = None,
        two_step_stop: bool = False,
        names: RowNames | None = None,
    ) -> None:
        names = names or RowNames()
        self.function = function
        self.enable_key = names.enables[function]
        self.forms = (self.enable_key, *names.alternates.get(function, ()))
        self.target_key = names.targets[function]
        self.prior_key = prior_key
        self.remember = remember
        self.beat_key = None if two_step_stop else self.target_key
        self.two_step_stop = two_step_stop
        self.target_range = POWER_RANGE
        self.starts: list[tuple[int, object]] = []
        self.changes: list[tuple[int, dict]] = []
        self.stops: list[int | None] = []

    @property
    def state_keys(self) -> frozenset[str]:
        return frozenset(self.forms)

    def running(self, *, values):
        forms = [values.get(key) for key in self.forms]
        if any(forms):
            return True
        return None if None in forms else False

    def held(self, *, values):
        return values.get(self.target_key)

    def usable(self, *, raw):
        return raw if isinstance(raw, int) and POWER_RANGE.contains(value=raw) else None

    def require_usable(self, *, raw):
        return int(raw)

    def start(self, *, watts, prior):
        self.starts.append((watts, prior))
        return Start(
            writes=(
                Write(key=self.target_key, value=watts),
                Write(key=self.enable_key, value=1, inspect_timeout=True),
            ),
            remember=self.remember,
        )

    def change(self, *, watts, values):
        self.changes.append((watts, dict(values)))
        return (Write(key=self.target_key, value=watts),)

    def stop(self, *, remembered):
        self.stops.append(remembered)
        if self.two_step_stop:
            return (
                Write(key=DIRECTION_KEY, value=STANDBY),
                Write(key=MODE_KEY, value=0 if remembered is None else remembered),
            )
        return (Write(key=self.enable_key, value=0),)


class Recorder:
    def __init__(self) -> None:
        self.notified: list[frozenset[str]] = []
        self.rescheduled = 0
        self.timers: list[dict] = []
        self.cancelled = 0
        self.listeners: list[dict] = []
        self.listeners_cancelled = 0
        self.tasks: list = []

    def track(self, hass, action, interval, *, name):
        self.timers.append(
            {"hass": hass, "action": action, "interval": interval, "name": name}
        )

        def cancel() -> None:
            self.cancelled += 1

        return cancel

    def listen(self, hass, entity_ids, action):
        self.listeners.append({"hass": hass, "ids": list(entity_ids), "action": action})

        def cancel() -> None:
            self.listeners_cancelled += 1

        return cancel

    def create_task(self, coroutine, name=None):
        self.tasks.append((coroutine, name))
        coroutine.close()


class FakeStates:
    def __init__(self) -> None:
        self.by_id: dict[str, SimpleNamespace] = {}

    def set(self, entity_id: str, state: str, **attributes: object) -> None:
        self.by_id[entity_id] = SimpleNamespace(state=state, attributes=attributes)

    def get(self, entity_id: str):
        return self.by_id.get(entity_id)


@dataclass(frozen=True)
class RowNames:
    timeout: str = TIMEOUT_KEY
    limits: tuple[str, ...] = LIMIT_KEYS
    enables: Mapping[PowerFunction, str] = field(default_factory=lambda: ENABLE_KEYS)
    targets: Mapping[PowerFunction, str] = field(default_factory=lambda: TARGET_KEYS)
    alternates: Mapping[PowerFunction, tuple[str, ...]] = field(
        default_factory=lambda: ALTERNATE_KEYS
    )


def statements(names: RowNames | None = None):
    names = names or RowNames()
    enables, targets, alternates = names.enables, names.targets, names.alternates
    timeout, limits = names.timeout, names.limits
    return SimpleNamespace(
        power_control={
            function: EnableBitMethod(
                enable_key=enables[function],
                target_key=targets[function],
                alternate_keys=alternates.get(function, ()),
                timeout_key=timeout,
                limit_keys=limits,
            )
            for function in PowerFunction
        }
    )


def build(recorder, *, contexts=READ_KEYS, functions=None, rows=None):
    coordinator = object.__new__(SajCoordinator)
    coordinator.hass = SimpleNamespace(
        loop=SimpleNamespace(time=lambda: NOW),
        states=FakeStates(),
        async_create_task=recorder.create_task,
    )
    coordinator.control = FakeControl()
    coordinator.poller = FakePoller()
    coordinator.ems = EmsOwnership()
    coordinator.ems_rows = rows or ems_rows(profile=statements())
    coordinator.writes = WriteStatistics()
    coordinator.heartbeat_interval = INTERVAL
    coordinator.assumed = {}
    coordinator.changed_keys = frozenset()
    coordinator.data = Telemetry(values={})
    coordinator.last_read = frozenset()
    coordinator.unavailable_keys = frozenset()
    coordinator.last_error = None
    coordinator.entry_id = "entry"
    coordinator._values = {}
    coordinator._cycle_lock = asyncio.Lock()
    coordinator._initial_refresh = False
    coordinator._update_task = None
    coordinator._stop_heartbeat = None
    coordinator.async_contexts = lambda: iter(set(contexts))
    coordinator.async_update_listeners = lambda: recorder.notified.append(
        coordinator.changed_keys
    )
    functions = functions or {
        function: FakeFunctionControl(function) for function in PowerFunction
    }
    coordinator.power_controls = functions
    coordinator.power_offered = tuple(functions)
    coordinator.power_targets = {}
    coordinator.remembered_modes = {}
    coordinator.schedules = ()
    coordinator.control_allowed = True
    coordinator.outstanding = {}
    coordinator._started = {}
    coordinator._closed = False
    coordinator._stopping = set()
    coordinator._stop_listening = None
    coordinator._stop_retry = None
    coordinator._store = FakeStore()

    def reschedule() -> None:
        recorder.rescheduled += 1

    coordinator._schedule_refresh = reschedule
    return coordinator


def hold_cycle(coordinator):
    started = asyncio.Event()
    release = asyncio.Event()

    async def behaviour():
        started.set()
        await release.wait()
        return SimpleNamespace(
            values={}, read=frozenset(), unavailable=frozenset(), next_wakeup=None
        )

    coordinator.poller.behaviour = behaviour
    return started, release


def read_result(values: Mapping[str, object], *, written=True):
    return WriteResult(values=values, assumed=False, written=written)


def sent_result(values: Mapping[str, object]):
    return WriteResult(values=values, assumed=True, written=True)


def cycle(values=None):
    return CycleResult(
        values=values or {},
        read=frozenset(values or {}),
        refused={},
        suspended=frozenset(),
        unavailable=frozenset(),
        next_wakeup=WAKEUP,
    )


def failed_cycle():
    return CycleFailedError(cause=TimeoutError(), next_wakeup=WAKEUP)
