from typing import TYPE_CHECKING

from homeassistant.const import Platform
from homeassistant.helpers import entity_registry as er

from .saj.guard import EndpointGuard
from .saj.schedule import Cadence

if TYPE_CHECKING:
    from collections.abc import Iterable

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from .saj.catalogue import Register

DOMAIN = "saj_local"
INTEGRATION_TITLE = "SAJ Local"
CONF_MODEL = "model"
CONF_DEVICE_TYPE = "device_type"
CONF_UNIT_ID = "unit_id"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_SENSORS = "sensors"
CONF_PREFIX = "prefix"
OBJECT_ID_ROOT = "saj"
KEY_PLACEHOLDER = "<key>"
DOMAIN_PLACEHOLDER = "<domain>"
SUBENTRY_POLLING_GROUP = "polling_group"
DEFAULT_PORT = 502
MAX_PORT = 65535
MIN_UNIT_ID = 1
MAX_UNIT_ID = 247
DEFAULT_UNIT_ID = 1
DEFAULT_SCAN_INTERVAL = 60
REQUEST_TIMEOUT = 5
PLATFORMS = (
    Platform.SENSOR,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SWITCH,
    Platform.TIME,
    Platform.TEXT,
)


def entity_unique_id(*, entry_id: str, key: str) -> str:
    return f"{entry_id}_{key}"


def entity_key(*, entry_id: str, unique_id: str) -> str | None:
    prefix = entity_unique_id(entry_id=entry_id, key="")
    return unique_id.removeprefix(prefix) if unique_id.startswith(prefix) else None


def object_id(*, prefix: str, key: str) -> str:
    parts = (OBJECT_ID_ROOT, prefix, key) if prefix else (OBJECT_ID_ROOT, key)
    return "_".join(parts)


def fixed_entity_id(*, domain: str, prefix: str, key: str) -> str:
    return f"{domain}.{object_id(prefix=prefix, key=key)}"


def entity_id_in_use(*, hass: HomeAssistant, entity_id: str) -> bool:
    return (
        er.async_get(hass).async_is_registered(entity_id)
        or hass.states.get(entity_id) is not None
    )


def endpoint_guard(*, hass: HomeAssistant, host: str, port: int) -> EndpointGuard:
    guards: dict[tuple[str, int], EndpointGuard] = hass.data.setdefault(DOMAIN, {})
    return guards.setdefault((host.casefold(), port), EndpointGuard())


def installation_entities(
    *, hass: HomeAssistant, entry_id: str
) -> dict[str, er.RegistryEntry]:
    registry = er.async_get(hass)
    entities: dict[str, er.RegistryEntry] = {}
    for registered in er.async_entries_for_config_entry(registry, entry_id):
        key = entity_key(entry_id=entry_id, unique_id=registered.unique_id)
        if key is not None:
            entities[key] = registered
    return entities


def enabled_entity_keys(
    *, hass: HomeAssistant, entry_id: str, registers: Iterable[Register]
) -> frozenset[str]:
    registered = installation_entities(hass=hass, entry_id=entry_id)
    return frozenset(
        register.key
        for register in registers
        if (
            register.core
            if register.key not in registered
            else registered[register.key].disabled_by is None
        )
    )


def group_cadences(
    *, entry: ConfigEntry, excluding: str | None = None
) -> list[Cadence]:
    return [
        Cadence(
            interval=int(subentry.data[CONF_SCAN_INTERVAL]),
            keys=frozenset(subentry.data[CONF_SENSORS]),
        )
        for subentry in entry.subentries.values()
        if subentry.subentry_type == SUBENTRY_POLLING_GROUP
        and subentry.subentry_id != excluding
    ]
