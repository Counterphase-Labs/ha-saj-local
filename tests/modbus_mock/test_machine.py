from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from saj_modbus_mock import machine as machine_module
from saj_modbus_mock.machine import Machine
from saj_modbus_mock.registers import EPOCH, Field
from saj_modbus_mock.simulation import control as ctl

from .builders import make_scenario

NOW = datetime(2026, 7, 4, 9, 30, tzinfo=UTC)


class StubClock:
    def __init__(self, *, start, speed, monotonic):
        self.args = {"start": start, "speed": speed, "monotonic": monotonic}
        self.set_to = []

    def now(self):
        return NOW

    def set(self, *, moment):
        self.set_to.append(moment)


class StubPlant:
    def __init__(self, *, settings, **_unused):
        self.settings = settings
        self.advanced = []
        self.second = 777
        self.fault_bits = (1, 2)
        self.restarts = 0
        self.jumps = []
        self.keepalives = []
        self.controller = SimpleNamespace(
            keepalive=lambda *, second: self.keepalives.append(second)
        )
        self.ledger = SimpleNamespace(clear=self._clear)
        self.cleared = 0

    def _clear(self):
        self.cleared += 1

    def advance(self, *, moment):
        self.advanced.append(moment)

    def restart(self):
        self.restarts += 1

    def jump_to(self, *, moment):
        self.jumps.append(moment)


class StubDevice:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


@pytest.fixture
def machine(monkeypatch):
    initial = {
        ctl.APP_MODE: 2,
        ctl.EMS_ENABLE: 0,
        ctl.CHARGE_CEILING: 90,
        ctl.BACKUP_RESERVE: 40,
        ctl.DISCHARGE_FLOOR_ON_GRID: 15,
        "meter_enable": 3,
        "ev_mode": 1,
    }
    monkeypatch.setattr(
        machine_module,
        "profiles",
        SimpleNamespace(
            build_blocks=lambda **_: "BLOCKS",
            overrun_code=lambda **_: "OVERRUN",
        ),
    )
    monkeypatch.setattr(machine_module, "initial_settings", lambda **_: dict(initial))
    monkeypatch.setattr(machine_module, "Clock", StubClock)
    monkeypatch.setattr(machine_module, "Plant", StubPlant)
    monkeypatch.setattr(machine_module, "Device", StubDevice)
    monkeypatch.setattr(machine_module, "build_telemetry", lambda **_: {"pv_w": 1.0})
    result = Machine(scenario=make_scenario(model="hs3"), monotonic=lambda: 0.0)
    result.initial = initial
    return result


def field(*, name, keepalive_bit=0, readable=True):
    from saj_modbus_mock.registers import Access

    return Field(
        address=0,
        name=name,
        keepalive_bit=keepalive_bit,
        access=Access.READ_WRITE if readable else Access.WRITE_ONLY,
    )


def test_the_machine_wires_the_profile_the_clock_the_plant_and_the_device_together(
    machine,
):
    assert machine.device.kwargs["blocks"] == "BLOCKS"
    assert machine.device.kwargs["overrun_code"] == "OVERRUN"
    assert machine.device.kwargs["observer"] is machine
    assert machine.device.kwargs["settings"] is machine.settings
    assert machine.plant.settings is machine.settings
    assert machine.clock.args["start"] == machine.scenario.simulation.start
    assert machine.clock.args["speed"] == machine.scenario.simulation.speed


def test_reading_telemetry_first_brings_the_plant_up_to_the_clock(machine):
    data = machine.device.kwargs["telemetry"]()

    assert machine.plant.advanced == [NOW]
    assert data["pv_w"] == 1.0


@pytest.mark.parametrize(
    ("ems", "app_mode", "running"),
    [(0, 2, 2.0), (8, 2, 6.0), (1, 0, 6.0)],
)
def test_the_running_mode_is_ems_while_any_enable_bit_is_set(
    machine, ems, app_mode, running
):
    machine.settings[ctl.APP_MODE] = app_mode
    machine.settings[ctl.EMS_ENABLE] = ems

    assert machine.telemetry()["running_mode"] == running


def test_setting_mirrors_follow_the_stored_settings(machine):
    data = machine.telemetry()

    assert data["mirror_charge_ceiling"] == 90.0
    assert data["mirror_reserve"] == 40.0
    assert data["mirror_discharge_floor"] == 15.0
    assert data["mirror_meter_mode"] == 3.0
    assert data["mirror_ev_mode"] == 1.0


def test_a_text_setting_mirrors_as_zero(machine):
    machine.settings["meter_enable"] = "n/a"

    assert machine.telemetry()["mirror_meter_mode"] == 0.0


def test_the_settings_serial_counts_writes_of_stored_registers_only(machine):
    assert machine.telemetry()["settings_change_serial"] == 0.0

    machine.field_written(field=field(name="a"), value=1)
    machine.field_written(field=field(name="b"), value=1)
    machine.field_written(field=field(name="cmd", readable=False), value=1)

    assert machine.telemetry()["settings_change_serial"] == 2.0


def test_enabling_standard_ems_borrows_the_application_mode_and_clearing_it_restores_it(
    machine,
):
    machine.settings[ctl.EMS_ENABLE] = 1
    machine.telemetry()
    assert machine.settings[ctl.APP_MODE] == ctl.MODE_EMS

    machine.settings[ctl.EMS_ENABLE] = 0
    machine.telemetry()

    assert machine.settings[ctl.APP_MODE] == 2


@pytest.mark.parametrize("bits", [2, 8, 32])
def test_the_other_ems_bits_leave_the_application_mode_alone(machine, bits):
    machine.settings[ctl.EMS_ENABLE] = bits

    machine.telemetry()

    assert machine.settings[ctl.APP_MODE] == 2


def test_turning_ems_on_counts_as_a_keepalive_but_changing_bits_while_on_does_not(
    machine,
):
    machine.settings[ctl.EMS_ENABLE] = 8
    machine.telemetry()
    assert machine.plant.keepalives == [777]

    machine.settings[ctl.EMS_ENABLE] = 10
    machine.telemetry()

    assert machine.plant.keepalives == [777]


def test_an_unchanged_enable_register_changes_nothing(machine):
    machine.telemetry()
    machine.telemetry()

    assert machine.plant.keepalives == []


@pytest.mark.parametrize(
    ("bit", "enable", "kept_alive"),
    [
        (0b1000, 0b1000, True),
        (0b1000, 0b0010, False),
        (0, 0b1000, False),
        (0b0010, 0b0010, True),
    ],
)
def test_reads_and_writes_of_the_active_target_register_keep_ems_alive(
    machine, bit, enable, kept_alive
):
    machine.settings[ctl.EMS_ENABLE] = enable
    target = field(name="target", keepalive_bit=bit)

    machine.field_read(field=target)
    machine.field_written(field=target, value=1)

    assert (machine.plant.keepalives.count(777) >= 2) is kept_alive


def test_clearing_faults_removes_the_fault_bits(machine):
    machine.field_written(field=field(name="cmd_clear_faults", readable=False), value=1)

    assert machine.plant.fault_bits == ()


def test_restart_is_forwarded_to_the_plant(machine):
    machine.field_written(field=field(name="cmd_restart", readable=False), value=1)

    assert machine.plant.restarts == 1


def test_clearing_power_history_clears_the_ledger(machine):
    machine.field_written(
        field=field(name="cmd_clear_power_history", readable=False), value=1
    )

    assert machine.plant.cleared == 1


def test_a_factory_reset_restores_the_start_values_and_forgets_ems_state(machine):
    machine.settings[ctl.EMS_ENABLE] = 1
    machine.telemetry()
    machine.settings[ctl.BACKUP_RESERVE] = 99

    machine.field_written(
        field=field(name="cmd_factory_reset", readable=False), value=1
    )

    assert machine.settings[ctl.BACKUP_RESERVE] == 40
    assert machine.settings[ctl.EMS_ENABLE] == 0
    assert machine.settings[ctl.APP_MODE] == 2
    machine.telemetry()
    assert machine.settings[ctl.APP_MODE] == 2


def test_writing_the_clock_moves_both_the_clock_and_the_plant(machine):
    seconds = (NOW - EPOCH).total_seconds()

    machine.field_written(
        field=field(name="cmd_set_clock", readable=False), value=seconds
    )

    assert machine.clock.set_to == [NOW]
    assert machine.plant.jumps == [NOW]


def test_other_writes_are_not_commands(machine):
    machine.field_written(field=field(name="something_else"), value=1)

    assert machine.plant.restarts == 0
    assert machine.plant.jumps == []
    assert machine.plant.fault_bits == (1, 2)
