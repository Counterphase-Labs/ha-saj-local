from typing import TYPE_CHECKING

from homeassistant.const import Platform
from homeassistant.helpers import entity_registry as er

from .saj.guard import EndpointGuard

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

DOMAIN = "saj_local"
INTEGRATION_TITLE = "SAJ Local"
CONF_MODEL = "model"
CONF_UNIT_ID = "unit_id"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_SENSORS = "sensors"
CONF_PREFIX = "prefix"
OBJECT_ID_ROOT = "saj"
KEY_PLACEHOLDER = "<key>"
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


def sensor_object_id(*, prefix: str, key: str) -> str:
    parts = (OBJECT_ID_ROOT, prefix, key) if prefix else (OBJECT_ID_ROOT, key)
    return "_".join(parts)


def sensor_entity_id(*, prefix: str, key: str) -> str:
    return f"{Platform.SENSOR}.{sensor_object_id(prefix=prefix, key=key)}"


def entity_id_in_use(*, hass: HomeAssistant, entity_id: str) -> bool:
    return (
        er.async_get(hass).async_is_registered(entity_id)
        or hass.states.get(entity_id) is not None
    )


def endpoint_guard(*, hass: HomeAssistant, host: str, port: int) -> EndpointGuard:
    guards: dict[tuple[str, int], EndpointGuard] = hass.data.setdefault(DOMAIN, {})
    return guards.setdefault((host.casefold(), port), EndpointGuard())
