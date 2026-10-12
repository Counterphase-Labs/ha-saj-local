import asyncio
import logging
from datetime import timedelta

import pytest

from custom_components.saj_local import coordinator as coordinator_module
from custom_components.saj_local.const import PowerSchedule
from custom_components.saj_local.saj.control import Write
from custom_components.saj_local.saj.errors import (
    AnotherFunctionRunningError,
    ControlDisabledError,
    EmsTimeoutError,
    LinkUnavailableError,
    NoPowerTargetError,
    WriteRejectedError,
)
from custom_components.saj_local.saj.models import PowerFunction, ems_rows
from tests.coordinators import (
    DIRECTION_KEY,
    ENABLE_KEYS,
    INTERVAL,
    MODE_KEY,
    STANDBY,
    TARGET_KEYS,
    FakeFunctionControl,
    FakeStore,
    RowNames,
    build,
    cycle,
    hold_cycle,
    read_result,
    statements,
)

BATTERY = PowerFunction.BATTERY
GRID = PowerFunction.GRID
INVERTER = PowerFunction.INVERTER
BATTERY_ENABLE = ENABLE_KEYS[BATTERY]
BATTERY_TARGET = TARGET_KEYS[BATTERY]
GRID_ENABLE = ENABLE_KEYS[GRID]
INVERTER_ENABLE = ENABLE_KEYS[INVERTER]
INVERTER_ALTERNATE = "ems_inverter_control"
NIGHT = "schedule.night"
DAY = "schedule.day"
RETRY_TIMER = "SAJ power control retry"
HEARTBEAT_TIMER = "SAJ EMS heartbeat"


def _operating_mode(*, remember=0):
    return {
        BATTERY: FakeFunctionControl(
            BATTERY,
            prior_key=MODE_KEY,
            remember=remember,
            two_step_stop=True,
        )
    }


def _ok(count: int):
    return [read_result({}) for _ in range(count)]


def _timers(recorder, name: str) -> list[dict]:
    return [timer for timer in recorder.timers if timer["name"] == name]


def _schedule(coordinator, function, entity_id, state, **attributes):
    coordinator.schedules = (
        *coordinator.schedules,
        PowerSchedule(function=function, entity_id=entity_id),
    )
    coordinator.hass.states.set(entity_id, state, **attributes)


async def _following(coordinator):
    await coordinator.async_follow_schedules()


async def test_the_stored_targets_and_modes_are_restored_for_functions_the_system_has(
    recorder,
):
    coordinator = build(recorder, functions=_operating_mode())
    coordinator._store = FakeStore(
        {
            "targets": {"battery": -600, "grid": 100},
            "remembered_modes": {"battery": 1, "inverter": 2},
        }
    )

    await coordinator.async_load_power_state()

    assert coordinator.power_targets == {BATTERY: -600}
    assert coordinator.remembered_modes == {BATTERY: 1}


async def test_nothing_stored_means_no_targets_and_no_remembered_mode(recorder):
    coordinator = build(recorder)

    await coordinator.async_load_power_state()

    assert coordinator.power_targets == {}
    assert coordinator.remembered_modes == {}


@pytest.mark.parametrize(
    ("values", "targets", "shown"),
    [
        ({BATTERY_ENABLE: 1, BATTERY_TARGET: -500}, {BATTERY: -600}, -500),
        ({BATTERY_ENABLE: 1}, {BATTERY: -600}, -600),
        ({BATTERY_ENABLE: 0, BATTERY_TARGET: -500}, {BATTERY: -600}, -600),
        ({}, {BATTERY: -600}, -600),
        ({BATTERY_ENABLE: 1}, {}, None),
    ],
    ids=["held", "held-unknown", "not-running", "unknown", "nothing"],
)
async def test_the_target_shown_is_what_the_inverter_holds_or_else_the_kept_target(
    recorder, values, targets, shown
):
    coordinator = build(recorder)
    coordinator._values = values
    coordinator.power_targets = targets

    assert coordinator.power_target_shown(function=BATTERY) == shown


async def test_a_value_only_assumed_is_used_for_the_state_and_a_polled_one_wins(
    recorder,
):
    coordinator = build(recorder)
    coordinator.assumed = {BATTERY_ENABLE: 0, BATTERY_TARGET: -500}
    coordinator._values = {BATTERY_ENABLE: 1}

    assert coordinator.power_running(function=BATTERY) is True
    assert coordinator.power_target_shown(function=BATTERY) == -500
    assert coordinator.power_range(function=BATTERY).maximum == 1000


async def test_switching_on_sends_the_target_then_the_bit_under_the_lock_and_owns_it(
    recorder, caplog
):
    coordinator = build(recorder)
    coordinator.power_targets[BATTERY] = -600
    coordinator.control.outcomes = _ok(2)
    coordinator.control.hold = asyncio.Event()

    with caplog.at_level(logging.INFO, logger=coordinator_module.__name__):
        starting = asyncio.create_task(coordinator.async_power_on(function=BATTERY))
        await coordinator.control.entered.wait()
        assert coordinator._cycle_lock.locked()
        coordinator.control.hold.set()
        await starting

    first, second = coordinator.control.calls
    assert (first["key"], first["value"]) == (BATTERY_TARGET, -600)
    assert (second["key"], second["value"]) == (BATTERY_ENABLE, 1)
    assert second["inspection"].extra_words == 1
    assert first["inspection"] is None
    assert coordinator.ems.owned == {BATTERY}
    assert len(_timers(recorder, HEARTBEAT_TIMER)) == 1
    assert coordinator._store.saved[-1] == {
        "targets": {"battery": -600},
        "remembered_modes": {},
    }
    assert "battery power control function started" in caplog.text


@pytest.mark.parametrize(
    ("setup", "error"),
    [
        ({"admission": ControlDisabledError()}, ControlDisabledError),
        ({}, NoPowerTargetError),
    ],
    ids=["control-off", "no-target"],
)
async def test_a_refused_switch_on_sends_nothing(recorder, setup, error):
    coordinator = build(recorder)
    coordinator.control.admission = setup.get("admission")
    coordinator.power_targets = setup.get("targets", {})

    with pytest.raises(error):
        await coordinator.async_power_on(function=BATTERY)

    assert coordinator.control.calls == []
    assert coordinator.control.settings_read == []
    assert coordinator.ems.owned == frozenset()


async def test_a_write_the_inverter_refuses_part_way_through_a_start_is_stopped_again(
    recorder,
):
    coordinator = build(recorder)
    coordinator.power_targets[BATTERY] = -600
    coordinator.control.outcomes = [
        read_result({}),
        WriteRejectedError(exception_code=2),
    ]
    coordinator.control.switch_off_outcomes = _ok(1)

    with pytest.raises(WriteRejectedError):
        await coordinator.async_power_on(function=BATTERY)

    assert coordinator.control.switch_offs == [Write(key=BATTERY_ENABLE, value=0)]
    assert coordinator.ems.owned == frozenset()


async def test_a_start_that_fails_at_its_first_write_has_nothing_to_stop(recorder):
    coordinator = build(recorder)
    coordinator.power_targets[BATTERY] = -600
    coordinator.control.outcomes = [WriteRejectedError(exception_code=2)]

    with pytest.raises(WriteRejectedError):
        await coordinator.async_power_on(function=BATTERY)

    assert coordinator.control.switch_offs == []
    assert coordinator.ems.owned == frozenset()


async def test_a_stop_that_fails_while_undoing_a_start_does_not_hide_the_first_failure(
    recorder, caplog
):
    coordinator = build(recorder)
    coordinator.power_targets[BATTERY] = -600
    coordinator.control.outcomes = [
        read_result({}),
        WriteRejectedError(exception_code=2),
    ]
    coordinator.control.switch_off_outcomes = [LinkUnavailableError()]

    with (
        caplog.at_level(logging.DEBUG, logger=coordinator_module.__name__),
        pytest.raises(WriteRejectedError),
    ):
        await coordinator.async_power_on(function=BATTERY)

    assert "could not undo the partial start of battery" in caplog.text


async def test_an_operating_mode_start_reads_the_mode_first_and_remembers_it(recorder):
    coordinator = build(recorder, functions=_operating_mode(remember=1))
    coordinator.power_targets[BATTERY] = -600
    coordinator.control.setting_outcomes = [1.0]
    coordinator.control.outcomes = _ok(2)

    await coordinator.async_power_on(function=BATTERY)

    assert coordinator.control.settings_read == [MODE_KEY]
    assert coordinator.power_controls[BATTERY].starts == [(-600, 1.0)]
    assert coordinator.remembered_modes == {BATTERY: 1}
    assert coordinator._store.saved[-1]["remembered_modes"] == {"battery": 1}
    assert _timers(recorder, HEARTBEAT_TIMER) == []


@pytest.mark.parametrize(
    ("failure", "link_lost"),
    [
        (LinkUnavailableError(cause=TimeoutError()), 1),
        (WriteRejectedError(exception_code=2), 0),
    ],
    ids=["link-failed", "refused"],
)
async def test_a_failed_read_of_the_mode_stops_the_start_before_anything_is_written(
    recorder, failure, link_lost
):
    coordinator = build(recorder, functions=_operating_mode())
    coordinator.power_targets[BATTERY] = -600
    coordinator.control.setting_outcomes = [failure]

    with pytest.raises(type(failure)):
        await coordinator.async_power_on(function=BATTERY)

    assert coordinator.control.calls == []
    assert coordinator.poller.link_failures == link_lost
    assert coordinator.remembered_modes == {}


@pytest.mark.parametrize(("previous", "restored"), [(None, {}), (2, {BATTERY: 2})])
async def test_a_start_that_fails_at_its_first_write_puts_the_remembered_mode_back(
    recorder, previous, restored
):
    coordinator = build(recorder, functions=_operating_mode(remember=1))
    coordinator.power_targets[BATTERY] = -600
    if previous is not None:
        coordinator.remembered_modes[BATTERY] = previous
    coordinator.control.setting_outcomes = [0]
    coordinator.control.outcomes = [WriteRejectedError(exception_code=2)]

    with pytest.raises(WriteRejectedError):
        await coordinator.async_power_on(function=BATTERY)

    assert coordinator.remembered_modes == restored


async def _running_operating_mode(recorder):
    coordinator = build(recorder, functions=_operating_mode(remember=1))
    coordinator.power_targets[BATTERY] = -600
    coordinator.control.setting_outcomes = [1]
    coordinator.control.outcomes = _ok(4)
    await coordinator.async_power_on(function=BATTERY)
    return coordinator


async def test_an_operating_mode_stop_sends_both_writes_and_forgets_the_mode(
    recorder, caplog
):
    coordinator = await _running_operating_mode(recorder)

    with caplog.at_level(logging.INFO, logger=coordinator_module.__name__):
        await coordinator.async_power_off(function=BATTERY)

    assert coordinator.control.switch_offs == [
        Write(key=DIRECTION_KEY, value=STANDBY),
        Write(key=MODE_KEY, value=1),
    ]
    assert coordinator.remembered_modes == {}
    assert coordinator.ems.owned == frozenset()
    assert coordinator._store.saved[-1]["remembered_modes"] == {}
    assert "battery power control function stopped" in caplog.text


async def test_a_stop_that_gets_its_first_write_through_is_finished_by_the_next_attempt(
    recorder,
):
    coordinator = build(recorder, functions=_operating_mode(remember=1))
    coordinator.power_targets[BATTERY] = -600
    coordinator.control.setting_outcomes = [1]
    coordinator.control.outcomes = [
        read_result({}),
        read_result({}),
        read_result({}),
        WriteRejectedError(exception_code=2),
        read_result({}),
        read_result({}),
    ]
    await coordinator.async_power_on(function=BATTERY)
    coordinator.control.outcomes = [
        read_result({}),
        WriteRejectedError(exception_code=2),
        read_result({}),
        read_result({}),
    ]

    with pytest.raises(WriteRejectedError):
        await coordinator.async_power_off(function=BATTERY)
    assert coordinator.ems.owned == {BATTERY}
    assert coordinator.remembered_modes == {BATTERY: 1}

    await coordinator.async_power_off(function=BATTERY)

    assert coordinator.power_controls[BATTERY].stops == [1, 1]
    assert coordinator.ems.owned == frozenset()
    assert coordinator.remembered_modes == {}


async def test_a_start_is_refused_by_a_fresh_read_whatever_entities_are_enabled(
    recorder,
):
    coordinator = build(recorder)
    coordinator.power_targets[BATTERY] = 1
    coordinator.control.state_outcomes = [{GRID_ENABLE: 1}]

    with pytest.raises(AnotherFunctionRunningError) as caught:
        await coordinator.async_power_on(function=BATTERY)

    assert caught.value.running is GRID
    assert coordinator.control.states_read == [
        {GRID_ENABLE, INVERTER_ENABLE, INVERTER_ALTERNATE}
    ]
    assert coordinator.control.calls == []
    assert coordinator.control.settings_read == []
    assert coordinator.ems.owned == frozenset()


async def test_a_system_where_nothing_else_runs_may_start(recorder):
    coordinator = build(recorder)
    coordinator._values = {GRID_ENABLE: 0}
    coordinator.power_targets[BATTERY] = 1
    coordinator.control.state_outcomes = [{GRID_ENABLE: 0, INVERTER_ENABLE: 0}]
    coordinator.control.outcomes = _ok(2)

    await coordinator.async_power_on(function=BATTERY)

    assert len(coordinator.control.calls) == 2


async def test_a_system_with_one_function_has_no_other_function_to_read(recorder):
    coordinator = build(recorder, functions={BATTERY: FakeFunctionControl(BATTERY)})
    coordinator.power_targets[BATTERY] = 1
    coordinator.control.outcomes = _ok(2)

    await coordinator.async_power_on(function=BATTERY)

    assert coordinator.control.states_read == []


@pytest.mark.parametrize(
    ("failure", "link_failures", "rejected"),
    [
        (LinkUnavailableError(cause=TimeoutError()), 1, 0),
        (WriteRejectedError(exception_code=2), 0, 1),
        (ControlDisabledError(), 0, 0),
    ],
)
async def test_a_failed_fresh_read_is_handled_like_a_failed_read_before_a_write(
    recorder, failure, link_failures, rejected
):
    coordinator = build(recorder)
    coordinator.power_targets[BATTERY] = 1
    coordinator.control.state_outcomes = [failure]

    with pytest.raises(type(failure)):
        await coordinator.async_power_on(function=BATTERY)

    assert coordinator.poller.link_failures == link_failures
    assert coordinator.writes.rejected == rejected
    assert coordinator.control.calls == []


async def test_a_schedule_start_is_refused_by_the_fresh_read_and_stays_outstanding(
    recorder,
):
    coordinator = build(recorder)
    _schedule(coordinator, BATTERY, NIGHT, "on", power=-600)
    coordinator.control.state_outcomes = [{GRID_ENABLE: 1}]

    await coordinator.async_follow_schedules()

    assert coordinator.control.calls == []
    assert coordinator.outstanding == {BATTERY: "start"}
    assert coordinator.ems.owned == frozenset()


async def _failed_start_whose_undo_fails(recorder, caplog=None):
    coordinator = build(recorder, functions=_operating_mode(remember=1))
    coordinator.power_targets[BATTERY] = -600
    coordinator.control.setting_outcomes = [1]
    coordinator.control.outcomes = [
        read_result({}),
        WriteRejectedError(exception_code=2),
    ]
    coordinator.control.switch_off_outcomes = [WriteRejectedError(exception_code=3)]
    return coordinator


async def test_a_failed_start_whose_undo_fails_is_owned_with_its_stop_outstanding(
    recorder,
):
    coordinator = await _failed_start_whose_undo_fails(recorder)

    with pytest.raises(WriteRejectedError) as caught:
        await coordinator.async_power_on(function=BATTERY)

    assert caught.value.exception_code == 2
    assert coordinator.ems.owned == {BATTERY}
    assert coordinator.remembered_modes == {BATTERY: 1}
    assert coordinator.outstanding == {BATTERY: "stop"}
    (timer,) = _timers(recorder, RETRY_TIMER)
    assert timer["interval"] == timedelta(seconds=INTERVAL)
    assert recorder.listeners == []


async def test_an_outstanding_stop_is_resent_each_interval_with_no_schedule(
    recorder, caplog
):
    coordinator = await _failed_start_whose_undo_fails(recorder)
    with pytest.raises(WriteRejectedError):
        await coordinator.async_power_on(function=BATTERY)
    retry = _timers(recorder, RETRY_TIMER)[0]["action"]
    cancelled = recorder.cancelled
    coordinator.control.switch_off_outcomes = [
        WriteRejectedError(exception_code=3),
        read_result({}),
        read_result({}),
    ]

    with caplog.at_level(logging.DEBUG, logger=coordinator_module.__name__):
        await retry(None)
        assert coordinator.ems.owned == {BATTERY}
        await retry(None)

    assert [write.key for write in coordinator.control.switch_offs] == [
        DIRECTION_KEY,
        DIRECTION_KEY,
        DIRECTION_KEY,
        MODE_KEY,
    ]
    assert coordinator.control.switch_offs[-1] == Write(key=MODE_KEY, value=1)
    assert coordinator.ems.owned == frozenset()
    assert coordinator.remembered_modes == {}
    assert coordinator.outstanding == {}
    assert recorder.cancelled == cancelled + 1
    levels = [
        record.levelno
        for record in caplog.records
        if "could not be stopped" in record.message
    ]
    assert levels == [logging.DEBUG]


async def test_the_outstanding_stop_is_not_kept_alive_and_unload_switches_it_off(
    recorder,
):
    coordinator = await _failed_start_whose_undo_fails(recorder)
    with pytest.raises(WriteRejectedError):
        await coordinator.async_power_on(function=BATTERY)
    coordinator.control.switch_off_outcomes = _ok(2)

    await coordinator.async_release_power_control()

    assert coordinator.control.switch_offs[-1] == Write(key=MODE_KEY, value=1)
    assert coordinator.ems.owned == frozenset()
    assert coordinator.remembered_modes == {}


async def test_with_a_schedule_the_mode_is_put_back_before_anything_starts_again(
    recorder,
):
    coordinator = await _failed_start_whose_undo_fails(recorder)
    _schedule(coordinator, BATTERY, NIGHT, "on", power=-600)

    await coordinator.async_follow_schedules()

    assert coordinator.outstanding == {BATTERY: "stop"}
    assert coordinator._started == {}
    coordinator.hass.states.set(NIGHT, "off")
    coordinator.control.switch_off_outcomes = _ok(2)
    retry = _timers(recorder, RETRY_TIMER)[0]["action"]

    await retry(None)

    assert coordinator.control.switch_offs[-1] == Write(key=MODE_KEY, value=1)
    assert coordinator.ems.owned == frozenset()
    assert coordinator.remembered_modes == {}
    assert len(coordinator.control.calls) == 2


async def test_a_function_whose_stop_is_outstanding_is_not_taken_over_by_its_schedule(
    recorder,
):
    coordinator = await _failed_start_whose_undo_fails(recorder)
    _schedule(coordinator, BATTERY, NIGHT, "on", power=-600)
    await coordinator.async_follow_schedules()
    coordinator._values = {BATTERY_ENABLE: 1}
    coordinator.control.switch_off_outcomes = [WriteRejectedError(exception_code=3)]

    await coordinator._follow()

    assert coordinator._started == {}
    assert coordinator.outstanding == {BATTERY: "stop"}


async def test_a_function_read_out_of_its_mode_is_released_and_forgets_the_mode(
    recorder,
):
    coordinator = await _failed_start_whose_undo_fails(recorder)
    with pytest.raises(WriteRejectedError):
        await coordinator.async_power_on(function=BATTERY)
    cancelled = recorder.cancelled
    coordinator.poller.outcomes = [cycle({BATTERY_ENABLE: 0})]

    await coordinator._async_update_data()

    assert coordinator.ems.owned == frozenset()
    assert coordinator.remembered_modes == {}
    assert coordinator._store.saved[-1]["remembered_modes"] == {}
    assert coordinator.outstanding == {}
    assert recorder.cancelled == cancelled + 1


async def test_a_half_done_stop_leaves_the_function_owned_and_running_in_its_mode(
    recorder,
):
    coordinator = await _failed_start_whose_undo_fails(recorder)
    with pytest.raises(WriteRejectedError):
        await coordinator.async_power_on(function=BATTERY)
    coordinator.poller.outcomes = [cycle({BATTERY_ENABLE: 1})]

    await coordinator._async_update_data()

    assert coordinator.ems.owned == {BATTERY}
    assert coordinator.remembered_modes == {BATTERY: 1}


async def test_releasing_a_function_with_no_remembered_mode_saves_nothing(recorder):
    coordinator = build(recorder)
    coordinator.ems.acquire(function=GRID)
    coordinator.poller.outcomes = [cycle({GRID_ENABLE: 0})]

    await coordinator._async_update_data()

    assert coordinator.ems.owned == frozenset()
    assert coordinator._store.saved == []


async def test_setting_a_target_while_off_keeps_it_and_sends_nothing(recorder):
    coordinator = build(recorder)

    await coordinator.async_set_power_target(function=BATTERY, raw=-600.0)

    assert coordinator.power_targets == {BATTERY: -600}
    assert coordinator.control.calls == []
    assert coordinator._store.saved[-1]["targets"] == {"battery": -600}
    assert recorder.notified


async def test_setting_a_target_while_running_changes_the_power_at_once(recorder):
    coordinator = build(recorder)
    coordinator._values = {BATTERY_ENABLE: 1}
    coordinator.control.outcomes = _ok(1)

    await coordinator.async_set_power_target(function=BATTERY, raw=-300)

    (call,) = coordinator.control.calls
    assert (call["key"], call["value"]) == (BATTERY_TARGET, -300)
    assert coordinator.power_controls[BATTERY].changes == [(-300, {BATTERY_ENABLE: 1})]
    assert coordinator.power_targets == {BATTERY: -300}


async def test_a_target_the_inverter_refuses_is_not_kept(recorder):
    coordinator = build(recorder)
    coordinator._values = {BATTERY_ENABLE: 1}
    coordinator.power_targets[BATTERY] = -600
    coordinator.control.outcomes = [WriteRejectedError(exception_code=2)]

    with pytest.raises(WriteRejectedError):
        await coordinator.async_set_power_target(function=BATTERY, raw=-300)

    assert coordinator.power_targets == {BATTERY: -600}


async def test_switching_off_stops_a_function_not_owned_and_clears_its_bit(recorder):
    coordinator = build(recorder)
    coordinator.control.outcomes = _ok(1)

    await coordinator.async_power_off(function=BATTERY)

    assert coordinator.control.switch_offs == [Write(key=BATTERY_ENABLE, value=0)]
    assert coordinator.power_controls[BATTERY].stops == [None]


async def test_an_operating_mode_function_switched_on_is_switched_off_on_unload(
    recorder,
):
    coordinator = await _running_operating_mode(recorder)

    await coordinator.async_release_power_control()

    assert coordinator.control.switch_offs == [
        Write(key=DIRECTION_KEY, value=STANDBY),
        Write(key=MODE_KEY, value=1),
    ]
    assert coordinator.ems.owned == frozenset()
    assert coordinator.remembered_modes == {}


async def test_one_function_that_cannot_be_switched_off_does_not_stop_the_others(
    recorder, caplog
):
    coordinator = build(recorder)
    coordinator.power_targets = {BATTERY: 1, GRID: 1}
    coordinator.control.outcomes = _ok(4)
    await coordinator.async_power_on(function=BATTERY)
    coordinator._values = {}
    await coordinator.async_power_on(function=GRID)
    coordinator.control.switch_off_outcomes = [
        WriteRejectedError(exception_code=2),
        read_result({}),
    ]

    with caplog.at_level(logging.INFO, logger=coordinator_module.__name__):
        await coordinator.async_release_power_control()

    assert [write.key for write in coordinator.control.switch_offs] == [
        BATTERY_ENABLE,
        GRID_ENABLE,
    ]
    assert "could not switch off the battery power control" in caplog.text
    assert "grid power control function stopped" in caplog.text
    assert coordinator.ems.owned == frozenset()


async def test_an_operating_mode_function_is_not_kept_alive(recorder):
    coordinator = build(recorder, functions=_operating_mode())
    coordinator.power_targets[BATTERY] = -600
    coordinator.control.setting_outcomes = [0]
    coordinator.control.outcomes = _ok(2)

    await coordinator.async_power_on(function=BATTERY)
    await coordinator._beat(None)

    assert _timers(recorder, HEARTBEAT_TIMER) == []
    assert coordinator.control.keep_alives == []


async def test_without_schedules_nothing_is_listened_to_or_decided(recorder):
    coordinator = build(recorder)

    await coordinator.async_follow_schedules()

    assert recorder.listeners == []
    assert coordinator.control.calls == []


async def test_a_schedule_that_is_on_at_load_starts_its_function_at_the_block_power(
    recorder,
):
    coordinator = build(recorder)
    _schedule(coordinator, BATTERY, NIGHT, "on", power=-600)
    coordinator.control.outcomes = _ok(2)

    await coordinator.async_follow_schedules()

    assert recorder.listeners[0]["ids"] == [NIGHT]
    assert [call["key"] for call in coordinator.control.calls] == [
        BATTERY_TARGET,
        BATTERY_ENABLE,
    ]
    assert coordinator.control.calls[0]["value"] == -600
    assert coordinator.power_targets == {BATTERY: -600}
    assert coordinator.ems.owned == {BATTERY}
    assert coordinator.outstanding == {}
    assert _timers(recorder, RETRY_TIMER) == []


async def test_a_schedule_without_a_block_power_starts_at_the_kept_target(recorder):
    coordinator = build(recorder)
    _schedule(coordinator, BATTERY, NIGHT, "on")
    coordinator.power_targets[BATTERY] = -400
    coordinator.control.outcomes = _ok(2)

    await coordinator.async_follow_schedules()

    assert coordinator.control.calls[0]["value"] == -400


async def test_a_schedule_change_runs_the_controller_in_the_background(recorder):
    coordinator = build(recorder)
    _schedule(coordinator, BATTERY, NIGHT, "on")
    await coordinator.async_follow_schedules()

    coordinator._schedule_changed(None)

    assert [name for _, name in recorder.tasks] == ["SAJ power control schedule"]


@pytest.mark.parametrize("state", ["off", "unavailable", "unknown", None])
async def test_a_schedule_whose_state_is_not_on_is_not_wanted(recorder, state):
    coordinator = build(recorder)
    _schedule(coordinator, BATTERY, NIGHT, "on", power=-600)
    coordinator.control.outcomes = _ok(2)
    coordinator.control.switch_off_outcomes = _ok(1)
    await coordinator.async_follow_schedules()
    if state is None:
        del coordinator.hass.states.by_id[NIGHT]
    else:
        coordinator.hass.states.set(NIGHT, state)

    await coordinator._follow()

    assert coordinator.control.switch_offs == [Write(key=BATTERY_ENABLE, value=0)]
    assert coordinator.ems.owned == frozenset()
    assert coordinator._started == {}


async def test_a_function_started_by_hand_is_left_alone_when_its_schedule_is_off(
    recorder,
):
    coordinator = build(recorder)
    _schedule(coordinator, BATTERY, NIGHT, "off")
    coordinator.ems.acquire(function=BATTERY)
    coordinator._values = {BATTERY_ENABLE: 1}

    await coordinator.async_follow_schedules()

    assert coordinator.control.calls == []
    assert coordinator.control.switch_offs == []


async def test_nothing_is_sent_while_nothing_is_wanted_and_nothing_is_outstanding(
    recorder,
):
    coordinator = build(recorder)
    _schedule(coordinator, BATTERY, NIGHT, "on", power=-600)
    coordinator.control.outcomes = _ok(2)
    await coordinator.async_follow_schedules()
    coordinator.control.calls.clear()

    await coordinator._follow()
    await coordinator._follow()

    assert coordinator.control.calls == []
    assert coordinator.control.switch_offs == []


async def test_a_function_switched_off_by_hand_is_not_started_again_until_the_next_on(
    recorder,
):
    coordinator = build(recorder)
    _schedule(coordinator, BATTERY, NIGHT, "on", power=-600)
    coordinator.control.outcomes = _ok(4)
    coordinator.control.switch_off_outcomes = _ok(1)
    await coordinator.async_follow_schedules()
    await coordinator.async_power_off(function=BATTERY)
    coordinator.control.calls.clear()

    await coordinator._follow()

    assert coordinator.control.calls == []
    coordinator.hass.states.set(NIGHT, "off")
    await coordinator._follow()
    coordinator.hass.states.set(NIGHT, "on", power=-600)
    await coordinator._follow()
    assert [call["key"] for call in coordinator.control.calls] == [
        BATTERY_TARGET,
        BATTERY_ENABLE,
    ]


@pytest.mark.parametrize(("first", "second"), [(-600, -300), (0, -600)])
async def test_a_new_block_power_changes_the_power_of_a_running_function(
    recorder, first, second
):
    coordinator = build(recorder)
    _schedule(coordinator, BATTERY, NIGHT, "on", power=first)
    coordinator.control.outcomes = _ok(3)
    await coordinator.async_follow_schedules()
    coordinator._values = {BATTERY_ENABLE: 1}
    coordinator.control.calls.clear()
    coordinator.hass.states.set(NIGHT, "on", power=second)

    await coordinator._follow()

    (call,) = coordinator.control.calls
    assert (call["key"], call["value"]) == (BATTERY_TARGET, second)
    assert coordinator.power_targets == {BATTERY: second}
    assert coordinator._started == {BATTERY: second}


async def test_a_function_already_running_is_taken_over_at_the_block_power(
    recorder,
):
    coordinator = build(recorder)
    coordinator._values = {BATTERY_ENABLE: 1}
    _schedule(coordinator, BATTERY, NIGHT, "on", power=-300)
    coordinator.control.outcomes = _ok(1)

    await coordinator.async_follow_schedules()

    assert [(call["key"], call["value"]) for call in coordinator.control.calls] == [
        (BATTERY_TARGET, -300)
    ]
    assert coordinator.ems.owned == {BATTERY}
    assert len(_timers(recorder, HEARTBEAT_TIMER)) == 1
    assert coordinator._started == {BATTERY: -300}


async def test_a_function_already_running_without_a_block_power_is_only_taken_over(
    recorder,
):
    coordinator = build(recorder)
    coordinator._values = {BATTERY_ENABLE: 1}
    _schedule(coordinator, BATTERY, NIGHT, "on")

    await coordinator.async_follow_schedules()

    assert coordinator.control.calls == []
    assert coordinator.ems.owned == {BATTERY}


@pytest.mark.parametrize(
    ("setup", "label", "message"),
    [
        ({"state": {}}, "no_target", "no power has been set"),
        ({"state": {"power": 0.5}}, "unusable_power", "not a whole number"),
        (
            {"state": {"power": -600}, "running": GRID_ENABLE},
            "another_running",
            "another power control function is running",
        ),
    ],
)
async def test_a_start_that_cannot_happen_is_outstanding_and_warns_once(
    recorder, caplog, setup, label, message
):
    coordinator = build(recorder)
    coordinator._values = {setup["running"]: 1} if "running" in setup else {}
    _schedule(coordinator, BATTERY, NIGHT, "on", **setup["state"])

    with caplog.at_level(logging.DEBUG, logger=coordinator_module.__name__):
        await coordinator.async_follow_schedules()
        first = [
            record.levelno for record in caplog.records if message in record.message
        ]
        await coordinator._follow()

    assert first == [logging.WARNING]
    assert [
        record.levelno for record in caplog.records if message in record.message
    ] == [logging.WARNING, logging.DEBUG]
    assert coordinator.outstanding == {BATTERY: label}
    assert coordinator.control.calls == []
    (timer,) = _timers(recorder, RETRY_TIMER)
    assert timer["interval"] == timedelta(seconds=INTERVAL)


async def test_a_start_that_fails_is_tried_again_each_interval_until_it_works(
    recorder, caplog
):
    coordinator = build(recorder)
    _schedule(coordinator, BATTERY, NIGHT, "on", power=-600)
    coordinator.control.outcomes = [
        WriteRejectedError(exception_code=2),
        WriteRejectedError(exception_code=2),
        read_result({}),
        read_result({}),
    ]

    with caplog.at_level(logging.DEBUG, logger=coordinator_module.__name__):
        await coordinator.async_follow_schedules()
        retry = _timers(recorder, RETRY_TIMER)[0]["action"]
        await retry(None)
        await retry(None)

    levels = [
        record.levelno
        for record in caplog.records
        if "did not complete" in record.message
    ]
    assert levels == [logging.WARNING, logging.DEBUG]
    assert coordinator.outstanding == {}
    assert coordinator.ems.owned == {BATTERY}
    assert len(_timers(recorder, RETRY_TIMER)) == 1
    assert recorder.cancelled >= 1
    assert "schedule action succeeded" in caplog.text
    sent_after = len(coordinator.control.calls)
    await retry(None)
    assert len(coordinator.control.calls) == sent_after


async def test_a_stop_that_fails_stays_outstanding_until_the_inverter_reports_it_off(
    recorder,
):
    coordinator = build(recorder)
    _schedule(coordinator, BATTERY, NIGHT, "on", power=-600)
    coordinator.control.outcomes = _ok(2)
    coordinator.control.switch_off_outcomes = [
        WriteRejectedError(exception_code=2),
        WriteRejectedError(exception_code=2),
    ]
    await coordinator.async_follow_schedules()
    coordinator.hass.states.set(NIGHT, "off")

    await coordinator._follow()
    retry = _timers(recorder, RETRY_TIMER)[0]["action"]
    await retry(None)

    assert coordinator.outstanding == {BATTERY: "stop"}
    assert len(coordinator.control.switch_offs) == 2
    coordinator.poller.outcomes = [cycle({BATTERY_ENABLE: 0})]
    await coordinator._async_update_data()
    await retry(None)
    assert len(coordinator.control.switch_offs) == 2
    assert coordinator.outstanding == {}
    assert coordinator._started == {}


async def test_nothing_is_ever_decided_with_control_off_or_on_an_unverified_model(
    recorder,
):
    coordinator = build(recorder)
    coordinator.control_allowed = False
    _schedule(coordinator, BATTERY, NIGHT, "on", power=-600)
    coordinator.power_targets[BATTERY] = -600

    await coordinator.async_follow_schedules()
    await coordinator._follow()

    assert coordinator.control.calls == []
    assert coordinator.outstanding == {}
    assert _timers(recorder, RETRY_TIMER) == []


async def test_releasing_stops_following_and_the_retry(recorder):
    coordinator = build(recorder)
    _schedule(coordinator, BATTERY, NIGHT, "on")
    await coordinator.async_follow_schedules()
    assert len(_timers(recorder, RETRY_TIMER)) == 1
    cancelled = recorder.cancelled

    await coordinator.async_release_power_control()
    await coordinator._follow()

    assert recorder.listeners_cancelled == 1
    assert recorder.cancelled == cancelled + 1
    assert coordinator.control.calls == []


async def test_two_functions_wanted_at_once_start_the_first_and_hold_back_the_second(
    recorder,
):
    coordinator = build(recorder)
    _schedule(coordinator, BATTERY, NIGHT, "on", power=-600)
    _schedule(coordinator, GRID, DAY, "on", power=100)
    coordinator.control.outcomes = _ok(2)

    await coordinator.async_follow_schedules()

    assert coordinator.ems.owned == {BATTERY}
    assert coordinator.outstanding == {GRID: "another_running"}


async def test_the_schedule_states_are_read_when_the_controller_runs(recorder):
    coordinator = build(recorder)
    _schedule(coordinator, BATTERY, NIGHT, "on", power=-600)
    coordinator.hass.states.by_id.pop(NIGHT)

    await coordinator.async_follow_schedules()

    assert coordinator.control.calls == []


async def test_the_first_cycle_reads_the_state_rows_of_a_scheduled_function(recorder):
    coordinator = build(recorder, contexts=set())
    _schedule(coordinator, BATTERY, NIGHT, "off")

    assert coordinator.enabled_keys == {BATTERY_ENABLE}


@pytest.mark.parametrize("context", ["battery_power_control", "battery_power_target"])
async def test_an_enabled_power_entity_gets_its_state_rows_polled(recorder, context):
    coordinator = build(recorder, contexts={context, "backup_reserve_soc"})

    assert coordinator.enabled_keys == {BATTERY_ENABLE, "backup_reserve_soc"}


async def test_the_state_rows_of_an_enabled_entity_are_found_in_the_registry_at_first(
    recorder, monkeypatch
):
    coordinator = build(recorder)
    coordinator._initial_refresh = True
    coordinator.device = type("Device", (), {"fit": None})()
    asked = {}

    def catalogue_keys(**asked_for):
        asked["catalogue"] = asked_for
        return frozenset({"backup_reserve_soc"})

    def power_keys(**asked_for):
        asked["power"] = asked_for
        return frozenset({"grid_power_target"})

    monkeypatch.setattr(coordinator_module, "enabled_entity_keys", catalogue_keys)
    monkeypatch.setattr(coordinator_module, "device_registers", lambda **_: ())
    monkeypatch.setattr(coordinator_module, "enabled_power_keys", power_keys)

    assert coordinator.enabled_keys == {"backup_reserve_soc", ENABLE_KEYS[GRID]}
    assert asked["power"]["keys"] == {
        "battery_power_control",
        "battery_power_target",
        "grid_power_control",
        "grid_power_target",
        "inverter_power_control",
        "inverter_power_target",
    }


async def test_shutdown_stops_following(recorder, monkeypatch):
    coordinator = build(recorder)
    _schedule(coordinator, BATTERY, NIGHT, "off")
    await coordinator.async_follow_schedules()

    async def framework_shutdown(_coordinator):
        return

    class Client:
        async def close(self) -> None:
            return

    coordinator.client = Client()
    monkeypatch.setattr(
        coordinator_module.DataUpdateCoordinator, "async_shutdown", framework_shutdown
    )

    await coordinator.async_shutdown()

    assert recorder.listeners_cancelled == 1


async def test_a_cycle_in_flight_delays_the_controller(recorder):
    coordinator = build(recorder)
    _schedule(coordinator, BATTERY, NIGHT, "on", power=-600)
    coordinator.control.outcomes = _ok(2)
    started, release = hold_cycle(coordinator)
    running = asyncio.create_task(coordinator._async_update_data())
    await started.wait()

    following = asyncio.create_task(coordinator.async_follow_schedules())
    await asyncio.sleep(0)
    assert coordinator.control.calls == []

    release.set()
    await asyncio.gather(running, following)

    assert len(coordinator.control.calls) == 2


OWN_ENABLES = {
    BATTERY: "q_battery_on",
    GRID: "q_grid_on",
    INVERTER: "q_inverter_on",
}
OWN_TARGETS = {
    BATTERY: "q_battery_target",
    GRID: "q_grid_target",
    INVERTER: "q_inverter_target",
}
OWN_ALTERNATE = "q_inverter_alternate"
OWN_TIMEOUT = "q_timeout"
OWN_LIMIT = "q_limit"


def _own_names(recorder):
    names = RowNames(
        timeout=OWN_TIMEOUT,
        limits=(OWN_LIMIT,),
        enables=OWN_ENABLES,
        targets=OWN_TARGETS,
        alternates={INVERTER: (OWN_ALTERNATE,)},
    )
    functions = {
        function: FakeFunctionControl(function, names=names)
        for function in PowerFunction
    }
    return build(
        recorder, functions=functions, rows=ems_rows(profile=statements(names))
    )


async def test_a_model_with_row_names_of_its_own_gets_the_exclusive_forms_and_ownership(
    recorder,
):
    coordinator = _own_names(recorder)
    coordinator.control.outcomes = _ok(2)

    await coordinator.write(key=OWN_ENABLES[INVERTER], value=1)
    await coordinator.write(key=OWN_ALTERNATE, value=1)

    first, second = coordinator.control.calls
    assert first["also"] == {OWN_ALTERNATE: 0}
    assert second["also"] == {OWN_ENABLES[INVERTER]: 0}
    assert first["inspection"].extra_words == 1
    assert coordinator.ems.owned == {INVERTER}


async def test_a_model_with_row_names_of_its_own_gets_the_timeout_check(recorder):
    coordinator = _own_names(recorder)
    coordinator.control.outcomes = _ok(2)

    await coordinator.write(key=OWN_TIMEOUT, value=90)
    await coordinator.write(key="backup_reserve_soc", value=1)

    timeout_call, other_call = coordinator.control.calls
    timeout_call["check"](90)
    with pytest.raises(EmsTimeoutError):
        timeout_call["check"](INTERVAL)
    assert other_call["check"] is None


async def test_a_model_with_row_names_of_its_own_gets_the_heartbeat_and_the_limits_read(
    recorder, caplog
):
    coordinator = _own_names(recorder)
    coordinator.control.outcomes = _ok(1)
    coordinator.control.keep_alive_outcomes = [
        7,
        LinkUnavailableError(cause=TimeoutError()),
        8,
    ]
    await coordinator.write(key=OWN_ENABLES[GRID], value=1)

    with caplog.at_level(logging.INFO, logger=coordinator_module.__name__):
        await coordinator._beat(None)
        await coordinator._beat(None)
        await coordinator._beat(None)

    assert coordinator.control.keep_alives == [OWN_TARGETS[GRID]] * 3
    assert coordinator.control.limit_reads == 2
    assert "heartbeat for q_grid_target recovered" in caplog.text
    assert coordinator.writes.beats_dropped == 1


async def test_the_alternate_form_of_a_function_reads_the_switch_on(recorder):
    coordinator = build(recorder)
    coordinator._values = {INVERTER_ALTERNATE: 1, INVERTER_ENABLE: 0}

    assert coordinator.power_running(function=INVERTER) is True


async def test_a_start_is_refused_when_only_the_alternate_form_of_another_is_set(
    recorder,
):
    coordinator = build(recorder)
    coordinator.power_targets[BATTERY] = 1
    coordinator.control.state_outcomes = [{INVERTER_ALTERNATE: 1, INVERTER_ENABLE: 0}]

    with pytest.raises(AnotherFunctionRunningError) as caught:
        await coordinator.async_power_on(function=BATTERY)

    assert caught.value.running is INVERTER
    assert coordinator.control.calls == []


async def _owned_through_the_alternate_form(recorder):
    coordinator = build(recorder)
    coordinator.control.outcomes = _ok(1)
    await coordinator.write(key=INVERTER_ALTERNATE, value=1)
    return coordinator


async def test_ownership_through_the_alternate_form_survives_polling(
    recorder,
):
    coordinator = await _owned_through_the_alternate_form(recorder)
    coordinator.poller.outcomes = [
        cycle({INVERTER_ENABLE: 0, INVERTER_ALTERNATE: 1}),
        cycle({INVERTER_ENABLE: 0, INVERTER_ALTERNATE: 0}),
    ]

    await coordinator._async_update_data()

    assert coordinator.ems.owned == {INVERTER}
    assert recorder.cancelled == 0
    assert len(_timers(recorder, HEARTBEAT_TIMER)) == 1

    await coordinator._async_update_data()

    assert coordinator.ems.owned == frozenset()
    assert recorder.cancelled == 1


async def test_a_function_owned_through_the_alternate_form_is_switched_off_on_unload(
    recorder,
):
    coordinator = await _owned_through_the_alternate_form(recorder)
    coordinator.control.outcomes = _ok(1)

    await coordinator.async_release_power_control()

    assert coordinator.control.switch_offs == [Write(key=INVERTER_ENABLE, value=0)]
    assert coordinator.ems.owned == frozenset()


async def test_every_form_of_an_owned_function_is_polled(recorder):
    coordinator = await _owned_through_the_alternate_form(recorder)

    assert coordinator.enabled_keys == {
        "backup_reserve_soc",
        "backup_reserve_soc_active",
        INVERTER_ENABLE,
        INVERTER_ALTERNATE,
    }
