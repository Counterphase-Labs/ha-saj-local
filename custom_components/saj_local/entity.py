import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorStateClass
from homeassistant.const import EntityCategory
from homeassistant.core import callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_PREFIX,
    DOMAIN,
    entity_id_in_use,
    entity_unique_id,
    fixed_entity_id,
    object_id,
)
from .coordinator import SajCoordinator
from .saj.catalogue import device_registers
from .saj.definitions import Quantity

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Mapping

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .saj.catalogue import Register
    from .saj.codec import Value
    from .saj.definitions import EntityKind
    from .saj.device import Device

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class Presentation:
    device_class: str | None = None
    state_class: SensorStateClass | None = None


def _measurement(*, device_class: str | None = None) -> Presentation:
    return Presentation(
        device_class=device_class, state_class=SensorStateClass.MEASUREMENT
    )


PRESENTATIONS: Mapping[Quantity, Presentation] = {
    Quantity.POWER: _measurement(device_class="power"),
    Quantity.APPARENT_POWER: _measurement(device_class="apparent_power"),
    Quantity.REACTIVE_POWER: _measurement(device_class="reactive_power"),
    Quantity.VOLTAGE: _measurement(device_class="voltage"),
    Quantity.CURRENT: _measurement(device_class="current"),
    Quantity.FREQUENCY: _measurement(device_class="frequency"),
    Quantity.POWER_FACTOR: _measurement(device_class="power_factor"),
    Quantity.TEMPERATURE: _measurement(device_class="temperature"),
    Quantity.DURATION: _measurement(device_class="duration"),
    Quantity.STATE_OF_CHARGE: _measurement(device_class="battery"),
    Quantity.PERCENTAGE: _measurement(),
    Quantity.RESISTANCE: _measurement(),
    Quantity.CAPACITY: _measurement(),
    Quantity.ENERGY: Presentation(
        device_class="energy", state_class=SensorStateClass.TOTAL_INCREASING
    ),
}
NO_PRESENTATION = Presentation()


def presentation_of(*, register: Register) -> Presentation:
    return PRESENTATIONS.get(register.quantity, NO_PRESENTATION)


def model_name(*, device: Device) -> str:
    qualifier = "" if device.detected else ", unverified"
    return f"{device.profile.display_name} ({device.rated_power} W{qualifier})"


class SajEntity(CoordinatorEntity[SajCoordinator]):
    _attr_has_entity_name = True

    def __init__(
        self, *, coordinator: SajCoordinator, register: Register, prefix: str
    ) -> None:
        super().__init__(coordinator=coordinator, context=register.key)
        self.key = register.key
        self.register = register
        self.entity_id = fixed_entity_id(
            domain=register.kind, prefix=prefix, key=register.key
        )
        self._written_available: bool | None = None
        self._attr_translation_key = register.key
        self._attr_unique_id = entity_unique_id(
            entry_id=coordinator.entry_id, key=register.key
        )
        self._attr_entity_registry_enabled_default = register.core
        category = register.definition.category
        self._attr_entity_category = (
            None if category is None else EntityCategory(category.value)
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry_id)},
            name="SAJ",
            manufacturer="SAJ",
            model=model_name(device=coordinator.device),
            serial_number=coordinator.device.serial,
        )

    @property
    def read_value(self) -> Value:
        return self.coordinator.data.get(key=self.key)

    @property
    def available(self) -> bool:
        return super().available and self.key not in self.coordinator.unavailable_keys

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self._written_available = self.available

    @callback
    def _handle_coordinator_update(self) -> None:
        if self.key in self.coordinator.last_read or (
            self.available != self._written_available
        ):
            self._written_available = self.available
            self.async_write_ha_state()


def add_entities(
    *,
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
    kind: EntityKind,
    entity_class: type[SajEntity],
) -> None:
    coordinator: SajCoordinator = entry.runtime_data.coordinator
    prefix: str = entry.options.get(CONF_PREFIX, "")
    registers = [
        register
        for register in device_registers(
            profile=coordinator.device.profile,
            device_type=coordinator.device.device_type,
        )
        if register.kind is kind
    ]
    _warn_about_displaced_entities(
        hass=hass,
        entry_id=coordinator.entry_id,
        prefix=prefix,
        kind=kind,
        keys=[register.key for register in registers],
    )
    async_add_entities(
        entity_class(coordinator=coordinator, register=register, prefix=prefix)
        for register in registers
    )


def platform_setup(
    *, kind: EntityKind, entity_class: type[SajEntity]
) -> Callable[[HomeAssistant, ConfigEntry, AddEntitiesCallback], Awaitable[None]]:
    async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
    ) -> None:
        add_entities(
            hass=hass,
            entry=entry,
            async_add_entities=async_add_entities,
            kind=kind,
            entity_class=entity_class,
        )

    return async_setup_entry


def _warn_about_displaced_entities(
    *,
    hass: HomeAssistant,
    entry_id: str,
    prefix: str,
    kind: EntityKind,
    keys: list[str],
) -> None:
    registry = er.async_get(hass)
    for key in keys:
        is_new = (
            registry.async_get_entity_id(
                kind, DOMAIN, entity_unique_id(entry_id=entry_id, key=key)
            )
            is None
        )
        wanted = fixed_entity_id(domain=kind, prefix=prefix, key=key)
        if is_new and entity_id_in_use(hass=hass, entity_id=wanted):
            _LOGGER.warning(
                "Entity ID %s is taken, so %s %s is registered as %s",
                wanted,
                kind,
                key,
                registry.async_get_available_entity_id(
                    kind, object_id(prefix=prefix, key=key)
                ),
            )
