from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

import pytest
from homeassistant import config_entries as config_entries_module
from homeassistant.config_entries import ConfigSubentry
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.saj_local import config_flow
from custom_components.saj_local.const import (
    CONF_KEYS,
    CONF_SCAN_INTERVAL,
    DOMAIN,
    SUBENTRY_POLLING_GROUP,
    entity_unique_id,
)
from custom_components.saj_local.saj.device import Device
from custom_components.saj_local.saj.profiles import PROFILES
from custom_components.saj_local.saj.telemetry import Readout

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

KEYS = ("pv_power", "battery_power", "grid_power", "load_power")
H2 = next(profile for profile in PROFILES if profile.key == "h2")
HS3 = next(profile for profile in PROFILES if profile.key == "hs3")


class QuietClient:
    def __init__(self, **_parameters) -> None:
        return

    async def close(self, **_options) -> None:
        return


@pytest.fixture(autouse=True)
def _integration(enable_custom_integrations, monkeypatch):
    del enable_custom_integrations

    # Starting a flow sets up the integration's dependencies, the frontend and the
    # http server, which takes longer than the flow and is not what these tests prove.
    async def no_dependencies(*_arguments):
        return None

    monkeypatch.setattr(
        config_entries_module, "async_process_deps_reqs", no_dependencies
    )


@pytest.fixture
def entry(hass) -> ConfigEntry:
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="H2-SERIAL",
        data={
            "host": "inverter",
            "port": 502,
            "unit_id": 1,
            "model": "automatic",
            "device_type": min(H2.device_types),
            "fitted_equipment": ["battery"],
        },
        options={"scan_interval": 60},
    )
    config_entry.add_to_hass(hass)
    return config_entry


@pytest.fixture
def entities(hass, entry) -> er.EntityRegistry:
    registry = er.async_get(hass)
    for key in KEYS:
        registered = registry.async_get_or_create(
            "sensor",
            DOMAIN,
            entity_unique_id(entry_id=entry.entry_id, key=key),
            config_entry=entry,
            suggested_object_id=f"saj_{key}",
            original_name=key.replace("_", " ").title(),
        )
        registry.async_update_entity(
            registered.entity_id, name=f"My {key}", icon="mdi:flash"
        )
    registry.async_update_entity(
        "sensor.saj_load_power", disabled_by=er.RegistryEntryDisabler.USER
    )
    return registry


def _snapshot(registry: er.EntityRegistry, entry: ConfigEntry) -> dict[str, tuple]:
    return {
        registered.entity_id: (
            registered.id,
            registered.unique_id,
            registered.name,
            registered.original_name,
            registered.icon,
            registered.disabled_by,
            registered.config_entry_id,
            registered.config_subentry_id,
        )
        for registered in er.async_entries_for_config_entry(registry, entry.entry_id)
    }


def _seed_groups(hass, entry, groups):
    for name, keys in groups.items():
        hass.config_entries.async_add_subentry(
            entry,
            ConfigSubentry(
                data=MappingProxyType({CONF_SCAN_INTERVAL: 10, CONF_KEYS: keys}),
                subentry_type=SUBENTRY_POLLING_GROUP,
                title=name,
                unique_id=None,
            ),
        )


async def _save_group(hass, entry, *, name, keys, subentry_id=None):
    manager = hass.config_entries.subentries
    context = {"source": "user"}
    if subentry_id is not None:
        context = {"source": "reconfigure", "subentry_id": subentry_id}
    result = await manager.async_init(
        (entry.entry_id, SUBENTRY_POLLING_GROUP), context=context
    )
    assert result["type"] is FlowResultType.FORM
    result = await manager.async_configure(
        result["flow_id"],
        {"name": name, "scan_interval": 10, "keys": list(keys)},
    )
    assert result["type"] is FlowResultType.MENU
    result = await manager.async_configure(
        result["flow_id"], {"next_step_id": "save_group"}
    )
    assert result["type"] in {FlowResultType.CREATE_ENTRY, FlowResultType.ABORT}


def _group_id(entry, title):
    return next(
        subentry.subentry_id
        for subentry in entry.subentries.values()
        if subentry.title == title
    )


def _keys_of(entry, title):
    return set(entry.subentries[_group_id(entry, title)].data["keys"])


async def test_deleting_groups_leaves_entities_alone(hass, entry, entities):
    _seed_groups(hass, entry, {"Fast": ["battery_power"], "Slow": ["grid_power"]})
    before = _snapshot(entities, entry)

    for title in ("Fast", "Slow"):
        hass.config_entries.async_remove_subentry(entry, _group_id(entry, title))

    assert entry.subentries == {}
    assert _snapshot(entities, entry) == before


async def test_creating_a_group_leaves_entities_alone(hass, entry, entities):
    _seed_groups(hass, entry, {"Slow": ["grid_power"]})
    before = _snapshot(entities, entry)
    assert len(before) == len(KEYS)

    await _save_group(hass, entry, name="Fast", keys=["pv_power", "battery_power"])

    assert _keys_of(entry, "Fast") == {"pv_power", "battery_power"}
    assert _snapshot(entities, entry) == before


@pytest.mark.parametrize(
    ("groups", "edit"),
    [
        (
            {"Fast": ["pv_power", "battery_power"], "Slow": ["grid_power"]},
            ("Fast", ["battery_power"]),
        ),
        (
            {"Fast": ["battery_power"], "Slow": ["grid_power"]},
            ("Slow", ["grid_power", "pv_power"]),
        ),
        (
            {"Fast": ["battery_power"], "Slow": ["grid_power", "pv_power"]},
            ("Slow", ["grid_power"]),
        ),
    ],
    ids=["moving out of a group", "moving into a group", "removing from a group"],
)
async def test_moving_and_removing_sensors_leave_entities_alone(
    hass, entry, entities, groups, edit
):
    name, keys = edit
    _seed_groups(hass, entry, groups)
    before = _snapshot(entities, entry)

    await _save_group(
        hass, entry, name=name, keys=keys, subentry_id=_group_id(entry, name)
    )

    assert _keys_of(entry, name) == set(keys)
    assert _snapshot(entities, entry) == before


@pytest.mark.parametrize(
    "swap",
    [(H2, HS3, "HS3-SERIAL"), (HS3, H2, "H2-SERIAL-2")],
)
async def test_replacing_the_model_while_groups_exist_leaves_entities_alone(
    hass, monkeypatch, entry, entities, swap
):
    start, end, end_serial = swap
    _seed_groups(hass, entry, {"Fast": ["pv_power", "battery_power"]})
    before = _snapshot(entities, entry)
    groups_before = {key: dict(value.data) for key, value in entry.subentries.items()}
    replacement = Device(
        end_serial,
        min(end.device_types),
        12000,
        end,
        detected=True,
    )

    async def identify(client, selection):
        del client, selection
        return replacement

    async def read(client, device, enabled):
        del client, device, enabled
        return Readout(values={}, refusals={})

    monkeypatch.setattr(config_flow, "ModbusTcpClient", QuietClient)
    monkeypatch.setattr(config_flow, "identify", identify)
    monkeypatch.setattr(config_flow, "read_telemetry", read)
    hass.config_entries.async_update_entry(entry, unique_id=f"{start.key}-OLD")

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            "host": "inverter",
            "port": 502,
            "unit_id": 1,
            "scan_interval": 60,
            "model": "automatic",
        },
    )
    assert result["step_id"] == "confirm_replacement"
    result = await hass.config_entries.options.async_configure(result["flow_id"], {})

    assert result["type"] is FlowResultType.ABORT
    assert entry.unique_id == end_serial
    assert _snapshot(entities, entry) == before
    assert {key: dict(value.data) for key, value in entry.subentries.items()} == (
        groups_before
    )
