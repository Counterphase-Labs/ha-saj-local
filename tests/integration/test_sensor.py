from types import SimpleNamespace

import pytest
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import PERCENTAGE, UnitOfPower

from custom_components.saj_local import sensor
from custom_components.saj_local.const import DOMAIN
from custom_components.saj_local.saj.device import Device
from custom_components.saj_local.saj.profiles import Profile
from custom_components.saj_local.saj.telemetry import Telemetry

ALL_KEYS = frozenset(
    {
        "operating_mode",
        "pv_power",
        "battery_power",
        "battery_soc",
        "grid_power",
        "load_power",
    }
)


def _profile(
    *, display_name: str = "Alpha", keys: frozenset[str] = ALL_KEYS
) -> Profile:
    return Profile(
        key=display_name.lower(),
        display_name=display_name,
        device_types=frozenset({1}),
        measurement_keys=keys,
        hand_verified=True,
    )


def _device(profile: Profile | None = None, *, detected: bool = True) -> Device:
    return Device(
        serial="TEST-001",
        device_type=1,
        rated_power=12000,
        profile=profile or _profile(),
        detected=detected,
    )


def _telemetry(**values) -> Telemetry:
    return Telemetry(values=values)


@pytest.fixture(autouse=True)
def _stub_coordinator_entity_constructor(monkeypatch):
    def construct_entity(self, coordinator, context=None):
        self.coordinator = coordinator
        self.coordinator_context = context

    monkeypatch.setattr(sensor.CoordinatorEntity, "__init__", construct_entity)


class FakeCoordinator:
    def __init__(self, data: Telemetry, device: Device | None = None) -> None:
        self.device = device or _device()
        self.data = data
        self.entry_id = "logical-installation-123"
        self.last_update_success = True
        self.unavailable_keys = frozenset()
        self.last_read = frozenset()

    def async_add_listener(self, _listener, context=None):
        del context
        return lambda: None


@pytest.mark.parametrize(
    ("supported", "display_name"),
    [
        (ALL_KEYS, "Alpha"),
        (frozenset({"pv_power", "battery_soc"}), "Beta"),
        (frozenset(), "Gamma"),
    ],
)
async def test_platform_creates_one_entity_per_key_supported_by_the_profile(
    supported, display_name
):
    device = _device(_profile(display_name=display_name, keys=supported))
    coordinator = FakeCoordinator(_telemetry(), device)
    entry = SimpleNamespace(runtime_data=SimpleNamespace(coordinator=coordinator))
    entities = []

    await sensor.async_setup_entry(None, entry, entities.extend)

    assert {entity.key for entity in entities} == supported
    assert {entity.coordinator_context for entity in entities} == supported


async def test_platform_creates_six_entities_from_entry_runtime():
    coordinator = FakeCoordinator(_telemetry())
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
    coordinator = FakeCoordinator(_telemetry(pv_power=2000, battery_power=-500))
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
    coordinator = FakeCoordinator(_telemetry(battery_soc=84.25))
    entity = sensor.SajSensor(
        coordinator,
        sensor.SensorDescription("battery_soc", SensorDeviceClass.BATTERY, PERCENTAGE),
    )

    assert entity.native_value == 84.25
    assert entity._attr_native_unit_of_measurement == PERCENTAGE
    assert entity._attr_state_class is SensorStateClass.MEASUREMENT


def test_operating_mode_is_an_enum_with_translated_state_key():
    coordinator = FakeCoordinator(_telemetry(operating_mode=2))
    entity = sensor.SajSensor(
        coordinator, sensor.SensorDescription("operating_mode", SensorDeviceClass.ENUM)
    )

    assert entity._attr_device_class is SensorDeviceClass.ENUM
    assert "operating" in entity._attr_options
    assert entity.native_value == "operating"
    assert entity._attr_translation_key == "operating_mode"


def test_unknown_mode_has_unknown_sensor_state_and_stable_device_identity():
    coordinator = FakeCoordinator(_telemetry(operating_mode=27))
    entity = sensor.SajSensor(
        coordinator, sensor.SensorDescription("operating_mode", SensorDeviceClass.ENUM)
    )

    assert entity.native_value is None
    assert entity._attr_unique_id == "logical-installation-123_operating_mode"
    assert entity._attr_device_info["identifiers"] == {
        (DOMAIN, "logical-installation-123")
    }
    assert entity._attr_device_info["name"] == "SAJ"
    assert entity._attr_device_info["model"] == "Alpha (12000 W)"
    assert entity._attr_device_info["serial_number"] == "TEST-001"


def test_non_measurement_description_has_no_state_class():
    entity = sensor.SajSensor(
        FakeCoordinator(_telemetry()), sensor.SensorDescription("custom")
    )

    assert not hasattr(entity, "_attr_state_class")


@pytest.mark.parametrize(
    ("display_name", "detected", "expected"),
    [
        ("Alpha", True, "Alpha (12000 W)"),
        ("Beta", True, "Beta (12000 W)"),
        ("Beta", False, "Beta (12000 W, unverified)"),
    ],
)
def test_device_model_names_the_effective_profile_and_whether_it_was_detected(
    display_name, detected, expected
):
    device = _device(_profile(display_name=display_name), detected=detected)
    entity = sensor.SajSensor(
        FakeCoordinator(_telemetry(), device),
        sensor.SensorDescription("pv_power", SensorDeviceClass.POWER, UnitOfPower.WATT),
    )

    assert entity._attr_device_info["model"] == expected


def test_unique_ids_and_device_identity_are_independent_of_the_profile():
    description = sensor.SensorDescription(
        "pv_power", SensorDeviceClass.POWER, UnitOfPower.WATT
    )
    entities = [
        sensor.SajSensor(
            FakeCoordinator(_telemetry(), _device(_profile(display_name=name))),
            description,
        )
        for name in ("Alpha", "Beta")
    ]

    assert len({entity._attr_unique_id for entity in entities}) == 1
    assert (
        len({frozenset(entity._attr_device_info["identifiers"]) for entity in entities})
        == 1
    )


@pytest.fixture
def writes(monkeypatch):
    recorded = []
    monkeypatch.setattr(
        sensor.SajSensor,
        "async_write_ha_state",
        lambda self: recorded.append(self.key),
    )
    return recorded


def _entity(coordinator, key="pv_power"):
    return sensor.SajSensor(coordinator, sensor.SensorDescription(key))


@pytest.mark.parametrize(
    ("installation_up", "unavailable", "expected"),
    [
        (True, frozenset(), True),
        (True, frozenset({"grid_power"}), True),
        (True, frozenset({"pv_power"}), False),
        (False, frozenset(), False),
        (False, frozenset({"pv_power"}), False),
    ],
)
def test_availability_combines_the_installation_and_the_sensor_itself(
    *, installation_up, unavailable, expected
):
    coordinator = FakeCoordinator(_telemetry())
    coordinator.last_update_success = installation_up
    coordinator.unavailable_keys = unavailable

    assert _entity(coordinator).available is expected


def test_a_sensor_writes_its_state_in_a_cycle_that_read_it(writes):
    coordinator = FakeCoordinator(_telemetry(pv_power=1))
    coordinator.last_read = frozenset({"pv_power"})
    entity = _entity(coordinator)

    entity._handle_coordinator_update()

    assert writes == ["pv_power"]


async def test_a_sensor_not_read_keeps_its_state_while_availability_is_unchanged(
    writes,
):
    coordinator = FakeCoordinator(_telemetry(pv_power=1))
    entity = _entity(coordinator)
    await entity.async_added_to_hass()
    coordinator.last_read = frozenset({"grid_power"})

    entity._handle_coordinator_update()
    entity._handle_coordinator_update()

    assert writes == []


async def test_a_sensor_not_read_writes_once_per_availability_change(writes):
    coordinator = FakeCoordinator(_telemetry(pv_power=1))
    entity = _entity(coordinator)
    await entity.async_added_to_hass()

    coordinator.last_update_success = False
    entity._handle_coordinator_update()
    entity._handle_coordinator_update()
    coordinator.last_update_success = True
    entity._handle_coordinator_update()
    coordinator.unavailable_keys = frozenset({"pv_power"})
    entity._handle_coordinator_update()
    coordinator.unavailable_keys = frozenset()
    entity._handle_coordinator_update()
    entity._handle_coordinator_update()

    assert writes == ["pv_power"] * 4


async def test_the_platform_adds_entities_without_attaching_them_to_a_subentry():
    coordinator = FakeCoordinator(_telemetry())
    entry = SimpleNamespace(runtime_data=SimpleNamespace(coordinator=coordinator))
    calls = []

    def add_entities(entities, *args, **kwargs):
        calls.append((list(entities), args, kwargs))

    await sensor.async_setup_entry(None, entry, add_entities)

    assert len(calls) == 1
    assert calls[0][1:] == ((), {})
