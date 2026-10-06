from types import SimpleNamespace

import pytest
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import PERCENTAGE, UnitOfPower

from custom_components.saj_local import sensor
from custom_components.saj_local.const import DOMAIN
from custom_components.saj_local.saj.hs3 import Hs3Device, Hs3Telemetry

DEVICE = Hs3Device("HS3-TEST-001", 0x1610, 12000)


@pytest.fixture(autouse=True)
def _stub_coordinator_entity_constructor(monkeypatch):
    def construct_entity(self, coordinator, context=None):
        self.coordinator = coordinator
        self.coordinator_context = context

    monkeypatch.setattr(sensor.CoordinatorEntity, "__init__", construct_entity)


class FakeCoordinator:
    def __init__(self, data: Hs3Telemetry) -> None:
        self.device = DEVICE
        self.data = data
        self.entry_id = "logical-installation-123"

    def async_add_listener(self, _listener, context=None):
        del context
        return lambda: None


async def test_platform_creates_six_entities_from_entry_runtime():
    coordinator = FakeCoordinator(Hs3Telemetry(2, 2000, -100, 50, 0, 1500))
    entry = SimpleNamespace(runtime_data=SimpleNamespace(coordinator=coordinator))
    entities = []

    await sensor.async_setup_entry(None, entry, entities.extend)

    assert len(entities) == 6
    assert {entity.key for entity in entities} == {
        "operating_mode",
        "pv_power",
        "battery_power",
        "battery_soc",
        "grid_power",
        "load_power",
    }
    assert {entity.coordinator_context for entity in entities} == {
        entity.key for entity in entities
    }


def test_power_sensors_expose_native_power_measurements():
    coordinator = FakeCoordinator(Hs3Telemetry(pv_power=2000, battery_power=-500))
    solar = sensor.SajSensor(
        coordinator,
        sensor.SensorDescription("pv_power", SensorDeviceClass.POWER, UnitOfPower.WATT),
    )
    battery = sensor.SajSensor(
        coordinator,
        sensor.SensorDescription(
            "battery_power", SensorDeviceClass.POWER, UnitOfPower.WATT
        ),
    )

    assert solar.native_value == 2000
    assert solar._attr_native_unit_of_measurement == UnitOfPower.WATT
    assert solar._attr_state_class is SensorStateClass.MEASUREMENT
    assert battery.native_value == -500


def test_battery_charge_uses_percent_and_battery_class():
    coordinator = FakeCoordinator(Hs3Telemetry(battery_soc=84.25))
    entity = sensor.SajSensor(
        coordinator,
        sensor.SensorDescription("battery_soc", SensorDeviceClass.BATTERY, PERCENTAGE),
    )

    assert entity.native_value == 84.25
    assert entity._attr_native_unit_of_measurement == PERCENTAGE
    assert entity._attr_state_class is SensorStateClass.MEASUREMENT


def test_operating_mode_is_an_enum_with_translated_state_key():
    coordinator = FakeCoordinator(Hs3Telemetry(operating_mode=2))
    entity = sensor.SajSensor(
        coordinator, sensor.SensorDescription("operating_mode", SensorDeviceClass.ENUM)
    )

    assert entity._attr_device_class is SensorDeviceClass.ENUM
    assert "operating" in entity._attr_options
    assert entity.native_value == "operating"
    assert entity._attr_translation_key == "operating_mode"


def test_unknown_mode_has_unknown_sensor_state_and_stable_device_identity():
    coordinator = FakeCoordinator(Hs3Telemetry(operating_mode=27))
    entity = sensor.SajSensor(
        coordinator, sensor.SensorDescription("operating_mode", SensorDeviceClass.ENUM)
    )

    assert entity.native_value is None
    assert entity._attr_unique_id == "logical-installation-123_operating_mode"
    assert entity._attr_device_info["identifiers"] == {
        (DOMAIN, "logical-installation-123")
    }
    assert entity._attr_device_info["name"] == "SAJ"
    assert entity._attr_device_info["model"] == "HS3 (12000 W)"


def test_non_measurement_description_has_no_state_class():
    entity = sensor.SajSensor(
        FakeCoordinator(Hs3Telemetry()), sensor.SensorDescription("custom")
    )

    assert not hasattr(entity, "_attr_state_class")
