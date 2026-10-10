import pytest
from homeassistant.exceptions import HomeAssistantError

from custom_components.saj_local.const import DOMAIN
from custom_components.saj_local.saj.definitions import EntityKind
from custom_components.saj_local.switch import SajSwitch
from tests.entities import FakeCoordinator, register_of


def _switch(*, value=None, coordinator=None) -> SajSwitch:
    return SajSwitch(
        coordinator=coordinator or FakeCoordinator(values={"test_row": value}),
        register=register_of(kind=EntityKind.SWITCH),
        prefix="",
    )


@pytest.mark.parametrize(
    ("value", "expected"), [(1, True), (0, False), (None, None), ("x", None)]
)
def test_a_switch_shows_whether_the_value_read_is_on(value, expected):
    assert _switch(value=value).is_on is expected


@pytest.mark.parametrize("action", ["async_turn_on", "async_turn_off"])
async def test_changing_a_switch_is_refused_and_no_request_is_sent(action):
    coordinator = FakeCoordinator(values={"test_row": 1})

    with pytest.raises(HomeAssistantError) as refusal:
        await getattr(_switch(coordinator=coordinator), action)()

    assert refusal.value.translation_domain == DOMAIN
    assert refusal.value.translation_key == "control_not_enabled"
    assert coordinator.requests_sent() == 0
