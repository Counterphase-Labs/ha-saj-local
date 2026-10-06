import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.exceptions import ConfigEntryError, ConfigEntryNotReady

from .config_flow import CONF_SCAN_INTERVAL, CONF_UNIT_ID
from .const import (
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_UNIT_ID,
    DOMAIN,
    PLATFORMS,
    REQUEST_TIMEOUT,
)
from .coordinator import SajCoordinator
from .saj.client import ModbusError, ModbusErrorMessage, ModbusTcpClient
from .saj.hs3 import Hs3Device, UnsupportedDeviceError, identify

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant


@dataclass
class SajRuntimeData:
    client: ModbusTcpClient
    device: Hs3Device
    coordinator: SajCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    client = ModbusTcpClient(
        host=entry.data[CONF_HOST],
        port=entry.data.get(CONF_PORT, DEFAULT_PORT),
        unit_id=entry.data.get(CONF_UNIT_ID, DEFAULT_UNIT_ID),
        timeout=REQUEST_TIMEOUT,
    )
    try:
        device = await identify(client=client)
        _validate_identity(device=device, serial=entry.unique_id)
        coordinator = SajCoordinator(
            hass=hass,
            client=client,
            device=device,
            entry_id=entry.entry_id,
            interval=entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
        await coordinator.async_config_entry_first_refresh()
    except UnsupportedDeviceError as err:
        await client.close()
        raise ConfigEntryError(
            translation_domain=DOMAIN, translation_key="unsupported_device"
        ) from err
    except ValueError as err:
        await client.close()
        raise ConfigEntryError(
            translation_domain=DOMAIN, translation_key="invalid_device_data"
        ) from err
    except ModbusError as err:
        await client.close()
        if err.exception_code is not None:
            translation_key = "read_rejected"
        elif str(err) in {
            ModbusErrorMessage.CONNECTION_TIMEOUT,
            ModbusErrorMessage.REQUEST_TIMEOUT,
        }:
            translation_key = "timeout"
        else:
            translation_key = "cannot_connect"
        raise ConfigEntryNotReady(
            translation_domain=DOMAIN, translation_key=translation_key
        ) from err
    except asyncio.CancelledError:
        await client.close()
        raise
    except Exception:
        await client.close()
        raise
    entry.runtime_data = SajRuntimeData(
        client=client, device=device, coordinator=coordinator
    )
    try:
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    except asyncio.CancelledError:
        await coordinator.async_shutdown()
        await client.close()
        raise
    except Exception:
        await coordinator.async_shutdown()
        await client.close()
        raise
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        await entry.runtime_data.coordinator.async_shutdown()
        await entry.runtime_data.client.close()
    return unloaded


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


def _validate_identity(*, device: Hs3Device, serial: str | None) -> None:
    if device.serial != serial:
        raise ConfigEntryError(
            translation_domain=DOMAIN, translation_key="identity_mismatch"
        )
