import asyncio
import logging
import math
from contextlib import asynccontextmanager, suppress
from datetime import timedelta
from typing import TYPE_CHECKING, NoReturn

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    CONF_MODEL,
    CONF_SCAN_INTERVAL,
    CONF_SENSORS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    SUBENTRY_POLLING_GROUP,
)
from .errors import has_safe_message, translate_error
from .saj.budget import BUDGET_PER_MINUTE
from .saj.client import ModbusError, ModbusTcpClient
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
from .saj.schedule import Cadence, Schedule, build_cadences
from .saj.telemetry import Telemetry

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Collection

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from .saj.device import Device
    from .saj.guard import EndpointGuard

_LOGGER = logging.getLogger(__name__)


def wakeup_delay(*, target: float, now: float) -> timedelta:
    # Home Assistant schedules from the whole second of the moment it schedules,
    # so rounding the distance up from that second lands on or after the target.
    # A zero interval would mean no schedule at all, hence the one second floor.
    return timedelta(seconds=max(1, math.ceil(target - math.floor(now))))


def _group_cadences(*, entry: ConfigEntry) -> list[Cadence]:
    return [
        Cadence(
            interval=int(subentry.data[CONF_SCAN_INTERVAL]),
            keys=frozenset(subentry.data[CONF_SENSORS]),
        )
        for subentry in entry.subentries.values()
        if subentry.subentry_type == SUBENTRY_POLLING_GROUP
    ]


class SajCoordinator(DataUpdateCoordinator[Telemetry]):
    def __init__(
        self,
        hass: HomeAssistant,
        client: ModbusTcpClient,
        device: Device,
        entry: ConfigEntry,
        guard: EndpointGuard,
    ) -> None:
        super().__init__(hass=hass, logger=_LOGGER, name="SAJ")
        self.client = client
        self.device = device
        self.model_selection = entry.data[CONF_MODEL]
        self.entry_id = entry.entry_id
        self.last_error: dict[str, int | str | None] | None = None
        self.last_read: frozenset[str] = frozenset()
        self.unavailable_keys: frozenset[str] = frozenset()
        self.poller = Poller(
            target=Target(client=client, device=device, selection=self.model_selection),
            tracking=Tracking(
                schedule=Schedule(
                    cadences=build_cadences(
                        default_interval=entry.options.get(
                            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                        ),
                        groups=_group_cadences(entry=entry),
                        supported=device.profile.measurement_keys,
                    ),
                    origin=hass.loop.time(),
                ),
                health=ReadHealth(),
                guard=guard,
            ),
            services=Services(clock=hass.loop.time, bound=asyncio.wait_for),
        )
        self._values: dict[str, int | float | None] = {}
        self._cycle_lock = asyncio.Lock()
        self._initial_refresh = True
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
                enabled = self._enabled_keys()
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
        self.unavailable_keys = result.unavailable
        self._schedule_wakeup(target=result.next_wakeup)
        return Telemetry(values=dict(self._values))

    def _schedule_wakeup(self, *, target: float | None) -> None:
        self.update_interval = (
            None
            if target is None
            else wakeup_delay(target=target, now=self.hass.loop.time())
        )

    async def async_shutdown(self) -> None:
        await super().async_shutdown()
        task = self._update_task
        if task is not None and task is not asyncio.current_task():
            task.cancel()
            with suppress(asyncio.CancelledError):
                await task
        await self.client.close()

    def _enabled_keys(self) -> set[str]:
        if self._initial_refresh:
            return set(self.device.profile.measurement_keys)
        return {str(context) for context in self.async_contexts()}

    @property
    def enabled_sensor_keys(self) -> set[str]:
        return self._enabled_keys()


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
