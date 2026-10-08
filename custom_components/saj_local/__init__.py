import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.exceptions import ConfigEntryError, ConfigEntryNotReady

from .const import (
    CONF_MODEL,
    CONF_SCAN_INTERVAL,
    CONF_UNIT_ID,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_UNIT_ID,
    DOMAIN,
    PLATFORMS,
    REQUEST_TIMEOUT,
    SUBENTRY_POLLING_GROUP,
    endpoint_guard,
)
from .coordinator import SajCoordinator
from .errors import HANDLED_ERRORS, translate_error
from .saj.client import ClientEnvironment, ModbusError, ModbusTcpClient
from .saj.device import Device, identify

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant


@dataclass
class SajRuntimeData:
    client: ModbusTcpClient
    device: Device
    coordinator: SajCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    model_selection = entry.data[CONF_MODEL]
    guard = endpoint_guard(
        hass=hass,
        host=entry.data[CONF_HOST],
        port=entry.data.get(CONF_PORT, DEFAULT_PORT),
    )
    if guard.retry_in(now=hass.loop.time()) > 0:
        raise ConfigEntryNotReady(
            translation_domain=DOMAIN, translation_key="backing_off"
        )
    client = ModbusTcpClient(
        host=entry.data[CONF_HOST],
        port=entry.data.get(CONF_PORT, DEFAULT_PORT),
        unit_id=entry.data.get(CONF_UNIT_ID, DEFAULT_UNIT_ID),
        timeout=REQUEST_TIMEOUT,
        environment=ClientEnvironment(budget=guard.budget),
    )
    try:
        device = await identify(client=client, selection=model_selection)
        _validate_identity(device=device, serial=entry.unique_id)
        coordinator = SajCoordinator(
            hass=hass,
            client=client,
            device=device,
            entry=entry,
            guard=guard,
        )
        await coordinator.async_config_entry_first_refresh()
    except HANDLED_ERRORS as err:
        await client.close()
        if isinstance(err, ModbusError):
            guard.failed(
                now=hass.loop.time(), base_delay=_shortest_interval(entry=entry)
            )
        translation = translate_error(error=err)
        failure = (
            ConfigEntryNotReady if isinstance(err, ModbusError) else ConfigEntryError
        )
        raise failure(
            translation_domain=DOMAIN,
            translation_key=translation.key,
            translation_placeholders=translation.placeholders,
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


def _shortest_interval(*, entry: ConfigEntry) -> int:
    return min(
        [
            entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            *(
                subentry.data[CONF_SCAN_INTERVAL]
                for subentry in entry.subentries.values()
                if subentry.subentry_type == SUBENTRY_POLLING_GROUP
            ),
        ]
    )


def _validate_identity(*, device: Device, serial: str | None) -> None:
    if device.serial != serial:
        raise ConfigEntryError(
            translation_domain=DOMAIN, translation_key="identity_mismatch"
        )
