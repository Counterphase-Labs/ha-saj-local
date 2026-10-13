import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers import issue_registry as ir

from .const import (
    DEFAULT_PORT,
    DOMAIN,
    EQUIPMENT_ISSUE_TRANSLATION_KEY,
    EQUIPMENT_SELECTOR,
    ISSUE_ENDPOINT_UNREACHABLE,
    ISSUE_IDENTITY_MISMATCH,
    ISSUE_MODEL_MISMATCH,
    ISSUE_REGISTERS_REFUSED,
    ISSUE_UNSUPPORTED_DEVICE,
    MODEL_ISSUES,
    UNREACHABLE_AFTER,
    installation_entities,
    selector_options,
)
from .errors import translate_error
from .label import entry_logger
from .saj.models import Equipment
from .saj.poller import IdentityChangedError

if TYPE_CHECKING:
    from collections.abc import Collection

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from .saj.guard import EndpointGuard

_LOGGER = logging.getLogger(__name__)

DATA_ENTRY_ID = "entry_id"
DATA_ISSUE = "issue"
DATA_NAMED = "named"
DATA_KEYS = "keys"
KEY_SEPARATOR = ","
NAME_SEPARATOR = ", "
NAMED_PLACEHOLDERS = {
    ISSUE_MODEL_MISMATCH: "detected_model",
    ISSUE_IDENTITY_MISMATCH: "found_serial",
    ISSUE_UNSUPPORTED_DEVICE: "device_type",
}
FIXABLE_MODEL_ISSUES = frozenset({ISSUE_MODEL_MISMATCH, ISSUE_IDENTITY_MISMATCH})


@dataclass(frozen=True)
class ModelFinding:
    key: str
    placeholders: dict[str, str]

    @property
    def named(self) -> str:
        return self.placeholders[NAMED_PLACEHOLDERS[self.key]]


def issue_id(*, entry_id: str, key: str) -> str:
    return f"{entry_id}_{key}"


def equipment_issue_id(*, entry_id: str, equipment: Equipment) -> str:
    return f"{entry_id}_{equipment.value}_not_detected"


def _is_open(*, hass: HomeAssistant, entry: ConfigEntry, key: str) -> bool:
    return (
        ir.async_get(hass).async_get_issue(
            DOMAIN, issue_id(entry_id=entry.entry_id, key=key)
        )
        is not None
    )


@dataclass(frozen=True)
class Issue:
    key: str
    severity: ir.IssueSeverity
    fixable: bool
    placeholders: dict[str, str]
    data: dict[str, str | int | float | None]


def _raise(*, hass: HomeAssistant, entry: ConfigEntry, issue: Issue) -> None:
    if not _is_open(hass=hass, entry=entry, key=issue.key):
        entry_logger(logger=_LOGGER, entry=entry).warning(
            "Repair issue %s raised", issue.key
        )
    ir.async_create_issue(
        hass,
        DOMAIN,
        issue_id(entry_id=entry.entry_id, key=issue.key),
        is_fixable=issue.fixable,
        severity=issue.severity,
        translation_key=issue.key,
        translation_placeholders={"installation": entry.title, **issue.placeholders},
        data={DATA_ENTRY_ID: entry.entry_id, **issue.data},
    )


def _clear(*, hass: HomeAssistant, entry: ConfigEntry, key: str) -> None:
    if _is_open(hass=hass, entry=entry, key=key):
        log_fixed(entry=entry, key=key)
    ir.async_delete_issue(hass, DOMAIN, issue_id(entry_id=entry.entry_id, key=key))


def log_fixed(*, entry: ConfigEntry, key: str) -> None:
    entry_logger(logger=_LOGGER, entry=entry).info("Repair issue %s cleared", key)


def model_finding(*, error: Exception) -> ModelFinding | None:
    if isinstance(error, IdentityChangedError):
        return ModelFinding(
            key=ISSUE_IDENTITY_MISMATCH, placeholders={"found_serial": error.serial}
        )
    translation = translate_error(error=error)
    if translation.concerns_model and translation.key in MODEL_ISSUES:
        return ModelFinding(key=translation.key, placeholders=translation.placeholders)
    return None


def raise_identity_issue(
    *, hass: HomeAssistant, entry: ConfigEntry, serial: str
) -> None:
    raise_model_issue(
        hass=hass,
        entry=entry,
        finding=ModelFinding(
            key=ISSUE_IDENTITY_MISMATCH, placeholders={"found_serial": serial}
        ),
    )


def raise_model_issue(
    *, hass: HomeAssistant, entry: ConfigEntry, finding: ModelFinding
) -> None:
    for other in MODEL_ISSUES:
        if other != finding.key:
            ir.async_delete_issue(
                hass, DOMAIN, issue_id(entry_id=entry.entry_id, key=other)
            )
    clear_unreachable(hass=hass, entry=entry)
    placeholders = dict(finding.placeholders)
    if finding.key == ISSUE_IDENTITY_MISMATCH:
        placeholders["approved_serial"] = entry.unique_id or ""
    _raise(
        hass=hass,
        entry=entry,
        issue=Issue(
            key=finding.key,
            severity=ir.IssueSeverity.ERROR,
            fixable=finding.key in FIXABLE_MODEL_ISSUES,
            placeholders=placeholders,
            data={DATA_ISSUE: finding.key, DATA_NAMED: finding.named},
        ),
    )


def clear_model_issues(*, hass: HomeAssistant, entry: ConfigEntry) -> None:
    for key in MODEL_ISSUES:
        _clear(hass=hass, entry=entry, key=key)


def model_issue_open(*, hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return any(_is_open(hass=hass, entry=entry, key=key) for key in MODEL_ISSUES)


def open_refusals(*, hass: HomeAssistant, entry: ConfigEntry) -> frozenset[str]:
    issue = ir.async_get(hass).async_get_issue(
        DOMAIN, issue_id(entry_id=entry.entry_id, key=ISSUE_REGISTERS_REFUSED)
    )
    if issue is None or not issue.data:
        return frozenset()
    return frozenset(str(issue.data[DATA_KEYS]).split(KEY_SEPARATOR))


def sync_refusals(
    *, hass: HomeAssistant, entry: ConfigEntry, keys: Collection[str]
) -> None:
    if not keys:
        _clear(hass=hass, entry=entry, key=ISSUE_REGISTERS_REFUSED)
        return
    registered = installation_entities(hass=hass, entry_id=entry.entry_id)
    names = [
        _entity_name(key=key, registered=registered.get(key)) for key in sorted(keys)
    ]
    _raise(
        hass=hass,
        entry=entry,
        issue=Issue(
            key=ISSUE_REGISTERS_REFUSED,
            severity=ir.IssueSeverity.WARNING,
            fixable=True,
            placeholders={"entities": NAME_SEPARATOR.join(names)},
            data={DATA_KEYS: KEY_SEPARATOR.join(sorted(keys))},
        ),
    )


def _entity_name(*, key: str, registered: object) -> str:
    name = getattr(registered, "name", None) or getattr(
        registered, "original_name", None
    )
    return name or key


def check_unreachable(
    *, hass: HomeAssistant, entry: ConfigEntry, guard: EndpointGuard, now: float
) -> None:
    failing = guard.failing_for(now=now)
    if failing is None or failing < UNREACHABLE_AFTER:
        return
    if model_issue_open(hass=hass, entry=entry):
        return
    _raise(
        hass=hass,
        entry=entry,
        issue=Issue(
            key=ISSUE_ENDPOINT_UNREACHABLE,
            severity=ir.IssueSeverity.ERROR,
            fixable=False,
            placeholders={
                "host": str(entry.data[CONF_HOST]),
                "port": str(entry.data.get(CONF_PORT, DEFAULT_PORT)),
            },
            data={},
        ),
    )


def clear_unreachable(*, hass: HomeAssistant, entry: ConfigEntry) -> None:
    _clear(hass=hass, entry=entry, key=ISSUE_ENDPOINT_UNREACHABLE)


async def sync_lapse_issues(
    *,
    hass: HomeAssistant,
    entry: ConfigEntry,
    equipment: Collection[Equipment],
    lapsed: Collection[Equipment],
) -> None:
    names = (
        await selector_options(hass=hass, selector_name=EQUIPMENT_SELECTOR)
        if lapsed
        else {}
    )
    for item in sorted(equipment):
        lapse_id = equipment_issue_id(entry_id=entry.entry_id, equipment=item)
        if item in lapsed:
            ir.async_create_issue(
                hass,
                DOMAIN,
                lapse_id,
                is_fixable=False,
                severity=ir.IssueSeverity.WARNING,
                translation_key=EQUIPMENT_ISSUE_TRANSLATION_KEY,
                translation_placeholders={
                    "installation": entry.title,
                    "equipment": names[item.value],
                },
            )
        else:
            ir.async_delete_issue(hass, DOMAIN, lapse_id)


def open_issue_keys(*, hass: HomeAssistant, entry: ConfigEntry) -> list[str]:
    keys = [
        key
        for key in (*MODEL_ISSUES, ISSUE_REGISTERS_REFUSED, ISSUE_ENDPOINT_UNREACHABLE)
        if _is_open(hass=hass, entry=entry, key=key)
    ]
    registry = ir.async_get(hass)
    keys.extend(
        f"{EQUIPMENT_ISSUE_TRANSLATION_KEY}:{item.value}"
        for item in Equipment
        if registry.async_get_issue(
            DOMAIN, equipment_issue_id(entry_id=entry.entry_id, equipment=item)
        )
        is not None
    )
    return keys


def remove_issues(*, hass: HomeAssistant, entry: ConfigEntry) -> None:
    for item in Equipment:
        ir.async_delete_issue(
            hass, DOMAIN, equipment_issue_id(entry_id=entry.entry_id, equipment=item)
        )
    for key in (*MODEL_ISSUES, ISSUE_REGISTERS_REFUSED, ISSUE_ENDPOINT_UNREACHABLE):
        ir.async_delete_issue(hass, DOMAIN, issue_id(entry_id=entry.entry_id, key=key))
