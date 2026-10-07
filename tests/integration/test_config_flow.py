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
from custom_components.saj_local.errors import Translation
from custom_components.saj_local.saj import errors as saj_errors
from custom_components.saj_local.saj.client import ModbusError, ModbusErrorMessage
from custom_components.saj_local.saj.device import Device
from custom_components.saj_local.saj.profiles import Profile

SERIAL = "TEST-001"
REPLACEMENT_SERIAL = "TEST-REPLACEMENT"
UNRECOGNISED_TYPE = 0x7777
ALPHA = Profile(
    key="alpha",
    display_name="Alpha",
    device_types=frozenset({0x0001}),
    measurement_keys=frozenset(),
    hand_verified=True,
)
BETA = Profile(
    key="beta",
    display_name="Beta",
    device_types=frozenset({0x0002}),
    measurement_keys=frozenset(),
    hand_verified=False,
)
INPUT = {
    "host": "inverter",
    "port": 502,
    "unit_id": 1,
    "scan_interval": 30,
    "model": "automatic",
}
SAVED_DATA = {"host": "inverter", "port": 502, "unit_id": 1, "model": "automatic"}


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


def _device(
    *,
    serial: str = SERIAL,
    profile: Profile = ALPHA,
    detected: bool = True,
    device_type: int = 0x0001,
) -> Device:
    return Device(serial, device_type, 12000, profile, detected=detected)


def _identifying(device: Device):
    async def identify(client, selection):
        del client
        identify.selections.append(selection)
        return device

    identify.selections = []
    return identify


def _failing_identify(error: BaseException):
    async def identify(client, selection):
        del client, selection
        raise error

    return identify


async def _telemetry(client, device) -> None:
    del client, device


@pytest.fixture(autouse=True)
def reset_flow_client_instances(monkeypatch):
    FlowClient.instances.clear()
    FlowClient.validation_session = None
    monkeypatch.setattr(config_flow.selector, "NumberSelector", FakeNumberSelector)
    monkeypatch.setattr(
        config_flow.selector, "NumberSelectorMode", FakeNumberSelectorMode
    )
    monkeypatch.setattr(config_flow, "PROFILES", (ALPHA, BETA))
    monkeypatch.setattr(config_flow, "ModbusTcpClient", FlowClient)
    monkeypatch.setattr(config_flow, "identify", _identifying(_device()))
    monkeypatch.setattr(config_flow, "read_telemetry", _telemetry)


def _form(**kwargs):
    return {"type": "form", **kwargs}


def _abort(*, reason):
    return {"type": "abort", "reason": reason}


def _flow(monkeypatch, *, entries=()):
    instance = object.__new__(config_flow.SajLocalConfigFlow)
    instance.hass = SimpleNamespace(config_entries=FakeConfigEntries(entries))
    monkeypatch.setattr(instance, "async_show_form", _form)
    monkeypatch.setattr(instance, "async_abort", _abort)
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


def _field_names(schema) -> list[str]:
    return [marker.schema for marker in schema.schema]


def _marker(schema, name: str):
    return next(marker for marker in schema.schema if marker.schema == name)


async def test_user_step_shows_the_five_fields_with_automatic_model_default(
    monkeypatch,
):
    instance = _flow(monkeypatch)

    result = await instance.async_step_user()

    assert result["step_id"] == "user"
    assert _field_names(result["data_schema"]) == [
        "host",
        "port",
        "unit_id",
        "scan_interval",
        "model",
    ]
    assert result["data_schema"]({"host": "inverter"}) == INPUT
    assert result["errors"] == {}


async def test_model_dropdown_offers_automatic_then_every_library_profile(
    monkeypatch,
):
    instance = _flow(monkeypatch)

    schema = (await instance.async_step_user())["data_schema"]
    model_selector = schema.schema[_marker(schema, "model")]

    assert model_selector.config["options"] == ["automatic", "alpha", "beta"]
    assert model_selector.config["mode"] == "dropdown"
    assert model_selector.config["translation_key"] == "model"


@pytest.mark.parametrize(("profile", "device_type"), [(ALPHA, 0x0001), (BETA, 0x0002)])
async def test_user_step_creates_entry_on_automatic_through_one_path(
    monkeypatch, profile, device_type
):
    instance = _flow(monkeypatch)
    identify = _identifying(_device(profile=profile, device_type=device_type))
    monkeypatch.setattr(config_flow, "identify", identify)
    submitted = {**INPUT, "unit_id": 5.0}

    result = await instance.async_step_user(submitted)

    assert result == {
        "type": "create_entry",
        "title": f"SAJ {SERIAL}",
        "data": {**SAVED_DATA, "unit_id": 5},
        "options": {"scan_interval": 30},
    }
    assert identify.selections == ["automatic"]
    assert instance.selected_unique_id == SERIAL
    assert FlowClient.instances[0].parameters == {
        "host": "inverter",
        "port": 502,
        "unit_id": 5,
        "timeout": config_flow.REQUEST_TIMEOUT,
    }
    assert FlowClient.instances[0].closed


async def test_user_step_stores_explicit_selection_and_never_the_detected_model(
    monkeypatch,
):
    instance = _flow(monkeypatch)
    identify = _identifying(_device(profile=BETA, device_type=0x0002))
    monkeypatch.setattr(config_flow, "identify", identify)

    result = await instance.async_step_user({**INPUT, "model": "beta"})

    assert result["data"]["model"] == "beta"
    assert set(result["data"]) == {"host", "port", "unit_id", "model"}
    assert identify.selections == ["beta"]


async def test_user_step_rejects_duplicate_endpoint_before_connecting(monkeypatch):
    entry = SimpleNamespace(data={"host": "INVERTER", "port": 502, "unit_id": 1})
    instance = _flow(monkeypatch, entries=[entry])

    result = await instance.async_step_user(INPUT)

    assert result["errors"] == {"base": "already_configured"}
    assert FlowClient.instances == []


async def test_user_step_rechecks_endpoint_after_validation_before_create(monkeypatch):
    other = SimpleNamespace(
        entry_id="entry-b",
        unique_id="OTHER",
        data={"host": "other", "port": 502, "unit_id": 1},
    )
    instance = _flow(monkeypatch, entries=[other])

    async def identify_and_claim_endpoint(client, selection):
        del client, selection
        other.data = {"host": "inverter", "port": 502, "unit_id": 1}
        return _device(serial="DIFFERENT")

    monkeypatch.setattr(config_flow, "identify", identify_and_claim_endpoint)
    result = await instance.async_step_user(INPUT)

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
    unit_marker = _marker(schema, "unit_id")
    port_marker = _marker(schema, "port")
    interval_marker = _marker(schema, "scan_interval")
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
    ("error", "concerns_model", "field"),
    [
        (saj_errors.UnsupportedDeviceError(UNRECOGNISED_TYPE), True, "model"),
        (saj_errors.ModelMismatchError(selected=ALPHA, detected=BETA), True, "model"),
        (saj_errors.UnknownModelError("gamma"), True, "model"),
        (ValueError("bad identity"), False, "base"),
        (ModbusError("communication error"), False, "base"),
    ],
)
async def test_user_step_attaches_translated_validation_failure_to_its_field(
    monkeypatch, error, concerns_model, field
):
    instance = _flow(monkeypatch)
    monkeypatch.setattr(config_flow, "identify", _failing_identify(error))

    def translate(error):
        return Translation(
            key="stubbed",
            concerns_model=concerns_model,
            placeholders={"detail": "value"},
        )

    monkeypatch.setattr(config_flow, "translate_error", translate)

    result = await instance.async_step_user(INPUT)

    assert result["errors"] == {field: "stubbed"}
    assert result["description_placeholders"] == {"detail": "value"}
    assert FlowClient.instances[-1].closed
    assert not hasattr(instance, "selected_unique_id")


async def test_failed_submission_redisplays_submitted_values(monkeypatch):
    instance = _flow(monkeypatch)
    monkeypatch.setattr(
        config_flow,
        "identify",
        _failing_identify(saj_errors.UnsupportedDeviceError(UNRECOGNISED_TYPE)),
    )
    submitted = {**INPUT, "host": "typed-host", "port": 1502, "model": "beta"}

    result = await instance.async_step_user(submitted)

    assert _marker(result["data_schema"], "host").default() == "typed-host"
    assert _marker(result["data_schema"], "port").default() == 1502
    assert _marker(result["data_schema"], "model").default() == "beta"


def _assumed_device(*, serial: str = SERIAL) -> Device:
    return _device(
        serial=serial, profile=BETA, detected=False, device_type=UNRECOGNISED_TYPE
    )


async def test_assumed_profile_requires_model_confirmation_before_creating(
    monkeypatch,
):
    instance = _flow(monkeypatch)
    monkeypatch.setattr(config_flow, "identify", _identifying(_assumed_device()))

    form = await instance.async_step_user({**INPUT, "model": "beta"})

    assert form["step_id"] == "confirm_model"
    assert form["description_placeholders"] == {
        "model": "Beta",
        "device_type": "0x7777",
    }
    assert not hasattr(instance, "selected_unique_id")
    assert FlowClient.instances[-1].closed


async def test_confirmed_model_creates_entry_with_the_selection(monkeypatch):
    instance = _flow(monkeypatch)
    monkeypatch.setattr(config_flow, "identify", _identifying(_assumed_device()))
    await instance.async_step_user({**INPUT, "model": "beta"})

    result = await instance.async_step_confirm_model({})

    assert result == {
        "type": "create_entry",
        "title": f"SAJ {SERIAL}",
        "data": {**SAVED_DATA, "model": "beta"},
        "options": {"scan_interval": 30},
    }
    assert instance.selected_unique_id == SERIAL


@pytest.mark.parametrize(
    "error",
    [ModbusError("Modbus exception response", exception_code=2), ValueError("x")],
)
async def test_assumed_profile_with_failed_reads_reports_read_error(monkeypatch, error):
    instance = _flow(monkeypatch)
    monkeypatch.setattr(config_flow, "identify", _identifying(_assumed_device()))
    monkeypatch.setattr(
        config_flow,
        "translate_error",
        lambda error: Translation(key=f"stubbed-{type(error).__name__}"),
    )

    async def failing_read(client, device):
        del client, device
        raise error

    monkeypatch.setattr(config_flow, "read_telemetry", failing_read)
    result = await instance.async_step_user({**INPUT, "model": "beta"})

    assert result["step_id"] == "user"
    assert result["errors"] == {"base": f"stubbed-{type(error).__name__}"}
    assert not hasattr(instance, "selected_unique_id")


async def test_model_confirmation_without_pending_change_aborts(monkeypatch):
    instance = _flow(monkeypatch)

    assert await instance.async_step_confirm_model({}) == _abort(
        reason="confirmation_not_pending"
    )


async def test_model_confirmation_prompt_repeats_pending_details(monkeypatch):
    instance = _flow(monkeypatch)
    monkeypatch.setattr(config_flow, "identify", _identifying(_assumed_device()))
    await instance.async_step_user({**INPUT, "model": "beta"})

    prompt = await instance.async_step_confirm_model()

    assert prompt["step_id"] == "confirm_model"
    assert prompt["description_placeholders"]["model"] == "Beta"
    assert not hasattr(instance, "selected_unique_id")


async def test_model_confirmation_aborts_when_endpoint_was_claimed_meanwhile(
    monkeypatch,
):
    other = SimpleNamespace(
        entry_id="entry-b", unique_id="OTHER", data={"host": "other"}
    )
    instance = _flow(monkeypatch, entries=[other])
    monkeypatch.setattr(config_flow, "identify", _identifying(_assumed_device()))
    await instance.async_step_user({**INPUT, "model": "beta"})
    other.data = {"host": "inverter", "port": 502, "unit_id": 1}

    result = await instance.async_step_confirm_model({})

    assert result == _abort(reason="already_configured")
    assert not hasattr(instance, "selected_unique_id")


def _saved_entry(*, entry_id="entry-a", serial=SERIAL, model="automatic"):
    return SimpleNamespace(
        entry_id=entry_id,
        unique_id=serial,
        title=f"SAJ {serial}",
        data={**SAVED_DATA, "model": model},
        options={"scan_interval": 45},
        update_count=0,
    )


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
    monkeypatch.setattr(instance, "async_show_form", _form)
    monkeypatch.setattr(instance, "async_abort", _abort)
    return instance


def _submission(**changes):
    return {**INPUT, "scan_interval": 45, **changes}


def _unchanged(entry, *, data=None, options=None, serial=SERIAL):
    assert entry.data == (data or SAVED_DATA)
    assert entry.options == (options or {"scan_interval": 45})
    assert entry.unique_id == serial
    assert entry.update_count == 0


async def test_options_form_prefills_the_five_fields_from_saved_state(monkeypatch):
    entry = _saved_entry(model="beta")
    flow = _options_flow(monkeypatch, entry=entry)

    form = await flow.async_step_init()
    schema = form["data_schema"]

    assert _field_names(schema) == [
        "host",
        "port",
        "unit_id",
        "scan_interval",
        "model",
    ]
    assert _marker(schema, "port").default() == 502
    assert _marker(schema, "unit_id").default() == 1
    assert _marker(schema, "scan_interval").default() == 45
    assert _marker(schema, "model").default() == "beta"
    assert schema.schema[_marker(schema, "unit_id")].config["mode"] == "box"
    assert schema.schema[_marker(schema, "scan_interval")].config["mode"] == "box"


async def test_options_step_uses_default_interval_when_none_saved(monkeypatch):
    entry = _saved_entry()
    entry.options = {}
    instance = _options_flow(monkeypatch, entry=entry)

    form = await instance.async_step_init()
    assert form["data_schema"]({"scan_interval": 30})["scan_interval"] == 30
    assert _marker(form["data_schema"], "scan_interval").default() == 30
    assert await instance.async_step_init(_submission(scan_interval=60)) == _abort(
        reason="changes_saved"
    )
    assert entry.options == {"scan_interval": 60}
    assert entry.update_count == 1


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

    result = await flow.async_step_init(_submission(**changes))

    assert result["errors"] == {"base": reason}
    _unchanged(entry)
    assert FlowClient.instances == []


@pytest.mark.parametrize(
    ("changes", "expected_data", "expected_interval"),
    [
        ({"scan_interval": 90}, SAVED_DATA, 90),
        ({}, SAVED_DATA, 45),
        (
            {"host": "new-inverter", "scan_interval": 60},
            {**SAVED_DATA, "host": "new-inverter"},
            60,
        ),
        ({"model": "alpha"}, {**SAVED_DATA, "model": "alpha"}, 45),
    ],
)
async def test_validated_edit_saves_once_and_keeps_entry_identity(
    monkeypatch, changes, expected_data, expected_interval
):
    entry = _saved_entry()
    flow = _options_flow(monkeypatch, entry=entry)

    result = await flow.async_step_init(_submission(**changes))

    assert result == _abort(reason="changes_saved")
    assert len(FlowClient.instances) == 1
    assert FlowClient.instances[0].closed
    assert entry.entry_id == "entry-a"
    assert entry.data == expected_data
    assert entry.options == {"scan_interval": expected_interval}
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

    async def identify(client, selection):
        del client, selection
        assert session.active
        session.events.append("identify")
        return _device()

    async def read(client, device):
        del client, device
        assert session.active
        session.events.append("telemetry")

    monkeypatch.setattr(config_flow, "identify", identify)
    monkeypatch.setattr(config_flow, "read_telemetry", read)

    await session.lock.acquire()
    validation = asyncio.create_task(
        flow.async_step_init(_submission(host="INVERTER", scan_interval=60))
    )
    await session.requested.wait()
    assert FlowClient.instances == []
    assert not session.active
    session.lock.release()
    result = await validation

    assert result == _abort(reason="changes_saved")
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

    async def identify(client, selection):
        del client, selection
        probe_started.set()
        return _device()

    monkeypatch.setattr(config_flow, "identify", identify)

    await session.lock.acquire()
    validation = asyncio.create_task(
        flow.async_step_init(_submission(host="new-inverter", scan_interval=60))
    )
    await probe_started.wait()
    result = await validation
    assert session.lock.locked()
    session.lock.release()

    assert result == _abort(reason="changes_saved")
    assert FlowClient.instances[-1].closed
    assert not FlowClient.instances[-1].created_inside_session
    assert not FlowClient.instances[-1].closed_inside_session
    assert session.calls == 0
    assert entry.data["host"] == "new-inverter"


async def test_same_endpoint_validation_without_runtime_uses_owned_client(monkeypatch):
    entry = _saved_entry()
    flow = _options_flow(monkeypatch, entry=entry)

    result = await flow.async_step_init(_submission(scan_interval=60))

    assert result == _abort(reason="changes_saved")
    assert FlowClient.instances[-1].closed
    assert entry.update_count == 1


@pytest.mark.parametrize(
    ("new_profile", "new_type"),
    [(ALPHA, 0x0001), (BETA, 0x0002)],
)
@pytest.mark.parametrize("new_host", ["inverter", "new-inverter"])
async def test_replacement_across_models_asks_confirmation_before_any_change(
    monkeypatch, new_profile, new_type, new_host
):
    entry = _saved_entry()
    flow = _options_flow(monkeypatch, entry=entry)
    monkeypatch.setattr(
        config_flow,
        "identify",
        _identifying(
            _device(
                serial=REPLACEMENT_SERIAL, profile=new_profile, device_type=new_type
            )
        ),
    )

    form = await flow.async_step_init(_submission(host=new_host, scan_interval=75))

    assert form["step_id"] == "confirm_replacement"
    assert form["description_placeholders"] == {
        "model": new_profile.display_name,
        "serial": REPLACEMENT_SERIAL,
    }
    _unchanged(entry)
    assert FlowClient.instances[-1].closed

    result = await flow.async_step_confirm_replacement({})

    assert result == _abort(reason="changes_saved")
    assert entry.entry_id == "entry-a"
    assert entry.unique_id == REPLACEMENT_SERIAL
    assert entry.title == f"SAJ {SERIAL}"
    assert entry.data == {**SAVED_DATA, "host": new_host}
    assert entry.options == {"scan_interval": 75}
    assert entry.update_count == 1


async def test_options_unknown_model_selection_reports_error_and_keeps_saved_state(
    monkeypatch,
):
    entry = _saved_entry()
    flow = _options_flow(monkeypatch, entry=entry)
    monkeypatch.setattr(
        config_flow,
        "identify",
        _failing_identify(saj_errors.UnknownModelError("gamma")),
    )

    result = await flow.async_step_init(_submission(model="gamma"))

    assert result["errors"] == {"model": "unknown_model"}
    assert result["description_placeholders"] == {"selection": "gamma"}
    _unchanged(entry)
    assert FlowClient.instances[-1].closed


@pytest.mark.parametrize(
    ("error", "reason"),
    [
        (
            ModbusError(ModbusErrorMessage.EXCEPTION_RESPONSE, exception_code=2),
            "read_rejected",
        ),
        (ValueError("undecodable"), "invalid_device_data"),
    ],
)
async def test_options_assumed_profile_with_failed_reads_keeps_saved_state(
    monkeypatch, error, reason
):
    entry = _saved_entry()
    flow = _options_flow(monkeypatch, entry=entry)
    monkeypatch.setattr(config_flow, "identify", _identifying(_assumed_device()))

    async def failing_read(client, device):
        del client, device
        raise error

    monkeypatch.setattr(config_flow, "read_telemetry", failing_read)

    result = await flow.async_step_init(_submission(model="beta"))

    assert result["step_id"] == "init"
    assert result["errors"] == {"base": reason}
    _unchanged(entry)
    assert FlowClient.instances[-1].closed


async def test_replacement_prompt_shown_again_until_submitted(monkeypatch):
    entry = _saved_entry()
    flow = _options_flow(monkeypatch, entry=entry)
    monkeypatch.setattr(
        config_flow,
        "identify",
        _identifying(_device(serial=REPLACEMENT_SERIAL, profile=BETA)),
    )
    await flow.async_step_init(_submission())

    prompt = await flow.async_step_confirm_replacement()

    assert prompt["step_id"] == "confirm_replacement"
    _unchanged(entry)


async def test_duplicate_serial_is_rejected_before_replacement_confirmation(
    monkeypatch,
):
    entry = _saved_entry()
    other = _saved_entry(entry_id="entry-b", serial=REPLACEMENT_SERIAL)
    other.data = {**SAVED_DATA, "host": "other"}
    flow = _options_flow(monkeypatch, entry=entry, entries=[entry, other])
    monkeypatch.setattr(
        config_flow,
        "identify",
        _identifying(_device(serial=REPLACEMENT_SERIAL)),
    )

    result = await flow.async_step_init(_submission(host="new-inverter"))

    assert result["errors"] == {"base": "already_configured"}
    _unchanged(entry)


@pytest.mark.parametrize("step", ["confirm_model", "confirm_replacement"])
async def test_confirmation_steps_without_pending_change_abort(monkeypatch, step):
    entry = _saved_entry()
    flow = _options_flow(monkeypatch, entry=entry)

    result = await getattr(flow, f"async_step_{step}")({})

    assert result == _abort(reason="confirmation_not_pending")
    _unchanged(entry)


@pytest.mark.parametrize(
    ("selection", "profile", "device_type", "reason"),
    [
        ("alpha", BETA, 0x0002, "model_mismatch"),
        ("automatic", None, UNRECOGNISED_TYPE, "unsupported_device"),
    ],
)
async def test_options_step_rejects_model_errors_without_saving(
    monkeypatch, selection, profile, device_type, reason
):
    entry = _saved_entry()
    flow = _options_flow(monkeypatch, entry=entry)
    error = (
        saj_errors.ModelMismatchError(selected=ALPHA, detected=profile)
        if profile
        else saj_errors.UnsupportedDeviceError(device_type)
    )
    monkeypatch.setattr(config_flow, "identify", _failing_identify(error))

    result = await flow.async_step_init(_submission(model=selection))

    assert result["errors"] == {"model": reason}
    assert result["description_placeholders"]
    assert _marker(result["data_schema"], "model").default() == selection
    _unchanged(entry)
    assert FlowClient.instances[-1].closed


@pytest.mark.parametrize("serial", [SERIAL, REPLACEMENT_SERIAL])
async def test_assumed_model_is_saved_only_after_confirmation(monkeypatch, serial):
    entry = _saved_entry()
    flow = _options_flow(monkeypatch, entry=entry)
    monkeypatch.setattr(
        config_flow, "identify", _identifying(_assumed_device(serial=serial))
    )

    form = await flow.async_step_init(_submission(model="beta"))

    assert form["step_id"] == "confirm_model"
    assert form["description_placeholders"] == {
        "model": "Beta",
        "device_type": "0x7777",
    }
    _unchanged(entry)
    if serial != SERIAL:
        replacement = await flow.async_step_confirm_model({})
        assert replacement["step_id"] == "confirm_replacement"
        _unchanged(entry)
        result = await flow.async_step_confirm_replacement({})
    else:
        result = await flow.async_step_confirm_model({})

    assert result == _abort(reason="changes_saved")
    assert entry.data == {**SAVED_DATA, "model": "beta"}
    assert entry.unique_id == serial
    assert entry.update_count == 1


async def test_replacement_confirmation_cannot_skip_model_confirmation(monkeypatch):
    entry = _saved_entry()
    flow = _options_flow(monkeypatch, entry=entry)
    monkeypatch.setattr(
        config_flow,
        "identify",
        _identifying(_assumed_device(serial=REPLACEMENT_SERIAL)),
    )
    await flow.async_step_init(_submission(model="beta"))

    form = await flow.async_step_confirm_replacement({})

    assert form["step_id"] == "confirm_model"
    _unchanged(entry)


async def test_model_prompt_is_shown_again_until_submitted(monkeypatch):
    entry = _saved_entry()
    flow = _options_flow(monkeypatch, entry=entry)
    monkeypatch.setattr(config_flow, "identify", _identifying(_assumed_device()))
    await flow.async_step_init(_submission(model="beta"))

    prompt = await flow.async_step_confirm_model()

    assert prompt["step_id"] == "confirm_model"
    _unchanged(entry)


@pytest.mark.parametrize("ownership_change", ["endpoint", "serial"])
@pytest.mark.parametrize("confirmation", ["replacement", "model"])
async def test_confirmation_rechecks_other_entry_ownership_before_saving(
    monkeypatch, ownership_change, confirmation
):
    entry = _saved_entry()
    other = _saved_entry(entry_id="entry-b", serial="OTHER")
    other.data = {**SAVED_DATA, "host": "other"}
    flow = _options_flow(monkeypatch, entry=entry, entries=[entry, other])
    device = (
        _device(serial=REPLACEMENT_SERIAL, profile=BETA)
        if confirmation == "replacement"
        else _assumed_device()
    )
    monkeypatch.setattr(config_flow, "identify", _identifying(device))
    await flow.async_step_init(
        _submission(host="new-inverter", port=1502, unit_id=2, scan_interval=75)
    )
    if ownership_change == "endpoint":
        other.data = {**SAVED_DATA, "host": "new-inverter", "port": 1502, "unit_id": 2}
    else:
        other.unique_id = device.serial

    result = await getattr(flow, f"async_step_confirm_{confirmation}")({})

    assert result == _abort(reason="already_configured")
    _unchanged(entry)


async def test_changed_endpoint_validation_failure_leaves_saved_state_unchanged(
    monkeypatch,
):
    entry = _saved_entry()
    flow = _options_flow(monkeypatch, entry=entry)
    monkeypatch.setattr(
        config_flow,
        "identify",
        _failing_identify(ModbusError(ModbusErrorMessage.CONNECTION_TIMEOUT)),
    )

    result = await flow.async_step_init(_submission(host="new-inverter"))

    assert result["errors"] == {"base": "timeout"}
    _unchanged(entry)
    assert FlowClient.instances[-1].closed


async def test_changed_endpoint_rejects_other_entry_before_connecting(monkeypatch):
    entry = _saved_entry()
    other = _saved_entry(entry_id="entry-b", serial="OTHER")
    other.data = {**SAVED_DATA, "host": "new-inverter"}
    flow = _options_flow(monkeypatch, entry=entry, entries=[entry, other])

    result = await flow.async_step_init(_submission(host="new-inverter"))

    assert result["errors"] == {"base": "already_configured"}
    assert FlowClient.instances == []
    _unchanged(entry)


async def test_connection_edit_rechecks_endpoint_ownership_after_validation(
    monkeypatch,
):
    entry = _saved_entry()
    other = _saved_entry(entry_id="entry-b", serial="OTHER")
    other.data = {**SAVED_DATA, "host": "other"}
    flow = _options_flow(monkeypatch, entry=entry, entries=[entry, other])

    async def identify_and_claim_endpoint(client, selection):
        del client, selection
        other.data = {**SAVED_DATA, "host": "new-inverter"}
        return _device()

    monkeypatch.setattr(config_flow, "identify", identify_and_claim_endpoint)
    result = await flow.async_step_init(_submission(host="new-inverter"))

    assert result["errors"] == {"base": "already_configured"}
    assert FlowClient.instances[-1].closed
    _unchanged(entry)


async def test_cancelled_endpoint_validation_closes_temporary_client(monkeypatch):
    entry = _saved_entry()
    flow = _options_flow(monkeypatch, entry=entry)
    monkeypatch.setattr(
        config_flow, "identify", _failing_identify(asyncio.CancelledError())
    )

    with pytest.raises(asyncio.CancelledError):
        await flow.async_step_init(_submission(host="new-inverter"))
    assert FlowClient.instances[-1].closed
    assert entry.update_count == 0


def test_options_flow_factory_returns_integration_flow():
    assert isinstance(
        config_flow.SajLocalConfigFlow.async_get_options_flow(None),
        config_flow.SajOptionsFlow,
    )
