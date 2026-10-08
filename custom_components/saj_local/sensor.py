from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfPower
from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, sensor_unique_id
from .coordinator import SajCoordinator
from .saj.telemetry import (
    BATTERY_POWER,
    BATTERY_SOC,
    GRID_POWER,
    LOAD_POWER,
    OPERATING_MODE,
    OPERATING_MODE_NAMES,
    PV_POWER,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .saj.device import Device


@dataclass(frozen=True)
class SensorDescription:
    key: str
    device_class: SensorDeviceClass | None = None
    unit: str | None = None


_DESCRIPTIONS = (
    SensorDescription(key=OPERATING_MODE, device_class=SensorDeviceClass.ENUM),
    SensorDescription(
        key=PV_POWER, device_class=SensorDeviceClass.POWER, unit=UnitOfPower.WATT
    ),
    SensorDescription(
        key=BATTERY_POWER, device_class=SensorDeviceClass.POWER, unit=UnitOfPower.WATT
    ),
    SensorDescription(
        key=BATTERY_SOC, device_class=SensorDeviceClass.BATTERY, unit=PERCENTAGE
    ),
    SensorDescription(
        key=GRID_POWER, device_class=SensorDeviceClass.POWER, unit=UnitOfPower.WATT
    ),
    SensorDescription(
        key=LOAD_POWER, device_class=SensorDeviceClass.POWER, unit=UnitOfPower.WATT
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    del hass
    coordinator: SajCoordinator = entry.runtime_data.coordinator
    supported_keys = coordinator.device.profile.measurement_keys
    async_add_entities(
        SajSensor(coordinator=coordinator, description=description)
        for description in _DESCRIPTIONS
        if description.key in supported_keys
    )


def _model_name(*, device: Device) -> str:
    qualifier = "" if device.detected else ", unverified"
    return f"{device.profile.display_name} ({device.rated_power} W{qualifier})"


class SajSensor(CoordinatorEntity[SajCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(
        self, coordinator: SajCoordinator, description: SensorDescription
    ) -> None:
        super().__init__(coordinator=coordinator, context=description.key)
        self.key = description.key
        self._written_available: bool | None = None
        self._attr_translation_key = description.key
        self._attr_unique_id = sensor_unique_id(
            entry_id=coordinator.entry_id, key=description.key
        )
        self._attr_device_class = description.device_class
        self._attr_native_unit_of_measurement = description.unit
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry_id)},
            name="SAJ",
            manufacturer="SAJ",
            model=_model_name(device=coordinator.device),
            serial_number=coordinator.device.serial,
        )
        if description.key == OPERATING_MODE:
            self._attr_options = list(OPERATING_MODE_NAMES.values())
        elif description.device_class is not None:
            self._attr_state_class = SensorStateClass.MEASUREMENT

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

    @property
    def native_value(self) -> int | float | str | None:
        value = self.coordinator.data.get(key=self.key)
        if self.key == OPERATING_MODE and value is not None:
            return OPERATING_MODE_NAMES.get(int(value))
        return value
