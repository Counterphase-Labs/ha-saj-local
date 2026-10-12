from typing import Any

from homeassistant.components.switch import SwitchEntity

from .entity import (
    PowerPlatform,
    SajEntity,
    SajPowerEntity,
    platform_setup,
)
from .saj.definitions import EntityKind


class SajSwitch(SajEntity, SwitchEntity):
    @property
    def is_on(self) -> bool | None:
        value = self.read_value
        return bool(value) if isinstance(value, int | float) else None

    async def async_turn_on(self, **kwargs: Any) -> None:
        del kwargs
        await self.async_change(value=1)

    async def async_turn_off(self, **kwargs: Any) -> None:
        del kwargs
        await self.async_change(value=0)


class SajPowerSwitch(SajPowerEntity, SwitchEntity):
    @property
    def is_on(self) -> bool | None:
        return self.coordinator.power_running(function=self.function)

    async def async_turn_on(self, **kwargs: Any) -> None:
        del kwargs
        await self.async_run(
            action=self.coordinator.async_power_on(function=self.function)
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        del kwargs
        await self.async_run(
            action=self.coordinator.async_power_off(function=self.function)
        )


async_setup_entry = platform_setup(
    kind=EntityKind.SWITCH,
    entity_class=SajSwitch,
    power=PowerPlatform(
        kind=EntityKind.SWITCH,
        entity_class=SajPowerSwitch,
        key_of=lambda function: function.switch_key,
    ),
)
