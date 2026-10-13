from __future__ import annotations

import logging
from types import SimpleNamespace
from typing import ClassVar

import pytest
from homeassistant.helpers import entity_registry as real_entity_registry

from custom_components.saj_local import repairs as repairs_module
from custom_components.saj_local.config_flow import (
    ABORT_ALREADY_CONFIGURED,
    ABORT_CHANGES_SAVED,
    ABORT_PREFIX_UNAVAILABLE,
    Validation,
)
from custom_components.saj_local.repairs import (
    ModelFixFlow,
    RefusedFixFlow,
    adoption_input,
    async_create_fix_flow,
)

ENTRY = SimpleNamespace(
    entry_id="entry-1",
    title="Roof inverter",
    data={"host": "inverter", "port": 1502, "unit_id": 3, "model": "h2"},
    options={
        "scan_interval": 30,
        "prefix": "roof",
        "allow_control": True,
        "ems_heartbeat": 45,
        "equipment": {"battery": "fitted"},
    },
    unique_id="SERIAL-1",
    update_listeners=[],
)
LOADED_ENTRY = SimpleNamespace(**{**vars(ENTRY), "update_listeners": [object()]})
CHANGE = SimpleNamespace(
    device=SimpleNamespace(
        serial="SERIAL-2", profile=SimpleNamespace(display_name="HS3")
    )
)


class FakeChanges:
    instances: ClassVar[list[FakeChanges]] = []
    validations: ClassVar[list[Validation]] = []
    serial_taken = False
    save_reason = ABORT_CHANGES_SAVED

    def __init__(self, *, hass, entry) -> None:
        self.hass = hass
        self.entry = entry
        self.validated: list[dict] = []
        self.saved: list[object] = []
        self.instances.append(self)

    async def validate(self, *, user_input):
        self.validated.append(user_input)
        return self.validations.pop(0)

    def serial_exists_for_other(self, *, serial):
        return self.serial_taken and serial == "SERIAL-2"

    async def save(self, *, change):
        self.saved.append(change)
        return self.save_reason


class FakeConfigEntries:
    def __init__(self, *, entry=ENTRY) -> None:
        self.entry = entry
        self.reloads: list[str] = []

    def async_get_entry(self, entry_id):
        return self.entry if entry_id == "entry-1" else None

    def async_schedule_reload(self, entry_id) -> None:
        self.reloads.append(entry_id)


@pytest.fixture(autouse=True)
def fake_changes(monkeypatch):
    FakeChanges.instances = []
    FakeChanges.validations = []
    FakeChanges.serial_taken = False
    FakeChanges.save_reason = ABORT_CHANGES_SAVED
    monkeypatch.setattr(repairs_module, "EntryChanges", FakeChanges)


def _form(**details):
    return {"type": "form", **details}


def _flow(flow, *, entry=ENTRY):
    flow.hass = SimpleNamespace(config_entries=FakeConfigEntries(entry=entry))
    flow.issue_id = "entry-1_registers_refused"
    flow.async_show_form = _form
    flow.async_abort = lambda *, reason: {"type": "abort", "reason": reason}
    flow.async_create_entry = lambda *, data: {"type": "create_entry", "data": data}
    return flow


def _model_flow(named="HS3", **kwargs):
    return _flow(
        ModelFixFlow(entry_id="entry-1", key="identity_mismatch", named=named),
        **kwargs,
    )


def _logged(caplog) -> list[str]:
    return [r.getMessage() for r in caplog.records if r.levelno == logging.INFO]


def _detected() -> Validation:
    return Validation(change=CHANGE)


def test_the_adopting_validation_reuses_the_saved_settings_with_automatic_model():
    assert adoption_input(entry=ENTRY) == {
        "host": "inverter",
        "port": 1502,
        "unit_id": 3,
        "scan_interval": 30,
        "model": "automatic",
        "prefix": "roof",
        "allow_control": True,
        "equipment": {"battery": "fitted"},
        "ems_heartbeat": 45,
    }


def test_the_adopting_validation_falls_back_to_the_defaults_of_a_bare_entry():
    entry = SimpleNamespace(data={"host": "inverter"}, options={})

    assert adoption_input(entry=entry) == {
        "host": "inverter",
        "port": 502,
        "unit_id": 1,
        "scan_interval": 60,
        "model": "automatic",
        "prefix": "",
        "allow_control": False,
        "equipment": {},
    }


async def test_the_model_fix_starts_at_its_one_confirm_step():
    FakeChanges.validations = [_detected()]

    form = await _model_flow().async_step_init()

    assert form["step_id"] == "confirm"
    assert form["errors"] == {}
    assert form["description_placeholders"] == {
        "installation": "Roof inverter",
        "model": "HS3",
        "serial": "SERIAL-2",
    }
    assert FakeChanges.instances[0].validated == [adoption_input(entry=ENTRY)]


async def test_showing_the_fix_saves_nothing():
    FakeChanges.validations = [_detected()]
    flow = _model_flow()

    await flow.async_step_confirm()

    assert FakeChanges.instances[0].saved == []
    assert flow.hass.config_entries.reloads == []


@pytest.mark.parametrize(
    ("named", "errors"),
    [
        ("HS3", {}),
        ("SERIAL-2", {}),
        ("H2", {"base": "device_changed"}),
        ("SERIAL-9", {"base": "device_changed"}),
    ],
)
async def test_the_form_says_so_when_the_device_is_not_what_the_issue_named(
    named, errors
):
    FakeChanges.validations = [_detected()]

    form = await _model_flow(named=named).async_step_confirm()

    assert form["errors"] == errors


@pytest.mark.parametrize(
    ("entry", "reloads"),
    [(ENTRY, ["entry-1"]), (LOADED_ENTRY, [])],
    ids=["not loaded, scheduled reload", "loaded, its update listener reloads"],
)
async def test_confirming_what_was_shown_saves_it_and_reloads_the_entry_once(
    entry, reloads, caplog
):
    FakeChanges.validations = [_detected(), _detected()]
    flow = _model_flow(entry=entry)
    await flow.async_step_confirm()

    with caplog.at_level(logging.INFO):
        result = await flow.async_step_confirm({})

    assert result == {"type": "create_entry", "data": {}}
    assert FakeChanges.instances[1].saved == [CHANGE]
    assert flow.hass.config_entries.reloads == reloads
    assert _logged(caplog) == ["Roof inverter: repair issue identity_mismatch cleared"]


async def test_values_the_user_did_not_see_are_shown_instead_of_saved(caplog):
    other = SimpleNamespace(
        device=SimpleNamespace(
            serial="SERIAL-3", profile=SimpleNamespace(display_name="H2")
        )
    )
    FakeChanges.validations = [_detected(), Validation(change=other)]
    flow = _model_flow()
    await flow.async_step_confirm()

    with caplog.at_level(logging.INFO):
        form = await flow.async_step_confirm({})

    assert _logged(caplog) == []
    assert form["errors"] == {"base": "device_changed"}
    assert form["description_placeholders"]["model"] == "H2"
    assert form["description_placeholders"]["serial"] == "SERIAL-3"
    assert FakeChanges.instances[1].saved == []
    assert flow.hass.config_entries.reloads == []


async def test_submitting_before_anything_was_shown_shows_it_first():
    FakeChanges.validations = [_detected()]
    flow = _model_flow()

    form = await flow.async_step_confirm({})

    assert form["errors"] == {"base": "device_changed"}
    assert FakeChanges.instances[0].saved == []


async def test_a_failing_validation_is_shown_on_the_form_and_saves_nothing(caplog):
    FakeChanges.validations = [
        Validation(
            errors={"model": "unsupported_device"}, placeholders={"device_type": "0x1"}
        )
    ]
    flow = _model_flow()

    with caplog.at_level(logging.INFO):
        form = await flow.async_step_confirm({})

    assert _logged(caplog) == []
    assert form["errors"] == {"base": "unsupported_device"}
    assert form["description_placeholders"] == {
        "installation": "Roof inverter",
        "model": "?",
        "serial": "?",
        "device_type": "0x1",
    }
    assert FakeChanges.instances[0].saved == []
    assert flow.hass.config_entries.reloads == []


async def test_a_serial_that_belongs_to_another_installation_is_not_adopted():
    FakeChanges.validations = [_detected()]
    FakeChanges.serial_taken = True

    form = await _model_flow().async_step_confirm({})

    assert form["errors"] == {"base": ABORT_ALREADY_CONFIGURED}
    assert FakeChanges.instances[0].saved == []


@pytest.mark.parametrize("reason", [ABORT_ALREADY_CONFIGURED, ABORT_PREFIX_UNAVAILABLE])
async def test_a_save_the_shared_path_refuses_aborts_the_fix_and_reloads_nothing(
    reason, caplog
):
    FakeChanges.validations = [_detected(), _detected()]
    FakeChanges.save_reason = reason
    flow = _model_flow()
    await flow.async_step_confirm()

    with caplog.at_level(logging.INFO):
        result = await flow.async_step_confirm({})

    assert _logged(caplog) == []
    assert result == {"type": "abort", "reason": reason}
    assert flow.hass.config_entries.reloads == []


async def test_a_fix_for_an_installation_that_is_gone_aborts():
    flow = _model_flow(entry=None)

    assert await flow.async_step_confirm() == {
        "type": "abort",
        "reason": "entry_removed",
    }


class FakeEntityRegistry:
    def __init__(self) -> None:
        self.disabled: list[tuple[str, object]] = []

    def async_update_entity(self, entity_id, *, disabled_by) -> None:
        self.disabled.append((entity_id, disabled_by))


@pytest.fixture
def refused(monkeypatch):
    registry = FakeEntityRegistry()
    monkeypatch.setattr(
        repairs_module,
        "er",
        SimpleNamespace(
            async_get=lambda _hass: registry,
            RegistryEntryDisabler=real_entity_registry.RegistryEntryDisabler,
        ),
    )
    monkeypatch.setattr(
        repairs_module,
        "installation_entities",
        lambda **_: {
            "pv_power": SimpleNamespace(entity_id="sensor.saj_pv_power"),
            "grid_power": SimpleNamespace(entity_id="sensor.saj_grid_power"),
        },
    )
    issue = SimpleNamespace(translation_placeholders={"entities": "Solar power"})
    monkeypatch.setattr(
        repairs_module,
        "ir",
        SimpleNamespace(
            async_get=lambda _hass: SimpleNamespace(async_get_issue=lambda *_: issue)
        ),
    )
    return registry


def _refused_flow(keys=("pv_power", "ems_timeout")):
    return _flow(RefusedFixFlow(entry_id="entry-1", keys=frozenset(keys)))


async def test_the_refusal_fix_lists_the_entities_it_will_disable(refused):
    form = await _refused_flow().async_step_init()

    assert form["step_id"] == "confirm"
    assert form["description_placeholders"] == {"entities": "Solar power"}
    assert refused.disabled == []


async def test_the_refusal_fix_without_its_issue_shows_no_placeholders(
    refused, monkeypatch
):
    monkeypatch.setattr(
        repairs_module,
        "ir",
        SimpleNamespace(
            async_get=lambda _hass: SimpleNamespace(async_get_issue=lambda *_: None)
        ),
    )

    form = await _refused_flow().async_step_confirm()

    assert form["description_placeholders"] == {}


async def test_confirming_disables_the_listed_entities_as_the_user(refused, caplog):
    with caplog.at_level(logging.INFO):
        result = await _refused_flow(
            ("pv_power", "grid_power", "ems_timeout")
        ).async_step_confirm({})

    assert result == {"type": "create_entry", "data": {}}
    assert refused.disabled == [
        ("sensor.saj_grid_power", real_entity_registry.RegistryEntryDisabler.USER),
        ("sensor.saj_pv_power", real_entity_registry.RegistryEntryDisabler.USER),
    ]
    assert _logged(caplog) == ["Roof inverter: repair issue registers_refused cleared"]


async def test_the_refusal_fix_for_an_installation_that_is_gone_aborts_unlogged(
    refused, caplog
):
    with caplog.at_level(logging.INFO):
        result = await _flow(
            RefusedFixFlow(entry_id="entry-1", keys=frozenset({"pv_power"})),
            entry=None,
        ).async_step_confirm({})

    assert result == {"type": "abort", "reason": "entry_removed"}
    assert refused.disabled == []
    assert _logged(caplog) == []


async def test_the_fix_flow_for_a_refusal_issue_holds_its_keys():
    flow = await async_create_fix_flow(
        SimpleNamespace(),
        "entry-1_registers_refused",
        {"entry_id": "entry-1", "keys": "pv_power,grid_power"},
    )

    assert isinstance(flow, RefusedFixFlow)
    assert flow._keys == {"pv_power", "grid_power"}
    assert flow._entry_id == "entry-1"


@pytest.mark.parametrize("key", ["model_mismatch", "identity_mismatch"])
async def test_the_fix_flow_for_a_model_issue_holds_what_it_named(key):
    flow = await async_create_fix_flow(
        SimpleNamespace(),
        f"entry-1_{key}",
        {"entry_id": "entry-1", "issue": key, "named": "H2"},
    )

    assert isinstance(flow, ModelFixFlow)
    assert flow._named == "H2"
    assert flow._key == key
    assert flow._entry_id == "entry-1"


async def test_home_assistant_starting_the_model_fix_shows_the_form_unflagged():
    FakeChanges.validations = [_detected()]
    flow = _model_flow(named="HS3")

    form = await flow.async_step_init({"issue_id": "entry-1_model_mismatch"})

    assert form["step_id"] == "confirm"
    assert form["errors"] == {}
    assert FakeChanges.instances[0].saved == []
    assert flow.hass.config_entries.reloads == []


async def test_home_assistant_starting_the_refusal_fix_disables_nothing(refused):
    flow = _refused_flow()

    form = await flow.async_step_init({"issue_id": "entry-1_registers_refused"})

    assert form["step_id"] == "confirm"
    assert refused.disabled == []


async def test_the_refusal_fix_disables_only_once_confirmed_after_the_form(refused):
    flow = _refused_flow()
    await flow.async_step_init({"issue_id": "entry-1_registers_refused"})

    result = await flow.async_step_confirm({})

    assert result["type"] == "create_entry"
    assert [entity_id for entity_id, _ in refused.disabled] == ["sensor.saj_pv_power"]
