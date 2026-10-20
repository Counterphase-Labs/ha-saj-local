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


def step(*, charger, moment=SUNDAY_EVENING, surplus=0.0, dt=10.0, stopped=False):
    return charger.evaluate(
        moment=moment, surplus_w=surplus, step_s=dt, stopped=stopped
    )


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


def test_a_charger_stopped_by_a_fault_draws_nothing_and_resumes_when_it_clears():
    charger = EvCharger(config=config(sessions=(BIG_SESSION,)), settings=settings())

    assert step(charger=charger, stopped=True) == 0.0
    assert charger.readout().state is ChargerState.CHARGER_SUSPENDED
    assert step(charger=charger, stopped=False) == 7000.0
    assert charger.readout().state is ChargerState.CHARGING


def test_a_stopped_charger_without_a_car_stays_idle():
    charger = EvCharger(config=config(), settings=settings())

    step(charger=charger, moment=SUNDAY_NOON, stopped=True)

    assert charger.readout().state is ChargerState.IDLE


def test_a_car_plugged_in_by_hand_charges_outside_any_schedule_until_its_need_is_met():
    charger = EvCharger(config=config(sessions=()), settings=settings())
    assert step(charger=charger, moment=SUNDAY_NOON) == 0.0

    charger.plug_in(energy_needed_wh=500, moment=SUNDAY_NOON)
    power = step(charger=charger, moment=SUNDAY_NOON, dt=100.0)
    charger.integrate(power_w=power, step_s=100.0)

    readout = charger.readout()
    assert power == 7000.0
    assert readout.state is ChargerState.CHARGING
    assert readout.session_start_s == int((SUNDAY_NOON - EPOCH).total_seconds())
    assert readout.session_end_s == 0
    assert step(charger=charger, moment=SUNDAY_NOON, dt=100.0) > 0
    charger.integrate(power_w=10000.0, step_s=3600.0)
    step(charger=charger, moment=SUNDAY_NOON)
    assert charger.readout().state is ChargerState.COMPLETE


def test_unplugging_by_hand_ends_a_scheduled_session_at_that_second():
    charger = EvCharger(config=config(sessions=(BIG_SESSION,)), settings=settings())
    assert step(charger=charger) == 7000.0
    moment = datetime(2026, 6, 21, 23, 0, 30, tzinfo=UTC)

    charger.unplug(moment=moment)

    assert step(charger=charger, moment=moment) == 0.0
    readout = charger.readout()
    assert readout.state is ChargerState.IDLE
    assert readout.session_end_s == int((moment - EPOCH).total_seconds())


def test_unplugging_a_hand_plugged_car_ends_it_and_keeps_the_open_window_shut():
    charger = EvCharger(config=config(), settings=settings())
    charger.plug_in(energy_needed_wh=500, moment=SUNDAY_EVENING)
    step(charger=charger)
    moment = datetime(2026, 6, 21, 22, 45, tzinfo=UTC)

    charger.unplug(moment=moment)
    step(charger=charger, moment=moment)
    step(charger=charger, moment=datetime(2026, 6, 21, 23, 0, tzinfo=UTC))
    step(charger=charger, moment=datetime(2026, 6, 22, 6, 59, tzinfo=UTC))

    readout = charger.readout()
    assert readout.state is ChargerState.IDLE
    assert readout.session_end_s == int((moment - EPOCH).total_seconds())


@pytest.mark.parametrize(
    "moment",
    [
        datetime(2026, 6, 21, 23, 0, tzinfo=UTC),
        datetime(2026, 6, 22, 3, 0, tzinfo=UTC),
    ],
)
def test_the_scenarios_sessions_return_after_the_window_that_was_cut_short_closes(
    moment,
):
    charger = EvCharger(config=config(sessions=(BIG_SESSION,)), settings=settings())
    assert step(charger=charger, moment=moment) == 7000.0
    charger.unplug(moment=moment)
    assert step(charger=charger, moment=moment) == 0.0

    next_evening = datetime(2026, 6, 22, 22, 30, tzinfo=UTC)
    power = step(charger=charger, moment=next_evening)

    assert power == 7000.0
    assert charger.readout().state is ChargerState.CHARGING
    assert charger.readout().session_energy_wh == 0.0


def test_unplugging_outside_every_window_keeps_the_next_window_open():
    charger = EvCharger(config=config(sessions=(BIG_SESSION,)), settings=settings())
    charger.unplug(moment=SUNDAY_NOON)

    assert step(charger=charger, moment=SUNDAY_EVENING) == 7000.0


def test_a_car_plugged_in_by_hand_stays_through_a_scenario_window_and_after_it():
    charger = EvCharger(config=config(sessions=(BIG_SESSION,)), settings=settings())
    charger.plug_in(energy_needed_wh=100000, moment=SUNDAY_NOON)
    assert step(charger=charger, moment=SUNDAY_NOON) == 7000.0

    assert step(charger=charger, moment=SUNDAY_EVENING) == 7000.0
    next_noon = datetime(2026, 6, 22, 12, 0, tzinfo=UTC)

    assert step(charger=charger, moment=next_noon) == 7000.0


def complete_hand_plugged_car():
    charger = EvCharger(config=config(), settings=settings())
    charger.plug_in(energy_needed_wh=500, moment=SUNDAY_EVENING)
    power = step(charger=charger, dt=3600.0)
    charger.integrate(power_w=power, step_s=3600.0)
    return charger


def test_a_hand_plugged_car_whose_need_is_met_stays_plugged_in_and_complete():
    charger = complete_hand_plugged_car()
    later = datetime(2026, 6, 23, 12, 0, tzinfo=UTC)

    assert step(charger=charger) == 0.0
    assert step(charger=charger, moment=later) == 0.0

    readout = charger.readout()
    assert readout.state is ChargerState.COMPLETE
    assert readout.session_end_s == 0
    assert charger.hand_state().remaining_wh == 0


def test_a_complete_hand_plugged_car_leaves_only_when_unplugged_by_hand():
    charger = complete_hand_plugged_car()
    step(charger=charger)

    charger.unplug(moment=SUNDAY_EVENING)

    assert step(charger=charger) == 0.0
    assert charger.readout().state is ChargerState.IDLE
    next_evening = datetime(2026, 6, 22, 22, 30, tzinfo=UTC)
    assert step(charger=charger, moment=next_evening) == 7000.0


def test_plugging_in_by_hand_ends_a_hold_on_the_window_and_starts_a_fresh_session():
    charger = EvCharger(config=config(sessions=(BIG_SESSION,)), settings=settings())
    charger.unplug(moment=SUNDAY_EVENING)
    step(charger=charger)

    charger.plug_in(energy_needed_wh=500, moment=SUNDAY_EVENING)

    assert step(charger=charger) == 7000.0
    assert charger.hand_state().suppressed_until_s == 0


def test_the_hand_state_is_the_remaining_need_and_the_end_of_a_window_kept_shut():
    charger = EvCharger(config=config(), settings=settings())
    assert charger.hand_state() == ev.HandState(remaining_wh=None, suppressed_until_s=0)
    charger.plug_in(energy_needed_wh=500, moment=SUNDAY_NOON)
    charger.unplug(moment=SUNDAY_EVENING)

    assert charger.hand_state() == ev.HandState(
        remaining_wh=None,
        suppressed_until_s=int(
            (datetime(2026, 6, 22, 7, 0, tzinfo=UTC) - EPOCH).total_seconds()
        ),
    )


def test_a_full_hand_plugged_car_has_nothing_remaining_but_is_still_plugged():
    charger = EvCharger(config=config(sessions=()), settings=settings())
    charger.plug_in(energy_needed_wh=500, moment=SUNDAY_NOON)
    charger.integrate(power_w=10000.0, step_s=3600.0)

    assert charger.hand_state().remaining_wh == 0


def test_restoring_a_complete_hand_plugged_car_plugs_it_in_complete():
    charger = EvCharger(config=config(sessions=()), settings=settings())

    charger.restore_hand_state(
        state=ev.HandState(remaining_wh=0, suppressed_until_s=0), moment=SUNDAY_NOON
    )

    assert step(charger=charger, moment=SUNDAY_NOON) == 0.0
    assert charger.readout().state is ChargerState.COMPLETE


def test_the_remaining_need_is_what_is_left_of_the_hand_plugged_session():
    charger = EvCharger(config=config(sessions=()), settings=settings())
    charger.plug_in(energy_needed_wh=1000, moment=SUNDAY_NOON)
    step(charger=charger, moment=SUNDAY_NOON)
    charger.integrate(power_w=3600.0, step_s=100.0)

    assert charger.hand_state().remaining_wh == 900


def test_restoring_the_hand_state_plugs_the_car_in_with_its_remaining_need():
    charger = EvCharger(config=config(), settings=settings())

    charger.restore_hand_state(
        state=ev.HandState(remaining_wh=300, suppressed_until_s=0),
        moment=SUNDAY_NOON,
    )

    assert step(charger=charger, moment=SUNDAY_NOON) == 7000.0
    assert charger.hand_state().remaining_wh == 300


def test_restoring_a_window_kept_shut_keeps_the_scenario_car_away_until_it_ends():
    charger = EvCharger(config=config(sessions=(BIG_SESSION,)), settings=settings())
    ends = int((datetime(2026, 6, 22, 7, 0, tzinfo=UTC) - EPOCH).total_seconds())

    charger.restore_hand_state(
        state=ev.HandState(remaining_wh=None, suppressed_until_s=ends),
        moment=SUNDAY_EVENING,
    )

    assert step(charger=charger) == 0.0
    assert step(charger=charger, moment=datetime(2026, 6, 22, 22, 30, tzinfo=UTC)) > 0


def test_restoring_no_hand_state_unplugs_a_hand_plugged_car():
    charger = EvCharger(config=config(sessions=()), settings=settings())
    charger.plug_in(energy_needed_wh=500, moment=SUNDAY_NOON)

    charger.restore_hand_state(
        state=ev.HandState(remaining_wh=None, suppressed_until_s=0), moment=SUNDAY_NOON
    )

    assert step(charger=charger, moment=SUNDAY_NOON) == 0.0


def test_unplugging_when_no_car_is_plugged_changes_no_session_time():
    charger = EvCharger(config=config(), settings=settings())

    charger.unplug(moment=SUNDAY_NOON)

    assert charger.readout().session_end_s == 0


def test_plugging_in_again_starts_a_fresh_session():
    charger = EvCharger(config=config(sessions=()), settings=settings())
    charger.plug_in(energy_needed_wh=100000, moment=SUNDAY_NOON)
    power = step(charger=charger, moment=SUNDAY_NOON)
    charger.integrate(power_w=power, step_s=10.0)
    charger.unplug(moment=SUNDAY_NOON)
    step(charger=charger, moment=SUNDAY_NOON)
    later = datetime(2026, 6, 21, 13, 30, tzinfo=UTC)

    charger.plug_in(energy_needed_wh=100000, moment=later)
    step(charger=charger, moment=later)

    readout = charger.readout()
    assert readout.session_energy_wh == 0.0
    assert readout.session_start_s == int((later - EPOCH).total_seconds())
