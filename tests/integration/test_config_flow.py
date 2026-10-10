from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from enum import StrEnum
from types import SimpleNamespace
from typing import TYPE_CHECKING, ClassVar

import pytest
from homeassistant.helpers import selector

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from custom_components.saj_local.saj.models import Profile

from custom_components.saj_local import config_flow
from custom_components.saj_local.errors import Translation
from custom_components.saj_local.saj import errors as saj_errors
from custom_components.saj_local.saj.catalogue import blocks_by_key
from custom_components.saj_local.saj.client import ModbusError, ModbusErrorMessage
from custom_components.saj_local.saj.device import Device
from custom_components.saj_local.saj.models.hs3 import PROFILE as HS3
from custom_components.saj_local.saj.telemetry import Readout
from tests.profiles import profile

SERIAL = "TEST-001"
REPLACEMENT_SERIAL = "TEST-REPLACEMENT"
UNRECOGNISED_TYPE = 0x7777
ALPHA = profile(
    base=HS3, key="alpha", device_types={0x0001}, keys=(), hand_verified=True
)
BETA = profile(
    base=HS3, key="beta", device_types={0x0002}, keys=(), hand_verified=False
)
GAMMA = profile(
    base=HS3,
    key="gamma",
    device_types={0x0003},
    keys={"pv_power", "grid_power", "battery_soc"},
    hand_verified=True,
)
GAMMA_TYPE = 0x0003
INPUT = {
    "host": "inverter",
    "port": 502,
    "unit_id": 1,
    "scan_interval": 30,
    "model": "automatic",
}
SAVED_DATA = {
    "host": "inverter",
    "port": 502,
    "unit_id": 1,
    "model": "automatic",
    "device_type": 0x0001,
}
DISABLED_LABEL = "{entity} (disabled)"
BLOCK_LABELS = {"realtime": "Realtime", "settings": "Settings", "energy": "Energy"}


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
        self.events = []

    def async_entries(self, _domain):
        return self.entries

    def async_update_entry(self, entry, **changes):
        entry.data = changes["data"]
        entry.options = changes["options"]
        entry.unique_id = changes["unique_id"]
        entry.update_count = getattr(entry, "update_count", 0) + 1
        self.events.append("update_entry")
        return True


def _device(
    *,
    serial: str = SERIAL,
    profile: Profile = ALPHA,
    detected: bool = True,
    device_type: int = 0x0001,
) -> Device:
    return Device(serial, device_type, 12000, profile, detected=detected)


def _nothing_taken(*, hass, entity_id) -> bool:
    del hass, entity_id
    return False


def _nothing_enabled(**asked) -> frozenset[str]:
    _nothing_enabled.asked.append(asked)
    return _nothing_enabled.keys


_nothing_enabled.asked = []
_nothing_enabled.keys = frozenset()


def _one_request_per_key(
    *, profile, device_type, enabled, default_interval, groups
) -> float:
    _one_request_per_key.asked.append(
        {
            "profile": profile,
            "device_type": device_type,
            "enabled": enabled,
            "default_interval": default_interval,
            "groups": list(groups),
        }
    )
    grouped = sum(len(group.keys) * 60 / group.interval for group in groups)
    return grouped + 60 / default_interval


_one_request_per_key.asked = []


def _requests_per_key(*, profile, device_type, keys) -> int:
    del profile, device_type
    return len(keys)


async def _block_translations(hass, language, category, integrations):
    del hass
    assert (language, category, integrations) == ("en", "selector", ["saj_local"])
    return {
        f"component.saj_local.selector.block.options.{block}": label
        for block, label in BLOCK_LABELS.items()
    } | {"component.saj_local.selector.entity_state.options.disabled": DISABLED_LABEL}


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


async def _telemetry(client, device, enabled) -> Readout:
    del client, device, enabled
    return Readout(values={}, refusals={})


@pytest.fixture(autouse=True)
def reset_flow_client_instances(monkeypatch):
    FlowClient.instances.clear()
    FlowClient.validation_session = None
    _nothing_enabled.asked.clear()
    _nothing_enabled.keys = frozenset()
    _one_request_per_key.asked.clear()
    monkeypatch.setattr(config_flow.selector, "NumberSelector", FakeNumberSelector)
    monkeypatch.setattr(
        config_flow.selector, "NumberSelectorMode", FakeNumberSelectorMode
    )
    monkeypatch.setattr(config_flow, "PROFILES", (ALPHA, BETA, GAMMA))
    monkeypatch.setattr(config_flow, "ModbusTcpClient", FlowClient)
    monkeypatch.setattr(config_flow, "identify", _identifying(_device()))
    monkeypatch.setattr(config_flow, "read_telemetry", _telemetry)
    monkeypatch.setattr(config_flow, "entity_id_in_use", _nothing_taken)
    monkeypatch.setattr(config_flow, "enabled_entity_keys", _nothing_enabled)
    monkeypatch.setattr(config_flow, "installation_load", _one_request_per_key)
    monkeypatch.setattr(config_flow, "requests_per_read", _requests_per_key)
    monkeypatch.setattr(config_flow, "async_get_translations", _block_translations)


def _form(**kwargs):
    return {"type": "form", **kwargs}


def _abort(*, reason):
    return {"type": "abort", "reason": reason}


def _flow(monkeypatch, *, entries=()):
    instance = object.__new__(config_flow.SajLocalConfigFlow)
    instance.hass = SimpleNamespace(
        config_entries=FakeConfigEntries(entries),
        config=SimpleNamespace(components=set(), language="en"),
        data={},
    )
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


def _use_home_assistant_number_selector(monkeypatch):
    monkeypatch.setattr(config_flow.selector, "NumberSelector", selector.NumberSelector)
    monkeypatch.setattr(
        config_flow.selector, "NumberSelectorMode", selector.NumberSelectorMode
    )


def _marker(schema, name: str):
    return next(marker for marker in schema.schema if marker.schema == name)


async def test_user_step_shows_the_seven_fields_with_automatic_model_default(
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
        "prefix",
        "allow_control",
    ]
    assert result["data_schema"]({"host": "inverter"}) == {
        **INPUT,
        "scan_interval": 60,
        "allow_control": False,
    }
    assert result["errors"] == {}


async def test_model_dropdown_offers_automatic_then_every_library_profile(
    monkeypatch,
):
    instance = _flow(monkeypatch)

    schema = (await instance.async_step_user())["data_schema"]
    model_selector = schema.schema[_marker(schema, "model")]

    assert model_selector.config["options"] == ["automatic", "alpha", "beta", "gamma"]
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
        "data": {**SAVED_DATA, "unit_id": 5, "device_type": device_type},
        "options": {"scan_interval": 30, "prefix": "", "allow_control": False},
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
    assert set(result["data"]) == {"host", "port", "unit_id", "model", "device_type"}
    assert identify.selections == ["beta"]


async def test_user_step_rejects_duplicate_endpoint_before_connecting(monkeypatch):
    entry = SimpleNamespace(
        data={"host": "INVERTER", "port": 502, "unit_id": 1},
        options={"prefix": "other"},
    )
    instance = _flow(monkeypatch, entries=[entry])

    result = await instance.async_step_user(INPUT)

    assert result["errors"] == {"base": "already_configured"}
    assert FlowClient.instances == []


async def test_user_step_rechecks_endpoint_after_validation_before_create(monkeypatch):
    other = SimpleNamespace(
        entry_id="entry-b",
        unique_id="OTHER",
        data={"host": "other", "port": 502, "unit_id": 1},
        options={"prefix": "other"},
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


ENDPOINT_NUMBER_ERRORS = [
    ("port", 0, "invalid_port"),
    ("port", -1, "invalid_port"),
    ("port", 65536, "invalid_port"),
    ("port", 502.5, "invalid_port"),
    ("unit_id", 0, "invalid_unit_id"),
    ("unit_id", -1, "invalid_unit_id"),
    ("unit_id", 248, "invalid_unit_id"),
    ("unit_id", 1.5, "invalid_unit_id"),
    ("scan_interval", 0, "invalid_scan_interval"),
    ("scan_interval", 2, "invalid_scan_interval"),
    ("scan_interval", -30, "invalid_scan_interval"),
    ("scan_interval", 30.5, "invalid_scan_interval"),
]


@pytest.mark.parametrize(("field", "value", "error"), ENDPOINT_NUMBER_ERRORS)
async def test_user_step_reports_a_bad_number_on_its_field_and_keeps_the_input(
    monkeypatch, field, value, error
):
    instance = _flow(monkeypatch)

    result = await instance.async_step_user({**INPUT, field: value})

    assert result["type"] == "form"
    assert result["errors"] == {field: error}
    assert _marker(result["data_schema"], field).default() == value
    assert FlowClient.instances == []
    assert not hasattr(instance, "selected_unique_id")


async def test_endpoint_schema_uses_box_number_selectors_without_a_range(monkeypatch):
    instance = _flow(monkeypatch)
    result = await instance.async_step_user()
    schema = result["data_schema"]
    unit_marker = _marker(schema, "unit_id")
    port_marker = _marker(schema, "port")

    for field in ("port", "unit_id", "scan_interval"):
        selector_ = schema.schema[_marker(schema, field)]
        assert isinstance(selector_, FakeNumberSelector)
        assert selector_.config == {"step": "any", "mode": "box"}
    assert unit_marker.default() == 1
    assert port_marker.default() == 502
    assert type(schema({"host": "inverter"})["port"]) is int
    assert schema({"host": "inverter", "unit_id": 247})["unit_id"] == 247


@pytest.mark.parametrize(("field", "value", "_error"), ENDPOINT_NUMBER_ERRORS)
async def test_endpoint_schema_lets_an_out_of_range_number_reach_the_step_handler(
    monkeypatch, field, value, _error
):
    _use_home_assistant_number_selector(monkeypatch)
    instance = _flow(monkeypatch)
    schema = (await instance.async_step_user())["data_schema"]

    assert schema({"host": "inverter", field: value})[field] == value


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
        "data": {**SAVED_DATA, "model": "beta", "device_type": UNRECOGNISED_TYPE},
        "options": {"scan_interval": 30, "prefix": "", "allow_control": False},
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

    async def failing_read(client, device, enabled):
        del client, device, enabled
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
        entry_id="entry-b",
        unique_id="OTHER",
        data={"host": "other"},
        options={"prefix": "other"},
    )
    instance = _flow(monkeypatch, entries=[other])
    monkeypatch.setattr(config_flow, "identify", _identifying(_assumed_device()))
    await instance.async_step_user({**INPUT, "model": "beta"})
    other.data = {"host": "inverter", "port": 502, "unit_id": 1}

    result = await instance.async_step_confirm_model({})

    assert result == _abort(reason="already_configured")
    assert not hasattr(instance, "selected_unique_id")


STORED_DEVICE_TYPES = {"automatic": 0x0001, "alpha": 0x0001, "beta": 0x0002}


def _saved_entry(*, entry_id="entry-a", serial=SERIAL, model="automatic", prefix=""):
    return SimpleNamespace(
        entry_id=entry_id,
        unique_id=serial,
        title=f"SAJ {serial}",
        data={
            **SAVED_DATA,
            "model": model,
            "device_type": STORED_DEVICE_TYPES[model],
        },
        options={"scan_interval": 45, "prefix": prefix},
        subentries={},
        update_count=0,
    )


def _options_flow(monkeypatch, *, entry, entries=None):
    instance = object.__new__(config_flow.SajOptionsFlow)
    instance.hass = SimpleNamespace(
        config_entries=FakeConfigEntries(entries if entries is not None else [entry]),
        config=SimpleNamespace(components=set(), language="en"),
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
    assert entry.options == (options or {"scan_interval": 45, "prefix": ""})
    assert entry.unique_id == serial
    assert entry.update_count == 0


async def test_options_form_prefills_the_seven_fields_from_saved_state(monkeypatch):
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
        "prefix",
        "allow_control",
    ]
    assert _marker(schema, "allow_control").default() is False
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
    assert entry.options == {"scan_interval": 60, "prefix": "", "allow_control": False}
    assert entry.update_count == 1


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"port": "invalid"}, "invalid_endpoint"),
        ({"unit_id": "invalid"}, "invalid_endpoint"),
    ],
)
async def test_options_step_rejects_non_numeric_endpoint_fields(
    monkeypatch, changes, reason
):
    entry = _saved_entry()
    flow = _options_flow(monkeypatch, entry=entry)

    result = await flow.async_step_init(_submission(**changes))

    assert result["errors"] == {"base": reason}
    _unchanged(entry)
    assert FlowClient.instances == []


@pytest.mark.parametrize(
    ("field", "value", "error"),
    [
        *ENDPOINT_NUMBER_ERRORS,
        ("scan_interval", "invalid", "invalid_scan_interval"),
    ],
)
async def test_options_step_reports_a_bad_number_on_its_field_and_keeps_the_input(
    monkeypatch, field, value, error
):
    entry = _saved_entry()
    flow = _options_flow(monkeypatch, entry=entry)

    result = await flow.async_step_init(_submission(**{field: value}))

    assert result["type"] == "form"
    assert result["errors"] == {field: error}
    assert _marker(result["data_schema"], field).default() == value
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
    assert entry.options == {
        "scan_interval": expected_interval,
        "prefix": "",
        "allow_control": False,
    }
    assert entry.unique_id == SERIAL
    assert entry.update_count == 1


def _entry_with_neighbour(monkeypatch, *, serial, neighbour_host):
    entry = _saved_entry()
    other = _saved_entry(entry_id="entry-b", serial=serial, prefix="other")
    other.data = {**SAVED_DATA, "host": neighbour_host}
    return entry, other, _options_flow(monkeypatch, entry=entry, entries=[entry, other])


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

    async def read(client, device, enabled):
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

    async def refused(client, device, enabled):
        del client, device, enabled
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
    assert entry.data == {**SAVED_DATA, "host": new_host, "device_type": new_type}
    assert entry.options == {"scan_interval": 75, "prefix": "", "allow_control": False}
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
    assert result["description_placeholders"] == {
        "selection": "gamma",
        "load": "1.3",
        "budget": "40",
    }
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

    async def failing_read(client, device, enabled):
        del client, device, enabled
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
    entry, _other, flow = _entry_with_neighbour(
        monkeypatch, serial=REPLACEMENT_SERIAL, neighbour_host="other"
    )
    monkeypatch.setattr(
        config_flow,
        "identify",
        _identifying(_device(serial=REPLACEMENT_SERIAL)),
    )

    result = await flow.async_step_init(_submission(host="new-inverter"))

    assert result["errors"] == {"base": "already_configured"}
    _unchanged(entry)


@pytest.mark.parametrize(
    "step",
    [
        "confirm_model",
        "confirm_replacement",
        "confirm_prefix",
        "confirm_load",
        "confirm_control",
    ],
)
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
    assert entry.data == {
        **SAVED_DATA,
        "model": "beta",
        "device_type": UNRECOGNISED_TYPE,
    }
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
    entry, other, flow = _entry_with_neighbour(
        monkeypatch, serial="OTHER", neighbour_host="other"
    )
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
    entry, _other, flow = _entry_with_neighbour(
        monkeypatch, serial="OTHER", neighbour_host="new-inverter"
    )

    result = await flow.async_step_init(_submission(host="new-inverter"))

    assert result["errors"] == {"base": "already_configured"}
    assert FlowClient.instances == []
    _unchanged(entry)


async def test_connection_edit_rechecks_endpoint_ownership_after_validation(
    monkeypatch,
):
    entry, other, flow = _entry_with_neighbour(
        monkeypatch, serial="OTHER", neighbour_host="other"
    )

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
        assert result["options"] == {
            "scan_interval": interval,
            "prefix": "",
            "allow_control": False,
        }
    else:
        assert result["errors"] == {"scan_interval": "invalid_scan_interval"}
        assert FlowClient.instances == []


ENTRY_ID = "entry-a"
CATALOGUE_BLOCKS = {
    "battery_soc": "realtime",
    "pv_power": "realtime",
    "grid_power": "energy",
}
ENABLED = frozenset({"pv_power", "grid_power", "battery_soc"})


def _registered(
    key, *, name=None, original_name="Original", domain="sensor", disabled_by=None
):
    return SimpleNamespace(
        disabled_by=disabled_by,
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


def _group_flow(
    monkeypatch,
    *,
    subentries=(),
    registered=REGISTERED,
    editing=None,
    blocks=CATALOGUE_BLOCKS,
):
    entry = SimpleNamespace(
        entry_id=ENTRY_ID,
        data={"model": "automatic", "device_type": GAMMA_TYPE},
        options={"scan_interval": 60},
        subentries={subentry.subentry_id: subentry for subentry in subentries},
    )
    flow = object.__new__(config_flow.SajPollingGroupFlow)
    flow.updates = []
    flow.created = []
    flow.hass = SimpleNamespace(
        config_entries=SimpleNamespace(
            async_get_known_entry=lambda _entry_id: entry,
            async_update_subentry=lambda **changes: flow.updates.append(changes),
        ),
        config=SimpleNamespace(language="en"),
    )
    flow.handler = (ENTRY_ID, "polling_group")
    flow.context = {"source": "user"}
    if editing is not None:
        flow.context = {"source": "reconfigure", "subentry_id": editing}
    flow.registered = list(registered)
    _nothing_enabled.keys = ENABLED
    monkeypatch.setattr(config_flow.er, "async_get", lambda _hass: "registry")
    monkeypatch.setattr(
        config_flow.er,
        "async_entries_for_config_entry",
        lambda registry, entry_id: (
            flow.registered if (registry, entry_id) == ("registry", ENTRY_ID) else []
        ),
    )
    monkeypatch.setattr(
        config_flow,
        "blocks_by_key",
        lambda *, profile, device_type: (
            dict(blocks) if (profile, device_type) == (GAMMA, GAMMA_TYPE) else {}
        ),
    )
    monkeypatch.setattr(flow, "async_show_form", _form)
    monkeypatch.setattr(flow, "async_abort", _abort)
    monkeypatch.setattr(
        flow,
        "async_show_menu",
        lambda *, step_id, menu_options, description_placeholders: {
            "type": "menu",
            "step_id": step_id,
            "menu_options": menu_options,
            "description_placeholders": description_placeholders,
        },
    )
    monkeypatch.setattr(
        flow,
        "async_create_entry",
        lambda *, title, data: (
            flow.created.append((title, data))
            or {"type": "create_entry", "title": title, "data": data}
        ),
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


@pytest.mark.parametrize("editing", [False, True])
async def test_the_form_describes_the_current_request_load(monkeypatch, *, editing):
    flow, _ = _group_flow(
        monkeypatch,
        subentries=[_group("g1", ["pv_power", "grid_power"], interval=10)],
        editing="g1" if editing else None,
    )
    step = flow.async_step_reconfigure if editing else flow.async_step_user

    form = await step()

    assert form["description_placeholders"] == {"load": "13", "budget": "40"}


async def test_the_load_comes_from_the_stored_device_enabled_entities_and_cadences(
    monkeypatch,
):
    group = _group("g1", ["pv_power"], interval=20)
    flow, entry = _group_flow(monkeypatch, subentries=[group])
    entry.options["scan_interval"] = 45

    await flow.async_step_user()

    assert [
        {key: value for key, value in call.items() if key != "groups"}
        for call in _one_request_per_key.asked
    ] == [
        {
            "profile": GAMMA,
            "device_type": GAMMA_TYPE,
            "enabled": ENABLED,
            "default_interval": 45,
        }
    ]
    assert _one_request_per_key.asked[0]["groups"] == [
        config_flow.Cadence(interval=20, keys=frozenset({"pv_power"}))
    ]
    asked = _nothing_enabled.asked[0]
    assert asked["entry_id"] == ENTRY_ID
    assert {register.key for register in asked["registers"]} == {
        "pv_power",
        "grid_power",
        "battery_soc",
    }


async def test_a_valid_submission_is_not_saved_until_the_save_choice(monkeypatch):
    flow, _ = _group_flow(monkeypatch)

    review = await flow.async_step_user(
        _group_input(scan_interval=15.0, sensors=["pv_power", "grid_power"])
    )

    assert review["type"] == "menu"
    assert review["step_id"] == "review_group"
    assert review["menu_options"] == ["save_group", "change_selection"]
    assert flow.created == []
    assert flow.updates == []

    saved = await flow.async_step_save_group()

    assert saved == {
        "type": "create_entry",
        "title": "Power",
        "data": {"scan_interval": 15, "sensors": ["pv_power", "grid_power"]},
    }
    assert type(saved["data"]["scan_interval"]) is int
    assert flow.updates == []


async def test_the_result_step_shows_the_group_requests_and_the_load_before_and_after(
    monkeypatch,
):
    flow, _ = _group_flow(monkeypatch)

    review = await flow.async_step_user(
        _group_input(scan_interval=10, sensors=["pv_power", "grid_power"])
    )

    assert review["description_placeholders"] == {
        "requests": "2",
        "before": "1",
        "after": "13",
        "budget": "40",
    }


async def test_only_enabled_entities_cost_requests_in_the_result_step(monkeypatch):
    flow, _ = _group_flow(monkeypatch)
    _nothing_enabled.keys = frozenset({"pv_power"})

    review = await flow.async_step_user(
        _group_input(scan_interval=10, sensors=["pv_power", "grid_power"])
    )

    assert review["description_placeholders"]["requests"] == "1"
    assert _one_request_per_key.asked[-1]["enabled"] == {"pv_power"}


async def test_the_result_step_of_an_edit_replaces_the_group_in_the_load_after(
    monkeypatch,
):
    group = _group("g1", ["pv_power"], title="Old", interval=10)
    flow, entry = _group_flow(monkeypatch, subentries=[group], editing="g1")

    review = await flow.async_step_reconfigure(
        _group_input(name="New", scan_interval=30, sensors=["grid_power"])
    )

    assert review["step_id"] == "review_group"
    assert review["description_placeholders"] == {
        "requests": "1",
        "before": "7",
        "after": "3",
        "budget": "40",
    }
    assert flow.updates == []

    result = await flow.async_step_save_group()

    assert result == _abort(reason="reconfigure_successful")
    assert len(flow.updates) == 1
    update = flow.updates[0]
    assert update["entry"] is entry
    assert update["subentry"] is group
    assert update["title"] == "New"
    assert update["data"] == {"scan_interval": 30, "sensors": ["grid_power"]}


@pytest.mark.parametrize(
    ("key_count", "step_id"),
    [(7, "review_group"), (8, "review_group_over_budget")],
)
async def test_the_result_step_says_so_when_the_load_with_the_group_is_over_the_budget(
    monkeypatch, key_count, step_id
):
    flow, entry = _group_flow(monkeypatch)
    entry.options["scan_interval"] = 12
    keys = [f"key_{index}" for index in range(key_count)]

    review = await flow.async_step_user(_group_input(scan_interval=12, sensors=keys))

    assert review["step_id"] == step_id
    assert review["menu_options"] == ["save_group", "change_selection"]
    assert flow.created == []
    saved = await flow.async_step_save_group()
    assert saved["type"] == "create_entry"


@pytest.mark.parametrize("editing", [False, True])
async def test_change_selection_returns_to_the_form_with_the_submission_kept(
    monkeypatch, *, editing
):
    group = _group("g1", ["grid_power"])
    flow, _ = _group_flow(
        monkeypatch, subentries=[group], editing="g1" if editing else None
    )
    step = flow.async_step_reconfigure if editing else flow.async_step_user
    submitted = _group_input(name="Mine", scan_interval=25, sensors=["pv_power"])
    await step(submitted)

    form = await flow.async_step_change_selection()

    assert form["type"] == "form"
    assert form["step_id"] == ("reconfigure" if editing else "user")
    schema = form["data_schema"]
    assert _marker(schema, "name").default() == "Mine"
    assert _marker(schema, "scan_interval").default() == 25
    assert _marker(schema, "sensors").default() == ["pv_power"]
    assert form["description_placeholders"] == {"load": "7", "budget": "40"}
    assert flow.created == []
    assert flow.updates == []


@pytest.mark.parametrize(
    "step", ["async_step_review_group", "async_step_review_group_over_budget"]
)
async def test_the_result_step_shows_the_same_figures_when_it_is_entered_again(
    monkeypatch, step
):
    flow, _ = _group_flow(monkeypatch)
    review = await flow.async_step_user(
        _group_input(sensors=["pv_power", "grid_power"])
    )

    again = await getattr(flow, step)({})

    assert again == review


async def test_a_changed_selection_goes_through_the_result_step_again(monkeypatch):
    flow, _ = _group_flow(monkeypatch)
    await flow.async_step_user(_group_input(sensors=["pv_power"]))
    await flow.async_step_change_selection()

    review = await flow.async_step_user(
        _group_input(sensors=["pv_power", "grid_power"])
    )

    assert review["description_placeholders"]["requests"] == "2"
    assert flow.created == []
    saved = await flow.async_step_save_group()
    assert saved["data"]["sensors"] == ["pv_power", "grid_power"]


@pytest.mark.parametrize(
    "step",
    [
        "async_step_save_group",
        "async_step_change_selection",
        "async_step_review_group",
        "async_step_review_group_over_budget",
    ],
)
async def test_the_result_choices_need_a_validated_submission(monkeypatch, step):
    flow, _ = _group_flow(monkeypatch)

    assert await getattr(flow, step)() == _abort(reason="confirmation_not_pending")


@pytest.mark.parametrize("interval", [2, 9, 0, -10, 12.5, "fast", None])
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
    assert _marker(result["data_schema"], "scan_interval").default() == interval
    assert flow.updates == []
    assert flow.created == []


@pytest.mark.parametrize("interval", [2, -10, 12.5])
async def test_group_schema_lets_an_out_of_range_interval_reach_the_step_handler(
    monkeypatch, interval
):
    _use_home_assistant_number_selector(monkeypatch)
    flow, _ = _group_flow(monkeypatch)
    schema = (await flow.async_step_user())["data_schema"]

    assert schema(_group_input(scan_interval=interval))["scan_interval"] == interval


async def test_a_submission_without_sensors_is_reported_on_the_sensors_field(
    monkeypatch,
):
    flow, _ = _group_flow(monkeypatch)

    result = await flow.async_step_user(_group_input(sensors=[]))

    assert result["type"] == "form"
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
async def test_an_installation_without_entities_cannot_have_groups(
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


async def test_adding_with_every_entity_already_grouped_is_aborted_with_a_reason(
    monkeypatch,
):
    groups = [
        _group("g1", ["pv_power", "grid_power"]),
        _group("g2", ["battery_soc"]),
    ]
    flow, _ = _group_flow(monkeypatch, subentries=groups)

    assert await flow.async_step_user() == _abort(reason="all_sensors_assigned")


async def test_editing_a_group_that_holds_every_entity_still_shows_the_form(
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


async def test_options_exclude_entities_of_other_groups_and_include_the_groups_own(
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


async def test_an_entity_released_by_one_group_is_offered_to_another(monkeypatch):
    first, second = _group("g1", ["pv_power"]), _group("g2", ["grid_power"])
    flow, entry = _group_flow(monkeypatch, subentries=[first, second], editing="g2")
    assert "pv_power" not in _offered(await flow.async_step_reconfigure())

    entry.subentries["g1"] = _group("g1", [])

    assert "pv_power" in _offered(await flow.async_step_reconfigure())


async def test_options_are_labelled_with_their_block_and_the_names_users_see(
    monkeypatch,
):
    registered = [
        _registered("pv_power", name="Roof", original_name="Solar power"),
        _registered("grid_power", original_name="Grid power"),
        _registered("battery_soc", name=None, original_name=None),
        _registered("load_power", original_name="Other entry"),
    ]
    registered[3].unique_id = "other-entry_load_power"
    flow, _ = _group_flow(monkeypatch, registered=registered)

    offered = _offered(await flow.async_step_user())

    assert offered == {
        "battery_soc": "Realtime: battery_soc",
        "pv_power": "Realtime: Roof",
        "grid_power": "Energy: Grid power",
    }


async def test_a_block_without_a_translation_is_labelled_by_its_name(monkeypatch):
    flow, _ = _group_flow(monkeypatch, blocks={"pv_power": "parallel"})

    assert _offered(await flow.async_step_user()) == {
        "pv_power": "parallel: Solar power"
    }


async def test_options_are_listed_in_register_order(monkeypatch):
    flow, _ = _group_flow(monkeypatch)

    offered = _offered(await flow.async_step_user())

    assert list(offered) == ["battery_soc", "pv_power", "grid_power"]


@pytest.mark.parametrize(
    ("disabled_by", "label"),
    [
        (None, "Realtime: Solar power"),
        ("user", "Realtime: Solar power (disabled)"),
        ("integration", "Realtime: Solar power (disabled)"),
    ],
)
async def test_a_disabled_entity_is_still_offered_and_says_it_is_disabled(
    monkeypatch, disabled_by, label
):
    entity = _registered(
        "pv_power", original_name="Solar power", disabled_by=disabled_by
    )
    flow, _ = _group_flow(monkeypatch, registered=[entity])

    assert _offered(await flow.async_step_user()) == {"pv_power": label}


async def test_a_group_may_hold_enabled_entities_of_several_domains(monkeypatch):
    registered = [
        _registered("pv_power", original_name="Solar power"),
        _registered("backup_reserve_soc", original_name="Reserve", domain="number"),
        _registered("ethernet_mode", original_name="Mode", domain="select"),
        _registered("battery_charge_enable", original_name="Charge", domain="switch"),
    ]
    blocks = dict.fromkeys(
        ("backup_reserve_soc", "ethernet_mode", "battery_charge_enable", "pv_power"),
        "settings",
    )
    flow, _ = _group_flow(monkeypatch, registered=registered, blocks=blocks)
    keys = list(blocks)
    _nothing_enabled.keys = frozenset(keys)

    form = await flow.async_step_user()
    review = await flow.async_step_user(_group_input(sensors=keys))
    saved = await flow.async_step_save_group()

    assert set(_offered(form)) == set(keys)
    assert review["description_placeholders"]["requests"] == "4"
    assert saved["data"]["sensors"] == keys


async def test_editing_works_while_the_entry_is_not_loaded(monkeypatch):
    group = _group("g1", ["pv_power"])
    flow, entry = _group_flow(monkeypatch, subentries=[group], editing="g1")
    assert not hasattr(entry, "runtime_data")

    form = await flow.async_step_reconfigure()
    review = await flow.async_step_reconfigure(_group_input())

    assert form["type"] == "form"
    assert review["type"] == "menu"


async def test_stale_entities_are_hidden_when_editing_and_dropped_on_save(monkeypatch):
    group = _group("g1", ["pv_power", "no_longer_exists"])
    flow, _ = _group_flow(monkeypatch, subentries=[group], editing="g1")

    form = await flow.async_step_reconfigure()
    shown = _marker(form["data_schema"], "sensors").default()
    await flow.async_step_reconfigure(_group_input(sensors=shown))
    await flow.async_step_save_group()

    assert shown == ["pv_power"]
    assert flow.updates[0]["data"]["sensors"] == ["pv_power"]


async def test_groups_of_other_subentry_types_do_not_own_entities(monkeypatch):
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


async def _read_refused(client, device, enabled):
    del client, device, enabled
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


def _id(prefix, key):
    return f"sensor.saj_{prefix}_{key}" if prefix else f"sensor.saj_{key}"


def _prefix_error(result):
    return result["errors"].get("prefix")


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", ""),
        ("house", "house"),
        ("  House  ", "house"),
        ("HOUSE", "house"),
        ("a", "a"),
        ("9lives", "9lives"),
        ("garage2", "garage2"),
        ("x" * 32, "x" * 32),
    ],
)
def test_a_well_formed_prefix_is_trimmed_and_lowercased(value, expected):
    checked = config_flow.validate_prefix(
        value=value, other_prefixes=set(), catalogue_keys=set()
    )

    assert checked == config_flow.PrefixCheck(prefix=expected, error=None)


@pytest.mark.parametrize(
    "value",
    [
        "_house",
        "house_",
        "a_b",
        "garage_2",
        "ho_use",
        "a__b",
        "a-b",
        "a b",
        "a.b",
        "house!",
        "x" * 33,
        "caf\u00e9",
        "_",
        5,
        None,
        ["house"],
    ],
)
def test_a_malformed_prefix_is_rejected_not_rewritten(value):
    checked = config_flow.validate_prefix(
        value=value, other_prefixes=set(), catalogue_keys=set()
    )

    assert checked.error == "invalid_prefix"


@pytest.mark.parametrize(
    ("value", "others", "error"),
    [
        ("house", {"house"}, "prefix_in_use"),
        ("HOUSE", {"house"}, "prefix_in_use"),
        ("", {""}, "prefix_in_use"),
        ("", {"house"}, None),
        ("house", {"", "garage"}, None),
    ],
)
def test_a_prefix_is_unique_across_installations_and_empty_counts_as_a_value(
    value, others, error
):
    checked = config_flow.validate_prefix(
        value=value, other_prefixes=others, catalogue_keys=set()
    )

    assert checked.error == error


@pytest.mark.parametrize(
    ("value", "error"),
    [
        ("battery", "prefix_shadows_entity"),
        ("pv", "prefix_shadows_entity"),
        ("backup", "prefix_shadows_entity"),
        ("batterypower", None),
        ("bat", None),
        ("power", None),
        ("", None),
    ],
)
def test_a_prefix_may_not_start_a_sensor_key_of_any_supported_model(value, error):
    checked = config_flow.validate_prefix(
        value=value,
        other_prefixes=set(),
        catalogue_keys={"battery_power", "pv_power", "backup_reserve_soc"},
    )

    assert checked.error == error


def test_a_malformed_prefix_is_reported_before_it_is_compared_with_anything():
    checked = config_flow.validate_prefix(
        value="Pv__x", other_prefixes={"pv__x"}, catalogue_keys={"pv__x_a"}
    )

    assert checked.error == "invalid_prefix"


def test_the_prefix_context_gathers_every_prefix_and_the_keys_of_every_model():
    entries = [
        SimpleNamespace(options={"prefix": "house"}),
        SimpleNamespace(options={"prefix": ""}),
        SimpleNamespace(options={}),
    ]

    context = config_flow.prefix_context(entries=entries)

    assert context.other_prefixes == {"house", ""}
    assert context.catalogue_keys == {"pv_power", "grid_power", "battery_soc"}


@pytest.mark.parametrize(
    ("taken", "expected"),
    [
        (set(), None),
        ({"sensor.saj_b"}, "sensor.saj_b"),
        ({"sensor.saj_c", "sensor.saj_a"}, "sensor.saj_a"),
    ],
)
def test_the_first_taken_entity_id_is_named(taken, expected):
    def is_taken(*, entity_id):
        return entity_id in taken

    found = config_flow.first_taken_entity_id(
        entity_ids=["sensor.saj_c", "sensor.saj_a", "sensor.saj_b"], is_taken=is_taken
    )

    assert found == expected


@pytest.mark.parametrize(
    ("recorded", "expected"),
    [
        (set(), None),
        ({"sensor.saj_c"}, "sensor.saj_c"),
        ({"sensor.saj_b", "sensor.saj_a", "elsewhere"}, "sensor.saj_a"),
    ],
)
async def test_the_first_entity_id_with_statistics_comes_from_one_lookup(
    recorded, expected
):
    lookups = []

    async def lookup(*, entity_ids):
        lookups.append(list(entity_ids))
        return recorded

    found = await config_flow.first_entity_id_with_statistics(
        entity_ids=["sensor.saj_c", "sensor.saj_a", "sensor.saj_b"],
        recorded_among=lookup,
    )

    assert found == expected
    assert lookups == [["sensor.saj_a", "sensor.saj_b", "sensor.saj_c"]]


async def test_recorded_statistic_ids_keep_only_the_recorders_own_statistics(
    monkeypatch,
):
    asked = []

    async def listed(hass, statistic_ids):
        asked.append((hass, statistic_ids))
        return [
            {"statistic_id": "sensor.saj_a", "source": "recorder"},
            {"statistic_id": "sensor.saj_b", "source": "some_integration"},
        ]

    monkeypatch.setattr(config_flow, "async_list_statistic_ids", listed)

    found = await config_flow._recorded_statistic_ids(
        hass="hass", entity_ids=["sensor.saj_a", "sensor.saj_b"]
    )

    assert found == {"sensor.saj_a"}
    assert asked == [("hass", {"sensor.saj_a", "sensor.saj_b"})]


def _conflict_hass(*, components=("recorder",)):
    return SimpleNamespace(config=SimpleNamespace(components=set(components)))


async def _find_conflict(monkeypatch, *, taken=(), recorded=(), **overrides):
    lookups = []

    def in_use(*, hass, entity_id):
        del hass
        return entity_id in taken

    async def statistics(*, hass, entity_ids):
        del hass
        lookups.append(sorted(entity_ids))
        return {entity_id for entity_id in entity_ids if entity_id in recorded}

    monkeypatch.setattr(config_flow, "entity_id_in_use", in_use)
    monkeypatch.setattr(config_flow, "_recorded_statistic_ids", statistics)
    arguments = {
        "hass": _conflict_hass(),
        "context": config_flow.PrefixContext(frozenset(), frozenset()),
        "prefix": "house",
        "domains": {"pv_power": "sensor", "backup_reserve_soc": "number"},
        "check_statistics": True,
        **overrides,
    }
    return await config_flow.find_prefix_conflict(**arguments), lookups


async def test_no_conflict_when_nothing_is_taken_and_no_statistics_exist(monkeypatch):
    conflict, lookups = await _find_conflict(monkeypatch)

    assert conflict is None
    assert lookups == [
        ["number.saj_house_backup_reserve_soc", "sensor.saj_house_pv_power"]
    ]


async def test_a_taken_entity_id_is_reported_on_the_prefix_field_naming_the_id(
    monkeypatch,
):
    conflict, lookups = await _find_conflict(
        monkeypatch,
        taken={"sensor.saj_house_pv_power", "number.saj_house_backup_reserve_soc"},
    )

    assert conflict.errors == {"prefix": "entity_id_taken"}
    assert conflict.placeholders == {"entity_id": "number.saj_house_backup_reserve_soc"}
    assert lookups == []


async def test_existing_statistics_are_reported_on_the_prefix_field_naming_the_id(
    monkeypatch,
):
    conflict, _ = await _find_conflict(
        monkeypatch, recorded={"sensor.saj_house_pv_power"}
    )

    assert conflict.errors == {"prefix": "statistics_exist"}
    assert conflict.placeholders == {"entity_id": "sensor.saj_house_pv_power"}


@pytest.mark.parametrize(
    "overrides",
    [
        {"check_statistics": False},
        {"hass": _conflict_hass(components=())},
    ],
)
async def test_statistics_are_not_looked_up_when_not_wanted_or_no_recorder_runs(
    monkeypatch, overrides
):
    conflict, lookups = await _find_conflict(
        monkeypatch, recorded={"sensor.saj_house_pv_power"}, **overrides
    )

    assert conflict is None
    assert lookups == []


async def test_a_rule_breaking_prefix_is_a_conflict_without_any_lookup(monkeypatch):
    conflict, lookups = await _find_conflict(
        monkeypatch,
        prefix="house",
        context=config_flow.PrefixContext(frozenset({"house"}), frozenset()),
    )

    assert conflict.errors == {"prefix": "prefix_in_use"}
    assert conflict.placeholders == {}
    assert lookups == []


def _other_entry(prefix="other"):
    return SimpleNamespace(
        entry_id="entry-b",
        unique_id="OTHER",
        data={"host": "other", "port": 502, "unit_id": 1},
        options={"prefix": prefix},
    )


def _gamma():
    return _identifying(_device(profile=GAMMA, device_type=0x0003))


def _taking(*entity_ids):
    def in_use(*, hass, entity_id):
        del hass
        return entity_id in entity_ids

    return in_use


def test_the_prefix_field_suggests_a_value_and_has_no_default():
    schema = config_flow._endpoint_schema(defaults={"prefix": "house"})
    marker = _marker(schema, "prefix")

    assert marker.description == {"suggested_value": "house"}
    assert marker.default is config_flow.vol.UNDEFINED
    assert "prefix" not in schema({"host": "inverter"})


async def test_setup_stores_the_normalised_prefix_in_the_entry_options(monkeypatch):
    instance = _flow(monkeypatch)

    result = await instance.async_step_user({**INPUT, "prefix": "  House "})

    assert result["options"] == {
        "scan_interval": 30,
        "prefix": "house",
        "allow_control": False,
    }
    assert "prefix" not in result["data"]


async def test_setup_treats_a_cleared_prefix_field_as_empty(monkeypatch):
    instance = _flow(monkeypatch)

    result = await instance.async_step_user(dict(INPUT))

    assert result["options"]["prefix"] == ""


@pytest.mark.parametrize(
    ("prefix", "other_prefix", "error"),
    [
        ("house", "house", "prefix_in_use"),
        ("", "", "prefix_in_use"),
        ("Bad Prefix", "other", "invalid_prefix"),
        ("pv", "other", "prefix_shadows_entity"),
    ],
)
async def test_setup_refuses_a_bad_prefix_on_the_prefix_field_before_connecting(
    monkeypatch, prefix, other_prefix, error
):
    other = _other_entry(prefix=other_prefix)
    other.data = {"host": "other", "port": 502, "unit_id": 1}
    instance = _flow(monkeypatch, entries=[other])
    monkeypatch.setattr(config_flow, "identify", _gamma())

    result = await instance.async_step_user({**INPUT, "prefix": prefix})

    assert result["step_id"] == "user"
    assert result["errors"] == {"prefix": error}
    assert FlowClient.instances == []
    assert _marker(result["data_schema"], "prefix").description == {
        "suggested_value": prefix
    }


async def test_setup_refuses_a_prefix_whose_entity_id_is_taken_naming_the_first(
    monkeypatch,
):
    instance = _flow(monkeypatch)
    monkeypatch.setattr(config_flow, "identify", _gamma())
    monkeypatch.setattr(
        config_flow,
        "entity_id_in_use",
        _taking("sensor.saj_house_pv_power", "sensor.saj_house_grid_power"),
    )

    result = await instance.async_step_user({**INPUT, "prefix": "house"})

    assert result["step_id"] == "user"
    assert result["errors"] == {"prefix": "entity_id_taken"}
    assert result["description_placeholders"] == {
        "entity_id": "sensor.saj_house_grid_power"
    }
    assert not hasattr(instance, "selected_unique_id")


async def test_setup_accepts_a_prefix_whose_entity_ids_are_free(monkeypatch):
    instance = _flow(monkeypatch)
    monkeypatch.setattr(config_flow, "identify", _gamma())
    monkeypatch.setattr(config_flow, "entity_id_in_use", _taking("sensor.saj_pv_power"))

    result = await instance.async_step_user({**INPUT, "prefix": "house"})

    assert result["type"] == "create_entry"


async def test_setup_never_consults_the_recorder(monkeypatch):
    instance = _flow(monkeypatch)
    instance.hass.config.components.add("recorder")
    monkeypatch.setattr(config_flow, "identify", _gamma())

    async def exploding(*, hass, entity_ids):
        raise AssertionError

    monkeypatch.setattr(config_flow, "_recorded_statistic_ids", exploding)

    result = await instance.async_step_user({**INPUT, "prefix": "house"})

    assert result["type"] == "create_entry"


async def test_setup_rechecks_the_prefix_when_the_model_is_confirmed(monkeypatch):
    other = _other_entry()
    instance = _flow(monkeypatch, entries=[other])
    monkeypatch.setattr(config_flow, "identify", _identifying(_assumed_device()))
    await instance.async_step_user({**INPUT, "model": "beta", "prefix": "house"})
    other.options = {"prefix": "house"}

    result = await instance.async_step_confirm_model({})

    assert result["step_id"] == "user"
    assert result["errors"] == {"prefix": "prefix_in_use"}
    assert _marker(result["data_schema"], "prefix").description == {
        "suggested_value": "house"
    }
    assert _marker(result["data_schema"], "model").default() == "beta"
    assert not hasattr(instance, "selected_unique_id")


async def test_setup_confirmation_creates_the_entry_with_its_prefix(monkeypatch):
    instance = _flow(monkeypatch)
    monkeypatch.setattr(config_flow, "identify", _identifying(_assumed_device()))
    await instance.async_step_user({**INPUT, "model": "beta", "prefix": "house"})

    result = await instance.async_step_confirm_model({})

    assert result["options"] == {
        "scan_interval": 30,
        "prefix": "house",
        "allow_control": False,
    }


class FakeEntityRegistry:
    def __init__(self, entities, events) -> None:
        self.entities = entities
        self.events = events

    def async_update_entity(self, entity_id, *, new_entity_id):
        self.events.append(("rename", entity_id, new_entity_id))
        next(
            entity for entity in self.entities if entity.entity_id == entity_id
        ).entity_id = new_entity_id


def _registered_entity(
    key, *, prefix="", entity_id=None, domain="sensor", owner="entry-a"
):
    return SimpleNamespace(
        entity_id=entity_id or _id(prefix, key),
        unique_id=f"{owner}_{key}",
        domain=domain,
        name=None,
        original_name=key,
    )


def _prefix_flow(monkeypatch, *, saved_prefix="", entities=None, others=()):
    entry = _saved_entry(prefix=saved_prefix)
    flow = _options_flow(monkeypatch, entry=entry, entries=[entry, *others])
    registered = (
        entities
        if entities is not None
        else [
            _registered_entity(key, prefix=saved_prefix)
            for key in ("pv_power", "grid_power")
        ]
    )
    registry = FakeEntityRegistry(registered, flow.hass.config_entries.events)
    monkeypatch.setattr(config_flow.er, "async_get", lambda _hass: registry)
    monkeypatch.setattr(
        config_flow.er,
        "async_entries_for_config_entry",
        lambda found, entry_id: found.entities if entry_id == "entry-a" else [],
    )
    monkeypatch.setattr(config_flow, "identify", _gamma())
    return entry, flow


def _renames(flow):
    return [
        event for event in flow.hass.config_entries.events if event != "update_entry"
    ]


async def test_the_options_form_suggests_the_saved_prefix(monkeypatch):
    entry = _saved_entry(prefix="house")
    flow = _options_flow(monkeypatch, entry=entry)

    form = await flow.async_step_init()

    assert _marker(form["data_schema"], "prefix").description == {
        "suggested_value": "house"
    }


async def test_the_options_form_suggests_an_empty_prefix_when_none_was_saved(
    monkeypatch,
):
    entry = _saved_entry()
    del entry.options["prefix"]
    flow = _options_flow(monkeypatch, entry=entry)

    form = await flow.async_step_init()

    assert _marker(form["data_schema"], "prefix").description == {"suggested_value": ""}


async def test_an_unchanged_prefix_skips_confirmation_and_renames_nothing(
    monkeypatch,
):
    entry, flow = _prefix_flow(monkeypatch, saved_prefix="house")

    result = await flow.async_step_init(_submission(prefix="house", scan_interval=90))

    assert result == _abort(reason="changes_saved")
    assert entry.options == {
        "scan_interval": 90,
        "prefix": "house",
        "allow_control": False,
    }
    assert flow.hass.config_entries.events == ["update_entry"]


async def test_an_unchanged_prefix_is_not_checked_against_the_registry_or_recorder(
    monkeypatch,
):
    entry, flow = _prefix_flow(monkeypatch, saved_prefix="house")
    flow.hass.config.components.add("recorder")
    monkeypatch.setattr(
        config_flow,
        "entity_id_in_use",
        _taking("sensor.saj_house_pv_power"),
    )

    result = await flow.async_step_init(_submission(prefix="house"))

    assert result == _abort(reason="changes_saved")
    assert entry.update_count == 1


@pytest.mark.parametrize(
    ("old", "new", "expected_old", "expected_new"),
    [
        ("", "house", "<domain>.saj_<key>", "<domain>.saj_house_<key>"),
        ("house", "garage", "<domain>.saj_house_<key>", "<domain>.saj_garage_<key>"),
        ("house", "", "<domain>.saj_house_<key>", "<domain>.saj_<key>"),
    ],
)
async def test_adding_changing_or_removing_a_prefix_asks_for_confirmation_first(
    monkeypatch, old, new, expected_old, expected_new
):
    entry, flow = _prefix_flow(monkeypatch, saved_prefix=old)

    form = await flow.async_step_init(_submission(prefix=new))

    assert form["step_id"] == "confirm_prefix"
    assert form["description_placeholders"] == {
        "old_pattern": expected_old,
        "new_pattern": expected_new,
    }
    _unchanged(entry, options={"scan_interval": 45, "prefix": old})
    assert flow.hass.config_entries.events == []


async def test_the_prefix_prompt_is_shown_again_until_submitted(monkeypatch):
    _entry, flow = _prefix_flow(monkeypatch)
    await flow.async_step_init(_submission(prefix="house"))

    prompt = await flow.async_step_confirm_prefix()

    assert prompt["step_id"] == "confirm_prefix"
    assert flow.hass.config_entries.events == []


async def test_prefix_confirmation_without_a_pending_change_aborts(monkeypatch):
    _entry, flow = _prefix_flow(monkeypatch)

    assert await flow.async_step_confirm_prefix({}) == _abort(
        reason="confirmation_not_pending"
    )


@pytest.mark.parametrize(
    ("old", "new"), [("", "house"), ("house", "garage"), ("house", "")]
)
async def test_confirming_renames_every_entity_then_saves_the_prefix(
    monkeypatch, old, new
):
    entry, flow = _prefix_flow(monkeypatch, saved_prefix=old)
    await flow.async_step_init(_submission(prefix=new))

    result = await flow.async_step_confirm_prefix({})

    assert result == _abort(reason="changes_saved")
    assert flow.hass.config_entries.events == [
        ("rename", _id(old, "pv_power"), _id(new, "pv_power")),
        ("rename", _id(old, "grid_power"), _id(new, "grid_power")),
        "update_entry",
    ]
    assert entry.options == {"scan_interval": 45, "prefix": new, "allow_control": False}
    assert entry.update_count == 1


async def test_only_entities_at_the_id_the_old_prefix_produces_are_renamed(
    monkeypatch,
):
    entities = [
        _registered_entity("pv_power", prefix="house"),
        _registered_entity("grid_power", entity_id="sensor.my_grid"),
        _registered_entity("battery_soc", prefix="house", domain="switch"),
        _registered_entity("load_power", prefix="house", owner="entry-b"),
    ]
    _entry, flow = _prefix_flow(monkeypatch, saved_prefix="house", entities=entities)
    await flow.async_step_init(_submission(prefix="garage"))

    await flow.async_step_confirm_prefix({})

    assert _renames(flow) == [
        ("rename", "sensor.saj_house_pv_power", "sensor.saj_garage_pv_power")
    ]
    assert entities[1].entity_id == "sensor.my_grid"
    assert entities[2].entity_id == "sensor.saj_house_battery_soc"


@pytest.mark.parametrize(
    "domain", ["sensor", "number", "select", "switch", "time", "text"]
)
async def test_a_prefix_change_renames_the_entities_of_every_domain(
    monkeypatch, domain
):
    entities = [
        _registered_entity(
            "backup_reserve_soc",
            entity_id=f"{domain}.saj_house_backup_reserve_soc",
            domain=domain,
        )
    ]
    _entry, flow = _prefix_flow(monkeypatch, saved_prefix="house", entities=entities)
    await flow.async_step_init(_submission(prefix="garage"))

    await flow.async_step_confirm_prefix({})

    assert _renames(flow) == [
        (
            "rename",
            f"{domain}.saj_house_backup_reserve_soc",
            f"{domain}.saj_garage_backup_reserve_soc",
        )
    ]


async def test_the_new_ids_of_every_domain_are_checked_before_a_prefix_change(
    monkeypatch,
):
    entities = [
        _registered_entity(
            "backup_reserve_soc",
            entity_id="number.saj_backup_reserve_soc",
            domain="number",
        )
    ]
    _entry, flow = _prefix_flow(monkeypatch, entities=entities)
    monkeypatch.setattr(
        config_flow, "entity_id_in_use", _taking("number.saj_house_backup_reserve_soc")
    )

    result = await flow.async_step_init(_submission(prefix="house"))

    assert result["errors"] == {"prefix": "entity_id_taken"}
    assert result["description_placeholders"]["entity_id"] == (
        "number.saj_house_backup_reserve_soc"
    )
    assert flow.hass.config_entries.events == []


async def test_a_disabled_entity_is_renamed_like_any_other(monkeypatch):
    disabled = _registered_entity("pv_power")
    disabled.disabled_by = "user"
    _entry, flow = _prefix_flow(monkeypatch, entities=[disabled])
    await flow.async_step_init(_submission(prefix="house"))

    await flow.async_step_confirm_prefix({})

    assert _renames(flow) == [
        ("rename", "sensor.saj_pv_power", "sensor.saj_house_pv_power")
    ]


async def test_a_taken_target_id_refuses_the_change_before_confirmation(
    monkeypatch,
):
    _entry, flow = _prefix_flow(monkeypatch)
    monkeypatch.setattr(
        config_flow, "entity_id_in_use", _taking("sensor.saj_house_grid_power")
    )

    result = await flow.async_step_init(_submission(prefix="house"))

    assert result["step_id"] == "init"
    assert result["errors"] == {"prefix": "entity_id_taken"}
    assert result["description_placeholders"] == {
        "entity_id": "sensor.saj_house_grid_power",
        "load": "1.3",
        "budget": "40",
    }
    assert _marker(result["data_schema"], "prefix").description == {
        "suggested_value": "house"
    }
    assert flow.hass.config_entries.events == []


async def test_a_target_id_of_an_entity_from_an_earlier_model_is_checked_too(
    monkeypatch,
):
    entities = [_registered_entity("battery_soc")]
    _entry, flow = _prefix_flow(monkeypatch, entities=entities)
    monkeypatch.setattr(
        config_flow, "entity_id_in_use", _taking("sensor.saj_house_battery_soc")
    )

    result = await flow.async_step_init(_submission(prefix="house"))

    assert result["errors"] == {"prefix": "entity_id_taken"}


async def test_a_target_id_taken_during_confirmation_aborts_and_renames_nothing(
    monkeypatch,
):
    entry, flow = _prefix_flow(monkeypatch)
    await flow.async_step_init(_submission(prefix="house"))
    monkeypatch.setattr(
        config_flow, "entity_id_in_use", _taking("sensor.saj_house_grid_power")
    )

    result = await flow.async_step_confirm_prefix({})

    assert result == _abort(reason="prefix_unavailable")
    assert flow.hass.config_entries.events == []
    _unchanged(entry)


async def test_a_prefix_claimed_during_confirmation_aborts_and_renames_nothing(
    monkeypatch,
):
    other = _other_entry()
    entry, flow = _prefix_flow(monkeypatch, others=[other])
    await flow.async_step_init(_submission(prefix="house"))
    other.options = {"prefix": "house"}

    result = await flow.async_step_confirm_prefix({})

    assert result == _abort(reason="prefix_unavailable")
    assert flow.hass.config_entries.events == []
    _unchanged(entry)


async def test_statistics_under_a_target_id_refuse_the_change_naming_the_id(
    monkeypatch,
):
    _entry, flow = _prefix_flow(monkeypatch)
    flow.hass.config.components.add("recorder")
    calls = []

    async def listed(hass, statistic_ids):
        calls.append(statistic_ids)
        return [{"statistic_id": "sensor.saj_house_pv_power", "source": "recorder"}]

    monkeypatch.setattr(config_flow, "async_list_statistic_ids", listed)

    result = await flow.async_step_init(_submission(prefix="house"))

    assert result["errors"] == {"prefix": "statistics_exist"}
    assert result["description_placeholders"] == {
        "entity_id": "sensor.saj_house_pv_power",
        "load": "1.3",
        "budget": "40",
    }
    assert calls == [
        {
            "sensor.saj_house_pv_power",
            "sensor.saj_house_grid_power",
            "sensor.saj_house_battery_soc",
        }
    ]
    assert flow.hass.config_entries.events == []


async def test_statistics_appearing_during_confirmation_abort_and_rename_nothing(
    monkeypatch,
):
    _entry, flow = _prefix_flow(monkeypatch)
    flow.hass.config.components.add("recorder")

    async def none_yet(hass, statistic_ids):
        return []

    monkeypatch.setattr(config_flow, "async_list_statistic_ids", none_yet)
    await flow.async_step_init(_submission(prefix="house"))

    async def appeared(hass, statistic_ids):
        return [{"statistic_id": "sensor.saj_house_grid_power", "source": "recorder"}]

    monkeypatch.setattr(config_flow, "async_list_statistic_ids", appeared)

    result = await flow.async_step_confirm_prefix({})

    assert result == _abort(reason="prefix_unavailable")
    assert flow.hass.config_entries.events == []


async def test_without_a_recorder_the_statistics_check_is_skipped(monkeypatch):
    _entry, flow = _prefix_flow(monkeypatch)

    async def exploding(hass, statistic_ids):
        raise AssertionError

    monkeypatch.setattr(config_flow, "async_list_statistic_ids", exploding)

    form = await flow.async_step_init(_submission(prefix="house"))

    assert form["step_id"] == "confirm_prefix"


@pytest.mark.parametrize(
    ("prefix", "other_prefix", "error"),
    [
        ("other", "other", "prefix_in_use"),
        ("", "", "prefix_in_use"),
        ("Not Valid", "other", "invalid_prefix"),
        ("pv", "other", "prefix_shadows_entity"),
    ],
)
async def test_configure_refuses_a_bad_prefix_on_the_prefix_field_before_connecting(
    monkeypatch, prefix, other_prefix, error
):
    other = _other_entry(prefix=other_prefix)
    entry, flow = _prefix_flow(monkeypatch, saved_prefix="house", others=[other])

    result = await flow.async_step_init(_submission(prefix=prefix))

    assert result["errors"] == {"prefix": error}
    assert FlowClient.instances == []
    _unchanged(entry, options={"scan_interval": 45, "prefix": "house"})


async def test_the_prefix_is_confirmed_after_the_model_and_the_replacement(
    monkeypatch,
):
    entry, flow = _prefix_flow(monkeypatch)
    monkeypatch.setattr(
        config_flow,
        "identify",
        _identifying(_assumed_device(serial=REPLACEMENT_SERIAL)),
    )

    form = await flow.async_step_init(_submission(model="beta", prefix="house"))
    assert form["step_id"] == "confirm_model"
    form = await flow.async_step_confirm_model({})
    assert form["step_id"] == "confirm_replacement"
    form = await flow.async_step_confirm_replacement({})
    assert form["step_id"] == "confirm_prefix"
    assert flow.hass.config_entries.events == []
    result = await flow.async_step_confirm_prefix({})

    assert result == _abort(reason="changes_saved")
    assert entry.unique_id == REPLACEMENT_SERIAL
    assert entry.data["model"] == "beta"
    assert entry.options["prefix"] == "house"
    assert entry.update_count == 1


async def test_confirming_the_prefix_first_cannot_skip_the_other_confirmations(
    monkeypatch,
):
    _entry, flow = _prefix_flow(monkeypatch)
    monkeypatch.setattr(config_flow, "identify", _identifying(_assumed_device()))
    await flow.async_step_init(_submission(model="beta", prefix="house"))

    form = await flow.async_step_confirm_prefix({})

    assert form["step_id"] == "confirm_model"
    assert flow.hass.config_entries.events == []


@pytest.mark.parametrize(
    ("saved", "submitted", "neighbour_prefix"),
    [
        ("pv", "pv", "other"),
        ("bad_saved", " BAD_SAVED ", "other"),
        ("dup", "dup", "dup"),
    ],
)
async def test_a_saved_prefix_that_now_breaks_a_rule_does_not_block_other_changes(
    monkeypatch, saved, submitted, neighbour_prefix
):
    entry, flow = _prefix_flow(
        monkeypatch, saved_prefix=saved, others=[_other_entry(prefix=neighbour_prefix)]
    )

    result = await flow.async_step_init(_submission(prefix=submitted, scan_interval=90))

    assert result == _abort(reason="changes_saved")
    assert entry.options == {
        "scan_interval": 90,
        "prefix": saved,
        "allow_control": False,
    }
    assert flow.hass.config_entries.events == ["update_entry"]


@pytest.mark.parametrize(
    ("saved", "submitted", "error"),
    [
        ("pv", "pv2_", "invalid_prefix"),
        ("bad_saved", "bad_other", "invalid_prefix"),
        ("pv", "battery", "prefix_shadows_entity"),
        ("dup", "other", "prefix_in_use"),
    ],
)
async def test_changing_a_rule_breaking_saved_prefix_to_a_bad_value_is_still_refused(
    monkeypatch, saved, submitted, error
):
    entry, flow = _prefix_flow(
        monkeypatch, saved_prefix=saved, others=[_other_entry(prefix="other")]
    )
    entry.data = {**entry.data, "device_type": 4}
    monkeypatch.setattr(
        config_flow,
        "PROFILES",
        (
            profile(
                base=HS3,
                key="delta",
                device_types={4},
                keys={"battery_power", "pv_power"},
                hand_verified=True,
            ),
        ),
    )

    result = await flow.async_step_init(_submission(prefix=submitted))

    assert result["errors"] == {"prefix": error}
    assert flow.hass.config_entries.events == []
    _unchanged(
        entry,
        data={**SAVED_DATA, "device_type": 4},
        options={"scan_interval": 45, "prefix": saved},
    )


def _entry_with_group(*, keys, interval=10):
    entry = _saved_entry()
    entry.subentries = {"g1": _group("g1", keys, interval=interval)}
    return entry


SIX_KEYS = [f"key_{index}" for index in range(6)]


@pytest.mark.parametrize(
    ("group_keys", "expected_load"),
    [([], "1.3"), (SIX_KEYS, "37.3")],
)
async def test_the_configure_form_describes_the_current_request_load(
    monkeypatch, group_keys, expected_load
):
    entry = _saved_entry()
    entry.subentries = {"g1": _group("g1", group_keys, interval=10)}
    flow = _options_flow(monkeypatch, entry=entry)

    form = await flow.async_step_init()

    assert form["description_placeholders"] == {"load": expected_load, "budget": "40"}


async def test_the_configure_load_comes_from_the_stored_device_and_enabled_entities(
    monkeypatch,
):
    entry = _entry_with_group(keys=["pv_power"], interval=20)
    _nothing_enabled.keys = frozenset({"pv_power"})
    flow = _options_flow(monkeypatch, entry=entry)

    await flow.async_step_init()

    call = _one_request_per_key.asked[0]
    assert (call["profile"], call["device_type"]) == (ALPHA, 0x0001)
    assert call["enabled"] == {"pv_power"}
    assert call["default_interval"] == 45
    assert call["groups"] == [
        config_flow.Cadence(interval=20, keys=frozenset({"pv_power"}))
    ]
    assert _nothing_enabled.asked[0]["entry_id"] == "entry-a"


@pytest.mark.parametrize(
    ("group_keys", "interval", "shown"),
    [
        (SIX_KEYS, 10, True),
        (SIX_KEYS, 20, False),
        (SIX_KEYS, 45, False),
        ([*SIX_KEYS, "key_6", "key_7"], 45, False),
        ([*SIX_KEYS, "key_6", "key_7"], 30, True),
        ([], 10, False),
    ],
)
async def test_the_load_is_confirmed_only_when_a_changed_interval_goes_over_budget(
    monkeypatch, group_keys, interval, *, shown
):
    entry = _entry_with_group(keys=group_keys)
    flow = _options_flow(monkeypatch, entry=entry)

    result = await flow.async_step_init(_submission(scan_interval=interval))

    if shown:
        assert result["step_id"] == "confirm_load"
        assert entry.update_count == 0
    else:
        assert result == _abort(reason="changes_saved")
        assert entry.options["scan_interval"] == interval


async def test_the_load_confirmation_shows_the_load_before_and_after(monkeypatch):
    entry = _entry_with_group(keys=SIX_KEYS)
    flow = _options_flow(monkeypatch, entry=entry)

    form = await flow.async_step_init(_submission(scan_interval=10))

    assert form["step_id"] == "confirm_load"
    assert form["description_placeholders"] == {
        "before": "37.3",
        "after": "42",
        "budget": "40",
    }
    after = _one_request_per_key.asked[0]
    assert after["default_interval"] == 10
    assert (after["profile"], after["device_type"]) == (ALPHA, 0x0001)


async def test_confirming_the_load_saves_the_interval_and_it_is_shown_until_confirmed(
    monkeypatch,
):
    entry = _entry_with_group(keys=SIX_KEYS)
    flow = _options_flow(monkeypatch, entry=entry)
    await flow.async_step_init(_submission(scan_interval=10))

    again = await flow.async_step_confirm_load()
    _unchanged(entry)
    result = await flow.async_step_confirm_load({})

    assert again["step_id"] == "confirm_load"
    assert result == _abort(reason="changes_saved")
    assert entry.options == {"scan_interval": 10, "prefix": "", "allow_control": False}
    assert entry.update_count == 1


def _replacement_flow(monkeypatch):
    entry = _entry_with_group(keys=SIX_KEYS)
    flow = _options_flow(monkeypatch, entry=entry)
    registry = FakeEntityRegistry([], flow.hass.config_entries.events)
    monkeypatch.setattr(config_flow.er, "async_get", lambda _hass: registry)
    monkeypatch.setattr(
        config_flow.er, "async_entries_for_config_entry", lambda *_args: []
    )
    monkeypatch.setattr(
        config_flow,
        "identify",
        _identifying(_assumed_device(serial=REPLACEMENT_SERIAL)),
    )
    return entry, flow


async def test_the_load_is_confirmed_after_the_model_the_replacement_and_the_prefix(
    monkeypatch,
):
    entry, flow = _replacement_flow(monkeypatch)

    steps = [
        await flow.async_step_init(
            _submission(model="beta", scan_interval=10, prefix="house")
        )
    ]
    steps.append(await flow.async_step_confirm_model({}))
    steps.append(await flow.async_step_confirm_replacement({}))
    steps.append(await flow.async_step_confirm_prefix({}))

    assert [form["step_id"] for form in steps] == [
        "confirm_model",
        "confirm_replacement",
        "confirm_prefix",
        "confirm_load",
    ]
    assert entry.update_count == 0
    result = await flow.async_step_confirm_load({})
    assert result == _abort(reason="changes_saved")
    assert entry.options == {
        "scan_interval": 10,
        "prefix": "house",
        "allow_control": False,
    }


async def test_the_load_after_a_replacement_is_computed_for_the_new_device(
    monkeypatch,
):
    entry = _entry_with_group(keys=SIX_KEYS)
    flow = _options_flow(monkeypatch, entry=entry)
    monkeypatch.setattr(
        config_flow,
        "identify",
        _identifying(
            _device(serial=REPLACEMENT_SERIAL, profile=BETA, device_type=0x0002)
        ),
    )

    await flow.async_step_init(_submission(scan_interval=10))
    await flow.async_step_confirm_replacement({})

    after = _one_request_per_key.asked[0]
    assert (after["profile"], after["device_type"]) == (BETA, 0x0002)
    stored = _one_request_per_key.asked[1]
    assert (stored["profile"], stored["device_type"]) == (ALPHA, 0x0001)


async def test_setup_checks_the_entity_ids_of_every_domain_the_device_has(monkeypatch):
    mixed = profile(
        base=HS3,
        key="mixed",
        device_types={5},
        keys={"pv_power", "backup_reserve_soc"},
        hand_verified=True,
    )
    monkeypatch.setattr(config_flow, "PROFILES", (mixed,))
    monkeypatch.setattr(
        config_flow, "identify", _identifying(_device(profile=mixed, device_type=5))
    )
    monkeypatch.setattr(
        config_flow, "entity_id_in_use", _taking("number.saj_house_backup_reserve_soc")
    )
    instance = _flow(monkeypatch)

    result = await instance.async_step_user({**INPUT, "prefix": "house"})

    assert result["errors"] == {"prefix": "entity_id_taken"}
    assert result["description_placeholders"] == {
        "entity_id": "number.saj_house_backup_reserve_soc"
    }


EMS_TYPE = 0x0004
EMS_PROFILE = profile(
    base=HS3,
    key="delta",
    device_types={EMS_TYPE},
    keys={"pv_power", "ems_battery_control", "ems_battery_power_target"},
    hand_verified=True,
)


def _ems_flow(monkeypatch, **saved_options):
    monkeypatch.setattr(config_flow, "PROFILES", (ALPHA, EMS_PROFILE))
    entry = _saved_entry()
    entry.data = {**SAVED_DATA, "device_type": EMS_TYPE}
    entry.options = {"scan_interval": 45, "prefix": "", **saved_options}
    monkeypatch.setattr(
        config_flow,
        "identify",
        _identifying(_device(profile=EMS_PROFILE, device_type=EMS_TYPE)),
    )
    return entry, _options_flow(monkeypatch, entry=entry)


async def test_the_heartbeat_field_is_offered_only_for_a_model_with_ems_rows(
    monkeypatch,
):
    plain = await _options_flow(monkeypatch, entry=_saved_entry()).async_step_init()
    _, flow = _ems_flow(monkeypatch)

    with_ems = await flow.async_step_init()

    assert "ems_heartbeat" not in _field_names(plain["data_schema"])
    assert _field_names(with_ems["data_schema"])[-2:] == [
        "allow_control",
        "ems_heartbeat",
    ]
    heartbeat = _marker(with_ems["data_schema"], "ems_heartbeat")
    assert heartbeat.default() == 60
    config = with_ems["data_schema"].schema[heartbeat].config
    assert "min" not in config
    assert "max" not in config


@pytest.mark.parametrize("value", [2, 3601, 60.5])
async def test_heartbeat_schema_lets_an_out_of_range_value_reach_the_step_handler(
    monkeypatch, value
):
    _use_home_assistant_number_selector(monkeypatch)
    _, flow = _ems_flow(monkeypatch)
    schema = (await flow.async_step_init())["data_schema"]

    assert schema({**_submission(), "ems_heartbeat": value})["ems_heartbeat"] == value


async def test_the_heartbeat_field_decision_does_not_need_the_installation_loaded(
    monkeypatch,
):
    entry, flow = _ems_flow(monkeypatch, ems_heartbeat=120)
    assert getattr(entry, "runtime_data", None) is None

    form = await flow.async_step_init()

    assert _marker(form["data_schema"], "ems_heartbeat").default() == 120


async def test_the_heartbeat_field_survives_a_redisplayed_submission(monkeypatch):
    _, flow = _ems_flow(monkeypatch)

    form = await flow.async_step_init(
        {**_submission(), "ems_heartbeat": 29, "allow_control": True}
    )

    assert "ems_heartbeat" in _field_names(form["data_schema"])
    assert _marker(form["data_schema"], "ems_heartbeat").default() == 29
    assert _marker(form["data_schema"], "allow_control").default() is True


@pytest.mark.parametrize("value", [2, 29, 3601, -60, 60.5, "soon", None, 0])
async def test_a_heartbeat_outside_30_to_3600_whole_seconds_is_refused_on_its_field(
    monkeypatch, value
):
    entry, flow = _ems_flow(monkeypatch)

    result = await flow.async_step_init({**_submission(), "ems_heartbeat": value})

    assert result["errors"] == {"ems_heartbeat": "invalid_ems_heartbeat"}
    assert _marker(result["data_schema"], "ems_heartbeat").default() == value
    assert entry.update_count == 0
    assert FlowClient.instances == []


@pytest.mark.parametrize("value", [30, 60, 3600])
async def test_a_valid_heartbeat_is_saved_with_the_options(monkeypatch, value):
    entry, flow = _ems_flow(monkeypatch)

    result = await flow.async_step_init({**_submission(), "ems_heartbeat": value})

    assert result == _abort(reason="changes_saved")
    assert entry.options["ems_heartbeat"] == value


async def test_a_model_without_ems_saves_no_heartbeat(monkeypatch):
    entry = _saved_entry()
    flow = _options_flow(monkeypatch, entry=entry)

    await flow.async_step_init(_submission())

    assert "ems_heartbeat" not in entry.options


async def test_switching_control_on_asks_for_confirmation_and_saves_nothing_first(
    monkeypatch,
):
    entry = _saved_entry()
    flow = _options_flow(monkeypatch, entry=entry)

    form = await flow.async_step_init({**_submission(), "allow_control": True})

    assert form["step_id"] == "confirm_control"
    assert entry.update_count == 0
    _unchanged(entry)


async def test_the_control_confirmation_repeats_until_confirmed_then_saves_it_on(
    monkeypatch,
):
    entry = _saved_entry()
    flow = _options_flow(monkeypatch, entry=entry)
    await flow.async_step_init({**_submission(), "allow_control": True})

    again = await flow.async_step_confirm_control()
    saved = await flow.async_step_confirm_control({})

    assert again["step_id"] == "confirm_control"
    assert saved == _abort(reason="changes_saved")
    assert entry.update_count == 1
    assert entry.options["allow_control"] is True


@pytest.mark.parametrize(
    ("saved", "submitted"), [(True, True), (True, False), (False, False)]
)
async def test_control_needs_no_confirmation_unless_it_is_being_switched_on(
    monkeypatch, *, saved, submitted
):
    entry = _saved_entry()
    entry.options = {"scan_interval": 45, "prefix": "", "allow_control": saved}
    flow = _options_flow(monkeypatch, entry=entry)

    result = await flow.async_step_init({**_submission(), "allow_control": submitted})

    assert result == _abort(reason="changes_saved")
    assert entry.options["allow_control"] is submitted


async def test_control_is_confirmed_after_model_replacement_prefix_and_load(
    monkeypatch,
):
    entry, flow = _replacement_flow(monkeypatch)

    steps = [
        await flow.async_step_init(
            {
                **_submission(model="beta", scan_interval=10, prefix="house"),
                "allow_control": True,
            }
        )
    ]
    for step in (
        flow.async_step_confirm_model,
        flow.async_step_confirm_replacement,
        flow.async_step_confirm_prefix,
        flow.async_step_confirm_load,
    ):
        steps.extend([await step({})])

    assert [form["step_id"] for form in steps] == [
        "confirm_model",
        "confirm_replacement",
        "confirm_prefix",
        "confirm_load",
        "confirm_control",
    ]
    assert entry.update_count == 0
    assert await flow.async_step_confirm_control({}) == _abort(reason="changes_saved")
    assert entry.options["allow_control"] is True


async def test_the_load_of_an_installation_counts_only_rows_that_are_read(monkeypatch):
    monkeypatch.setattr(config_flow, "PROFILES", (ALPHA, EMS_PROFILE))
    entry = _saved_entry()
    entry.data = {**SAVED_DATA, "device_type": EMS_TYPE}
    flow = _options_flow(monkeypatch, entry=entry)

    await flow.async_step_init()

    offered = {register.key for register in _nothing_enabled.asked[0]["registers"]}
    assert offered == {"pv_power", "ems_battery_control"}


async def test_polling_group_options_leave_out_rows_that_are_not_read(monkeypatch):
    monkeypatch.setattr(config_flow, "PROFILES", (EMS_PROFILE,))
    flow, entry = _group_flow(
        monkeypatch,
        registered=[
            _registered("pv_power"),
            _registered("ems_battery_control", domain="switch"),
            _registered("ems_battery_power_target", domain="number"),
        ],
    )
    entry.data = {"model": "automatic", "device_type": EMS_TYPE}
    monkeypatch.setattr(config_flow, "blocks_by_key", blocks_by_key)

    form = await flow.async_step_user()

    assert set(_offered(form)) == {"pv_power", "ems_battery_control"}


def _setup_with_ems(monkeypatch):
    monkeypatch.setattr(config_flow, "PROFILES", (ALPHA, EMS_PROFILE))
    monkeypatch.setattr(
        config_flow,
        "identify",
        _identifying(_device(profile=EMS_PROFILE, device_type=EMS_TYPE)),
    )
    return _flow(monkeypatch)


async def test_setup_with_control_left_off_creates_the_entry_without_confirmation(
    monkeypatch,
):
    instance = _flow(monkeypatch)
    monkeypatch.setattr(config_flow, "identify", _identifying(_device()))

    result = await instance.async_step_user({**INPUT, "allow_control": False})

    assert result["type"] == "create_entry"
    assert result["options"]["allow_control"] is False


async def test_setup_with_control_on_confirms_before_creating_anything(monkeypatch):
    instance = _flow(monkeypatch)
    monkeypatch.setattr(config_flow, "identify", _identifying(_device()))

    form = await instance.async_step_user({**INPUT, "allow_control": True})
    again = await instance.async_step_confirm_control()
    assert not hasattr(instance, "selected_unique_id")
    created = await instance.async_step_confirm_control({})

    assert form["step_id"] == "confirm_control"
    assert again["step_id"] == "confirm_control"
    assert created["type"] == "create_entry"
    assert created["options"]["allow_control"] is True


async def test_setup_confirms_control_only_after_the_model_confirmation(monkeypatch):
    instance = _flow(monkeypatch)
    monkeypatch.setattr(config_flow, "identify", _identifying(_assumed_device()))

    model = await instance.async_step_user(
        {**INPUT, "model": "beta", "allow_control": True}
    )
    control = await instance.async_step_confirm_model({})
    created = await instance.async_step_confirm_control({})

    assert model["step_id"] == "confirm_model"
    assert control["step_id"] == "confirm_control"
    assert created["type"] == "create_entry"
    assert created["options"]["allow_control"] is True


async def test_setup_control_confirmation_without_pending_change_aborts(monkeypatch):
    instance = _flow(monkeypatch)

    result = await instance.async_step_confirm_control({})

    assert result == _abort(reason="confirmation_not_pending")


async def test_setup_control_confirmation_asks_an_ems_device_for_the_heartbeat(
    monkeypatch,
):
    instance = _setup_with_ems(monkeypatch)

    form = await instance.async_step_user({**INPUT, "allow_control": True})

    assert form["step_id"] == "confirm_control"
    assert _field_names(form["data_schema"]) == ["ems_heartbeat"]
    assert _marker(form["data_schema"], "ems_heartbeat").default() == 60


async def test_setup_stores_the_confirmed_heartbeat(monkeypatch):
    instance = _setup_with_ems(monkeypatch)
    await instance.async_step_user({**INPUT, "allow_control": True})

    created = await instance.async_step_confirm_control({"ems_heartbeat": 120})

    assert created["type"] == "create_entry"
    assert created["options"]["allow_control"] is True
    assert created["options"]["ems_heartbeat"] == 120


@pytest.mark.parametrize("value", [2, 29, 3601, -60, 60.5, "x"])
async def test_setup_refuses_an_invalid_heartbeat_and_creates_nothing(
    monkeypatch, value
):
    instance = _setup_with_ems(monkeypatch)
    await instance.async_step_user({**INPUT, "allow_control": True})

    form = await instance.async_step_confirm_control({"ems_heartbeat": value})

    assert form["step_id"] == "confirm_control"
    assert form["errors"] == {"ems_heartbeat": "invalid_ems_heartbeat"}
    assert _marker(form["data_schema"], "ems_heartbeat").default() == value
    assert not hasattr(instance, "selected_unique_id")


async def test_setup_control_confirmation_has_no_heartbeat_without_ems_rows(
    monkeypatch,
):
    instance = _flow(monkeypatch)
    monkeypatch.setattr(config_flow, "identify", _identifying(_device()))

    form = await instance.async_step_user({**INPUT, "allow_control": True})
    created = await instance.async_step_confirm_control({})

    assert _field_names(form["data_schema"]) == []
    assert "ems_heartbeat" not in created["options"]


async def test_failed_setup_validation_keeps_the_control_tick(monkeypatch):
    instance = _flow(monkeypatch)
    monkeypatch.setattr(
        config_flow,
        "identify",
        _failing_identify(saj_errors.UnsupportedDeviceError(UNRECOGNISED_TYPE)),
    )

    result = await instance.async_step_user({**INPUT, "allow_control": True})

    assert result["step_id"] == "user"
    assert _marker(result["data_schema"], "allow_control").default() is True
