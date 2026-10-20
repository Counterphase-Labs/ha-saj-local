import pytest

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


@pytest.mark.parametrize(("option", "code"), [("first", 0), ("sixth", 5)])
async def test_choosing_an_option_sends_its_code_to_the_coordinator(option, code):
    coordinator = FakeCoordinator(values={"test_row": 0})

    await _select(coordinator=coordinator).async_select_option(option)

    coordinator.write.assert_awaited_once_with(key="test_row", value=code)
