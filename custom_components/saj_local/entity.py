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
    FUNCTION_SELECTOR,
    entity_id_in_use,
    entity_unique_id,
    fixed_entity_id,
    object_id,
    selector_options,
)
from .coordinator import SajCoordinator
from .errors import WRITE_ERRORS, write_failure
from .saj.catalogue import device_registers
from .saj.definitions import Access, Quantity

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Mapping

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .saj.catalogue import Register
    from .saj.codec import Value
    from .saj.definitions import EntityKind
    from .saj.device import Device
    from .saj.models import PowerFunction

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


@dataclass(frozen=True)
class EntityIdentity:
    domain: str
    key: str
    prefix: str


class SajBaseEntity(CoordinatorEntity[SajCoordinator]):
    _attr_has_entity_name = True

    def __init__(
        self,
        *,
        coordinator: SajCoordinator,
        identity: EntityIdentity,
        category: EntityCategory | None,
        enabled_default: bool,
    ) -> None:
        key = identity.key
        super().__init__(coordinator=coordinator, context=key)
        self.key = key
        self.entity_id = fixed_entity_id(
            domain=identity.domain, prefix=identity.prefix, key=key
        )
        self._attr_translation_key = key
        self._attr_unique_id = entity_unique_id(entry_id=coordinator.entry_id, key=key)
        self._attr_entity_registry_enabled_default = enabled_default
        self._attr_entity_category = category
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry_id)},
            name="SAJ",
            manufacturer="SAJ",
            model=model_name(device=coordinator.device),
            serial_number=coordinator.device.serial,
        )


class SajEntity(SajBaseEntity):
    def __init__(
        self, *, coordinator: SajCoordinator, register: Register, prefix: str
    ) -> None:
        category = register.definition.category
        super().__init__(
            coordinator=coordinator,
            identity=EntityIdentity(
                domain=register.kind, key=register.key, prefix=prefix
            ),
            category=None if category is None else EntityCategory(category.value),
            enabled_default=register.core,
        )
        self.register = register
        self._written_available: bool | None = None

    @property
    def read_value(self) -> Value:
        if self.register.access is Access.WRITE_ONLY:
            return self.coordinator.assumed.get(self.key)
        return self.coordinator.data.get(key=self.key)

    async def async_change(self, *, value: Value) -> None:
        try:
            await self.coordinator.write(key=self.key, value=value)
        except WRITE_ERRORS as error:
            raise write_failure(error=error) from error

    @property
    def available(self) -> bool:
        return super().available and self.key not in self.coordinator.unavailable_keys

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self._written_available = self.available

    @callback
    def _handle_coordinator_update(self) -> None:
        if (
            self.key in self.coordinator.last_read
            or self.key in self.coordinator.changed_keys
            or self.available != self._written_available
        ):
            self._written_available = self.available
            self.async_write_ha_state()


class SajPowerEntity(SajBaseEntity):
    def __init__(
        self,
        *,
        coordinator: SajCoordinator,
        function: PowerFunction,
        identity: EntityIdentity,
    ) -> None:
        super().__init__(
            coordinator=coordinator,
            identity=identity,
            category=EntityCategory.CONFIG,
            enabled_default=False,
        )
        self.function = function

    async def async_run(self, *, action: Awaitable[None]) -> None:
        try:
            await action
        except WRITE_ERRORS as error:
            names = await selector_options(
                hass=self.hass, selector_name=FUNCTION_SELECTOR
            )
            raise write_failure(error=error, function_names=names) from error


@dataclass(frozen=True)
class PowerPlatform:
    kind: EntityKind
    entity_class: type[SajPowerEntity]
    key_of: Callable[[PowerFunction], str]


def add_power_entities(
    *,
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
    platform: PowerPlatform,
) -> None:
    coordinator: SajCoordinator = entry.runtime_data.coordinator
    prefix: str = entry.options.get(CONF_PREFIX, "")
    keys = {
        function: platform.key_of(function) for function in coordinator.power_offered
    }
    if not keys:
        return
    _warn_about_displaced_entities(
        hass=hass,
        entry_id=coordinator.entry_id,
        prefix=prefix,
        kind=platform.kind,
        keys=list(keys.values()),
    )
    async_add_entities(
        platform.entity_class(
            coordinator=coordinator,
            function=function,
            identity=EntityIdentity(domain=platform.kind, key=key, prefix=prefix),
        )
        for function, key in keys.items()
    )


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
        for register in device_registers(fit=coordinator.device.fit)
        if register.kind is kind and register.exposed
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
    *,
    kind: EntityKind,
    entity_class: type[SajEntity],
    power: PowerPlatform | None = None,
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
        if power is not None:
            add_power_entities(
                hass=hass,
                entry=entry,
                async_add_entities=async_add_entities,
                platform=power,
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
