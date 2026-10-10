from typing import TYPE_CHECKING

from homeassistant.components.button import ButtonEntity
from homeassistant.util import dt as dt_util

from .entity import SajEntity, platform_setup
from .saj.codec import Encoding
from .saj.definitions import EntityKind

if TYPE_CHECKING:
    from datetime import datetime


class SajButton(SajEntity, ButtonEntity):
    async def async_press(self) -> None:
        await self.async_change(value=self._payload())

    def _payload(self) -> datetime | None:
        if self.register.encoding is Encoding.CLOCK:
            return dt_util.now().replace(tzinfo=None)
        return None


async_setup_entry = platform_setup(kind=EntityKind.BUTTON, entity_class=SajButton)
