from datetime import time

import pytest
from homeassistant.exceptions import HomeAssistantError

from custom_components.saj_local.const import DOMAIN
from custom_components.saj_local.saj.definitions import EntityKind
from custom_components.saj_local.time import SajTime
from tests.entities import FakeCoordinator, register_of


def _time_entity(*, value=None, coordinator=None) -> SajTime:
    return SajTime(
        coordinator=coordinator or FakeCoordinator(values={"test_row": value}),
        register=register_of(kind=EntityKind.TIME),
        prefix="",
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [(time(6, 30), time(6, 30)), (None, None), (630, None)],
)
def test_a_time_shows_the_time_of_day_read(value, expected):
    assert _time_entity(value=value).native_value == expected


@pytest.mark.parametrize("requested", [time(0, 0), time(23, 59)])
async def test_changing_a_time_is_refused_and_no_request_is_sent(requested):
    coordinator = FakeCoordinator(values={"test_row": time(6, 30)})

    with pytest.raises(HomeAssistantError) as refusal:
        await _time_entity(coordinator=coordinator).async_set_value(requested)

    assert refusal.value.translation_domain == DOMAIN
    assert refusal.value.translation_key == "control_not_enabled"
    assert coordinator.requests_sent() == 0
