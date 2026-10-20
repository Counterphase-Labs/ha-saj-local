from __future__ import annotations

from types import SimpleNamespace

import pytest
from homeassistant.helpers import entity_registry as er

from custom_components.saj_local import controls
from custom_components.saj_local.const import DOMAIN
from custom_components.saj_local.controls import (
    CONTROL_MARK,
    apply_control_set,
    control_member_keys,
    keys_to_enable,
    start_control_listener,
)
from custom_components.saj_local.saj.definitions import EntityKind
from custom_components.saj_local.saj.models import PowerFunction
from tests.entities import register_of

INTEGRATION = er.RegistryEntryDisabler.INTEGRATION
USER = er.RegistryEntryDisabler.USER
ENTRY_ID = "entry-1"
FIT = object()


def _registers():
    return (
        register_of(
            kind=EntityKind.NUMBER, key="member_default_off", core=False, control=True
        ),
        register_of(
            kind=EntityKind.NUMBER, key="member_default_on", core=True, control=True
        ),
        register_of(kind=EntityKind.NUMBER, key="plain_setting", core=False),
        register_of(
            kind=EntityKind.NUMBER,
            key="member_hidden",
            core=False,
            control=True,
            exposed=False,
        ),
    )


def _offered_registers(*, fit):
    del fit
    return _registers()


def _offered_functions(*, fit):
    del fit
    return (PowerFunction.BATTERY,)


@pytest.fixture(autouse=True)
def catalogue(monkeypatch):
    monkeypatch.setattr(controls, "device_registers", _offered_registers)
    monkeypatch.setattr(controls, "power_functions", _offered_functions)


class FakeRegistry:
    def __init__(self, entities) -> None:
        self.entities = {entity.entity_id: entity for entity in entities}
        self.updates: list[tuple[str, object]] = []

    def async_get(self, entity_id):
        return self.entities.get(entity_id)

    def async_update_entity(self, entity_id, *, disabled_by):
        self.entities[entity_id].disabled_by = disabled_by
        self.updates.append((entity_id, disabled_by))

    def async_update_entity_options(self, entity_id, domain, options):
        entity = self.entities[entity_id]
        if options is None:
            entity.options.pop(domain, None)
        else:
            entity.options[domain] = options
        self.updates.append((entity_id, options))


def _entity(key, *, disabled_by=None, marked=False, config_entry_id=ENTRY_ID):
    return SimpleNamespace(
        entity_id=f"number.{key}",
        unique_id=key,
        disabled_by=disabled_by,
        config_entry_id=config_entry_id,
        options={DOMAIN: {CONTROL_MARK: True}} if marked else {},
    )


def _install(monkeypatch, *entities):
    registry = FakeRegistry(entities)

    def registry_of(hass):
        del hass
        return registry

    def installed(*, hass, entry_id):
        del hass, entry_id
        return {entity.unique_id: entity for entity in registry.entities.values()}

    monkeypatch.setattr(controls.er, "async_get", registry_of)
    monkeypatch.setattr(controls, "installation_entities", installed)
    return registry


def _apply(*, allowed):
    apply_control_set(
        hass=SimpleNamespace(),
        entry=SimpleNamespace(entry_id=ENTRY_ID),
        fit=FIT,
        allowed=allowed,
    )


def test_the_members_are_exposed_control_registers_and_power_function_entities():
    assert control_member_keys(fit=FIT) == {
        "member_default_off",
        "member_default_on",
        PowerFunction.BATTERY.switch_key,
        PowerFunction.BATTERY.target_key,
    }


POWER_ENABLED = {
    key: _entity(key)
    for key in (PowerFunction.BATTERY.switch_key, PowerFunction.BATTERY.target_key)
}


@pytest.mark.parametrize(
    ("registered", "expected"),
    [
        ({}, {"member_default_off", "battery_power_control", "battery_power_target"}),
        (
            {
                **POWER_ENABLED,
                "member_default_off": _entity(
                    "member_default_off", disabled_by=INTEGRATION
                ),
            },
            {"member_default_off"},
        ),
        (
            {
                **POWER_ENABLED,
                "member_default_off": _entity("member_default_off", disabled_by=USER),
            },
            set(),
        ),
        ({**POWER_ENABLED, "member_default_off": _entity("member_default_off")}, set()),
    ],
    ids=["new-system", "disabled-by-integration", "disabled-by-user", "enabled"],
)
def test_the_members_to_enable_are_those_the_integration_would_enable(
    registered, expected
):
    assert keys_to_enable(fit=FIT, registered=registered) == expected


def test_switching_on_enables_only_members_the_integration_disabled_and_marks_them(
    monkeypatch,
):
    registry = _install(
        monkeypatch,
        _entity("member_default_off", disabled_by=INTEGRATION),
        _entity("battery_power_control", disabled_by=INTEGRATION),
        _entity("battery_power_target", disabled_by=USER),
        _entity("member_default_on"),
        _entity("plain_setting", disabled_by=INTEGRATION),
    )

    _apply(allowed=True)

    states = {
        key: (entity.disabled_by, CONTROL_MARK in entity.options.get(DOMAIN, {}))
        for key, entity in (
            (entity.unique_id, entity) for entity in registry.entities.values()
        )
    }
    assert states == {
        "member_default_off": (None, True),
        "battery_power_control": (None, True),
        "battery_power_target": (USER, False),
        "member_default_on": (None, False),
        "plain_setting": (INTEGRATION, False),
    }


def test_switching_on_skips_members_that_are_not_registered(monkeypatch):
    registry = _install(monkeypatch, _entity("plain_setting", disabled_by=INTEGRATION))

    _apply(allowed=True)

    assert registry.updates == []


def test_switching_off_disables_marked_members_and_removes_the_marks(monkeypatch):
    registry = _install(
        monkeypatch,
        _entity("member_default_off", marked=True),
        _entity("member_default_on"),
        _entity("plain_setting"),
    )

    _apply(allowed=False)

    states = {
        entity.unique_id: (
            entity.disabled_by,
            CONTROL_MARK in entity.options.get(DOMAIN, {}),
        )
        for entity in registry.entities.values()
    }
    assert states == {
        "member_default_off": (INTEGRATION, False),
        "member_default_on": (None, False),
        "plain_setting": (None, False),
    }


def test_switching_off_only_removes_the_mark_of_a_member_the_user_disabled(
    monkeypatch,
):
    registry = _install(
        monkeypatch, _entity("member_default_off", disabled_by=USER, marked=True)
    )

    _apply(allowed=False)

    assert registry.updates == [("number.member_default_off", None)]
    assert registry.entities["number.member_default_off"].disabled_by is USER


def _event(*, entity_id, action="update", changes=("disabled_by",)):
    return SimpleNamespace(
        data={
            "entity_id": entity_id,
            "action": action,
            "changes": dict.fromkeys(changes),
        }
    )


class FakeBus:
    def __init__(self) -> None:
        self.listened: list[tuple[str, object]] = []

    def async_listen(self, event_type, listener):
        self.listened.append((event_type, listener))
        return lambda: None


def _listener(monkeypatch, *entities):
    registry = _install(monkeypatch, *entities)
    bus = FakeBus()
    cancel = start_control_listener(
        hass=SimpleNamespace(bus=bus), entry=SimpleNamespace(entry_id=ENTRY_ID)
    )
    return registry, bus, cancel


def test_the_listener_watches_entity_registry_updates_and_can_be_removed(monkeypatch):
    _, bus, cancel = _listener(monkeypatch)

    assert [event_type for event_type, _ in bus.listened] == [
        er.EVENT_ENTITY_REGISTRY_UPDATED
    ]
    assert callable(cancel)


def test_a_member_the_user_disables_loses_its_mark(monkeypatch):
    registry, bus, _ = _listener(
        monkeypatch, _entity("member_default_off", disabled_by=USER, marked=True)
    )

    bus.listened[0][1](_event(entity_id="number.member_default_off"))

    assert registry.entities["number.member_default_off"].options == {}


@pytest.mark.parametrize(
    ("entity", "event"),
    [
        (
            _entity("m", disabled_by=INTEGRATION, marked=True),
            _event(entity_id="number.m"),
        ),
        (_entity("m", disabled_by=USER), _event(entity_id="number.m")),
        (
            _entity("m", disabled_by=USER, marked=True, config_entry_id="other"),
            _event(entity_id="number.m"),
        ),
        (
            _entity("m", disabled_by=USER, marked=True),
            _event(entity_id="number.m", action="create"),
        ),
        (
            _entity("m", disabled_by=USER, marked=True),
            _event(entity_id="number.m", changes=("options",)),
        ),
        (_entity("m", disabled_by=USER, marked=True), _event(entity_id="number.gone")),
    ],
    ids=[
        "disabled-by-integration",
        "not-marked",
        "other-installation",
        "not-an-update",
        "other-change",
        "removed-entity",
    ],
)
def test_the_listener_leaves_every_other_update_alone(monkeypatch, entity, event):
    registry, bus, _ = _listener(monkeypatch, entity)

    bus.listened[0][1](event)

    assert registry.updates == []
