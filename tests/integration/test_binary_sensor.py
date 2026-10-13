import pytest
from homeassistant.components.binary_sensor import BinarySensorDeviceClass

from custom_components.saj_local.binary_sensor import SajBinarySensor
from custom_components.saj_local.saj.definitions import EntityKind
from tests.entities import FakeCoordinator, register_of


def _sensor(*, value=None) -> SajBinarySensor:
    return SajBinarySensor(
        coordinator=FakeCoordinator(values={"test_row": value}),
        register=register_of(kind=EntityKind.BINARY_SENSOR),
        prefix="",
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [(1, True), (0, False), (5, True), (None, None), ("x", None)],
)
def test_a_fault_is_on_when_the_derived_value_is_not_zero(value, expected):
    assert _sensor(value=value).is_on is expected


def test_a_fault_is_reported_as_a_problem():
    assert _sensor().device_class is BinarySensorDeviceClass.PROBLEM


def test_a_fault_is_unavailable_while_its_register_is_refused():
    sensor = _sensor(value=1)
    sensor.coordinator.unavailable_keys = frozenset({"test_row"})

    assert sensor.available is False
