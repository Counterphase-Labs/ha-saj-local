import dataclasses
from datetime import UTC, date, datetime
from types import SimpleNamespace

import pytest

from saj_modbus_mock import machine as machine_module
from saj_modbus_mock.device import Block
from saj_modbus_mock.exceptions import ControlError
from saj_modbus_mock.link import Link, LinkSettings, RefusedBlock
from saj_modbus_mock.machine import Machine, Wiring
from saj_modbus_mock.profiles.common import CLEAR_CURRENT_FAULT, CLEAR_FAULT_HISTORY
from saj_modbus_mock.registers import EPOCH, Access, Encoding, Field
from saj_modbus_mock.simulation import control as ctl
from saj_modbus_mock.simulation.environment import LoadConfig, Variation
from saj_modbus_mock.simulation.ev_charger import HandState
from saj_modbus_mock.simulation.faults import (
    Effect,
    Equipment,
    FaultBit,
    FaultEntry,
    FaultMap,
    FaultState,
    PackCodes,
)

from .builders import make_scenario

NOW = datetime(2026, 7, 4, 9, 30, tzinfo=UTC)
GRID_LOST = FaultBit(register=0x4005, bit=23)
GRID_LOST_B = FaultBit(register=0x4009, bit=23)
RESERVED = FaultBit(register=0x4005, bit=22)
HOT = FaultBit(register=0x400B, bit=10)
CHARGER = FaultBit(register=0x30AB, bit=2)
METER_LOST = FaultBit(register=0x4005, bit=1)
INVERTER_STOP = frozenset({Effect.INVERTER_STOP})
FAULT_MAP = FaultMap(
    entries=(
        FaultEntry(
            Equipment.INVERTER, GRID_LOST, "Grid lost", frozenset({Effect.GRID_LOST})
        ),
        FaultEntry(
            Equipment.INVERTER, GRID_LOST_B, "Grid lost", frozenset({Effect.GRID_LOST})
        ),
        FaultEntry(
            Equipment.INVERTER, METER_LOST, "Meter communication lost", INVERTER_STOP
        ),
        FaultEntry(
            Equipment.INVERTER, RESERVED, "reserved", frozenset(), reserved=True
        ),
        FaultEntry(
            Equipment.BATTERY,
            HOT,
            "Battery too hot to charge",
            frozenset({Effect.NO_CHARGE}),
        ),
        FaultEntry(
            Equipment.EV_CHARGER,
            CHARGER,
            "EV charger AC overvoltage",
            frozenset({Effect.EV_STOP}),
        ),
    ),
    pack_count=2,
)
TELEMETRY = {
    "pv_w": 1.0,
    "ext_pv_w": 7.0,
    "load_w": 2.0,
    "grid_export_w": 3.0,
    "battery_w": 4.0,
    "soc_percent": 55.0,
    "ev_power_w": 6.0,
    "grid_r_v": 230.0,
    "frequency_hz": 50.0,
    "operating_mode": 2.0,
    "running_mode": 6.0,
    "ev_state": 1.0,
}
APP_MODE_FIELD = Field(
    address=0x3647,
    name=ctl.APP_MODE,
    access=Access.READ_WRITE,
    options=frozenset({0, 6}),
    labels=((6, "EMS"),),
)
SETTING_FIELD = Field(address=1, name="a_setting", access=Access.READ_WRITE)
SCALED_FIELD = Field(
    address=0x20, name="scaled_limit", access=Access.READ_WRITE, scale=0.0001
)
BACKUP_RESERVE_FIELD = Field(
    address=0x10, name=ctl.BACKUP_RESERVE, access=Access.READ_WRITE
)
EMS_ENABLE_FIELD = Field(address=0x11, name=ctl.EMS_ENABLE, access=Access.READ_WRITE)
FIXED_FIELD = Field(address=0x12, name="meter_enable", access=Access.READ_ONLY)
COMMAND_FIELD = Field(address=2, name="cmd_restart", access=Access.WRITE_ONLY)
CLOCK_FIELD = Field(
    address=3, name="cmd_set_clock", encoding=Encoding.CLOCK, access=Access.WRITE_ONLY
)
KNOWN_FIELDS = {
    field.name: field
    for field in (APP_MODE_FIELD, SETTING_FIELD, COMMAND_FIELD, CLOCK_FIELD)
}


BLOCK = Block(
    start=0,
    end=0x4000,
    fields=(
        SETTING_FIELD,
        SCALED_FIELD,
        BACKUP_RESERVE_FIELD,
        EMS_ENABLE_FIELD,
        FIXED_FIELD,
        COMMAND_FIELD,
        CLOCK_FIELD,
    ),
)
BLOCK_WITH_MODE = Block(start=0x3647, end=0x3647, fields=(APP_MODE_FIELD,))


class StubClock:
    def __init__(self, *, start, speed, monotonic):
        self.args = {"start": start, "speed": speed, "monotonic": monotonic}
        self.speed = speed
        self.set_to = []
        self.speeds = []

    def now(self):
        return NOW

    def set(self, *, moment):
        self.set_to.append(moment)

    def set_speed(self, *, speed):
        self.speeds.append(speed)
        self.speed = speed


class StubLedger:
    def __init__(self):
        self.cleared = 0
        self.resets = []
        self.restored = []

    def clear(self):
        self.cleared += 1

    def reset(self, *, moment):
        self.resets.append(moment)

    def totals_wh(self):
        return {"pv": 5.0}

    def starts_wh(self):
        return {"today": {"pv": 1.0}, "month": {"pv": 2.0}, "year": {"pv": 3.0}}

    day = date(2026, 7, 4)

    def restore(self, *, totals_wh, moment, starts_wh=None, day=None):
        self.restored.append((totals_wh, moment, starts_wh, day))


class StubCharger:
    def __init__(self):
        self.hand = HandState(remaining_wh=None, suppressed_until_s=0)

    def hand_state(self):
        return self.hand


class StubPlant:
    def __init__(self, *, scenario, settings, fault_effects):
        self.scenario = scenario
        self.settings = settings
        self.fault_effects = fault_effects
        self.advanced = []
        self.second = 777
        self.faults = FaultState()
        self.seed = 7
        self.variation = Variation()
        self.load = LoadConfig(base_w=300, peak_w=3000)
        self.holds = {}
        self.battery = SimpleNamespace(soc=0.5)
        self.restarts = 0
        self.jumps = []
        self.tuned = []
        self.held = []
        self.socs = []
        self.ev_actions = []
        self.keepalives = []
        self.controller = SimpleNamespace(
            keepalive=lambda *, second: self.keepalives.append(second)
        )
        self.ledger = StubLedger()
        self.ev = StubCharger()
        self.restored_ev = []

    def moment(self):
        return NOW

    def advance(self, *, moment):
        self.advanced.append(moment)

    def restart(self):
        self.restarts += 1

    def jump_to(self, *, moment):
        self.jumps.append(moment)

    def set_faults(self, *, faults):
        self.faults = faults

    def tune(self, *, seed, variation, load):
        self.tuned.append((seed, variation, load))
        self.seed, self.variation, self.load = seed, variation, load

    def hold(self, *, holds):
        self.holds = dict(holds)

    def set_soc(self, *, soc):
        self.socs.append(soc)
        self.battery.soc = soc

    def plug_ev(self, *, energy_needed_wh):
        self.ev_actions.append(("in", energy_needed_wh))

    def unplug_ev(self):
        self.ev_actions.append(("out",))

    def restore_ev(self, *, state):
        self.restored_ev.append(state)


class StubDevice:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.written = []
        self.refused_stored = {}

    def field_named(self, *, name):
        return KNOWN_FIELDS.get(name)

    def write_named(self, *, values):
        self.written.append(dict(values))

    def peek_fields(self):
        return {"a_setting": [1], "meter_enable": [3]}

    def check_stored(self, *, name, value):
        reason = self.refused_stored.get((name, value))
        if reason is not None:
            raise ControlError(key=name, reason=reason)


@pytest.fixture
def made(monkeypatch):
    initial = {
        ctl.APP_MODE: 2,
        ctl.EMS_ENABLE: 0,
        ctl.CHARGE_CEILING: 90,
        ctl.BACKUP_RESERVE: 40,
        ctl.DISCHARGE_FLOOR_ON_GRID: 15,
        "meter_enable": 3,
        "ev_mode": 1,
        "a_setting": 1,
        "scaled_limit": 0,
    }
    monkeypatch.setattr(
        machine_module,
        "profiles",
        SimpleNamespace(
            build_blocks=lambda **_: (BLOCK, BLOCK_WITH_MODE),
            build_fault_map=lambda **_: FAULT_MAP,
            overrun_code=lambda **_: "OVERRUN",
        ),
    )
    monkeypatch.setattr(machine_module, "initial_settings", lambda **_: dict(initial))
    monkeypatch.setattr(machine_module, "Clock", StubClock)
    monkeypatch.setattr(machine_module, "Plant", StubPlant)
    monkeypatch.setattr(machine_module, "Device", StubDevice)
    monkeypatch.setattr(machine_module, "build_telemetry", lambda **_: dict(TELEMETRY))
    monkeypatch.setattr(
        machine_module, "dump_scenario", lambda *, scenario: ("yaml", scenario)
    )
    events = SimpleNamespace(changes=0, resets=0)

    def changed():
        events.changes += 1

    def reset():
        events.resets += 1

    result = Machine(
        scenario=make_scenario(
            model="hs3", ev_charger={"installed": True}, meters={"meter_a": True}
        ),
        monotonic=lambda: 0.0,
        wiring=Wiring(on_change=changed, on_reset=reset),
    )
    result.initial = initial
    result.events = events
    return result


@pytest.fixture
def machine(made):
    return made


def field(*, name, keepalive_bit=0, readable=True):
    return Field(
        address=0,
        name=name,
        keepalive_bit=keepalive_bit,
        access=Access.READ_WRITE if readable else Access.WRITE_ONLY,
    )


def refused(*, action):
    with pytest.raises(ControlError) as caught:
        action()
    return caught.value.key, caught.value.reason


def test_the_machine_wires_the_profile_the_clock_the_plant_and_the_device_together(
    machine,
):
    assert machine.device.kwargs["overrun_code"] == "OVERRUN"
    assert machine.device.kwargs["observer"] is machine
    assert machine.device.kwargs["settings"] is machine.settings
    assert machine.plant.settings is machine.settings
    assert machine.plant.fault_effects == FAULT_MAP.effects()
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


def faulted_state():
    return FaultState(
        inverter=frozenset({GRID_LOST}),
        battery=frozenset({HOT}),
        ev_charger=frozenset({CHARGER}),
        packs=(PackCodes(pack=1, fault=1),),
    )


def test_clearing_the_current_fault_clears_every_fault_on_every_equipment(machine):
    machine.plant.faults = faulted_state()

    machine.field_written(
        field=field(name="cmd_clear_faults", readable=False), value=CLEAR_CURRENT_FAULT
    )

    assert machine.plant.faults == FaultState()


def test_clearing_the_fault_history_leaves_every_active_fault_in_place(machine):
    machine.plant.faults = faulted_state()

    machine.field_written(
        field=field(name="cmd_clear_faults", readable=False), value=CLEAR_FAULT_HISTORY
    )

    assert machine.plant.faults == faulted_state()


def test_restart_is_forwarded_to_the_plant(machine):
    machine.field_written(field=field(name="cmd_restart", readable=False), value=1)

    assert machine.plant.restarts == 1


def test_clearing_power_history_clears_the_ledger(machine):
    machine.field_written(
        field=field(name="cmd_clear_power_history", readable=False), value=1
    )

    assert machine.plant.ledger.cleared == 1


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
    assert machine.plant.ledger.cleared == 0


def test_every_write_from_a_client_is_reported_as_a_change(machine):
    machine.field_written(field=field(name="a"), value=1)
    machine.field_written(field=field(name="cmd", readable=False), value=1)

    assert machine.events.changes == 2


def test_the_description_covers_the_model_faults_variation_holds_and_presets(machine):
    description = machine.describe()

    assert set(description) == {
        "model",
        "settings",
        "commands",
        "faults",
        "variation",
        "holds",
        "presets",
        "cards",
        "nodes",
        "link",
    }
    assert description["model"]["name"] == "hs3"
    assert description["faults"]["clear_all"] == {
        "command": "cmd_clear_faults",
        "value": CLEAR_CURRENT_FAULT,
    }
    assert description["faults"]["packs"] == [1, 2]
    variation = {entry["name"]: entry for entry in description["variation"]}
    assert variation["base_w"]["scenario"] == 300
    assert variation["seed"]["scenario"] == machine.scenario.simulation.seed
    keys = {preset["key"] for preset in description["presets"]}
    assert {
        "grid-lost",
        "battery-empty",
        "ev-charging",
        "meter-communication-lost",
    } <= keys
    assert "unstable-grid" in keys


def test_presets_leave_out_equipment_that_is_not_fitted(monkeypatch, machine):
    machine.scenario = make_scenario(
        model="hs3", battery={"modules": 0}, meters={"meter_a": False}
    )

    keys = {preset.key for preset in machine.presets()}

    assert "battery-empty" not in keys
    assert "meter-communication-lost" not in keys
    assert "ev-charging" not in keys
    assert "grid-lost" in keys


def test_the_state_reports_what_was_changed_and_the_live_readings(machine):
    machine.settings[ctl.APP_MODE] = 6
    machine.plant.holds = {"pv_w": 900.0}
    machine.plant.faults = FaultState(inverter=frozenset({GRID_LOST}))

    state = machine.state()

    assert state["time"] == "2026-07-04T09:30:00"
    assert state["speed"] == machine.scenario.simulation.speed
    assert state["settings"][ctl.APP_MODE] == {"raw": 6, "value": 6}
    assert state["faults"]["inverter"] == {"0x4005:23": True}
    assert state["holds"]["pv_w"] == 900.0
    assert state["holds"]["load_w"] is None
    assert state["variation"]["base_w"] == 300
    assert state["variation"]["seed"] == 7
    assert state["battery"] == {"soc_percent": 55.0}
    assert state["ev_charger"] == {"plugged": False}
    readings = {reading["label"]: reading["value"] for reading in state["readings"]}
    assert readings["PV power"] == 1.0
    assert readings["Operating mode"] == "2 Operating"
    assert readings["Application mode"] == "6 EMS"


def test_readings_of_equipment_that_is_not_fitted_are_left_out(machine):
    machine.scenario = make_scenario(model="hs3", battery={"modules": 0})

    labels = {reading["label"] for reading in machine.state()["readings"]}

    assert "Battery power" not in labels
    assert "PV power" in labels


def test_an_application_mode_without_a_name_shows_its_code_only(machine, monkeypatch):
    machine.settings[ctl.APP_MODE] = 0

    readings = {r["label"]: r["value"] for r in machine.state()["readings"]}

    assert readings["Application mode"] == "0"


def test_a_plugged_in_car_is_reported(machine, monkeypatch):
    monkeypatch.setitem(TELEMETRY, "ev_state", 3.0)

    assert machine.state()["ev_charger"] == {"plugged": True}


def test_settings_are_written_by_name_through_the_device(machine):
    machine.set_settings(values={"a_setting": 5, ctl.APP_MODE: 6})

    assert machine.device.written == [{"a_setting": 5, ctl.APP_MODE: 6}]


def test_a_command_cannot_be_written_as_a_setting(machine):
    assert refused(action=lambda: machine.set_settings(values={"cmd_restart": 1})) == (
        "cmd_restart",
        "is not a setting",
    )
    assert machine.device.written == []


def test_an_unknown_setting_is_left_for_the_device_to_refuse(machine):
    machine.set_settings(values={"nothing": 1})

    assert machine.device.written == [{"nothing": 1}]


def test_a_command_is_run_by_name_and_value(machine):
    machine.run_command(values={"name": "cmd_restart", "value": 1})

    assert machine.device.written == [{"cmd_restart": 1}]


@pytest.mark.parametrize(
    "values",
    [
        {"name": "a_setting", "value": 1},
        {"name": "cmd_set_clock", "value": 1},
        {"name": "nothing", "value": 1},
        {"name": 5, "value": 1},
        {"value": 1},
    ],
)
def test_only_commands_can_be_run_as_commands(machine, values):
    assert refused(action=lambda: machine.run_command(values=values)) == (
        "name",
        "is not a command",
    )
    assert machine.device.written == []


def test_faults_are_set_and_cleared_by_bit_and_the_plant_is_told(machine):
    machine.set_faults(
        values={
            "inverter": {"0x4005:23": True, "0x4009:23": True},
            "battery": {"0x400B:10": True},
        }
    )
    assert machine.plant.faults.inverter == {GRID_LOST, GRID_LOST_B}
    assert machine.plant.faults.battery == {HOT}

    machine.set_faults(values={"inverter": {"0x4005:23": False, "0x4005:22": False}})

    assert machine.plant.faults.inverter == {GRID_LOST_B}
    assert machine.plant.faults.battery == {HOT}
    assert machine.events.changes == 2
    assert machine.plant.advanced


def test_a_reserved_bit_can_be_set_like_any_other(machine):
    machine.set_faults(values={"inverter": {"0x4005:22": True}})

    assert machine.plant.faults.inverter == {RESERVED}


@pytest.mark.parametrize(
    ("values", "key", "reason"),
    [
        ({"engine": {}}, "engine", "unknown key"),
        ({"inverter": 5}, "inverter", "must be a mapping"),
        (
            {"inverter": {"0x4005:40": True}},
            "inverter.0x4005:40",
            "is not a fault of this device",
        ),
        (
            {"battery": {"0x4005:23": True}},
            "battery.0x4005:23",
            "is not a fault of this device",
        ),
        ({"inverter": {"0x4005:23": 1}}, "inverter.0x4005:23", "must be true or false"),
        ({"packs": 5}, "packs", "must be a mapping"),
        ({"packs": {"x": {}}}, "packs.x", "must be a number"),
        ({"packs": {"0": {}}}, "packs.0", "must be 1..2"),
        ({"packs": {"3": {}}}, "packs.3", "must be 1..2"),
        ({"packs": {"1": 5}}, "packs.1", "must be a mapping"),
        ({"packs": {"1": {"other": 1}}}, "other", "unknown key"),
        ({"packs": {"1": {"fault": 70000}}}, "packs.1.fault", "must be 0..65535"),
        ({"packs": {"1": {"warning": 1.5}}}, "packs.1.warning", "must be an integer"),
    ],
)
def test_a_refused_fault_request_names_the_key_and_changes_nothing(
    machine, values, key, reason
):
    assert refused(action=lambda: machine.set_faults(values=values)) == (key, reason)
    assert machine.plant.faults == FaultState()
    assert machine.events.changes == 0


def test_pack_codes_are_set_per_pack_and_a_missing_code_keeps_its_value(machine):
    machine.set_faults(values={"packs": {"1": {"fault": 4, "warning": 2}}})

    machine.set_faults(values={"packs": {"1": {"fault": 9}, "2": {"warning": 1}}})

    assert machine.plant.faults.packs == (
        PackCodes(pack=1, fault=9, warning=2),
        PackCodes(pack=2, warning=1),
    )


def test_pack_codes_are_refused_without_a_battery(machine):
    machine._fault_map = FaultMap(entries=(), pack_count=0)

    assert refused(action=lambda: machine.set_faults(values={"packs": {"1": {}}})) == (
        "packs",
        "no battery fitted",
    )


def test_variation_changes_merge_into_the_running_values_and_keep_the_rest(machine):
    machine.set_variation(
        values={"cloud_depth": 0.9, "base_w": 500, "peak_w": 4000, "seed": 12}
    )

    seed, variation, load = machine.plant.tuned[-1]
    assert seed == 12
    assert variation == Variation(cloud_depth=0.9)
    assert load == LoadConfig(base_w=500, peak_w=4000)

    machine.set_variation(values={"voltage_period_s": 30})

    seed, variation, load = machine.plant.tuned[-1]
    assert (seed, load) == (12, LoadConfig(base_w=500, peak_w=4000))
    assert variation == Variation(cloud_depth=0.9, voltage_period_s=30)
    assert machine.events.changes == 2


@pytest.mark.parametrize(
    ("values", "key", "reason"),
    [
        ({"colour": 1}, "colour", "unknown key"),
        ({"cloud_depth": 3}, "cloud_depth", "must be 0..1"),
        ({"cloud_depth": "x"}, "cloud_depth", "must be a number"),
        ({"cloud_period_s": 90.5}, "cloud_period_s", "must be an integer"),
        ({"seed": -1}, "seed", "must be 0..65535"),
        ({"base_w": 5000}, "peak_w", "must be >= base_w"),
    ],
)
def test_a_refused_variation_changes_nothing(machine, values, key, reason):
    found = refused(action=lambda: machine.set_variation(values=values))

    assert found[0] == key
    assert found[1].startswith(reason[:12])
    assert machine.plant.tuned == []
    assert machine.events.changes == 0


def test_holds_are_set_and_released(machine):
    machine.set_holds(values={"pv_w": 2500, "voltage_v": 240})
    assert machine.plant.holds == {"pv_w": 2500.0, "voltage_v": 240.0}

    machine.set_holds(values={"pv_w": None, "load_w": None})

    assert machine.plant.holds == {"voltage_v": 240.0}


@pytest.mark.parametrize(
    ("values", "key", "reason"),
    [
        ({"colour": 1}, "colour", "unknown key"),
        ({"pv_w": -5}, "pv_w", "must be 0..50000"),
        ({"pv_w": "x"}, "pv_w", "must be a number"),
    ],
)
def test_a_refused_hold_changes_nothing(machine, values, key, reason):
    assert refused(action=lambda: machine.set_holds(values=values)) == (key, reason)
    assert machine.plant.holds == {}


def test_the_state_of_charge_is_set_as_a_fraction(machine):
    machine.set_battery(values={"soc_percent": 80})

    assert machine.plant.socs == [0.8]
    assert machine.events.changes == 1


@pytest.mark.parametrize(
    ("values", "key", "reason"),
    [
        ({"soc_percent": 101}, "soc_percent", "must be 0..100"),
        ({"soc_percent": "x"}, "soc_percent", "must be a number"),
        ({}, "soc_percent", "must be a number"),
        ({"other": 1}, "other", "unknown key"),
    ],
)
def test_a_refused_state_of_charge_changes_nothing(machine, values, key, reason):
    assert refused(action=lambda: machine.set_battery(values=values)) == (key, reason)
    assert machine.plant.socs == []


def test_the_state_of_charge_cannot_be_set_without_a_battery(machine):
    machine.scenario = make_scenario(model="hs3", battery={"modules": 0})

    assert refused(action=lambda: machine.set_battery(values={"soc_percent": 5})) == (
        "soc_percent",
        "no battery fitted",
    )


def test_a_car_is_plugged_in_with_its_need_or_unplugged(machine):
    machine.set_ev(values={"plugged": True, "energy_needed_wh": 15000})
    machine.set_ev(values={"plugged": True})
    machine.set_ev(values={"plugged": False})

    assert machine.plant.ev_actions == [("in", 15000), ("in", 20000), ("out",)]
    assert machine.events.changes == 3


@pytest.mark.parametrize(
    ("values", "key", "reason"),
    [
        ({"plugged": "yes"}, "plugged", "must be true or false"),
        (
            {"plugged": True, "energy_needed_wh": 0},
            "energy_needed_wh",
            "must be 1..200000",
        ),
        (
            {"plugged": True, "energy_needed_wh": 1.5},
            "energy_needed_wh",
            "must be an integer",
        ),
        ({"other": 1}, "other", "unknown key"),
    ],
)
def test_a_refused_car_change_does_nothing(machine, values, key, reason):
    assert refused(action=lambda: machine.set_ev(values=values)) == (key, reason)
    assert machine.plant.ev_actions == []


def test_the_car_cannot_be_plugged_in_without_a_charger(machine):
    machine.scenario = make_scenario(model="hs3")

    assert refused(action=lambda: machine.set_ev(values={"plugged": True})) == (
        "plugged",
        "no EV charger fitted",
    )


def test_the_clock_is_moved_and_its_speed_changed_independently(machine):
    machine.set_clock(values={"time": "2026-08-01T12:00:00"})
    machine.set_clock(values={"speed": 60})
    machine.set_clock(values={"time": "2026-08-01T12:00:00+02:00", "speed": 0})

    assert machine.clock.set_to == [
        datetime(2026, 8, 1, 12, 0, tzinfo=UTC),
        datetime(2026, 8, 1, 10, 0, tzinfo=UTC),
    ]
    assert machine.plant.jumps == machine.clock.set_to
    assert machine.clock.speeds == [60.0, 0.0]


@pytest.mark.parametrize(
    ("values", "key", "reason"),
    [
        ({"time": "tomorrow"}, "time", "must be an ISO 8601 date and time"),
        ({"time": 5}, "time", "must be an ISO 8601 date and time"),
        ({"speed": -1}, "speed", "must be 0..100000"),
        ({"time": "2026-08-01T12:00:00", "speed": "x"}, "speed", "must be a number"),
        ({"other": 1}, "other", "unknown key"),
    ],
)
def test_a_refused_clock_change_moves_nothing(machine, values, key, reason):
    assert refused(action=lambda: machine.set_clock(values=values)) == (key, reason)
    assert machine.clock.set_to == []
    assert machine.clock.speeds == []


def test_the_energy_counters_go_back_to_their_start_values(machine):
    machine.reset_ledger()

    assert machine.plant.ledger.resets == [NOW]
    assert machine.events.changes == 1


def test_a_reset_returns_everything_to_the_scenario_and_forgets_the_saved_state(
    machine,
):
    machine.settings[ctl.BACKUP_RESERVE] = 99
    first_plant = machine.plant

    machine.reset()

    assert machine.settings[ctl.BACKUP_RESERVE] == 40
    assert machine.plant is not first_plant
    assert machine.plant.holds == {}
    assert machine.events.resets == 1
    assert machine.settings is machine.device.kwargs["settings"]


def test_an_unknown_preset_is_refused_and_changes_nothing(machine):
    machine.settings[ctl.BACKUP_RESERVE] = 99

    assert refused(action=lambda: machine.apply_preset(key="nope")) == (
        "nope",
        "is not a preset of this device",
    )
    assert machine.settings[ctl.BACKUP_RESERVE] == 99
    assert machine.events.resets == 0


def test_a_preset_returns_settings_variation_faults_and_holds_to_the_scenario_first(
    machine,
):
    machine.scenario = make_scenario(
        model="hs3",
        ev_charger={"installed": True},
        meters={"meter_a": True},
        faults=FaultState(battery=frozenset({HOT})),
    )
    machine.settings[ctl.BACKUP_RESERVE] = 99
    machine.plant.holds = {"pv_w": 10.0}
    machine.plant.faults = FaultState(inverter=frozenset({RESERVED}))
    machine.plant.seed = 99
    machine.plant.variation = Variation(cloud_depth=0.9)

    machine.apply_preset(key="high-load")

    assert machine.settings[ctl.BACKUP_RESERVE] == 40
    assert machine.plant.holds == {}
    assert machine.plant.faults == FaultState(battery=frozenset({HOT}))
    assert machine.plant.seed == machine.scenario.simulation.seed
    assert machine.plant.tuned[0] == (
        machine.scenario.simulation.seed,
        machine.scenario.variation,
        machine.scenario.site.load,
    )


def test_a_preset_applies_its_variation_after_returning_to_the_scenario(machine):
    machine.apply_preset(key="high-load")

    _seed, variation, load = machine.plant.tuned[-1]
    assert load == LoadConfig(base_w=1500, peak_w=9000)
    assert variation.spike_chance > 0.3


def test_a_preset_keeps_the_time_the_speed_the_energy_totals_and_the_charge(machine):
    machine.clock.speed = 30.0
    first_plant = machine.plant
    first_clock = machine.clock

    machine.apply_preset(key="high-load")

    assert machine.plant is first_plant
    assert machine.clock is first_clock
    assert machine.clock.set_to == []
    assert machine.clock.speed == 30.0
    assert machine.plant.jumps == []
    assert machine.plant.ledger.cleared == 0
    assert machine.plant.ledger.resets == []
    assert machine.plant.ledger.restored == []
    assert machine.plant.socs == []
    assert machine.plant.battery.soc == 0.5


def test_a_preset_that_sets_the_charge_changes_only_the_charge(machine):
    machine.apply_preset(key="battery-full")

    assert machine.plant.socs == [1.0]
    assert machine.clock.set_to == []
    assert machine.plant.ledger.resets == []


def test_a_preset_marks_the_state_changed_without_forgetting_the_saved_state(machine):
    machine.apply_preset(key="clear-sky")

    assert machine.events.resets == 0
    assert machine.events.changes > 0


def test_a_fault_preset_sets_every_bit_that_reports_the_named_condition(machine):
    machine.apply_preset(key="grid-lost")

    assert machine.plant.faults.inverter == {GRID_LOST, GRID_LOST_B}


def test_a_battery_preset_sets_the_charge_or_the_fault(machine):
    machine.apply_preset(key="battery-empty")
    assert machine.plant.socs == [0.05]

    machine.apply_preset(key="battery-too-hot-to-charge")
    assert machine.plant.faults.battery == {HOT}

    machine.apply_preset(key="battery-pack-fault")
    assert machine.plant.faults.packs == (PackCodes(pack=1, fault=1),)


def test_the_charging_preset_plugs_a_car_in_and_selects_the_standard_mode(machine):
    machine.apply_preset(key="ev-charging")

    assert machine.device.written == [{"ev_mode": 1}]
    assert machine.plant.ev_actions == [("in", 20000)]


def test_the_exported_scenario_carries_the_running_state_the_scenario_can_express(
    machine,
):
    machine.plant.seed = 33
    machine.plant.variation = Variation(cloud_depth=0.2)
    machine.plant.load = LoadConfig(base_w=1, peak_w=2)
    machine.plant.faults = FaultState(inverter=frozenset({GRID_LOST}))
    machine.clock.speed = 5.0

    label, exported = machine.export_scenario()

    assert label == "yaml"
    assert exported.simulation.seed == 33
    assert exported.simulation.start == NOW
    assert exported.simulation.speed == 5.0
    assert exported.site.load == LoadConfig(base_w=1, peak_w=2)
    assert exported.variation == Variation(cloud_depth=0.2)
    assert exported.faults == machine.plant.faults
    assert exported.battery == dataclasses.replace(
        machine.scenario.battery, initial_soc_percent=50
    )


@pytest.mark.parametrize(
    ("soc", "percent"), [(0.496, 50), (0.0, 0), (1.0, 100), (1.3, 100), (-0.2, 0)]
)
def test_the_exported_scenario_starts_the_battery_at_the_charge_it_has_now(
    machine, soc, percent
):
    machine.plant.battery.soc = soc

    _label, exported = machine.export_scenario()

    assert exported.battery.initial_soc_percent == percent


def test_the_exported_scenario_leaves_a_missing_battery_alone(machine):
    machine.scenario = make_scenario(model="hs3", battery={"modules": 0})

    _label, exported = machine.export_scenario()

    assert exported.battery == machine.scenario.battery


def test_a_snapshot_holds_what_a_restart_keeps(machine):
    machine.settings[ctl.BACKUP_RESERVE] = 77
    machine.plant.holds = {"pv_w": 10.0}
    machine.plant.faults = FaultState(
        battery=frozenset({HOT}), packs=(PackCodes(pack=1, warning=2),)
    )

    snapshot = machine.snapshot()

    assert snapshot["settings"][ctl.BACKUP_RESERVE] == 77
    assert snapshot["holds"] == {"pv_w": 10.0}
    assert snapshot["faults"]["battery"] == {"0x400B:10": True}
    assert snapshot["faults"]["packs"] == {"1": {"fault": 0, "warning": 2}}
    assert snapshot["variation"]["base_w"] == 300
    assert snapshot["soc_percent"] == 50.0
    assert snapshot["ledger_wh"] == {"pv": 5.0}
    assert snapshot["ledger_periods"] == {
        "day": "2026-07-04",
        "starts_wh": machine.plant.ledger.starts_wh(),
    }
    assert snapshot["clock"] == {"time": NOW.isoformat(), "speed": 1.0}
    assert snapshot["ev"] == {"remaining_wh": None, "suppressed_until_s": 0}


def test_a_snapshot_holds_a_hand_plugged_car_and_a_window_kept_shut(machine):
    machine.plant.ev.hand = HandState(remaining_wh=1500, suppressed_until_s=99)

    assert machine.snapshot()["ev"] == {
        "remaining_wh": 1500,
        "suppressed_until_s": 99,
    }


def test_restoring_a_snapshot_brings_back_the_hand_plugged_car(machine):
    snapshot = {
        **machine.snapshot(),
        "ev": {"remaining_wh": 1500, "suppressed_until_s": 99},
    }

    machine.restore(snapshot=snapshot)

    assert machine.plant.restored_ev == [
        HandState(remaining_wh=1500, suppressed_until_s=99)
    ]


def test_a_complete_hand_plugged_car_is_saved_and_restored_as_plugged_in(machine):
    machine.plant.ev.hand = HandState(remaining_wh=0, suppressed_until_s=0)
    snapshot = machine.snapshot()

    machine.restore(snapshot=snapshot)

    assert snapshot["ev"]["remaining_wh"] == 0
    assert machine.plant.restored_ev == [
        HandState(remaining_wh=0, suppressed_until_s=0)
    ]


def test_a_snapshot_without_car_state_restores_as_no_hand_state(machine):
    snapshot = machine.snapshot()
    del snapshot["ev"]

    machine.restore(snapshot=snapshot)

    assert machine.plant.restored_ev == [
        HandState(remaining_wh=None, suppressed_until_s=0)
    ]


@pytest.mark.parametrize(
    "damage",
    [
        "text",
        {"remaining_wh": "lots"},
        {"remaining_wh": -1},
        {"remaining_wh": 200_001},
        {"remaining_wh": 1.5},
        {"suppressed_until_s": -1},
        {"suppressed_until_s": 1 << 41},
        {"suppressed_until_s": True},
        {"unknown": 1},
    ],
)
def test_unreadable_car_state_starts_from_the_scenario_and_keeps_the_file(
    machine, damage
):
    snapshot = {**machine.snapshot(), "ev": damage}
    machine.settings[ctl.BACKUP_RESERVE] = 99

    with pytest.raises(ControlError):
        machine.restore(snapshot=snapshot)

    assert machine.settings[ctl.BACKUP_RESERVE] == 40
    assert machine.events.resets == 0


def test_car_state_is_refused_when_no_charger_is_fitted(machine):
    machine.scenario = make_scenario(model="hs3")
    snapshot = {**machine.snapshot(), "ev": {"remaining_wh": 500}}

    with pytest.raises(ControlError) as caught:
        machine.restore(snapshot=snapshot)

    assert caught.value.key == "ev"
    assert machine.events.resets == 0


def test_an_empty_car_state_is_accepted_when_no_charger_is_fitted(machine):
    machine.scenario = make_scenario(model="hs3")

    machine.restore(snapshot=machine.snapshot())

    assert machine.events.resets == 0


def test_restoring_a_snapshot_brings_back_everything_it_holds(machine):
    machine.settings[ctl.EMS_ENABLE] = 0
    machine.plant.holds = {"pv_w": 10.0}
    machine.plant.faults = FaultState(inverter=frozenset({GRID_LOST}))
    machine.plant.seed = 99
    snapshot = machine.snapshot()
    snapshot["settings"][ctl.BACKUP_RESERVE] = 11
    snapshot["settings"][ctl.EMS_ENABLE] = 8
    snapshot["saved_app_mode"] = 2
    snapshot["ledger_wh"] = {"pv": 123.0}
    machine.plant.holds = {}
    machine.plant.faults = FaultState()

    machine.restore(snapshot=snapshot)

    assert machine.settings[ctl.BACKUP_RESERVE] == 11
    assert machine.plant.holds == {"pv_w": 10.0}
    assert machine.plant.faults.inverter == {GRID_LOST}
    assert machine.plant.seed == 99
    assert machine.clock.set_to == [NOW]
    assert machine.plant.ledger.restored == [
        ({"pv": 123.0}, NOW, machine.plant.ledger.starts_wh(), date(2026, 7, 4))
    ]
    machine.telemetry()
    assert machine.settings[ctl.APP_MODE] == 2
    assert machine.plant.keepalives == [777]


def test_restoring_without_a_battery_leaves_the_charge_alone(machine):
    machine.scenario = make_scenario(model="hs3", battery={"modules": 0})
    snapshot = machine.snapshot()
    snapshot["soc_percent"] = None

    machine.restore(snapshot=snapshot)

    assert machine.plant.socs == []


@pytest.mark.parametrize(
    "damage",
    [
        {"clock": None},
        {"settings": 5},
        {"settings": {"nothing": 1}},
        {"settings": {ctl.APP_MODE: "text"}},
        {"settings": {ctl.APP_MODE: True}},
        {"variation": {"cloud_depth": 9}},
        {"holds": []},
        {"faults": {"inverter": {"0x4005:99": True}}},
        {"soc_percent": "x"},
        {"ledger_wh": {"pv": -1}},
        {"ledger_wh": None},
        {"ledger_periods": 5},
        {"ledger_periods": {"day": "2026-07-04"}},
        {"ledger_periods": {"day": "x", "starts_wh": {}}},
        {"ledger_periods": {"day": None, "starts_wh": {}}},
        {"ledger_periods": {"day": "2026-07-04", "starts_wh": []}},
        {"ledger_periods": {"day": "2026-07-04", "starts_wh": {"week": {}}}},
        {"ledger_periods": {"day": "2026-07-04", "starts_wh": {"today": {}}}},
        {
            "ledger_periods": {
                "day": "2026-07-04",
                "starts_wh": {"today": {"pv": "x"}, "month": {}, "year": {}},
            }
        },
        {
            "ledger_periods": {
                "day": "2026-07-04",
                "starts_wh": {"today": {"pv": 6.0}, "month": {}, "year": {}},
            }
        },
        {"ledger_periods": {"day": "2026-07-04", "starts_wh": {}, "extra": 1}},
    ],
)
def test_an_unreadable_snapshot_starts_from_the_scenario_and_keeps_the_file(
    machine, damage
):
    snapshot = {**machine.snapshot(), **damage}
    machine.settings[ctl.BACKUP_RESERVE] = 99

    with pytest.raises(ControlError):
        machine.restore(snapshot=snapshot)

    assert machine.settings[ctl.BACKUP_RESERVE] == 40
    assert machine.events.resets == 0


@pytest.mark.parametrize(
    "reason",
    [
        "value outside enumeration",
        "value below minimum",
        "value above maximum",
        "text must be ASCII",
        "text is too long",
        "is not a whole raw value",
    ],
)
def test_a_refused_setting_starts_from_the_scenario_and_keeps_the_file(machine, reason):
    snapshot = machine.snapshot()
    snapshot["settings"][ctl.BACKUP_RESERVE] = 77
    machine.device.refused_stored[(ctl.BACKUP_RESERVE, 77)] = reason
    machine.settings[ctl.CHARGE_CEILING] = 55

    with pytest.raises(ControlError) as caught:
        machine.restore(snapshot=snapshot)

    assert (caught.value.key, caught.value.reason) == (ctl.BACKUP_RESERVE, reason)
    assert machine.settings == machine.initial
    assert machine.clock.set_to == []
    assert machine.events.resets == 0


def test_a_snapshot_the_device_accepts_is_restored(machine):
    snapshot = machine.snapshot()
    snapshot["settings"][ctl.BACKUP_RESERVE] = 77

    machine.restore(snapshot=snapshot)

    assert machine.settings[ctl.BACKUP_RESERVE] == 77
    assert machine.events.resets == 0


def test_a_snapshot_without_the_borrowed_application_mode_keeps_the_current_one(
    machine,
):
    snapshot = machine.snapshot()
    del snapshot["saved_app_mode"]
    machine._saved_app_mode = 4

    machine.restore(snapshot=snapshot)

    assert machine._saved_app_mode == 4


def test_a_restored_system_gets_the_full_ems_timeout_from_the_restored_moment(machine):
    snapshot = machine.snapshot()
    snapshot["settings"][ctl.EMS_ENABLE] = 8
    machine.plant.second = 4242

    machine.restore(snapshot=snapshot)

    assert machine.plant.keepalives == [4242]


def test_live_readings_are_rounded_for_display(machine, monkeypatch):
    monkeypatch.setitem(TELEMETRY, "pv_w", 11780.955218209907)
    monkeypatch.setitem(TELEMETRY, "soc_percent", 49.98765)
    monkeypatch.setitem(TELEMETRY, "grid_r_v", 231.58472)
    monkeypatch.setitem(TELEMETRY, "frequency_hz", 50.034295730912156)

    readings = {r["label"]: r["value"] for r in machine.state()["readings"]}

    assert readings["PV power"] == 11781
    assert readings["Battery state of charge"] == 50.0
    assert readings["Grid voltage"] == 231.6
    assert readings["Grid frequency"] == 50.03


def test_readings_never_show_a_negative_zero(machine, monkeypatch):
    monkeypatch.setitem(TELEMETRY, "battery_w", -0.04)

    readings = {r["label"]: r["value"] for r in machine.state()["readings"]}

    assert str(readings["Battery power"]) == "0.0"


def test_the_state_reports_the_current_value_of_each_reading_a_hold_can_fix(
    machine, monkeypatch
):
    monkeypatch.setitem(TELEMETRY, "pv_w", 1234.4)
    monkeypatch.setitem(TELEMETRY, "load_w", 560.6)
    monkeypatch.setitem(TELEMETRY, "ev_power_w", 0.0)
    monkeypatch.setitem(TELEMETRY, "grid_r_v", 231.58472)
    monkeypatch.setitem(TELEMETRY, "frequency_hz", 50.034295)

    assert machine.state()["hold_readings"] == {
        "pv_w": 1234,
        "load_w": 561,
        "voltage_v": 231.6,
        "frequency_hz": 50.03,
    }


def test_the_household_load_leaves_out_what_the_charger_draws(machine, monkeypatch):
    monkeypatch.setitem(TELEMETRY, "load_w", 11_697.0)
    monkeypatch.setitem(TELEMETRY, "ev_power_w", 11_000.0)

    state = machine.state()

    assert state["card_readings"]["household_load_w"] == 697
    assert state["hold_readings"]["load_w"] == 697
    assert state["node_readings"]["ev_power_w"] == 11_000
    readings = {r["label"]: r["value"] for r in state["readings"]}
    assert readings["Household load"] == 697


def test_the_state_gives_each_card_reading_by_the_name_the_description_gives(machine):
    names = {
        reading["name"]
        for card in machine.describe()["cards"]
        for reading in card["readings"]
    }

    state = machine.state()

    assert set(state["card_readings"]) == names
    assert state["card_readings"]["operating_mode"].startswith("2 ")
    assert state["card_readings"]["car"] in {"Plugged in", "Not plugged in"}


def test_restoring_a_snapshot_brings_back_where_each_energy_period_started(machine):
    snapshot = {
        **machine.snapshot(),
        "ledger_wh": {"pv": 10.0},
        "ledger_periods": {
            "day": "2026-07-03",
            "starts_wh": {
                "today": {"pv": 4.0},
                "month": {"pv": 2.0},
                "year": {"pv": 0.0},
            },
        },
    }

    machine.restore(snapshot=snapshot)

    assert machine.plant.ledger.restored == [
        (
            {"pv": 10.0},
            NOW,
            {"today": {"pv": 4.0}, "month": {"pv": 2.0}, "year": {"pv": 0.0}},
            date(2026, 7, 3),
        )
    ]


def test_a_snapshot_without_energy_periods_restores_only_the_totals(machine):
    snapshot = machine.snapshot()
    del snapshot["ledger_periods"]

    machine.restore(snapshot=snapshot)

    assert machine.plant.ledger.restored == [({"pv": 5.0}, NOW, None, None)]


def test_a_snapshot_holds_only_the_settings_a_client_can_write(machine):
    snapshot = machine.snapshot()

    assert set(snapshot["settings"]) == {
        ctl.APP_MODE,
        ctl.BACKUP_RESERVE,
        ctl.EMS_ENABLE,
        "a_setting",
        "scaled_limit",
    }


def test_restoring_skips_saved_values_of_read_only_registers(machine):
    snapshot = machine.snapshot()
    snapshot["settings"]["meter_enable"] = 9

    machine.restore(snapshot=snapshot)

    assert machine.settings["meter_enable"] == 3
    assert machine.events.resets == 0


def test_restoring_still_refuses_a_name_that_is_not_a_register(machine):
    snapshot = machine.snapshot()
    snapshot["settings"]["nothing"] = 1

    assert refused(action=lambda: machine.restore(snapshot=snapshot)) == (
        "nothing",
        "is not a setting",
    )


def test_a_scaled_setting_is_shown_to_the_decimals_of_its_scale(machine):
    machine.settings["scaled_limit"] = 65535 * 0.0001

    assert machine.state()["settings"]["scaled_limit"] == {
        "raw": 65535,
        "value": 6.5535,
    }


def test_the_description_lists_the_cards_and_nodes_of_the_fitted_equipment(machine):
    description = machine.describe()

    assert [card["key"] for card in description["cards"]] == [
        "solar",
        "house",
        "grid",
        "battery",
        "ev_charger",
        "inverter",
    ]
    assert [node["kind"] for node in description["nodes"]] == [
        "solar",
        "grid",
        "house",
        "battery",
        "ev_charger",
    ]
    settings = {entry["name"]: entry for entry in description["settings"]}
    assert settings[ctl.BACKUP_RESERVE]["scenario"] == {"raw": 40, "value": 40}


def test_a_battery_less_machine_has_no_battery_card_or_node(machine):
    machine.scenario = make_scenario(model="hs3", battery={"modules": 0})

    description = machine.describe()

    assert "battery" not in [card["key"] for card in description["cards"]]
    assert "battery" not in [node["kind"] for node in description["nodes"]]
    assert "battery_w" not in machine.state()["node_readings"]


def test_external_pv_is_a_node_with_its_reading_only_when_meter_b_is_fitted(machine):
    machine.scenario = make_scenario(model="hs3", meters={"meter_b": True})
    fitted = machine.describe()
    fitted_state = machine.state()
    machine.scenario = make_scenario(model="hs3", meters={"meter_b": False})
    absent = machine.describe()

    assert "external_pv" in [node["kind"] for node in fitted["nodes"]]
    assert fitted_state["node_readings"]["ext_pv_w"] == 7
    assert fitted_state["card_readings"]["ext_pv_w"] == 7
    assert "external_pv" not in [node["kind"] for node in absent["nodes"]]
    assert "external_pv" not in [card["key"] for card in absent["cards"]]
    assert "ext_pv_w" not in machine.state()["node_readings"]


def test_the_state_gives_each_diagram_reading_by_the_name_the_description_gives(
    machine,
):
    names = {
        reading["name"]
        for node in machine.describe()["nodes"]
        for reading in node["readings"]
    }

    assert set(machine.state()["node_readings"]) == names
    assert machine.state()["node_readings"]["pv_w"] == 1


def test_nothing_differs_from_the_scenario_at_start(machine):
    assert machine.state()["changes"] == {
        "holds": [],
        "faults": {"inverter": 0, "battery": 0, "ev_charger": 0},
        "settings": [],
        "variation": [],
        "link": [],
    }


def test_the_changes_name_every_hold_fault_setting_and_variation_that_differs(machine):
    machine.settings[ctl.BACKUP_RESERVE] = 99
    machine.plant.holds = {"load_w": 10.0, "pv_w": 20.0}
    machine.plant.faults = FaultState(
        inverter=frozenset({GRID_LOST, GRID_LOST_B}),
        packs=(PackCodes(pack=1, fault=1),),
    )
    machine.plant.seed = 9
    machine.plant.variation = Variation(cloud_depth=0.9)

    assert machine.state()["changes"] == {
        "holds": ["pv_w", "load_w"],
        "faults": {"inverter": 2, "battery": 1, "ev_charger": 0},
        "settings": [ctl.BACKUP_RESERVE],
        "variation": ["cloud_depth", "seed"],
        "link": [],
    }


def test_the_changes_clear_when_the_machine_is_reset(machine):
    machine.settings[ctl.BACKUP_RESERVE] = 99
    machine.plant.holds = {"pv_w": 20.0}

    machine.reset()

    changes = machine.state()["changes"]
    assert (changes["holds"], changes["settings"]) == ([], [])


def changed_system(machine):
    machine.scenario = make_scenario(
        model="hs3",
        ev_charger={"installed": True},
        faults=FaultState(
            battery=frozenset({HOT}), packs=(PackCodes(pack=2, warning=1),)
        ),
    )
    machine.plant.seed = 99
    machine.plant.variation = Variation(
        cloud_depth=0.9, drift_depth=0.5, voltage_swing_v=10.0
    )
    machine.plant.load = LoadConfig(base_w=1, peak_w=2)
    machine.plant.holds = {
        "pv_w": 1.0,
        "load_w": 2.0,
        "voltage_v": 230.0,
        "frequency_hz": 50.0,
    }
    machine.plant.faults = FaultState(
        inverter=frozenset({GRID_LOST}),
        battery=frozenset({HOT, FaultBit(register=0x400B, bit=3)}),
        ev_charger=frozenset({CHARGER}),
        packs=(PackCodes(pack=1, fault=3),),
    )


def observed(machine):
    plant = machine.plant
    return {
        "seed": plant.seed,
        "cloud_depth": plant.variation.cloud_depth,
        "drift_depth": plant.variation.drift_depth,
        "voltage_swing_v": plant.variation.voltage_swing_v,
        "load": (plant.load.base_w, plant.load.peak_w),
        "holds": set(plant.holds),
        "inverter": plant.faults.inverter,
        "battery": plant.faults.battery,
        "ev_charger": plant.faults.ev_charger,
        "packs": plant.faults.packs,
    }


ALL_HOLDS = {"pv_w", "load_w", "voltage_v", "frequency_hz"}
SCENARIO_LOAD = (300, 3000)
DEFAULT_VARIATION = Variation()


@pytest.mark.parametrize(
    ("card", "returned"),
    [
        (
            "solar",
            {
                "cloud_depth": DEFAULT_VARIATION.cloud_depth,
                "holds": ALL_HOLDS - {"pv_w"},
            },
        ),
        (
            "house",
            {
                "drift_depth": DEFAULT_VARIATION.drift_depth,
                "load": SCENARIO_LOAD,
                "holds": ALL_HOLDS - {"load_w"},
            },
        ),
        (
            "grid",
            {
                "voltage_swing_v": DEFAULT_VARIATION.voltage_swing_v,
                "holds": {"pv_w", "load_w"},
            },
        ),
        ("inverter", {"seed": 7, "inverter": frozenset()}),
        (
            "battery",
            {"battery": frozenset({HOT}), "packs": (PackCodes(pack=2, warning=1),)},
        ),
        ("ev_charger", {"ev_charger": frozenset()}),
    ],
)
def test_a_card_reset_returns_only_that_cards_parameters_holds_and_faults(
    machine, card, returned
):
    changed_system(machine)
    before = observed(machine)

    machine.reset_card(key=card)

    assert observed(machine) == {**before, **returned}


def test_a_card_reset_leaves_settings_the_charge_the_car_the_clock_and_the_counters(
    machine,
):
    changed_system(machine)
    machine.settings[ctl.BACKUP_RESERVE] = 99
    for card in ("solar", "house", "grid", "battery", "ev_charger", "inverter"):
        machine.reset_card(key=card)

    assert machine.settings[ctl.BACKUP_RESERVE] == 99
    assert machine.plant.socs == []
    assert machine.plant.ev_actions == []
    assert machine.clock.set_to == []
    assert machine.plant.jumps == []
    assert machine.plant.ledger.cleared == 0
    assert machine.plant.ledger.resets == []
    assert machine.events.resets == 0
    assert machine.events.changes > 0


@pytest.mark.parametrize("card", ["nope", "", "battery"])
def test_an_unknown_card_or_one_that_is_not_fitted_is_refused_and_changes_nothing(
    machine, card
):
    changed_system(machine)
    machine.scenario = make_scenario(
        model="hs3", battery={"modules": 0}, ev_charger={"installed": True}
    )
    before = observed(machine)
    changes = machine.events.changes

    assert refused(action=lambda: machine.reset_card(key=card)) == (
        card,
        "is not a card of this device",
    )

    assert observed(machine) == before
    assert machine.events.changes == changes


def test_the_register_snapshot_lists_every_block_without_reading_as_a_client(machine):
    blocks = machine.registers()["blocks"]

    assert [(block["start"], block["end"]) for block in blocks] == [
        ("0x0000", "0x4000"),
        ("0x3647", "0x3647"),
    ]
    fields = {field["name"]: field for field in blocks[0]["fields"]}
    assert fields["a_setting"]["words"] == [1]
    assert fields["a_setting"]["last_read"] is None
    assert machine.device.written == []


def test_the_register_snapshot_takes_when_a_client_last_read_from_the_recorder(
    machine,
):
    times = {1: 12.5}
    reading = Machine(
        scenario=machine.scenario,
        monotonic=lambda: 0.0,
        wiring=Wiring(last_read=lambda *, address: times.get(address)),
    )

    fields = {
        field["name"]: field for field in reading.registers()["blocks"][0]["fields"]
    }

    assert fields["a_setting"]["last_read"] == 12.5
    assert fields["meter_enable"]["last_read"] is None


WALL_TIME = 100.0
SCENARIO_LINK = LinkSettings(latency_ms=50, refused_blocks=(RefusedBlock(1, 2, 3),))


@pytest.fixture
def link_machine(made):
    link = Link(seed=0)
    result = Machine(
        scenario=make_scenario(
            model="hs3",
            ev_charger={"installed": True},
            meters={"meter_a": True},
            link=SCENARIO_LINK,
        ),
        monotonic=lambda: 0.0,
        wiring=Wiring(
            link=link,
            wall_clock=lambda: WALL_TIME,
        ),
    )
    result.link = link
    return result


def test_the_link_starts_as_the_scenario_has_it(link_machine):
    state = link_machine.state()

    assert link_machine.link.settings == SCENARIO_LINK
    assert state["link"]["latency_ms"] == 50
    assert state["link"]["refused_blocks"] == [{"start": 1, "end": 2, "code": 3}]
    assert state["changes"]["link"] == []


def test_the_description_gives_each_link_setting_its_bounds_and_scenario_value(
    link_machine,
):
    settings = {
        setting["name"]: setting
        for setting in link_machine.describe()["link"]["settings"]
    }

    assert settings["latency_ms"] == {
        "name": "latency_ms",
        "kind": "whole",
        "minimum": 0,
        "maximum": 60_000,
        "unit": "ms",
        "scenario": 50,
    }
    assert settings["busy_percent"]["kind"] == "percent"
    assert settings["busy_percent"]["maximum"] == 100
    assert settings["offline"]["kind"] == "flag"
    assert settings["refused_blocks"] == {
        "name": "refused_blocks",
        "kind": "blocks",
        "address_bounds": [0, 65535],
        "code_bounds": [0, 255],
        "scenario": [{"start": 1, "end": 2, "code": 3}],
    }


def test_link_settings_are_applied_to_the_link_and_reported_as_changes(link_machine):
    link_machine.set_link(
        values={
            "latency_ms": 800,
            "busy_percent": 12.5,
            "offline": True,
            "refused_blocks": [{"start": 4, "end": 9, "code": 0}],
        }
    )

    settings = link_machine.link.settings
    assert (settings.latency_ms, settings.busy_percent, settings.offline) == (
        800,
        12.5,
        True,
    )
    assert settings.refused_blocks == (RefusedBlock(start=4, end=9, code=0),)
    assert link_machine.state()["changes"]["link"] == [
        "latency_ms",
        "busy_percent",
        "offline",
        "refused_blocks",
    ]
    assert link_machine.state()["link"]["jitter_ms"] == 0


@pytest.mark.parametrize(
    ("values", "key", "reason"),
    [
        ({"nothing": 1}, "nothing", "unknown key"),
        ({"latency_ms": "x"}, "latency_ms", "must be a number"),
        ({"latency_ms": True}, "latency_ms", "must be a number"),
        ({"latency_ms": -1}, "latency_ms", "must be 0..60000"),
        ({"latency_ms": 1.5}, "latency_ms", "must be an integer"),
        ({"busy_percent": 101}, "busy_percent", "must be 0..100"),
        ({"offline": 1}, "offline", "must be true or false"),
        ({"refused_blocks": 5}, "refused_blocks", "must be a list"),
        ({"refused_blocks": [5]}, "refused_blocks[0]", "must be a mapping"),
        (
            {"refused_blocks": [{"start": 1, "end": 2}]},
            "refused_blocks[0].code",
            "is required",
        ),
        (
            {"refused_blocks": [{"start": 1, "end": 2, "code": 1, "x": 1}]},
            "x",
            "unknown key",
        ),
        (
            {"refused_blocks": [{"start": 9, "end": 2, "code": 1}]},
            "refused_blocks[0].end",
            "must be >= start",
        ),
        (
            {"refused_blocks": [{"start": 1, "end": 2, "code": 256}]},
            "refused_blocks[0].code",
            "must be 0..255",
        ),
        (
            {"offline_seconds": 30},
            "offline_seconds",
            "must be <= offline_period_seconds",
        ),
        (
            {"lockout_requests": 5},
            "lockout_window_seconds",
            "must be >= 1 when lockout_requests is set",
        ),
    ],
)
def test_a_refused_link_setting_names_its_key_and_changes_nothing(
    link_machine, values, key, reason
):
    assert refused(action=lambda: link_machine.set_link(values=values)) == (key, reason)
    assert link_machine.link.settings == SCENARIO_LINK


def test_a_refused_link_setting_among_valid_ones_changes_none_of_them(link_machine):
    refused(
        action=lambda: link_machine.set_link(
            values={"latency_ms": 9, "busy_percent": 500}
        )
    )

    assert link_machine.link.settings == SCENARIO_LINK


def test_the_module_state_follows_the_link_and_the_wall_clock(link_machine):
    assert link_machine.state()["module"]["status"] == "online"

    link_machine.set_link(values={"offline_seconds": 50, "offline_period_seconds": 60})

    assert link_machine.state()["module"]["status"] == "offline"


def test_dropping_connections_asks_the_link_to_drop_them(link_machine):
    before = link_machine.link.drop_generation

    link_machine.drop_connections()

    assert link_machine.link.drop_generation == before + 1


def lock_out(*, machine):
    snapshot = machine.snapshot()
    snapshot["lockout"] = {"addresses": ["10.0.0.9"], "whole_port": False}
    machine.restore(snapshot=snapshot)


def test_resetting_the_module_clears_a_lockout_and_marks_the_state_changed(
    link_machine,
):
    lock_out(machine=link_machine)
    assert link_machine.state()["module"]["status"] == "locked_out"

    link_machine.reset_module()

    assert link_machine.state()["module"]["status"] == "online"
    assert link_machine.link.lockout_state().addresses == ()


def test_a_reset_returns_the_link_to_the_scenario_and_clears_a_lockout(link_machine):
    link_machine.set_link(values={"latency_ms": 9})
    lock_out(machine=link_machine)

    link_machine.reset()

    assert link_machine.link.settings == SCENARIO_LINK
    assert link_machine.state()["module"]["status"] == "online"


def test_a_preset_returns_the_link_to_the_scenario_then_applies_its_own_changes(
    link_machine,
):
    link_machine.set_link(values={"latency_ms": 9, "busy_percent": 50})
    lock_out(machine=link_machine)

    link_machine.apply_preset(key="flaky-link")

    settings = link_machine.link.settings
    assert settings.latency_ms == 50
    assert settings.busy_percent == 0
    assert (settings.no_answer_percent, settings.dropped_connection_percent) == (5, 2)
    assert link_machine.link.lockout_state().addresses == ()


@pytest.mark.parametrize("key", ["clear-sky", "high-load"])
def test_a_preset_without_link_changes_leaves_the_link_as_the_scenario(
    link_machine, key
):
    link_machine.set_link(values={"latency_ms": 9})

    link_machine.apply_preset(key=key)

    assert link_machine.link.settings == SCENARIO_LINK


def test_the_locked_out_preset_locks_the_whole_port_above_its_threshold(link_machine):
    link_machine.apply_preset(key="module-locked-out")

    settings = link_machine.link.settings
    assert (
        settings.lockout_requests,
        settings.lockout_window_seconds,
        settings.lockout_whole_port,
    ) == (120, 60, True)


def draws(*, machine):
    return [
        machine.link.decide_request(
            client="c", sequence=n, start=0, count=1, now=0.0
        ).fault
        for n in range(1, 60)
    ]


def test_the_links_draws_follow_the_simulation_seed_in_force(link_machine):
    link_machine.set_link(values={"busy_percent": 50})

    link_machine.set_variation(values={"seed": 11})
    first = draws(machine=link_machine)
    link_machine.set_variation(values={"seed": 12})
    second = draws(machine=link_machine)
    link_machine.set_variation(values={"seed": 11})

    assert first != second
    assert draws(machine=link_machine) == first


def test_a_return_to_the_scenario_puts_the_links_seed_back(link_machine):
    link_machine.set_variation(values={"seed": 11})
    link_machine.set_link(values={"busy_percent": 50})

    link_machine.apply_preset(key="clear-sky")
    link_machine.set_link(values={"busy_percent": 50})
    after_preset = draws(machine=link_machine)
    link_machine.reset()
    link_machine.set_link(values={"busy_percent": 50})

    assert draws(machine=link_machine) == after_preset


def test_the_register_snapshot_shows_the_blocks_the_link_refuses(link_machine):
    link_machine.set_link(
        values={"refused_blocks": [{"start": 0x3647, "end": 0x3647, "code": 0}]}
    )

    blocks = link_machine.registers()["blocks"]

    assert [block["refusal"] for block in blocks] == [
        {"code": 0, "model": False, "link": True}
    ] * 2


def test_the_register_snapshot_leaves_blocks_the_link_does_not_touch_alone(
    link_machine,
):
    link_machine.set_link(
        values={"refused_blocks": [{"start": 0x5000, "end": 0x5001, "code": 0}]}
    )

    blocks = link_machine.registers()["blocks"]

    assert [block["refusal"] for block in blocks] == [None, None]


def test_the_exported_scenario_carries_the_running_link(link_machine):
    link_machine.set_link(values={"latency_ms": 9})

    assert link_machine.export_scenario()[1].link.latency_ms == 9


def test_a_snapshot_holds_the_link_and_a_lockout_and_restoring_brings_them_back(
    link_machine,
):
    link_machine.set_link(values={"latency_ms": 9, "lockout_whole_port": True})
    link_machine.restore(
        snapshot={
            **link_machine.snapshot(),
            "lockout": {"addresses": ["10.0.0.9"], "whole_port": True},
        }
    )
    snapshot = link_machine.snapshot()
    link_machine.reset()

    link_machine.restore(snapshot=snapshot)

    assert snapshot["link"]["latency_ms"] == 9
    assert snapshot["lockout"] == {"addresses": ["10.0.0.9"], "whole_port": True}
    assert link_machine.link.settings.latency_ms == 9
    assert link_machine.link.lockout_state().addresses == ("10.0.0.9",)
    assert link_machine.link.lockout_state().whole_port is True


@pytest.mark.parametrize(
    "damage",
    [
        {"link": None},
        {"link": {"latency_ms": "x"}},
        {"lockout": None},
        {"lockout": {"addresses": "x", "whole_port": False}},
        {"lockout": {"addresses": [1], "whole_port": False}},
        {"lockout": {"addresses": [], "whole_port": "x"}},
        {"lockout": {"addresses": [], "whole_port": False, "extra": 1}},
    ],
)
def test_an_unreadable_saved_link_starts_from_the_scenario(link_machine, damage):
    snapshot = {**link_machine.snapshot(), **damage}
    link_machine.set_link(values={"latency_ms": 9})

    with pytest.raises(ControlError):
        link_machine.restore(snapshot=snapshot)

    assert link_machine.link.settings == SCENARIO_LINK
