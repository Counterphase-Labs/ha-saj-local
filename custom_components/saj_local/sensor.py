from datetime import datetime
from typing import TYPE_CHECKING

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.util import dt as dt_util

from .entity import SajEntity, platform_setup, presentation_of
from .saj.codec import option_name
from .saj.definitions import EntityKind, Quantity

if TYPE_CHECKING:
    from .coordinator import SajCoordinator
    from .saj.catalogue import Register


class SajSensor(SajEntity, SensorEntity):
    def __init__(
        self, *, coordinator: SajCoordinator, register: Register, prefix: str
    ) -> None:
        super().__init__(coordinator=coordinator, register=register, prefix=prefix)
        presentation = presentation_of(register=register)
        if register.options is not None:
            self._attr_device_class = SensorDeviceClass.ENUM
            self._attr_options = list(register.options.values())
        elif register.quantity is Quantity.TIMESTAMP:
            self._attr_device_class = SensorDeviceClass.TIMESTAMP
        else:
            self._attr_device_class = (
                None
                if presentation.device_class is None
                else SensorDeviceClass(presentation.device_class)
            )
            self._attr_state_class = presentation.state_class
            self._attr_native_unit_of_measurement = (
                None if register.unit is None else register.unit.value
            )

    @property
    def native_value(self) -> int | float | str | datetime | None:
        value = self.read_value
        if self.register.options is not None:
            if not isinstance(value, int | float):
                return None
            return option_name(code=value, options=self.register.options)
        if isinstance(value, datetime) and value.tzinfo is None:
            return value.replace(tzinfo=dt_util.get_default_time_zone())
        if isinstance(value, int | float | str | datetime):
            return value
        return None


async_setup_entry = platform_setup(kind=EntityKind.SENSOR, entity_class=SajSensor)
