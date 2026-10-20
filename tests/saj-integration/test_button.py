from datetime import UTC, datetime

import pytest

from custom_components.saj_local import button
from custom_components.saj_local.saj.codec import Encoding
from custom_components.saj_local.saj.definitions import EntityKind
from tests.entities import FakeCoordinator, register_of


def _button(*, coordinator=None, **changes) -> button.SajButton:
    return button.SajButton(
        coordinator=coordinator or FakeCoordinator(),
        register=register_of(kind=EntityKind.BUTTON, **changes),
        prefix="",
    )


async def test_pressing_a_command_button_sends_no_value():
    coordinator = FakeCoordinator()

    await _button(coordinator=coordinator).async_press()

    coordinator.write.assert_awaited_once_with(key="test_row", value=None)


@pytest.mark.parametrize(
    "now",
    [
        datetime(2026, 3, 9, 14, 5, 59, tzinfo=UTC),
        datetime(2027, 12, 31, 23, 59, 0, tzinfo=UTC),
    ],
)
async def test_pressing_the_clock_button_sends_the_local_time_without_a_zone(
    monkeypatch, now
):
    class Zoned:
        def replace(self, *, tzinfo):
            assert tzinfo is None
            return now

    monkeypatch.setattr(button.dt_util, "now", Zoned)
    coordinator = FakeCoordinator()

    await _button(coordinator=coordinator, encoding=Encoding.CLOCK).async_press()

    coordinator.write.assert_awaited_once_with(key="test_row", value=now)


def test_a_button_is_a_disabled_configuration_command():
    built = _button(core=False)

    assert built.entity_registry_enabled_default is False
    assert built.entity_category == "config"
    assert built.entity_id == "button.saj_test_row"
