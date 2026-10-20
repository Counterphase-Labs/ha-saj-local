import pytest

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


@pytest.mark.parametrize(
    ("action", "sent"), [("async_turn_on", 1), ("async_turn_off", 0)]
)
async def test_turning_a_switch_sends_one_or_zero_to_the_coordinator(action, sent):
    coordinator = FakeCoordinator(values={"test_row": 1})

    await getattr(_switch(coordinator=coordinator), action)()

    coordinator.write.assert_awaited_once_with(key="test_row", value=sent)
