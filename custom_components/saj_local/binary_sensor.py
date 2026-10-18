from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.const import EntityCategory

from .const import CONF_PREFIX
from .entity import EntityIdentity, SajBaseEntity, SajEntity, platform_setup
from .saj.definitions import EntityKind

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import SajCoordinator

CONTROL_ALLOWED_KEY = "control_allowed"


class SajBinarySensor(SajEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self) -> bool | None:
        value = self.read_value
        return bool(value) if isinstance(value, int | float) else None


class SajControlAllowedSensor(SajBaseEntity, BinarySensorEntity):
    def __init__(self, *, coordinator: SajCoordinator, prefix: str) -> None:
        super().__init__(
            coordinator=coordinator,
            identity=EntityIdentity(
                domain=EntityKind.BINARY_SENSOR, key=CONTROL_ALLOWED_KEY, prefix=prefix
            ),
            category=EntityCategory.DIAGNOSTIC,
            enabled_default=True,
        )

    @property
    def is_on(self) -> bool:
        return self.coordinator.control_allowed


register_sensors = platform_setup(
    kind=EntityKind.BINARY_SENSOR, entity_class=SajBinarySensor
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    await register_sensors(hass, entry, async_add_entities)
    async_add_entities(
        [
            SajControlAllowedSensor(
                coordinator=entry.runtime_data.coordinator,
                prefix=entry.options.get(CONF_PREFIX, ""),
            )
        ]
    )
