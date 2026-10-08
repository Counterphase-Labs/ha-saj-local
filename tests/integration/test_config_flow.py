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
from custom_components.saj_local.saj.telemetry import Readout

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


class InstallationClient:
    def __init__(self) -> None:
        self.closed = False

    async def close(self) -> None:
        self.closed = True


class FakeValidationSession:
    def __init__(self) -> None:
        self.client = InstallationClient()
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
    async def _session(self) -> AsyncIterator[InstallationClient]:
        await self.lock.acquire()
        self.active = True
        self.events.append("session_enter")
        try:
            yield self.client
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


async def _telemetry(client, device) -> Readout:
    del client, device
    return Readout(values={}, refusals={})


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
    instance.hass = SimpleNamespace(config_entries=FakeConfigEntries(entries), data={})
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
    assert result["data_schema"]({"host": "inverter"}) == {
        **INPUT,
        "scan_interval": 60,
    }
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
    parameters = dict(FlowClient.instances[0].parameters)
    environment = parameters.pop("environment")
    assert parameters == {
        "host": "inverter",
        "port": 502,
        "unit_id": 5,
        "timeout": config_flow.REQUEST_TIMEOUT,
    }
    assert (
        environment.budget is instance.hass.data["saj_local"][("inverter", 502)].budget
    )
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
        "min": 10,
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
        config_entries=FakeConfigEntries(entries if entries is not None else [entry]),
        data={},
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
    assert _marker(form["data_schema"], "scan_interval").default() == 60
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
        ({"scan_interval": 9}, "invalid_scan_interval"),
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


async def test_same_endpoint_validation_probes_over_the_installation_client(
    monkeypatch,
):
    entry, session, flow = _options_flow_with_validation_session(monkeypatch)

    async def identify(client, selection):
        del selection
        assert client is session.client
        assert session.active
        session.events.append("identify")
        return _device()

    async def read(client, device):
        del device
        assert client is session.client
        assert session.active
        session.events.append("telemetry")
        return Readout(values={}, refusals={})

    monkeypatch.setattr(config_flow, "identify", identify)
    monkeypatch.setattr(config_flow, "read_telemetry", read)

    await session.lock.acquire()
    validation = asyncio.create_task(
        flow.async_step_init(_submission(host="INVERTER", scan_interval=60))
    )
    await session.requested.wait()
    assert not session.active
    session.lock.release()
    result = await validation

    assert result == _abort(reason="changes_saved")
    assert FlowClient.instances == []
    assert not session.client.closed
    assert session.events == [
        "session_enter",
        "identify",
        "telemetry",
        "session_exit",
    ]
    assert entry.update_count == 1


async def test_refused_required_register_fails_validation_without_saving(
    monkeypatch,
):
    entry, session, flow = _options_flow_with_validation_session(monkeypatch)

    async def refused(client, device):
        del client, device
        return Readout(values={}, refusals={"pv_power": 2})

    monkeypatch.setattr(config_flow, "read_telemetry", refused)

    result = await flow.async_step_init(_submission(scan_interval=60))

    assert result["errors"] == {"base": "read_rejected"}
    _unchanged(entry)
    assert not session.client.closed


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


@pytest.mark.parametrize(
    ("interval", "accepted"),
    [(9, False), (9.5, False), (10, True), (10.5, False), (60, True)],
)
async def test_user_step_enforces_the_shared_minimum_interval(
    monkeypatch, interval, *, accepted
):
    instance = _flow(monkeypatch)

    result = await instance.async_step_user({**INPUT, "scan_interval": interval})

    if accepted:
        assert result["options"] == {"scan_interval": interval}
    else:
        assert result["errors"] == {"base": "invalid_scan_interval"}
        assert FlowClient.instances == []


ENTRY_ID = "entry-a"


def _registered(key, *, name=None, original_name="Original", domain="sensor"):
    return SimpleNamespace(
        unique_id=f"{ENTRY_ID}_{key}",
        domain=domain,
        name=name,
        original_name=original_name,
    )


REGISTERED = [
    _registered("pv_power", original_name="Solar power"),
    _registered("grid_power", original_name="Grid power"),
    _registered("battery_soc", name="My battery", original_name="Battery charge"),
]


def _group(subentry_id, keys, *, interval=10, title="Group"):
    return SimpleNamespace(
        subentry_id=subentry_id,
        subentry_type="polling_group",
        title=title,
        data={"scan_interval": interval, "sensors": list(keys)},
    )


def _group_flow(monkeypatch, *, subentries=(), registered=REGISTERED, editing=None):
    entry = SimpleNamespace(
        entry_id=ENTRY_ID,
        subentries={subentry.subentry_id: subentry for subentry in subentries},
    )
    flow = object.__new__(config_flow.SajPollingGroupFlow)
    flow.updates = []
    flow.hass = SimpleNamespace(
        config_entries=SimpleNamespace(
            async_get_known_entry=lambda _entry_id: entry,
            async_update_subentry=lambda **changes: flow.updates.append(changes),
        )
    )
    flow.handler = (ENTRY_ID, "polling_group")
    flow.context = {"source": "user"}
    if editing is not None:
        flow.context = {"source": "reconfigure", "subentry_id": editing}
    flow.registered = list(registered)
    monkeypatch.setattr(config_flow.er, "async_get", lambda _hass: "registry")
    monkeypatch.setattr(
        config_flow.er,
        "async_entries_for_config_entry",
        lambda registry, entry_id: (
            flow.registered if (registry, entry_id) == ("registry", ENTRY_ID) else []
        ),
    )
    monkeypatch.setattr(flow, "async_show_form", _form)
    monkeypatch.setattr(flow, "async_abort", _abort)
    monkeypatch.setattr(
        flow,
        "async_create_entry",
        lambda *, title, data: {"type": "create_entry", "title": title, "data": data},
    )
    return flow, entry


def _offered(form):
    schema = form["data_schema"]
    selector = schema.schema[_marker(schema, "sensors")]
    return {option["value"]: option["label"] for option in selector.config["options"]}


def _group_input(**changes):
    return {
        "name": "Power",
        "scan_interval": 10,
        "sensors": ["pv_power"],
        **changes,
    }


async def test_the_polling_group_type_is_declared_by_the_config_flow():
    types = config_flow.SajLocalConfigFlow.async_get_supported_subentry_types(None)

    assert types == {"polling_group": config_flow.SajPollingGroupFlow}


async def test_add_and_edit_show_the_same_three_field_form(monkeypatch):
    add, _ = _group_flow(monkeypatch)
    edit, _ = _group_flow(
        monkeypatch, subentries=[_group("g1", ["pv_power"])], editing="g1"
    )

    added = await add.async_step_user()
    edited = await edit.async_step_reconfigure()

    assert _field_names(added["data_schema"]) == ["name", "scan_interval", "sensors"]
    assert _field_names(edited["data_schema"]) == _field_names(added["data_schema"])
    assert added["step_id"] == "user"
    assert edited["step_id"] == "reconfigure"
    assert added["errors"] == edited["errors"] == {}


async def test_a_new_group_starts_at_the_shortest_interval_with_nothing_selected(
    monkeypatch,
):
    flow, _ = _group_flow(monkeypatch)

    schema = (await flow.async_step_user())["data_schema"]

    assert _marker(schema, "scan_interval").default() == config_flow.MIN_INTERVAL
    assert _marker(schema, "sensors").default() == []


async def test_the_form_requires_a_name_and_trims_it(monkeypatch):
    flow, _ = _group_flow(monkeypatch)
    schema = (await flow.async_step_user())["data_schema"]

    assert schema(_group_input(name="  Power  "))["name"] == "Power"
    with pytest.raises(config_flow.vol.Invalid):
        schema(_group_input(name="   "))
    with pytest.raises(config_flow.vol.Invalid):
        schema({"scan_interval": 10, "sensors": []})


async def test_a_valid_submission_adds_a_group_titled_by_its_name(monkeypatch):
    flow, _ = _group_flow(monkeypatch)

    result = await flow.async_step_user(
        _group_input(scan_interval=15.0, sensors=["pv_power", "grid_power"])
    )

    assert result == {
        "type": "create_entry",
        "title": "Power",
        "data": {"scan_interval": 15, "sensors": ["pv_power", "grid_power"]},
    }
    assert type(result["data"]["scan_interval"]) is int
    assert flow.updates == []


async def test_a_valid_edit_updates_the_group_in_place_without_a_flow_reload(
    monkeypatch,
):
    group = _group("g1", ["pv_power"], title="Old")
    flow, entry = _group_flow(monkeypatch, subentries=[group], editing="g1")

    result = await flow.async_step_reconfigure(
        _group_input(name="New", scan_interval=30, sensors=["grid_power"])
    )

    assert result == _abort(reason="reconfigure_successful")
    assert len(flow.updates) == 1
    update = flow.updates[0]
    assert update["entry"] is entry
    assert update["subentry"] is group
    assert update["title"] == "New"
    assert update["data"] == {"scan_interval": 30, "sensors": ["grid_power"]}


@pytest.mark.parametrize("interval", [9, 0, 12.5, "fast", None])
@pytest.mark.parametrize("editing", [False, True])
async def test_an_invalid_interval_is_reported_on_its_field_and_nothing_is_saved(
    monkeypatch, interval, *, editing
):
    group = _group("g1", ["grid_power"])
    flow, _ = _group_flow(
        monkeypatch,
        subentries=[group],
        editing="g1" if editing else None,
    )
    step = flow.async_step_reconfigure if editing else flow.async_step_user

    result = await step(_group_input(scan_interval=interval))

    assert result["type"] == "form"
    assert result["errors"] == {"scan_interval": "invalid_scan_interval"}
    assert flow.updates == []


async def test_a_submission_without_sensors_is_reported_on_the_sensors_field(
    monkeypatch,
):
    flow, _ = _group_flow(monkeypatch)

    result = await flow.async_step_user(_group_input(sensors=[]))

    assert result["errors"] == {"sensors": "no_sensors_selected"}


async def test_a_sensor_owned_by_another_group_is_rejected_on_the_sensors_field(
    monkeypatch,
):
    other = _group("g2", ["pv_power"])
    flow, _ = _group_flow(monkeypatch, subentries=[other])

    result = await flow.async_step_user(
        _group_input(sensors=["pv_power", "grid_power"])
    )

    assert result["errors"] == {"sensors": "sensor_in_other_group"}


async def test_every_error_is_reported_together_and_the_submission_is_redisplayed(
    monkeypatch,
):
    flow, _ = _group_flow(monkeypatch)

    result = await flow.async_step_user(
        _group_input(name="Mine", scan_interval=3, sensors=[])
    )

    assert result["errors"] == {
        "scan_interval": "invalid_scan_interval",
        "sensors": "no_sensors_selected",
    }
    schema = result["data_schema"]
    assert _marker(schema, "name").default() == "Mine"
    assert _marker(schema, "scan_interval").default() == 3


@pytest.mark.parametrize("editing", [False, True])
async def test_an_installation_without_sensors_cannot_have_groups(
    monkeypatch, *, editing
):
    group = _group("g1", [])
    flow, _ = _group_flow(
        monkeypatch,
        subentries=[group],
        registered=[],
        editing="g1" if editing else None,
    )
    step = flow.async_step_reconfigure if editing else flow.async_step_user

    assert await step() == _abort(reason="no_sensors")


async def test_adding_with_every_sensor_already_grouped_is_aborted_with_a_reason(
    monkeypatch,
):
    groups = [
        _group("g1", ["pv_power", "grid_power"]),
        _group("g2", ["battery_soc"]),
    ]
    flow, _ = _group_flow(monkeypatch, subentries=groups)

    assert await flow.async_step_user() == _abort(reason="all_sensors_assigned")


async def test_editing_a_group_that_holds_every_sensor_still_shows_the_form(
    monkeypatch,
):
    group = _group("g1", ["pv_power", "grid_power", "battery_soc"])
    flow, _ = _group_flow(monkeypatch, subentries=[group], editing="g1")

    form = await flow.async_step_reconfigure()

    assert set(_offered(form)) == {"pv_power", "grid_power", "battery_soc"}
    assert _marker(form["data_schema"], "sensors").default() == [
        "pv_power",
        "grid_power",
        "battery_soc",
    ]
    assert _marker(form["data_schema"], "name").default() == "Group"
    assert _marker(form["data_schema"], "scan_interval").default() == 10


async def test_options_exclude_sensors_of_other_groups_and_include_the_groups_own(
    monkeypatch,
):
    groups = [_group("g1", ["pv_power"]), _group("g2", ["grid_power"])]
    adding, _ = _group_flow(monkeypatch, subentries=groups)
    editing, _ = _group_flow(monkeypatch, subentries=groups, editing="g1")

    assert set(_offered(await adding.async_step_user())) == {"battery_soc"}
    assert set(_offered(await editing.async_step_reconfigure())) == {
        "pv_power",
        "battery_soc",
    }


async def test_a_sensor_released_by_one_group_is_offered_to_another(monkeypatch):
    first, second = _group("g1", ["pv_power"]), _group("g2", ["grid_power"])
    flow, entry = _group_flow(monkeypatch, subentries=[first, second], editing="g2")
    assert "pv_power" not in _offered(await flow.async_step_reconfigure())

    entry.subentries["g1"] = _group("g1", [])

    assert "pv_power" in _offered(await flow.async_step_reconfigure())


async def test_options_are_labelled_with_the_names_users_see(monkeypatch):
    registered = [
        _registered("pv_power", name="Roof", original_name="Solar power"),
        _registered("grid_power", original_name="Grid power"),
        _registered("battery_soc", name=None, original_name=None),
        _registered("load_power", original_name="Other entry"),
        _registered("operating_mode", original_name="Not a sensor", domain="switch"),
    ]
    registered[3].unique_id = "other-entry_load_power"
    flow, _ = _group_flow(monkeypatch, registered=registered)

    offered = _offered(await flow.async_step_user())

    assert offered == {
        "pv_power": "Roof",
        "grid_power": "Grid power",
        "battery_soc": "battery_soc",
    }


async def test_options_are_listed_in_label_order(monkeypatch):
    flow, _ = _group_flow(monkeypatch)

    offered = _offered(await flow.async_step_user())

    assert list(offered.values()) == sorted(offered.values())


async def test_a_disabled_sensor_is_still_offered(monkeypatch):
    disabled = _registered("pv_power", original_name="Solar power")
    disabled.disabled_by = "user"
    flow, _ = _group_flow(monkeypatch, registered=[disabled])

    assert set(_offered(await flow.async_step_user())) == {"pv_power"}


async def test_editing_works_while_the_entry_is_not_loaded(monkeypatch):
    group = _group("g1", ["pv_power"])
    flow, entry = _group_flow(monkeypatch, subentries=[group], editing="g1")
    assert not hasattr(entry, "runtime_data")

    form = await flow.async_step_reconfigure()

    assert form["type"] == "form"


async def test_stale_sensors_are_hidden_when_editing_and_dropped_on_save(monkeypatch):
    group = _group("g1", ["pv_power", "no_longer_exists"])
    flow, _ = _group_flow(monkeypatch, subentries=[group], editing="g1")

    form = await flow.async_step_reconfigure()
    shown = _marker(form["data_schema"], "sensors").default()
    await flow.async_step_reconfigure(_group_input(sensors=shown))

    assert shown == ["pv_power"]
    assert flow.updates[0]["data"]["sensors"] == ["pv_power"]


async def test_groups_of_other_subentry_types_do_not_own_sensors(monkeypatch):
    foreign = SimpleNamespace(
        subentry_id="x", subentry_type="something_else", title="", data={}
    )
    flow, _ = _group_flow(monkeypatch, subentries=[foreign])

    assert set(_offered(await flow.async_step_user())) == {
        "pv_power",
        "grid_power",
        "battery_soc",
    }


async def test_temporary_validation_clients_draw_on_the_endpoints_shared_budget(
    monkeypatch,
):
    instance = _flow(monkeypatch)
    other = _flow(monkeypatch)
    other.hass = instance.hass

    await instance.async_step_user(INPUT)
    await other.async_step_user({**INPUT, "host": "INVERTER"})
    await instance.async_step_user({**INPUT, "port": 503})

    budgets = [
        client.parameters["environment"].budget for client in FlowClient.instances
    ]
    assert budgets[0] is budgets[1]
    assert budgets[2] is not budgets[0]


async def test_validation_is_not_held_back_by_the_endpoints_back_off(monkeypatch):
    instance = _flow(monkeypatch)
    config_flow.endpoint_guard(hass=instance.hass, host="inverter", port=502).failed(
        now=0, base_delay=300
    )

    result = await instance.async_step_user(INPUT)

    assert result["type"] == "create_entry"
    assert len(FlowClient.instances) == 1


def _backed_off_guard(flow, *, failures=2):
    guard = config_flow.endpoint_guard(hass=flow.hass, host="inverter", port=502)
    for _ in range(failures):
        guard.failed(now=100, base_delay=30)
    for moment in (1.0, 2.0, 3.0):
        guard.budget.record(now=moment)
    return guard


def _state(guard):
    return (
        guard.consecutive_failures,
        guard.backoff_delay,
        guard.retry_in(now=100),
        list(guard.budget._sent),
    )


async def _read_refused(client, device):
    del client, device
    return Readout(values={}, refusals={"pv_power": 2})


async def _identify_unreachable(client, selection):
    del client, selection
    raise ModbusError(ModbusErrorMessage.CONNECTION_FAILED)


async def test_a_passed_validation_over_a_temporary_client_clears_the_back_off(
    monkeypatch,
):
    instance = _flow(monkeypatch)
    guard = _backed_off_guard(instance)
    budget_history = list(guard.budget._sent)

    result = await instance.async_step_user(INPUT)

    assert result["type"] == "create_entry"
    assert guard.consecutive_failures == 0
    assert guard.backoff_delay == 0
    assert guard.retry_in(now=100) == 0
    assert list(guard.budget._sent) == budget_history


async def test_a_passed_validation_over_the_installation_client_clears_the_back_off(
    monkeypatch,
):
    entry, session, flow = _options_flow_with_validation_session(monkeypatch)
    guard = _backed_off_guard(flow)
    budget_history = list(guard.budget._sent)

    result = await flow.async_step_init(_submission(scan_interval=60))

    assert result == _abort(reason="changes_saved")
    assert not session.client.closed
    assert guard.consecutive_failures == 0
    assert guard.retry_in(now=100) == 0
    assert list(guard.budget._sent) == budget_history
    assert entry.update_count == 1


@pytest.mark.parametrize(
    "failing_step",
    [
        ("identify", _identify_unreachable),
        ("read_telemetry", _read_refused),
    ],
)
async def test_a_failed_validation_over_a_temporary_client_leaves_the_guard_alone(
    monkeypatch, failing_step
):
    instance = _flow(monkeypatch)
    guard = _backed_off_guard(instance)
    before = _state(guard)
    monkeypatch.setattr(config_flow, *failing_step)

    result = await instance.async_step_user(INPUT)

    assert result["errors"]
    assert _state(guard) == before


@pytest.mark.parametrize(
    "failing_step",
    [
        ("identify", _identify_unreachable),
        ("read_telemetry", _read_refused),
    ],
)
async def test_a_failed_validation_over_the_installation_client_leaves_the_guard_alone(
    monkeypatch, failing_step
):
    entry, session, flow = _options_flow_with_validation_session(monkeypatch)
    guard = _backed_off_guard(flow)
    before = _state(guard)
    monkeypatch.setattr(config_flow, *failing_step)

    result = await flow.async_step_init(_submission(scan_interval=60))

    assert result["errors"]
    assert _state(guard) == before
    assert not session.client.closed
    assert entry.update_count == 0
