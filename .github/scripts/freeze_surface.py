from __future__ import annotations

import importlib
import json
import re
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from types import SimpleNamespace
from typing import Any

PACKAGE = "custom_components.saj_local"
FRONTEND_SOURCE = Path("frontend/src")
ENTRY_ID_PLACEHOLDER = "<entry id>"
PREFIX_PLACEHOLDER = "<prefix>"
SETTLED_DATA = "_settled_data"
POWER_ENTITIES = {
    "number": ("SajPowerNumber", "target_key"),
    "switch": ("SajPowerSwitch", "switch_key"),
}
FRONTEND_REGISTRATIONS = {
    "cards": "registerCard",
    "badges": "registerBadge",
    "card_features": "registerCardFeature",
}
EDITOR_FORM = re.compile(r"static getConfigForm\(\)[^{]*\{(.*?)\n    \}\n", re.DOTALL)
EDITOR_FIELD = re.compile(
    r'\b(boolean|select|multiSelect)Field\(\{\s*name:\s*"([a-z_]+)"'
)
OPTIONS_SOURCE = re.compile(r"\boptions:\s*([A-Z_]+)\.map\(")
DEVICE_FIELD = re.compile(r'\bDEVICE_FIELD\b[^=]*=\s*\{\s*name:\s*"([a-z_]+)"')
Importer = Callable[[str], Any]


class SurfaceError(Exception):
    pass


def _value(item: Any) -> Any:
    return getattr(item, "value", item)


def _coordinator() -> SimpleNamespace:
    device = SimpleNamespace(
        profile=SimpleNamespace(display_name=""),
        rated_power=0,
        detected=True,
        serial="",
    )
    return SimpleNamespace(entry_id=ENTRY_ID_PLACEHOLDER, device=device)


def _hass() -> SimpleNamespace:
    return SimpleNamespace(data={}, config=SimpleNamespace(config_dir=""))


def _form(*, entity: Any, inverted: bool) -> dict[str, Any]:
    options = getattr(entity, "options", None)
    return {
        "unit": getattr(entity, "native_unit_of_measurement", None),
        "device_class": _value(entity.device_class),
        "state_class": _value(getattr(entity, "state_class", None)),
        "options": None if options is None else list(options),
        "inverted": inverted,
    }


def _class_name(*, kind: str) -> str:
    return "Saj" + "".join(part.title() for part in kind.split("_"))


def _model_entities(*, load: Importer, catalogue: Any) -> dict[str, dict[str, Any]]:
    entity = load("entity")
    coordinator = _coordinator()
    forms: dict[str, dict[str, Any]] = {}
    for register in catalogue.registers:
        if not register.exposed:
            continue
        kind = _value(register.kind)
        created = getattr(load(kind), _class_name(kind=kind))(
            coordinator=coordinator, register=register, prefix=""
        )
        forms.setdefault(kind, {})[register.key] = _form(
            entity=created, inverted=register.definition.inverted
        )
    for kind, (class_name, key_name) in POWER_ENTITIES.items():
        for function in catalogue.profile.power_control:
            key = getattr(function, key_name)
            created = getattr(load(kind), class_name)(
                coordinator=coordinator,
                function=function,
                identity=entity.EntityIdentity(domain=kind, key=key, prefix=""),
            )
            forms.setdefault(kind, {})[key] = _form(entity=created, inverted=False)
    allowed = load("binary_sensor").SajControlAllowedSensor(
        coordinator=coordinator, prefix=""
    )
    forms.setdefault("binary_sensor", {})[load("binary_sensor").CONTROL_ALLOWED_KEY] = (
        _form(entity=allowed, inverted=False)
    )
    return forms


def _identifiers(*, load: Importer) -> dict[str, Any]:
    entity = load("entity")
    const = load("const")

    def base(*, prefix: str) -> Any:
        return entity.SajBaseEntity(
            coordinator=_coordinator(),
            identity=entity.EntityIdentity(
                domain=const.DOMAIN_PLACEHOLDER,
                key=const.KEY_PLACEHOLDER,
                prefix=prefix,
            ),
            category=None,
            enabled_default=True,
        )

    prefixed = base(prefix=PREFIX_PLACEHOLDER)
    return {
        "unique_id": prefixed.unique_id,
        "entity_id": prefixed.entity_id,
        "entity_id_without_prefix": base(prefix="").entity_id,
        "device_identifiers": dict(prefixed.device_info["identifiers"]),
    }


def _stored(*, load: Importer) -> dict[str, Any]:
    const = load("const")
    config_flow = load("config_flow")
    submission = config_flow.Submission(
        host="",
        port=0,
        unit_id=0,
        scan_interval=0,
        model="",
        prefix="",
        allow_control=True,
        ems_heartbeat=0,
        equipment={"": ""},
    )
    change = config_flow.PendingChange(
        submission=submission, device=SimpleNamespace(device_type=0)
    )
    settled = getattr(load("equipment"), SETTLED_DATA)(
        data={}, remembered=(), fitted=(), limit=0
    )
    group = config_flow.PollingGroup(name="", interval=0, keys=())
    store = load("coordinator").power_control_store(
        hass=_hass(), entry_id=ENTRY_ID_PLACEHOLDER
    )
    flow = config_flow.SajLocalConfigFlow
    profiles = load("saj.profiles")
    models = load("saj.models")
    return {
        "config_entry_data_keys": sorted({*change.entry_data, *settled}),
        "config_entry_option_keys": sorted(submission.entry_options),
        "subentries": {
            const.SUBENTRY_POLLING_GROUP: {"data_keys": sorted(group.data)},
            const.SUBENTRY_POWER_SCHEDULE: {
                "data_keys": sorted([const.CONF_FUNCTION, const.CONF_SCHEDULE])
            },
        },
        "power_control_store": {
            "key": store.key,
            "version": store.version,
            "top_level_keys": sorted([const.STORED_TARGETS, const.STORED_MODES]),
        },
        "config_flow": {"VERSION": flow.VERSION, "MINOR_VERSION": flow.MINOR_VERSION},
        "values": {
            "model": sorted([profiles.AUTOMATIC, *(p.key for p in profiles.PROFILES)]),
            "equipment_name": sorted(_value(item) for item in models.Equipment),
            "equipment_setting": sorted(
                _value(item) for item in load("saj.equipment").Setting
            ),
            "power_function": sorted(_value(item) for item in models.PowerFunction),
        },
    }


def _registered_type(*, text: str, written: str) -> str:
    if written.startswith('"'):
        return written.strip('"')
    constant = re.search(rf'\bconst\s+{written}\s*=\s*"([^"]+)"', text)
    if constant is None:
        message = f"the registered type {written} has no string constant"
        raise SurfaceError(message)
    return constant[1]


def _constant_values(*, texts: Sequence[str], name: str) -> list[str]:
    for text in texts:
        found = re.search(rf"\bconst\s+{name}\b[^=]*=\s*\[([^\]]*)\]", text)
        if found is not None:
            return re.findall(r'"([^"]+)"', found[1])
    message = f"the accepted values {name} have no array constant"
    raise SurfaceError(message)


def _device_setting(*, texts: Sequence[str]) -> str:
    for text in texts:
        found = DEVICE_FIELD.search(text)
        if found is not None:
            return found[1]
    message = "the shared editor definition has no device field"
    raise SurfaceError(message)


def _editor_settings(*, text: str, texts: Sequence[str]) -> dict[str, list[str]]:
    form = EDITOR_FORM.search(text)
    if form is None:
        return {}
    body = form[1]
    if "configForm(" not in body:
        message = "a getConfigForm builds no editor form with configForm"
        raise SurfaceError(message)
    settings: dict[str, list[str]] = {_device_setting(texts=texts): []}
    fields = list(EDITOR_FIELD.finditer(body))
    for index, field in enumerate(fields):
        end = fields[index + 1].start() if index + 1 < len(fields) else len(body)
        source = OPTIONS_SOURCE.search(body[field.end() : end])
        if field[1] == "boolean":
            settings[field[2]] = []
        elif source is None:
            message = f"the setting {field[2]} has no options constant"
            raise SurfaceError(message)
        else:
            settings[field[2]] = sorted(_constant_values(texts=texts, name=source[1]))
    return settings


def _frontend(*, source: Path) -> dict[str, dict[str, Any]]:
    found: dict[str, dict[str, Any]] = {kind: {} for kind in FRONTEND_REGISTRATIONS}
    texts = {
        path: path.read_text(encoding="utf-8") for path in sorted(source.rglob("*.ts"))
    }
    for path, text in texts.items():
        settings = _editor_settings(text=text, texts=list(texts.values()))
        for kind, call in FRONTEND_REGISTRATIONS.items():
            for written in re.findall(
                rf'\b{call}\(\{{\s*type:\s*("[^"]+"|[A-Za-z_]\w*)', text
            ):
                if kind != "card_features" and not settings:
                    message = f"{path} registers an element with no editor settings"
                    raise SurfaceError(message)
                found[kind][_registered_type(text=text, written=written)] = {
                    "settings": settings
                }
    if not any(found.values()):
        message = f"no card, badge or card feature registrations found in {source}"
        raise SurfaceError(message)
    return found


def build_surface(*, tree: Path, import_module: Importer) -> dict[str, Any]:
    def load(name: str) -> Any:
        return import_module(f"{PACKAGE}.{name}")

    catalogues = load("saj.catalogue").CATALOGUES
    return {
        **{
            key: _model_entities(load=load, catalogue=catalogue)
            for key, catalogue in catalogues.items()
        },
        "identifiers": _identifiers(load=load),
        "stored": _stored(load=load),
        **_frontend(source=tree / FRONTEND_SOURCE),
    }


def main() -> int:
    tree = Path(sys.argv[1]).resolve()
    sys.path.insert(0, str(tree))
    try:
        surface = build_surface(tree=tree, import_module=importlib.import_module)
    except SurfaceError as error:
        sys.stderr.write(f"{error}\n")
        return 1
    sys.stdout.write(json.dumps(surface, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
