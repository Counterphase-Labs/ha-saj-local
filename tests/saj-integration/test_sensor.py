from datetime import UTC, datetime, time

import pytest
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.components.sensor.const import DEVICE_CLASS_UNITS
from homeassistant.util import dt as dt_util

from custom_components.saj_local.saj.catalogue import CATALOGUES
from custom_components.saj_local.saj.codec import Encoding
from custom_components.saj_local.saj.definitions import EntityKind, Quantity, Unit
from custom_components.saj_local.sensor import SajSensor
from tests.entities import FakeCoordinator, register

OPTIONS = {0: "idle", 2: "charging"}


def _sensor(*, value=None, **changes) -> SajSensor:
    return SajSensor(
        coordinator=FakeCoordinator(values={"test_row": value}),
        register=register(**changes),
        prefix="",
    )


@pytest.mark.parametrize(
    ("quantity", "unit", "device_class", "state_class"),
    [
        (Quantity.POWER, Unit.WATT, "power", SensorStateClass.MEASUREMENT),
        (
            Quantity.APPARENT_POWER,
            Unit.VOLT_AMPERE,
            "apparent_power",
            SensorStateClass.MEASUREMENT,
        ),
        (
            Quantity.REACTIVE_POWER,
            Unit.VAR,
            "reactive_power",
            SensorStateClass.MEASUREMENT,
        ),
        (Quantity.VOLTAGE, Unit.VOLT, "voltage", SensorStateClass.MEASUREMENT),
        (Quantity.CURRENT, Unit.AMPERE, "current", SensorStateClass.MEASUREMENT),
        (Quantity.FREQUENCY, Unit.HERTZ, "frequency", SensorStateClass.MEASUREMENT),
        (Quantity.POWER_FACTOR, None, "power_factor", SensorStateClass.MEASUREMENT),
        (
            Quantity.TEMPERATURE,
            Unit.CELSIUS,
            "temperature",
            SensorStateClass.MEASUREMENT,
        ),
        (Quantity.DURATION, Unit.SECOND, "duration", SensorStateClass.MEASUREMENT),
        (Quantity.DURATION, Unit.MINUTE, "duration", SensorStateClass.MEASUREMENT),
        (
            Quantity.STORED_ENERGY,
            Unit.KILOWATT_HOUR,
            "energy_storage",
            SensorStateClass.MEASUREMENT,
        ),
        (
            Quantity.STATE_OF_CHARGE,
            Unit.PERCENT,
            "battery",
            SensorStateClass.MEASUREMENT,
        ),
        (Quantity.PERCENTAGE, Unit.PERCENT, None, SensorStateClass.MEASUREMENT),
        (Quantity.RESISTANCE, Unit.KILOOHM, None, SensorStateClass.MEASUREMENT),
        (Quantity.CAPACITY, Unit.AMPERE_HOUR, None, SensorStateClass.MEASUREMENT),
        (
            Quantity.ENERGY,
            Unit.KILOWATT_HOUR,
            "energy",
            SensorStateClass.TOTAL_INCREASING,
        ),
        (Quantity.COUNT, None, None, None),
        (Quantity.CODE, None, None, None),
        (Quantity.VERSION, None, None, None),
    ],
)
def test_the_quantity_decides_device_class_unit_and_state_class(
    quantity, unit, device_class, state_class
):
    built = _sensor(quantity=quantity, unit=unit)

    assert built.device_class == device_class
    assert built.native_unit_of_measurement == (None if unit is None else unit.value)
    assert built.state_class == state_class


@pytest.mark.parametrize(
    ("quantity", "encoding"),
    [
        (Quantity.TEXT, Encoding.TEXT),
        (Quantity.ADDRESS, Encoding.MAC),
        (Quantity.VERSION, Encoding.U16),
    ],
)
def test_text_and_version_sensors_have_no_class_and_show_the_value_as_read(
    quantity, encoding
):
    built = _sensor(quantity=quantity, encoding=encoding, value="1.005")

    assert built.device_class is None
    assert built.state_class is None
    assert built.native_value == "1.005"


@pytest.mark.parametrize("value", [2000, -500, 84.25, 0])
def test_a_numeric_sensor_shows_the_value_as_read(value):
    assert (
        _sensor(quantity=Quantity.POWER, unit=Unit.WATT, value=value).native_value
        == value
    )


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0, "idle"),
        (2, "charging"),
        (1, None),
        (27, None),
        (2.0, "charging"),
        (None, None),
    ],
)
def test_an_enumerated_sensor_shows_the_name_of_the_code_and_unknown_for_no_name(
    value, expected
):
    built = _sensor(quantity=Quantity.CODE, options=OPTIONS, value=value)

    assert built.native_value == expected


def test_an_enumerated_sensor_exposes_its_named_options_as_an_enum():
    built = _sensor(quantity=Quantity.CODE, options=OPTIONS)

    assert built.device_class is SensorDeviceClass.ENUM
    assert built.options == ["idle", "charging"]
    assert built.native_unit_of_measurement is None
    assert built.state_class is None


def test_a_unix_time_sensor_is_a_timestamp_shown_as_read():
    moment = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)

    built = _sensor(
        quantity=Quantity.TIMESTAMP, encoding=Encoding.UNIX_TIME, value=moment
    )

    assert built.device_class is SensorDeviceClass.TIMESTAMP
    assert built.native_value == moment


def test_a_clock_without_a_zone_is_taken_to_be_in_the_home_assistant_time_zone():
    clock = datetime(2026, 1, 2, 3, 4, 5)  # noqa: DTZ001

    built = _sensor(quantity=Quantity.TIMESTAMP, encoding=Encoding.CLOCK, value=clock)

    assert built.native_value == clock.replace(tzinfo=dt_util.get_default_time_zone())


@pytest.mark.parametrize("value", [None, time(1, 2)])
def test_a_sensor_without_a_usable_value_has_an_unknown_state(value):
    assert (
        _sensor(quantity=Quantity.POWER, unit=Unit.WATT, value=value).native_value
        is None
    )


def test_a_sensor_without_any_reading_has_an_unknown_state():
    built = SajSensor(coordinator=FakeCoordinator(), register=register(), prefix="")

    assert built.native_value is None


def _shipped_sensor_registers():
    seen = {}
    for catalogue in CATALOGUES.values():
        for row in catalogue.registers:
            if row.kind is EntityKind.SENSOR:
                seen.setdefault(row.key, row)
    return list(seen.values())


@pytest.mark.parametrize("row", _shipped_sensor_registers(), ids=lambda row: row.key)
def test_every_shipped_sensor_has_a_unit_its_device_class_accepts(row):
    built = SajSensor(coordinator=FakeCoordinator(), register=row, prefix="")

    allowed = DEVICE_CLASS_UNITS.get(built.device_class)
    if allowed is not None:
        assert built.native_unit_of_measurement in allowed
