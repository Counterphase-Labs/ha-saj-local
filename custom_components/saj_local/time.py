from datetime import time

from homeassistant.components.time import TimeEntity

from .entity import SajEntity, platform_setup
from .errors import control_not_enabled
from .saj.definitions import EntityKind


class SajTime(SajEntity, TimeEntity):
    @property
    def native_value(self) -> time | None:
        value = self.read_value
        return value if isinstance(value, time) else None

    async def async_set_value(self, value: time) -> None:
        del value
        raise control_not_enabled()


async_setup_entry = platform_setup(kind=EntityKind.TIME, entity_class=SajTime)
