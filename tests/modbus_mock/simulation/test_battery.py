import pytest

from saj_modbus_mock.simulation.battery import MODULE_NOMINAL_VOLTAGE_V, BatteryBank


def bank(*, modules=2, ah=100, soc=0.5, pack_v=400.0):
    return BatteryBank(
        modules=modules, module_capacity_ah=ah, pack_voltage_v=pack_v, initial_soc=soc
    )


def test_capacity_scales_with_module_count_and_size():
    assert bank(modules=2, ah=100).capacity_wh == pytest.approx(
        2 * 100 * MODULE_NOMINAL_VOLTAGE_V
    )
    assert bank(modules=4, ah=50).capacity_ah == 200
    assert bank(modules=4, ah=50).capacity_wh == bank(modules=2, ah=100).capacity_wh


def test_power_limit_is_half_the_capacity_per_hour_capped_by_the_inverter():
    small = bank(modules=1)
    large = bank(modules=8)

    assert small.power_limit_w(rated_power_w=12000.0) == pytest.approx(
        small.capacity_wh / 2
    )
    assert large.power_limit_w(rated_power_w=3000.0) == 3000.0


def test_a_bank_without_modules_has_no_charge_state_and_no_power():
    empty = bank(modules=0, soc=0.8)

    assert empty.soc == 0.0
    assert empty.max_charge_w(ceiling_soc=1.0, rated_power_w=5000.0, dt_s=1) == 0.0
    assert empty.max_discharge_w(floor_soc=0.0, rated_power_w=5000.0, dt_s=1) == 0.0
    empty.apply(power_w=1000.0, dt_s=60)
    assert empty.soc == 0.0
    assert empty.throughput_wh == 0.0


def test_discharge_stops_at_the_floor_and_charge_at_the_ceiling():
    battery = bank(soc=0.5)

    assert battery.max_discharge_w(floor_soc=0.5, rated_power_w=12000.0, dt_s=1) == 0.0
    assert battery.max_charge_w(ceiling_soc=0.5, rated_power_w=12000.0, dt_s=1) == 0.0
    assert battery.max_discharge_w(floor_soc=0.2, rated_power_w=12000.0, dt_s=1) > 0.0
    assert battery.max_charge_w(ceiling_soc=0.9, rated_power_w=12000.0, dt_s=1) > 0.0


def test_the_power_allowed_never_overshoots_the_floor_within_one_step():
    battery = bank(soc=0.2001)
    dt = 10.0
    allowed = battery.max_discharge_w(floor_soc=0.2, rated_power_w=12000.0, dt_s=dt)

    battery.apply(power_w=allowed, dt_s=dt)

    assert battery.soc == pytest.approx(0.2)


@pytest.mark.parametrize(("power", "direction"), [(1000.0, -1), (-1000.0, 1)])
def test_applying_power_moves_state_of_charge_and_counts_throughput(power, direction):
    battery = bank(soc=0.5)
    before = battery.soc

    battery.apply(power_w=power, dt_s=3600)

    assert (battery.soc - before) * direction > 0
    assert battery.throughput_wh == pytest.approx(1000.0)
    assert battery.soc - before == pytest.approx(
        direction * 1000.0 / battery.capacity_wh
    )


def test_a_bigger_bank_moves_state_of_charge_more_slowly_for_the_same_power():
    small = bank(modules=1)
    large = bank(modules=4)

    small.apply(power_w=1000.0, dt_s=600)
    large.apply(power_w=1000.0, dt_s=600)

    assert 0.5 - small.soc == pytest.approx(4 * (0.5 - large.soc))


def test_pack_voltage_rises_with_state_of_charge():
    low = bank(soc=0.1).pack_voltage_v()
    high = bank(soc=1.0).pack_voltage_v()

    assert low < high == pytest.approx(400.0)


def test_temperature_rises_with_load_and_saturates():
    battery = bank()

    idle = battery.temperature_c(power_w=0.0, rated_power_w=1000.0)

    assert battery.temperature_c(power_w=500.0, rated_power_w=1000.0) > idle
    assert battery.temperature_c(
        power_w=5000.0, rated_power_w=1000.0
    ) == battery.temperature_c(
        power_w=1000.0,
        rated_power_w=1000.0,
    )


def test_cycles_count_full_charge_and_discharge_pairs_of_throughput():
    battery = bank(modules=1)
    battery.apply(power_w=-battery.capacity_wh, dt_s=3600)
    battery.throughput_wh = 0.0
    battery.apply(power_w=battery.capacity_wh, dt_s=3600)
    battery.apply(power_w=-battery.capacity_wh, dt_s=3600)

    assert battery.cycles() == 1
