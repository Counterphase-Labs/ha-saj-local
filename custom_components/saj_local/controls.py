from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.core import callback
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN, installation_entities
from .saj.catalogue import device_registers
from .saj.power_control import power_functions

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import Event, HomeAssistant

    from .saj.catalogue import Fit

CONTROL_MARK = "enabled_with_control"


def control_member_keys(*, fit: Fit) -> frozenset[str]:
    registers = {
        register.key
        for register in device_registers(fit=fit)
        if register.control and register.exposed
    }
    power = {
        key
        for function in power_functions(fit=fit)
        for key in (function.switch_key, function.target_key)
    }
    return frozenset(registers | power)


def keys_to_enable(
    *, fit: Fit, registered: Mapping[str, er.RegistryEntry]
) -> frozenset[str]:
    enabled_by_default = {
        register.key for register in device_registers(fit=fit) if register.core
    }
    return frozenset(
        key
        for key in control_member_keys(fit=fit)
        if (
            registered[key].disabled_by is er.RegistryEntryDisabler.INTEGRATION
            if key in registered
            else key not in enabled_by_default
        )
    )


def apply_control_set(
    *, hass: HomeAssistant, entry: ConfigEntry, fit: Fit, allowed: bool
) -> None:
    registered = installation_entities(hass=hass, entry_id=entry.entry_id)
    if allowed:
        _switch_on(
            hass=hass,
            entities=[
                registered[key]
                for key in control_member_keys(fit=fit)
                if key in registered
            ],
        )
    else:
        _switch_off(hass=hass, entities=list(registered.values()))


def start_control_listener(
    *, hass: HomeAssistant, entry: ConfigEntry
) -> Callable[[], None]:
    registry = er.async_get(hass)

    @callback
    def release_user_choice(event: Event[er.EventEntityRegistryUpdatedData]) -> None:
        entity = registry.async_get(event.data["entity_id"])
        if (
            event.data["action"] == "update"
            and "disabled_by" in event.data["changes"]
            and entity is not None
            and entity.config_entry_id == entry.entry_id
            and entity.disabled_by is er.RegistryEntryDisabler.USER
            and _is_marked(entity=entity)
        ):
            _remove_mark(registry=registry, entity=entity)

    return hass.bus.async_listen(er.EVENT_ENTITY_REGISTRY_UPDATED, release_user_choice)


def _is_marked(*, entity: er.RegistryEntry) -> bool:
    return CONTROL_MARK in entity.options.get(DOMAIN, {})


def _remove_mark(*, registry: er.EntityRegistry, entity: er.RegistryEntry) -> None:
    registry.async_update_entity_options(entity.entity_id, DOMAIN, None)


def _switch_on(*, hass: HomeAssistant, entities: list[er.RegistryEntry]) -> None:
    registry = er.async_get(hass)
    for entity in entities:
        if entity.disabled_by is er.RegistryEntryDisabler.INTEGRATION:
            registry.async_update_entity_options(
                entity.entity_id, DOMAIN, {CONTROL_MARK: True}
            )
            registry.async_update_entity(entity.entity_id, disabled_by=None)


def _switch_off(*, hass: HomeAssistant, entities: list[er.RegistryEntry]) -> None:
    registry = er.async_get(hass)
    for entity in entities:
        if not _is_marked(entity=entity):
            continue
        _remove_mark(registry=registry, entity=entity)
        if entity.disabled_by is None:
            registry.async_update_entity(
                entity.entity_id, disabled_by=er.RegistryEntryDisabler.INTEGRATION
            )
