from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)

from .entity import SajEntity, platform_setup
from .saj.definitions import EntityKind


class SajBinarySensor(SajEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self) -> bool | None:
        value = self.read_value
        return bool(value) if isinstance(value, int | float) else None


async_setup_entry = platform_setup(
    kind=EntityKind.BINARY_SENSOR, entity_class=SajBinarySensor
)
