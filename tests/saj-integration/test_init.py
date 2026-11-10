from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field, replace
from types import SimpleNamespace
from typing import ClassVar

import pytest
from homeassistant.exceptions import ConfigEntryError, ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import UpdateFailed

import custom_components.saj_local as integration
from custom_components.saj_local import SajRuntimeData, errors
from custom_components.saj_local.const import DOMAIN, endpoint_guard
from custom_components.saj_local.equipment import PackReport
from custom_components.saj_local.saj import errors as saj_errors
from custom_components.saj_local.saj.client import ModbusError, ModbusErrorMessage
from custom_components.saj_local.saj.device import Device
from custom_components.saj_local.saj.models import Equipment
from custom_components.saj_local.saj.models.hs3 import PROFILE as HS3
from tests.issues import IssueRecorder
from tests.profiles import profile

SERIAL = "HS3-TEST-001"
PROFILE = profile(
    base=HS3, key="alpha", device_types={0x1610}, keys=(), hand_verified=True
)
OTHER_PROFILE = profile(
    base=HS3, key="beta", device_types={0x0010}, keys=(), hand_verified=False
)
DEVICE = Device(SERIAL, 0x1610, 12000, PROFILE, detected=True)
PACKS = PackReport(count_read=None, limit=None)


class FakeClient:
    instances: ClassVar[list[FakeClient]] = []

    def __init__(self, *_args, **_kwargs) -> None:
        self.host = _kwargs.get("host", _args[0] if _args else "host")
        self.environment = _kwargs.get("environment")
        self.closed = False
        self.instances.append(self)

    def is_connected(self) -> bool:
        return not self.closed

    async def close(self, **_options) -> None:
        self.closed = True


class FakeCoordinator:
    instances: ClassVar[list[FakeCoordinator]] = []

    def __init__(self, *_args, **kwargs) -> None:
        self.entry = kwargs.get("entry")
        self.installation = kwargs.get("installation")
        self.refreshed = False
        self.shutdown = False
        self.released = 0
        self.battery_saves = 0
        self.control_allowed = True
        self.events: list[str] = []
        self.setup_events: list[str] = []
        self.instances.append(self)

    async def async_release_power_control(self) -> None:
        self.released += 1
        self.events.append("release")

    async def async_save_battery(self) -> None:
        self.battery_saves += 1

    async def async_load_stored_state(self) -> None:
        self.setup_events.append("load")

    async def async_config_entry_first_refresh(self) -> None:
        self.refreshed = True
        self.setup_events.append("refresh")

    async def async_follow_schedules(self) -> None:
        self.setup_events.append("follow")

    async def async_shutdown(self) -> None:
        self.shutdown = True
        self.events.append("shutdown")


@dataclass
class FakeEntry:
    unique_id: str
    data: dict[str, object]
    options: dict[str, object] = field(default_factory=dict)
    subentries: dict[str, object] = field(default_factory=dict)
    runtime_data: SajRuntimeData | None = None
    entry_id: str = "entry-1"
    title: str = "Roof inverter"
    unload_callbacks: list = field(default_factory=list)

    def add_update_listener(self, _listener):
        return lambda: None

    def async_on_unload(self, callback) -> None:
        self.unload_callbacks.append(callback)


class FakeBus:
    def __init__(self) -> None:
        self.listeners: list[tuple[str, object]] = []
        self.removed = 0

    def async_listen_once(self, event_type, listener):
        self.listeners.append((event_type, listener))

        def remove() -> None:
            self.removed += 1

        return remove


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


NOW = 500.0


@pytest.fixture(autouse=True)
def issues(monkeypatch) -> IssueRecorder:
    recorder = IssueRecorder()
    recorder.install(
        monkeypatch,
        module=integration,
        names=(
            "check_unreachable",
            "clear_model_issues",
            "raise_identity_issue",
            "raise_model_issue",
            "remove_issues",
        ),
    )
    return recorder


class ControlRecorder:
    def __init__(self) -> None:
        self.applied: list[dict[str, object]] = []
        self.listening: list[dict[str, object]] = []
        self.stopped = 0
        self.order: list[str] = []

    def apply(self, **kwargs) -> None:
        self.applied.append(kwargs)
        self.order.append("apply")

    def listen(self, **kwargs):
        self.listening.append(kwargs)
        self.order.append("listen")

        def stop() -> None:
            self.stopped += 1

        return stop


@pytest.fixture(autouse=True)
def controls(monkeypatch) -> ControlRecorder:
    recorder = ControlRecorder()
    monkeypatch.setattr(integration, "apply_control_set", recorder.apply)
    monkeypatch.setattr(integration, "start_control_listener", recorder.listen)
    return recorder


def _hass():
    return SimpleNamespace(
        config_entries=FakeConfigEntries(),
        data={},
        bus=FakeBus(),
        loop=SimpleNamespace(time=lambda: NOW),
    )


def _entry(
    host: str = "inverter", serial: str = SERIAL, model: str = "automatic"
) -> FakeEntry:
    return FakeEntry(
        unique_id=serial,
        data={"host": host, "port": 502, "unit_id": 1, "model": model},
    )


def _patch_success(monkeypatch) -> None:
    monkeypatch.setattr(integration, "ModbusTcpClient", FakeClient)
    monkeypatch.setattr(integration, "SajCoordinator", FakeCoordinator)

    async def identify(client, selection):
        return DEVICE

    monkeypatch.setattr(integration, "identify", identify)

    async def settle_equipment(*, hass, entry, client, device):
        del hass, entry, client
        return device, {}, PACKS

    monkeypatch.setattr(integration, "settle_equipment", settle_equipment)


async def test_setup_gives_the_masked_label_to_the_client_and_control_and_logs_identity(
    monkeypatch, caplog
):
    captured = {}

    class RecordingControl:
        def __init__(self, **kwargs) -> None:
            captured.update(kwargs)

    _patch_success(monkeypatch)
    monkeypatch.setattr(integration, "Control", RecordingControl)

    with caplog.at_level(logging.DEBUG, logger=integration.__name__):
        assert await integration.async_setup_entry(_hass(), _entry())

    label = "Roof inverter (xxxxx001)"
    assert FakeClient.instances[0].environment.label == label
    assert captured["environment"].label == label
    assert [record.getMessage() for record in caplog.records] == [
        (
            f"{label}: Identity read: model alpha, device type 0x1610, "
            "rated power 12000 W, detected"
        )
    ]
    assert SERIAL not in caplog.text


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


@pytest.mark.parametrize("selection", ["automatic", "alpha", "beta"])
async def test_entry_load_identifies_with_the_stored_model_selection(
    monkeypatch, selection
):
    hass = _hass()
    _patch_success(monkeypatch)
    selections = []

    async def identify(client, selection):
        selections.append(selection)
        return DEVICE

    monkeypatch.setattr(integration, "identify", identify)
    entry = _entry(model=selection)

    assert await integration.async_setup_entry(hass, entry)
    assert selections == [selection]
    assert FakeCoordinator.instances[0].entry is entry


async def test_multiple_entries_own_independent_runtime_resources(monkeypatch):
    hass = _hass()
    _patch_success(monkeypatch)

    async def identify_by_endpoint(client, selection):
        return Device(f"SERIAL-{client.host}", 0x1610, 12000, PROFILE, detected=True)

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
    ("failure", "expected_error"),
    [
        (saj_errors.UnsupportedDeviceError(0x1234), ConfigEntryError),
        (
            saj_errors.ModelMismatchError(selected=PROFILE, detected=OTHER_PROFILE),
            ConfigEntryError,
        ),
        (saj_errors.UnknownModelError("gamma"), ConfigEntryError),
        (ValueError("invalid data"), ConfigEntryError),
        (ModbusError(ModbusErrorMessage.MISMATCHED_HEADER), ConfigEntryNotReady),
    ],
)
async def test_setup_closes_client_and_applies_translation_to_device_failure(
    monkeypatch, failure, expected_error
):
    hass = _hass()
    _patch_success(monkeypatch)

    async def fail(client, selection):
        raise failure

    def translate(error):
        assert error is failure
        return errors.Translation(key="stubbed", placeholders={"detail": "value"})

    monkeypatch.setattr(integration, "identify", fail)
    monkeypatch.setattr(integration, "translate_error", translate)
    entry = _entry()

    with pytest.raises(expected_error) as error:
        await integration.async_setup_entry(hass, entry)
    assert type(error.value) is expected_error
    assert error.value.translation_domain == DOMAIN
    assert error.value.translation_key == "stubbed"
    assert error.value.translation_placeholders == {"detail": "value"}
    assert error.value.__cause__ is failure
    assert FakeClient.instances[0].closed


async def test_setup_rejects_replacement_serial_and_closes_client(monkeypatch, issues):
    hass = _hass()
    _patch_success(monkeypatch)

    async def other_identity(client, selection):
        return Device("OTHER-SERIAL", 0x1610, 12000, PROFILE, detected=True)

    monkeypatch.setattr(integration, "identify", other_identity)
    entry = _entry()

    with pytest.raises(ConfigEntryError):
        await integration.async_setup_entry(hass, entry)
    assert FakeClient.instances[0].closed
    assert FakeCoordinator.instances == []
    assert issues.called("raise_identity_issue") == [
        {"hass": hass, "entry": entry, "serial": "OTHER-SERIAL"}
    ]
    assert issues.called("clear_model_issues") == []


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

    async def cancelled(client, selection):
        raise asyncio.CancelledError

    monkeypatch.setattr(integration, "identify", cancelled)
    entry = _entry()

    with pytest.raises(asyncio.CancelledError):
        await integration.async_setup_entry(hass, entry)
    assert FakeClient.instances[0].closed


async def test_setup_closes_client_on_unexpected_exception(monkeypatch):
    hass = _hass()
    _patch_success(monkeypatch)

    async def crash(client, selection):
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
    entry.runtime_data = SajRuntimeData(client, DEVICE, coordinator, {}, PACKS)

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


def _guard(hass, host="inverter", port=502):
    return endpoint_guard(hass=hass, host=host, port=port)


async def test_load_inside_the_back_off_is_not_ready_and_sends_nothing(monkeypatch):
    hass = _hass()
    _patch_success(monkeypatch)
    _guard(hass).failed(now=NOW - 5, base_delay=30)

    with pytest.raises(ConfigEntryNotReady) as error:
        await integration.async_setup_entry(hass, _entry())

    assert error.value.translation_domain == DOMAIN
    assert error.value.translation_key == "backing_off"
    assert FakeClient.instances == []
    assert FakeCoordinator.instances == []


async def test_load_after_the_back_off_proceeds(monkeypatch):
    hass = _hass()
    _patch_success(monkeypatch)
    _guard(hass).failed(now=NOW - 30, base_delay=30)

    assert await integration.async_setup_entry(hass, _entry())


@pytest.mark.parametrize(
    ("options", "groups", "expected_base"),
    [
        ({}, [], 60),
        ({"scan_interval": 45}, [], 45),
        ({"scan_interval": 45}, [20, 90], 20),
        ({"scan_interval": 15}, [20], 15),
    ],
)
async def test_a_failed_load_counts_as_a_failure_from_the_shortest_interval(
    monkeypatch, options, groups, expected_base
):
    hass = _hass()
    _patch_success(monkeypatch)

    async def fail(client, selection):
        raise ModbusError(ModbusErrorMessage.CONNECTION_FAILED)

    monkeypatch.setattr(integration, "identify", fail)
    entry = _entry()
    entry.options = options
    entry.subentries = {
        f"g{index}": SimpleNamespace(
            subentry_type="polling_group",
            data={"scan_interval": interval, "keys": ["pv_power"]},
        )
        for index, interval in enumerate(groups)
    }

    with pytest.raises(ConfigEntryNotReady):
        await integration.async_setup_entry(hass, entry)

    guard = _guard(hass)
    assert guard.consecutive_failures == 1
    assert guard.backoff_delay == expected_base
    assert guard.retry_in(now=NOW) == expected_base


async def test_a_configuration_failure_does_not_count_against_the_endpoint(
    monkeypatch, issues
):
    hass = _hass()
    _patch_success(monkeypatch)

    async def fail(client, selection):
        raise ValueError

    monkeypatch.setattr(integration, "identify", fail)

    with pytest.raises(ConfigEntryError):
        await integration.async_setup_entry(hass, _entry())

    assert _guard(hass).consecutive_failures == 0
    assert issues.called("raise_model_issue") == []


async def test_every_load_of_an_endpoint_reuses_its_guard_and_budget(monkeypatch):
    hass = _hass()
    _patch_success(monkeypatch)
    first, second = _entry(), _entry()

    assert await integration.async_setup_entry(hass, first)
    assert await integration.async_setup_entry(hass, second)

    guard = _guard(hass)
    assert [client.environment.budget for client in FakeClient.instances] == [
        guard.budget,
        guard.budget,
    ]
    assert [c.entry for c in FakeCoordinator.instances] == [first, second]
    assert hass.data[DOMAIN] == {("inverter", 502): guard}


async def test_different_endpoints_have_separate_guards(monkeypatch):
    hass = _hass()
    _patch_success(monkeypatch)
    _guard(hass, "inverter-a").failed(now=NOW, base_delay=30)

    assert await integration.async_setup_entry(hass, _entry("inverter-b"))
    with pytest.raises(ConfigEntryNotReady):
        await integration.async_setup_entry(hass, _entry("inverter-a"))

    assert _guard(hass, "inverter-b").consecutive_failures == 0
    assert _guard(hass, "inverter-b").budget is not _guard(hass, "inverter-a").budget
    assert _guard(hass, "INVERTER-A") is _guard(hass, "inverter-a")
    assert _guard(hass, "inverter-a", 503) is not _guard(hass, "inverter-a")


@pytest.mark.parametrize("allowed", [True, False])
async def test_the_library_control_is_built_with_the_entry_option(
    monkeypatch, *, allowed
):
    hass = _hass()
    _patch_success(monkeypatch)
    entry = _entry()
    entry.options = {"allow_control": allowed}

    assert await integration.async_setup_entry(hass, entry)

    installation = FakeCoordinator.instances[0].installation
    assert installation.control._enabled is allowed
    assert installation.control._link is installation.client
    assert installation.control._clock() == NOW


async def test_control_is_off_when_the_entry_never_saved_the_option(monkeypatch):
    hass = _hass()
    _patch_success(monkeypatch)

    assert await integration.async_setup_entry(hass, _entry())

    assert FakeCoordinator.instances[0].installation.control._enabled is False


async def test_ems_is_released_when_home_assistant_stops_and_the_listener_is_removed(
    monkeypatch,
):
    hass = _hass()
    _patch_success(monkeypatch)
    entry = _entry()
    assert await integration.async_setup_entry(hass, entry)
    ((event_type, listener), _) = hass.bus.listeners

    await listener(None)

    assert event_type == "homeassistant_stop"
    assert FakeCoordinator.instances[0].released == 1
    for callback in entry.unload_callbacks:
        callback()
    assert hass.bus.removed == 2


async def test_the_battery_store_is_saved_when_home_assistant_stops(
    monkeypatch,
):
    hass = _hass()
    _patch_success(monkeypatch)
    entry = _entry()
    assert await integration.async_setup_entry(hass, entry)
    (_, (event_type, listener)) = hass.bus.listeners

    await listener(None)

    assert event_type == "homeassistant_stop"
    assert FakeCoordinator.instances[0].battery_saves == 1
    assert FakeCoordinator.instances[0].released == 0


async def test_ems_is_released_before_the_coordinator_shuts_down_on_unload(
    monkeypatch,
):
    hass = _hass()
    _patch_success(monkeypatch)
    entry = _entry()
    assert await integration.async_setup_entry(hass, entry)

    assert await integration.async_unload_entry(hass, entry)

    assert FakeCoordinator.instances[0].events == ["release", "shutdown"]


async def test_nothing_is_released_when_the_platforms_fail_to_unload(monkeypatch):
    hass = _hass()
    entry = _entry()
    coordinator = FakeCoordinator()
    entry.runtime_data = SajRuntimeData(FakeClient(), DEVICE, coordinator, {}, PACKS)

    async def fail_unload(_entry, _platforms):
        return False

    monkeypatch.setattr(hass.config_entries, "async_unload_platforms", fail_unload)
    assert not await integration.async_unload_entry(hass, entry)

    assert coordinator.released == 0


async def test_the_device_with_its_fitted_equipment_is_what_the_installation_uses(
    monkeypatch,
):
    hass = _hass()
    _patch_success(monkeypatch)
    entry = _entry()
    settled = replace(DEVICE, equipment=frozenset({Equipment.BATTERY}))
    reports = {Equipment.BATTERY: "report"}
    packs = PackReport(count_read=2, limit=2)
    seen = []

    async def settle_equipment(*, hass, entry, client, device):
        seen.append((hass, entry, client, device))
        return settled, reports, packs

    monkeypatch.setattr(integration, "settle_equipment", settle_equipment)

    assert await integration.async_setup_entry(hass, entry)

    assert seen == [(hass, entry, FakeClient.instances[0], DEVICE)]
    assert FakeCoordinator.instances[0].installation.device is settled
    assert entry.runtime_data.device is settled
    assert entry.runtime_data.equipment is reports
    assert entry.runtime_data.packs is packs


@pytest.mark.parametrize(
    ("failure", "expected_error"),
    [
        (ModbusError(ModbusErrorMessage.REQUEST_TIMEOUT), ConfigEntryNotReady),
        (ValueError("bad"), ConfigEntryError),
    ],
)
async def test_a_failed_detection_fails_setup_like_any_other_read(
    monkeypatch, failure, expected_error
):
    hass = _hass()
    _patch_success(monkeypatch)

    async def settle_equipment(*, hass, entry, client, device):
        raise failure

    monkeypatch.setattr(integration, "settle_equipment", settle_equipment)
    monkeypatch.setattr(
        integration,
        "translate_error",
        lambda **_: errors.Translation(key="stubbed", placeholders={}),
    )

    with pytest.raises(expected_error):
        await integration.async_setup_entry(hass, _entry())

    assert FakeClient.instances[0].closed
    assert FakeCoordinator.instances == []


class FakeStore:
    removed = 0

    async def async_remove(self) -> None:
        FakeStore.removed += 1


async def test_removing_the_installation_removes_its_repair_issues_and_stored_state(
    monkeypatch,
):
    hass = _hass()
    entry = _entry()
    removed = []
    asked = []
    FakeStore.removed = 0
    monkeypatch.setattr(
        integration,
        "remove_issues",
        lambda *, hass, entry: removed.append((hass, entry)),
    )
    for store in ("power_control_store", "battery_store"):
        monkeypatch.setattr(
            integration,
            store,
            lambda *, name=store, **asked_for: (
                asked.append((name, asked_for)) or FakeStore()
            ),
        )

    await integration.async_remove_entry(hass, entry)

    assert removed == [(hass, entry)]
    assert asked == [
        ("power_control_store", {"hass": hass, "entry_id": entry.entry_id}),
        ("battery_store", {"hass": hass, "entry_id": entry.entry_id}),
    ]
    assert FakeStore.removed == 2


async def test_stored_state_loads_before_the_first_refresh_and_schedules_follow_up(
    monkeypatch,
):
    hass = _hass()
    _patch_success(monkeypatch)
    forwarded = []

    async def forward(_entry, _platforms):
        forwarded.append(list(FakeCoordinator.instances[0].setup_events))

    monkeypatch.setattr(hass.config_entries, "async_forward_entry_setups", forward)

    assert await integration.async_setup_entry(hass, _entry())

    assert forwarded == [["load", "refresh"]]
    assert FakeCoordinator.instances[0].setup_events == ["load", "refresh", "follow"]


async def test_every_load_attempt_checks_whether_the_endpoint_has_been_down_too_long(
    monkeypatch, issues
):
    hass = _hass()
    _patch_success(monkeypatch)
    guard = _guard(hass)
    guard.failed(now=NOW - 5, base_delay=30)
    entry = _entry()

    with pytest.raises(ConfigEntryNotReady):
        await integration.async_setup_entry(hass, entry)

    assert issues.calls == [
        (
            "check_unreachable",
            {"hass": hass, "entry": entry, "guard": guard, "now": NOW},
        )
    ]


async def test_a_load_that_fails_to_connect_checks_the_endpoint_after_recording_it(
    monkeypatch, issues
):
    hass = _hass()
    _patch_success(monkeypatch)

    async def fail(client, selection):
        raise ModbusError(ModbusErrorMessage.CONNECTION_FAILED)

    monkeypatch.setattr(integration, "identify", fail)

    with pytest.raises(ConfigEntryNotReady):
        await integration.async_setup_entry(hass, _entry())

    assert [name for name, _ in issues.calls] == [
        "check_unreachable",
        "check_unreachable",
    ]
    assert _guard(hass).consecutive_failures == 1


async def test_a_model_error_at_load_raises_the_model_issue_it_is_found_to_be(
    monkeypatch, issues
):
    hass = _hass()
    _patch_success(monkeypatch)
    failure = saj_errors.UnsupportedDeviceError(0x1234)
    issues.finding = "finding"

    async def fail(client, selection):
        raise failure

    monkeypatch.setattr(integration, "identify", fail)
    entry = _entry()

    with pytest.raises(ConfigEntryError):
        await integration.async_setup_entry(hass, entry)

    assert issues.called("raise_model_issue") == [
        {"hass": hass, "entry": entry, "finding": "finding"}
    ]


async def test_a_load_that_identifies_the_configured_device_clears_the_model_issues(
    monkeypatch, issues
):
    hass = _hass()
    _patch_success(monkeypatch)
    entry = _entry()

    assert await integration.async_setup_entry(hass, entry)

    assert (
        "clear_model_issues",
        {"hass": hass, "entry": entry},
    ) in issues.calls


@pytest.mark.parametrize("allowed", [True, False])
async def test_setup_applies_the_control_set_once_the_platforms_are_set_up(
    monkeypatch, controls, allowed
):
    hass = _hass()
    _patch_success(monkeypatch)
    entry = _entry()
    events = []

    async def forward(_entry, _platforms):
        events.append("platforms")

    def apply(**kwargs):
        events.append("apply")
        controls.apply(**kwargs)

    class AllowingCoordinator(FakeCoordinator):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.control_allowed = allowed

    monkeypatch.setattr(hass.config_entries, "async_forward_entry_setups", forward)
    monkeypatch.setattr(integration, "apply_control_set", apply)
    monkeypatch.setattr(integration, "SajCoordinator", AllowingCoordinator)

    assert await integration.async_setup_entry(hass, entry)

    assert events == ["platforms", "apply"]
    assert controls.applied == [
        {"hass": hass, "entry": entry, "fit": DEVICE.fit, "allowed": allowed}
    ]


async def test_setup_starts_the_registry_listener_and_removes_it_on_unload(
    monkeypatch, controls
):
    hass = _hass()
    _patch_success(monkeypatch)
    entry = _entry()

    assert await integration.async_setup_entry(hass, entry)

    assert controls.order == ["apply", "listen"]
    assert controls.listening == [{"hass": hass, "entry": entry}]
    for callback in entry.unload_callbacks:
        callback()
    assert controls.stopped == 1


async def test_a_failed_platform_setup_applies_no_control_set(monkeypatch, controls):
    hass = _hass()
    _patch_success(monkeypatch)

    async def fail(_entry, _platforms):
        raise RuntimeError

    monkeypatch.setattr(hass.config_entries, "async_forward_entry_setups", fail)

    with pytest.raises(RuntimeError):
        await integration.async_setup_entry(hass, _entry())

    assert controls.order == []


async def test_integration_setup_registers_the_cards_bundle_once(monkeypatch):
    registered = []

    async def register(*, hass):
        registered.append(hass)

    monkeypatch.setattr(integration, "async_register_frontend", register)
    hass = _hass()

    assert await integration.async_setup(hass, {})
    assert registered == [hass]
