from typing import TYPE_CHECKING

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberMode,
)
from homeassistant.const import UnitOfPower

from .entity import (
    PowerPlatform,
    SajEntity,
    SajPowerEntity,
    platform_setup,
    presentation_of,
)
from .saj.definitions import Access, EntityKind

POWER_STEP = 1

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
        self._attr_assumed_state = register.access is Access.WRITE_ONLY
        settable = register.definition.settable_range
        if settable is not None:
            self._attr_native_min_value = settable.minimum
            self._attr_native_max_value = settable.maximum

    @property
    def native_value(self) -> float | None:
        value = self.read_value
        return value if isinstance(value, int | float) else None

    async def async_set_native_value(self, value: float) -> None:
        await self.async_change(value=value)


class SajPowerNumber(SajPowerEntity, NumberEntity):
    _attr_mode = NumberMode.BOX
    _attr_device_class = NumberDeviceClass.POWER
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_native_step = POWER_STEP

    @property
    def native_min_value(self) -> float:
        return self.coordinator.power_range(function=self.function).minimum

    @property
    def native_max_value(self) -> float:
        return self.coordinator.power_range(function=self.function).maximum

    @property
    def native_value(self) -> float | None:
        return self.coordinator.power_target_shown(function=self.function)

    async def async_set_native_value(self, value: float) -> None:
        await self.async_run(
            action=self.coordinator.async_set_power_target(
                function=self.function, raw=value
            )
        )


async_setup_entry = platform_setup(
    kind=EntityKind.NUMBER,
    entity_class=SajNumber,
    power=PowerPlatform(
        kind=EntityKind.NUMBER,
        entity_class=SajPowerNumber,
        key_of=lambda function: function.target_key,
    ),
)
