import asyncio
import logging
from contextlib import asynccontextmanager, suppress
from datetime import timedelta
from typing import TYPE_CHECKING, NoReturn

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, SENSOR_KEYS
from .saj.client import ModbusError, ModbusErrorMessage, ModbusTcpClient
from .saj.hs3 import (
    Hs3Device,
    Hs3Telemetry,
    UnsupportedDeviceError,
    identify,
    read_telemetry,
)

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class SajCoordinator(DataUpdateCoordinator[Hs3Telemetry]):
    def __init__(
        self,
        hass: HomeAssistant,
        client: ModbusTcpClient,
        device: Hs3Device,
        entry_id: str,
        interval: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name="SAJ",
            update_interval=timedelta(seconds=interval),
        )
        self.client = client
        self.device = device
        self.interval = interval
        self.entry_id = entry_id
        self.last_error: dict[str, int | str | None] | None = None
        self._cycle_lock = asyncio.Lock()
        self._initial_refresh = True
        self._update_task: asyncio.Task[object] | None = None

    @asynccontextmanager
    async def async_validation_session(self) -> AsyncIterator[None]:
        async with self._cycle_lock:
            yield

    async def _async_update_data(self) -> Hs3Telemetry:
        async with self._cycle_lock:
            self._update_task = asyncio.current_task()
            try:
                try:
                    if not self.client.is_connected():
                        await self.client.close()
                        await self.client.connect()
                        current = await identify(client=self.client)
                        if current.serial != self.device.serial:
                            _raise_identity_changed()
                    enabled = self._enabled_keys()
                    snapshot = await read_telemetry(client=self.client, enabled=enabled)
                except (
                    ModbusError,
                    IdentityChangedError,
                    TimeoutError,
                    OSError,
                    ValueError,
                    UnsupportedDeviceError,
                ) as err:
                    await self.client.close()
                    error = {
                        "type": type(err).__name__,
                        "reason": str(err)
                        if isinstance(err, ModbusError | IdentityChangedError)
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
            return set(SENSOR_KEYS)
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


def _raise_update_failed(error: Exception) -> NoReturn:
    if isinstance(error, TimeoutError) or (
        isinstance(error, ModbusError)
        and str(error)
        in {
            ModbusErrorMessage.CONNECTION_TIMEOUT,
            ModbusErrorMessage.REQUEST_TIMEOUT,
        }
    ):
        key = "timeout"
    elif isinstance(error, ModbusError) and error.exception_code is not None:
        key = "read_rejected"
    elif isinstance(error, UnsupportedDeviceError):
        key = "unsupported_device"
    elif isinstance(error, IdentityChangedError):
        key = "identity_mismatch"
    elif isinstance(error, ValueError):
        key = "invalid_device_data"
    else:
        key = "cannot_connect"
    raise UpdateFailed(
        translation_domain=DOMAIN,
        translation_key=key,
    ) from error
