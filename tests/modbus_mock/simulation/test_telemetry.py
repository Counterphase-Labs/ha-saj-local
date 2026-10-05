from types import SimpleNamespace

import pytest

from saj_modbus_mock.simulation.ev_charger import ChargerReadout, ChargerState
from saj_modbus_mock.simulation.plant import ENERGY_FLOWS
from saj_modbus_mock.simulation.telemetry import build_telemetry, operating_mode
from tests.modbus_mock.builders import make_scenario


def make_sample(**changes):
    sample = {
        "pv_w": 3000.0,
        "ext_pv_w": 0.0,
        "load_w": 1000.0,
        "battery_w": -1000.0,
        "grid_w": -1000.0,
        "inverter_w": 2000.0,
        "ev_w": 0.0,
        "backup_w": 0.0,
        "soc": 0.5,
        "curtailed_w": 0.0,
        "shed_w": 0.0,
        "frequency_hz": 50.0,
        "pv1_w": 2000.0,
        "pv2_w": 1000.0,
        "pv3_w": 0.0,
        "pv4_w": 0.0,
        "voltage_0_v": 230.0,
        "voltage_1_v": 231.0,
        "voltage_2_v": 232.0,
    }
    sample.update(changes)
    return sample


class StubBattery:
    def __init__(self, *, modules=2, soc=0.5):
        self.modules = modules
        self.soc = soc
        self.capacity_ah = modules * 100

    def pack_voltage_v(self):
        return 400.0

    def power_limit_w(self, **_arguments):
        return 4000.0

    def temperature_c(self, **_arguments):
        return 25.0

    def cycles(self):
        return 3


class StubLedger:
    def kwh(self, *, flow, period):
        return {"today": 1.0, "month": 10.0, "year": 100.0, "total": 1000.0}[period] * (
            1 + ENERGY_FLOWS.index(flow) / 100
        )


class StubEv:
    def __init__(self, *, state=ChargerState.IDLE, power=0.0, phases=3):
        self._readout = ChargerReadout(
            state=state,
            power_w=power,
            session_energy_wh=100.0,
            total_energy_wh=5000.0,
            session_start_s=10,
            session_end_s=0,
            session_seconds=125,
            phases=phases,
            max_power_w=11000,
        )

    def readout(self):
        return self._readout


PLANT_OPTIONS = {
    "sample",
    "averaged",
    "modules",
    "fault_bits",
    "online",
    "restart",
    "ev",
}


def make_plant(*, model="hs3", **options):
    plant_options = {key: options.pop(key) for key in PLANT_OPTIONS & set(options)}
    scenario = make_scenario(model=model, **options)
    weights = (0.5, 0.25, 0.25) if scenario.device.model.phases == 3 else (1.0,)
    return SimpleNamespace(
        scenario=scenario,
        battery=StubBattery(modules=plant_options.get("modules", 2)),
        sample=plant_options.get("sample") or make_sample(),
        averaged=plant_options.get("averaged") or make_sample(grid_w=-500.0, soc=0.4),
        weights=weights,
        ledger=StubLedger(),
        ev=plant_options.get("ev") or StubEv(),
        fault_bits=plant_options.get("fault_bits", ()),
        online=plant_options.get("online", True),
        restart_remaining_s=plant_options.get("restart", 0),
        second=12345,
    )


def telemetry(**kwargs):
    return build_telemetry(plant=make_plant(**kwargs))


def test_totals_come_straight_from_the_sample_and_the_average_uses_its_own_prefix():
    out = telemetry()

    assert out["pv_w"] == 3000.0
    assert out["battery_w"] == -1000.0
    assert out["grid_w"] == -1000.0
    assert out["avg_grid_w"] == -500.0
    assert out["soc_percent"] == 50.0
    assert out["avg_soc_percent"] == 40.0
    assert out["clock_s"] == 12345.0


@pytest.mark.parametrize(
    ("key", "expected"),
    [
        ("direction_pv", 1.0),
        ("direction_battery", -1.0),
        ("direction_grid", -1.0),
        ("direction_output", 1.0),
    ],
)
def test_direction_registers_follow_the_sign_of_each_flow(key, expected):
    assert telemetry()[key] == expected


def test_directions_are_zero_for_idle_flows_and_positive_for_import():
    out = telemetry(sample=make_sample(pv_w=0.0, battery_w=0.0, grid_w=700.0))

    assert (out["direction_pv"], out["direction_battery"], out["direction_grid"]) == (
        0.0,
        0.0,
        1.0,
    )


def test_phase_values_split_each_total_by_the_phase_weights():
    out = telemetry()

    assert out["grid_r_w"] == pytest.approx(-500.0)
    assert out["grid_s_w"] == pytest.approx(-250.0)
    assert out["grid_r_v"] == 230.0
    assert out["grid_t_v"] == 232.0
    assert out["grid_r_a"] == pytest.approx(-500.0 / 230.0)
    assert out["grid_r_va"] > abs(out["grid_r_w"])
    assert out["inv_r_w"] == pytest.approx(1000.0)
    assert out["load_s_w"] == pytest.approx(250.0)
    assert out["gridload_r_w"] == 0.0


def test_a_single_phase_model_has_only_its_first_phase():
    out = telemetry(
        model="h2",
        sample=make_sample(voltage_1_v=0.0, voltage_2_v=0.0),
        averaged=make_sample(),
    )

    assert out["grid_r_w"] == pytest.approx(-1000.0)
    assert "grid_s_w" not in out
    assert out["ac_phase_count"] == 1.0


def test_strings_report_power_voltage_and_current_only_while_generating():
    out = telemetry()

    assert out["pv1_w"] == 2000.0
    assert out["pv1_v"] > 0
    assert out["pv1_a"] == pytest.approx(2000.0 / out["pv1_v"])
    assert (out["pv3_w"], out["pv3_v"], out["pv3_a"]) == (0.0, 0.0, 0.0)


@pytest.mark.parametrize(
    ("meter_a", "grid_connected", "present"),
    [(True, True, True), (False, True, False), (True, False, False)],
)
def test_meter_a_reads_the_grid_only_when_installed_and_connected(
    meter_a, grid_connected, present
):
    out = telemetry(
        meters={"meter_a": meter_a, "meter_b": False},
        site={"grid_connected": grid_connected},
    )

    assert out["meter_a_status"] == float(present)
    assert (out["meter_a_r_w"] != 0.0) is present
    assert (out["ct_grid_w"] != 0.0) is present


def test_meter_b_reads_external_generation_only_when_installed():
    sample = make_sample(ext_pv_w=900.0)

    with_b = telemetry(sample=sample, meters={"meter_a": True, "meter_b": True})
    without = telemetry(sample=sample, meters={"meter_a": True, "meter_b": False})

    assert with_b["meter_b_status"] == 1.0
    assert with_b["meter_b_r_w"] == pytest.approx(450.0)
    assert without["meter_b_status"] == 0.0
    assert without["meter_b_r_w"] == 0.0


def test_energy_counters_cover_every_flow_and_period_and_scale_with_inverters():
    single = telemetry()
    double = telemetry(parallel={"inverters": 2})

    for flow in ENERGY_FLOWS:
        for period in ("today", "month", "year", "total"):
            assert f"{flow}_{period}_kwh" in single
    assert double["parallel_pv_total_kwh"] == pytest.approx(2 * single["pv_total_kwh"])
    assert single["parallel_pv_total_kwh"] == single["pv_total_kwh"]
    assert single["sum_sell_total_kwh"] == single["sell_total_kwh"]


def test_phase_share_counters_only_exist_for_the_extra_phases():
    three = telemetry()

    assert three["sell_phase2_total_kwh"] == pytest.approx(
        three["sell_total_kwh"] * 0.25
    )
    assert "sell_phase3_total_kwh" in three
    assert "sell_phase2_total_kwh" not in telemetry(
        model="h2", sample=make_sample(), averaged=make_sample()
    )


def test_parallel_values_multiply_the_unit_and_split_into_signed_words():
    out = telemetry(parallel={"inverters": 2}, sample=make_sample(grid_w=-40000.0))

    assert out["parallel_grid_w"] == -80000.0
    low = out["parallel_grid_w_low"]
    high = out["parallel_grid_w_high"]
    assert int(high) * 65536 + int(low) == -80000
    assert high == -2.0
    assert out["parallel_capacity_ah"] == 400.0
    assert out["parallel_soc_percent"] == out["soc_percent"]


def test_battery_modules_are_reported_individually_and_absent_ones_read_zero():
    out = telemetry(modules=2)

    assert out["module1_soc_percent"] == 50.0
    assert out["module2_v"] == 400.0
    assert out["module1_a"] == pytest.approx(-1000.0 / 2 / 400.0)
    assert out["module1_cycles"] == 3.0
    assert (
        out["module3_soc_percent"] == out["module3_v"] == out["module3_cycles"] == 0.0
    )
    assert out["module3_discharge_kwh_low"] == 0.0
    assert out["battery_modules"] == 2.0
    assert out["battery_online_mask"] == 0b11
    assert out["battery_capacity_ah"] == 200.0
    assert out["battery_half_a"] == pytest.approx(out["battery_a"] / 2)


def test_a_bank_without_modules_reports_no_voltage_or_capacity():
    out = telemetry(modules=0)

    assert out["battery_v"] == 0.0
    assert out["battery_current_limit_a"] == 0.0
    assert out["battery_online_mask"] == 0.0
    assert out["battery_user_capacity_ah"] == 0.0


def test_the_discharge_counter_of_a_pack_is_its_share_split_into_words():
    out = telemetry(modules=2)

    kwh = int(out["module1_discharge_kwh_high"]) * 65536 + int(
        out["module1_discharge_kwh_low"]
    )
    assert kwh == int(out["bat_discharge_total_kwh"] / 2)


@pytest.mark.parametrize(
    ("state", "pilot"),
    [
        (ChargerState.IDLE, 12.0),
        (ChargerState.READY, 9.0),
        (ChargerState.CHARGING, 6.0),
    ],
)
def test_the_control_pilot_voltage_follows_the_charger_state(state, pilot):
    out = telemetry(
        ev=StubEv(state=state, power=6900.0 if state is ChargerState.CHARGING else 0.0)
    )

    assert out["ev_cp_v"] == pilot
    assert out["ev_on"] == float(state is ChargerState.CHARGING)


def test_charger_phases_beyond_the_installed_count_read_zero():
    out = telemetry(ev=StubEv(state=ChargerState.CHARGING, power=2300.0, phases=1))

    assert out["ev_r_v"] == 230.0
    assert out["ev_r_a"] == pytest.approx(10.0)
    assert out["ev_s_v"] == out["ev_t_a"] == 0.0
    assert out["ev_session_minutes"] == 2.0
    assert out["ev_set_current_a"] == pytest.approx(11000 / 230)
    assert out["ev_session_wh"] == 100.0


def test_charger_installation_and_limits_come_from_the_scenario():
    out = telemetry(ev_charger={"installed": True, "phases": 1, "max_power_w": 7000})

    assert out["ev_installed"] == 1.0
    assert out["ev_phases"] == 1.0
    assert out["ev_max_power_w"] == 7000.0
    assert out["ev_min_power_w"] == pytest.approx(6 * 230)


@pytest.mark.parametrize(
    ("fault_bits", "online", "grid", "expected"),
    [
        ((1,), True, True, 5.0),
        ((), False, True, 1.0),
        ((), True, False, 3.0),
        ((), True, True, 2.0),
    ],
)
def test_the_operating_mode_reports_fault_waiting_off_grid_or_running(
    fault_bits, online, grid, expected
):
    plant = make_plant(
        fault_bits=fault_bits, online=online, site={"grid_connected": grid}
    )

    assert operating_mode(plant=plant) == expected


def test_fault_bits_become_the_fault_word_and_count():
    out = telemetry(fault_bits=(0, 4), online=False, restart=12)

    assert out["fault_word"] == 0b10001
    assert out["fault_count"] == 2.0
    assert out["conn_time_s"] == 12.0


def test_a_zero_source_exists_for_registers_without_a_quantity():
    assert telemetry()["zero"] == 0.0


GRID_SIDE_SUFFIXES = ("v", "a", "hz", "dc", "w", "va", "pf")


@pytest.mark.parametrize("prefix", ["", "avg_"])
def test_off_grid_every_grid_side_value_reads_zero_while_the_output_carries_the_load(
    prefix,
):
    out = telemetry(
        site={"grid_connected": False},
        sample=make_sample(grid_w=0.0, backup_w=1000.0, load_w=1000.0),
        averaged=make_sample(grid_w=0.0, backup_w=1000.0, load_w=1000.0),
    )

    for group in ("grid", "side", "gridload"):
        for phase in "rst":
            for suffix in GRID_SIDE_SUFFIXES:
                assert out[f"{prefix}{group}_{phase}_{suffix}"] == 0.0
    assert out[f"{prefix}out_r_w"] == pytest.approx(500.0)
    assert out[f"{prefix}out_r_v"] == 230.0
    assert out[f"{prefix}out_r_hz"] == 50.0
    assert out["grid_w"] == out["grid_load_w"] == 0.0


def test_grid_connected_the_grid_side_values_are_live():
    out = telemetry()

    assert out["grid_r_v"] == 230.0
    assert out["grid_r_hz"] == 50.0
    assert out["side_r_v"] == 230.0
