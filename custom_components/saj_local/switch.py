from typing import Any

from homeassistant.components.switch import SwitchEntity

from .entity import SajEntity, platform_setup
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


async_setup_entry = platform_setup(kind=EntityKind.SWITCH, entity_class=SajSwitch)
