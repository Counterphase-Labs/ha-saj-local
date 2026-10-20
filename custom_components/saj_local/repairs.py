from dataclasses import dataclass
from typing import TYPE_CHECKING

import voluptuous as vol
from homeassistant.components.repairs import RepairsFlow
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import issue_registry as ir

from .config_flow import (
    ABORT_ALREADY_CONFIGURED,
    ABORT_CHANGES_SAVED,
    BASE_ERROR,
    EntryChanges,
    Validation,
)
from .const import (
    CONF_ALLOW_CONTROL,
    CONF_EMS_HEARTBEAT,
    CONF_EQUIPMENT,
    CONF_MODEL,
    CONF_PREFIX,
    CONF_SCAN_INTERVAL,
    CONF_UNIT_ID,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_UNIT_ID,
    DOMAIN,
    ISSUE_REGISTERS_REFUSED,
    installation_entities,
)
from .issues import (
    DATA_ENTRY_ID,
    DATA_ISSUE,
    DATA_KEYS,
    DATA_NAMED,
    KEY_SEPARATOR,
    log_fixed,
)
from .saj.profiles import AUTOMATIC

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.data_entry_flow import FlowResult

STEP_CONFIRM = "confirm"
ERROR_DEVICE_CHANGED = "device_changed"
ABORT_ENTRY_REMOVED = "entry_removed"
UNKNOWN_VALUE = "?"
ISSUE_DATA = dict[str, str | int | float | None]


@dataclass(frozen=True)
class Detected:
    model: str
    serial: str


def adoption_input(*, entry: ConfigEntry) -> dict[str, object]:
    options = entry.options
    values: dict[str, object] = {
        CONF_HOST: entry.data[CONF_HOST],
        CONF_PORT: entry.data.get(CONF_PORT, DEFAULT_PORT),
        CONF_UNIT_ID: entry.data.get(CONF_UNIT_ID, DEFAULT_UNIT_ID),
        CONF_SCAN_INTERVAL: options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        CONF_MODEL: AUTOMATIC,
        CONF_PREFIX: options.get(CONF_PREFIX, ""),
        CONF_ALLOW_CONTROL: options.get(CONF_ALLOW_CONTROL, False),
        CONF_EQUIPMENT: dict(options.get(CONF_EQUIPMENT, {})),
    }
    if CONF_EMS_HEARTBEAT in options:
        values[CONF_EMS_HEARTBEAT] = options[CONF_EMS_HEARTBEAT]
    return values


class ConfirmFlow(RepairsFlow):
    async_step_confirm: Callable[[dict[str, str] | None], Awaitable[FlowResult]]

    async def async_step_init(
        self, user_input: dict[str, str] | None = None
    ) -> FlowResult:
        del user_input
        return await self.async_step_confirm(None)

    def issue_placeholders(self) -> dict[str, str]:
        issue = ir.async_get(self.hass).async_get_issue(DOMAIN, self.issue_id)
        return {} if issue is None else dict(issue.translation_placeholders or {})


class ModelFixFlow(ConfirmFlow):
    def __init__(self, *, entry_id: str, key: str, named: str) -> None:
        self._entry_id = entry_id
        self._key = key
        self._named = named
        self._shown: Detected | None = None

    async def async_step_confirm(
        self, user_input: dict[str, str] | None = None
    ) -> FlowResult:
        entry = self.hass.config_entries.async_get_entry(self._entry_id)
        if entry is None:
            return self.async_abort(reason=ABORT_ENTRY_REMOVED)
        changes = EntryChanges(hass=self.hass, entry=entry)
        validation = await changes.validate(user_input=adoption_input(entry=entry))
        change = validation.change
        if change is not None and changes.serial_exists_for_other(
            serial=change.device.serial
        ):
            validation = Validation(errors={BASE_ERROR: ABORT_ALREADY_CONFIGURED})
            change = None
        if change is None:
            return self._form(entry=entry, validation=validation)
        detected = Detected(
            model=change.device.profile.display_name, serial=change.device.serial
        )
        if user_input is not None and detected == self._shown:
            reloads_itself = bool(entry.update_listeners)
            reason = await changes.save(change=change)
            if reason != ABORT_CHANGES_SAVED:
                return self.async_abort(reason=reason)
            if not reloads_itself:
                self.hass.config_entries.async_schedule_reload(entry.entry_id)
            log_fixed(entry=entry, key=self._key)
            return self.async_create_entry(data={})
        differs = self._named not in (detected.model, detected.serial)
        self._shown = detected
        return self._form(
            entry=entry,
            validation=Validation(
                errors={BASE_ERROR: ERROR_DEVICE_CHANGED}
                if differs or user_input is not None
                else {},
                placeholders={"model": detected.model, "serial": detected.serial},
            ),
        )

    def _form(self, *, entry: ConfigEntry, validation: Validation) -> FlowResult:
        errors = (
            {BASE_ERROR: next(iter(validation.errors.values()))}
            if validation.errors
            else {}
        )
        raised_with = self.issue_placeholders()
        return self.async_show_form(
            step_id=STEP_CONFIRM,
            data_schema=vol.Schema({}),
            errors=errors,
            description_placeholders={
                "selected_model": UNKNOWN_VALUE,
                "approved_serial": UNKNOWN_VALUE,
                "model": raised_with.get("detected_model", UNKNOWN_VALUE),
                "serial": raised_with.get("found_serial", UNKNOWN_VALUE),
                **raised_with,
                "installation": entry.title,
                **validation.placeholders,
            },
        )


class RefusedFixFlow(ConfirmFlow):
    def __init__(self, *, entry_id: str, keys: frozenset[str]) -> None:
        self._entry_id = entry_id
        self._keys = keys

    async def async_step_confirm(
        self, user_input: dict[str, str] | None = None
    ) -> FlowResult:
        if user_input is None:
            return self.async_show_form(
                step_id=STEP_CONFIRM,
                data_schema=vol.Schema({}),
                description_placeholders=self.issue_placeholders(),
            )
        entry = self.hass.config_entries.async_get_entry(self._entry_id)
        if entry is None:
            return self.async_abort(reason=ABORT_ENTRY_REMOVED)
        registry = er.async_get(self.hass)
        registered = installation_entities(hass=self.hass, entry_id=self._entry_id)
        for key in sorted(self._keys & registered.keys()):
            registry.async_update_entity(
                registered[key].entity_id,
                disabled_by=er.RegistryEntryDisabler.USER,
            )
        log_fixed(entry=entry, key=ISSUE_REGISTERS_REFUSED)
        return self.async_create_entry(data={})


async def async_create_fix_flow(
    hass: HomeAssistant, issue_id: str, data: ISSUE_DATA | None
) -> RepairsFlow:
    del hass, issue_id
    values = data or {}
    entry_id = str(values[DATA_ENTRY_ID])
    if DATA_KEYS in values:
        return RefusedFixFlow(
            entry_id=entry_id,
            keys=frozenset(str(values[DATA_KEYS]).split(KEY_SEPARATOR)),
        )
    return ModelFixFlow(
        entry_id=entry_id,
        key=str(values[DATA_ISSUE]),
        named=str(values[DATA_NAMED]),
    )
