import asyncio
import logging
from contextlib import asynccontextmanager, suppress
from datetime import timedelta
from typing import TYPE_CHECKING, NoReturn

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import CONF_MODEL, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN
from .errors import HANDLED_ERRORS, has_safe_message, translate_error
from .saj.client import ModbusError, ModbusTcpClient
from .saj.device import Device, identify
from .saj.telemetry import Telemetry, read_telemetry

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class SajCoordinator(DataUpdateCoordinator[Telemetry]):
    def __init__(
        self,
        hass: HomeAssistant,
        client: ModbusTcpClient,
        device: Device,
        entry: ConfigEntry,
    ) -> None:
        interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name="SAJ",
            update_interval=timedelta(seconds=interval),
        )
        self.client = client
        self.device = device
        self.model_selection = entry.data[CONF_MODEL]
        self.interval = interval
        self.entry_id = entry.entry_id
        self.last_error: dict[str, int | str | None] | None = None
        self._cycle_lock = asyncio.Lock()
        self._initial_refresh = True
        self._update_task: asyncio.Task[object] | None = None

    @asynccontextmanager
    async def async_validation_session(self) -> AsyncIterator[None]:
        async with self._cycle_lock:
            yield

    async def _async_update_data(self) -> Telemetry:
        async with self._cycle_lock:
            self._update_task = asyncio.current_task()
            try:
                try:
                    if not self.client.is_connected():
                        await self.client.close()
                        await self.client.connect()
                        current = await identify(
                            client=self.client, selection=self.model_selection
                        )
                        if current.serial != self.device.serial:
                            _raise_identity_changed()
                    enabled = self._enabled_keys()
                    snapshot = await read_telemetry(
                        client=self.client, device=self.device, enabled=enabled
                    )
                except UPDATE_ERRORS as err:
                    await self.client.close()
                    error = {
                        "type": type(err).__name__,
                        "reason": str(err)
                        if isinstance(err, IdentityChangedError)
                        or has_safe_message(error=err)
                        else "Device read failed",
                        "exception_code": err.exception_code
                        if isinstance(err, ModbusError)
                        else None,
                    }
                    if self.last_error != error:
                        _LOGGER.warning("SAJ update failed (%s)", error["type"])
                    self.last_error = error
                    _raise_update_failed(err)
                except asyncio.CancelledError:
                    await self.client.close()
                    raise
                if self.last_error is not None:
                    _LOGGER.info("SAJ connection restored for configured device")
                self.last_error = None
                self._initial_refresh = False
                return snapshot
            finally:
                self._update_task = None

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


def _raise_identity_changed() -> NoReturn:
    raise IdentityChangedError


class IdentityChangedError(Exception):
    def __init__(self) -> None:
        message = "Device identity changed at configured endpoint"
        super().__init__(message)


UPDATE_ERRORS: tuple[type[Exception], ...] = (
    *HANDLED_ERRORS,
    IdentityChangedError,
    TimeoutError,
    OSError,
)


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
