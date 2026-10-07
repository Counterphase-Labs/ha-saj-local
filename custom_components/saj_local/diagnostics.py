from typing import TYPE_CHECKING, Any

from .const import CONF_MODEL, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
from .saj.telemetry import OPERATING_MODE, OPERATING_MODE_NAMES

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    del hass
    runtime = entry.runtime_data
    coordinator = runtime.coordinator
    data = {
        "model_selection": entry.data[CONF_MODEL],
        "profile": runtime.device.profile.key,
        "profile_detected": runtime.device.detected,
        "profile_hand_verified": runtime.device.profile.hand_verified,
        "device_type": runtime.device.device_type,
        "rated_power_w": runtime.device.rated_power,
        "poll_interval_seconds": entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        ),
        "enabled_sensors": sorted(coordinator.enabled_sensor_keys),
        "connected": runtime.client.is_connected(),
        "last_update_success": coordinator.last_update_success,
        "last_error": coordinator.last_error,
    }
    mode = (
        coordinator.data.get(key=OPERATING_MODE)
        if coordinator.data is not None
        else None
    )
    if mode is not None and mode not in OPERATING_MODE_NAMES:
        data["unknown_operating_mode"] = mode
    return data
