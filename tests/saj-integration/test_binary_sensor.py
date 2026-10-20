from types import SimpleNamespace

import pytest
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.const import EntityCategory

from custom_components.saj_local import binary_sensor
from custom_components.saj_local.binary_sensor import (
    SajBinarySensor,
    SajControlAllowedSensor,
)
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


@pytest.mark.parametrize("allowed", [True, False])
def test_control_allowed_follows_the_coordinator(allowed):
    coordinator = FakeCoordinator()
    coordinator.control_allowed = allowed

    sensor = SajControlAllowedSensor(coordinator=coordinator, prefix="")

    assert sensor.is_on is allowed


def test_control_allowed_is_a_diagnostic_entity_enabled_by_default():
    sensor = SajControlAllowedSensor(coordinator=FakeCoordinator(), prefix="roof")

    assert sensor.entity_category is EntityCategory.DIAGNOSTIC
    assert sensor.entity_registry_enabled_default is True
    assert sensor.entity_id == "binary_sensor.saj_roof_control_allowed"
    assert sensor.translation_key == "control_allowed"


async def test_the_platform_adds_the_register_sensors_and_control_allowed(monkeypatch):
    added = []
    registered = []

    async def register_sensors(hass, entry, async_add_entities):
        registered.append((hass, entry, async_add_entities))

    monkeypatch.setattr(binary_sensor, "register_sensors", register_sensors)
    entry = SimpleNamespace(
        runtime_data=SimpleNamespace(coordinator=FakeCoordinator()),
        options={"prefix": "roof"},
    )
    hass = object()

    await binary_sensor.async_setup_entry(hass, entry, added.append)

    assert registered == [(hass, entry, added.append)]
    (entities,) = added
    assert [type(entity) for entity in entities] == [SajControlAllowedSensor]
    assert entities[0].entity_id == "binary_sensor.saj_roof_control_allowed"
