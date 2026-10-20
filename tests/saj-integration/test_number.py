import pytest
from homeassistant.components.number import NumberDeviceClass, NumberMode

from custom_components.saj_local.number import SajNumber
from custom_components.saj_local.saj.codec import Encoding, Range
from custom_components.saj_local.saj.definitions import (
    Access,
    EntityKind,
    Quantity,
    Unit,
)
from tests.entities import FakeCoordinator, register_of

LIMITS = Range(minimum=10, maximum=90)


def _number(*, value=None, coordinator=None, **changes) -> SajNumber:
    return SajNumber(
        coordinator=coordinator or FakeCoordinator(values={"test_row": value}),
        register=register_of(kind=EntityKind.NUMBER, **changes),
        prefix="",
    )


@pytest.mark.parametrize("value", [10, 50.5, 90])
def test_a_number_shows_the_value_as_read(value):
    assert _number(value=value, range=LIMITS).native_value == value


@pytest.mark.parametrize("value", [0, 5, 91, 65535, -1])
def test_a_number_outside_its_range_still_shows_the_value_as_read(value):
    assert _number(value=value, range=LIMITS).native_value == value


@pytest.mark.parametrize("value", [None, "text"])
def test_a_number_without_a_numeric_reading_is_unknown(value):
    assert _number(value=value, range=LIMITS).native_value is None


def test_the_range_limits_what_can_be_set():
    built = _number(range=LIMITS, scale=0.5)

    assert (built.native_min_value, built.native_max_value) == (10, 90)
    assert built.native_step == 0.5
    assert built.mode is NumberMode.BOX


@pytest.mark.parametrize(
    ("encoding", "scale", "lowest", "highest"),
    [
        (Encoding.U16, 1, 0, 65535),
        (Encoding.I16, 1, -32768, 32767),
        (Encoding.U16, 0.1, 0, 6553.5),
        (Encoding.U32, 1, 0, 4294967295),
        (Encoding.I32, 1, -2147483648, 2147483647),
    ],
)
def test_a_number_without_a_documented_range_may_be_set_across_its_encoding(
    encoding, scale, lowest, highest
):
    built = _number(range=None, encoding=encoding, scale=scale)

    assert (built.native_min_value, built.native_max_value) == (lowest, highest)


def test_a_number_that_is_not_numeric_keeps_the_default_limits():
    built = _number(range=None, encoding=Encoding.TIME_OF_DAY)

    assert (built.native_min_value, built.native_max_value) == (0, 100)


def test_a_number_takes_its_unit_and_device_class_from_its_quantity():
    built = _number(range=LIMITS, quantity=Quantity.POWER, unit=Unit.WATT)

    assert built.native_unit_of_measurement == "W"
    assert built.device_class is NumberDeviceClass.POWER


def test_a_number_without_a_quantity_class_or_unit_has_neither():
    built = _number(range=LIMITS)

    assert built.native_unit_of_measurement is None
    assert built.device_class is None


@pytest.mark.parametrize("value", [0, 50.5, 1000])
async def test_changing_a_number_sends_the_value_to_the_coordinator(value):
    coordinator = FakeCoordinator(values={"test_row": 50})

    await _number(coordinator=coordinator, range=LIMITS).async_set_native_value(value)

    coordinator.write.assert_awaited_once_with(key="test_row", value=value)


def test_a_write_only_number_is_unknown_until_something_is_sent_then_assumed():
    coordinator = FakeCoordinator()
    built = _number(coordinator=coordinator, range=LIMITS, access=Access.WRITE_ONLY)

    assert built.assumed_state is True
    assert built.native_value is None

    coordinator.assumed["test_row"] = 42.5

    assert built.native_value == 42.5


def test_a_number_that_is_read_does_not_claim_an_assumed_state():
    assert _number(value=5, range=LIMITS).assumed_state is False


def test_a_write_only_number_ignores_the_snapshot_of_readings():
    coordinator = FakeCoordinator(values={"test_row": 99})

    built = _number(coordinator=coordinator, range=LIMITS, access=Access.WRITE_ONLY)

    assert built.native_value is None
