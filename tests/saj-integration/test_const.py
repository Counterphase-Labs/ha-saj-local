from types import SimpleNamespace

import pytest

from custom_components.saj_local import const
from custom_components.saj_local.saj.definitions import Combination, Operation


@pytest.mark.parametrize(
    ("prefix", "key", "expected_object_id"),
    [
        ("", "pv_power", "saj_pv_power"),
        ("house", "pv_power", "saj_house_pv_power"),
        ("garage2", "battery_soc", "saj_garage2_battery_soc"),
    ],
)
@pytest.mark.parametrize(
    "domain",
    [
        "sensor",
        "binary_sensor",
        "number",
        "select",
        "switch",
        "time",
        "button",
    ],
)
def test_the_entity_id_is_the_domain_then_the_fixed_root_prefix_and_key(
    domain, prefix, key, expected_object_id
):
    assert const.object_id(prefix=prefix, key=key) == expected_object_id
    assert (
        const.fixed_entity_id(domain=domain, prefix=prefix, key=key)
        == f"{domain}.{expected_object_id}"
    )


def test_every_entity_domain_is_a_platform():
    assert {str(platform) for platform in const.PLATFORMS} == {
        "sensor",
        "binary_sensor",
        "number",
        "select",
        "switch",
        "time",
        "button",
    }


@pytest.mark.parametrize(
    ("unique_id", "key"),
    [("entry-1_pv_power", "pv_power"), ("entry-2_pv_power", None), ("entry-1_", "")],
)
def test_the_key_is_what_follows_the_config_entry_id_in_the_unique_id(unique_id, key):
    assert const.entity_unique_id(entry_id="entry-1", key="pv_power") == (
        "entry-1_pv_power"
    )
    assert const.entity_key(entry_id="entry-1", unique_id=unique_id) == key


class FakeRegistry:
    def __init__(self, registered) -> None:
        self.registered = registered

    def async_is_registered(self, entity_id) -> bool:
        return entity_id in self.registered


@pytest.mark.parametrize(
    ("registered", "states", "in_use"),
    [
        ({"sensor.a"}, {}, True),
        (set(), {"sensor.a": object()}, True),
        ({"sensor.a"}, {"sensor.a": object()}, True),
        ({"sensor.b"}, {"sensor.b": object()}, False),
        (set(), {}, False),
    ],
)
def test_an_entity_id_is_in_use_when_registered_or_when_it_has_a_state(
    monkeypatch, registered, states, *, in_use
):
    monkeypatch.setattr(const.er, "async_get", lambda _hass: FakeRegistry(registered))
    hass = SimpleNamespace(states=SimpleNamespace(get=states.get))

    assert const.entity_id_in_use(hass=hass, entity_id="sensor.a") is in_use


def _registry_entry(key, *, disabled_by=None, entry_id="entry-1"):
    return SimpleNamespace(
        unique_id=const.entity_unique_id(entry_id=entry_id, key=key),
        disabled_by=disabled_by,
    )


def _registry_of(monkeypatch, *entries):
    monkeypatch.setattr(const.er, "async_get", lambda _hass: "registry")
    monkeypatch.setattr(
        const.er,
        "async_entries_for_config_entry",
        lambda registry, entry_id: (
            list(entries) if (registry, entry_id) == ("registry", "entry-1") else []
        ),
    )


def _register(key, *, core, combination=None):
    return SimpleNamespace(
        key=key,
        core=core,
        combination=combination,
        sources=() if combination is None else combination.sources,
    )


def test_an_enabled_estimate_enables_the_readings_it_needs_whatever_their_entities_do(
    monkeypatch,
):
    _registry_of(monkeypatch, _registry_entry("input_row", disabled_by="user"))
    estimate = Combination(operation=Operation.ESTIMATE, sources=("input_row", "other"))
    registers = [
        _register("estimate_row", core=True, combination=estimate),
        _register("input_row", core=False),
        _register(
            "sum_row",
            core=True,
            combination=Combination(operation=Operation.SUM, sources=("summed",)),
        ),
    ]

    enabled = const.enabled_entity_keys(
        hass=None, entry_id="entry-1", registers=registers
    )

    assert enabled == {"estimate_row", "sum_row", "input_row", "other"}


def test_the_installation_entities_are_the_registry_entries_of_the_entry_by_key(
    monkeypatch,
):
    pv = _registry_entry("pv_power")
    foreign = SimpleNamespace(unique_id="entry-2_grid_power", disabled_by=None)
    _registry_of(monkeypatch, pv, foreign)

    assert const.installation_entities(hass=None, entry_id="entry-1") == {
        "pv_power": pv
    }


@pytest.mark.parametrize(
    ("registered", "expected"),
    [
        ({}, {"core_row"}),
        ({"core_row": "user", "other_row": None}, {"other_row"}),
        ({"core_row": None, "other_row": "integration"}, {"core_row"}),
        ({"other_row": None}, {"core_row", "other_row"}),
        ({"core_row": "user", "other_row": "user"}, set()),
    ],
)
def test_a_row_is_enabled_by_its_registry_entry_or_else_its_core_marking(
    monkeypatch, registered, expected
):
    _registry_of(
        monkeypatch,
        *(
            _registry_entry(key, disabled_by=disabled_by)
            for key, disabled_by in registered.items()
        ),
    )
    registers = [_register("core_row", core=True), _register("other_row", core=False)]

    enabled = const.enabled_entity_keys(
        hass=None, entry_id="entry-1", registers=registers
    )

    assert enabled == expected


@pytest.mark.parametrize(
    ("registered", "expected"),
    [
        ({}, set()),
        ({"battery_power_control": None}, {"battery_power_control"}),
        (
            {"battery_power_control": "user", "grid_power_target": None},
            {"grid_power_target"},
        ),
        ({"other_row": None}, set()),
    ],
)
def test_a_power_entity_is_enabled_only_when_it_is_in_the_registry_and_not_disabled(
    monkeypatch, registered, expected
):
    _registry_of(
        monkeypatch,
        *(
            _registry_entry(key, disabled_by=disabled_by)
            for key, disabled_by in registered.items()
        ),
    )

    enabled = const.enabled_power_keys(
        hass=None,
        entry_id="entry-1",
        keys=["battery_power_control", "grid_power_target", "inverter_power_target"],
    )

    assert enabled == expected


def _subentry(subentry_id, *, kind="polling_group", interval=10, keys=("a",)):
    return SimpleNamespace(
        subentry_id=subentry_id,
        subentry_type=kind,
        data={"scan_interval": interval, "keys": list(keys)},
    )


@pytest.mark.parametrize(
    ("excluding", "expected_intervals"),
    [(None, [10, 30]), ("g1", [30]), ("g2", [10]), ("unknown", [10, 30])],
)
def test_group_cadences_cover_polling_groups_only_and_can_leave_one_out(
    excluding, expected_intervals
):
    entry = SimpleNamespace(
        subentries={
            "g1": _subentry("g1", interval=10, keys=("a", "b")),
            "other": _subentry("other", kind="something_else", interval=5),
            "g2": _subentry("g2", interval=30, keys=("c",)),
        }
    )

    cadences = const.group_cadences(entry=entry, excluding=excluding)

    assert [cadence.interval for cadence in cadences] == expected_intervals
    assert all(isinstance(cadence.keys, frozenset) for cadence in cadences)
    assert const.group_cadences(entry=entry)[0].keys == {"a", "b"}


async def test_selector_options_are_the_translated_labels_of_one_selector(monkeypatch):
    asked = []

    async def translations(hass, language, category, integrations):
        asked.append((hass, language, category, integrations))
        return {
            "component.saj_local.selector.power_function.options.battery": "Batterie",
            "component.saj_local.selector.power_function.options.grid": "Netz",
            "component.saj_local.selector.other.options.battery": "Other",
            "component.saj_local.issues.model_mismatch.title": "Title",
        }

    monkeypatch.setattr(const, "async_get_translations", translations)
    hass = SimpleNamespace(config=SimpleNamespace(language="de"))

    options = await const.selector_options(hass=hass, selector_name="power_function")

    assert options == {"battery": "Batterie", "grid": "Netz"}
    assert asked == [(hass, "de", "selector", [const.DOMAIN])]


def test_installations_of_one_endpoint_share_a_guard_whatever_the_host_case():
    hass = SimpleNamespace(data={})

    first = const.endpoint_guard(hass=hass, host="Inverter.Local", port=502)

    assert const.endpoint_guard(hass=hass, host="inverter.local", port=502) is first
    assert const.endpoint_guard(hass=hass, host="inverter.local", port=503) is not first
    assert const.endpoint_guard(hass=hass, host="other.local", port=502) is not first


def _schedule_subentry(subentry_id, *, kind="power_schedule", function="battery"):
    return SimpleNamespace(
        subentry_id=subentry_id,
        subentry_type=kind,
        data={"function": function, "schedule": f"registry-{subentry_id}"},
    )


@pytest.mark.parametrize(
    ("excluding", "expected"),
    [
        (None, [("battery", "registry-s1"), ("grid", "registry-s2")]),
        ("s1", [("grid", "registry-s2")]),
        ("s2", [("battery", "registry-s1")]),
        ("unknown", [("battery", "registry-s1"), ("grid", "registry-s2")]),
    ],
)
def test_power_schedules_cover_schedule_subentries_only_and_can_leave_one_out(
    excluding, expected
):
    entry = SimpleNamespace(
        subentries={
            "s1": _schedule_subentry("s1", function="battery"),
            "other": _schedule_subentry("other", kind="polling_group"),
            "s2": _schedule_subentry("s2", function="grid"),
        }
    )

    schedules = const.power_schedules(entry=entry, excluding=excluding)

    assert [(item.function.value, item.registry_id) for item in schedules] == expected
