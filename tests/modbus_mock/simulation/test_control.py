from datetime import UTC, datetime

import pytest

from saj_modbus_mock.simulation import control as ctl
from saj_modbus_mock.simulation.control import (
    BatteryRequest,
    Controller,
    RequestKind,
    SiteContext,
    schedule_power_percent,
    slot_key,
)

SUNDAY_NIGHT = datetime(2026, 6, 21, 22, 0, tzinfo=UTC)
MONDAY_NIGHT = datetime(2026, 6, 22, 22, 0, tzinfo=UTC)
RATED = 10000.0
ALL_DAYS = 0x7F
SUNDAY = 0x40


def hhmm(*, hour, minute=0):
    return (hour << 8) | minute


def context(**changes):
    values = {
        "rated_power_w": RATED,
        "grid_connected": True,
        "has_meter_a": True,
        "inverters": 1,
    }
    values.update(changes)
    return SiteContext(**values)


def controller(*, settings=None, **changes):
    return Controller(
        settings=settings if settings is not None else {}, context=context(**changes)
    )


def command(*, ctrl, moment=SUNDAY_NIGHT, second=1000, soc=0.5):
    return ctrl.command(moment=moment, second=second, soc=soc)


def slot_settings(*, kind, window, **options):
    days = options.get("days", ALL_DAYS)
    percent = options.get("percent", 10)
    index = options.get("index", 1)
    enable = options.get("enable")
    start, end = window
    enable_key = (
        ctl.CHARGE_ENABLE_MASK if kind == "charge" else ctl.DISCHARGE_ENABLE_MASK
    )
    return {
        enable_key: 1 << (index - 1) if enable is None else enable,
        slot_key(kind=kind, index=index, part="start"): hhmm(
            hour=start[0], minute=start[1]
        ),
        slot_key(kind=kind, index=index, part="end"): hhmm(hour=end[0], minute=end[1]),
        slot_key(kind=kind, index=index, part="days_power"): (days << 8) | percent,
    }


def test_self_use_asks_for_no_forced_battery_power():
    assert command(ctrl=controller()).request is None


@pytest.mark.parametrize("mode", [3, 11, 14, 0])
def test_other_application_modes_behave_as_self_use(mode):
    assert command(ctrl=controller(settings={ctl.APP_MODE: mode})).request is None


def test_text_settings_are_treated_as_unset():
    assert command(ctrl=controller(settings={ctl.APP_MODE: "garbage"})).request is None


def test_ems_mode_without_a_target_idles_the_battery():
    request = command(ctrl=controller(settings={ctl.APP_MODE: ctl.MODE_EMS})).request

    assert request == BatteryRequest(kind=RequestKind.BATTERY, power_w=0.0)


@pytest.mark.parametrize(
    ("window", "days", "expected"),
    [
        (((21, 0), (23, 0)), ALL_DAYS, -1000.0),
        (((21, 0), (23, 0)), SUNDAY, -1000.0),
        (((21, 0), (23, 0)), 0x01, None),
        (((23, 0), (23, 30)), ALL_DAYS, None),
        (((20, 0), (6, 0)), ALL_DAYS, -1000.0),
        (((6, 0), (20, 0)), ALL_DAYS, None),
        (((22, 0), (22, 0)), ALL_DAYS, None),
    ],
)
def test_a_charge_slot_forces_charging_inside_its_window_and_weekdays(
    window, days, expected
):
    settings = slot_settings(kind="charge", window=window, days=days)
    settings[ctl.APP_MODE] = ctl.MODE_TIME_OF_USE
    settings[ctl.TOU_OUTSIDE_MODE] = 1

    request = command(ctrl=controller(settings=settings)).request

    if expected is None:
        assert request is None
    else:
        assert request == BatteryRequest(kind=RequestKind.BATTERY, power_w=expected)


def test_a_discharge_slot_forces_discharging_and_charge_slots_win_over_it():
    settings = slot_settings(kind="discharge", window=((21, 0), (23, 0)), percent=20)
    settings[ctl.APP_MODE] = ctl.MODE_TIME_OF_USE
    assert command(ctrl=controller(settings=dict(settings))).request.power_w == 2000.0

    settings.update(slot_settings(kind="charge", window=((21, 0), (23, 0)), percent=5))
    assert command(ctrl=controller(settings=settings)).request.power_w == -500.0


def test_a_slot_without_its_enable_bit_is_ignored():
    settings = slot_settings(kind="charge", window=((21, 0), (23, 0)), enable=0)
    settings[ctl.APP_MODE] = ctl.MODE_TIME_OF_USE
    settings[ctl.TOU_OUTSIDE_MODE] = 1

    assert command(ctrl=controller(settings=settings)).request is None


@pytest.mark.parametrize(("outside", "idle"), [(0, True), (1, False)])
def test_outside_its_windows_time_of_use_follows_the_outside_mode(outside, idle):
    settings = slot_settings(kind="charge", window=((1, 0), (2, 0)))
    settings.update({ctl.APP_MODE: ctl.MODE_TIME_OF_USE, ctl.TOU_OUTSIDE_MODE: outside})

    request = command(ctrl=controller(settings=settings)).request

    assert (request == BatteryRequest(kind=RequestKind.BATTERY, power_w=0.0)) is idle


@pytest.mark.parametrize(
    ("soc", "reserve", "expected_power"),
    [(0.3, 80, -420.0), (0.9, 80, None)],
)
def test_backup_mode_tops_up_to_the_reserve_and_never_discharges(
    soc, reserve, expected_power
):
    settings = {
        ctl.APP_MODE: ctl.MODE_BACKUP,
        ctl.BACKUP_RESERVE: reserve,
        ctl.BACKUP_CHARGE_POWER: 4.2,
    }

    result = command(ctrl=controller(settings=settings), soc=soc)

    assert result.allow_discharge is False
    if expected_power is None:
        assert result.request is None
    else:
        assert result.request == BatteryRequest(
            kind=RequestKind.BATTERY, power_w=expected_power
        )


@pytest.mark.parametrize(
    ("grid_connected", "floor_key"),
    [(True, ctl.DISCHARGE_FLOOR_ON_GRID), (False, ctl.DISCHARGE_FLOOR_OFF_GRID)],
)
def test_soc_bounds_come_from_the_grid_state(grid_connected, floor_key):
    settings = {floor_key: 25, ctl.CHARGE_CEILING: 90}

    result = command(ctrl=controller(settings=settings, grid_connected=grid_connected))

    assert result.floor_soc == 0.25
    assert result.ceiling_soc == 0.9


def test_the_charge_ceiling_defaults_to_full():
    assert command(ctrl=controller()).ceiling_soc == 1.0


@pytest.mark.parametrize(("mode", "expected"), [(0, None), (1, 5000.0)])
def test_anti_reflux_caps_export_only_when_enabled(mode, expected):
    settings = {ctl.ANTI_REFLUX_MODE: mode, ctl.ANTI_REFLUX_POWER_LIMIT: 0.5}

    assert command(ctrl=controller(settings=settings)).export_limit_w == expected


@pytest.mark.parametrize(
    ("enable", "key", "kind"),
    [
        (0b1000, ctl.EMS_INVERTER_TARGET, RequestKind.INVERTER),
        (0b0001, ctl.EMS_INVERTER_TARGET, RequestKind.INVERTER),
        (0b0010, ctl.EMS_BATTERY_TARGET, RequestKind.BATTERY),
        (0b100000, ctl.EMS_GRID_TARGET, RequestKind.GRID),
    ],
)
def test_ems_targets_are_fractions_of_rated_power_and_override_the_application_mode(
    enable, key, kind
):
    settings = {ctl.EMS_ENABLE: enable, key: -0.05, ctl.APP_MODE: ctl.MODE_BACKUP}

    result = command(ctrl=controller(settings=settings))

    assert result.request == BatteryRequest(kind=kind, power_w=-500.0)
    assert result.allow_discharge is True


def test_ems_limits_travel_with_the_command():
    settings = {
        ctl.EMS_ENABLE: 0b1000,
        ctl.EMS_PV_LIMIT: 0.015,
        ctl.EMS_SELL_LIMIT: 0.02,
        ctl.EMS_BUY_LIMIT: 0.03,
        ctl.EMS_BATTERY_CHARGE_CURRENT: 1.5,
        ctl.EMS_BATTERY_DISCHARGE_CURRENT: 2.5,
    }

    result = command(ctrl=controller(settings=settings))

    assert result.pv_limit_w == pytest.approx(150.0)
    assert result.inverter_sell_limit_w == pytest.approx(200.0)
    assert result.inverter_buy_limit_w == pytest.approx(300.0)
    assert result.charge_current_limit_a == 1.5
    assert result.discharge_current_limit_a == 2.5


def test_the_unrestricted_pv_limit_is_no_limit():
    settings = {ctl.EMS_ENABLE: 0b1000, ctl.EMS_PV_LIMIT: ctl.EMS_NO_PV_LIMIT}

    assert command(ctrl=controller(settings=settings)).pv_limit_w is None


@pytest.mark.parametrize(
    "changes",
    [{"has_meter_a": False}, {"inverters": 2}],
)
def test_the_grid_point_target_needs_meter_a_and_a_single_inverter(changes):
    settings = {ctl.EMS_ENABLE: 0b100000, ctl.EMS_GRID_TARGET: -0.05}

    result = command(ctrl=controller(settings=settings, **changes))

    assert result.request is None


def test_ems_bits_are_reported_without_the_exit_noise_of_other_bits():
    assert controller(settings={ctl.EMS_ENABLE: 0b101010}).ems_active_bits() == 0b101010
    assert controller(settings={ctl.EMS_ENABLE: 0b010100}).ems_active_bits() == 0


def ems_settings(**extra):
    settings = {
        ctl.EMS_ENABLE: 0b1000,
        ctl.EMS_TIMEOUT: 5,
        ctl.EMS_INVERTER_TARGET: -0.05,
    }
    settings.update(extra)
    return settings


def test_ems_stays_active_until_the_timeout_elapses_without_keepalive():
    settings = ems_settings()
    ctrl = controller(settings=settings)
    ctrl.keepalive(second=100)

    command(ctrl=ctrl, second=105)
    assert settings[ctl.EMS_ENABLE] == 0b1000
    command(ctrl=ctrl, second=106)

    assert settings[ctl.EMS_ENABLE] == 0
    assert settings[ctl.EMS_INVERTER_TARGET] == 0


def test_a_keepalive_restarts_the_timeout():
    settings = ems_settings()
    ctrl = controller(settings=settings)
    ctrl.keepalive(second=100)
    ctrl.keepalive(second=105)

    command(ctrl=ctrl, second=109)

    assert settings[ctl.EMS_ENABLE] == 0b1000


@pytest.mark.parametrize(
    ("enable", "target_key"),
    [
        (0b0010, ctl.EMS_BATTERY_TARGET),
        (0b100000, ctl.EMS_GRID_TARGET),
        (0b0001, ctl.EMS_INVERTER_TARGET),
    ],
)
def test_only_the_timeout_exit_bit_leaves_ems_but_every_target_is_cleared(
    enable, target_key
):
    settings = ems_settings(**{ctl.EMS_ENABLE: enable, target_key: -0.05})
    ctrl = controller(settings=settings)
    ctrl.keepalive(second=0)

    command(ctrl=ctrl, second=100)

    assert settings[ctl.EMS_ENABLE] == enable
    assert settings[target_key] == 0


def test_the_maximum_timeout_value_and_a_disabled_ems_never_expire():
    never = ems_settings(**{ctl.EMS_TIMEOUT: ctl.EMS_NO_TIMEOUT})
    off = {ctl.EMS_ENABLE: 0, ctl.EMS_TIMEOUT: 1}

    command(ctrl=controller(settings=never), second=10**6)
    command(ctrl=controller(settings=off), second=10**6)

    assert never[ctl.EMS_ENABLE] == 0b1000
    assert off[ctl.EMS_ENABLE] == 0


def test_an_expired_timeout_is_not_applied_twice():
    settings = ems_settings(**{ctl.EMS_ENABLE: 0b1010})
    ctrl = controller(settings=settings)
    ctrl.keepalive(second=0)
    command(ctrl=ctrl, second=100)
    settings[ctl.EMS_BATTERY_TARGET] = -0.1

    command(ctrl=ctrl, second=101)

    assert settings[ctl.EMS_BATTERY_TARGET] == -0.1


def test_schedule_power_reads_the_first_matching_slot_only():
    settings = slot_settings(
        kind="charge", window=((21, 0), (23, 0)), percent=10, index=2, enable=0b10
    )

    assert (
        schedule_power_percent(
            settings=settings,
            kind="charge",
            enable_key=ctl.CHARGE_ENABLE_MASK,
            moment=MONDAY_NIGHT,
        )
        == 10.0
    )
    settings[ctl.CHARGE_ENABLE_MASK] = 0b01
    assert (
        schedule_power_percent(
            settings=settings,
            kind="charge",
            enable_key=ctl.CHARGE_ENABLE_MASK,
            moment=MONDAY_NIGHT,
        )
        is None
    )
