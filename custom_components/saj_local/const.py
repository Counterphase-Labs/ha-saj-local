from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.const import Platform
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.translation import async_get_translations

from .saj.catalogue import is_estimate
from .saj.guard import EndpointGuard
from .saj.models import PowerFunction
from .saj.schedule import Cadence

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from .saj.catalogue import Register

DOMAIN = "saj_local"
INTEGRATION_TITLE = "SAJ Local"
VALIDATION_LABEL = f"{INTEGRATION_TITLE} validation"
CONF_MODEL = "model"
CONF_DEVICE_TYPE = "device_type"
CONF_UNIT_ID = "unit_id"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_KEYS = "keys"
CONF_PREFIX = "prefix"
CONF_ALLOW_CONTROL = "allow_control"
CONF_EMS_HEARTBEAT = "ems_heartbeat"
CONF_EQUIPMENT = "equipment"
CONF_DETECTED_EQUIPMENT = "detected_equipment"
CONF_FITTED_EQUIPMENT = "fitted_equipment"
CONF_HIGHEST_PACK_COUNT = "highest_pack_count"
EQUIPMENT_SELECTOR = "equipment"
EQUIPMENT_ISSUE_TRANSLATION_KEY = "equipment_not_detected"
ISSUE_MODEL_MISMATCH = "model_mismatch"
ISSUE_IDENTITY_MISMATCH = "identity_mismatch"
ISSUE_UNSUPPORTED_DEVICE = "unsupported_device"
ISSUE_REGISTERS_REFUSED = "registers_refused"
ISSUE_ENDPOINT_UNREACHABLE = "endpoint_unreachable"
MODEL_ISSUES = (
    ISSUE_MODEL_MISMATCH,
    ISSUE_IDENTITY_MISMATCH,
    ISSUE_UNSUPPORTED_DEVICE,
)
UNREACHABLE_AFTER = 15 * 60
OBJECT_ID_ROOT = "saj"
KEY_PLACEHOLDER = "<key>"
DOMAIN_PLACEHOLDER = "<domain>"
SUBENTRY_POLLING_GROUP = "polling_group"
SUBENTRY_POWER_SCHEDULE = "power_schedule"
CONF_FUNCTION = "function"
CONF_SCHEDULE = "schedule"
SCHEDULE_DOMAIN = "schedule"
FUNCTION_SELECTOR = "power_function"
SCHEDULE_ON = "on"
SCHEDULE_POWER_ATTRIBUTE = "power"
POWER_STORAGE_VERSION = 1
BATTERY_STORAGE_VERSION = 1
BATTERY_SAVE_INTERVAL = 10 * 60
STORED_TARGETS = "targets"
STORED_MODES = "remembered_modes"
DEFAULT_PORT = 502
MAX_PORT = 65535
MIN_UNIT_ID = 1
MAX_UNIT_ID = 247
DEFAULT_UNIT_ID = 1
DEFAULT_SCAN_INTERVAL = 60
REQUEST_TIMEOUT = 5
EMS_RELEASE_TIMEOUT = 5
PLATFORMS = (
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SWITCH,
    Platform.TIME,
    Platform.BUTTON,
)


async def selector_options(
    *, hass: HomeAssistant, selector_name: str
) -> dict[str, str]:
    translations = await async_get_translations(
        hass, hass.config.language, "selector", [DOMAIN]
    )
    prefix = f"component.{DOMAIN}.selector.{selector_name}.options."
    return {
        name.removeprefix(prefix): label
        for name, label in translations.items()
        if name.startswith(prefix)
    }


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
    return enabled_keys(
        registered=installation_entities(hass=hass, entry_id=entry_id),
        registers=registers,
    )


def enabled_keys(
    *, registered: Mapping[str, er.RegistryEntry], registers: Iterable[Register]
) -> frozenset[str]:
    shown = [
        register
        for register in registers
        if (
            register.core
            if register.key not in registered
            else registered[register.key].disabled_by is None
        )
    ]
    return frozenset(register.key for register in shown) | frozenset(
        source
        for register in shown
        if is_estimate(register=register)
        for source in register.sources
    )


def group_cadences(
    *, entry: ConfigEntry, excluding: str | None = None
) -> list[Cadence]:
    return [
        Cadence(
            interval=int(subentry.data[CONF_SCAN_INTERVAL]),
            keys=frozenset(subentry.data[CONF_KEYS]),
        )
        for subentry in entry.subentries.values()
        if subentry.subentry_type == SUBENTRY_POLLING_GROUP
        and subentry.subentry_id != excluding
    ]


@dataclass(frozen=True)
class PowerSchedule:
    function: PowerFunction
    registry_id: str


def power_schedules(
    *, entry: ConfigEntry, excluding: str | None = None
) -> tuple[PowerSchedule, ...]:
    return tuple(
        PowerSchedule(
            function=PowerFunction(subentry.data[CONF_FUNCTION]),
            registry_id=subentry.data[CONF_SCHEDULE],
        )
        for subentry in entry.subentries.values()
        if subentry.subentry_type == SUBENTRY_POWER_SCHEDULE
        and subentry.subentry_id != excluding
    )


def enabled_power_keys(
    *, hass: HomeAssistant, entry_id: str, keys: Iterable[str]
) -> frozenset[str]:
    registered = installation_entities(hass=hass, entry_id=entry_id)
    return frozenset(
        key for key in keys if key in registered and registered[key].disabled_by is None
    )
