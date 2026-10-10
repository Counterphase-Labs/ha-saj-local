from typing import TYPE_CHECKING

from homeassistant.components.select import SelectEntity

from .entity import SajEntity, platform_setup
from .errors import control_not_enabled
from .saj.codec import option_name
from .saj.definitions import EntityKind

if TYPE_CHECKING:
    from .coordinator import SajCoordinator
    from .saj.catalogue import Register


class SajSelect(SajEntity, SelectEntity):
    def __init__(
        self, *, coordinator: SajCoordinator, register: Register, prefix: str
    ) -> None:
        super().__init__(coordinator=coordinator, register=register, prefix=prefix)
        self._options_by_code = dict(register.options or {})
        self._attr_options = list(self._options_by_code.values())

    @property
    def current_option(self) -> str | None:
        value = self.read_value
        if not isinstance(value, int | float):
            return None
        return option_name(code=value, options=self._options_by_code)

    async def async_select_option(self, option: str) -> None:
        del option
        raise control_not_enabled()


async_setup_entry = platform_setup(kind=EntityKind.SELECT, entity_class=SajSelect)
