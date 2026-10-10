import asyncio
import logging
from datetime import timedelta
from types import SimpleNamespace

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.saj_local import coordinator as coordinator_module
from custom_components.saj_local.coordinator import (
    LastWrite,
    SajCoordinator,
    WriteStatistics,
)
from custom_components.saj_local.errors import WriteOutcome
from custom_components.saj_local.saj.control import WriteResult
from custom_components.saj_local.saj.ems import EmsFunction, EmsOwnership
from custom_components.saj_local.saj.errors import (
    ControlDisabledError,
    EmsTimeoutError,
    LinkUnavailableError,
    WriteMismatchError,
    WriteRejectedError,
    WriteUnconfirmedError,
)
from custom_components.saj_local.saj.poller import CycleFailedError, CycleResult
from custom_components.saj_local.saj.telemetry import Telemetry

NOW = 100.4
WAKEUP = NOW + 30
INTERVAL = 60
READ_KEYS = {"backup_reserve_soc", "backup_reserve_soc_active"}


class FakeControl:
    def __init__(self) -> None:
        self.calls: list[dict] = []
        self.switch_offs: list[tuple[str, ...]] = []
        self.outcomes: list = []
        self.keep_alives: list[str] = []
        self.keep_alive_outcomes: list = []
        self.limit_reads = 0
        self.limit_outcomes: list = []
        self.hold: asyncio.Event | None = None
        self.entered = asyncio.Event()

    async def write(self, *, key, value, also=None, inspection=None, check=None):
        self.calls.append(
            {
                "key": key,
                "value": value,
                "also": also,
                "inspection": inspection,
                "check": check,
            }
        )
        self.entered.set()
        if self.hold is not None:
            await self.hold.wait()
        return self._outcome()

    async def keep_alive_read_ems(self, *, key):
        self.keep_alives.append(key)
        outcome = self.keep_alive_outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome

    async def read_ems_limits(self):
        self.limit_reads += 1
        if not self.limit_outcomes:
            return {}
        outcome = self.limit_outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome

    async def switch_off_ems(self, *, keys):
        self.switch_offs.append(tuple(keys))
        self.entered.set()
        if self.hold is not None:
            await self.hold.wait()
        return self._outcome()

    def _outcome(self):
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


class FakePoller:
    def __init__(self) -> None:
        self.link_failures = 0
        self.behaviour = None
        self.outcomes = []

    async def link_failed(self) -> float:
        self.link_failures += 1
        return WAKEUP

    async def run(self, *, enabled):
        del enabled
        if self.outcomes:
            outcome = self.outcomes.pop(0)
            if isinstance(outcome, BaseException):
                raise outcome
            return outcome
        return await self.behaviour()


class Recorder:
    def __init__(self) -> None:
        self.notified: list[frozenset[str]] = []
        self.rescheduled = 0
        self.timers: list[dict] = []
        self.cancelled = 0

    def track(self, hass, action, interval, *, name):
        self.timers.append(
            {"hass": hass, "action": action, "interval": interval, "name": name}
        )

        def cancel() -> None:
            self.cancelled += 1

        return cancel


@pytest.fixture
def recorder(monkeypatch) -> Recorder:
    recorded = Recorder()
    monkeypatch.setattr(coordinator_module, "async_track_time_interval", recorded.track)
    return recorded


def _build(recorder, *, contexts=READ_KEYS):
    coordinator = object.__new__(SajCoordinator)
    coordinator.hass = SimpleNamespace(loop=SimpleNamespace(time=lambda: NOW))
    coordinator.control = FakeControl()
    coordinator.poller = FakePoller()
    coordinator.ems = EmsOwnership()
    coordinator.writes = WriteStatistics()
    coordinator.heartbeat_interval = INTERVAL
    coordinator.assumed = {}
    coordinator.changed_keys = frozenset()
    coordinator.data = Telemetry(values={})
    coordinator.last_read = frozenset()
    coordinator.unavailable_keys = frozenset()
    coordinator.last_error = None
    coordinator._values = {}
    coordinator._cycle_lock = asyncio.Lock()
    coordinator._initial_refresh = False
    coordinator._update_task = None
    coordinator._stop_heartbeat = None
    coordinator.async_contexts = lambda: iter(set(contexts))
    coordinator.async_update_listeners = lambda: recorder.notified.append(
        coordinator.changed_keys
    )

    def reschedule() -> None:
        recorder.rescheduled += 1

    coordinator._schedule_refresh = reschedule
    return coordinator


def _hold_cycle(coordinator):
    started = asyncio.Event()
    release = asyncio.Event()

    async def behaviour():
        started.set()
        await release.wait()
        return SimpleNamespace(
            values={}, read=frozenset(), unavailable=frozenset(), next_wakeup=None
        )

    coordinator.poller.behaviour = behaviour
    return started, release


def _read(values, *, written=True):
    return WriteResult(values=values, assumed=False, written=written)


def _sent(values):
    return WriteResult(values=values, assumed=True, written=True)


async def test_a_write_hands_the_key_and_value_to_the_library(recorder):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [_read({"backup_reserve_soc": 40})]

    await coordinator.write(key="backup_reserve_soc", value=40)

    assert coordinator.control.calls == [
        {
            "key": "backup_reserve_soc",
            "value": 40,
            "also": {},
            "inspection": None,
            "check": None,
        }
    ]


async def test_a_write_waits_for_a_cycle_in_flight_and_a_cycle_waits_for_a_write(
    recorder,
):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [_read({})]
    started, release = _hold_cycle(coordinator)
    cycle = asyncio.create_task(coordinator._async_update_data())
    await started.wait()
    writing = asyncio.create_task(coordinator.write(key="backup_reserve_soc", value=1))
    await asyncio.sleep(0)
    assert coordinator.control.calls == []

    release.set()
    await asyncio.gather(cycle, writing)

    assert len(coordinator.control.calls) == 1
    coordinator.control.hold = asyncio.Event()
    coordinator.control.entered.clear()
    coordinator.control.outcomes = [_read({})]
    writing = asyncio.create_task(coordinator.write(key="backup_reserve_soc", value=2))
    await coordinator.control.entered.wait()
    later_cycle = asyncio.create_task(coordinator._async_update_data())
    await asyncio.sleep(0)
    assert coordinator._cycle_lock.locked()
    assert not later_cycle.done()
    coordinator.control.hold.set()
    release.set()
    await asyncio.gather(writing, later_cycle)


async def test_read_back_values_are_published_and_only_changed_keys_notify(
    recorder,
):
    coordinator = _build(recorder)
    coordinator._values = {"backup_reserve_soc": 30, "backup_reserve_soc_active": 30}
    coordinator.control.outcomes = [
        _read({"backup_reserve_soc": 40, "backup_reserve_soc_active": 30})
    ]

    await coordinator.write(key="backup_reserve_soc", value=40)

    assert coordinator.data == Telemetry(
        values={"backup_reserve_soc": 40, "backup_reserve_soc_active": 30}
    )
    assert recorder.notified == [frozenset({"backup_reserve_soc"})]
    assert coordinator.changed_keys == frozenset()


async def test_a_value_nobody_listens_to_is_not_published(recorder):
    coordinator = _build(recorder, contexts={"backup_reserve_soc"})
    coordinator.control.outcomes = [
        _read({"backup_reserve_soc": 40, "backup_reserve_soc_active": 40})
    ]

    await coordinator.write(key="backup_reserve_soc", value=40)

    assert coordinator.data == Telemetry(values={"backup_reserve_soc": 40})


async def test_a_write_that_changes_nothing_notifies_nobody(recorder):
    coordinator = _build(recorder)
    coordinator._values = {"backup_reserve_soc": 40}
    coordinator.control.outcomes = [_read({"backup_reserve_soc": 40}, written=False)]

    await coordinator.write(key="backup_reserve_soc", value=40)

    assert recorder.notified == []
    assert coordinator.writes == WriteStatistics()


async def test_the_polling_schedule_is_left_alone_by_a_write(recorder):
    coordinator = _build(recorder)
    coordinator.update_interval = timedelta(seconds=17)
    coordinator.control.outcomes = [_read({"backup_reserve_soc": 40})]

    await coordinator.write(key="backup_reserve_soc", value=40)

    assert coordinator.update_interval == timedelta(seconds=17)
    assert recorder.rescheduled == 0
    assert coordinator.poller.link_failures == 0


async def test_a_write_only_row_is_remembered_as_what_was_sent(recorder):
    coordinator = _build(recorder, contexts={"ems_battery_power_target"})
    coordinator.control.outcomes = [
        _sent({"ems_battery_power_target": 12.5}),
        _sent({"ems_battery_power_target": 12.5}),
    ]
    assert coordinator.assumed == {}

    await coordinator.write(key="ems_battery_power_target", value=12.5)
    await coordinator.write(key="ems_battery_power_target", value=12.5)

    assert coordinator.assumed == {"ems_battery_power_target": 12.5}
    assert recorder.notified == [frozenset({"ems_battery_power_target"})]
    assert coordinator._values == {}


async def test_a_command_is_logged_at_info_when_acknowledged(recorder, caplog):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [_sent({})]

    with caplog.at_level(logging.INFO, logger=coordinator_module.__name__):
        await coordinator.write(key="restart_inverter", value=None)

    assert "command restart_inverter acknowledged" in caplog.text
    assert recorder.notified == []


async def test_an_acknowledged_write_is_counted_and_remembered(recorder):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [_read({"backup_reserve_soc": 40})]

    await coordinator.write(key="backup_reserve_soc", value=40)

    assert coordinator.writes.acknowledged == 1
    assert coordinator.writes.last == LastWrite(
        key="backup_reserve_soc",
        outcome=WriteOutcome.ACKNOWLEDGED,
        exception_code=None,
    )


async def test_a_rule_refusal_is_not_a_write_and_is_not_logged(recorder, caplog):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [ControlDisabledError()]

    with (
        caplog.at_level(logging.DEBUG, logger=coordinator_module.__name__),
        pytest.raises(ControlDisabledError),
    ):
        await coordinator.write(key="backup_reserve_soc", value=40)

    assert coordinator.writes == WriteStatistics()
    assert coordinator.poller.link_failures == 0
    assert caplog.records == []
    assert not coordinator._cycle_lock.locked()


async def test_a_rejection_is_counted_with_its_exception_code_and_keeps_the_link(
    recorder,
):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [WriteRejectedError(exception_code=3)]

    with pytest.raises(WriteRejectedError):
        await coordinator.write(key="backup_reserve_soc", value=40)

    assert coordinator.writes.rejected == 1
    assert coordinator.writes.last == LastWrite(
        key="backup_reserve_soc", outcome=WriteOutcome.REJECTED, exception_code=3
    )
    assert coordinator.poller.link_failures == 0
    assert recorder.rescheduled == 0


async def _unconfirmed_write(recorder, caplog, *, value):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [
        WriteUnconfirmedError(cause=TimeoutError(), acknowledged=False)
    ]
    with (
        caplog.at_level(logging.WARNING, logger=coordinator_module.__name__),
        pytest.raises(WriteUnconfirmedError),
    ):
        await coordinator.write(key="backup_reserve_soc", value=value)
    return coordinator


async def test_an_unconfirmed_write_warns_and_schedules_the_backoff(recorder, caplog):
    coordinator = await _unconfirmed_write(recorder, caplog, value=40)

    assert coordinator.writes.unconfirmed == 1
    assert coordinator.writes.last.outcome is WriteOutcome.UNCONFIRMED
    assert coordinator.poller.link_failures == 1
    assert coordinator.update_interval == timedelta(seconds=31)
    assert recorder.rescheduled == 1
    assert "not confirmed" in caplog.text


async def test_a_failed_pre_read_link_schedules_the_backoff_without_counting_a_write(
    recorder,
):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [LinkUnavailableError(cause=TimeoutError())]

    with pytest.raises(LinkUnavailableError):
        await coordinator.write(key="backup_reserve_soc", value=40)

    assert coordinator.poller.link_failures == 1
    assert coordinator.writes == WriteStatistics()


async def test_an_unreachable_endpoint_without_a_link_failure_schedules_nothing(
    recorder,
):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [LinkUnavailableError()]

    with pytest.raises(LinkUnavailableError):
        await coordinator.write(key="backup_reserve_soc", value=40)

    assert coordinator.poller.link_failures == 0


async def test_a_mismatch_shows_the_read_back_warns_and_still_fails(recorder, caplog):
    coordinator = _build(recorder)
    coordinator._values = {"backup_reserve_soc": 30}
    coordinator.control.outcomes = [
        WriteMismatchError(read_back={"backup_reserve_soc": 35})
    ]

    with (
        caplog.at_level(logging.WARNING, logger=coordinator_module.__name__),
        pytest.raises(WriteMismatchError),
    ):
        await coordinator.write(key="backup_reserve_soc", value=40)

    assert coordinator.data == Telemetry(values={"backup_reserve_soc": 35})
    assert recorder.notified == [frozenset({"backup_reserve_soc"})]
    assert coordinator.writes.acknowledged == 1
    assert coordinator.writes.last.outcome is WriteOutcome.MISMATCHED
    assert "different value" in caplog.text
    assert coordinator.poller.link_failures == 0


@pytest.mark.parametrize("key", ["ems_inverter_control", "ems_battery_control"])
async def test_switching_an_ems_function_on_inspects_the_timeout_and_takes_ownership(
    recorder, key
):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [_read({key: 1})]

    await coordinator.write(key=key, value=1)

    call = coordinator.control.calls[0]
    assert call["inspection"] is not None
    assert call["inspection"].extra_words == 1
    assert coordinator.ems.owned_enable_keys == (key,)
    assert len(recorder.timers) == 1
    assert recorder.timers[0]["interval"] == timedelta(seconds=INTERVAL)
    assert recorder.timers[0]["hass"] is coordinator.hass


async def test_the_two_inverter_forms_exclude_each_other_in_the_same_write(recorder):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [_read({}), _read({})]

    await coordinator.write(key="ems_inverter_control", value=1)
    await coordinator.write(key="ems_inverter_control_with_timeout_exit", value=1)

    assert coordinator.control.calls[1]["also"] == {"ems_inverter_control": 0}
    assert coordinator.ems.owned_enable_keys == (
        "ems_inverter_control_with_timeout_exit",
    )
    assert len(recorder.timers) == 1


@pytest.mark.parametrize(
    ("device_timeout", "interval", "refused"),
    [(30, 60, True), (60, 60, True), (61, 60, False), (0xFFFF, 60, False)],
)
async def test_the_device_timeout_must_be_longer_than_the_heartbeat_to_switch_on(
    recorder, device_timeout, interval, refused
):
    coordinator = _build(recorder)
    coordinator.heartbeat_interval = interval
    coordinator.control.outcomes = [_read({})]
    await coordinator.write(key="ems_grid_control", value=1)
    inspection = coordinator.control.calls[0]["inspection"]

    if refused:
        with pytest.raises(EmsTimeoutError):
            inspection.check((device_timeout,))
    else:
        inspection.check((device_timeout,))


@pytest.mark.parametrize(
    ("value", "refused"),
    [(30, True), (60, True), (59.6, True), (61, False), (0xFFFF, False)],
)
async def test_writing_the_timeout_hands_the_library_a_check_against_the_heartbeat(
    recorder, value, *, refused
):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [_read({})]

    await coordinator.write(key="ems_timeout", value=value)

    check = coordinator.control.calls[0]["check"]
    if refused:
        with pytest.raises(EmsTimeoutError):
            check(value)
    else:
        check(value)


@pytest.mark.parametrize("key", ["backup_reserve_soc", "ems_grid_control"])
async def test_no_other_row_gets_a_value_check(recorder, key):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [_read({})]

    await coordinator.write(key=key, value=1)

    assert coordinator.control.calls[0]["check"] is None


async def test_a_refusal_by_the_library_surfaces_unchanged_for_the_timeout(recorder):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [ControlDisabledError()]

    with pytest.raises(ControlDisabledError):
        await coordinator.write(key="ems_timeout", value=5)


async def test_a_function_already_on_is_not_owned_when_nothing_was_written(recorder):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [_read({"ems_grid_control": 1}, written=False)]

    await coordinator.write(key="ems_grid_control", value=1)
    await recorder_beat(coordinator)

    assert coordinator.ems.owned == frozenset()
    assert recorder.timers == []
    assert coordinator.control.keep_alives == []
    assert len(coordinator.control.calls) == 1


async def recorder_beat(coordinator):
    await coordinator._beat(None)


async def test_switching_off_ends_ownership_even_when_nothing_needed_writing(
    recorder,
):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [_read({}), _read({}, written=False)]
    await coordinator.write(key="ems_grid_control", value=1)

    await coordinator.write(key="ems_grid_control", value=0)

    assert coordinator.ems.owned == frozenset()
    assert recorder.cancelled == 1


async def _fail_a_cycle(coordinator, caplog):
    with (
        caplog.at_level(logging.WARNING, logger=coordinator_module.__name__),
        pytest.raises(UpdateFailed),
    ):
        await coordinator._async_update_data()


async def _own_grid(coordinator):
    coordinator.control.outcomes = [_read({})]
    await coordinator.write(key="ems_grid_control", value=1)


def _cycle(values=None):
    return CycleResult(
        values=values or {},
        read=frozenset(values or {}),
        refused={},
        suspended=frozenset(),
        unavailable=frozenset(),
        next_wakeup=WAKEUP,
    )


def _failed_cycle():
    return CycleFailedError(cause=TimeoutError(), next_wakeup=WAKEUP)


async def test_a_failed_cycle_keeps_ownership_and_the_heartbeat(recorder):
    coordinator = _build(recorder)
    await _own_grid(coordinator)
    coordinator.poller.outcomes = [_failed_cycle()]

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()

    assert coordinator.ems.owned == {EmsFunction.GRID}
    assert recorder.cancelled == 0


async def test_the_next_beat_after_the_connection_returns_reads_the_target(recorder):
    coordinator = _build(recorder)
    await _own_grid(coordinator)
    timer = recorder.timers[0]["action"]
    coordinator.control.keep_alive_outcomes = [LinkUnavailableError(), 7]
    coordinator.poller.outcomes = [_failed_cycle(), _cycle()]
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()
    await timer(None)
    await coordinator._async_update_data()

    await timer(None)

    assert coordinator.control.keep_alives == ["ems_grid_power_target"] * 2
    assert coordinator.writes.beats_dropped == 1
    assert coordinator.writes.beats_sent == 1
    assert coordinator.ems.owned == {EmsFunction.GRID}


async def test_a_beat_without_an_answer_keeps_ownership_and_skips_the_tick(recorder):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [_read({}), _read({})]
    coordinator.control.keep_alive_outcomes = [
        LinkUnavailableError(cause=TimeoutError())
    ]
    await coordinator.write(key="ems_battery_control", value=1)
    await coordinator.write(key="ems_grid_control", value=1)
    last_write = coordinator.writes.last

    await coordinator._beat(None)

    assert coordinator.ems.owned == {EmsFunction.BATTERY, EmsFunction.GRID}
    assert recorder.cancelled == 0
    assert coordinator.writes.beats_dropped == 1
    assert coordinator.control.keep_alives == ["ems_battery_power_target"]
    assert coordinator.poller.link_failures == 1
    assert coordinator.writes.unconfirmed == 0
    assert coordinator.writes.last == last_write


async def test_the_owned_bits_are_cleared_on_unload_after_an_outage_that_recovered(
    recorder,
):
    coordinator = _build(recorder)
    await _own_grid(coordinator)
    coordinator.poller.outcomes = [_failed_cycle(), _cycle()]
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()
    await coordinator._async_update_data()
    coordinator.control.outcomes = [_read({})]

    await coordinator.async_release_ems()

    assert coordinator.control.switch_offs == [("ems_grid_control",)]
    assert coordinator.ems.owned == frozenset()
    assert recorder.cancelled == 1


async def test_a_cycle_that_reads_an_owned_switch_off_ends_that_function(
    recorder, caplog
):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [_read({}), _read({})]
    await coordinator.write(key="ems_battery_control", value=1)
    await coordinator.write(key="ems_grid_control", value=1)
    coordinator.poller.outcomes = [_cycle({"ems_battery_control": 0})]

    with caplog.at_level(logging.INFO, logger=coordinator_module.__name__):
        await coordinator._async_update_data()

    assert coordinator.ems.owned == {EmsFunction.GRID}
    assert recorder.cancelled == 0
    assert "battery function was found switched off" in caplog.text


async def test_the_heartbeat_ends_when_the_last_owned_function_is_found_off(
    recorder,
):
    coordinator = _build(recorder)
    await _own_grid(coordinator)
    coordinator.poller.outcomes = [_cycle({"ems_grid_control": 0})]

    await coordinator._async_update_data()

    assert coordinator.ems.owned == frozenset()
    assert recorder.cancelled == 1


@pytest.mark.parametrize(
    "values", [{}, {"ems_grid_control": 1}, {"ems_battery_control": 0}]
)
async def test_a_cycle_that_did_not_read_the_owned_switch_off_keeps_ownership(
    recorder, values
):
    coordinator = _build(recorder)
    await _own_grid(coordinator)
    coordinator.poller.outcomes = [_cycle(values)]

    await coordinator._async_update_data()

    assert coordinator.ems.owned == {EmsFunction.GRID}
    assert recorder.cancelled == 0


async def test_a_value_merged_from_an_earlier_cycle_does_not_end_ownership(recorder):
    coordinator = _build(recorder, contexts=READ_KEYS | {"ems_grid_control"})
    await _own_grid(coordinator)
    coordinator._values = {"ems_grid_control": 0}
    coordinator.poller.outcomes = [_cycle()]

    await coordinator._async_update_data()

    assert coordinator.ems.owned == {EmsFunction.GRID}


async def test_switching_a_function_off_needs_no_timeout_check_and_ends_ownership(
    recorder,
):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [_read({}), _read({})]
    await coordinator.write(key="ems_grid_control", value=1)

    await coordinator.write(key="ems_grid_control", value=0)

    assert coordinator.control.calls[1]["inspection"] is None
    assert coordinator.ems.owned == frozenset()
    assert recorder.cancelled == 1


async def test_a_function_found_on_is_not_owned_and_gets_no_heartbeat(recorder):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [_sent({"ems_grid_power_target": 5})]

    await coordinator.write(key="ems_grid_power_target", value=5)
    await coordinator._beat(None)

    assert coordinator.ems.owned == frozenset()
    assert recorder.timers == []
    assert coordinator.control.keep_alives == []
    assert len(coordinator.control.calls) == 1


async def test_each_beat_reads_the_target_of_every_owned_function_once(recorder):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [_read({}), _read({})]
    coordinator.control.keep_alive_outcomes = [12.5, -3]
    await coordinator.write(key="ems_battery_control", value=1)
    await coordinator.write(key="ems_grid_control", value=1)

    await recorder.timers[0]["action"](None)

    assert coordinator.control.keep_alives == [
        "ems_battery_power_target",
        "ems_grid_power_target",
    ]
    assert len(coordinator.control.calls) == 2
    assert coordinator.writes.beats_sent == 2
    assert coordinator.ems.owned == {EmsFunction.BATTERY, EmsFunction.GRID}


async def test_a_beat_shows_the_value_read_and_notifies_only_when_it_changed(recorder):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [_read({})]
    coordinator.control.keep_alive_outcomes = [12.5, 12.5, 0]
    await coordinator.write(key="ems_battery_control", value=1)

    await coordinator._beat(None)
    assert coordinator.assumed == {"ems_battery_power_target": 12.5}
    assert recorder.notified == [frozenset({"ems_battery_power_target"})]

    await coordinator._beat(None)
    assert len(recorder.notified) == 1

    await coordinator._beat(None)
    assert coordinator.assumed == {"ems_battery_power_target": 0}
    assert len(recorder.notified) == 2


async def test_a_beat_neither_writes_nor_touches_the_write_counters(recorder):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [_read({})]
    coordinator.control.keep_alive_outcomes = [1, WriteRejectedError(exception_code=2)]
    await coordinator.write(key="ems_battery_control", value=1)
    before = (
        coordinator.writes.acknowledged,
        coordinator.writes.rejected,
        coordinator.writes.unconfirmed,
        coordinator.writes.last,
    )

    await coordinator._beat(None)
    await coordinator._beat(None)

    assert before == (
        coordinator.writes.acknowledged,
        coordinator.writes.rejected,
        coordinator.writes.unconfirmed,
        coordinator.writes.last,
    )
    assert len(coordinator.control.calls) == 1


async def test_a_beat_waits_for_a_cycle_in_flight(recorder):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [_read({})]
    coordinator.control.keep_alive_outcomes = [1]
    await coordinator.write(key="ems_battery_control", value=1)
    started, release = _hold_cycle(coordinator)
    cycle = asyncio.create_task(coordinator._async_update_data())
    await started.wait()
    beating = asyncio.create_task(coordinator._beat(None))
    await asyncio.sleep(0)
    assert coordinator.control.keep_alives == []

    release.set()
    await asyncio.gather(cycle, beating)

    assert coordinator.control.keep_alives == ["ems_battery_power_target"]


async def test_a_dropped_beat_is_logged_counted_and_does_not_stop_the_heartbeat(
    recorder, caplog
):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [_read({})]
    coordinator.control.keep_alive_outcomes = [WriteRejectedError(exception_code=2), 1]
    await coordinator.write(key="ems_battery_control", value=1)

    with caplog.at_level(logging.DEBUG, logger=coordinator_module.__name__):
        await coordinator._beat(None)
    await coordinator._beat(None)

    assert coordinator.writes.beats_dropped == 1
    assert coordinator.writes.beats_sent == 1
    assert "heartbeat for ems_battery_power_target dropped" in caplog.text
    assert coordinator.ems.owned == {EmsFunction.BATTERY}
    assert recorder.cancelled == 0
    assert coordinator.poller.link_failures == 0


async def test_a_refused_beat_is_dropped_and_ownership_is_kept(recorder):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [_read({})]
    coordinator.control.keep_alive_outcomes = [LinkUnavailableError()]
    await coordinator.write(key="ems_battery_control", value=1)

    await coordinator._beat(None)

    assert coordinator.writes.beats_dropped == 1
    assert coordinator.ems.owned == {EmsFunction.BATTERY}
    assert coordinator.poller.link_failures == 0


async def test_a_link_failure_without_ownership_does_not_warn_about_a_heartbeat(
    recorder, caplog
):
    await _unconfirmed_write(recorder, caplog, value=1)

    assert "heartbeat" not in caplog.text


def _beating(recorder, outcomes, *keys):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [_read({}) for _ in keys]
    coordinator.control.keep_alive_outcomes = outcomes
    return coordinator


def _drop():
    return WriteRejectedError(exception_code=2)


async def _beat_logged(coordinator, caplog):
    caplog.clear()
    with caplog.at_level(logging.DEBUG, logger=coordinator_module.__name__):
        await coordinator._beat(None)
    return [(r.levelno, r.getMessage()) for r in caplog.records]


async def test_the_first_dropped_beat_warns_naming_the_target_and_the_timeout(
    recorder, caplog
):
    coordinator = _beating(recorder, [_drop()], "ems_battery_control")
    await coordinator.write(key="ems_battery_control", value=1)

    records = await _beat_logged(coordinator, caplog)

    ((level, message),) = records
    assert level == logging.WARNING
    assert "ems_battery_power_target" in message
    assert "EMS timeout" in message


async def test_further_consecutive_drops_stay_at_debug(recorder, caplog):
    coordinator = _beating(recorder, [_drop(), _drop()], "ems_battery_control")
    await coordinator.write(key="ems_battery_control", value=1)
    await _beat_logged(coordinator, caplog)

    records = await _beat_logged(coordinator, caplog)

    assert [level for level, _ in records] == [logging.DEBUG]


async def test_a_success_after_a_drop_logs_one_recovery_and_a_later_drop_warns_again(
    recorder, caplog
):
    coordinator = _beating(recorder, [_drop(), 1, 1, _drop()], "ems_battery_control")
    await coordinator.write(key="ems_battery_control", value=1)
    await _beat_logged(coordinator, caplog)

    recovery = await _beat_logged(coordinator, caplog)
    steady = await _beat_logged(coordinator, caplog)
    again = await _beat_logged(coordinator, caplog)

    assert [level for level, _ in recovery] == [logging.INFO]
    assert "recovered" in recovery[0][1]
    assert steady == []
    assert [level for level, _ in again] == [logging.WARNING]


async def test_two_functions_are_tracked_independently(recorder, caplog):
    coordinator = _beating(
        recorder,
        [_drop(), _drop(), _drop(), 1],
        "ems_battery_control",
        "ems_grid_control",
    )
    await coordinator.write(key="ems_battery_control", value=1)
    await coordinator.write(key="ems_grid_control", value=1)

    first = await _beat_logged(coordinator, caplog)
    second = await _beat_logged(coordinator, caplog)

    assert [level for level, _ in first] == [logging.WARNING, logging.WARNING]
    assert [level for level, _ in second] == [logging.DEBUG, logging.INFO]


async def test_releasing_clears_only_the_owned_enable_bits_in_one_write(
    recorder, caplog
):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [_read({}), _read({}), _read({})]
    await coordinator.write(key="ems_battery_control", value=1)
    await coordinator.write(key="ems_grid_control", value=1)

    with caplog.at_level(logging.INFO, logger=coordinator_module.__name__):
        await coordinator.async_release_ems()

    assert coordinator.control.switch_offs == [
        ("ems_battery_control", "ems_grid_control")
    ]
    assert len(coordinator.control.calls) == 2
    assert coordinator.ems.owned == frozenset()
    assert recorder.cancelled == 1
    assert "EMS enable bits cleared" in caplog.text


async def test_releasing_with_nothing_owned_sends_nothing(recorder):
    coordinator = _build(recorder)

    await coordinator.async_release_ems()

    assert coordinator.control.calls == []


async def test_a_refused_release_warns_naming_the_timeout_and_still_lets_go(
    recorder, caplog
):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [_read({}), WriteRejectedError(exception_code=2)]
    await coordinator.write(key="ems_battery_control", value=1)

    with caplog.at_level(logging.WARNING, logger=coordinator_module.__name__):
        await coordinator.async_release_ems()

    assert "EMS timeout" in caplog.text
    assert coordinator.ems.owned == frozenset()
    assert recorder.cancelled == 1


async def test_a_release_that_takes_too_long_is_abandoned(
    recorder, caplog, monkeypatch
):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [_read({}), _read({})]
    await coordinator.write(key="ems_battery_control", value=1)
    coordinator.control.hold = asyncio.Event()
    monkeypatch.setattr(coordinator_module, "EMS_RELEASE_TIMEOUT", 0)

    with caplog.at_level(logging.WARNING, logger=coordinator_module.__name__):
        await coordinator.async_release_ems()

    assert "TimeoutError" in caplog.text
    assert coordinator.ems.owned == frozenset()
    assert not coordinator._cycle_lock.locked()


async def test_a_release_waits_for_a_cycle_longer_than_its_limit(recorder, monkeypatch):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [_read({}), _read({})]
    await coordinator.write(key="ems_battery_control", value=1)
    monkeypatch.setattr(coordinator_module, "EMS_RELEASE_TIMEOUT", 0.01)
    started, finish = _hold_cycle(coordinator)
    cycle = asyncio.create_task(coordinator._async_update_data())
    await started.wait()
    releasing = asyncio.create_task(coordinator.async_release_ems())
    await asyncio.sleep(0.05)
    assert coordinator.control.switch_offs == []
    assert not releasing.done()

    finish.set()
    await asyncio.gather(cycle, releasing)

    assert coordinator.control.switch_offs == [("ems_battery_control",)]
    assert coordinator.ems.owned == frozenset()


async def test_a_release_whose_own_requests_exceed_the_limit_is_abandoned(
    recorder, caplog, monkeypatch
):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [_read({})]
    await coordinator.write(key="ems_battery_control", value=1)
    coordinator.control.hold = asyncio.Event()
    coordinator.control.entered.clear()
    monkeypatch.setattr(coordinator_module, "EMS_RELEASE_TIMEOUT", 0.01)

    with caplog.at_level(logging.WARNING, logger=coordinator_module.__name__):
        await coordinator.async_release_ems()

    assert coordinator.control.switch_offs == [("ems_battery_control",)]
    assert "EMS timeout" in caplog.text
    assert coordinator.ems.owned == frozenset()
    assert not coordinator._cycle_lock.locked()


async def test_shutdown_stops_the_heartbeat(recorder, monkeypatch):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [_read({})]
    await coordinator.write(key="ems_battery_control", value=1)

    async def framework_shutdown(_coordinator):
        return

    async def close() -> None:
        return

    coordinator.client = SimpleNamespace(close=close)
    monkeypatch.setattr(
        coordinator_module.DataUpdateCoordinator, "async_shutdown", framework_shutdown
    )

    await coordinator.async_shutdown()

    assert recorder.cancelled == 1


async def test_a_beat_reads_the_target_then_the_limits_and_shows_them(recorder):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [_read({})]
    coordinator.control.keep_alive_outcomes = [12.5]
    coordinator.control.limit_outcomes = [
        {"ems_pv_power_limit": 80, "ems_battery_charge_current_limit": 25.5}
    ]
    await coordinator.write(key="ems_battery_control", value=1)

    await coordinator._beat(None)

    assert coordinator.control.keep_alives == ["ems_battery_power_target"]
    assert coordinator.control.limit_reads == 1
    assert coordinator.assumed == {
        "ems_battery_power_target": 12.5,
        "ems_pv_power_limit": 80,
        "ems_battery_charge_current_limit": 25.5,
    }


async def test_a_limit_changed_by_a_beat_is_announced_once_to_its_entity(recorder):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [_read({})]
    coordinator.control.keep_alive_outcomes = [1, 1, 1]
    coordinator.control.limit_outcomes = [
        {"ems_pv_power_limit": 80},
        {"ems_pv_power_limit": 80},
        {"ems_pv_power_limit": None},
    ]
    await coordinator.write(key="ems_battery_control", value=1)

    await coordinator._beat(None)
    await coordinator._beat(None)
    await coordinator._beat(None)

    assert recorder.notified == [
        frozenset({"ems_battery_power_target"}),
        frozenset({"ems_pv_power_limit"}),
        frozenset({"ems_pv_power_limit"}),
    ]
    assert coordinator.assumed["ems_pv_power_limit"] is None


async def test_nothing_is_read_when_no_function_is_owned(recorder):
    coordinator = _build(recorder)

    await coordinator._beat(None)

    assert coordinator.control.keep_alives == []
    assert coordinator.control.limit_reads == 0


async def test_a_limits_refusal_is_no_dropped_beat_and_no_warning(recorder, caplog):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [_read({})]
    coordinator.control.keep_alive_outcomes = [1]
    coordinator.control.limit_outcomes = [LinkUnavailableError()]
    await coordinator.write(key="ems_battery_control", value=1)

    with caplog.at_level(logging.DEBUG, logger=coordinator_module.__name__):
        await coordinator._beat(None)

    assert coordinator.writes.beats_sent == 1
    assert coordinator.writes.beats_dropped == 0
    assert coordinator.poller.link_failures == 0
    assert [r for r in caplog.records if r.levelno >= logging.WARNING] == []
    assert "limits were not read" in caplog.text


async def test_limits_nobody_answers_run_the_link_failed_handling(recorder):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [_read({})]
    coordinator.control.keep_alive_outcomes = [1]
    coordinator.control.limit_outcomes = [LinkUnavailableError(cause=TimeoutError())]
    await coordinator.write(key="ems_battery_control", value=1)

    await coordinator._beat(None)

    assert coordinator.poller.link_failures == 1
    assert recorder.rescheduled == 1
    assert coordinator.writes.beats_dropped == 0
    assert coordinator.ems.owned == {EmsFunction.BATTERY}


async def test_a_target_link_failure_skips_the_limits(recorder):
    coordinator = _build(recorder)
    coordinator.control.outcomes = [_read({})]
    coordinator.control.keep_alive_outcomes = [
        LinkUnavailableError(cause=TimeoutError())
    ]
    await coordinator.write(key="ems_battery_control", value=1)

    await coordinator._beat(None)

    assert coordinator.control.limit_reads == 0
    assert coordinator.poller.link_failures == 1
