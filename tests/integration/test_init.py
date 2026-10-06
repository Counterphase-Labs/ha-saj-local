from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import ClassVar

import pytest
from homeassistant.exceptions import ConfigEntryError, ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import UpdateFailed

import custom_components.saj_local as integration
from custom_components.saj_local import SajRuntimeData
from custom_components.saj_local.const import DOMAIN
from custom_components.saj_local.saj.client import ModbusError, ModbusErrorMessage
from custom_components.saj_local.saj.hs3 import Hs3Device, UnsupportedDeviceError

SERIAL = "HS3-TEST-001"
DEVICE = Hs3Device(SERIAL, 0x1610, 12000)


class FakeClient:
    instances: ClassVar[list[FakeClient]] = []

    def __init__(self, *_args, **_kwargs) -> None:
        self.host = _kwargs.get("host", _args[0] if _args else "host")
        self.closed = False
        self.instances.append(self)

    def is_connected(self) -> bool:
        return not self.closed

    async def close(self) -> None:
        self.closed = True


class FakeCoordinator:
    instances: ClassVar[list[FakeCoordinator]] = []

    def __init__(self, *_args, **_kwargs) -> None:
        self.refreshed = False
        self.shutdown = False
        self.instances.append(self)

    async def async_config_entry_first_refresh(self) -> None:
        self.refreshed = True

    async def async_shutdown(self) -> None:
        self.shutdown = True


@dataclass
class FakeEntry:
    unique_id: str
    data: dict[str, object]
    options: dict[str, object] = field(default_factory=dict)
    runtime_data: SajRuntimeData | None = None
    entry_id: str = "entry-1"

    def add_update_listener(self, _listener):
        return lambda: None

    def async_on_unload(self, _callback) -> None:
        return


class FakeConfigEntries:
    async def async_forward_entry_setups(self, _entry, _platforms) -> None:
        return

    async def async_unload_platforms(self, _entry, _platforms) -> bool:
        return True

    async def async_reload(self, _entry_id) -> None:
        return


@pytest.fixture(autouse=True)
def reset_fake_instances():
    FakeClient.instances.clear()
    FakeCoordinator.instances.clear()


def _hass():
    return SimpleNamespace(config_entries=FakeConfigEntries())


def _entry(host: str = "inverter", serial: str = SERIAL) -> FakeEntry:
    return FakeEntry(
        unique_id=serial,
        data={"host": host, "port": 502, "unit_id": 1},
    )


def _patch_success(monkeypatch) -> None:
    monkeypatch.setattr(integration, "ModbusTcpClient", FakeClient)
    monkeypatch.setattr(integration, "SajCoordinator", FakeCoordinator)

    async def identify(client):
        return DEVICE

    monkeypatch.setattr(integration, "identify", identify)


async def test_entry_loads_into_runtime_and_unloads_owned_resources(monkeypatch):
    hass = _hass()
    _patch_success(monkeypatch)
    entry = _entry()

    async def forward(_entry, _platforms):
        return

    async def unload(_entry, _platforms):
        return True

    monkeypatch.setattr(hass.config_entries, "async_forward_entry_setups", forward)
    monkeypatch.setattr(hass.config_entries, "async_unload_platforms", unload)

    assert await integration.async_setup_entry(hass, entry)
    assert isinstance(entry.runtime_data, SajRuntimeData)
    assert entry.runtime_data.device == DEVICE
    assert entry.runtime_data.coordinator.refreshed

    assert await integration.async_unload_entry(hass, entry)
    assert entry.runtime_data.coordinator.shutdown
    assert FakeClient.instances[0].closed


async def test_multiple_entries_own_independent_runtime_resources(monkeypatch):
    hass = _hass()
    _patch_success(monkeypatch)

    async def identify_by_endpoint(client):
        return Hs3Device(f"SERIAL-{client.host}", 0x1610, 12000)

    async def forward(_entry, _platforms):
        return

    monkeypatch.setattr(integration, "identify", identify_by_endpoint)
    monkeypatch.setattr(hass.config_entries, "async_forward_entry_setups", forward)
    entries = (
        _entry("inverter-a", "SERIAL-inverter-a"),
        _entry("inverter-b", "SERIAL-inverter-b"),
    )
    for entry in entries:
        assert await integration.async_setup_entry(hass, entry)

    assert entries[0].runtime_data.client is not entries[1].runtime_data.client
    assert (
        entries[0].runtime_data.coordinator is not entries[1].runtime_data.coordinator
    )


@pytest.mark.parametrize(
    ("failure", "expected_error", "reason"),
    [
        (UnsupportedDeviceError("unsupported"), ConfigEntryError, "unsupported_device"),
        (
            ModbusError(ModbusErrorMessage.CONNECTION_TIMEOUT),
            ConfigEntryNotReady,
            "timeout",
        ),
        (
            ModbusError(ModbusErrorMessage.REQUEST_TIMEOUT),
            ConfigEntryNotReady,
            "timeout",
        ),
        (
            ModbusError("Modbus exception response", exception_code=6),
            ConfigEntryNotReady,
            "read_rejected",
        ),
        (
            ModbusError(ModbusErrorMessage.MISMATCHED_HEADER),
            ConfigEntryNotReady,
            "cannot_connect",
        ),
        (ValueError("invalid data"), ConfigEntryError, "invalid_device_data"),
    ],
)
async def test_setup_closes_client_and_classifies_device_failure(
    monkeypatch, failure, expected_error, reason
):
    hass = _hass()
    _patch_success(monkeypatch)

    async def fail(client):
        raise failure

    monkeypatch.setattr(integration, "identify", fail)
    entry = _entry()

    with pytest.raises(expected_error) as error:
        await integration.async_setup_entry(hass, entry)
    assert error.value.translation_key == reason
    assert error.value.__cause__ is failure
    assert FakeClient.instances[0].closed


async def test_setup_rejects_replacement_serial_and_closes_client(monkeypatch):
    hass = _hass()
    _patch_success(monkeypatch)

    async def other_identity(client):
        return Hs3Device("OTHER-SERIAL", 0x1610, 12000)

    monkeypatch.setattr(integration, "identify", other_identity)
    entry = _entry()

    with pytest.raises(ConfigEntryError):
        await integration.async_setup_entry(hass, entry)
    assert FakeClient.instances[0].closed
    assert FakeCoordinator.instances == []


async def test_initial_telemetry_failure_after_identity_closes_client_with_translation(
    monkeypatch,
):
    hass = _hass()
    _patch_success(monkeypatch)
    entry = _entry()
    translated_failure = UpdateFailed(
        translation_domain=DOMAIN, translation_key="read_rejected"
    )

    async def fail_first_refresh(self):
        self.refreshed = True
        raise ConfigEntryNotReady(
            translation_domain=translated_failure.translation_domain,
            translation_key=translated_failure.translation_key,
        ) from translated_failure

    monkeypatch.setattr(
        FakeCoordinator, "async_config_entry_first_refresh", fail_first_refresh
    )

    with pytest.raises(ConfigEntryNotReady) as caught:
        await integration.async_setup_entry(hass, entry)

    assert caught.value.translation_domain == DOMAIN
    assert caught.value.translation_key == "read_rejected"
    assert caught.value.__cause__ is translated_failure
    assert FakeCoordinator.instances[0].refreshed
    assert FakeClient.instances[0].closed


async def test_setup_closes_client_on_cancellation(monkeypatch):
    hass = _hass()
    _patch_success(monkeypatch)

    async def cancelled(client):
        raise asyncio.CancelledError

    monkeypatch.setattr(integration, "identify", cancelled)
    entry = _entry()

    with pytest.raises(asyncio.CancelledError):
        await integration.async_setup_entry(hass, entry)
    assert FakeClient.instances[0].closed


async def test_setup_closes_client_on_unexpected_exception(monkeypatch):
    hass = _hass()
    _patch_success(monkeypatch)

    async def crash(client):
        raise RuntimeError

    monkeypatch.setattr(integration, "identify", crash)
    entry = _entry()

    with pytest.raises(RuntimeError):
        await integration.async_setup_entry(hass, entry)
    assert FakeClient.instances[0].closed


async def test_setup_cleans_up_if_platform_forwarding_fails(monkeypatch):
    hass = _hass()
    _patch_success(monkeypatch)
    entry = _entry()

    async def fail_forward(_entry, _platforms):
        raise RuntimeError

    monkeypatch.setattr(hass.config_entries, "async_forward_entry_setups", fail_forward)

    with pytest.raises(RuntimeError):
        await integration.async_setup_entry(hass, entry)
    assert FakeCoordinator.instances[0].shutdown
    assert FakeClient.instances[0].closed


async def test_setup_cleans_up_if_platform_forwarding_is_cancelled(monkeypatch):
    hass = _hass()
    _patch_success(monkeypatch)
    entry = _entry()

    async def cancel_forward(_entry, _platforms):
        raise asyncio.CancelledError

    monkeypatch.setattr(
        hass.config_entries, "async_forward_entry_setups", cancel_forward
    )

    with pytest.raises(asyncio.CancelledError):
        await integration.async_setup_entry(hass, entry)
    assert FakeCoordinator.instances[0].shutdown
    assert FakeClient.instances[0].closed


async def test_unload_failure_preserves_entry_resources(monkeypatch):
    hass = _hass()
    entry = _entry()
    client = FakeClient()
    coordinator = FakeCoordinator()
    entry.runtime_data = SajRuntimeData(client, DEVICE, coordinator)

    async def fail_unload(_entry, _platforms):
        return False

    monkeypatch.setattr(hass.config_entries, "async_unload_platforms", fail_unload)
    assert not await integration.async_unload_entry(hass, entry)
    assert not client.closed
    assert not coordinator.shutdown


async def test_options_listener_reloads_entry(monkeypatch):
    hass = _hass()
    calls = []

    async def reload(entry_id):
        calls.append(entry_id)

    monkeypatch.setattr(hass.config_entries, "async_reload", reload)
    entry = _entry()
    await integration._async_options_updated(hass, entry)
    assert calls == [entry.entry_id]
