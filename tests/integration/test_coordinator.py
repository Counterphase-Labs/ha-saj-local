import asyncio
import logging
from datetime import timedelta
from types import SimpleNamespace

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.saj_local import coordinator as coordinator_module
from custom_components.saj_local.const import DOMAIN
from custom_components.saj_local.coordinator import SajCoordinator
from custom_components.saj_local.errors import Translation
from custom_components.saj_local.saj.client import ModbusError, ModbusErrorMessage
from custom_components.saj_local.saj.device import Device
from custom_components.saj_local.saj.errors import (
    ModelMismatchError,
    UnknownModelError,
    UnsupportedDeviceError,
)
from custom_components.saj_local.saj.profiles import Profile
from custom_components.saj_local.saj.telemetry import Telemetry

PROFILE = Profile(
    key="alpha",
    display_name="Alpha",
    device_types=frozenset({0x1610}),
    measurement_keys=frozenset({"pv_power", "grid_power", "battery_soc"}),
    hand_verified=True,
)
OTHER_PROFILE = Profile(
    key="beta",
    display_name="Beta",
    device_types=frozenset({0x0010}),
    measurement_keys=frozenset(),
    hand_verified=False,
)
SELECTION = "automatic"
DEVICE = Device("TEST-001", 0x1610, 12000, PROFILE, detected=True)
TELEMETRY = Telemetry(values={"pv_power": 3000})


class FakeClient:
    def __init__(self, *, connected: bool = True) -> None:
        self.connected = connected
        self.closed = False
        self.connect_calls = 0
        self.close_calls = 0

    def is_connected(self) -> bool:
        return self.connected

    async def connect(self) -> None:
        self.connect_calls += 1
        self.connected = True

    async def close(self) -> None:
        self.close_calls += 1
        self.connected = False
        self.closed = True


def _coordinator(
    monkeypatch, *, connected: bool = True, contexts: set[str] | None = None
) -> tuple[SajCoordinator, FakeClient]:
    client = FakeClient(connected=connected)
    coordinator = object.__new__(SajCoordinator)
    coordinator.client = client
    coordinator.device = DEVICE
    coordinator.model_selection = SELECTION
    coordinator.interval = 30
    coordinator.last_error = None
    coordinator._cycle_lock = asyncio.Lock()
    coordinator._initial_refresh = True
    coordinator._update_task = None
    active_contexts = contexts or set()
    coordinator.async_contexts = lambda: iter(active_contexts)
    monkeypatch.setattr(coordinator_module, "identify", _identify)
    monkeypatch.setattr(coordinator_module, "read_telemetry", _read)
    return coordinator, client


def _replace_framework_shutdown(monkeypatch) -> None:
    async def framework_shutdown(_coordinator):
        return

    monkeypatch.setattr(
        coordinator_module.DataUpdateCoordinator, "async_shutdown", framework_shutdown
    )


async def _start_blocked_cycle(coordinator, monkeypatch):
    started = asyncio.Event()
    wait_forever = asyncio.Event()

    async def read(client, device, enabled):
        del client, device, enabled
        started.set()
        await wait_forever.wait()
        return TELEMETRY

    monkeypatch.setattr(coordinator_module, "read_telemetry", read)
    task = asyncio.create_task(coordinator._async_update_data())
    await started.wait()
    return task


def test_constructor_initializes_coordinator_state_with_framework_stub(monkeypatch):
    captured = {}
    client = FakeClient()
    hass = object()

    def framework_init(coordinator, *, hass, logger, name, update_interval) -> None:
        captured.update(
            hass=hass,
            logger=logger,
            name=name,
            update_interval=update_interval,
        )

    monkeypatch.setattr(
        coordinator_module.DataUpdateCoordinator, "__init__", framework_init
    )
    entry = SimpleNamespace(
        entry_id="logical-installation",
        options={"scan_interval": 47},
        data={"model": "alpha"},
    )
    coordinator = SajCoordinator(hass, client, DEVICE, entry)

    assert captured["hass"] is hass
    assert captured["name"] == "SAJ"
    assert captured["update_interval"] == timedelta(seconds=47)
    assert coordinator.client is client
    assert coordinator.device is DEVICE
    assert coordinator.entry_id == "logical-installation"
    assert coordinator.interval == 47
    assert coordinator.model_selection == "alpha"
    assert coordinator.last_error is None
    assert coordinator._initial_refresh


async def _identify(client, selection) -> Device:
    del client, selection
    return DEVICE


async def _read(client, device, enabled) -> Telemetry:
    del client, device, enabled
    return TELEMETRY


async def test_first_callback_reads_all_sensor_contexts(monkeypatch):
    coordinator, _client = _coordinator(monkeypatch)
    received: list[set[str]] = []

    async def read(client, device, enabled):
        del client, device
        received.append(enabled)
        return TELEMETRY

    monkeypatch.setattr(coordinator_module, "read_telemetry", read)

    assert await coordinator._async_update_data() == TELEMETRY
    assert received == [set(PROFILE.measurement_keys)]
    assert coordinator.enabled_sensor_keys == set()


async def test_callback_reads_only_contexts_with_active_entity_listeners(monkeypatch):
    coordinator, _client = _coordinator(
        monkeypatch, contexts={"pv_power", "grid_power"}
    )
    await coordinator._async_update_data()
    received: list[set[str]] = []

    async def read(client, device, enabled):
        del client, device
        received.append(enabled)
        return TELEMETRY

    monkeypatch.setattr(coordinator_module, "read_telemetry", read)
    await coordinator._async_update_data()

    assert received == [{"pv_power", "grid_power"}]


async def test_callback_requests_no_telemetry_when_all_sensor_contexts_are_inactive(
    monkeypatch,
):
    coordinator, _client = _coordinator(monkeypatch)
    await coordinator._async_update_data()
    coordinator.async_contexts = lambda: iter(set())
    received: list[set[str]] = []

    async def read(client, device, enabled):
        del client, device
        received.append(enabled)
        return Telemetry(values={})

    monkeypatch.setattr(coordinator_module, "read_telemetry", read)
    await coordinator._async_update_data()

    assert received == [set()]


async def test_callback_lock_serializes_overlapping_cycles(monkeypatch):
    coordinator, _client = _coordinator(monkeypatch)
    first_started = asyncio.Event()
    release_first = asyncio.Event()
    active_reads = 0
    maximum_active_reads = 0

    async def read(client, device, enabled):
        nonlocal active_reads, maximum_active_reads
        del client, device, enabled
        active_reads += 1
        maximum_active_reads = max(maximum_active_reads, active_reads)
        if active_reads == 1:
            first_started.set()
            await release_first.wait()
        active_reads -= 1
        return TELEMETRY

    monkeypatch.setattr(coordinator_module, "read_telemetry", read)
    first = asyncio.create_task(coordinator._async_update_data())
    await first_started.wait()
    second = asyncio.create_task(coordinator._async_update_data())
    await asyncio.sleep(0)
    assert active_reads == 1
    release_first.set()
    await asyncio.gather(first, second)

    assert maximum_active_reads == 1


async def test_validation_session_waits_for_poll_and_serializes_next_poll(monkeypatch):
    coordinator, _client = _coordinator(monkeypatch)
    poll_started = asyncio.Event()
    release_poll = asyncio.Event()
    validation_started = asyncio.Event()
    release_validation = asyncio.Event()
    active_requests = 0
    maximum_active_requests = 0

    async def read(client, device, enabled):
        nonlocal active_requests, maximum_active_requests
        del client, device, enabled
        active_requests += 1
        maximum_active_requests = max(maximum_active_requests, active_requests)
        poll_started.set()
        await release_poll.wait()
        active_requests -= 1
        return TELEMETRY

    async def validation_probe():
        nonlocal active_requests, maximum_active_requests
        async with coordinator.async_validation_session():
            active_requests += 1
            maximum_active_requests = max(maximum_active_requests, active_requests)
            validation_started.set()
            await release_validation.wait()
            active_requests -= 1

    monkeypatch.setattr(coordinator_module, "read_telemetry", read)
    poll = asyncio.create_task(coordinator._async_update_data())
    await poll_started.wait()
    validation = asyncio.create_task(validation_probe())
    next_poll = asyncio.create_task(coordinator._async_update_data())
    await asyncio.sleep(0)
    assert not validation_started.is_set()
    assert active_requests == 1

    release_poll.set()
    await poll
    await validation_started.wait()
    assert active_requests == 1
    assert not next_poll.done()
    release_validation.set()
    await asyncio.gather(validation, next_poll)

    assert maximum_active_requests == 1


@pytest.mark.parametrize("cancel", [False, True])
async def test_validation_session_releases_cycle_lock_after_error_or_cancellation(
    monkeypatch, cancel
):
    coordinator, _client = _coordinator(monkeypatch)
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


async def test_reconnect_identifies_with_the_stored_model_selection(monkeypatch):
    coordinator, _client = _coordinator(monkeypatch, connected=False)
    coordinator.model_selection = "beta"
    selections = []

    async def identify(client, selection):
        del client
        selections.append(selection)
        return DEVICE

    monkeypatch.setattr(coordinator_module, "identify", identify)
    await coordinator._async_update_data()

    assert selections == ["beta"]


async def test_reconnect_checks_identity_then_records_recovery(monkeypatch, caplog):
    coordinator, client = _coordinator(monkeypatch, connected=False)
    coordinator.last_error = {"type": "ModbusError", "exception_code": 6}

    with caplog.at_level(logging.INFO):
        assert await coordinator._async_update_data() == TELEMETRY

    assert client.connect_calls == 1
    assert "SAJ connection restored" in caplog.text
    assert coordinator.last_error is None


MODEL_FAILURES = [
    UnsupportedDeviceError(0x1234),
    ModelMismatchError(selected=PROFILE, detected=OTHER_PROFILE),
    UnknownModelError("gamma"),
]


@pytest.mark.parametrize(
    "failure",
    [
        TimeoutError("private timeout details"),
        OSError("private host socket details"),
        ValueError("malformed telemetry"),
        ModbusError(ModbusErrorMessage.MISMATCHED_HEADER),
        *MODEL_FAILURES,
    ],
)
async def test_poll_failures_close_client_and_carry_translated_action(
    monkeypatch, failure
):
    coordinator, client = _coordinator(monkeypatch)

    async def fail(client, device, enabled):
        del client, device, enabled
        raise failure

    def translate(error):
        assert error is failure
        return Translation(key="stubbed", placeholders={"detail": "value"})

    monkeypatch.setattr(coordinator_module, "read_telemetry", fail)
    monkeypatch.setattr(coordinator_module, "translate_error", translate)
    with pytest.raises(UpdateFailed) as caught:
        await coordinator._async_update_data()

    assert caught.value.translation_domain == DOMAIN
    assert caught.value.translation_key == "stubbed"
    assert caught.value.translation_placeholders == {"detail": "value"}
    assert caught.value.__cause__ is failure
    assert client.closed


async def _last_error_after_failure(monkeypatch, failure):
    coordinator, _client = _coordinator(monkeypatch)

    async def fail(client, device, enabled):
        del client, device, enabled
        raise failure

    monkeypatch.setattr(coordinator_module, "read_telemetry", fail)
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()
    return coordinator.last_error


@pytest.mark.parametrize("failure", MODEL_FAILURES)
async def test_model_failures_record_their_own_message_in_last_error(
    monkeypatch, failure
):
    assert await _last_error_after_failure(monkeypatch, failure) == {
        "type": type(failure).__name__,
        "reason": str(failure),
        "exception_code": None,
    }


@pytest.mark.parametrize(
    "failure", [OSError("private host socket details"), ValueError("private")]
)
async def test_other_failures_record_a_generic_reason(monkeypatch, failure):
    last_error = await _last_error_after_failure(monkeypatch, failure)

    assert last_error["reason"] == "Device read failed"


async def test_modbus_failure_records_exception_code(monkeypatch):
    failure = ModbusError(ModbusErrorMessage.EXCEPTION_RESPONSE, exception_code=2)

    last_error = await _last_error_after_failure(monkeypatch, failure)

    assert last_error["exception_code"] == 2


async def test_reconnect_identity_change_has_specific_translation(monkeypatch):
    coordinator, client = _coordinator(monkeypatch, connected=False)

    async def identify_other(client, selection):
        del client, selection
        return Device("OTHER-SERIAL", 0x1610, 12000, PROFILE, detected=True)

    monkeypatch.setattr(coordinator_module, "identify", identify_other)
    with pytest.raises(UpdateFailed) as caught:
        await coordinator._async_update_data()

    assert caught.value.translation_domain == DOMAIN
    assert caught.value.translation_key == "identity_mismatch"
    assert client.closed
    assert coordinator.last_error["type"] == "IdentityChangedError"
    assert "OTHER-SERIAL" not in str(coordinator.last_error)


async def test_identical_failures_log_only_on_state_transition(monkeypatch, caplog):
    coordinator, client = _coordinator(monkeypatch)

    async def fail(client, device, enabled):
        del client, device, enabled
        error_message = "Modbus exception response"
        raise ModbusError(error_message)

    monkeypatch.setattr(coordinator_module, "read_telemetry", fail)
    with caplog.at_level(logging.WARNING):
        for _ in range(2):
            with pytest.raises(UpdateFailed):
                await coordinator._async_update_data()
            client.connected = True

    assert caplog.text.count("SAJ update failed") == 1


async def test_cancelled_callback_closes_client_and_propagates(monkeypatch):
    coordinator, client = _coordinator(monkeypatch)
    task = await _start_blocked_cycle(coordinator, monkeypatch)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert client.closed


async def test_shutdown_cancels_in_flight_callback_and_closes_client(monkeypatch):
    coordinator, client = _coordinator(monkeypatch)
    _replace_framework_shutdown(monkeypatch)
    task = await _start_blocked_cycle(coordinator, monkeypatch)
    await coordinator.async_shutdown()

    assert task.cancelled()
    assert client.closed
    assert coordinator.last_error is None


async def test_shutdown_during_own_callback_does_not_cancel_current_task(monkeypatch):
    coordinator, client = _coordinator(monkeypatch)
    _replace_framework_shutdown(monkeypatch)

    async def read(client, device, enabled):
        del client, device, enabled
        await coordinator.async_shutdown()
        return TELEMETRY

    monkeypatch.setattr(coordinator_module, "read_telemetry", read)
    assert await coordinator._async_update_data() == TELEMETRY
    assert client.closed


async def test_shutdown_without_active_callback_still_closes_client(monkeypatch):
    coordinator, client = _coordinator(monkeypatch)
    _replace_framework_shutdown(monkeypatch)
    await coordinator.async_shutdown()

    assert client.closed
