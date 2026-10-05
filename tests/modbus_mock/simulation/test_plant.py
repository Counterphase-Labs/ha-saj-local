from datetime import timedelta

import pytest

from saj_modbus_mock.registers import EPOCH
from saj_modbus_mock.simulation import control as ctl
from saj_modbus_mock.simulation import plant as plant_module
from saj_modbus_mock.simulation.balance import BalanceResult
from saj_modbus_mock.simulation.control import Command
from saj_modbus_mock.simulation.environment import EnvironmentSample
from tests.modbus_mock.builders import START, make_scenario

STEP = plant_module.INTEGRATION_STEP_S


class StubEnvironment:
    def __init__(self, *, strings=(2000.0, 1000.0), load=800.0, external=500.0):
        self.calls = []
        self.strings = strings
        self.load = load
        self.external = external

    def sample(self, *, second, **_unused):
        self.calls.append(second)
        load = self.load(second) if callable(self.load) else self.load
        return EnvironmentSample(
            string_powers_w=self.strings, load_w=load, external_pv_w=self.external
        )


class StubBattery:
    def __init__(self, *, modules, soc):
        self.modules = modules
        self.soc = soc
        self.applied = []
        self.limit_steps = []

    def max_charge_w(self, *, dt_s, **_unused):
        self.limit_steps.append(dt_s)
        return 111.0

    def max_discharge_w(self, *, dt_s, **_unused):
        self.limit_steps.append(dt_s)
        return 222.0

    def pack_voltage_v(self):
        return 333.0

    def apply(self, *, power_w, dt_s):
        self.applied.append((power_w, dt_s))


class StubController:
    def __init__(self, *, command):
        self.command_to_give = command
        self.calls = []

    def command(self, *, second, soc, **_unused):
        self.calls.append((second, soc))
        return self.command_to_give


class StubEv:
    def __init__(self, *, power=0.0):
        self.power = power
        self.evaluated = []
        self.integrated = []

    def evaluate(self, *, surplus_w, step_s, **_unused):
        self.evaluated.append({"surplus": surplus_w, "step": step_s})
        return self.power

    def integrate(self, *, power_w, step_s):
        self.integrated.append((power_w, step_s))


class StubLedger:
    def __init__(self, **kwargs):
        self.initial = kwargs
        self.added = []
        self.aligned = []

    def add(self, *, flows_w, dt_s, moment):
        self.added.append((flows_w, dt_s, moment))

    def align(self, *, moment):
        self.aligned.append(moment)


class Rig:
    """The plant with every collaborator replaced by a recording stub."""

    def __init__(self, *, monkeypatch, scenario=None, **options):
        self.scenario = scenario or make_scenario(model="hs3")
        self.env = options.get("env") or StubEnvironment()
        self.balance_inputs = []
        self.balance_result = None
        self.battery = None
        self.ledger = None
        self.controller = StubController(command=options.get("command") or Command())
        self.ev = StubEv(power=options.get("ev_power", 0.0))

        def make_battery(**kwargs):
            self.battery = StubBattery(
                modules=kwargs["modules"], soc=kwargs["initial_soc"]
            )
            return self.battery

        def make_ledger(**kwargs):
            self.ledger = StubLedger(**kwargs)
            return self.ledger

        def solve(*, inputs):
            self.balance_inputs.append(inputs)
            if self.balance_result is not None:
                return self.balance_result
            return BalanceResult(
                pv_w=inputs.pv_available_w,
                battery_w=100.0,
                grid_w=inputs.demand_w - inputs.pv_available_w - 100.0,
                load_w=inputs.demand_w,
                curtailed_w=0.0,
                shed_w=0.0,
            )

        monkeypatch.setattr(plant_module, "Environment", lambda **_arguments: self.env)
        monkeypatch.setattr(plant_module, "BatteryBank", make_battery)
        monkeypatch.setattr(
            plant_module, "Controller", lambda **_arguments: self.controller
        )
        monkeypatch.setattr(plant_module, "EvCharger", lambda **_arguments: self.ev)
        monkeypatch.setattr(plant_module, "EnergyLedger", make_ledger)
        monkeypatch.setattr(plant_module, "solve_balance", solve)
        monkeypatch.setattr(
            plant_module, "phase_weights", lambda **_arguments: (0.5, 0.25, 0.25)
        )
        monkeypatch.setattr(
            plant_module, "grid_frequency_hz", lambda **_arguments: 50.5
        )
        monkeypatch.setattr(
            plant_module,
            "grid_voltage_v",
            lambda **arguments: 230.0 + arguments["phase"],
        )
        self.settings = options.get("settings", {})
        self.plant = plant_module.Plant(scenario=self.scenario, settings=self.settings)

    def advance(self, *, seconds):
        self.plant.advance(moment=START + timedelta(seconds=seconds))


def start_second():
    return int((START - EPOCH).total_seconds())


def offset_scenario(offset):
    start = START + timedelta(seconds=offset)
    simulation = make_scenario(model="hs3").simulation
    return make_scenario(
        model="hs3",
        simulation=type(simulation)(seed=simulation.seed, start=start, speed=1.0),
    )


def test_building_a_plant_does_no_simulation_work(monkeypatch):
    rig = Rig(monkeypatch=monkeypatch)

    assert rig.env.calls == []
    assert rig.ev.evaluated == []
    assert rig.balance_inputs == []
    assert rig.plant.second == start_second()
    assert rig.battery.soc == 0.5


def test_the_first_advance_reports_the_start_instant_without_integrating_anything(
    monkeypatch,
):
    rig = Rig(monkeypatch=monkeypatch)

    rig.advance(seconds=0)

    assert set(rig.env.calls) == {start_second()}
    assert rig.battery.applied == []
    assert rig.ledger.added == []
    assert rig.plant.sample["pv_w"] == 3000.0


def test_integration_runs_in_whole_steps_up_to_the_last_boundary_only(monkeypatch):
    rig = Rig(monkeypatch=monkeypatch)

    rig.advance(seconds=2 * STEP + 7)

    assert rig.battery.applied == [(100.0, STEP), (100.0, STEP)]
    assert [moment for _, _, moment in rig.ledger.added] == [
        START,
        START + timedelta(seconds=STEP),
    ]
    assert {dt for _, dt, _ in rig.ledger.added} == {STEP}


@pytest.mark.parametrize(
    ("seconds", "steps"), [(0, 0), (STEP - 1, 0), (STEP, 1), (3 * STEP + 9, 3)]
)
def test_a_partial_step_is_never_integrated(monkeypatch, seconds, steps):
    rig = Rig(monkeypatch=monkeypatch)

    rig.advance(seconds=seconds)

    assert len(rig.battery.applied) == steps
    assert len(rig.ledger.added) == steps
    assert len(rig.ev.integrated) == steps


def test_the_reported_values_come_from_the_exact_second_with_the_state_of_the_boundary(
    monkeypatch,
):
    rig = Rig(monkeypatch=monkeypatch)

    rig.advance(seconds=STEP + 7)

    assert rig.env.calls[-1] == start_second() + STEP + 7
    assert rig.controller.calls[-1] == (start_second() + STEP + 7, 0.5)
    assert rig.plant.second == start_second() + STEP + 7
    assert len(rig.battery.applied) == 1


def test_boundaries_are_aligned_to_the_clock_not_to_the_start_instant(monkeypatch):
    rig = Rig(monkeypatch=monkeypatch, scenario=offset_scenario(3))

    rig.plant.advance(moment=START + timedelta(seconds=3))
    assert rig.battery.applied == []
    rig.plant.advance(moment=START + timedelta(seconds=STEP - 1))
    assert rig.battery.applied == []
    rig.plant.advance(moment=START + timedelta(seconds=STEP))

    assert len(rig.battery.applied) == 1
    assert rig.ledger.added[0][2] == START


def test_the_state_does_not_depend_on_how_often_the_plant_was_polled(monkeypatch):
    once = Rig(monkeypatch=monkeypatch)
    often = Rig(monkeypatch=monkeypatch)

    once.advance(seconds=6 * STEP + 4)
    for second in range(6 * STEP + 5):
        often.advance(seconds=second)

    assert once.plant.sample == often.plant.sample
    assert once.ledger.added == often.ledger.added
    assert once.battery.applied == often.battery.applied
    assert once.ev.integrated == often.ev.integrated


def test_each_integrated_step_uses_the_ten_second_step_for_its_limits(monkeypatch):
    rig = Rig(monkeypatch=monkeypatch)

    rig.advance(seconds=STEP)

    assert set(rig.battery.limit_steps) == {STEP}
    assert {entry["step"] for entry in rig.ev.evaluated} == {STEP}


def test_the_collaborators_see_the_instant_and_state_they_need(monkeypatch):
    rig = Rig(monkeypatch=monkeypatch, ev_power=1500.0)

    rig.advance(seconds=0)

    assert rig.ev.evaluated[0]["surplus"] == 2200.0
    inputs = rig.balance_inputs[0]
    assert inputs.demand_w == 800.0 + 1500.0
    assert inputs.pv_available_w == 3000.0
    assert inputs.max_charge_w == 111.0
    assert inputs.max_discharge_w == 222.0
    assert inputs.pack_voltage_v == 333.0
    assert inputs.online is True


def test_the_electric_vehicle_energy_integrated_is_what_the_step_delivered(monkeypatch):
    rig = Rig(monkeypatch=monkeypatch, ev_power=1500.0)

    rig.advance(seconds=2 * STEP + 3)

    assert rig.ev.integrated == [(1500.0, STEP), (1500.0, STEP)]


def test_the_sample_records_what_the_balance_returned(monkeypatch):
    rig = Rig(
        monkeypatch=monkeypatch,
        env=StubEnvironment(strings=(2000.0, 1000.0), load=800.0),
    )
    rig.balance_result = BalanceResult(
        pv_w=1500.0,
        battery_w=-200.0,
        grid_w=-500.0,
        load_w=800.0,
        curtailed_w=1500.0,
        shed_w=0.0,
    )

    rig.advance(seconds=0)

    sample = rig.plant.sample
    assert sample["pv_w"] == 1500.0
    assert sample["pv1_w"] == pytest.approx(1000.0)
    assert sample["pv2_w"] == pytest.approx(500.0)
    assert sample["pv3_w"] == sample["pv4_w"] == 0.0
    assert sample["battery_w"] == -200.0
    assert sample["grid_w"] == -500.0
    assert sample["inverter_w"] == 1300.0
    assert sample["load_w"] == 800.0
    assert sample["curtailed_w"] == 1500.0
    assert sample["soc"] == 0.5
    assert sample["frequency_hz"] == 50.5
    assert [sample[f"voltage_{phase}_v"] for phase in range(3)] == [230.0, 231.0, 232.0]
    assert sample["backup_w"] == 0.0


def test_there_is_no_string_share_when_the_sun_is_down(monkeypatch):
    rig = Rig(monkeypatch=monkeypatch, env=StubEnvironment(strings=(0.0, 0.0)))

    rig.advance(seconds=0)

    assert rig.plant.sample["pv1_w"] == 0.0


def test_the_ledger_is_fed_with_the_signed_flows_of_each_step(monkeypatch):
    rig = Rig(monkeypatch=monkeypatch, ev_power=700.0)
    rig.balance_result = BalanceResult(
        pv_w=1500.0,
        battery_w=-200.0,
        grid_w=-500.0,
        load_w=800.0,
        curtailed_w=0.0,
        shed_w=0.0,
    )

    rig.advance(seconds=STEP)

    flows, dt, moment = rig.ledger.added[0]
    assert dt == STEP
    assert moment == START
    assert flows["pv"] == 1500.0
    assert flows["bat_charge"] == 200.0
    assert flows["bat_discharge"] == 0.0
    assert flows["sell"] == 500.0
    assert flows["feed_in"] == 0.0
    assert flows["load"] == 800.0
    assert flows["ev"] == 700.0
    assert flows["pv_hours"] == plant_module.GENERATING_HOUR_RATE
    assert set(flows) == set(plant_module.ENERGY_FLOWS)


def test_generating_hours_only_count_while_solar_produces(monkeypatch):
    rig = Rig(monkeypatch=monkeypatch)
    rig.balance_result = BalanceResult(
        pv_w=0.0, battery_w=0.0, grid_w=800.0, load_w=800.0, curtailed_w=0.0, shed_w=0.0
    )

    rig.advance(seconds=STEP)

    assert rig.ledger.added[0][0]["pv_hours"] == 0.0


def test_the_ledger_starts_with_a_distinct_lifetime_total_per_flow(monkeypatch):
    rig = Rig(monkeypatch=monkeypatch)

    totals = rig.ledger.initial["initial_totals_wh"]

    assert set(totals) == set(plant_module.ENERGY_FLOWS)
    assert len(set(totals.values())) > 1
    assert all(total > 0 for total in totals.values())


@pytest.mark.parametrize(
    ("changes", "expected"),
    [
        ({"meters": {"meter_b": True}}, 500.0),
        ({"meters": {"meter_b": False}}, 0.0),
        ({"meters": {"meter_b": True}, "site": {"grid_connected": False}}, 0.0),
    ],
)
def test_external_generation_needs_meter_b_and_a_grid(monkeypatch, changes, expected):
    rig = Rig(monkeypatch=monkeypatch, scenario=make_scenario(model="hs3", **changes))

    rig.advance(seconds=0)

    assert rig.balance_inputs[-1].external_pv_w == expected
    assert rig.plant.sample["ext_pv_w"] == expected


def test_load_served_off_grid_is_reported_as_backup_load(monkeypatch):
    rig = Rig(
        monkeypatch=monkeypatch,
        scenario=make_scenario(model="hs3", site={"grid_connected": False}),
    )

    rig.advance(seconds=0)

    assert rig.plant.sample["backup_w"] == rig.plant.sample["load_w"]


def off_grid_rig(*, monkeypatch, soc, modules=2, strings=(100.0,), load=800.0):
    scenario = make_scenario(
        model="hs3",
        site={"grid_connected": False},
        battery={"modules": modules, "initial_soc_percent": soc},
    )
    return Rig(
        monkeypatch=monkeypatch,
        scenario=scenario,
        settings={ctl.DISCHARGE_FLOOR_OFF_GRID: 10},
        env=StubEnvironment(strings=strings, load=load),
    )


@pytest.mark.parametrize(
    ("soc", "pv", "expected"),
    [(10, 100.0, True), (50, 100.0, False), (10, 5000.0, False)],
)
def test_off_grid_load_is_shed_when_the_battery_is_at_its_floor_and_solar_is_short(
    monkeypatch, soc, pv, expected
):
    rig = off_grid_rig(monkeypatch=monkeypatch, soc=soc, strings=(pv,))

    rig.advance(seconds=0)

    assert rig.balance_inputs[-1].shedding is expected


def test_shedding_continues_until_the_battery_recovers_above_the_floor_margin(
    monkeypatch,
):
    rig = off_grid_rig(monkeypatch=monkeypatch, soc=10)
    rig.advance(seconds=0)
    assert rig.plant.shedding is True

    rig.battery.soc = 0.115
    rig.advance(seconds=STEP)
    assert rig.balance_inputs[-1].shedding is True

    rig.battery.soc = 0.13
    rig.advance(seconds=2 * STEP)
    assert rig.balance_inputs[-1].shedding is False
    assert rig.plant.shedding is False


def test_a_reading_between_boundaries_does_not_change_the_shedding_state(monkeypatch):
    rig = off_grid_rig(monkeypatch=monkeypatch, soc=10, strings=(5000.0,))
    rig.advance(seconds=0)
    assert rig.plant.shedding is False

    rig.env.strings = (100.0,)
    rig.advance(seconds=4)

    assert rig.balance_inputs[-1].shedding is True
    assert rig.plant.shedding is False


@pytest.mark.parametrize(("pv", "expected"), [(100.0, True), (5000.0, False)])
def test_off_grid_without_a_battery_sheds_whenever_solar_is_short(
    monkeypatch, pv, expected
):
    rig = off_grid_rig(monkeypatch=monkeypatch, soc=50, modules=0, strings=(pv,))

    rig.advance(seconds=0)

    assert rig.balance_inputs[-1].shedding is expected


def test_grid_connected_plants_never_shed(monkeypatch):
    rig = Rig(
        monkeypatch=monkeypatch,
        scenario=make_scenario(model="hs3", battery={"initial_soc_percent": 0}),
        env=StubEnvironment(strings=(0.0,)),
    )

    rig.advance(seconds=0)

    assert rig.balance_inputs[-1].shedding is False


def test_faults_keep_the_inverter_offline_until_they_are_cleared(monkeypatch):
    rig = Rig(
        monkeypatch=monkeypatch,
        scenario=make_scenario(model="hs3", faults={"inverter_fault_bits": (3,)}),
    )
    rig.advance(seconds=0)
    assert rig.balance_inputs[-1].online is False

    rig.plant.fault_bits = ()
    rig.advance(seconds=1)

    assert rig.balance_inputs[-1].online is True


def test_a_restart_countdown_is_second_accurate_between_boundaries(monkeypatch):
    rig = Rig(monkeypatch=monkeypatch)
    rig.advance(seconds=0)

    rig.plant.restart()

    assert rig.plant.online is False
    assert rig.plant.restart_remaining_s == plant_module.RESTART_SECONDS
    rig.advance(seconds=plant_module.RESTART_SECONDS - 1)
    assert rig.plant.online is False
    assert rig.plant.restart_remaining_s == 1
    assert rig.balance_inputs[-1].online is False
    rig.advance(seconds=plant_module.RESTART_SECONDS)
    assert rig.plant.online is True
    assert rig.plant.restart_remaining_s == 0
    assert rig.balance_inputs[-1].online is True


def test_the_reported_instant_sees_a_cleared_restart_before_the_next_boundary(
    monkeypatch,
):
    rig = Rig(monkeypatch=monkeypatch)
    rig.advance(seconds=0)
    rig.plant.restart_until = start_second() + 5

    rig.advance(seconds=4)
    assert rig.balance_inputs[-1].online is False
    rig.advance(seconds=5)

    assert rig.balance_inputs[-1].online is True
    assert len(rig.battery.applied) == 0


def test_jumping_moves_time_realigns_the_ledger_and_recomputes_the_sample_there(
    monkeypatch,
):
    rig = Rig(monkeypatch=monkeypatch)
    rig.advance(seconds=5 * STEP)
    target = START + timedelta(days=3)

    rig.plant.jump_to(moment=target)
    rig.plant.advance(moment=target)

    assert rig.ledger.aligned == [target]
    assert rig.plant.second == int((target - EPOCH).total_seconds())
    assert rig.env.calls[-1] == rig.plant.second
    assert len(rig.battery.applied) == 5


def ramp(second):
    return float(second - start_second())


def test_the_average_before_any_step_is_the_current_sample(monkeypatch):
    rig = Rig(monkeypatch=monkeypatch, env=StubEnvironment(strings=(0.0,), load=ramp))

    rig.advance(seconds=4)

    assert rig.plant.averaged["load_w"] == pytest.approx(4.0)


def test_the_average_before_the_first_complete_window_covers_the_steps_so_far(
    monkeypatch,
):
    rig = Rig(monkeypatch=monkeypatch, env=StubEnvironment(strings=(0.0,), load=ramp))

    rig.advance(seconds=100 + 4)

    assert rig.plant.averaged["load_w"] == pytest.approx(45.0)


def test_the_average_publishes_the_mean_of_the_steps_of_the_previous_complete_window(
    monkeypatch,
):
    window = plant_module.AVERAGE_WINDOW_S
    rig = Rig(monkeypatch=monkeypatch, env=StubEnvironment(strings=(0.0,), load=ramp))

    rig.advance(seconds=window + 40)

    assert rig.plant.averaged["load_w"] == pytest.approx((window - STEP) / 2)
    rig.advance(seconds=window + 60)
    assert rig.plant.averaged["load_w"] == pytest.approx((window - STEP) / 2)


def test_a_jump_restarts_the_averaging_window(monkeypatch):
    rig = Rig(monkeypatch=monkeypatch)
    rig.advance(seconds=plant_module.AVERAGE_WINDOW_S + STEP)

    rig.plant.jump_to(moment=START)
    rig.plant.advance(moment=START)

    assert rig.plant.averaged["load_w"] == pytest.approx(rig.plant.sample["load_w"])
