from typing import TYPE_CHECKING

from .saj.guard import EndpointGuard

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

DOMAIN = "saj_local"
INTEGRATION_TITLE = "SAJ Local"
CONF_MODEL = "model"
CONF_UNIT_ID = "unit_id"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_SENSORS = "sensors"
SUBENTRY_POLLING_GROUP = "polling_group"
DEFAULT_PORT = 502
MAX_PORT = 65535
MIN_UNIT_ID = 1
MAX_UNIT_ID = 247
DEFAULT_UNIT_ID = 1
DEFAULT_SCAN_INTERVAL = 60
REQUEST_TIMEOUT = 5
PLATFORMS = ("sensor",)


def sensor_unique_id(*, entry_id: str, key: str) -> str:
    return f"{entry_id}_{key}"


def sensor_key(*, entry_id: str, unique_id: str) -> str | None:
    prefix = sensor_unique_id(entry_id=entry_id, key="")
    return unique_id.removeprefix(prefix) if unique_id.startswith(prefix) else None


def endpoint_guard(*, hass: HomeAssistant, host: str, port: int) -> EndpointGuard:
    guards: dict[tuple[str, int], EndpointGuard] = hass.data.setdefault(DOMAIN, {})
    return guards.setdefault((host.casefold(), port), EndpointGuard())
