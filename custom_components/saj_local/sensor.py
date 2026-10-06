from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfPower
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SajCoordinator
from .saj.hs3 import MODE_NAMES

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback


@dataclass(frozen=True)
class SensorDescription:
    key: str
    device_class: SensorDeviceClass | None = None
    unit: str | None = None


_DESCRIPTIONS = (
    SensorDescription(key="operating_mode", device_class=SensorDeviceClass.ENUM),
    SensorDescription(
        key="pv_power", device_class=SensorDeviceClass.POWER, unit=UnitOfPower.WATT
    ),
    SensorDescription(
        key="battery_power", device_class=SensorDeviceClass.POWER, unit=UnitOfPower.WATT
    ),
    SensorDescription(
        key="battery_soc", device_class=SensorDeviceClass.BATTERY, unit=PERCENTAGE
    ),
    SensorDescription(
        key="grid_power", device_class=SensorDeviceClass.POWER, unit=UnitOfPower.WATT
    ),
    SensorDescription(
        key="load_power", device_class=SensorDeviceClass.POWER, unit=UnitOfPower.WATT
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    del hass
    coordinator: SajCoordinator = entry.runtime_data.coordinator
    async_add_entities(
        SajSensor(coordinator=coordinator, description=description)
        for description in _DESCRIPTIONS
    )


class SajSensor(CoordinatorEntity[SajCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(
        self, coordinator: SajCoordinator, description: SensorDescription
    ) -> None:
        super().__init__(coordinator=coordinator, context=description.key)
        self.key = description.key
        self._attr_translation_key = description.key
        self._attr_unique_id = f"{coordinator.entry_id}_{description.key}"
        self._attr_device_class = description.device_class
        self._attr_native_unit_of_measurement = description.unit
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry_id)},
            name="SAJ",
            manufacturer="SAJ",
            model=f"HS3 ({coordinator.device.rated_power} W)",
            serial_number=coordinator.device.serial,
        )
        if description.key == "operating_mode":
            self._attr_options = list(MODE_NAMES.values())
        elif description.device_class is not None:
            self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int | float | str | None:
        value = getattr(self.coordinator.data, self.key)
        if self.key == "operating_mode" and value is not None:
            return MODE_NAMES.get(value)
        return value
