from functools import partial
from types import SimpleNamespace

import pytest
import voluptuous as vol

from custom_components.saj_local import config_flow
from custom_components.saj_local.const import PowerSchedule, power_schedules
from custom_components.saj_local.saj.models import PowerFunction

ENTRY_ID = "entry-a"
BATTERY = PowerFunction.BATTERY
GRID = PowerFunction.GRID
FUNCTION_LABELS = {"battery": "Battery", "grid": "Grid", "inverter": "Inverter"}
STORED_FIT = object()
REGISTERED = ("schedule.night", "schedule.day")


class Registry:
    def __init__(self, *entity_ids: str) -> None:
        self.entries = {_registry_id(entity_id): entity_id for entity_id in entity_ids}

    def async_get(self, key: str):
        for registry_id, entity_id in self.entries.items():
            if key in (registry_id, entity_id):
                return SimpleNamespace(id=registry_id, entity_id=entity_id)
        return None


def _registry_id(entity_id: str) -> str:
    return f"id-{entity_id}"


def _form(**kwargs):
    return {"type": "form", **kwargs}


def _abort(*, reason):
    return {"type": "abort", "reason": reason}


class KnownEntries:
    def __init__(self, *, entry, updates) -> None:
        self.entry = entry
        self.updates = updates

    def async_get_known_entry(self, _entry_id):
        return self.entry

    def async_update_subentry(self, **changes) -> None:
        self.updates.append(changes)


def _created(created, *, title, data):
    created.append((title, data))
    return {"type": "create_entry", "title": title, "data": data}


def _schedule(subentry_id, function, entity_id):
    return SimpleNamespace(
        subentry_id=subentry_id,
        subentry_type="power_schedule",
        title=function.capitalize(),
        data={"function": function, "schedule": _registry_id(entity_id)},
    )


def _polling_group():
    return SimpleNamespace(
        subentry_id="g1",
        subentry_type="polling_group",
        title="Group",
        data={"scan_interval": 10, "keys": []},
    )


def _flow(
    monkeypatch, *, subentries=(), allow=True, editing=None, functions=(BATTERY, GRID)
):
    entry = SimpleNamespace(
        entry_id=ENTRY_ID,
        options={"allow_control": allow},
        subentries={subentry.subentry_id: subentry for subentry in subentries},
    )
    flow = object.__new__(config_flow.SajPowerScheduleFlow)
    flow.updates = []
    flow.created = []
    flow.hass = SimpleNamespace(
        config_entries=KnownEntries(entry=entry, updates=flow.updates),
        config=SimpleNamespace(language="en"),
        registry=Registry(*REGISTERED),
    )
    flow.handler = (ENTRY_ID, "power_schedule")
    flow.context = {"source": "user"}
    if editing is not None:
        flow.context = {"source": "reconfigure", "subentry_id": editing}

    async def labels(*, hass, selector_name):
        del hass
        assert selector_name == "power_function"
        return FUNCTION_LABELS

    monkeypatch.setattr(config_flow, "selector_options", labels)
    monkeypatch.setattr(
        config_flow, "er", SimpleNamespace(async_get=lambda hass: hass.registry)
    )
    monkeypatch.setattr(config_flow, "_stored_fit", lambda **_: STORED_FIT)
    monkeypatch.setattr(
        config_flow,
        "power_functions",
        lambda *, fit: functions if fit is STORED_FIT else (),
    )
    for name, replacement in (
        ("async_show_form", _form),
        ("async_abort", _abort),
        ("async_create_entry", partial(_created, flow.created)),
    ):
        monkeypatch.setattr(flow, name, replacement)
    return flow, entry


def _input(**changes):
    return {"function": "battery", "schedule": "schedule.night", **changes}


def _marker(schema, name):
    return next(marker for marker in schema.schema if marker == name)


@pytest.mark.parametrize(
    ("functions", "offered"),
    [((BATTERY,), True), ((BATTERY, GRID), True), ((), False)],
)
def test_the_schedule_type_is_offered_only_to_a_system_with_a_function(
    monkeypatch, functions, offered
):
    monkeypatch.setattr(config_flow, "_stored_fit", lambda **_: STORED_FIT)
    monkeypatch.setattr(config_flow, "power_functions", lambda **_: functions)

    types = config_flow.SajLocalConfigFlow.async_get_supported_subentry_types(None)

    assert ("power_schedule" in types) is offered
    assert types["polling_group"] is config_flow.SajPollingGroupFlow
    if offered:
        assert types["power_schedule"] is config_flow.SajPowerScheduleFlow


async def test_the_form_asks_for_a_function_and_a_schedule_and_nothing_about_time(
    monkeypatch,
):
    flow, _ = _flow(monkeypatch)

    form = await flow.async_step_user()

    assert form["step_id"] == "user"
    assert form["errors"] == {}
    schema = form["data_schema"]
    assert list(schema.schema) == ["function", "schedule"]
    function = schema.schema[_marker(schema, "function")]
    assert function.config["options"] == ["battery", "grid"]
    assert function.config["translation_key"] == "power_function"
    assert schema.schema[_marker(schema, "schedule")].config["domain"] == ["schedule"]


async def test_the_function_options_are_those_the_library_gives_for_the_system(
    monkeypatch,
):
    flow, _ = _flow(monkeypatch, functions=(PowerFunction.INVERTER,))

    form = await flow.async_step_user()

    schema = form["data_schema"]
    assert schema.schema[_marker(schema, "function")].config["options"] == ["inverter"]


async def test_a_valid_schedule_is_created_titled_by_its_function(monkeypatch):
    flow, _ = _flow(monkeypatch)

    result = await flow.async_step_user(_input(function="grid"))

    assert result == {
        "type": "create_entry",
        "title": "Grid",
        "data": {"function": "grid", "schedule": _registry_id("schedule.night")},
    }


async def test_another_function_may_use_a_free_schedule_beside_existing_ones(
    monkeypatch,
):
    flow, _ = _flow(
        monkeypatch,
        subentries=[_schedule("s1", "battery", "schedule.night"), _polling_group()],
    )

    result = await flow.async_step_user(
        _input(function="grid", schedule="schedule.day")
    )

    assert result["type"] == "create_entry"


@pytest.mark.parametrize(
    ("submitted", "errors"),
    [
        (
            _input(),
            {"function": "function_already_scheduled", "schedule": "schedule_in_use"},
        ),
        (_input(schedule="schedule.day"), {"function": "function_already_scheduled"}),
        (_input(function="grid"), {"schedule": "schedule_in_use"}),
    ],
    ids=["both", "function", "schedule"],
)
async def test_a_function_or_schedule_already_used_is_refused_with_its_own_message(
    monkeypatch, submitted, errors
):
    flow, _ = _flow(
        monkeypatch, subentries=[_schedule("s1", "battery", "schedule.night")]
    )

    form = await flow.async_step_user(submitted)

    assert form["type"] == "form"
    assert form["errors"] == errors
    assert flow.created == []
    schema = form["data_schema"]
    assert schema.schema[_marker(schema, "function")].config["options"] == [
        "battery",
        "grid",
    ]


async def test_a_schedule_is_refused_while_allow_control_is_off(monkeypatch):
    flow, _ = _flow(monkeypatch, allow=False)

    form = await flow.async_step_user(_input())

    assert form["errors"] == {"base": "control_not_allowed"}
    assert flow.created == []


async def test_a_refused_form_is_shown_again_with_what_was_submitted(monkeypatch):
    flow, _ = _flow(monkeypatch, allow=False)

    form = await flow.async_step_user(_input(function="grid", schedule="schedule.day"))

    schema = form["data_schema"]
    assert _marker(schema, "function").default() == "grid"
    assert _marker(schema, "schedule").default() == "schedule.day"


async def test_reconfiguring_shows_the_saved_choice(monkeypatch):
    saved = _schedule("s1", "battery", "schedule.night")
    flow, _ = _flow(monkeypatch, subentries=[saved], editing="s1")

    form = await flow.async_step_reconfigure()

    assert form["step_id"] == "reconfigure"
    schema = form["data_schema"]
    assert _marker(schema, "function").default() == "battery"
    assert _marker(schema, "schedule").default() == "schedule.night"


async def test_reconfiguring_updates_the_schedule_and_may_keep_its_own_choices(
    monkeypatch,
):
    saved = _schedule("s1", "battery", "schedule.night")
    flow, entry = _flow(
        monkeypatch,
        subentries=[saved, _schedule("s2", "grid", "schedule.day")],
        editing="s1",
    )

    result = await flow.async_step_reconfigure(_input(function="battery"))

    assert result == _abort(reason="reconfigure_successful")
    (update,) = flow.updates
    assert update["entry"] is entry
    assert update["subentry"] is saved
    assert update["title"] == "Battery"
    assert update["data"] == {
        "function": "battery",
        "schedule": _registry_id("schedule.night"),
    }


async def test_reconfiguring_cannot_take_the_function_or_schedule_of_another(
    monkeypatch,
):
    flow, _ = _flow(
        monkeypatch,
        subentries=[
            _schedule("s1", "battery", "schedule.night"),
            _schedule("s2", "grid", "schedule.day"),
        ],
        editing="s1",
    )

    form = await flow.async_step_reconfigure(
        _input(function="grid", schedule="schedule.day")
    )

    assert form["errors"] == {
        "function": "function_already_scheduled",
        "schedule": "schedule_in_use",
    }
    assert flow.updates == []


def test_the_schedules_of_a_system_are_read_from_its_schedule_subentries():
    entry = SimpleNamespace(
        subentries={
            "s1": _schedule("s1", "battery", "schedule.night"),
            "s2": _schedule("s2", "grid", "schedule.day"),
            "g1": _polling_group(),
        }
    )

    assert power_schedules(entry=entry) == (
        PowerSchedule(function=BATTERY, registry_id=_registry_id("schedule.night")),
        PowerSchedule(function=GRID, registry_id=_registry_id("schedule.day")),
    )
    assert power_schedules(entry=entry, excluding="s1") == (
        PowerSchedule(function=GRID, registry_id=_registry_id("schedule.day")),
    )


async def test_a_schedule_helper_without_a_registry_entry_is_refused(monkeypatch):
    flow, _ = _flow(monkeypatch)

    form = await flow.async_step_user(_input(schedule="schedule.yaml_only"))

    assert form["errors"] == {"schedule": "schedule_not_registered"}
    assert flow.created == []


async def test_reconfiguring_shows_no_schedule_when_the_saved_helper_is_gone(
    monkeypatch,
):
    saved = _schedule("s1", "battery", "schedule.removed")
    flow, _ = _flow(monkeypatch, subentries=[saved], editing="s1")

    form = await flow.async_step_reconfigure()

    schema = form["data_schema"]
    assert _marker(schema, "function").default() == "battery"
    assert _marker(schema, "schedule").default is vol.UNDEFINED
