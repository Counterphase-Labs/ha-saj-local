import asyncio
import logging
import math
from contextlib import asynccontextmanager, suppress
from dataclasses import dataclass
from datetime import timedelta
from typing import TYPE_CHECKING, NoReturn

from homeassistant.core import callback
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_interval,
)
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    CONF_ALLOW_CONTROL,
    CONF_EMS_HEARTBEAT,
    CONF_MODEL,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    EMS_RELEASE_TIMEOUT,
    POWER_STORAGE_VERSION,
    SCHEDULE_ON,
    SCHEDULE_POWER_ATTRIBUTE,
    STORED_MODES,
    STORED_TARGETS,
    enabled_entity_keys,
    enabled_power_keys,
    group_cadences,
    power_schedules,
)
from .errors import (
    WRITE_ERRORS,
    WriteError,
    WriteOutcome,
    has_safe_message,
    read_back_values,
    rejection_code,
    translate_error,
    write_outcome,
)
from .issues import (
    check_unreachable,
    clear_model_issues,
    clear_unreachable,
    model_finding,
    open_refusals,
    raise_model_issue,
    sync_refusals,
)
from .saj.budget import BUDGET_PER_MINUTE
from .saj.catalogue import device_keys, device_registers, hidden_sources
from .saj.client import ModbusError, ModbusTcpClient
from .saj.definitions import Quantity
from .saj.ems import (
    DEFAULT_HEARTBEAT_INTERVAL,
    EmsOwnership,
    switch_changes,
    timeout_check,
    timeout_inspection,
)
from .saj.faults import FaultWatch
from .saj.health import ReadHealth, tracked_refusals
from .saj.models import PowerFunction, ems_rows
from .saj.poller import (
    CycleFailedError,
    CycleResult,
    IdentityChangedError,
    Poller,
    Services,
    Target,
    Tracking,
)
from .saj.power_control import (
    Action,
    ActionKind,
    Blocker,
    Situation,
    Wish,
    decide,
    power_controls,
    power_functions,
    require_none_running,
    require_target,
)
from .saj.schedule import Schedule, build_cadences
from .saj.telemetry import Telemetry

if TYPE_CHECKING:
    from collections.abc import (
        AsyncIterator,
        Awaitable,
        Callable,
        Collection,
        Mapping,
    )
    from datetime import datetime

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import Event, EventStateChangedData, HomeAssistant

    from .const import PowerSchedule
    from .saj.codec import Range, Value
    from .saj.control import Control, Inspection, Write, WriteResult
    from .saj.device import Device
    from .saj.guard import EndpointGuard
    from .saj.models import PowerMethod
    from .saj.power_control import FunctionControl

_LOGGER = logging.getLogger(__name__)
BLOCKER_MESSAGES: dict[Blocker | None, str] = {
    Blocker.NO_TARGET: "no power has been set and the schedule block has none",
    Blocker.ANOTHER_RUNNING: "another power control function is running",
    Blocker.UNUSABLE_POWER: "the schedule block's power is not a whole number in range",
}


@dataclass(frozen=True)
class LastWrite:
    key: str
    outcome: WriteOutcome
    exception_code: int | None


@dataclass
class WriteStatistics:
    acknowledged: int = 0
    rejected: int = 0
    unconfirmed: int = 0
    last: LastWrite | None = None
    beats_sent: int = 0
    beats_dropped: int = 0


def power_control_store(
    *, hass: HomeAssistant, entry_id: str
) -> Store[dict[str, dict[str, int]]]:
    return Store(hass, POWER_STORAGE_VERSION, f"{DOMAIN}.power_control.{entry_id}")


def wakeup_delay(*, target: float, now: float) -> timedelta:
    # Home Assistant schedules from the whole second of the moment it schedules,
    # so rounding the distance up from that second lands on or after the target.
    # A zero interval would mean no schedule at all, hence the one second floor.
    return timedelta(seconds=max(1, math.ceil(target - math.floor(now))))


@dataclass(frozen=True)
class Installation:
    client: ModbusTcpClient
    device: Device
    guard: EndpointGuard
    control: Control


class SajCoordinator(DataUpdateCoordinator[Telemetry]):
    def __init__(
        self,
        hass: HomeAssistant,
        installation: Installation,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(hass=hass, logger=_LOGGER, name="SAJ")
        client = installation.client
        device = installation.device
        guard = installation.guard
        self.client = client
        self.device = device
        self.guard = guard
        self.control = installation.control
        self.heartbeat_interval: int = entry.options.get(
            CONF_EMS_HEARTBEAT, DEFAULT_HEARTBEAT_INTERVAL
        )
        self.ems = EmsOwnership()
        self.ems_rows = ems_rows(profile=device.profile)
        self.power_controls = power_controls(device=device)
        self.power_offered = power_functions(fit=device.fit)
        self.power_targets: dict[PowerFunction, int] = {}
        self.remembered_modes: dict[PowerFunction, int] = {}
        self.schedules: tuple[PowerSchedule, ...] = power_schedules(entry=entry)
        self.control_allowed: bool = bool(
            entry.options.get(CONF_ALLOW_CONTROL, False) and device.detected
        )
        self.outstanding: dict[PowerFunction, str] = {}
        self._started: dict[PowerFunction, int | None] = {}
        self._stopping: set[PowerFunction] = set()
        self._closed = False
        self._stop_listening: Callable[[], None] | None = None
        self._stop_retry: Callable[[], None] | None = None
        self._store = power_control_store(hass=hass, entry_id=entry.entry_id)
        self.writes = WriteStatistics()
        self.assumed: dict[str, Value] = {}
        self.changed_keys: frozenset[str] = frozenset()
        self._stop_heartbeat: Callable[[], None] | None = None
        self.model_selection = entry.data[CONF_MODEL]
        self.entry_id = entry.entry_id
        self._entry = entry
        self._faults = FaultWatch(fault_map=device.profile.faults)
        self._packs_on: frozenset[str] = frozenset()
        self.last_error: dict[str, int | str | None] | None = None
        self.last_read: frozenset[str] = frozenset()
        self.unavailable_keys: frozenset[str] = frozenset()
        self._initial_refresh = True
        self.poller = Poller(
            target=Target(client=client, device=device, selection=self.model_selection),
            tracking=Tracking(
                schedule=Schedule(
                    cadences=build_cadences(
                        default_interval=entry.options.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                        groups=group_cadences(entry=entry),
                        supported=device_keys(fit=device.fit),
                    ),
                    origin=hass.loop.time(),
                ),
                health=ReadHealth(),
                guard=guard,
            ),
            services=Services(clock=hass.loop.time, bound=asyncio.wait_for),
            enabled=self.enabled_keys,
        )
        self._values: dict[str, Value] = {}
        self._cycle_lock = asyncio.Lock()
        self._update_task: asyncio.Task[object] | None = None
        self._log_plan()

    def _log_plan(self) -> None:
        plans = self.poller.cadence_plans()
        for plan in plans:
            _LOGGER.debug(
                "SAJ cadence every %s s reads %s as %s%s",
                plan.interval,
                sorted(plan.keys),
                [f"{address:#06x}+{count}" for address, count in plan.ranges],
                " (default)" if plan.default else "",
            )
        load = self.poller.planned_load()
        if load > BUDGET_PER_MINUTE:
            _LOGGER.warning(
                "SAJ cadences plan %.1f requests per minute, above the budget of %.0f;"
                " they will run slower than configured",
                load,
                BUDGET_PER_MINUTE,
            )

    @asynccontextmanager
    async def async_validation_session(self) -> AsyncIterator[ModbusTcpClient]:
        try:
            async with self._cycle_lock:
                try:
                    yield self.client
                finally:
                    await self.client.close()
        finally:
            self.hass.async_create_task(
                self.async_request_refresh(), name="SAJ refresh after validation"
            )

    async def _async_update_data(self) -> Telemetry:
        async with self._cycle_lock:
            self._update_task = asyncio.current_task()
            try:
                enabled = self.enabled_keys
                try:
                    result = await self.poller.run(enabled=enabled)
                except CycleFailedError as failure:
                    self._fail(failure=failure)
                telemetry = self._publish(result=result, enabled=enabled)
                await self._release_switched_off(fresh=result.values)
                return telemetry
            finally:
                self._update_task = None

    def _fail(self, *, failure: CycleFailedError) -> NoReturn:
        err = failure.cause
        self._values = {}
        self.last_read = frozenset()
        error = {
            "type": type(err).__name__,
            "reason": str(err)
            if isinstance(err, IdentityChangedError) or has_safe_message(error=err)
            else "Device read failed",
            "exception_code": err.exception_code
            if isinstance(err, ModbusError)
            else None,
        }
        if self.last_error != error:
            _LOGGER.warning("SAJ update failed (%s)", error["type"])
        self.last_error = error
        finding = model_finding(error=err)
        if finding is not None:
            raise_model_issue(hass=self.hass, entry=self._entry, finding=finding)
        check_unreachable(
            hass=self.hass,
            entry=self._entry,
            guard=self.guard,
            now=self.hass.loop.time(),
        )
        self._schedule_wakeup(target=failure.next_wakeup)
        _raise_update_failed(err)

    def _publish(self, *, result: CycleResult, enabled: Collection[str]) -> Telemetry:
        if self.last_error is not None:
            _LOGGER.info("SAJ connection restored for configured device")
        self.last_error = None
        self._initial_refresh = False
        merged = {**self._values, **result.values}
        self._values = {
            key: value
            for key, value in merged.items()
            if key in enabled and key not in result.unavailable
        }
        self.last_read = result.read
        self.unavailable_keys = result.unavailable
        self._sync_issues(result=result, enabled=enabled)
        self._log_faults()
        self._schedule_wakeup(target=result.next_wakeup)
        return Telemetry(values=dict(self._values))

    def _sync_issues(self, *, result: CycleResult, enabled: Collection[str]) -> None:
        clear_unreachable(hass=self.hass, entry=self._entry)
        clear_model_issues(hass=self.hass, entry=self._entry)
        tracked = open_refusals(hass=self.hass, entry=self._entry)
        hidden = {
            register.key
            for register in device_registers(fit=self.device.fit)
            if not register.exposed
        }
        updated = (
            tracked_refusals(
                tracked=tracked,
                suspended=result.suspended - hidden,
                enabled=enabled,
                answered=result.read,
            )
            - hidden
        )
        if updated != tracked:
            sync_refusals(hass=self.hass, entry=self._entry, keys=updated)

    def _log_faults(self) -> None:
        name = self._entry.title
        words = self.device.profile.faults.registers_of(values=self._values)
        transition = self._faults.observe(words=words)
        for fault in sorted(transition.raised):
            _LOGGER.warning("%s: fault %s is on", name, fault)
        for fault in sorted(transition.cleared):
            _LOGGER.info("%s: fault %s cleared", name, fault)
        for source in transition.unrecognised_raised:
            _LOGGER.warning("%s: unrecognised fault bit %s is set", name, source)
        for source in transition.unrecognised_cleared:
            _LOGGER.info("%s: unrecognised fault bit %s cleared", name, source)
        self._log_pack_faults(name=name)

    def _log_pack_faults(self, *, name: str) -> None:
        seen = {
            register.key: bool(self._values[register.key])
            for register in device_registers(fit=self.device.fit)
            if register.quantity is Quantity.PROBLEM
            and register.combination is None
            and isinstance(self._values.get(register.key), int | float)
        }
        on = frozenset(key for key, value in seen.items() if value) | (
            self._packs_on - seen.keys()
        )
        for key in sorted(on - self._packs_on):
            _LOGGER.warning("%s: fault %s is on", name, key)
        for key in sorted(self._packs_on - on):
            _LOGGER.info("%s: fault %s cleared", name, key)
        self._packs_on = on

    def _schedule_wakeup(self, *, target: float | None) -> None:
        self.update_interval = (
            None
            if target is None
            else wakeup_delay(target=target, now=self.hass.loop.time())
        )

    async def write(
        self, *, key: str, value: Value, also: Mapping[str, Value] | None = None
    ) -> None:
        companions, inspection, check = self._ems_request(key=key, value=value)
        changes = {key: value, **companions, **(also or {})}
        async with self._cycle_lock:
            await self._settle(
                key=key,
                changes=changes,
                send=lambda: self.control.write(
                    key=key,
                    value=value,
                    also={name: sent for name, sent in changes.items() if name != key},
                    inspection=inspection,
                    check=check,
                ),
            )

    async def _settle(
        self,
        *,
        key: str,
        changes: Mapping[str, Value],
        send: Callable[[], Awaitable[WriteResult]],
    ) -> None:
        try:
            result = await send()
        except WRITE_ERRORS as error:
            await self._write_failed(key=key, error=error)
            raise
        self._write_succeeded(key=key, changes=changes, result=result)

    def _ems_request(
        self, *, key: str, value: Value
    ) -> tuple[dict[str, Value], Inspection | None, Callable[[Value], None] | None]:
        if key in self.ems_rows.timeouts:
            return {}, None, timeout_check(interval=self.heartbeat_interval)
        if key not in self.ems_rows.functions:
            return {}, None, None
        on = bool(value)
        companions: dict[str, Value] = {
            name: sent
            for name, sent in switch_changes(rows=self.ems_rows, key=key, on=on).items()
            if name != key
        }
        inspection = (
            timeout_inspection(interval=self.heartbeat_interval) if on else None
        )
        return companions, inspection, None

    def _write_succeeded(
        self, *, key: str, changes: Mapping[str, Value], result: WriteResult
    ) -> None:
        self._apply_written(values=result.values, assumed=result.assumed)
        if result.written:
            self.writes.acknowledged += 1
            self.writes.last = LastWrite(
                key=key, outcome=WriteOutcome.ACKNOWLEDGED, exception_code=None
            )
            if result.assumed and not result.values:
                _LOGGER.info("SAJ command %s acknowledged", key)
        self._track_ownership(changes=changes, result=result)

    async def _write_failed(self, *, key: str, error: WriteError) -> None:
        outcome = write_outcome(error=error)
        if outcome is not None:
            self._record_failure(key=key, error=error, outcome=outcome)
        if error.link_failed:
            await self._link_lost()

    def _record_failure(
        self, *, key: str, error: WriteError, outcome: WriteOutcome
    ) -> None:
        if outcome is WriteOutcome.REJECTED:
            self.writes.rejected += 1
        elif outcome is WriteOutcome.UNCONFIRMED:
            self.writes.unconfirmed += 1
            _LOGGER.warning("SAJ write to %s was not confirmed by the inverter", key)
        else:
            self.writes.acknowledged += 1
            _LOGGER.warning(
                "SAJ write to %s was acknowledged but the inverter holds"
                " a different value",
                key,
            )
            self._apply_written(values=read_back_values(error=error), assumed=False)
        self.writes.last = LastWrite(
            key=key, outcome=outcome, exception_code=rejection_code(error=error)
        )

    async def _link_lost(self) -> None:
        self._schedule_wakeup(target=await self.poller.link_failed())
        self._schedule_refresh()

    def _apply_written(self, *, values: Mapping[str, Value], assumed: bool) -> None:
        known = self.assumed if assumed else self._values
        wanted = (
            values
            if assumed
            else {k: v for k, v in values.items() if k in self.enabled_keys}
        )
        changed = frozenset(k for k, v in wanted.items() if known.get(k) != v)
        known.update(wanted)
        if not changed:
            return
        self.data = Telemetry(values=dict(self._values))
        self.changed_keys = changed
        self.async_update_listeners()
        self.changed_keys = frozenset()

    def _track_ownership(
        self, *, changes: Mapping[str, Value], result: WriteResult
    ) -> None:
        for name, sent in changes.items():
            function = self.ems_rows.functions.get(name)
            if function is None or not (result.written or not sent):
                continue
            if sent:
                self.ems.acquire(function=function, key=name)
            else:
                self.ems.release_function(function=function, key=name)
        self._sync_heartbeat()

    async def _release_switched_off(self, *, fresh: Mapping[str, Value]) -> None:
        states: dict[PowerFunction, bool | None] = {}
        if self.ems.owned:
            values = {**self.power_values, **fresh}
            for function in self.ems.owned:
                control = self.power_controls[function]
                if not control.state_keys.isdisjoint(fresh):
                    states[function] = control.running(values=values)
        released = sorted(self.ems.found_off(states=states))
        for function in released:
            _LOGGER.info(
                "SAJ %s power control function was found switched off in the"
                " inverter; it is no longer owned",
                function,
            )
            self._stopping.discard(function)
            self.outstanding.pop(function, None)
        forgotten = [
            function
            for function in released
            if self.remembered_modes.pop(function, None) is not None
        ]
        self._sync_heartbeat()
        self._sync_retry()
        if forgotten:
            await self._save_power_state()

    def _end_ownership(self) -> None:
        self.ems.release()
        self._started = {}
        self._stopping.clear()
        self._cancel_heartbeat()

    def _sync_heartbeat(self) -> None:
        if not self._beat_targets():
            self._cancel_heartbeat()
        elif self._stop_heartbeat is None:
            self._stop_heartbeat = async_track_time_interval(
                self.hass,
                self._beat,
                timedelta(seconds=self.heartbeat_interval),
                name="SAJ EMS heartbeat",
            )

    def _beat_targets(self) -> dict[PowerFunction, str]:
        return {
            function: control.beat_key
            for function, control in self.power_controls.items()
            if function in self.ems.owned
            and function not in self._stopping
            and control.beat_key is not None
        }

    def _cancel_heartbeat(self) -> None:
        if self._stop_heartbeat is not None:
            self._stop_heartbeat()
            self._stop_heartbeat = None

    async def _beat(self, now: datetime) -> None:
        del now
        async with self._cycle_lock:
            keys = self.ems.beat_keys(targets=self._beat_targets())
            for key in keys:
                try:
                    value = await self.control.keep_alive_read_ems(key=key)
                except WRITE_ERRORS as error:
                    self._beat_dropped(key=key, error=error)
                    if error.link_failed:
                        await self._link_lost()
                        return
                else:
                    self.writes.beats_sent += 1
                    if self.ems.beat_succeeded(
                        function=self.ems_rows.target_functions[key]
                    ):
                        _LOGGER.info("SAJ EMS heartbeat for %s recovered", key)
                    self._apply_written(values={key: value}, assumed=True)
            if keys:
                await self._read_limits()

    async def _read_limits(self) -> None:
        try:
            values = await self.control.read_ems_limits()
        except WRITE_ERRORS as error:
            _LOGGER.debug("SAJ EMS limits were not read: %s", error)
            if error.link_failed:
                await self._link_lost()
            return
        self._apply_written(values=values, assumed=True)

    def _beat_dropped(self, *, key: str, error: WriteError) -> None:
        self.writes.beats_dropped += 1
        if self.ems.beat_dropped(function=self.ems_rows.target_functions[key]):
            _LOGGER.warning(
                "SAJ EMS heartbeat for %s dropped: %s; the inverter's EMS timeout"
                " will end the function if beats keep failing",
                key,
                error,
            )
        else:
            _LOGGER.debug("SAJ EMS heartbeat for %s dropped: %s", key, error)

    @property
    def power_values(self) -> dict[str, Value]:
        return {**self.assumed, **self._values}

    def power_running(self, *, function: PowerFunction) -> bool | None:
        return self.power_controls[function].running(values=self.power_values)

    def power_target_shown(self, *, function: PowerFunction) -> int | None:
        if self.power_running(function=function):
            held = self.power_controls[function].held(values=self.power_values)
            if held is not None:
                return held
        return self.power_targets.get(function)

    def power_range(self, *, function: PowerFunction) -> Range:
        return self.power_controls[function].target_range

    def _running_functions(self) -> frozenset[PowerFunction]:
        return frozenset(
            function
            for function in self.power_controls
            if self.power_running(function=function)
        )

    async def async_load_power_state(self) -> None:
        stored = await self._store.async_load() or {}
        self.power_targets = {
            function: int(watts)
            for name, watts in stored.get(STORED_TARGETS, {}).items()
            if (function := PowerFunction(name)) in self.power_controls
        }
        self.remembered_modes = {
            function: int(mode)
            for name, mode in stored.get(STORED_MODES, {}).items()
            if (function := PowerFunction(name)) in self.power_controls
        }

    async def _save_power_state(self) -> None:
        await self._store.async_save(
            {
                STORED_TARGETS: {
                    function.value: watts
                    for function, watts in self.power_targets.items()
                },
                STORED_MODES: {
                    function.value: mode
                    for function, mode in self.remembered_modes.items()
                },
            }
        )

    async def async_power_on(self, *, function: PowerFunction) -> None:
        async with self._cycle_lock:
            self.control.require_admitted()
            watts = require_target(function=function, targets=self.power_targets)
            await self._start(function=function, watts=watts)

    async def async_power_off(self, *, function: PowerFunction) -> None:
        async with self._cycle_lock:
            await self._stop(function=function)

    async def async_set_power_target(
        self, *, function: PowerFunction, raw: float
    ) -> None:
        watts = self.power_controls[function].require_usable(raw=raw)
        async with self._cycle_lock:
            if self.power_running(function=function):
                await self._change(function=function, watts=watts)
            self.power_targets[function] = watts
            await self._save_power_state()
        self.async_update_listeners()

    async def _start(self, *, function: PowerFunction, watts: int) -> None:
        control = self.power_controls[function]
        await self._require_others_idle(function=function)
        prior = await self._read_prior(control=control)
        plan = control.start(watts=watts, prior=prior)
        previous = self.remembered_modes.get(function)
        if plan.remember is not None:
            self.remembered_modes[function] = plan.remember
        sent = 0
        try:
            for write in plan.writes:
                await self._send(write=write)
                sent += 1
        except WRITE_ERRORS:
            await self._undo_start(function=function, sent=sent, previous=previous)
            raise
        self.ems.acquire(function=function)
        self._sync_heartbeat()
        await self._save_power_state()
        self.async_update_listeners()
        _LOGGER.info("SAJ %s power control function started", function)

    async def _require_others_idle(self, *, function: PowerFunction) -> None:
        others = {
            other: control
            for other, control in self.power_controls.items()
            if other != function
        }
        keys = frozenset().union(*(control.state_keys for control in others.values()))
        running: set[PowerFunction] = set()
        if keys:
            fresh = await self._read_guarded(
                key=min(keys), read=lambda: self.control.read_states(keys=keys)
            )
            self._apply_written(values=fresh, assumed=False)
            running = {
                other
                for other, control in others.items()
                if control.running(values=fresh)
            }
        require_none_running(function=function, running=running)

    async def _read_prior(self, *, control: FunctionControl[PowerMethod]) -> Value:
        key = control.prior_key
        if key is None:
            return None
        return await self._read_guarded(
            key=key, read=lambda: self.control.read_setting(key=key)
        )

    async def _read_guarded[Read](
        self, *, key: str, read: Callable[[], Awaitable[Read]]
    ) -> Read:
        try:
            return await read()
        except WRITE_ERRORS as error:
            await self._write_failed(key=key, error=error)
            raise

    async def _undo_start(
        self, *, function: PowerFunction, sent: int, previous: int | None
    ) -> None:
        if sent:
            try:
                await self._stop(function=function)
            except WRITE_ERRORS as error:
                _LOGGER.warning(
                    "SAJ could not undo the partial start of %s: %s;"
                    " its stop is outstanding",
                    function,
                    error,
                )
                await self._leave_stop_outstanding(function=function)
            return
        if previous is None:
            self.remembered_modes.pop(function, None)
        else:
            self.remembered_modes[function] = previous

    async def _leave_stop_outstanding(self, *, function: PowerFunction) -> None:
        self.ems.acquire(function=function)
        self._stopping.add(function)
        self.outstanding[function] = str(ActionKind.STOP)
        self._sync_heartbeat()
        self._sync_retry()
        await self._save_power_state()
        self.async_update_listeners()

    async def _change(self, *, function: PowerFunction, watts: int) -> None:
        writes = self.power_controls[function].change(
            watts=watts, values=self.power_values
        )
        for write in writes:
            await self._send(write=write)
        self.async_update_listeners()

    async def _stop(self, *, function: PowerFunction) -> None:
        writes = self.power_controls[function].stop(
            remembered=self.remembered_modes.get(function)
        )
        for write in writes:
            await self._switch_off(write=write)
        self.remembered_modes.pop(function, None)
        self._stopping.discard(function)
        self.ems.release_function(function=function)
        self._sync_heartbeat()
        await self._save_power_state()
        self.async_update_listeners()
        _LOGGER.info("SAJ %s power control function stopped", function)

    async def _send(self, *, write: Write) -> None:
        inspection = (
            timeout_inspection(interval=self.heartbeat_interval)
            if write.inspect_timeout
            else None
        )
        changes = {write.key: write.value, **write.also}
        await self._settle(
            key=write.key,
            changes=changes,
            send=lambda: self.control.write(
                key=write.key,
                value=write.value,
                also=write.also,
                inspection=inspection,
            ),
        )

    async def _switch_off(self, *, write: Write) -> None:
        await self._settle(
            key=write.key,
            changes={write.key: write.value, **write.also},
            send=lambda: self.control.switch_off(write=write),
        )

    async def async_follow_schedules(self) -> None:
        if not self.schedules:
            return
        self._stop_listening = async_track_state_change_event(
            self.hass,
            [schedule.entity_id for schedule in self.schedules],
            self._schedule_changed,
        )
        await self._follow()

    @callback
    def _schedule_changed(self, event: Event[EventStateChangedData]) -> None:
        del event
        self.hass.async_create_task(self._follow(), name="SAJ power control schedule")

    def _wishes(self) -> dict[PowerFunction, Wish]:
        wishes: dict[PowerFunction, Wish] = {}
        for schedule in self.schedules:
            state = self.hass.states.get(schedule.entity_id)
            on = state is not None and state.state == SCHEDULE_ON
            wishes[schedule.function] = Wish(
                on=on,
                power=state.attributes.get(SCHEDULE_POWER_ATTRIBUTE)
                if on and state is not None
                else None,
            )
        return wishes

    async def _follow(self, now: datetime | None = None) -> None:
        del now
        async with self._cycle_lock:
            if self._closed:
                return
            previous = self.outstanding
            self.outstanding = {}
            await self._finish_stops(previous=previous)
            if self.schedules and self.control_allowed:
                await self._follow_schedules(previous=previous)
            self.outstanding.update(dict.fromkeys(self._stopping, str(ActionKind.STOP)))
            self._sync_retry()

    async def _finish_stops(self, *, previous: Mapping[PowerFunction, str]) -> None:
        for function in sorted(self._stopping):
            try:
                await self._stop(function=function)
            except WRITE_ERRORS as error:
                label = str(ActionKind.STOP)
                self.outstanding[function] = label
                level = (
                    logging.DEBUG
                    if previous.get(function) == label
                    else logging.WARNING
                )
                _LOGGER.log(
                    level,
                    "SAJ %s power control function could not be stopped: %s",
                    function,
                    error,
                )

    async def _follow_schedules(self, *, previous: Mapping[PowerFunction, str]) -> None:
        wishes = {
            function: wish
            for function, wish in self._wishes().items()
            if function not in self._stopping
        }
        actions = decide(
            wishes=wishes,
            situation=Situation(
                controls={
                    function: self.power_controls[function]
                    for function in self.power_offered
                },
                running=self._running_functions(),
                owned=self.ems.owned,
                started=self._started,
                targets=self.power_targets,
            ),
        )
        for action in actions:
            await self._act(action=action, previous=previous)

    async def _act(
        self, *, action: Action, previous: Mapping[PowerFunction, str]
    ) -> None:
        if action.kind is ActionKind.BLOCKED:
            self._attempt_failed(action=action, previous=previous, error=None)
            return
        try:
            await self._performers[action.kind](action)
        except WRITE_ERRORS as error:
            self._attempt_failed(action=action, previous=previous, error=error)
            return
        if action.function in previous:
            _LOGGER.info(
                "SAJ %s power control schedule action succeeded", action.function
            )

    async def _forget(self, action: Action) -> None:
        self._started.pop(action.function, None)

    async def _schedule_stop(self, action: Action) -> None:
        await self._stop(function=action.function)
        self._started.pop(action.function, None)

    async def _apply_change(self, action: Action) -> None:
        watts = action.watts
        if watts is None:
            return
        await self._change(function=action.function, watts=watts)
        self.power_targets[action.function] = watts

    async def _schedule_change(self, action: Action) -> None:
        await self._apply_change(action)
        self._started[action.function] = action.watts

    async def _schedule_take_over(self, action: Action) -> None:
        await self._apply_change(action)
        self.ems.acquire(function=action.function)
        self._sync_heartbeat()
        self._started[action.function] = action.watts

    async def _schedule_start(self, action: Action) -> None:
        function = action.function
        if action.watts is not None:
            self.power_targets[function] = action.watts
        await self._start(function=function, watts=self.power_targets[function])
        self._started[function] = action.watts

    @property
    def _performers(self) -> dict[ActionKind, Callable[[Action], Awaitable[None]]]:
        return {
            ActionKind.FORGET: self._forget,
            ActionKind.STOP: self._schedule_stop,
            ActionKind.CHANGE_POWER: self._schedule_change,
            ActionKind.TAKE_OVER: self._schedule_take_over,
            ActionKind.START: self._schedule_start,
        }

    def _attempt_failed(
        self,
        *,
        action: Action,
        previous: Mapping[PowerFunction, str],
        error: Exception | None,
    ) -> None:
        function = action.function
        label = str(action.blocker or action.kind)
        self.outstanding[function] = label
        level = logging.DEBUG if previous.get(function) == label else logging.WARNING
        reason = BLOCKER_MESSAGES[action.blocker] if error is None else str(error)
        _LOGGER.log(
            level,
            "SAJ %s power control schedule action %s did not complete: %s",
            function,
            label,
            reason,
        )

    def _sync_retry(self) -> None:
        if not (self.outstanding or self._stopping):
            if self._stop_retry is not None:
                self._stop_retry()
                self._stop_retry = None
        elif self._stop_retry is None:
            self._stop_retry = async_track_time_interval(
                self.hass,
                self._follow,
                timedelta(seconds=self.heartbeat_interval),
                name="SAJ power control retry",
            )

    def _stop_following(self) -> None:
        self._closed = True
        if self._stop_listening is not None:
            self._stop_listening()
            self._stop_listening = None
        if self._stop_retry is not None:
            self._stop_retry()
            self._stop_retry = None

    async def async_release_power_control(self) -> None:
        self._stop_following()
        owned = sorted(self.ems.owned)
        if not owned:
            return
        async with self._cycle_lock:
            try:
                async with asyncio.timeout(EMS_RELEASE_TIMEOUT):
                    for function in owned:
                        await self._release_function(function=function)
            except TimeoutError:
                _LOGGER.warning(
                    "SAJ ran out of time switching off the power control"
                    " functions it owns"
                )
            finally:
                self._end_ownership()

    async def _release_function(self, *, function: PowerFunction) -> None:
        try:
            await self._stop(function=function)
        except WRITE_ERRORS as error:
            _LOGGER.warning(
                "SAJ could not switch off the %s power control function it owns (%s)",
                function,
                type(error).__name__,
            )

    async def async_shutdown(self) -> None:
        self._stop_following()
        self._cancel_heartbeat()
        await super().async_shutdown()
        task = self._update_task
        if task is not None and task is not asyncio.current_task():
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
        await self.client.close()

    @property
    def enabled_keys(self) -> set[str]:
        entity_keys = self._power_entity_keys()
        if self._initial_refresh:
            wanted = set(
                enabled_entity_keys(
                    hass=self.hass,
                    entry_id=self.entry_id,
                    registers=device_registers(fit=self.device.fit),
                )
            ) | enabled_power_keys(
                hass=self.hass, entry_id=self.entry_id, keys=entity_keys
            )
        else:
            wanted = {str(context) for context in self.async_contexts()}
        return (
            (wanted - entity_keys)
            | self._power_state_keys(wanted=wanted)
            | hidden_sources(fit=self.device.fit, keys=wanted)
        )

    def _power_entity_keys(self) -> frozenset[str]:
        return frozenset(
            key
            for function in self.power_offered
            for key in (function.switch_key, function.target_key)
        )

    def _power_state_keys(self, *, wanted: Collection[str]) -> set[str]:
        scheduled = {schedule.function for schedule in self.schedules}
        followed = {
            function
            for function in self.power_offered
            if function in scheduled
            or function.switch_key in wanted
            or function.target_key in wanted
        }
        return {
            key
            for function in followed | self.ems.owned
            for key in self.power_controls[function].state_keys
        }


def _raise_update_failed(error: Exception) -> NoReturn:
    if isinstance(error, IdentityChangedError):
        raise UpdateFailed(
            translation_domain=DOMAIN, translation_key="identity_mismatch"
        ) from error
    translation = translate_error(error=error)
    raise UpdateFailed(
        translation_domain=DOMAIN,
        translation_key=translation.key,
        translation_placeholders=translation.placeholders,
    ) from error
