import asyncio
import logging
from datetime import timedelta

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.saj_local import coordinator as coordinator_module
from custom_components.saj_local.const import DOMAIN, SENSOR_KEYS
from custom_components.saj_local.coordinator import SajCoordinator
from custom_components.saj_local.saj.client import ModbusError, ModbusErrorMessage
from custom_components.saj_local.saj.hs3 import (
    Hs3Device,
    Hs3Telemetry,
    UnsupportedDeviceError,
)

DEVICE = Hs3Device("HS3-TEST-001", 0x1610, 12000)
TELEMETRY = Hs3Telemetry(2, 3000, -200, 75, -40, 1000)


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

    async def read(client, enabled):
        del client, enabled
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
    coordinator = SajCoordinator(
        hass, client, DEVICE, entry_id="logical-installation", interval=47
    )

    assert captured["hass"] is hass
    assert captured["name"] == "SAJ"
    assert captured["update_interval"] == timedelta(seconds=47)
    assert coordinator.client is client
    assert coordinator.device is DEVICE
    assert coordinator.entry_id == "logical-installation"
    assert coordinator.interval == 47
    assert coordinator.last_error is None
    assert coordinator._initial_refresh


async def _identify(client) -> Hs3Device:
    del client
    return DEVICE


async def _read(client, enabled) -> Hs3Telemetry:
    del client, enabled
    return TELEMETRY


async def test_first_callback_reads_all_sensor_contexts(monkeypatch):
    coordinator, _client = _coordinator(monkeypatch)
    received: list[set[str]] = []

    async def read(client, enabled):
        del client
        received.append(enabled)
        return TELEMETRY

    monkeypatch.setattr(coordinator_module, "read_telemetry", read)

    assert await coordinator._async_update_data() == TELEMETRY
    assert received == [set(SENSOR_KEYS)]
    assert coordinator.enabled_sensor_keys == set()


async def test_callback_reads_only_contexts_with_active_entity_listeners(monkeypatch):
    coordinator, _client = _coordinator(
        monkeypatch, contexts={"pv_power", "grid_power"}
    )
    await coordinator._async_update_data()
    received: list[set[str]] = []

    async def read(client, enabled):
        del client
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

    async def read(client, enabled):
        del client
        received.append(enabled)
        return Hs3Telemetry()

    monkeypatch.setattr(coordinator_module, "read_telemetry", read)
    await coordinator._async_update_data()

    assert received == [set()]


async def test_callback_lock_serializes_overlapping_cycles(monkeypatch):
    coordinator, _client = _coordinator(monkeypatch)
    first_started = asyncio.Event()
    release_first = asyncio.Event()
    active_reads = 0
    maximum_active_reads = 0

    async def read(client, enabled):
        nonlocal active_reads, maximum_active_reads
        del client, enabled
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

    async def read(client, enabled):
        nonlocal active_requests, maximum_active_requests
        del client, enabled
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


async def test_reconnect_checks_identity_then_records_recovery(monkeypatch, caplog):
    coordinator, client = _coordinator(monkeypatch, connected=False)
    coordinator.last_error = {"type": "ModbusError", "exception_code": 6}

    with caplog.at_level(logging.INFO):
        assert await coordinator._async_update_data() == TELEMETRY

    assert client.connect_calls == 1
    assert "SAJ connection restored" in caplog.text
    assert coordinator.last_error is None


@pytest.mark.parametrize(
    ("failure", "translation_key"),
    [
        (TimeoutError("private timeout details"), "timeout"),
        (ModbusError(ModbusErrorMessage.CONNECTION_TIMEOUT), "timeout"),
        (ModbusError(ModbusErrorMessage.REQUEST_TIMEOUT), "timeout"),
        (ModbusError("Modbus exception response", exception_code=2), "read_rejected"),
        (ModbusError(ModbusErrorMessage.MISMATCHED_HEADER), "cannot_connect"),
        (OSError("private host socket details"), "cannot_connect"),
        (ValueError("malformed telemetry"), "invalid_device_data"),
        (UnsupportedDeviceError("unsupported device"), "unsupported_device"),
    ],
)
async def test_poll_failures_close_client_and_carry_translated_action(
    monkeypatch, failure, translation_key
):
    coordinator, client = _coordinator(monkeypatch)

    async def fail(client, enabled):
        del client, enabled
        raise failure

    monkeypatch.setattr(coordinator_module, "read_telemetry", fail)
    with pytest.raises(UpdateFailed) as caught:
        await coordinator._async_update_data()

    assert caught.value.translation_domain == DOMAIN
    assert caught.value.translation_key == translation_key
    assert caught.value.__cause__ is failure
    assert client.closed
    assert caught.value.args == (translation_key,)
    if isinstance(failure, ModbusError) and failure.exception_code is not None:
        assert coordinator.last_error["exception_code"] == 2
    if isinstance(failure, OSError):
        assert coordinator.last_error["reason"] == "Device read failed"


async def test_reconnect_identity_change_has_specific_translation(monkeypatch):
    coordinator, client = _coordinator(monkeypatch, connected=False)

    async def identify_other(client):
        del client
        return Hs3Device("OTHER-SERIAL", 0x1610, 12000)

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

    async def fail(client, enabled):
        del client, enabled
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

    async def read(client, enabled):
        del client, enabled
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
