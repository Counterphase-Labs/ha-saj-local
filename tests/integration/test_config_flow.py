from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from enum import StrEnum
from types import SimpleNamespace
from typing import TYPE_CHECKING, ClassVar

import pytest

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

from custom_components.saj_local import config_flow
from custom_components.saj_local.saj.client import ModbusError, ModbusErrorMessage
from custom_components.saj_local.saj.hs3 import (
    Hs3Device,
    Hs3Telemetry,
    UnsupportedDeviceError,
)

SERIAL = "HS3-TEST-001"
INPUT = {"host": "inverter", "port": 502, "unit_id": 1, "scan_interval": 30}


class FlowAbortError(Exception):
    pass


class FakeValidationSession:
    def __init__(self) -> None:
        self.lock = asyncio.Lock()
        self.requested = asyncio.Event()
        self.active = False
        self.calls = 0
        self.events: list[str] = []

    def async_validation_session(self):
        self.calls += 1
        self.requested.set()
        return self._session()

    @asynccontextmanager
    async def _session(self) -> AsyncIterator[None]:
        await self.lock.acquire()
        self.active = True
        self.events.append("session_enter")
        try:
            yield
        finally:
            self.events.append("session_exit")
            self.active = False
            self.lock.release()


class FlowClient:
    instances: ClassVar[list[FlowClient]] = []
    validation_session: ClassVar[FakeValidationSession | None] = None

    def __init__(self, **kwargs) -> None:
        self.parameters = kwargs
        self.closed = False
        self.instances.append(self)
        if self.validation_session is not None:
            self.validation_session.events.append("client_create")
            self.created_inside_session = self.validation_session.active

    async def close(self) -> None:
        self.closed = True
        if self.validation_session is not None:
            self.validation_session.events.append("client_close")
            self.closed_inside_session = self.validation_session.active


class FakeNumberSelector:
    def __init__(self, config) -> None:
        self.config = config

    def __call__(self, value):
        return value


class FakeNumberSelectorMode(StrEnum):
    BOX = "box"


class FakeConfigEntries:
    def __init__(self, entries=()) -> None:
        self.entries = list(entries)

    def async_entries(self, _domain):
        return self.entries

    def async_update_entry(self, entry, **changes):
        entry.data = changes["data"]
        entry.options = changes["options"]
        entry.unique_id = changes["unique_id"]
        entry.update_count = getattr(entry, "update_count", 0) + 1
        return True


async def _identify(client) -> Hs3Device:
    del client
    return Hs3Device(SERIAL, 0x1610, 12000)


async def _telemetry(client) -> Hs3Telemetry:
    del client
    return Hs3Telemetry()


async def _identify_replacement(client) -> Hs3Device:
    del client
    return Hs3Device("HS3-REPLACEMENT", 0x1610, 15000)


@pytest.fixture(autouse=True)
def reset_flow_client_instances(monkeypatch):
    FlowClient.instances.clear()
    FlowClient.validation_session = None
    monkeypatch.setattr(config_flow.selector, "NumberSelector", FakeNumberSelector)
    monkeypatch.setattr(
        config_flow.selector, "NumberSelectorMode", FakeNumberSelectorMode
    )


def _flow(monkeypatch, *, entries=()):
    instance = object.__new__(config_flow.SajLocalConfigFlow)
    instance.hass = SimpleNamespace(config_entries=FakeConfigEntries(entries))
    monkeypatch.setattr(config_flow, "ModbusTcpClient", FlowClient)
    monkeypatch.setattr(config_flow, "identify", _identify)
    monkeypatch.setattr(config_flow, "read_telemetry", _telemetry)
    monkeypatch.setattr(
        instance,
        "async_show_form",
        lambda *, step_id, data_schema, errors: {
            "type": "form",
            "step_id": step_id,
            "data_schema": data_schema,
            "errors": errors,
        },
    )
    monkeypatch.setattr(
        instance,
        "async_set_unique_id",
        lambda unique_id: _set_unique_id(instance, unique_id),
    )
    monkeypatch.setattr(instance, "_abort_if_unique_id_configured", lambda: None)
    monkeypatch.setattr(
        instance,
        "async_create_entry",
        lambda *, title, data, options: {
            "type": "create_entry",
            "title": title,
            "data": data,
            "options": options,
        },
    )
    return instance


async def _set_unique_id(instance, unique_id: str) -> None:
    instance.selected_unique_id = unique_id


async def test_user_step_shows_endpoint_form_and_defaults(monkeypatch):
    instance = _flow(monkeypatch)

    result = await instance.async_step_user()

    assert result["type"] == "form"
    assert result["step_id"] == "user"
    assert result["data_schema"]({"host": "inverter"}) == INPUT
    assert result["errors"] == {}


async def test_user_step_validates_endpoint_and_creates_serial_identity(monkeypatch):
    instance = _flow(monkeypatch)
    submitted = {**INPUT, "unit_id": 5.0}

    result = await instance.async_step_user(submitted)

    assert result == {
        "type": "create_entry",
        "title": f"SAJ {SERIAL}",
        "data": {"host": "inverter", "port": 502, "unit_id": 5},
        "options": {"scan_interval": 30},
    }
    assert instance.selected_unique_id == SERIAL
    assert FlowClient.instances[0].parameters == {
        "host": "inverter",
        "port": 502,
        "unit_id": 5,
        "timeout": config_flow.REQUEST_TIMEOUT,
    }
    assert FlowClient.instances[0].closed


async def test_user_step_rejects_duplicate_endpoint_before_connecting(monkeypatch):
    entry = SimpleNamespace(data={"host": "INVERTER", "port": 502, "unit_id": 1})
    instance = _flow(monkeypatch, entries=[entry])

    result = await instance.async_step_user(INPUT)

    assert result["errors"] == {"base": "already_configured"}
    assert FlowClient.instances == []


async def test_user_step_rechecks_endpoint_after_validation_before_create(monkeypatch):
    other = SimpleNamespace(
        entry_id="entry-b",
        unique_id="HS3-OTHER",
        data={"host": "other", "port": 502, "unit_id": 1},
    )
    instance = _flow(monkeypatch, entries=[other])

    async def identify_and_claim_endpoint(client):
        del client
        other.data = {"host": "inverter", "port": 502, "unit_id": 1}
        return Hs3Device("HS3-DIFFERENT-SERIAL", 0x1610, 12000)

    monkeypatch.setattr(config_flow, "identify", identify_and_claim_endpoint)
    result = await instance.async_step_user(INPUT)

    assert result["type"] == "form"
    assert result["errors"] == {"base": "already_configured"}
    assert FlowClient.instances[-1].closed
    assert not hasattr(instance, "selected_unique_id")


async def test_user_step_rejects_empty_host(monkeypatch):
    instance = _flow(monkeypatch)

    result = await instance.async_step_user({**INPUT, "host": "   "})

    assert result["errors"] == {"base": "invalid_host"}
    assert FlowClient.instances == []


@pytest.mark.parametrize("unit_id", [0, 1.5, 248])
async def test_user_step_rejects_invalid_unit_id(monkeypatch, unit_id):
    instance = _flow(monkeypatch)

    result = await instance.async_step_user({**INPUT, "unit_id": unit_id})

    assert result["errors"] == {"base": "invalid_unit_id"}
    assert FlowClient.instances == []


async def test_endpoint_schema_uses_box_number_selector_with_integer_range(monkeypatch):
    instance = _flow(monkeypatch)
    result = await instance.async_step_user()
    schema = result["data_schema"]
    unit_marker = next(
        key for key in schema.schema if getattr(key, "schema", None) == "unit_id"
    )
    port_marker = next(
        key for key in schema.schema if getattr(key, "schema", None) == "port"
    )
    interval_marker = next(
        key for key in schema.schema if getattr(key, "schema", None) == "scan_interval"
    )
    unit_selector = schema.schema[unit_marker]

    assert isinstance(unit_selector, FakeNumberSelector)
    assert unit_selector.config == {
        "min": 1.0,
        "max": 247.0,
        "step": 1.0,
        "mode": "box",
    }
    assert schema.schema[port_marker].config == {
        "min": 1,
        "step": 1,
        "mode": "box",
        "max": 65535,
    }
    assert schema.schema[interval_marker].config == {
        "min": 30,
        "step": 1,
        "mode": "box",
    }
    assert unit_marker.default() == 1
    assert port_marker.default() == 502
    assert type(schema({"host": "inverter"})["port"]) is int
    assert schema({"host": "inverter", "unit_id": 247})["unit_id"] == 247


async def test_user_step_aborts_duplicate_serial_after_validation(monkeypatch):
    instance = _flow(monkeypatch)

    def abort_duplicate():
        raise FlowAbortError

    monkeypatch.setattr(instance, "_abort_if_unique_id_configured", abort_duplicate)
    with pytest.raises(FlowAbortError):
        await instance.async_step_user(INPUT)

    assert instance.selected_unique_id == SERIAL
    assert FlowClient.instances[-1].closed


@pytest.mark.parametrize(
    ("error", "reason"),
    [
        (UnsupportedDeviceError("unsupported"), "unsupported_device"),
        (ValueError("bad identity"), "invalid_device_data"),
        (ModbusError("communication error"), "cannot_connect"),
        (ModbusError("Connection timed out"), "timeout"),
        (ModbusError("Modbus exception response", exception_code=6), "read_rejected"),
    ],
)
async def test_user_step_reports_classified_validation_failure(
    monkeypatch, error, reason
):
    instance = _flow(monkeypatch)

    async def fail_identify(client):
        del client
        raise error

    monkeypatch.setattr(config_flow, "identify", fail_identify)
    result = await instance.async_step_user(INPUT)

    assert result["errors"] == {"base": reason}
    assert FlowClient.instances[-1].closed


async def test_options_step_uses_default_and_stores_interval(monkeypatch):
    entry = _saved_entry()
    entry.options = {}
    instance = _options_flow(monkeypatch, entry=entry)

    form = await instance.async_step_init()
    assert form["data_schema"]({"scan_interval": 30}) == {
        "host": "inverter",
        "port": 502,
        "unit_id": 1,
        "scan_interval": 30,
    }
    assert await instance.async_step_init(
        {"host": "inverter", "port": 502, "unit_id": 1, "scan_interval": 60}
    ) == {"type": "abort", "reason": "changes_saved"}
    assert entry.options == {"scan_interval": 60}
    assert entry.update_count == 1


def _options_flow(monkeypatch, *, entry, entries=None):
    instance = object.__new__(config_flow.SajOptionsFlow)
    instance.hass = SimpleNamespace(
        config_entries=FakeConfigEntries(entries if entries is not None else [entry])
    )
    monkeypatch.setattr(
        config_flow.SajOptionsFlow,
        "config_entry",
        property(lambda _instance: entry),
    )
    monkeypatch.setattr(config_flow, "ModbusTcpClient", FlowClient)
    monkeypatch.setattr(config_flow, "identify", _identify)
    monkeypatch.setattr(config_flow, "read_telemetry", _telemetry)
    monkeypatch.setattr(
        instance,
        "async_show_form",
        lambda *, step_id, data_schema, **kwargs: {
            "type": "form",
            "step_id": step_id,
            "data_schema": data_schema,
            **kwargs,
        },
    )
    monkeypatch.setattr(
        instance, "async_abort", lambda *, reason: {"type": "abort", "reason": reason}
    )
    return instance


def _saved_entry(*, entry_id="entry-a", serial=SERIAL):
    return SimpleNamespace(
        entry_id=entry_id,
        unique_id=serial,
        title=f"SAJ {serial}",
        data={"host": "inverter", "port": 502, "unit_id": 1},
        options={"scan_interval": 45},
        update_count=0,
    )


async def test_options_form_prefills_connection_and_cadence_as_numeric_boxes(
    monkeypatch,
):
    entry = _saved_entry()
    flow = _options_flow(monkeypatch, entry=entry)

    form = await flow.async_step_init()
    validated = form["data_schema"](
        {
            "host": "inverter",
            "port": 502,
            "unit_id": 1,
            "scan_interval": 45,
        }
    )
    markers = {marker.schema: marker for marker in form["data_schema"].schema}

    assert set(markers) == {"host", "port", "unit_id", "scan_interval"}
    assert validated["scan_interval"] == 45
    assert markers["port"].default() == 502
    assert markers["unit_id"].default() == 1
    assert markers["scan_interval"].default() == 45
    assert form["data_schema"].schema[markers["unit_id"]].config["mode"] == "box"
    assert form["data_schema"].schema[markers["scan_interval"]].config["mode"] == "box"


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"port": "invalid"}, "invalid_endpoint"),
        ({"port": 1.5}, "invalid_port"),
        ({"port": 0}, "invalid_port"),
        ({"unit_id": "invalid"}, "invalid_endpoint"),
        ({"unit_id": 1.5}, "invalid_unit_id"),
        ({"scan_interval": "invalid"}, "invalid_scan_interval"),
        ({"scan_interval": 30.5}, "invalid_scan_interval"),
        ({"scan_interval": 29}, "invalid_scan_interval"),
    ],
)
async def test_options_step_rejects_invalid_numeric_fields(
    monkeypatch, changes, reason
):
    entry = _saved_entry()
    flow = _options_flow(monkeypatch, entry=entry)
    submitted = {
        "host": "inverter",
        "port": 502,
        "unit_id": 1,
        "scan_interval": 45,
        **changes,
    }

    result = await flow.async_step_init(submitted)

    assert result["errors"] == {"base": reason}
    assert entry.data == {"host": "inverter", "port": 502, "unit_id": 1}
    assert entry.options == {"scan_interval": 45}
    assert entry.update_count == 0
    assert FlowClient.instances == []


async def test_interval_only_edit_validates_endpoint_before_saving(monkeypatch):
    entry = _saved_entry()
    original_data = dict(entry.data)
    flow = _options_flow(monkeypatch, entry=entry)

    result = await flow.async_step_init(
        {"host": "inverter", "port": 502, "unit_id": 1, "scan_interval": 90}
    )

    assert result == {"type": "abort", "reason": "changes_saved"}
    assert entry.data == original_data
    assert entry.options == {"scan_interval": 90}
    assert entry.unique_id == SERIAL
    assert entry.update_count == 1
    assert len(FlowClient.instances) == 1
    assert FlowClient.instances[0].closed


async def test_unchanged_endpoint_and_interval_validates_and_saves_once(monkeypatch):
    entry = _saved_entry()
    flow = _options_flow(monkeypatch, entry=entry)

    result = await flow.async_step_init(
        {"host": "inverter", "port": 502, "unit_id": 1, "scan_interval": 45}
    )

    assert result == {"type": "abort", "reason": "changes_saved"}
    assert entry.data == {"host": "inverter", "port": 502, "unit_id": 1}
    assert entry.options == {"scan_interval": 45}
    assert entry.unique_id == SERIAL
    assert entry.update_count == 1
    assert len(FlowClient.instances) == 1
    assert FlowClient.instances[0].closed


async def test_connection_edit_validates_same_serial_and_keeps_entry_identity(
    monkeypatch,
):
    entry = _saved_entry()
    flow = _options_flow(monkeypatch, entry=entry)
    result = await flow.async_step_init(
        {"host": "new-inverter", "port": 502, "unit_id": 1, "scan_interval": 60}
    )

    assert result == {"type": "abort", "reason": "changes_saved"}
    assert FlowClient.instances[0].parameters["host"] == "new-inverter"
    assert FlowClient.instances[0].closed
    assert entry.entry_id == "entry-a"
    assert entry.data == {"host": "new-inverter", "port": 502, "unit_id": 1}
    assert entry.options == {"scan_interval": 60}
    assert entry.unique_id == SERIAL
    assert entry.update_count == 1


def _options_flow_with_validation_session(monkeypatch):
    entry = _saved_entry()
    session = FakeValidationSession()
    entry.runtime_data = SimpleNamespace(coordinator=session)
    FlowClient.validation_session = session
    return entry, session, _options_flow(monkeypatch, entry=entry)


async def test_same_endpoint_validation_uses_session_through_client_cleanup(
    monkeypatch,
):
    entry, session, flow = _options_flow_with_validation_session(monkeypatch)

    async def identify(client):
        del client
        assert session.active
        session.events.append("identify")
        return Hs3Device(SERIAL, 0x1610, 12000)

    async def read(client):
        del client
        assert session.active
        session.events.append("telemetry")
        return Hs3Telemetry()

    monkeypatch.setattr(config_flow, "identify", identify)
    monkeypatch.setattr(config_flow, "read_telemetry", read)

    await session.lock.acquire()
    validation = asyncio.create_task(
        flow.async_step_init(
            {
                "host": "INVERTER",
                "port": 502,
                "unit_id": 1,
                "scan_interval": 60,
            }
        )
    )
    await session.requested.wait()
    assert FlowClient.instances == []
    assert not session.active
    session.lock.release()
    result = await validation

    assert result == {"type": "abort", "reason": "changes_saved"}
    assert FlowClient.instances[-1].closed
    assert FlowClient.instances[-1].created_inside_session
    assert FlowClient.instances[-1].closed_inside_session
    assert session.events == [
        "session_enter",
        "client_create",
        "identify",
        "telemetry",
        "client_close",
        "session_exit",
    ]
    assert not session.active
    assert entry.update_count == 1


async def test_different_endpoint_validation_bypasses_session_while_poll_is_active(
    monkeypatch,
):
    entry, session, flow = _options_flow_with_validation_session(monkeypatch)
    probe_started = asyncio.Event()

    async def identify(client):
        del client
        probe_started.set()
        return Hs3Device(SERIAL, 0x1610, 12000)

    monkeypatch.setattr(config_flow, "identify", identify)

    await session.lock.acquire()
    validation = asyncio.create_task(
        flow.async_step_init(
            {
                "host": "new-inverter",
                "port": 502,
                "unit_id": 1,
                "scan_interval": 60,
            }
        )
    )
    await probe_started.wait()
    result = await validation
    assert session.lock.locked()
    session.lock.release()

    assert result == {"type": "abort", "reason": "changes_saved"}
    assert FlowClient.instances[-1].closed
    assert not FlowClient.instances[-1].created_inside_session
    assert not FlowClient.instances[-1].closed_inside_session
    assert session.calls == 0
    assert entry.data["host"] == "new-inverter"


async def test_same_endpoint_validation_without_runtime_uses_owned_client(monkeypatch):
    entry = _saved_entry()
    flow = _options_flow(monkeypatch, entry=entry)

    result = await flow.async_step_init(
        {
            "host": "inverter",
            "port": 502,
            "unit_id": 1,
            "scan_interval": 60,
        }
    )

    assert result == {"type": "abort", "reason": "changes_saved"}
    assert FlowClient.instances[-1].closed
    assert entry.update_count == 1


@pytest.mark.parametrize(
    ("new_host", "new_port"), [("inverter", 502), ("new-inverter", 502)]
)
async def test_different_serial_requires_confirmation_before_any_saved_change(
    monkeypatch, new_host, new_port
):
    entry = _saved_entry()
    original_data = dict(entry.data)
    original_options = dict(entry.options)
    flow = _options_flow(monkeypatch, entry=entry)

    monkeypatch.setattr(config_flow, "identify", _identify_replacement)
    form = await flow.async_step_init(
        {
            "host": new_host,
            "port": new_port,
            "unit_id": 1,
            "scan_interval": 75,
        }
    )

    assert form["step_id"] == "confirm_replacement"
    assert form["description_placeholders"] == {"serial": "HS3-REPLACEMENT"}
    assert entry.data == original_data
    assert entry.options == original_options
    assert entry.unique_id == SERIAL
    assert entry.update_count == 0
    assert FlowClient.instances[-1].closed


async def test_duplicate_serial_is_rejected_before_replacement_confirmation(
    monkeypatch,
):
    entry = _saved_entry()
    other = _saved_entry(entry_id="entry-b", serial="HS3-REPLACEMENT")
    flow = _options_flow(monkeypatch, entry=entry, entries=[entry, other])
    monkeypatch.setattr(config_flow, "identify", _identify_replacement)

    result = await flow.async_step_init(
        {
            "host": "new-inverter",
            "port": 502,
            "unit_id": 1,
            "scan_interval": 60,
        }
    )

    assert result["errors"] == {"base": "already_configured"}
    assert entry.unique_id == SERIAL
    assert entry.data == {"host": "inverter", "port": 502, "unit_id": 1}
    assert entry.options == {"scan_interval": 45}
    assert entry.update_count == 0


async def test_confirmation_prompt_and_missing_pending_replacement(monkeypatch):
    entry = _saved_entry()
    flow = _options_flow(monkeypatch, entry=entry)

    prompt = await flow.async_step_confirm_replacement()
    aborted = await flow.async_step_confirm_replacement({})

    assert prompt["step_id"] == "confirm_replacement"
    assert prompt["description_placeholders"] == {"serial": ""}
    assert aborted == {"type": "abort", "reason": "replacement_not_pending"}
    assert entry.update_count == 0


async def test_confirmed_replacement_updates_serial_and_connection_once(monkeypatch):
    entry = _saved_entry()
    flow = _options_flow(monkeypatch, entry=entry)
    monkeypatch.setattr(config_flow, "identify", _identify_replacement)
    await flow.async_step_init(
        {
            "host": "new-inverter",
            "port": 1502,
            "unit_id": 2,
            "scan_interval": 75,
        }
    )

    result = await flow.async_step_confirm_replacement({})

    assert result == {"type": "abort", "reason": "changes_saved"}
    assert entry.entry_id == "entry-a"
    assert entry.unique_id == "HS3-REPLACEMENT"
    assert entry.title == f"SAJ {SERIAL}"
    assert entry.data == {"host": "new-inverter", "port": 1502, "unit_id": 2}
    assert entry.options == {"scan_interval": 75}
    assert entry.update_count == 1


@pytest.mark.parametrize("ownership_change", ["endpoint", "serial"])
async def test_replacement_rechecks_other_entry_ownership_before_saving(
    monkeypatch, ownership_change
):
    entry = _saved_entry()
    other = _saved_entry(entry_id="entry-b", serial="HS3-OTHER")
    flow = _options_flow(monkeypatch, entry=entry, entries=[entry, other])
    monkeypatch.setattr(config_flow, "identify", _identify_replacement)
    await flow.async_step_init(
        {
            "host": "new-inverter",
            "port": 1502,
            "unit_id": 2,
            "scan_interval": 75,
        }
    )
    if ownership_change == "endpoint":
        other.data = {"host": "new-inverter", "port": 1502, "unit_id": 2}
    else:
        other.unique_id = "HS3-REPLACEMENT"

    result = await flow.async_step_confirm_replacement({})

    assert result == {"type": "abort", "reason": "already_configured"}
    assert entry.unique_id == SERIAL
    assert entry.data == {"host": "inverter", "port": 502, "unit_id": 1}
    assert entry.options == {"scan_interval": 45}
    assert entry.update_count == 0


async def test_changed_endpoint_validation_failure_leaves_saved_state_unchanged(
    monkeypatch,
):
    entry = _saved_entry()
    flow = _options_flow(monkeypatch, entry=entry)

    async def reject(client):
        del client
        raise ModbusError(ModbusErrorMessage.CONNECTION_TIMEOUT)

    monkeypatch.setattr(config_flow, "identify", reject)
    result = await flow.async_step_init(
        {"host": "new-inverter", "port": 502, "unit_id": 1, "scan_interval": 60}
    )

    assert result["errors"] == {"base": "timeout"}
    assert entry.data == {"host": "inverter", "port": 502, "unit_id": 1}
    assert entry.options == {"scan_interval": 45}
    assert entry.unique_id == SERIAL
    assert entry.update_count == 0
    assert FlowClient.instances[-1].closed


async def test_changed_endpoint_rejects_other_entry_before_connecting(monkeypatch):
    entry = _saved_entry()
    other = _saved_entry(entry_id="entry-b", serial="HS3-OTHER")
    other.data = {"host": "new-inverter", "port": 502, "unit_id": 1}
    flow = _options_flow(monkeypatch, entry=entry, entries=[entry, other])

    result = await flow.async_step_init(
        {"host": "new-inverter", "port": 502, "unit_id": 1, "scan_interval": 60}
    )

    assert result["errors"] == {"base": "already_configured"}
    assert FlowClient.instances == []
    assert entry.update_count == 0


async def test_connection_edit_rechecks_endpoint_ownership_after_validation(
    monkeypatch,
):
    entry = _saved_entry()
    other = _saved_entry(entry_id="entry-b", serial="HS3-OTHER")
    flow = _options_flow(monkeypatch, entry=entry, entries=[entry, other])

    async def identify_and_claim_endpoint(client):
        del client
        other.data = {"host": "new-inverter", "port": 502, "unit_id": 1}
        return Hs3Device(SERIAL, 0x1610, 12000)

    monkeypatch.setattr(config_flow, "identify", identify_and_claim_endpoint)
    result = await flow.async_step_init(
        {"host": "new-inverter", "port": 502, "unit_id": 1, "scan_interval": 60}
    )

    assert result["errors"] == {"base": "already_configured"}
    assert FlowClient.instances[-1].closed
    assert entry.data == {"host": "inverter", "port": 502, "unit_id": 1}
    assert entry.options == {"scan_interval": 45}
    assert entry.unique_id == SERIAL
    assert entry.update_count == 0


async def test_cancelled_endpoint_validation_closes_temporary_client(monkeypatch):
    entry = _saved_entry()
    flow = _options_flow(monkeypatch, entry=entry)

    async def cancel(client):
        del client
        raise asyncio.CancelledError

    monkeypatch.setattr(config_flow, "identify", cancel)
    with pytest.raises(asyncio.CancelledError):
        await flow.async_step_init(
            {"host": "new-inverter", "port": 502, "unit_id": 1, "scan_interval": 60}
        )
    assert FlowClient.instances[-1].closed
    assert entry.update_count == 0


def test_options_flow_factory_returns_integration_flow():
    assert isinstance(
        config_flow.SajLocalConfigFlow.async_get_options_flow(None),
        config_flow.SajOptionsFlow,
    )
