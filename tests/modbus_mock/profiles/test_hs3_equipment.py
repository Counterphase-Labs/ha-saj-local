import pytest

from saj_modbus_mock.profiles import hs3_equipment as eq
from saj_modbus_mock.profiles.fields import ZERO
from saj_modbus_mock.registers import Access, Encoding
from saj_modbus_mock.simulation import control as ctl
from saj_modbus_mock.simulation import ev_charger as ev
from tests.modbus_mock.builders import by_address, by_name, make_scenario
from tests.modbus_mock.profiles.fakes import isolate


@pytest.fixture(autouse=True)
def stubbed_helpers(monkeypatch):
    isolate(monkeypatch, eq)
    monkeypatch.setattr(eq, "ems_labels", lambda: {0: "Off", 99: "Ninety-nine"})


def test_average_registers_read_the_five_minute_mean_of_their_quantity():
    fields = by_address(fields=eq.average_fields())

    assert fields[0x513E].source == "avg_grid_w"
    assert fields[0x5140].source == "avg_grid_r_w"
    assert fields[0x5197].source == "avg_pv1_w"
    assert fields[0x5197].encoding is Encoding.U32
    assert fields[0x5196].encoding is Encoding.U16
    assert fields[0x51A5].source == ZERO


def test_the_ethernet_block_has_a_three_word_mac_and_writable_addresses():
    fields = by_address(fields=eq.ethernet_fields())

    assert fields[0x0F04].words == 3
    assert not fields[0x0F04].writable
    assert fields[0x0F08].initial == "192.168.1.50"
    assert fields[0x0F08].writable
    assert fields[0x0F08].words == 8
    assert fields[0x0F07].options == {0, 1}


@pytest.mark.parametrize(("installed", "enabled"), [(True, 1), (False, 0)])
def test_the_charger_enable_setting_follows_the_installation(installed, enabled):
    scenario = make_scenario(model="hs3", ev_charger={"installed": installed})

    fields = by_name(fields=eq.ev_settings_fields(scenario=scenario))

    assert fields[ev.EV_ENABLED].initial == enabled


def test_the_charger_power_setting_is_bounded_by_the_charger_maximum():
    scenario = make_scenario(
        model="hs3", ev_charger={"installed": True, "max_power_w": 7000}
    )

    field = by_name(fields=eq.ev_settings_fields(scenario=scenario))[ev.EV_CHARGE_POWER]

    assert field.initial == field.maximum == 7000
    assert field.words == 2


def test_charger_schedule_slots_use_the_keys_the_charger_reads():
    names = {
        field.name
        for field in eq.ev_settings_fields(scenario=make_scenario(model="hs3"))
    }

    for index in range(1, ev.SLOTS + 1):
        for part in ("start", "end", "date", "power_w"):
            assert ev.slot_key(index=index, part=part) in names


def test_the_charger_ems_current_is_in_amps_with_the_protocol_range():
    field = by_name(fields=eq.ev_settings_fields(scenario=make_scenario(model="hs3")))[
        ev.EV_EMS_CURRENT
    ]

    assert field.scale == 0.1
    assert (field.minimum, field.maximum) == (60, 320)


def test_the_charger_ems_command_is_a_three_bit_field_that_starts_switched_off():
    field = by_name(fields=eq.ev_settings_fields(scenario=make_scenario(model="hs3")))[
        ev.EV_EMS_COMMAND
    ]

    assert field.writable
    assert (field.minimum, field.maximum) == (None, 0b111)
    assert field.initial & 0b1


def test_charger_data_is_read_only_and_describes_the_session():
    fields = by_address(fields=eq.ev_data_fields())

    assert all(not field.writable for field in fields.values())
    assert fields[0x3024].words == 16
    assert fields[0x309D].source == "ev_state"
    assert fields[0x30B8].encoding is Encoding.U32
    assert fields[0x309E].source == "ev_r_v"


def test_ems_targets_restart_the_timeout_for_the_bits_that_use_them():
    fields = by_name(fields=eq.ems_fields())

    assert fields[ctl.EMS_INVERTER_TARGET].keepalive_bit == 0b001001
    assert fields[ctl.EMS_BATTERY_TARGET].keepalive_bit == 0b000010
    assert fields[ctl.EMS_GRID_TARGET].keepalive_bit == 0b100000
    assert fields[ctl.EMS_BUY_LIMIT].keepalive_bit == 0
    assert all(field.access is Access.READ_WRITE for field in fields.values())


def test_ems_starts_disabled_with_documented_defaults():
    fields = by_name(fields=eq.ems_fields())

    assert fields[ctl.EMS_ENABLE].initial == 0
    assert fields[ctl.EMS_ENABLE].options == {0, 99}
    assert dict(fields[ctl.EMS_ENABLE].labels) == {0: "Off", 99: "Ninety-nine"}
    assert fields[ctl.EMS_TIMEOUT].initial == 300
    assert fields[ctl.EMS_PV_LIMIT].initial == ctl.EMS_NO_PV_LIMIT
    assert (
        fields[ctl.EMS_BUY_LIMIT].initial == fields[ctl.EMS_SELL_LIMIT].initial == 1.0
    )
    assert fields[ctl.EMS_BATTERY_CHARGE_CURRENT].scale == 0.1


@pytest.mark.parametrize(
    "key",
    [ctl.EMS_INVERTER_TARGET, ctl.EMS_BATTERY_TARGET, ctl.EMS_GRID_TARGET],
)
def test_ems_targets_are_signed_fractions_of_rated_power(key):
    field = by_name(fields=eq.ems_fields())[key]

    assert field.encoding is Encoding.I16
    assert field.scale == 0.0001


@pytest.mark.parametrize(
    ("address", "source"), [(0x30AB, "fault_30ab"), (0x30AD, "fault_30ad")]
)
def test_the_charger_error_registers_are_two_word_readings_of_the_fault_words(
    address, source
):
    fields = by_address(fields=eq.ev_data_fields())

    assert fields[address].source == source
    assert fields[address].words == 2
    assert not fields[address].writable


def test_the_charger_choices_name_the_values_they_accept():
    scenario = make_scenario(model="hs3", ev_charger={"installed": True})
    fields = by_name(fields=eq.ev_settings_fields(scenario=scenario))

    for name in (ev.EV_MODE, "ev_baud", "ev_port_mode"):
        assert {code for code, _label in fields[name].labels} == fields[name].options
    assert dict(fields[ev.EV_MODE].labels)[ev.MODE_FORCED]
    ethernet = by_name(fields=eq.ethernet_fields())["ethernet_net_mode"]
    assert {code for code, _label in ethernet.labels} == ethernet.options
