from typing import TYPE_CHECKING

from homeassistant.components.text import TextEntity

from .entity import SajEntity, platform_setup
from .errors import control_not_enabled
from .saj.definitions import EntityKind

if TYPE_CHECKING:
    from .coordinator import SajCoordinator
    from .saj.catalogue import Register

CHARACTERS_PER_WORD = 2


class SajText(SajEntity, TextEntity):
    def __init__(
        self, *, coordinator: SajCoordinator, register: Register, prefix: str
    ) -> None:
        super().__init__(coordinator=coordinator, register=register, prefix=prefix)
        self._attr_native_max = register.words * CHARACTERS_PER_WORD

    @property
    def native_value(self) -> str | None:
        value = self.read_value
        return value if isinstance(value, str) else None

    async def async_set_value(self, value: str) -> None:
        del value
        raise control_not_enabled()


async_setup_entry = platform_setup(kind=EntityKind.TEXT, entity_class=SajText)
