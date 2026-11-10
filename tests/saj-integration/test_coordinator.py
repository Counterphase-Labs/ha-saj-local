import asyncio
import logging
from contextlib import contextmanager
from datetime import timedelta
from types import SimpleNamespace
from typing import TYPE_CHECKING, ClassVar

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.saj_local import coordinator as coordinator_module
from custom_components.saj_local.const import DOMAIN
from custom_components.saj_local.coordinator import (
    Installation,
    SajCoordinator,
    power_control_store,
    wakeup_delay,
)
from custom_components.saj_local.errors import Translation
from custom_components.saj_local.saj.budget import BUDGET_PER_MINUTE
from custom_components.saj_local.saj.client import (
    ConnectionReason,
    ModbusError,
    ModbusErrorMessage,
)
from custom_components.saj_local.saj.device import Device
from custom_components.saj_local.saj.ems import EmsOwnership
from custom_components.saj_local.saj.errors import (
    ModelMismatchError,
    UnknownModelError,
    UnsupportedDeviceError,
)
from custom_components.saj_local.saj.faults import FaultWatch
from custom_components.saj_local.saj.models import ems_rows
from custom_components.saj_local.saj.models.hs3 import PROFILE as HS3
from custom_components.saj_local.saj.poller import (
    CadencePlan,
    CycleFailedError,
    CycleResult,
    IdentityChangedError,
)
from custom_components.saj_local.saj.schedule import Cadence
from custom_components.saj_local.saj.telemetry import Telemetry
from tests.coordinators import (
    ROOF_ENTRY,
    ROOF_LABEL,
    FakeBatteryEstimates,
    FakeStore,
    coordinator_logger,
    statements,
)
from tests.issues import IssueRecorder

if TYPE_CHECKING:
    from collections.abc import Iterator
from tests.profiles import profile

SUPPORTED_KEYS = frozenset(
    {"pv_power", "grid_power", "battery_soc", "pv_energy_today", "backup_reserve_soc"}
)
PROFILE = profile(
    base=HS3,
    key="alpha",
    device_types={0x1610},
    keys=SUPPORTED_KEYS,
    hand_verified=True,
)
OTHER_PROFILE = profile(
    base=HS3, key="beta", device_types={0x0010}, keys=(), hand_verified=False
)
SELECTION = "automatic"
DEVICE = Device("TEST-001", 0x1610, 12000, PROFILE, detected=True)
NOW = 100.4


def _result(
    values: dict | None = None,
    *,
    refused: dict | None = None,
    unavailable: set | None = None,
    suspended: set | None = None,
    next_wakeup: float | None = NOW + 10,
) -> CycleResult:
    values = values or {}
    return CycleResult(
        values=values,
        read=frozenset(values),
        refused=refused or {},
        suspended=frozenset(suspended or ()),
        unavailable=frozenset(unavailable or ()),
        next_wakeup=next_wakeup,
    )


class FakeClient:
    def __init__(self) -> None:
        self.closed = False
        self.unremembering = False
        self.close_reasons: list[ConnectionReason] = []

    async def close(self, *, reason: ConnectionReason) -> None:
        self.closed = True
        self.close_reasons.append(reason)

    @contextmanager
    def unremembered(self) -> Iterator[None]:
        self.unremembering = True
        try:
            yield
        finally:
            self.unremembering = False


class FakeControl:
    pass


class FakePoller:
    def __init__(self) -> None:
        self.outcomes: list = []
        self.enabled_seen: list[set[str]] = []
        self.behaviour = None
        self.plans: tuple[CadencePlan, ...] = ()
        self.load = 0.0

    async def run(self, *, enabled):
        self.enabled_seen.append(set(enabled))
        if self.behaviour is not None:
            return await self.behaviour()
        outcome = self.outcomes.pop(0) if self.outcomes else _result()
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome

    def cadence_plans(self):
        return self.plans

    def planned_load(self):
        return self.load


@pytest.fixture(autouse=True)
def every_supported_entity_is_enabled(monkeypatch):
    monkeypatch.setattr(
        coordinator_module,
        "enabled_entity_keys",
        lambda **asked: frozenset(register.key for register in asked["registers"]),
    )
    monkeypatch.setattr(
        coordinator_module, "enabled_power_keys", lambda **_: frozenset()
    )
    monkeypatch.setattr(
        coordinator_module, "power_control_store", lambda **_: FakeStore()
    )
    monkeypatch.setattr(coordinator_module, "BatteryEstimates", FakeBatteryEstimates)


@pytest.fixture(autouse=True)
def issues(monkeypatch) -> IssueRecorder:
    recorder = IssueRecorder()
    recorder.opened = frozenset()
    recorder.install(
        monkeypatch,
        module=coordinator_module,
        names=(
            "check_unreachable",
            "clear_model_issues",
            "clear_unreachable",
            "raise_model_issue",
            "sync_refusals",
        ),
    )
    monkeypatch.setattr(
        coordinator_module, "open_refusals", lambda **_: recorder.opened
    )
    return recorder


def _run_task(coro, *, name):
    assert name
    return asyncio.create_task(coro)


async def _no_refresh() -> None:
    return None


def _coordinator(
    *, contexts: set[str] | None = None
) -> tuple[SajCoordinator, FakeClient, FakePoller]:
    client = FakeClient()
    poller = FakePoller()
    coordinator = object.__new__(SajCoordinator)
    coordinator.client = client
    coordinator.device = DEVICE
    coordinator.model_selection = SELECTION
    coordinator.entry_id = "logical-installation"
    coordinator._entry = ROOF_ENTRY
    coordinator._log = coordinator_logger()
    coordinator.guard = object()
    coordinator._faults = FaultWatch(fault_map=DEVICE.profile.faults)
    coordinator._packs_on = frozenset()
    coordinator.last_error = None
    coordinator.last_read = frozenset()
    coordinator.unavailable_keys = frozenset()
    coordinator.poller = poller
    coordinator.hass = SimpleNamespace(
        loop=SimpleNamespace(time=lambda: NOW),
        async_create_task=_run_task,
    )
    coordinator.async_request_refresh = _no_refresh
    coordinator._values = {}
    coordinator.battery = FakeBatteryEstimates()
    coordinator._cycle_lock = asyncio.Lock()
    coordinator._initial_refresh = True
    coordinator._update_task = None
    coordinator._stop_heartbeat = None
    coordinator.ems = EmsOwnership()
    coordinator.ems_rows = ems_rows(profile=statements())
    coordinator.power_controls = {}
    coordinator.power_offered = ()
    coordinator.schedules = ()
    coordinator.assumed = {}
    coordinator.remembered_modes = {}
    coordinator.outstanding = {}
    coordinator._closed = False
    coordinator._stopping = set()
    coordinator.schedule_entities = {}
    coordinator._schedule_trackers = []
    coordinator._stop_retry = None
    active_contexts = contexts or set()
    coordinator.async_contexts = lambda: iter(active_contexts)
    return coordinator, client, poller


def _failure(cause: Exception, *, next_wakeup: float = NOW + 20) -> CycleFailedError:
    return CycleFailedError(cause=cause, next_wakeup=next_wakeup)


def _replace_framework_shutdown(monkeypatch) -> None:
    async def framework_shutdown(_coordinator):
        return

    monkeypatch.setattr(
        coordinator_module.DataUpdateCoordinator, "async_shutdown", framework_shutdown
    )


async def _start_blocked_cycle(coordinator, poller):
    started = asyncio.Event()
    wait_forever = asyncio.Event()

    async def behaviour():
        started.set()
        await wait_forever.wait()

    poller.behaviour = behaviour
    task = asyncio.create_task(coordinator._async_update_data())
    await started.wait()
    return task


class RecordingSchedule:
    instances: ClassVar[list] = []

    def __init__(self, *, cadences, origin) -> None:
        self.cadences = tuple(cadences)
        self.origin = origin
        self.instances.append(self)


class RecordingPoller(FakePoller):
    instances: ClassVar[list] = []

    def __init__(self, *, target, tracking, services, enabled, label) -> None:
        super().__init__()
        self.label = label
        self.enabled = enabled
        self.target = target
        self.tracking = tracking
        self.services = services
        self.instances.append(self)


def _entry(*, options=None, subentries=()) -> SimpleNamespace:
    return SimpleNamespace(
        entry_id="logical-installation",
        title=ROOF_ENTRY.title,
        unique_id=ROOF_ENTRY.unique_id,
        options={"scan_interval": 47} if options is None else options,
        data={"model": "alpha"},
        subentries={
            f"id-{index}": SimpleNamespace(
                subentry_id=f"id-{index}", subentry_type=kind, data=data
            )
            for index, (kind, data) in enumerate(subentries)
        },
    )


def _construct(monkeypatch, entry, *, poller_class=RecordingPoller):
    RecordingSchedule.instances.clear()
    RecordingPoller.instances.clear()
    captured = {}

    def framework_init(coordinator, *, hass, logger, name) -> None:
        coordinator.hass = hass
        captured.update(hass=hass, name=name)

    def build(*, default_interval, groups, supported):
        captured.update(
            default_interval=default_interval,
            groups=list(groups),
            supported=supported,
        )
        return ("built", default_interval)

    monkeypatch.setattr(
        coordinator_module.DataUpdateCoordinator, "__init__", framework_init
    )
    monkeypatch.setattr(coordinator_module, "build_cadences", build)
    monkeypatch.setattr(coordinator_module, "Schedule", RecordingSchedule)
    monkeypatch.setattr(coordinator_module, "Poller", poller_class)
    hass = SimpleNamespace(loop=SimpleNamespace(time=lambda: NOW))
    client = FakeClient()
    guard = object()
    captured["guard"] = guard
    captured["control"] = FakeControl()
    installation = Installation(
        client=client, device=DEVICE, guard=guard, control=captured["control"]
    )
    coordinator = SajCoordinator(hass, installation, entry)
    return coordinator, client, captured


def test_constructor_builds_the_poller_from_the_default_interval_and_polling_groups(
    monkeypatch,
):
    entry = _entry(
        subentries=[
            ("polling_group", {"scan_interval": 10, "keys": ["pv_power"]}),
            ("something_else", {"scan_interval": 5, "keys": ["grid_power"]}),
            ("polling_group", {"scan_interval": 120, "keys": ["battery_soc"]}),
        ]
    )

    coordinator, client, captured = _construct(monkeypatch, entry)

    assert captured["default_interval"] == 47
    assert captured["groups"] == [
        Cadence(interval=10, keys=frozenset({"pv_power"})),
        Cadence(interval=120, keys=frozenset({"battery_soc"})),
    ]
    assert captured["supported"] == SUPPORTED_KEYS
    assert captured["name"] == ROOF_LABEL
    assert coordinator.poller.label == ROOF_LABEL
    poller = coordinator.poller
    assert poller.target.client is client
    assert poller.target.device is DEVICE
    assert poller.target.selection == "alpha"
    assert poller.tracking.schedule.cadences == ("built", 47)
    assert poller.tracking.schedule.origin == NOW
    assert poller.tracking.guard is captured["guard"]
    assert poller.services.clock() == NOW
    assert coordinator.entry_id == "logical-installation"
    assert coordinator.last_error is None
    assert coordinator._initial_refresh


def test_the_poller_is_told_the_installations_enabled_keys_at_load(monkeypatch):
    asked = {}

    def enabled_in_registry(*, hass, entry_id, registers):
        asked.update(entry_id=entry_id, keys={r.key for r in registers})
        return frozenset({"pv_power"})

    monkeypatch.setattr(coordinator_module, "enabled_entity_keys", enabled_in_registry)

    coordinator, _, _ = _construct(monkeypatch, _entry())

    assert coordinator.poller.enabled == frozenset({"pv_power"})
    assert asked == {"entry_id": "logical-installation", "keys": set(SUPPORTED_KEYS)}


def test_constructor_uses_the_default_interval_when_none_was_saved(monkeypatch):
    _, _, captured = _construct(monkeypatch, _entry(options={}))

    assert captured["default_interval"] == coordinator_module.DEFAULT_SCAN_INTERVAL


def test_constructor_logs_each_cadence_plan_at_debug(monkeypatch, caplog):
    class PlannedPoller(RecordingPoller):
        def __init__(self, **kwargs) -> None:
            super().__init__(**kwargs)
            self.plans = (
                CadencePlan(
                    interval=60,
                    keys=frozenset({"a", "b"}),
                    ranges=((0x4004, 1), (0x40A5, 3)),
                    default=True,
                ),
                CadencePlan(
                    interval=10,
                    keys=frozenset({"c"}),
                    ranges=((0x406F, 1),),
                    default=False,
                ),
            )

    with caplog.at_level(logging.DEBUG):
        _construct(monkeypatch, _entry(), poller_class=PlannedPoller)

    messages = [record.getMessage() for record in caplog.records]
    assert any("every 60 s" in m and "default" in m for m in messages)
    assert any("every 10 s" in m and "default" not in m for m in messages)
    assert any("0x4004+1" in m and "0x40a5+3" in m for m in messages)


@pytest.mark.parametrize(
    ("load", "warned"),
    [(0.0, False), (BUDGET_PER_MINUTE, False), (BUDGET_PER_MINUTE + 0.1, True)],
)
def test_planned_load_above_the_budget_warns_once_at_load(
    monkeypatch, caplog, load, *, warned
):
    class LoadedPoller(RecordingPoller):
        def __init__(self, **kwargs) -> None:
            super().__init__(**kwargs)
            self.load = load

    with caplog.at_level(logging.WARNING):
        _construct(monkeypatch, _entry(), poller_class=LoadedPoller)

    assert len([r for r in caplog.records if r.levelno == logging.WARNING]) == int(
        warned
    )


@pytest.mark.parametrize(
    ("target", "now"),
    [
        (105.2, 100.9),
        (105.0, 100.0),
        (101.0, 100.99),
        (100.0, 100.5),
        (50.0, 100.5),
        (1000.0001, 3.5),
    ],
)
def test_a_wakeup_never_lands_before_the_target_and_is_never_zero(target, now):
    delay = wakeup_delay(target=target, now=now)

    assert delay >= timedelta(seconds=1)
    assert int(now) + delay.total_seconds() >= target


def test_a_wakeup_is_the_closest_whole_second_after_the_target():
    assert wakeup_delay(target=110.2, now=100.9) == timedelta(seconds=11)
    assert wakeup_delay(target=110.0, now=100.9) == timedelta(seconds=10)


async def test_first_callback_reads_the_entities_enabled_in_the_registry(monkeypatch):
    coordinator, _client, poller = _coordinator()
    asked = {}

    def enabled_in_registry(*, hass, entry_id, registers):
        asked.update(hass=hass, entry_id=entry_id, keys={r.key for r in registers})
        return frozenset({"pv_power", "backup_reserve_soc"})

    monkeypatch.setattr(coordinator_module, "enabled_entity_keys", enabled_in_registry)

    await coordinator._async_update_data()

    assert poller.enabled_seen == [{"pv_power", "backup_reserve_soc"}]
    assert asked == {
        "hass": coordinator.hass,
        "entry_id": "logical-installation",
        "keys": SUPPORTED_KEYS,
    }
    assert coordinator.enabled_keys == set()


async def test_later_callbacks_read_only_sensors_with_active_listeners():
    coordinator, _client, poller = _coordinator(contexts={"pv_power", "grid_power"})
    await coordinator._async_update_data()

    await coordinator._async_update_data()

    assert poller.enabled_seen[1] == {"pv_power", "grid_power"}
    assert coordinator.enabled_keys == {"pv_power", "grid_power"}


async def test_the_result_is_published_and_merged_with_earlier_values():
    coordinator, _client, poller = _coordinator(
        contexts={"pv_power", "grid_power", "battery_soc"}
    )
    poller.outcomes = [
        _result({"pv_power": 1, "grid_power": 2, "battery_soc": 3}),
        _result({"pv_power": 10}),
    ]

    first = await coordinator._async_update_data()
    second = await coordinator._async_update_data()

    assert first == Telemetry(values={"pv_power": 1, "grid_power": 2, "battery_soc": 3})
    assert second == Telemetry(
        values={"pv_power": 10, "grid_power": 2, "battery_soc": 3}
    )
    assert coordinator.last_read == {"pv_power"}


async def test_a_sensor_without_a_listener_leaves_the_snapshot():
    coordinator, _client, poller = _coordinator(contexts={"pv_power", "grid_power"})
    poller.outcomes = [
        _result({"pv_power": 1, "grid_power": 2}),
        _result({"pv_power": 5}),
    ]
    await coordinator._async_update_data()
    coordinator.async_contexts = lambda: iter({"pv_power"})

    snapshot = await coordinator._async_update_data()

    assert snapshot == Telemetry(values={"pv_power": 5})


async def test_unavailable_sensors_are_removed_from_the_snapshot_and_reported():
    coordinator, _client, poller = _coordinator(contexts={"pv_power", "grid_power"})
    poller.outcomes = [
        _result({"pv_power": 1, "grid_power": 2}),
        _result({"pv_power": 5}, unavailable={"grid_power"}),
    ]
    await coordinator._async_update_data()

    snapshot = await coordinator._async_update_data()

    assert snapshot == Telemetry(values={"pv_power": 5})
    assert coordinator.unavailable_keys == {"grid_power"}


async def test_the_battery_estimates_join_the_snapshot_and_count_as_read():
    coordinator, _client, poller = _coordinator(
        contexts={"battery_power", "battery_time_to_empty"}
    )
    coordinator._initial_refresh = False
    coordinator.battery.estimates = {"battery_time_to_empty": 90}
    poller.outcomes = [_result({"battery_power": 1500})]

    snapshot = await coordinator._async_update_data()

    assert snapshot == Telemetry(
        values={"battery_power": 1500, "battery_time_to_empty": 90}
    )
    assert coordinator.last_read == {"battery_power", "battery_time_to_empty"}
    (update,) = coordinator.battery.updates
    assert update["read"] == {"battery_power"}
    assert update["values"] == {"battery_power": 1500}
    assert update["enabled"] == {"battery_power", "battery_time_to_empty"}


async def test_the_stored_state_is_the_power_state_and_then_the_battery_totals():
    coordinator, _client, _poller = _coordinator()
    loaded = []

    async def load_power_state() -> None:
        loaded.append("power")

    coordinator.async_load_power_state = load_power_state

    await coordinator.async_load_stored_state()

    assert loaded == ["power"]
    assert coordinator.battery.loads == 1


async def test_the_battery_totals_are_offered_for_saving_after_every_poll():
    coordinator, _client, poller = _coordinator(contexts={"pv_power"})
    poller.outcomes = [_result({"pv_power": 1}), _result({"pv_power": 2})]

    await coordinator._async_update_data()
    await coordinator._async_update_data()

    assert coordinator.battery.saves == [False, False]


async def test_the_battery_totals_are_saved_at_once_when_the_coordinator_shuts_down(
    monkeypatch,
):
    coordinator, _client, _poller = _coordinator()
    _replace_framework_shutdown(monkeypatch)

    await coordinator.async_shutdown()

    assert coordinator.battery.saves == [True]


async def test_a_failed_cycle_never_lets_old_values_mix_with_new_ones():
    coordinator, _client, poller = _coordinator(contexts={"pv_power", "grid_power"})
    poller.outcomes = [
        _result({"pv_power": 1, "grid_power": 2}),
        _failure(TimeoutError()),
        _result({"pv_power": 7}),
    ]
    await coordinator._async_update_data()
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()
    assert coordinator.last_read == frozenset()

    snapshot = await coordinator._async_update_data()

    assert snapshot == Telemetry(values={"pv_power": 7})


@pytest.mark.parametrize(
    ("next_wakeup", "expected"),
    [
        (NOW + 10, timedelta(seconds=11)),
        (NOW + 59.9, timedelta(seconds=61)),
        (None, None),
    ],
)
async def test_the_next_wakeup_follows_the_result_and_never_precedes_it(
    next_wakeup, expected
):
    coordinator, _client, poller = _coordinator()
    poller.outcomes = [_result(next_wakeup=next_wakeup)]

    await coordinator._async_update_data()

    assert coordinator.update_interval == expected
    if expected is not None:
        assert int(NOW) + coordinator.update_interval.total_seconds() >= next_wakeup


async def test_a_wakeup_that_is_already_due_is_still_a_scheduled_wakeup():
    coordinator, _client, poller = _coordinator()
    poller.outcomes = [_result(next_wakeup=NOW - 30)]

    await coordinator._async_update_data()

    assert coordinator.update_interval == timedelta(seconds=1)


MODEL_FAILURES = [
    UnsupportedDeviceError(0x1234),
    ModelMismatchError(selected=PROFILE, detected=OTHER_PROFILE),
    UnknownModelError("gamma"),
]


@pytest.mark.parametrize(
    "cause",
    [
        TimeoutError("private timeout details"),
        OSError("private host socket details"),
        ValueError("malformed telemetry"),
        ModbusError(ModbusErrorMessage.MISMATCHED_HEADER),
        *MODEL_FAILURES,
    ],
)
async def test_a_failed_cycle_becomes_a_translated_update_failure(monkeypatch, cause):
    coordinator, _client, poller = _coordinator()
    poller.outcomes = [_failure(cause, next_wakeup=NOW + 35)]

    def translate(error):
        assert error is cause
        return Translation(key="stubbed", placeholders={"detail": "value"})

    monkeypatch.setattr(coordinator_module, "translate_error", translate)
    with pytest.raises(UpdateFailed) as caught:
        await coordinator._async_update_data()

    assert caught.value.translation_domain == DOMAIN
    assert caught.value.translation_key == "stubbed"
    assert caught.value.translation_placeholders == {"detail": "value"}
    assert caught.value.__cause__ is cause
    assert coordinator.update_interval == timedelta(seconds=36)


async def _last_error_after_failure(cause):
    coordinator, _client, poller = _coordinator()
    poller.outcomes = [_failure(cause)]
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()
    return coordinator.last_error


@pytest.mark.parametrize("cause", MODEL_FAILURES)
async def test_model_failures_record_their_own_message_in_last_error(cause):
    assert await _last_error_after_failure(cause) == {
        "type": type(cause).__name__,
        "reason": str(cause),
        "exception_code": None,
    }


@pytest.mark.parametrize(
    "cause", [OSError("private host socket details"), ValueError("private")]
)
async def test_other_failures_record_a_generic_reason(cause):
    last_error = await _last_error_after_failure(cause)

    assert last_error["reason"] == "Device read failed"


async def test_modbus_failure_records_exception_code():
    cause = ModbusError(ModbusErrorMessage.EXCEPTION_RESPONSE, exception_code=2)

    last_error = await _last_error_after_failure(cause)

    assert last_error["exception_code"] == 2


async def test_identity_change_has_specific_translation_and_no_serial_in_last_error():
    coordinator, _client, poller = _coordinator()
    poller.outcomes = [_failure(IdentityChangedError(serial="OTHER"))]

    with pytest.raises(UpdateFailed) as caught:
        await coordinator._async_update_data()

    assert caught.value.translation_domain == DOMAIN
    assert caught.value.translation_key == "identity_mismatch"
    assert coordinator.last_error["type"] == "IdentityChangedError"
    assert "OTHER-SERIAL" not in str(coordinator.last_error)


async def test_identical_failures_log_only_on_state_transition(caplog):
    coordinator, _client, poller = _coordinator()
    poller.outcomes = [
        _failure(ModbusError("Modbus exception response")),
        _failure(ModbusError("Modbus exception response")),
    ]

    with caplog.at_level(logging.WARNING):
        for _ in range(2):
            with pytest.raises(UpdateFailed):
                await coordinator._async_update_data()

    assert caplog.text.count(f"{ROOF_LABEL}: Update failed") == 1


async def test_recovery_is_logged_once_and_clears_the_last_error(caplog):
    coordinator, _client, poller = _coordinator()
    coordinator.last_error = {"type": "ModbusError", "exception_code": 6}
    poller.outcomes = [_result(), _result()]

    with caplog.at_level(logging.INFO):
        await coordinator._async_update_data()
        await coordinator._async_update_data()

    assert caplog.text.count(f"{ROOF_LABEL}: Connection restored") == 1
    assert coordinator.last_error is None


async def test_callback_lock_serializes_overlapping_cycles():
    coordinator, _client, poller = _coordinator()
    first_started = asyncio.Event()
    release_first = asyncio.Event()
    active = 0
    maximum = 0

    async def behaviour():
        nonlocal active, maximum
        active += 1
        maximum = max(maximum, active)
        if active == 1:
            first_started.set()
            await release_first.wait()
        active -= 1
        return _result()

    poller.behaviour = behaviour
    first = asyncio.create_task(coordinator._async_update_data())
    await first_started.wait()
    second = asyncio.create_task(coordinator._async_update_data())
    await asyncio.sleep(0)
    assert active == 1
    release_first.set()
    await asyncio.gather(first, second)

    assert maximum == 1


async def test_validation_session_hands_out_the_installation_client_under_lock():
    coordinator, client, _poller = _coordinator()

    async with coordinator.async_validation_session() as shared:
        assert shared is client
        assert coordinator._cycle_lock.locked()

    assert not coordinator._cycle_lock.locked()


@pytest.mark.parametrize("fails", [False, True])
async def test_validation_session_closes_the_client_when_it_ends(fails):
    coordinator, client, _poller = _coordinator()
    lock_held_at_close = None

    async def close(*, reason: ConnectionReason) -> None:
        nonlocal lock_held_at_close
        lock_held_at_close = coordinator._cycle_lock.locked()
        client.closed = True
        client.close_reasons.append(reason)

    client.close = close
    lock_held_at_refresh = []

    async def request_refresh() -> None:
        lock_held_at_refresh.append(coordinator._cycle_lock.locked())

    coordinator.async_request_refresh = request_refresh

    async def validate() -> None:
        async with coordinator.async_validation_session():
            assert not client.closed
            assert client.unremembering
            assert not lock_held_at_refresh
            if fails:
                failure_message = "validation failed"
                raise ValueError(failure_message)

    if fails:
        with pytest.raises(ValueError, match="validation failed"):
            await validate()
    else:
        await validate()

    await asyncio.sleep(0)

    assert client.closed
    assert not client.unremembering
    assert client.close_reasons == [ConnectionReason.VALIDATION]
    assert lock_held_at_close is True
    assert lock_held_at_refresh == [False]


async def test_validation_session_waits_for_poll_and_serializes_next_poll():
    coordinator, _client, poller = _coordinator()
    poll_started = asyncio.Event()
    release_poll = asyncio.Event()
    validation_started = asyncio.Event()
    release_validation = asyncio.Event()
    active = 0
    maximum = 0

    async def behaviour():
        nonlocal active, maximum
        active += 1
        maximum = max(maximum, active)
        poll_started.set()
        await release_poll.wait()
        active -= 1
        return _result()

    async def validation_probe():
        nonlocal active, maximum
        async with coordinator.async_validation_session():
            active += 1
            maximum = max(maximum, active)
            validation_started.set()
            await release_validation.wait()
            active -= 1

    poller.behaviour = behaviour
    poll = asyncio.create_task(coordinator._async_update_data())
    await poll_started.wait()
    validation = asyncio.create_task(validation_probe())
    next_poll = asyncio.create_task(coordinator._async_update_data())
    await asyncio.sleep(0)
    assert not validation_started.is_set()
    assert active == 1

    release_poll.set()
    await poll
    await validation_started.wait()
    assert active == 1
    assert not next_poll.done()
    release_validation.set()
    await asyncio.gather(validation, next_poll)

    assert maximum == 1


@pytest.mark.parametrize("cancel", [False, True])
async def test_validation_session_releases_cycle_lock_after_error_or_cancellation(
    cancel,
):
    coordinator, _client, _poller = _coordinator()
    entered = asyncio.Event()

    async def validation_probe():
        async with coordinator.async_validation_session():
            entered.set()
            if cancel:
                await asyncio.Event().wait()
            failure_message = "validation failed"
            raise ValueError(failure_message)

    task = asyncio.create_task(validation_probe())
    await entered.wait()
    if cancel:
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    else:
        with pytest.raises(ValueError, match="validation failed"):
            await task

    async with coordinator.async_validation_session():
        assert coordinator._cycle_lock.locked()


async def test_cancelled_callback_propagates_and_releases_the_cycle():
    coordinator, _client, poller = _coordinator()
    task = await _start_blocked_cycle(coordinator, poller)
    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task

    assert coordinator._update_task is None
    assert not coordinator._cycle_lock.locked()


async def test_shutdown_cancels_in_flight_callback_and_closes_client(monkeypatch):
    coordinator, client, poller = _coordinator()
    _replace_framework_shutdown(monkeypatch)
    task = await _start_blocked_cycle(coordinator, poller)
    await coordinator.async_shutdown()

    assert task.cancelled()
    assert client.closed
    assert coordinator.last_error is None


async def test_shutdown_during_own_callback_does_not_cancel_current_task(monkeypatch):
    coordinator, client, poller = _coordinator()
    _replace_framework_shutdown(monkeypatch)

    async def behaviour():
        await coordinator.async_shutdown()
        return _result({"pv_power": 4})

    poller.behaviour = behaviour

    assert await coordinator._async_update_data() == Telemetry(values={"pv_power": 4})
    assert client.closed


async def test_shutdown_without_active_callback_still_closes_client(monkeypatch):
    coordinator, client, _poller = _coordinator()
    _replace_framework_shutdown(monkeypatch)
    await coordinator.async_shutdown()

    assert client.closed


def test_the_stored_power_state_of_an_installation_has_its_own_versioned_file(
    monkeypatch,
):
    created = []

    class RecordingStore:
        def __init__(self, hass, version, key) -> None:
            created.append((hass, version, key))

    monkeypatch.setattr(coordinator_module, "Store", RecordingStore)
    hass = object()

    store = power_control_store(hass=hass, entry_id="entry-1")

    assert isinstance(store, RecordingStore)
    assert created == [
        (
            hass,
            coordinator_module.POWER_STORAGE_VERSION,
            "saj_local.power_control.entry-1",
        )
    ]


HS3_DEVICE = Device("TEST-001", 0x1610, 12000, HS3, detected=True)
GRID_LOST = {"inverter_fault_word_1": 1 << 23, "inverter_fault_word_3": 1 << 23}


def _hs3_coordinator(*, contexts=None):
    coordinator, client, poller = _coordinator(contexts=contexts)
    coordinator.device = HS3_DEVICE
    coordinator._faults = FaultWatch(fault_map=HS3.faults)
    return coordinator, client, poller


def test_the_words_behind_an_enabled_fault_entity_are_read_with_it():
    coordinator, _, _ = _hs3_coordinator(contexts={"inverter_fault_grid_lost"})
    coordinator._initial_refresh = False

    assert coordinator.enabled_keys == {
        "inverter_fault_grid_lost",
        "inverter_fault_word_1",
        "inverter_fault_word_3",
    }


async def test_a_good_cycle_clears_the_unreachable_and_model_issues(issues):
    coordinator, _, _ = _coordinator()

    await coordinator._async_update_data()

    assert issues.called("clear_unreachable") == [
        {"hass": coordinator.hass, "entry": coordinator._entry}
    ]
    assert issues.called("clear_model_issues") == [
        {"hass": coordinator.hass, "entry": coordinator._entry}
    ]


@pytest.mark.parametrize(
    ("tracked", "suspended", "read", "synced"),
    [
        (set(), set(), {"pv_power"}, None),
        (set(), {"pv_power"}, set(), {"pv_power"}),
        ({"pv_power"}, set(), set(), None),
        ({"pv_power"}, set(), {"pv_power"}, set()),
        ({"pv_power", "gone"}, {"grid_power"}, set(), {"pv_power", "grid_power"}),
    ],
)
async def test_the_refusal_issue_follows_what_is_suspended_answered_and_still_read(
    issues, tracked, suspended, read, synced
):
    coordinator, _, poller = _coordinator(contexts={"pv_power", "grid_power"})
    issues.opened = frozenset(tracked)
    poller.outcomes = [
        _result(dict.fromkeys(read, 1), suspended=suspended),
    ]

    await coordinator._async_update_data()

    calls = issues.called("sync_refusals")
    assert [call["keys"] for call in calls] == ([] if synced is None else [synced])
    assert all(
        call["hass"] is coordinator.hass and call["entry"] is coordinator._entry
        for call in calls
    )


async def test_a_failed_cycle_raises_the_model_issue_it_is_found_to_be(issues):
    coordinator, _, poller = _coordinator()
    issues.finding = "finding"
    cause = UnsupportedDeviceError(0x1234)
    poller.outcomes = [_failure(cause)]

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()

    assert issues.errors == [cause]
    assert issues.called("raise_model_issue") == [
        {
            "hass": coordinator.hass,
            "entry": coordinator._entry,
            "finding": "finding",
        }
    ]


async def test_a_failed_cycle_that_is_no_model_finding_raises_no_model_issue(issues):
    coordinator, _, poller = _coordinator()
    poller.outcomes = [_failure(TimeoutError())]

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()

    assert issues.called("raise_model_issue") == []


async def test_every_failed_cycle_checks_how_long_the_endpoint_has_been_down(issues):
    coordinator, _, poller = _coordinator()
    poller.outcomes = [_failure(TimeoutError())]

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()

    assert issues.called("check_unreachable") == [
        {
            "hass": coordinator.hass,
            "entry": coordinator._entry,
            "guard": coordinator.guard,
            "now": NOW,
        }
    ]


def _logged(caplog, level):
    return [r.getMessage() for r in caplog.records if r.levelno == level]


async def test_a_fault_turning_on_and_off_is_logged_once_each(caplog):
    coordinator, _, poller = _hs3_coordinator(contexts=set(GRID_LOST))
    poller.outcomes = [
        _result(GRID_LOST),
        _result(GRID_LOST),
        _result({"inverter_fault_word_1": 0, "inverter_fault_word_3": 0}),
    ]

    with caplog.at_level(logging.INFO):
        for _ in range(3):
            await coordinator._async_update_data()

    assert _logged(caplog, logging.WARNING) == [
        f"{ROOF_LABEL}: Fault inverter_fault_grid_lost is on"
    ]
    assert _logged(caplog, logging.INFO) == [
        f"{ROOF_LABEL}: Fault inverter_fault_grid_lost cleared"
    ]


async def test_an_unrecognised_bit_turning_on_and_off_is_logged_with_its_place(caplog):
    coordinator, _, poller = _hs3_coordinator(contexts={"inverter_fault_word_2"})
    poller.outcomes = [
        _result({"inverter_fault_word_2": 0b100}),
        _result({"inverter_fault_word_2": 0}),
    ]

    with caplog.at_level(logging.INFO):
        await coordinator._async_update_data()
        await coordinator._async_update_data()

    assert _logged(caplog, logging.WARNING) == [
        f"{ROOF_LABEL}: Unrecognised fault bit 0x4007:2 is set"
    ]
    assert _logged(caplog, logging.INFO) == [
        f"{ROOF_LABEL}: Unrecognised fault bit 0x4007:2 cleared"
    ]


async def test_a_battery_pack_fault_is_logged_when_it_turns_on_and_off(caplog):
    coordinator, _, poller = _hs3_coordinator(
        contexts={"battery_pack1_fault", "battery_pack1_warning"}
    )
    poller.outcomes = [
        _result({"battery_pack1_fault": 0, "battery_pack1_warning": 5}),
        _result({"battery_pack1_fault": 0, "battery_pack1_warning": 5}),
        _result({"battery_pack1_fault": 0, "battery_pack1_warning": 0}),
    ]

    with caplog.at_level(logging.INFO):
        for _ in range(3):
            await coordinator._async_update_data()

    assert _logged(caplog, logging.WARNING) == [
        f"{ROOF_LABEL}: Fault battery_pack1_warning is on"
    ]
    assert _logged(caplog, logging.INFO) == [
        f"{ROOF_LABEL}: Fault battery_pack1_warning cleared"
    ]


async def test_a_pack_word_that_is_not_read_is_not_taken_for_a_cleared_fault(caplog):
    coordinator, _, poller = _hs3_coordinator(contexts={"battery_pack1_warning"})
    poller.outcomes = [
        _result({"battery_pack1_warning": 5}),
        _result({}, unavailable={"battery_pack1_warning"}),
    ]

    with caplog.at_level(logging.INFO):
        await coordinator._async_update_data()
        await coordinator._async_update_data()

    assert _logged(caplog, logging.INFO) == []


HIDDEN_EV = {"ev_fault_word_1", "ev_fault_word_2"}


async def test_hidden_words_are_never_listed_in_the_refusal_issue(issues):
    coordinator, _, poller = _hs3_coordinator(contexts={"ev_fault", "pv_power"})
    poller.outcomes = [_result(suspended={"ev_fault", *HIDDEN_EV})]

    await coordinator._async_update_data()

    assert [call["keys"] for call in issues.called("sync_refusals")] == [{"ev_fault"}]


async def test_a_suspended_hidden_word_alone_does_not_open_the_refusal_issue(issues):
    coordinator, _, poller = _hs3_coordinator(contexts={"ev_fault"})
    coordinator._initial_refresh = False
    poller.outcomes = [_result(suspended=HIDDEN_EV)]

    await coordinator._async_update_data()

    assert issues.called("sync_refusals") == []


async def test_a_hidden_word_left_in_the_issue_is_dropped_with_its_dependents(issues):
    coordinator, _, poller = _hs3_coordinator(contexts={"pv_power"})
    coordinator._initial_refresh = False
    issues.opened = frozenset({"ev_fault", *HIDDEN_EV})
    poller.outcomes = [_result({"pv_power": 1})]

    await coordinator._async_update_data()

    assert [call["keys"] for call in issues.called("sync_refusals")] == [set()]
