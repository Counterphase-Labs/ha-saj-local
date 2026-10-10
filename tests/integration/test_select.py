import pytest
from homeassistant.exceptions import HomeAssistantError

from custom_components.saj_local.const import DOMAIN
from custom_components.saj_local.saj.definitions import EntityKind
from custom_components.saj_local.select import SajSelect
from tests.entities import FakeCoordinator, register_of

OPTIONS = {0: "first", 1: "second", 5: "sixth"}


def _select(*, value=None, coordinator=None) -> SajSelect:
    return SajSelect(
        coordinator=coordinator or FakeCoordinator(values={"test_row": value}),
        register=register_of(kind=EntityKind.SELECT, options=OPTIONS),
        prefix="",
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [(0, "first"), (5, "sixth"), (1.0, "second"), (3, None), (None, None), ("x", None)],
)
def test_a_select_shows_the_name_of_the_code_read_and_unknown_for_no_name(
    value, expected
):
    assert _select(value=value).current_option == expected


def test_a_select_offers_its_named_options():
    assert _select().options == ["first", "second", "sixth"]


@pytest.mark.parametrize("option", ["first", "sixth", "not an option"])
async def test_changing_a_select_is_refused_and_no_request_is_sent(option):
    coordinator = FakeCoordinator(values={"test_row": 0})

    with pytest.raises(HomeAssistantError) as refusal:
        await _select(coordinator=coordinator).async_select_option(option)

    assert refusal.value.translation_domain == DOMAIN
    assert refusal.value.translation_key == "control_not_enabled"
    assert coordinator.requests_sent() == 0
