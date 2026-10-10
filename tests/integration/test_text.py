import pytest
from homeassistant.exceptions import HomeAssistantError

from custom_components.saj_local.const import DOMAIN
from custom_components.saj_local.saj.definitions import EntityKind
from custom_components.saj_local.text import SajText
from tests.entities import FakeCoordinator, register_of


def _text(*, value=None, coordinator=None, **changes) -> SajText:
    return SajText(
        coordinator=coordinator or FakeCoordinator(values={"test_row": value}),
        register=register_of(kind=EntityKind.TEXT, **changes),
        prefix="",
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [("192.168.1.20", "192.168.1.20"), (None, None), (5, None)],
)
def test_a_text_shows_the_text_read(value, expected):
    assert _text(value=value).native_value == expected


@pytest.mark.parametrize(("words", "longest"), [(8, 16), (2, 4)])
def test_a_text_is_as_long_as_its_registers_can_hold(words, longest):
    assert _text(words=words).native_max == longest


@pytest.mark.parametrize("requested", ["", "10.0.0.1"])
async def test_changing_a_text_is_refused_and_no_request_is_sent(requested):
    coordinator = FakeCoordinator(values={"test_row": "192.168.1.20"})

    with pytest.raises(HomeAssistantError) as refusal:
        await _text(coordinator=coordinator).async_set_value(requested)

    assert refusal.value.translation_domain == DOMAIN
    assert refusal.value.translation_key == "control_not_enabled"
    assert coordinator.requests_sent() == 0
