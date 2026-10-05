from datetime import UTC, datetime, time

import pytest

from saj_modbus_mock.registers import EPOCH
from saj_modbus_mock.scenario import EvChargerConfig, EvSession
from saj_modbus_mock.simulation import ev_charger as ev
from saj_modbus_mock.simulation.ev_charger import ChargerState, EvCharger

SUNDAY_EVENING = datetime(2026, 6, 21, 22, 30, tzinfo=UTC)
SUNDAY_NOON = datetime(2026, 6, 21, 12, 0, tzinfo=UTC)
NIGHT_SESSION = EvSession(plug_in=time(22, 0), unplug=time(7, 0), energy_needed_wh=500)
BIG_SESSION = EvSession(plug_in=time(22, 0), unplug=time(7, 0), energy_needed_wh=50000)


def config(**changes):
    values = {
        "installed": True,
        "phases": 3,
        "max_power_w": 11000,
        "sessions": (NIGHT_SESSION,),
    }
    values.update(changes)
    return EvChargerConfig(**values)


def settings(**changes):
    values = {ev.EV_ENABLED: 1, ev.EV_MODE: ev.MODE_FORCED, ev.EV_CHARGE_POWER: 7000}
    values.update(changes)
    return values


def step(*, charger, moment=SUNDAY_EVENING, surplus=0.0, dt=10.0):
    return charger.evaluate(moment=moment, surplus_w=surplus, step_s=dt)


def test_a_charger_that_is_not_installed_draws_nothing():
    charger = EvCharger(config=config(installed=False), settings=settings())

    assert step(charger=charger) == 0.0
    assert charger.readout().state is ChargerState.IDLE


def test_without_a_plugged_vehicle_the_charger_is_idle():
    charger = EvCharger(config=config(), settings=settings())

    assert step(charger=charger, moment=SUNDAY_NOON) == 0.0
    assert charger.readout().state is ChargerState.IDLE


def test_forced_charging_draws_the_configured_power_without_integrating_it():
    charger = EvCharger(config=config(sessions=(BIG_SESSION,)), settings=settings())

    power = step(charger=charger)

    readout = charger.readout()
    assert power == 7000.0
    assert readout.state is ChargerState.CHARGING
    assert readout.power_w == 7000.0
    assert readout.session_energy_wh == 0.0
    assert readout.total_energy_wh == 0.0


def test_integrating_a_step_adds_its_energy_to_the_session_and_the_lifetime_total():
    charger = EvCharger(config=config(sessions=(BIG_SESSION,)), settings=settings())
    power = step(charger=charger)

    charger.integrate(power_w=power, step_s=10.0)
    charger.integrate(power_w=0.0, step_s=10.0)

    readout = charger.readout()
    assert readout.session_energy_wh == pytest.approx(7000 * 10 / 3600)
    assert readout.total_energy_wh == readout.session_energy_wh
    assert readout.session_seconds == 10


def test_charging_power_is_capped_at_the_charger_maximum():
    charger = EvCharger(
        config=config(max_power_w=3000, sessions=(BIG_SESSION,)),
        settings=settings(**{ev.EV_CHARGE_POWER: 9000}),
    )

    assert step(charger=charger) == 3000.0


def test_the_last_step_of_a_session_delivers_only_the_remaining_energy():
    charger = EvCharger(
        config=config(), settings=settings(**{ev.EV_CHARGE_POWER: 11000})
    )

    first = step(charger=charger, dt=100.0)
    charger.integrate(power_w=first, step_s=100.0)
    second = step(charger=charger, dt=100.0)
    charger.integrate(power_w=second, step_s=100.0)
    third = step(charger=charger, dt=100.0)

    assert first == 11000.0
    assert second == pytest.approx((500.0 - first * 100 / 3600) * 3600 / 100.0)
    assert charger.readout().session_energy_wh == pytest.approx(500.0)
    assert third == 0.0
    assert charger.readout().state is ChargerState.COMPLETE


def test_the_session_starts_and_ends_at_its_scheduled_seconds_whenever_it_is_noticed():
    charger = EvCharger(config=config(sessions=(BIG_SESSION,)), settings=settings())
    plug_in = datetime(2026, 6, 21, 22, 0, tzinfo=UTC)
    unplug = datetime(2026, 6, 22, 7, 0, tzinfo=UTC)

    step(charger=charger, moment=SUNDAY_EVENING)
    assert charger.readout().session_start_s == int((plug_in - EPOCH).total_seconds())
    step(charger=charger, moment=datetime(2026, 6, 22, 7, 0, 41, tzinfo=UTC))

    readout = charger.readout()
    assert readout.state is ChargerState.IDLE
    assert readout.session_end_s == int((unplug - EPOCH).total_seconds())


def test_noticing_a_session_late_gives_the_same_start_as_noticing_it_at_once():
    early = EvCharger(config=config(sessions=(BIG_SESSION,)), settings=settings())
    late = EvCharger(config=config(sessions=(BIG_SESSION,)), settings=settings())

    step(charger=early, moment=datetime(2026, 6, 21, 22, 0, 1, tzinfo=UTC))
    step(charger=late, moment=datetime(2026, 6, 21, 23, 41, 7, tzinfo=UTC))

    assert early.readout().session_start_s == late.readout().session_start_s


def test_a_new_session_resets_the_session_counters_but_not_the_lifetime_total():
    next_evening = datetime(2026, 6, 22, 22, 30, tzinfo=UTC)
    charger = EvCharger(config=config(sessions=(BIG_SESSION,)), settings=settings())
    charger.integrate(power_w=step(charger=charger), step_s=600.0)
    step(charger=charger, moment=SUNDAY_NOON)
    total = charger.readout().total_energy_wh

    step(charger=charger, moment=next_evening)

    readout = charger.readout()
    assert readout.session_energy_wh == 0.0
    assert readout.session_seconds == 0
    assert readout.total_energy_wh == total
    assert readout.session_start_s > 0


@pytest.mark.parametrize(
    ("changes", "state"),
    [
        ({ev.EV_ENABLED: 0}, ChargerState.READY),
        ({ev.EV_MODE: ev.MODE_DISABLED}, ChargerState.READY),
        ({ev.EV_MODE: ev.MODE_PV_SURPLUS}, ChargerState.CHARGER_SUSPENDED),
        ({ev.EV_MODE: ev.MODE_TIME_BASED}, ChargerState.CHARGER_SUSPENDED),
        ({ev.EV_MODE: ev.MODE_EMS}, ChargerState.CHARGER_SUSPENDED),
    ],
)
def test_a_plugged_vehicle_that_gets_no_power_is_ready_or_suspended(changes, state):
    charger = EvCharger(
        config=config(sessions=(BIG_SESSION,)), settings=settings(**changes)
    )

    assert step(charger=charger) == 0.0
    assert charger.readout().state is state


def slot_settings(*, start, end, date=0x7F00, power=3000, index=1):
    return {
        ev.slot_key(index=index, part="start"): (start[0] << 8) | start[1],
        ev.slot_key(index=index, part="end"): (end[0] << 8) | end[1],
        ev.slot_key(index=index, part="date"): date,
        ev.slot_key(index=index, part="power_w"): power,
    }


@pytest.mark.parametrize(
    ("window", "date", "expected"),
    [
        (((22, 0), (23, 0)), 0x7F00, 3000.0),
        (((22, 0), (23, 0)), 0x4000, 3000.0),
        (((22, 0), (23, 0)), 0x0100, 0.0),
        (((1, 0), (2, 0)), 0x7F00, 0.0),
        (((22, 0), (22, 0)), 0x7F00, 0.0),
        (((20, 0), (6, 0)), 0x7F00, 3000.0),
    ],
)
def test_time_based_charging_follows_the_schedule_slots(window, date, expected):
    values = settings(**{ev.EV_MODE: ev.MODE_TIME_BASED})
    values.update(slot_settings(start=window[0], end=window[1], date=date))
    charger = EvCharger(config=config(sessions=(BIG_SESSION,)), settings=values)

    assert step(charger=charger) == expected


def test_time_based_charging_uses_a_later_matching_slot():
    values = settings(**{ev.EV_MODE: ev.MODE_TIME_BASED})
    values.update(slot_settings(start=(1, 0), end=(2, 0), index=1))
    values.update(slot_settings(start=(22, 0), end=(23, 0), power=1500, index=2))
    charger = EvCharger(config=config(sessions=(BIG_SESSION,)), settings=values)

    assert step(charger=charger) == 1500.0


@pytest.mark.parametrize(
    ("surplus", "function", "expected"),
    [
        (20000.0, 0, 11000.0),
        (5000.0, 0, 5000.0),
        (1000.0, 0, 0.0),
        (1000.0, 4, 6 * 230 * 3),
    ],
)
def test_surplus_charging_follows_solar_power_with_an_optional_minimum_current(
    surplus, function, expected
):
    values = settings(**{ev.EV_MODE: ev.MODE_PV_SURPLUS, ev.EV_FUNCTION: function})
    charger = EvCharger(config=config(sessions=(BIG_SESSION,)), settings=values)

    assert step(charger=charger, surplus=surplus) == expected


@pytest.mark.parametrize(
    ("command", "current", "phases", "expected"),
    [
        (1, 10.0, 3, 0.0),
        (0, 10.0, 3, 6900.0),
        (0, 10.0, 1, 2300.0),
        (0, 32.0, 3, 11000.0),
    ],
)
def test_ems_charging_needs_a_start_command_and_uses_the_commanded_current(
    command, current, phases, expected
):
    values = settings(
        **{
            ev.EV_MODE: ev.MODE_EMS,
            ev.EV_EMS_COMMAND: command,
            ev.EV_EMS_CURRENT: current,
        }
    )
    charger = EvCharger(
        config=config(phases=phases, sessions=(BIG_SESSION,)), settings=values
    )

    assert step(charger=charger) == expected


def test_text_settings_count_as_unset():
    charger = EvCharger(
        config=config(sessions=(BIG_SESSION,)),
        settings=settings(**{ev.EV_ENABLED: "yes"}),
    )

    assert step(charger=charger) == 0.0


def test_a_session_that_started_yesterday_reports_yesterdays_plug_in_second():
    charger = EvCharger(config=config(sessions=(BIG_SESSION,)), settings=settings())
    early_morning = datetime(2026, 6, 22, 3, 0, tzinfo=UTC)
    plug_in = datetime(2026, 6, 21, 22, 0, tzinfo=UTC)

    step(charger=charger, moment=early_morning)

    assert charger.readout().session_start_s == int((plug_in - EPOCH).total_seconds())
