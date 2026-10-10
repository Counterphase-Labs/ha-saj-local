import asyncio
import logging
import math
from contextlib import asynccontextmanager, suppress
from dataclasses import dataclass
from datetime import timedelta
from typing import TYPE_CHECKING, NoReturn

from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    CONF_EMS_HEARTBEAT,
    CONF_MODEL,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    EMS_RELEASE_TIMEOUT,
    EMS_TIMEOUT_KEY,
    enabled_entity_keys,
    group_cadences,
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
from .saj.budget import BUDGET_PER_MINUTE
from .saj.catalogue import device_keys, device_registers
from .saj.client import ModbusError, ModbusTcpClient
from .saj.ems import (
    DEFAULT_HEARTBEAT_INTERVAL,
    FUNCTION_BY_ENABLE_KEY,
    EmsOwnership,
    switch_changes,
    timeout_check,
    timeout_inspection,
)
from .saj.health import ReadHealth
from .saj.poller import (
    CycleFailedError,
    CycleResult,
    IdentityChangedError,
    Poller,
    Services,
    Target,
    Tracking,
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
    from homeassistant.core import HomeAssistant

    from .saj.codec import Value
    from .saj.control import Control, Inspection, WriteResult
    from .saj.device import Device
    from .saj.guard import EndpointGuard

_LOGGER = logging.getLogger(__name__)
RELEASE_FAILURES: tuple[type[Exception], ...] = (*WRITE_ERRORS, TimeoutError)


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
        self.writes = WriteStatistics()
        self.assumed: dict[str, Value] = {}
        self.changed_keys: frozenset[str] = frozenset()
        self._stop_heartbeat: Callable[[], None] | None = None
        self.model_selection = entry.data[CONF_MODEL]
        self.entry_id = entry.entry_id
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
                        supported=device_keys(
                            profile=device.profile, device_type=device.device_type
                        ),
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
        async with self._cycle_lock:
            yield self.client

    async def _async_update_data(self) -> Telemetry:
        async with self._cycle_lock:
            self._update_task = asyncio.current_task()
            try:
                enabled = self.enabled_keys
                try:
                    result = await self.poller.run(enabled=enabled)
                except CycleFailedError as failure:
                    self._fail(failure=failure)
                return self._publish(result=result, enabled=enabled)
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
        self._release_switched_off(values=result.values)
        self.unavailable_keys = result.unavailable
        self._schedule_wakeup(target=result.next_wakeup)
        return Telemetry(values=dict(self._values))

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
        if key == EMS_TIMEOUT_KEY:
            return {}, None, timeout_check(interval=self.heartbeat_interval)
        if key not in FUNCTION_BY_ENABLE_KEY:
            return {}, None, None
        on = bool(value)
        companions: dict[str, Value] = {
            name: sent
            for name, sent in switch_changes(key=key, on=on).items()
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
            if name in FUNCTION_BY_ENABLE_KEY and (result.written or not sent):
                self.ems.switched(key=name, on=bool(sent))
        if self.ems.owned and self._stop_heartbeat is None:
            self._stop_heartbeat = async_track_time_interval(
                self.hass,
                self._beat,
                timedelta(seconds=self.heartbeat_interval),
                name="SAJ EMS heartbeat",
            )
        elif not self.ems.owned:
            self._cancel_heartbeat()

    def _release_switched_off(self, *, values: Mapping[str, Value]) -> None:
        for function in sorted(self.ems.found_off(values=values)):
            _LOGGER.info(
                "SAJ EMS %s function was found switched off in the inverter;"
                " it is no longer kept alive",
                function,
            )
        if not self.ems.owned:
            self._cancel_heartbeat()

    def _end_ownership(self) -> None:
        self.ems.release()
        self._cancel_heartbeat()

    def _cancel_heartbeat(self) -> None:
        if self._stop_heartbeat is not None:
            self._stop_heartbeat()
            self._stop_heartbeat = None

    async def _beat(self, now: datetime) -> None:
        del now
        async with self._cycle_lock:
            keys = self.ems.beat_keys()
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
                    if self.ems.beat_succeeded(target_key=key):
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
        if self.ems.beat_dropped(target_key=key):
            _LOGGER.warning(
                "SAJ EMS heartbeat for %s dropped: %s; the inverter's EMS timeout"
                " will end the function if beats keep failing",
                key,
                error,
            )
        else:
            _LOGGER.debug("SAJ EMS heartbeat for %s dropped: %s", key, error)

    async def async_release_ems(self) -> None:
        owned = self.ems.owned_enable_keys
        if not owned:
            return
        async with self._cycle_lock:
            try:
                async with asyncio.timeout(EMS_RELEASE_TIMEOUT):
                    await self._settle(
                        key=owned[0],
                        changes=dict.fromkeys(owned, 0),
                        send=lambda: self.control.switch_off_ems(keys=owned),
                    )
            except RELEASE_FAILURES as error:
                _LOGGER.warning(
                    "SAJ could not switch off the EMS functions it owns (%s);"
                    " the inverter's EMS timeout ends them instead",
                    type(error).__name__,
                )
            else:
                _LOGGER.info("SAJ EMS enable bits cleared: %s", ", ".join(owned))
            finally:
                self._end_ownership()

    async def async_shutdown(self) -> None:
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
        if self._initial_refresh:
            return set(
                enabled_entity_keys(
                    hass=self.hass,
                    entry_id=self.entry_id,
                    registers=device_registers(
                        profile=self.device.profile,
                        device_type=self.device.device_type,
                    ),
                )
            )
        return {str(context) for context in self.async_contexts()}


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
