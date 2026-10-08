from typing import TYPE_CHECKING, Any

from .const import CONF_MODEL, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
from .saj.budget import BUDGET_PER_MINUTE
from .saj.telemetry import OPERATING_MODE, OPERATING_MODE_NAMES

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    runtime = entry.runtime_data
    coordinator = runtime.coordinator
    poller = coordinator.poller
    now = hass.loop.time()
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
        "cadences": [
            {
                "default": plan.default,
                "interval_seconds": plan.interval,
                "sensors": sorted(plan.keys),
                "requests_per_read": plan.requests,
            }
            for plan in poller.cadence_plans()
        ],
        "planned_requests_per_minute": poller.planned_load(),
        "request_budget_per_minute": BUDGET_PER_MINUTE,
        "last_cycle_read": sorted(coordinator.last_read),
        "refused_sensors": {
            key: {
                "exception_code": refusal.code,
                "consecutive_refusals": refusal.count,
                "suspended": refusal.retest_at is not None,
                "next_retest_in_seconds": None
                if refusal.retest_at is None
                else max(0.0, refusal.retest_at - now),
            }
            for key, refusal in poller.refusals.items()
        },
        "consecutive_failed_cycles": poller.consecutive_failures,
        "backoff_seconds": poller.backoff_seconds,
        "late_frames_discarded": runtime.client.late_frames_discarded,
        "stale_reconnects": poller.stale_reconnects,
    }
    mode = (
        coordinator.data.get(key=OPERATING_MODE)
        if coordinator.data is not None
        else None
    )
    if mode is not None and mode not in OPERATING_MODE_NAMES:
        data["unknown_operating_mode"] = mode
    return data
