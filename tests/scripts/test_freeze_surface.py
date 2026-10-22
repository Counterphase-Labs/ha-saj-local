from __future__ import annotations

import importlib
import json
import runpy
import sys
from enum import StrEnum
from types import SimpleNamespace

import freeze_surface
import pytest

ENTRY_ID = "<entry id>"


class Kind(StrEnum):
    SENSOR = "sensor"
    BINARY_SENSOR = "binary_sensor"


class DeviceClass(StrEnum):
    POWER = "power"


class FakeEntity:
    def __init__(self, *, coordinator, register, prefix):
        self.coordinator = coordinator
        self.native_unit_of_measurement = register.unit
        self.device_class = register.device_class
        self.options = register.options
        self.prefix = prefix


class FakeSensor(FakeEntity):
    state_class = "measurement"


class FakeBinarySensor(FakeEntity):
    pass


class FakePowerEntity:
    unit_of_measurement = None
    device_class = None

    def __init__(self, *, coordinator, function, identity):
        self.coordinator = coordinator
        self.function = function
        self.identity = identity


class FakeControlAllowed:
    device_class = None

    def __init__(self, *, coordinator, prefix):
        self.coordinator = coordinator
        self.prefix = prefix


class FakeBase:
    def __init__(self, *, coordinator, identity, category, enabled_default):
        self.unique_id = f"{coordinator.entry_id}_{identity.key}"
        prefix = f"{identity.prefix}_" if identity.prefix else ""
        self.entity_id = f"{identity.domain}.saj_{prefix}{identity.key}"
        self.device_info = {"identifiers": {("saj_local", coordinator.entry_id)}}
        assert category is None
        assert enabled_default is True


def register(*, key, kind, unit=None, device_class=None, options=None, **flags):
    return SimpleNamespace(
        key=key,
        kind=kind,
        unit=unit,
        device_class=device_class,
        options=options,
        exposed=flags.get("exposed", True),
        private=flags.get("private", False),
        definition=SimpleNamespace(inverted=flags.get("inverted", False)),
    )


class Function(StrEnum):
    GRID = "grid"

    @property
    def target_key(self):
        return f"{self.value}_target"

    @property
    def switch_key(self):
        return f"{self.value}_switch"


class Submission:
    def __init__(self, **fields):
        del fields
        self.entry_options = {"scan_interval": 0, "prefix": ""}
        self.entry_data = {"host": ""}


class Group:
    def __init__(self, *, name, interval, keys):
        del name
        self.data = {"scan_interval": interval, "keys": list(keys)}


class Change:
    def __init__(self, *, submission, device):
        self.entry_data = {**submission.entry_data, "device_type": device.device_type}


class Flow:
    VERSION = 1
    MINOR_VERSION = 2


class Store:
    key = f"saj_local.power_control.{ENTRY_ID}"
    version = 1


def settled_data(*, data, remembered, fitted, limit):
    return {"detected_equipment": [], "highest_pack_count": limit}


def power_control_store(**fields):
    del fields
    return Store


def fake_modules():
    catalogue = SimpleNamespace(
        registers=(
            register(
                key="battery_power",
                kind=Kind.SENSOR,
                unit="W",
                device_class=DeviceClass.POWER,
            ),
            register(
                key="mode", kind=Kind.SENSOR, device_class="enum", options=["a", "b"]
            ),
            register(key="alarm", kind=Kind.BINARY_SENSOR, inverted=True),
            register(key="hidden", kind=Kind.SENSOR, exposed=False),
            register(key="raw", kind=Kind.SENSOR, private=True),
        ),
        profile=SimpleNamespace(power_control={Function.GRID: object()}),
    )
    return {
        "saj.catalogue": SimpleNamespace(CATALOGUES={"hs3": catalogue}),
        "sensor": SimpleNamespace(SajSensor=FakeSensor),
        "binary_sensor": SimpleNamespace(
            SajBinarySensor=FakeBinarySensor,
            SajControlAllowedSensor=FakeControlAllowed,
            CONTROL_ALLOWED_KEY="control_allowed",
        ),
        "number": SimpleNamespace(SajPowerNumber=FakePowerEntity),
        "switch": SimpleNamespace(SajPowerSwitch=FakePowerEntity),
        "entity": SimpleNamespace(
            SajBaseEntity=FakeBase,
            EntityIdentity=SimpleNamespace,
        ),
        "const": SimpleNamespace(
            DOMAIN_PLACEHOLDER="<domain>",
            KEY_PLACEHOLDER="<key>",
            SUBENTRY_POLLING_GROUP="group",
            SUBENTRY_POWER_SCHEDULE="schedule",
            CONF_FUNCTION="function",
            CONF_SCHEDULE="schedule",
            STORED_TARGETS="targets",
            STORED_MODES="modes",
        ),
        "config_flow": SimpleNamespace(
            Submission=Submission,
            PendingChange=Change,
            PollingGroup=Group,
            SajLocalConfigFlow=Flow,
        ),
        "equipment": SimpleNamespace(_settled_data=settled_data),
        "coordinator": SimpleNamespace(power_control_store=power_control_store),
        "saj.profiles": SimpleNamespace(
            AUTOMATIC="automatic", PROFILES=[SimpleNamespace(key="hs3")]
        ),
        "saj.models": SimpleNamespace(
            Equipment=StrEnum("Equipment", {"BATTERY": "battery"}),
            PowerFunction=Function,
        ),
        "saj.equipment": SimpleNamespace(
            Setting=StrEnum("Setting", {"A": "automatic"})
        ),
    }


def importer(modules):
    return lambda name: modules[name.removeprefix(f"{freeze_surface.PACKAGE}.")]


def write_frontend(tree, files):
    for name, text in files.items():
        path = tree / "frontend" / "src" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def card_source(*, fields, constants=""):
    return (
        constants
        + 'const TYPE = "saj-local-status-card";\n'
        + "class Card {\n"
        + "    static getConfigForm(): ReturnType<typeof configForm> {\n"
        + f"        return configForm((text) => [{fields}]);\n"
        + "    }\n"
        + "}\n"
        + 'registerCard({\n    type: TYPE,\n    nameKey: "x",\n});\n'
    )


EDITOR = {
    "cards/editor.ts": (
        "const DEVICE_FIELD: EditorField = {\n"
        '    name: "device",\n    required: true,\n};\n'
    )
}
FRONTEND = {
    **EDITOR,
    "cards/status.ts": card_source(
        fields=(
            'booleanField({ name: "show_energy", fallback: true }),\n'
            '            selectField({\n                name: "scope",\n'
            "                options: SCOPES.map((scope) => ({ value: scope })),\n"
            "            }),\n"
            '            multiSelectField({ name: "sections", options: IDS.map(f) }),'
        ),
        constants=(
            'export const SCOPES: readonly Scope[] = ["b", "a"];\n'
            'export const IDS = [\n    "x",\n    "y",\n] as const;\n'
        ),
    ),
    "badges/status.ts": card_source(fields="").replace("registerCard", "registerBadge"),
    "features/weekdays.ts": (
        'registerCardFeature({ type: "saj-local-weekdays", nameKey: "x" });\n'
    ),
    "registration.ts": "export const registerCard = ({ type }) => type;\n",
}


@pytest.fixture
def tree(tmp_path):
    write_frontend(tmp_path, FRONTEND)
    return tmp_path


def test_every_exposed_and_private_register_is_listed_under_its_platform(tree):
    surface = freeze_surface.build_surface(
        tree=tree, import_module=importer(fake_modules())
    )

    assert surface["hs3"]["sensor"] == {
        "battery_power": {
            "unit": "W",
            "device_class": "power",
            "state_class": "measurement",
            "options": None,
            "inverted": False,
        },
        "mode": {
            "unit": None,
            "device_class": "enum",
            "state_class": "measurement",
            "options": ["a", "b"],
            "inverted": False,
        },
        "raw": {
            "unit": None,
            "device_class": None,
            "state_class": "measurement",
            "options": None,
            "inverted": False,
        },
    }
    assert surface["hs3"]["binary_sensor"]["alarm"] == {
        "unit": None,
        "device_class": None,
        "state_class": None,
        "options": None,
        "inverted": True,
    }


def test_the_power_and_control_allowed_entities_join_their_platforms(tree):
    surface = freeze_surface.build_surface(
        tree=tree, import_module=importer(fake_modules())
    )

    assert set(surface["hs3"]["number"]) == {"grid_target"}
    assert set(surface["hs3"]["switch"]) == {"grid_switch"}
    assert "control_allowed" in surface["hs3"]["binary_sensor"]


def test_the_identifier_forms_come_from_the_entity_code(tree):
    surface = freeze_surface.build_surface(
        tree=tree, import_module=importer(fake_modules())
    )

    assert surface["identifiers"] == {
        "unique_id": f"{ENTRY_ID}_<key>",
        "entity_id": "<domain>.saj_<prefix>_<key>",
        "entity_id_without_prefix": "<domain>.saj_<key>",
        "device_identifiers": {"saj_local": ENTRY_ID},
    }


def test_the_stored_forms_come_from_the_configuration_code(tree):
    surface = freeze_surface.build_surface(
        tree=tree, import_module=importer(fake_modules())
    )

    assert surface["stored"] == {
        "config_entry_data_keys": [
            "detected_equipment",
            "device_type",
            "highest_pack_count",
            "host",
        ],
        "config_entry_option_keys": ["prefix", "scan_interval"],
        "subentries": {
            "group": {"data_keys": ["keys", "scan_interval"]},
            "schedule": {"data_keys": ["function", "schedule"]},
        },
        "power_control_store": {
            "key": f"saj_local.power_control.{ENTRY_ID}",
            "version": 1,
            "top_level_keys": ["modes", "targets"],
        },
        "config_flow": {"VERSION": 1, "MINOR_VERSION": 2},
        "values": {
            "model": ["automatic", "hs3"],
            "equipment_name": ["battery"],
            "equipment_setting": ["automatic"],
            "power_function": ["grid"],
        },
    }


def test_the_frontend_registrations_give_each_type_with_its_settings(tree):
    surface = freeze_surface.build_surface(
        tree=tree, import_module=importer(fake_modules())
    )

    assert surface["cards"] == {
        "saj-local-status-card": {
            "settings": {
                "device": [],
                "show_energy": [],
                "scope": ["a", "b"],
                "sections": ["x", "y"],
            }
        }
    }
    assert surface["badges"] == {"saj-local-status-card": {"settings": {"device": []}}}
    assert surface["card_features"] == {"saj-local-weekdays": {"settings": {}}}


def test_a_select_setting_without_an_options_constant_fails_loudly(tmp_path):
    write_frontend(
        tmp_path,
        {
            **EDITOR,
            "card.ts": card_source(
                fields='selectField({ name: "scope", options: [] })'
            ),
        },
    )

    with pytest.raises(freeze_surface.SurfaceError, match="scope has no options"):
        freeze_surface.build_surface(
            tree=tmp_path, import_module=importer(fake_modules())
        )


def test_an_options_constant_that_is_no_array_fails_loudly(tmp_path):
    write_frontend(
        tmp_path,
        {
            **EDITOR,
            "card.ts": card_source(
                fields='selectField({ name: "scope", options: MISSING.map(f) })'
            ),
        },
    )

    with pytest.raises(freeze_surface.SurfaceError, match="MISSING"):
        freeze_surface.build_surface(
            tree=tmp_path, import_module=importer(fake_modules())
        )


def test_an_editor_form_that_does_not_use_config_form_fails_loudly(tmp_path):
    source = card_source(fields="").replace("configForm((text) =>", "other((text) =>")
    write_frontend(tmp_path, {"card.ts": source})

    with pytest.raises(freeze_surface.SurfaceError, match="builds no editor form"):
        freeze_surface.build_surface(
            tree=tmp_path, import_module=importer(fake_modules())
        )


def test_a_shared_editor_without_a_device_field_fails_loudly(tmp_path):
    write_frontend(tmp_path, {"card.ts": card_source(fields="")})

    with pytest.raises(freeze_surface.SurfaceError, match="no device field"):
        freeze_surface.build_surface(
            tree=tmp_path, import_module=importer(fake_modules())
        )


def test_a_card_without_an_editor_fails_loudly(tmp_path):
    write_frontend(
        tmp_path, {"card.ts": 'registerCard({ type: "saj-local-x-card" });\n'}
    )

    with pytest.raises(freeze_surface.SurfaceError, match="no editor settings"):
        freeze_surface.build_surface(
            tree=tmp_path, import_module=importer(fake_modules())
        )


def test_a_source_with_no_registrations_fails_loudly(tmp_path):
    write_frontend(tmp_path, {"registration.ts": FRONTEND["registration.ts"]})

    with pytest.raises(freeze_surface.SurfaceError, match="no card, badge"):
        freeze_surface.build_surface(
            tree=tmp_path, import_module=importer(fake_modules())
        )


def test_a_registered_type_without_a_string_constant_fails_loudly(tmp_path):
    write_frontend(
        tmp_path,
        {
            **EDITOR,
            "card.ts": card_source(fields="").replace("type: TYPE", "type: MISSING"),
        },
    )

    with pytest.raises(freeze_surface.SurfaceError, match="MISSING"):
        freeze_surface.build_surface(
            tree=tmp_path, import_module=importer(fake_modules())
        )


def test_main_prints_the_surface_as_sorted_json(tree, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["freeze_surface.py", str(tree)])
    monkeypatch.setattr(sys, "path", list(sys.path))
    monkeypatch.setattr(
        freeze_surface.importlib, "import_module", importer(fake_modules())
    )

    assert freeze_surface.main() == 0

    printed = json.loads(capsys.readouterr().out)
    assert sorted(printed) == [
        "badges",
        "card_features",
        "cards",
        "hs3",
        "identifiers",
        "stored",
    ]
    assert sys.path[0] == str(tree.resolve())


def test_main_reports_a_surface_error_on_standard_error(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["freeze_surface.py", str(tmp_path)])
    monkeypatch.setattr(sys, "path", list(sys.path))
    monkeypatch.setattr(
        freeze_surface.importlib, "import_module", importer(fake_modules())
    )

    assert freeze_surface.main() == 1

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "no card, badge" in captured.err


def test_running_the_surface_as_a_script_exits_with_the_status_of_main(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(sys, "argv", ["freeze_surface.py", str(tmp_path)])
    monkeypatch.setattr(sys, "path", list(sys.path))
    monkeypatch.setattr(importlib, "import_module", importer(fake_modules()))

    with pytest.raises(SystemExit) as stopped:
        runpy.run_module("freeze_surface", run_name="__main__")

    assert stopped.value.code == 1
