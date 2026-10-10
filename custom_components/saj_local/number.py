from typing import TYPE_CHECKING

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberMode,
)

from .entity import SajEntity, platform_setup, presentation_of
from .errors import control_not_enabled
from .saj.definitions import EntityKind

if TYPE_CHECKING:
    from .coordinator import SajCoordinator
    from .saj.catalogue import Register


class SajNumber(SajEntity, NumberEntity):
    _attr_mode = NumberMode.BOX

    def __init__(
        self, *, coordinator: SajCoordinator, register: Register, prefix: str
    ) -> None:
        super().__init__(coordinator=coordinator, register=register, prefix=prefix)
        device_class = presentation_of(register=register).device_class
        self._attr_device_class = (
            None if device_class is None else NumberDeviceClass(device_class)
        )
        self._attr_native_unit_of_measurement = (
            None if register.unit is None else register.unit.value
        )
        self._attr_native_step = register.scale
        settable = register.definition.settable_range
        if settable is not None:
            self._attr_native_min_value = settable.minimum
            self._attr_native_max_value = settable.maximum

    @property
    def native_value(self) -> float | None:
        value = self.read_value
        return value if isinstance(value, int | float) else None

    async def async_set_native_value(self, value: float) -> None:
        del value
        raise control_not_enabled()


async_setup_entry = platform_setup(kind=EntityKind.NUMBER, entity_class=SajNumber)
