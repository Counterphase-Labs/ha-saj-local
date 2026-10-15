import pytest

from saj_modbus_mock.profiles import h2_extras
from saj_modbus_mock.registers import Encoding
from tests.modbus_mock.builders import by_address, by_name, make_scenario
from tests.modbus_mock.profiles.fakes import isolate


@pytest.fixture(autouse=True)
def stubbed_helpers(monkeypatch):
    isolate(monkeypatch, h2_extras)


def settings(**changes):
    return h2_extras.settings_fields(scenario=make_scenario(model="h2", **changes))


def test_every_setting_is_either_writable_with_bounds_or_a_read_only_mirror():
    for field in settings():
        if field.writable:
            assert field.minimum is not None
            assert field.maximum is not None
            assert field.minimum <= field.initial / field.scale <= field.maximum
        else:
            assert field.name in {"machine_model", "power_rated"}


def test_the_machine_mirrors_report_the_scenario_not_a_constant():
    scenario = make_scenario(model="h2", device={"rated_power_w": 5000})

    fields = by_address(fields=h2_extras.settings_fields(scenario=scenario))

    assert fields[0x366D].initial == 5000
    assert fields[0x366C].initial == scenario.device.model.device_type


def test_the_lead_acid_capacity_keeps_its_default_with_a_lithium_battery_fitted():
    fields = by_name(fields=settings(battery={"modules": 3, "module_capacity_ah": 100}))

    assert fields["battery_total_capacity_setting"].initial == 0


@pytest.mark.parametrize(
    ("address", "scale", "maximum"),
    [
        (0x3652, 0.1, 4500),
        (0x3657, 0.1, 300),
        (0x366A, 0.01, 6000),
        (0x3670, 0.001, 3000),
        (0x3672, 1.0, 1000),
    ],
)
def test_settings_carry_the_scale_and_range_of_their_unit(address, scale, maximum):
    field = by_address(fields=settings())[address]

    assert (field.scale, field.maximum) == (scale, maximum)


def test_realtime_extras_have_the_protocol_widths():
    fields = by_address(fields=h2_extras.realtime_fields())

    assert fields[0x400D].words == 2
    assert fields[0x401C].words == 6
    assert fields[0x40B0].words == 12
    assert fields[0x40BD].encoding is Encoding.U32
    assert fields[0x406B].encoding is Encoding.I16


def test_realtime_extras_are_live_where_a_matching_quantity_exists():
    fields = by_address(fields=h2_extras.realtime_fields())

    assert fields[0x400F].source == "fault_count"
    assert fields[0x401B].source == "settings_change_serial"
    assert fields[0x40BC].source == "pv_hours_today_kwh"
    assert fields[0x406B].source == fields[0x406C].source == "battery_half_a"
    assert fields[0x40BC].scale == 0.1


def test_realtime_extras_are_all_read_only():
    assert all(not field.writable for field in h2_extras.realtime_fields())
