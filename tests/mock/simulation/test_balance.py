import dataclasses

import pytest

from saj_modbus_mock.simulation.balance import BalanceInput, solve_balance
from saj_modbus_mock.simulation.control import BatteryRequest, Command, RequestKind

BASE = BalanceInput(
    pv_available_w=0.0,
    external_pv_w=0.0,
    demand_w=1000.0,
    command=Command(),
    grid_connected=True,
    online=True,
    max_charge_w=5000.0,
    max_discharge_w=5000.0,
    pack_voltage_v=400.0,
    shedding=False,
)


def solve(**changes):
    command = changes.pop("command", None)
    inputs = dataclasses.replace(BASE, **changes)
    if command is not None:
        inputs = dataclasses.replace(inputs, command=command)
    return solve_balance(inputs=inputs), inputs


def assert_balanced(*, result, inputs):
    total = result.pv_w + inputs.external_pv_w + result.battery_w + result.grid_w
    assert total == pytest.approx(result.load_w)


def test_full_battery_and_surplus_solar_is_exported():
    result, inputs = solve(pv_available_w=10000.0, max_charge_w=0.0)

    assert result.grid_w == pytest.approx(-9000.0)
    assert result.battery_w == 0.0
    assert_balanced(result=result, inputs=inputs)


@pytest.mark.parametrize(
    ("pv", "demand", "battery", "grid"),
    [
        (0.0, 1000.0, 1000.0, 0.0),
        (400.0, 1000.0, 600.0, 0.0),
        (3000.0, 1000.0, -2000.0, 0.0),
        (9000.0, 1000.0, -5000.0, -3000.0),
    ],
)
def test_self_use_follows_the_load_with_the_battery_then_the_grid(
    pv, demand, battery, grid
):
    result, inputs = solve(pv_available_w=pv, demand_w=demand)

    assert result.battery_w == pytest.approx(battery)
    assert result.grid_w == pytest.approx(grid)
    assert_balanced(result=result, inputs=inputs)


def test_the_battery_discharge_limit_leaves_the_rest_to_the_grid():
    result, inputs = solve(demand_w=3000.0, max_discharge_w=1200.0)

    assert result.battery_w == pytest.approx(1200.0)
    assert result.grid_w == pytest.approx(1800.0)
    assert_balanced(result=result, inputs=inputs)


def test_backup_mode_never_discharges():
    result, _ = solve(demand_w=3000.0, command=Command(allow_discharge=False))

    assert result.battery_w == 0.0
    assert result.grid_w == pytest.approx(3000.0)


@pytest.mark.parametrize(
    ("kind", "target", "pv", "battery", "grid"),
    [
        (RequestKind.BATTERY, -2000.0, 0.0, -2000.0, 3000.0),
        (RequestKind.BATTERY, 3000.0, 500.0, 3000.0, -2500.0),
        (RequestKind.INVERTER, -500.0, 0.0, -500.0, 1500.0),
        (RequestKind.INVERTER, 700.0, 300.0, 400.0, 300.0),
        (RequestKind.GRID, -600.0, 0.0, 400.0, 600.0),
        (RequestKind.GRID, 500.0, 0.0, 1500.0, -500.0),
    ],
)
def test_a_request_decides_which_quantity_the_battery_holds(
    kind, target, pv, battery, grid
):
    command = Command(request=BatteryRequest(kind=kind, power_w=target))

    result, inputs = solve(pv_available_w=pv, command=command)

    assert result.battery_w == pytest.approx(battery)
    assert result.grid_w == pytest.approx(grid)
    assert_balanced(result=result, inputs=inputs)


@pytest.mark.parametrize(
    ("changes", "expected"),
    [
        ({"charge_current_limit_a": 2.0}, -800.0),
        ({"discharge_current_limit_a": 2.0}, -2000.0),
    ],
)
def test_battery_current_limits_cap_power_at_the_pack_voltage(changes, expected):
    command = Command(
        request=BatteryRequest(kind=RequestKind.BATTERY, power_w=-2000.0),
        **changes,
    )

    result, _ = solve(command=command)

    assert result.battery_w == pytest.approx(expected)


def test_a_discharge_current_limit_caps_discharge():
    command = Command(
        request=BatteryRequest(kind=RequestKind.BATTERY, power_w=3000.0),
        discharge_current_limit_a=2.0,
    )

    result, _ = solve(command=command)

    assert result.battery_w == pytest.approx(800.0)


@pytest.mark.parametrize(
    ("target", "expected_inverter"),
    [(1000.0, 240.0), (-1000.0, -240.0)],
)
def test_inverter_limits_cap_what_the_inverter_exchanges(target, expected_inverter):
    command = Command(
        request=BatteryRequest(kind=RequestKind.INVERTER, power_w=target),
        inverter_sell_limit_w=240.0,
        inverter_buy_limit_w=240.0,
    )

    result, _ = solve(command=command)

    assert result.pv_w + result.battery_w == pytest.approx(expected_inverter)


def test_a_pv_limit_curtails_generation():
    result, inputs = solve(
        pv_available_w=5000.0,
        max_charge_w=0.0,
        command=Command(pv_limit_w=1800.0),
    )

    assert result.pv_w == 1800.0
    assert result.curtailed_w == pytest.approx(3200.0)
    assert_balanced(result=result, inputs=inputs)


def test_the_export_limit_trims_solar_before_anything_else():
    result, inputs = solve(
        pv_available_w=6000.0,
        max_charge_w=0.0,
        command=Command(export_limit_w=1000.0),
    )

    assert result.grid_w == pytest.approx(-1000.0)
    assert result.curtailed_w == pytest.approx(4000.0)
    assert_balanced(result=result, inputs=inputs)


def test_the_export_limit_trims_battery_discharge_when_solar_is_not_enough():
    command = Command(
        request=BatteryRequest(kind=RequestKind.BATTERY, power_w=4000.0),
        export_limit_w=500.0,
    )

    result, inputs = solve(pv_available_w=500.0, command=command)

    assert result.grid_w == pytest.approx(-500.0)
    assert result.pv_w == 0.0
    assert result.battery_w == pytest.approx(1500.0)
    assert_balanced(result=result, inputs=inputs)


def test_exports_under_the_limit_are_left_alone():
    result, _ = solve(
        pv_available_w=2000.0,
        max_charge_w=0.0,
        command=Command(export_limit_w=5000.0),
    )

    assert result.grid_w == pytest.approx(-1000.0)
    assert result.curtailed_w == 0.0


def test_external_generation_reduces_what_the_inverter_must_cover():
    result, inputs = solve(external_pv_w=700.0)

    assert result.battery_w == pytest.approx(300.0)
    assert_balanced(result=result, inputs=inputs)


def test_an_offline_inverter_leaves_the_load_to_the_grid_and_loses_solar():
    result, inputs = solve(pv_available_w=4000.0, online=False)

    assert result.pv_w == 0.0
    assert result.battery_w == 0.0
    assert result.grid_w == pytest.approx(1000.0)
    assert result.curtailed_w == pytest.approx(4000.0)
    assert_balanced(result=result, inputs=inputs)


@pytest.mark.parametrize(
    ("pv", "battery", "curtailed"),
    [(0.0, 1000.0, 0.0), (400.0, 600.0, 0.0), (3000.0, -2000.0, 0.0)],
)
def test_off_grid_the_battery_covers_the_load_and_nothing_touches_the_grid(
    pv, battery, curtailed
):
    result, _ = solve(pv_available_w=pv, grid_connected=False)

    assert result.grid_w == 0.0
    assert result.battery_w == pytest.approx(battery)
    assert result.load_w == pytest.approx(1000.0)
    assert result.curtailed_w == pytest.approx(curtailed)
    assert result.shed_w == 0.0


def test_off_grid_solar_is_curtailed_when_the_battery_cannot_absorb_it():
    result, _ = solve(pv_available_w=4000.0, grid_connected=False, max_charge_w=0.0)

    assert result.pv_w == pytest.approx(1000.0)
    assert result.curtailed_w == pytest.approx(3000.0)


def test_off_grid_load_is_shed_entirely_while_shedding():
    result, _ = solve(
        pv_available_w=300.0,
        grid_connected=False,
        shedding=True,
        max_discharge_w=0.0,
    )

    assert result.load_w == 0.0
    assert result.shed_w == pytest.approx(1000.0)
    assert result.battery_w == pytest.approx(-300.0)
    assert result.pv_w == pytest.approx(300.0)
