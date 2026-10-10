import re
from contextlib import nullcontext
from dataclasses import dataclass, field, replace
from functools import partial
from typing import TYPE_CHECKING, Any, Protocol

import voluptuous as vol
from homeassistant.components.recorder.statistics import async_list_statistic_ids
from homeassistant.config_entries import (
    ConfigFlow,
    ConfigFlowResult,
    ConfigSubentryFlow,
    OptionsFlow,
    SubentryFlowResult,
)
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.core import callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import selector
from homeassistant.helpers.translation import async_get_translations

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Collection, Iterable, Mapping
    from contextlib import AbstractAsyncContextManager

    from homeassistant.config_entries import ConfigEntry, ConfigSubentry
    from homeassistant.core import HomeAssistant

    from .saj.guard import EndpointGuard
    from .saj.models import Profile

from .const import (
    CONF_ALLOW_CONTROL,
    CONF_DEVICE_TYPE,
    CONF_EMS_HEARTBEAT,
    CONF_MODEL,
    CONF_PREFIX,
    CONF_SCAN_INTERVAL,
    CONF_SENSORS,
    CONF_UNIT_ID,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_UNIT_ID,
    DOMAIN,
    DOMAIN_PLACEHOLDER,
    KEY_PLACEHOLDER,
    MAX_PORT,
    MAX_UNIT_ID,
    MIN_UNIT_ID,
    REQUEST_TIMEOUT,
    SUBENTRY_POLLING_GROUP,
    enabled_entity_keys,
    endpoint_guard,
    entity_id_in_use,
    fixed_entity_id,
    group_cadences,
    installation_entities,
)
from .errors import HANDLED_ERRORS, translate_error
from .saj.budget import BUDGET_PER_MINUTE
from .saj.catalogue import (
    blocks_by_key,
    device_read_registers,
    device_registers,
    known_keys,
)
from .saj.client import ClientEnvironment, ModbusTcpClient
from .saj.device import Device, identify
from .saj.device_type import format_device_type
from .saj.ems import (
    DEFAULT_HEARTBEAT_INTERVAL,
    FUNCTION_BY_ENABLE_KEY,
    valid_heartbeat_interval,
)
from .saj.load import installation_load, requests_per_read
from .saj.profiles import AUTOMATIC, PROFILES, resolve_profile
from .saj.schedule import MIN_INTERVAL, Cadence
from .saj.telemetry import read_telemetry, setup_keys

MODEL_TRANSLATION_KEY = "model"
STEP_CONFIRM_MODEL = "confirm_model"
STEP_CONFIRM_REPLACEMENT = "confirm_replacement"
STEP_CONFIRM_PREFIX = "confirm_prefix"
STEP_CONFIRM_LOAD = "confirm_load"
STEP_CONFIRM_CONTROL = "confirm_control"
STEP_REVIEW_GROUP = "review_group"
STEP_REVIEW_GROUP_OVER_BUDGET = "review_group_over_budget"
STEP_SAVE_GROUP = "save_group"
STEP_CHANGE_SELECTION = "change_selection"
BLOCK_SELECTOR = "block"
ENTITY_STATE_SELECTOR = "entity_state"
DISABLED_STATE = "disabled"
LOAD_DECIMALS = 1
ABORT_NOT_PENDING = "confirmation_not_pending"
ABORT_ALREADY_CONFIGURED = "already_configured"
ABORT_NO_SENSORS = "no_sensors"
ABORT_ALL_SENSORS_ASSIGNED = "all_sensors_assigned"
ABORT_PREFIX_UNAVAILABLE = "prefix_unavailable"
ERROR_NO_SENSORS_SELECTED = "no_sensors_selected"
ERROR_SENSOR_IN_OTHER_GROUP = "sensor_in_other_group"
ERROR_INVALID_PREFIX = "invalid_prefix"
ERROR_PREFIX_SHADOWS_ENTITY = "prefix_shadows_entity"
ERROR_PREFIX_IN_USE = "prefix_in_use"
ERROR_ENTITY_ID_TAKEN = "entity_id_taken"
ERROR_STATISTICS_EXIST = "statistics_exist"
ERROR_INVALID_EMS_HEARTBEAT = "invalid_ems_heartbeat"
PREFIX_SHAPE = re.compile(r"[a-z0-9]+")
MAX_PREFIX_LENGTH = 32
RECORDER_COMPONENT = "recorder"
RECORDER_STATISTICS_SOURCE = "recorder"


class EndpointCheck(Protocol):
    def __call__(self, *, host: str, port: int, unit_id: int) -> bool: ...


class GuardSource(Protocol):
    def __call__(self, *, host: str, port: int) -> EndpointGuard: ...


class SessionFactory(Protocol):
    def __call__(
        self, *, host: str, port: int, unit_id: int
    ) -> AbstractAsyncContextManager[ModbusTcpClient | None]: ...


class EntityIdCheck(Protocol):
    def __call__(self, *, entity_id: str) -> bool: ...


class StatisticsLookup(Protocol):
    def __call__(
        self, *, entity_ids: Collection[str]
    ) -> Awaitable[Collection[str]]: ...


@dataclass(frozen=True)
class PrefixContext:
    other_prefixes: frozenset[str]
    catalogue_keys: frozenset[str]
    saved_prefix: str | None = None


@dataclass(frozen=True)
class PrefixCheck:
    prefix: str
    error: str | None = None


@dataclass(frozen=True)
class Submission:
    host: str
    port: int
    unit_id: int
    scan_interval: int
    model: str
    prefix: str
    allow_control: bool = False
    ems_heartbeat: int | None = None

    @property
    def entry_data(self) -> dict[str, Any]:
        return {
            CONF_HOST: self.host,
            CONF_PORT: self.port,
            CONF_UNIT_ID: self.unit_id,
            CONF_MODEL: self.model,
        }

    @property
    def entry_options(self) -> dict[str, Any]:
        options: dict[str, Any] = {
            CONF_SCAN_INTERVAL: self.scan_interval,
            CONF_PREFIX: self.prefix,
            CONF_ALLOW_CONTROL: self.allow_control,
        }
        if self.ems_heartbeat is not None:
            options[CONF_EMS_HEARTBEAT] = self.ems_heartbeat
        return options

    @property
    def form_values(self) -> dict[str, Any]:
        return {**self.entry_data, **self.entry_options}


@dataclass
class PendingChange:
    submission: Submission
    device: Device
    model_confirmed: bool = False
    replacement_confirmed: bool = False
    prefix_confirmed: bool = False
    load_confirmed: bool = False
    control_confirmed: bool = False

    @property
    def entry_data(self) -> dict[str, Any]:
        return {
            **self.submission.entry_data,
            CONF_DEVICE_TYPE: self.device.device_type,
        }


@dataclass(frozen=True)
class Validation:
    change: PendingChange | None = None
    errors: dict[str, str] = field(default_factory=dict)
    placeholders: dict[str, str] = field(default_factory=dict)

    @property
    def feedback(self) -> dict[str, Any]:
        return {
            "errors": self.errors,
            "description_placeholders": self.placeholders,
        }


class SajLocalConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1
    _pending: PendingChange | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        validation = await validate_submission(
            user_input=user_input,
            endpoint_taken=self._endpoint_exists,
            validation_session=_unguarded_session,
            guard_for=self._guard_for,
            prefix_context=self._prefix_context(),
        )
        if validation.change is not None:
            conflict = await self._prefix_conflict(change=validation.change)
            if conflict is None:
                self._pending = validation.change
                return await self._async_advance(change=validation.change)
            validation = conflict
        return self._show_user_form(defaults=user_input, validation=validation)

    async def async_step_confirm_model(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        change = self._pending
        if change is None:
            return self.async_abort(reason=ABORT_NOT_PENDING)
        if user_input is None:
            return self._show_model_confirmation(change=change)
        submission = change.submission
        if self._endpoint_exists(
            host=submission.host, port=submission.port, unit_id=submission.unit_id
        ):
            return self.async_abort(reason=ABORT_ALREADY_CONFIGURED)
        conflict = await self._prefix_conflict(change=change)
        if conflict is not None:
            return self._show_user_form(
                defaults=submission.form_values, validation=conflict
            )
        change.model_confirmed = True
        return await self._async_advance(change=change)

    async def async_step_confirm_control(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        change = self._pending
        if change is None:
            return self.async_abort(reason=ABORT_NOT_PENDING)
        if user_input is None:
            return self._show_control_confirmation(change=change)
        errors: dict[str, str] = {}
        if offers_ems_device(device=change.device):
            heartbeat = _normalized_heartbeat(user_input=user_input)
            if heartbeat is None:
                errors[CONF_EMS_HEARTBEAT] = ERROR_INVALID_EMS_HEARTBEAT
                return self._show_control_confirmation(
                    change=change, submitted=user_input, errors=errors
                )
            change.submission = replace(change.submission, ems_heartbeat=heartbeat)
        change.control_confirmed = True
        return await self._async_advance(change=change)

    async def _async_advance(self, *, change: PendingChange) -> ConfigFlowResult:
        if not change.device.detected and not change.model_confirmed:
            return self._show_model_confirmation(change=change)
        if change.submission.allow_control and not change.control_confirmed:
            return self._show_control_confirmation(change=change)
        return await self._async_create_entry(change=change)

    def _show_control_confirmation(
        self,
        *,
        change: PendingChange,
        submitted: Mapping[str, Any] | None = None,
        errors: dict[str, str] | None = None,
    ) -> ConfigFlowResult:
        return self.async_show_form(
            step_id=STEP_CONFIRM_CONTROL,
            data_schema=_control_confirmation_schema(
                ems=offers_ems_device(device=change.device), submitted=submitted
            ),
            errors=errors or {},
            description_placeholders={},
        )

    def _show_user_form(
        self, *, defaults: dict[str, Any] | None, validation: Validation
    ) -> ConfigFlowResult:
        return self.async_show_form(
            step_id="user",
            data_schema=_endpoint_schema(defaults=defaults, control=True),
            **validation.feedback,
        )

    def _prefix_context(self) -> PrefixContext:
        return prefix_context(entries=self.hass.config_entries.async_entries(DOMAIN))

    async def _prefix_conflict(self, *, change: PendingChange) -> Validation | None:
        return await find_prefix_conflict(
            hass=self.hass,
            context=self._prefix_context(),
            prefix=change.submission.prefix,
            domains=_device_domains(device=change.device),
            check_statistics=False,
        )

    def _show_model_confirmation(self, *, change: PendingChange) -> ConfigFlowResult:
        return self.async_show_form(**_model_confirmation_form(device=change.device))

    async def _async_create_entry(self, *, change: PendingChange) -> ConfigFlowResult:
        submission = change.submission
        await self.async_set_unique_id(change.device.serial)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
            title=f"SAJ {change.device.serial}",
            data=change.entry_data,
            options=submission.entry_options,
        )

    def _guard_for(self, *, host: str, port: int) -> EndpointGuard:
        return endpoint_guard(hass=self.hass, host=host, port=port)

    def _endpoint_exists(self, *, host: str, port: int, unit_id: int) -> bool:
        return any(
            _entry_owns_endpoint(entry=entry, host=host, port=port, unit_id=unit_id)
            for entry in self.hass.config_entries.async_entries(DOMAIN)
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        del config_entry
        return SajOptionsFlow()

    @classmethod
    @callback
    def async_get_supported_subentry_types(
        cls, config_entry: ConfigEntry
    ) -> dict[str, type[ConfigSubentryFlow]]:
        del config_entry
        return {SUBENTRY_POLLING_GROUP: SajPollingGroupFlow}


class SajOptionsFlow(OptionsFlow):
    _pending: PendingChange | None = None

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        validation = await validate_submission(
            user_input=user_input,
            endpoint_taken=self._endpoint_exists_for_other,
            validation_session=self._validation_session,
            guard_for=self._guard_for,
            prefix_context=self._prefix_context(),
        )
        change = validation.change
        if change is not None:
            if self._serial_exists_for_other(serial=change.device.serial):
                validation = Validation(errors={"base": ABORT_ALREADY_CONFIGURED})
            else:
                conflict = await self._prefix_conflict(change=change)
                if conflict is None:
                    self._pending = change
                    return await self._async_advance(change=change)
                validation = conflict
        return self.async_show_form(
            step_id="init",
            data_schema=_options_schema(
                entry=self.config_entry,
                submitted=user_input,
                ems=offers_ems(entry=self.config_entry),
            ),
            errors=validation.errors,
            description_placeholders={
                **load_placeholders(
                    installation=stored_installation_load(
                        hass=self.hass, entry=self.config_entry
                    )
                ),
                **validation.placeholders,
            },
        )

    async def async_step_confirm_model(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        return await self._async_confirm(
            submitted=user_input is not None, confirm=_confirm_model
        )

    async def async_step_confirm_replacement(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        return await self._async_confirm(
            submitted=user_input is not None, confirm=_confirm_replacement
        )

    async def async_step_confirm_prefix(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        return await self._async_confirm(
            submitted=user_input is not None, confirm=_confirm_prefix
        )

    async def async_step_confirm_load(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        return await self._async_confirm(
            submitted=user_input is not None, confirm=_confirm_load
        )

    async def async_step_confirm_control(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        return await self._async_confirm(
            submitted=user_input is not None, confirm=_confirm_control
        )

    async def _async_confirm(
        self, *, submitted: bool, confirm: Callable[[PendingChange], None]
    ) -> ConfigFlowResult:
        pending = self._pending
        if pending is None:
            return self.async_abort(reason=ABORT_NOT_PENDING)
        if submitted:
            confirm(pending)
        return await self._async_advance(change=pending)

    async def _async_advance(self, *, change: PendingChange) -> ConfigFlowResult:
        device = change.device
        if not device.detected and not change.model_confirmed:
            return self.async_show_form(**_model_confirmation_form(device=device))
        if (
            device.serial != self.config_entry.unique_id
            and not change.replacement_confirmed
        ):
            return self.async_show_form(
                step_id=STEP_CONFIRM_REPLACEMENT,
                data_schema=vol.Schema({}),
                errors={},
                description_placeholders={
                    "model": device.profile.display_name,
                    "serial": device.serial,
                },
            )
        if self._prefix_changed(change=change) and not change.prefix_confirmed:
            return self.async_show_form(
                **_prefix_confirmation_form(
                    old_prefix=self._current_prefix,
                    new_prefix=change.submission.prefix,
                )
            )
        if not change.load_confirmed:
            load_change = self._interval_load_change(change=change)
            if load_change is not None:
                return self.async_show_form(
                    step_id=STEP_CONFIRM_LOAD,
                    data_schema=vol.Schema({}),
                    errors={},
                    description_placeholders=load_change.placeholders,
                )
        if self._control_switched_on(change=change) and not change.control_confirmed:
            return self.async_show_form(
                step_id=STEP_CONFIRM_CONTROL,
                data_schema=vol.Schema({}),
                errors={},
                description_placeholders={},
            )
        return await self._save_changes(change=change)

    def _control_switched_on(self, *, change: PendingChange) -> bool:
        return change.submission.allow_control and not self.config_entry.options.get(
            CONF_ALLOW_CONTROL, False
        )

    def _interval_load_change(self, *, change: PendingChange) -> LoadChange | None:
        entry = self.config_entry
        submitted_interval = change.submission.scan_interval
        if submitted_interval == entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        ):
            return None
        after = installation_load_of(
            hass=self.hass,
            entry=entry,
            profile=change.device.profile,
            device_type=change.device.device_type,
            default_interval=submitted_interval,
        ).per_minute
        if after <= BUDGET_PER_MINUTE:
            return None
        return LoadChange(
            before=stored_installation_load(hass=self.hass, entry=entry).per_minute,
            after=after,
        )

    @property
    def _current_prefix(self) -> str:
        return self.config_entry.options.get(CONF_PREFIX, "")

    def _prefix_changed(self, *, change: PendingChange) -> bool:
        return change.submission.prefix != self._current_prefix

    def _other_entries(self) -> list[ConfigEntry]:
        return [
            entry
            for entry in self.hass.config_entries.async_entries(DOMAIN)
            if entry.entry_id != self.config_entry.entry_id
        ]

    def _prefix_context(self) -> PrefixContext:
        return prefix_context(
            entries=self._other_entries(), saved_prefix=self._current_prefix
        )

    async def _prefix_conflict(self, *, change: PendingChange) -> Validation | None:
        if not self._prefix_changed(change=change):
            return None
        registered = installation_entities(
            hass=self.hass, entry_id=self.config_entry.entry_id
        )
        domains = {
            **_device_domains(device=change.device),
            **{key: entity.domain for key, entity in registered.items()},
        }
        return await find_prefix_conflict(
            hass=self.hass,
            context=self._prefix_context(),
            prefix=change.submission.prefix,
            domains=domains,
            check_statistics=True,
        )

    def _rename_entities(self, *, new_prefix: str) -> None:
        registry = er.async_get(self.hass)
        renames: dict[str, str] = {}
        for key, registered in installation_entities(
            hass=self.hass, entry_id=self.config_entry.entry_id
        ).items():
            if registered.entity_id == fixed_entity_id(
                domain=registered.domain, prefix=self._current_prefix, key=key
            ):
                renames[registered.entity_id] = fixed_entity_id(
                    domain=registered.domain, prefix=new_prefix, key=key
                )
        for entity_id, new_entity_id in renames.items():
            registry.async_update_entity(entity_id, new_entity_id=new_entity_id)

    def _guard_for(self, *, host: str, port: int) -> EndpointGuard:
        return endpoint_guard(hass=self.hass, host=host, port=port)

    def _validation_session(
        self, *, host: str, port: int, unit_id: int
    ) -> AbstractAsyncContextManager[ModbusTcpClient | None]:
        entry = self.config_entry
        if not _entry_owns_endpoint(entry=entry, host=host, port=port, unit_id=unit_id):
            return nullcontext(None)
        runtime_data = getattr(entry, "runtime_data", None)
        coordinator = getattr(runtime_data, "coordinator", None)
        if coordinator is None:
            return nullcontext(None)
        return coordinator.async_validation_session()

    def _endpoint_exists_for_other(self, *, host: str, port: int, unit_id: int) -> bool:
        return any(
            entry.entry_id != self.config_entry.entry_id
            and _entry_owns_endpoint(entry=entry, host=host, port=port, unit_id=unit_id)
            for entry in self.hass.config_entries.async_entries(DOMAIN)
        )

    def _serial_exists_for_other(self, *, serial: str) -> bool:
        return any(
            entry.entry_id != self.config_entry.entry_id and entry.unique_id == serial
            for entry in self.hass.config_entries.async_entries(DOMAIN)
        )

    async def _save_changes(self, *, change: PendingChange) -> ConfigFlowResult:
        submission = change.submission
        if self._endpoint_exists_for_other(
            host=submission.host, port=submission.port, unit_id=submission.unit_id
        ) or self._serial_exists_for_other(serial=change.device.serial):
            return self.async_abort(reason=ABORT_ALREADY_CONFIGURED)
        if await self._prefix_conflict(change=change) is not None:
            return self.async_abort(reason=ABORT_PREFIX_UNAVAILABLE)
        if self._prefix_changed(change=change):
            self._rename_entities(new_prefix=submission.prefix)
        self.hass.config_entries.async_update_entry(
            self.config_entry,
            data=change.entry_data,
            options=submission.entry_options,
            unique_id=change.device.serial,
        )
        return self.async_abort(reason="changes_saved")


@dataclass(frozen=True)
class PollingGroup:
    name: str
    interval: int
    sensors: tuple[str, ...]

    @property
    def data(self) -> dict[str, Any]:
        return {CONF_SCAN_INTERVAL: self.interval, CONF_SENSORS: list(self.sensors)}


@dataclass(frozen=True)
class InstallationLoad:
    profile: Profile
    device_type: int
    enabled: frozenset[str]
    default_interval: int
    groups: tuple[Cadence, ...]

    @property
    def per_minute(self) -> float:
        return installation_load(
            profile=self.profile,
            device_type=self.device_type,
            enabled=self.enabled,
            default_interval=self.default_interval,
            groups=self.groups,
        )

    def requests_per_read(self, *, keys: Collection[str]) -> int:
        return requests_per_read(
            profile=self.profile,
            device_type=self.device_type,
            keys=self.enabled & frozenset(keys),
        )


@dataclass(frozen=True)
class LoadChange:
    before: float
    after: float

    @property
    def over_budget(self) -> bool:
        return self.after > BUDGET_PER_MINUTE

    @property
    def placeholders(self) -> dict[str, str]:
        return {
            "before": format_load(load=self.before),
            "after": format_load(load=self.after),
            "budget": format_load(load=BUDGET_PER_MINUTE),
        }


def format_load(*, load: float) -> str:
    return f"{round(load, LOAD_DECIMALS):g}"


def load_placeholders(*, installation: InstallationLoad) -> dict[str, str]:
    return {
        "load": format_load(load=installation.per_minute),
        "budget": format_load(load=BUDGET_PER_MINUTE),
    }


def installation_load_of(
    *,
    hass: HomeAssistant,
    entry: ConfigEntry,
    profile: Profile,
    device_type: int,
    default_interval: int,
) -> InstallationLoad:
    return InstallationLoad(
        profile=profile,
        device_type=device_type,
        enabled=enabled_entity_keys(
            hass=hass,
            entry_id=entry.entry_id,
            registers=device_read_registers(profile=profile, device_type=device_type),
        ),
        default_interval=default_interval,
        groups=tuple(group_cadences(entry=entry)),
    )


def stored_installation_load(
    *, hass: HomeAssistant, entry: ConfigEntry
) -> InstallationLoad:
    profile, device_type = _stored_profile(entry=entry)
    return installation_load_of(
        hass=hass,
        entry=entry,
        profile=profile,
        device_type=device_type,
        default_interval=entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
    )


@dataclass(frozen=True)
class PendingGroup:
    group: PollingGroup
    submitted: dict[str, Any]
    subentry: ConfigSubentry | None


@dataclass(frozen=True)
class GroupContext:
    entry: ConfigEntry
    installation: InstallationLoad
    labels: dict[str, str]
    claimed: frozenset[str]


class SajPollingGroupFlow(ConfigSubentryFlow):
    _pending: PendingGroup | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        return await self._group_step(user_input=user_input, subentry=None)

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        return await self._group_step(
            user_input=user_input, subentry=self._get_reconfigure_subentry()
        )

    async def async_step_review_group(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        del user_input
        return await self._review()

    async def async_step_review_group_over_budget(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        del user_input
        return await self._review()

    async def async_step_save_group(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        del user_input
        pending = self._pending
        if pending is None:
            return self.async_abort(reason=ABORT_NOT_PENDING)
        group = pending.group
        if pending.subentry is None:
            return self.async_create_entry(title=group.name, data=group.data)
        return self.async_update_and_abort(
            self._get_entry(), pending.subentry, title=group.name, data=group.data
        )

    async def async_step_change_selection(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        del user_input
        pending = self._pending
        if pending is None:
            return self.async_abort(reason=ABORT_NOT_PENDING)
        context = await self._context(subentry=pending.subentry)
        return self._show_group_form(
            context=context,
            subentry=pending.subentry,
            submitted=pending.submitted,
            errors={},
        )

    async def _context(self, *, subentry: ConfigSubentry | None) -> GroupContext:
        entry = self._get_entry()
        installation = stored_installation_load(hass=self.hass, entry=entry)
        return GroupContext(
            entry=entry,
            installation=installation,
            labels=await _entity_labels(
                hass=self.hass, entry=entry, installation=installation
            ),
            claimed=_claimed_keys(
                entry=entry,
                excluding=None if subentry is None else subentry.subentry_id,
            ),
        )

    async def _group_step(
        self, *, user_input: dict[str, Any] | None, subentry: ConfigSubentry | None
    ) -> SubentryFlowResult:
        context = await self._context(subentry=subentry)
        selectable = _selectable(context=context)
        if not context.labels:
            return self.async_abort(reason=ABORT_NO_SENSORS)
        if subentry is None and not selectable:
            return self.async_abort(reason=ABORT_ALL_SENSORS_ASSIGNED)
        errors: dict[str, str] = {}
        if user_input is not None:
            group, errors = validate_group(
                user_input=user_input, claimed=context.claimed
            )
            if group is not None:
                self._pending = PendingGroup(
                    group=group, submitted=dict(user_input), subentry=subentry
                )
                return await self._review()
        return self._show_group_form(
            context=context, subentry=subentry, submitted=user_input, errors=errors
        )

    def _show_group_form(
        self,
        *,
        context: GroupContext,
        subentry: ConfigSubentry | None,
        submitted: Mapping[str, Any] | None,
        errors: dict[str, str],
    ) -> SubentryFlowResult:
        selectable = _selectable(context=context)
        return self.async_show_form(
            step_id="user" if subentry is None else "reconfigure",
            data_schema=_group_schema(
                options=selectable,
                defaults=_group_defaults(
                    subentry=subentry, submitted=submitted, selectable=selectable
                ),
            ),
            description_placeholders=load_placeholders(
                installation=context.installation
            ),
            errors=errors,
        )

    async def _review(self) -> SubentryFlowResult:
        pending = self._pending
        if pending is None:
            return self.async_abort(reason=ABORT_NOT_PENDING)
        context = await self._context(subentry=pending.subentry)
        keys = frozenset(pending.group.sensors)
        saved = Cadence(interval=pending.group.interval, keys=keys)
        excluding = None if pending.subentry is None else pending.subentry.subentry_id
        installation = context.installation
        change = LoadChange(
            before=installation.per_minute,
            after=replace(
                installation,
                groups=(
                    *group_cadences(entry=context.entry, excluding=excluding),
                    saved,
                ),
            ).per_minute,
        )
        return self.async_show_menu(
            step_id=STEP_REVIEW_GROUP_OVER_BUDGET
            if change.over_budget
            else STEP_REVIEW_GROUP,
            menu_options=[STEP_SAVE_GROUP, STEP_CHANGE_SELECTION],
            description_placeholders={
                **change.placeholders,
                "requests": str(installation.requests_per_read(keys=keys)),
            },
        )


def validate_group(
    *, user_input: Mapping[str, Any], claimed: Collection[str]
) -> tuple[PollingGroup | None, dict[str, str]]:
    errors: dict[str, str] = {}
    interval = _normalized_interval(user_input=user_input)
    if interval is None:
        errors[CONF_SCAN_INTERVAL] = "invalid_scan_interval"
    sensors = tuple(user_input.get(CONF_SENSORS, ()))
    if not sensors:
        errors[CONF_SENSORS] = ERROR_NO_SENSORS_SELECTED
    elif not set(claimed).isdisjoint(sensors):
        errors[CONF_SENSORS] = ERROR_SENSOR_IN_OTHER_GROUP
    if interval is None or errors:
        return None, errors
    return (
        PollingGroup(name=user_input[CONF_NAME], interval=interval, sensors=sensors),
        errors,
    )


async def _selector_options(
    *, hass: HomeAssistant, selector_name: str
) -> dict[str, str]:
    translations = await async_get_translations(
        hass, hass.config.language, "selector", [DOMAIN]
    )
    prefix = f"component.{DOMAIN}.selector.{selector_name}.options."
    return {
        name.removeprefix(prefix): label
        for name, label in translations.items()
        if name.startswith(prefix)
    }


async def _entity_labels(
    *, hass: HomeAssistant, entry: ConfigEntry, installation: InstallationLoad
) -> dict[str, str]:
    blocks = blocks_by_key(
        profile=installation.profile, device_type=installation.device_type
    )
    block_labels = await _selector_options(hass=hass, selector_name=BLOCK_SELECTOR)
    disabled_label = (
        await _selector_options(hass=hass, selector_name=ENTITY_STATE_SELECTOR)
    )[DISABLED_STATE]
    entities = installation_entities(hass=hass, entry_id=entry.entry_id)
    return {
        key: _option_label(
            block=block_labels.get(block, block),
            entity=entity,
            key=key,
            disabled_label=disabled_label,
        )
        for key, block in blocks.items()
        if (entity := entities.get(key)) is not None
    }


def _option_label(
    *, block: str, entity: er.RegistryEntry, key: str, disabled_label: str
) -> str:
    name = f"{block}: {entity.name or entity.original_name or key}"
    if entity.disabled_by is None:
        return name
    return disabled_label.format(entity=name)


def _selectable(*, context: GroupContext) -> dict[str, str]:
    return {
        key: label
        for key, label in context.labels.items()
        if key not in context.claimed
    }


def _claimed_keys(*, entry: ConfigEntry, excluding: str | None) -> frozenset[str]:
    return frozenset(
        key
        for cadence in group_cadences(entry=entry, excluding=excluding)
        for key in cadence.keys
    )


def _group_defaults(
    *,
    subentry: ConfigSubentry | None,
    submitted: Mapping[str, Any] | None,
    selectable: Mapping[str, str],
) -> dict[str, Any]:
    if submitted is not None:
        return dict(submitted)
    if subentry is None:
        return {CONF_SCAN_INTERVAL: MIN_INTERVAL}
    return {
        CONF_NAME: subentry.title,
        CONF_SCAN_INTERVAL: subentry.data[CONF_SCAN_INTERVAL],
        CONF_SENSORS: [key for key in subentry.data[CONF_SENSORS] if key in selectable],
    }


def _group_schema(
    *, options: Mapping[str, str], defaults: Mapping[str, Any]
) -> vol.Schema:
    name_marker = (
        vol.Required(CONF_NAME, default=defaults[CONF_NAME])
        if CONF_NAME in defaults
        else vol.Required(CONF_NAME)
    )
    return vol.Schema(
        {
            name_marker: vol.All(str, vol.Strip, vol.Length(min=1)),
            vol.Required(
                CONF_SCAN_INTERVAL,
                default=defaults.get(CONF_SCAN_INTERVAL, MIN_INTERVAL),
            ): _number_box(),
            vol.Required(
                CONF_SENSORS, default=defaults.get(CONF_SENSORS, [])
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        selector.SelectOptionDict(value=key, label=label)
                        for key, label in options.items()
                    ],
                    multiple=True,
                    mode=selector.SelectSelectorMode.LIST,
                )
            ),
        }
    )


async def validate_submission(
    *,
    user_input: dict[str, Any] | None,
    endpoint_taken: EndpointCheck,
    validation_session: SessionFactory,
    guard_for: GuardSource,
    prefix_context: PrefixContext,
) -> Validation:
    if user_input is None:
        return Validation()
    errors: dict[str, str] = {}
    endpoint = _normalized_endpoint(user_input=user_input, errors=errors)
    interval = _normalized_interval(user_input=user_input)
    if interval is None:
        errors[CONF_SCAN_INTERVAL] = "invalid_scan_interval"
    heartbeat = _normalized_heartbeat(user_input=user_input)
    if heartbeat is None and CONF_EMS_HEARTBEAT in user_input:
        errors[CONF_EMS_HEARTBEAT] = ERROR_INVALID_EMS_HEARTBEAT
    checked_prefix = _checked_prefix(
        value=user_input.get(CONF_PREFIX, ""), context=prefix_context
    )
    if checked_prefix.error is not None:
        errors[CONF_PREFIX] = checked_prefix.error
    if endpoint is None or interval is None or errors:
        return Validation(errors=errors)
    host, port, unit_id = endpoint
    submission = Submission(
        host=host,
        port=port,
        unit_id=unit_id,
        scan_interval=interval,
        model=user_input[CONF_MODEL],
        prefix=checked_prefix.prefix,
        allow_control=bool(user_input.get(CONF_ALLOW_CONTROL, False)),
        ems_heartbeat=heartbeat,
    )
    if endpoint_taken(host=host, port=port, unit_id=unit_id):
        return Validation(errors={"base": ABORT_ALREADY_CONFIGURED})
    async with validation_session(host=host, port=port, unit_id=unit_id) as shared:
        probe = await _probe_device(
            submission=submission,
            shared_client=shared,
            guard=guard_for(host=host, port=port),
        )
    if probe.change is None:
        return probe
    if endpoint_taken(host=host, port=port, unit_id=unit_id):
        return Validation(errors={"base": ABORT_ALREADY_CONFIGURED})
    return probe


async def _probe_device(
    *,
    submission: Submission,
    shared_client: ModbusTcpClient | None,
    guard: EndpointGuard,
) -> Validation:
    if shared_client is not None:
        validation = await _probe_with(client=shared_client, submission=submission)
    else:
        client = ModbusTcpClient(
            host=submission.host,
            port=submission.port,
            unit_id=submission.unit_id,
            timeout=REQUEST_TIMEOUT,
            environment=ClientEnvironment(budget=guard.budget),
        )
        try:
            validation = await _probe_with(client=client, submission=submission)
        finally:
            await client.close()
    if validation.change is not None:
        guard.succeeded()
    return validation


async def _probe_with(*, client: ModbusTcpClient, submission: Submission) -> Validation:
    try:
        device = await identify(client=client, selection=submission.model)
        readout = await read_telemetry(
            client=client, device=device, enabled=setup_keys(device)
        )
        readout.require_complete()
    except HANDLED_ERRORS as err:
        translation = translate_error(error=err)
        field_name = CONF_MODEL if translation.concerns_model else "base"
        return Validation(
            errors={field_name: translation.key},
            placeholders=translation.placeholders,
        )
    return Validation(change=PendingChange(submission=submission, device=device))


def _confirm_model(change: PendingChange) -> None:
    change.model_confirmed = True


def _confirm_replacement(change: PendingChange) -> None:
    change.replacement_confirmed = True


def _confirm_prefix(change: PendingChange) -> None:
    change.prefix_confirmed = True


def _confirm_load(change: PendingChange) -> None:
    change.load_confirmed = True


def _confirm_control(change: PendingChange) -> None:
    change.control_confirmed = True


def prefix_context(
    *, entries: Iterable[ConfigEntry], saved_prefix: str | None = None
) -> PrefixContext:
    return PrefixContext(
        saved_prefix=saved_prefix,
        other_prefixes=frozenset(
            entry.options.get(CONF_PREFIX, "") for entry in entries
        ),
        catalogue_keys=known_keys(profiles=PROFILES),
    )


def _checked_prefix(*, value: object, context: PrefixContext) -> PrefixCheck:
    if (
        context.saved_prefix is not None
        and isinstance(value, str)
        and value.strip().lower() == context.saved_prefix
    ):
        return PrefixCheck(prefix=context.saved_prefix)
    return validate_prefix(
        value=value,
        other_prefixes=context.other_prefixes,
        catalogue_keys=context.catalogue_keys,
    )


def validate_prefix(
    *, value: object, other_prefixes: Collection[str], catalogue_keys: Collection[str]
) -> PrefixCheck:
    if not isinstance(value, str):
        return PrefixCheck(prefix="", error=ERROR_INVALID_PREFIX)
    prefix = value.strip().lower()
    if prefix and (
        len(prefix) > MAX_PREFIX_LENGTH or PREFIX_SHAPE.fullmatch(prefix) is None
    ):
        return PrefixCheck(prefix=prefix, error=ERROR_INVALID_PREFIX)
    if prefix and any(key.startswith(f"{prefix}_") for key in catalogue_keys):
        return PrefixCheck(prefix=prefix, error=ERROR_PREFIX_SHADOWS_ENTITY)
    if prefix in other_prefixes:
        return PrefixCheck(prefix=prefix, error=ERROR_PREFIX_IN_USE)
    return PrefixCheck(prefix=prefix)


def first_taken_entity_id(
    *, entity_ids: Iterable[str], is_taken: EntityIdCheck
) -> str | None:
    return next(
        (
            entity_id
            for entity_id in sorted(entity_ids)
            if is_taken(entity_id=entity_id)
        ),
        None,
    )


async def first_entity_id_with_statistics(
    *, entity_ids: Iterable[str], recorded_among: StatisticsLookup
) -> str | None:
    candidates = sorted(entity_ids)
    recorded = await recorded_among(entity_ids=candidates)
    return next((entity_id for entity_id in candidates if entity_id in recorded), None)


async def find_prefix_conflict(
    *,
    hass: HomeAssistant,
    context: PrefixContext,
    prefix: str,
    domains: Mapping[str, str],
    check_statistics: bool,
) -> Validation | None:
    checked = validate_prefix(
        value=prefix,
        other_prefixes=context.other_prefixes,
        catalogue_keys=context.catalogue_keys,
    )
    if checked.error is not None:
        return Validation(errors={CONF_PREFIX: checked.error})
    entity_ids = [
        fixed_entity_id(domain=domain, prefix=prefix, key=key)
        for key, domain in domains.items()
    ]
    taken = first_taken_entity_id(
        entity_ids=entity_ids, is_taken=partial(entity_id_in_use, hass=hass)
    )
    if taken is not None:
        return _entity_id_conflict(error=ERROR_ENTITY_ID_TAKEN, entity_id=taken)
    if not check_statistics or RECORDER_COMPONENT not in hass.config.components:
        return None
    recorded = await first_entity_id_with_statistics(
        entity_ids=entity_ids,
        recorded_among=partial(_recorded_statistic_ids, hass=hass),
    )
    if recorded is None:
        return None
    return _entity_id_conflict(error=ERROR_STATISTICS_EXIST, entity_id=recorded)


def _entity_id_conflict(*, error: str, entity_id: str) -> Validation:
    return Validation(
        errors={CONF_PREFIX: error}, placeholders={"entity_id": entity_id}
    )


async def _recorded_statistic_ids(
    *, hass: HomeAssistant, entity_ids: Collection[str]
) -> frozenset[str]:
    listed = await async_list_statistic_ids(hass, set(entity_ids))
    return frozenset(
        item["statistic_id"]
        for item in listed
        if item["source"] == RECORDER_STATISTICS_SOURCE
    )


def _unguarded_session(
    *, host: str, port: int, unit_id: int
) -> AbstractAsyncContextManager[ModbusTcpClient | None]:
    del host, port, unit_id
    return nullcontext(None)


def _model_confirmation_form(*, device: Device) -> dict[str, Any]:
    return {
        "step_id": STEP_CONFIRM_MODEL,
        "data_schema": vol.Schema({}),
        "errors": {},
        "description_placeholders": {
            "model": device.profile.display_name,
            "device_type": format_device_type(device.device_type),
        },
    }


def _prefix_confirmation_form(*, old_prefix: str, new_prefix: str) -> dict[str, Any]:
    return {
        "step_id": STEP_CONFIRM_PREFIX,
        "data_schema": vol.Schema({}),
        "errors": {},
        "description_placeholders": {
            "old_pattern": fixed_entity_id(
                domain=DOMAIN_PLACEHOLDER, prefix=old_prefix, key=KEY_PLACEHOLDER
            ),
            "new_pattern": fixed_entity_id(
                domain=DOMAIN_PLACEHOLDER, prefix=new_prefix, key=KEY_PLACEHOLDER
            ),
        },
    }


def _device_domains(*, device: Device) -> dict[str, str]:
    return {
        register.key: register.kind.value
        for register in device_registers(
            profile=device.profile, device_type=device.device_type
        )
    }


def _endpoint_schema(
    *,
    defaults: dict[str, Any] | None = None,
    control: bool = False,
    ems: bool = False,
) -> vol.Schema:
    values = defaults or {}
    host_marker = (
        vol.Required(CONF_HOST, default=values[CONF_HOST])
        if CONF_HOST in values
        else vol.Required(CONF_HOST)
    )
    schema: dict[vol.Marker, Any] = {
        host_marker: str,
        vol.Required(
            CONF_PORT, default=values.get(CONF_PORT, DEFAULT_PORT)
        ): _number_box(),
        vol.Required(
            CONF_UNIT_ID, default=values.get(CONF_UNIT_ID, DEFAULT_UNIT_ID)
        ): _number_box(),
        vol.Required(
            CONF_SCAN_INTERVAL,
            default=values.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        ): _number_box(),
        vol.Required(CONF_MODEL, default=values.get(CONF_MODEL, AUTOMATIC)): (
            _model_selector()
        ),
        vol.Optional(
            CONF_PREFIX, description={"suggested_value": values.get(CONF_PREFIX, "")}
        ): str,
    }
    if control:
        schema[
            vol.Required(
                CONF_ALLOW_CONTROL, default=values.get(CONF_ALLOW_CONTROL, False)
            )
        ] = selector.BooleanSelector()
    if ems:
        schema.update(_heartbeat_field(values=values))
    return vol.Schema(schema)


def _heartbeat_field(*, values: Mapping[str, Any]) -> dict[vol.Marker, Any]:
    return {
        vol.Required(
            CONF_EMS_HEARTBEAT,
            default=values.get(CONF_EMS_HEARTBEAT, DEFAULT_HEARTBEAT_INTERVAL),
        ): _number_box()
    }


def _control_confirmation_schema(
    *, ems: bool, submitted: Mapping[str, Any] | None
) -> vol.Schema:
    if not ems:
        return vol.Schema({})
    return vol.Schema(_heartbeat_field(values=submitted or {}))


def _options_schema(
    *, entry: ConfigEntry, submitted: dict[str, Any] | None, ems: bool
) -> vol.Schema:
    if submitted is not None:
        return _endpoint_schema(defaults=submitted, control=True, ems=ems)
    defaults = {
        **entry.data,
        CONF_SCAN_INTERVAL: entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        ),
        CONF_PREFIX: entry.options.get(CONF_PREFIX, ""),
        CONF_ALLOW_CONTROL: entry.options.get(CONF_ALLOW_CONTROL, False),
        CONF_EMS_HEARTBEAT: entry.options.get(
            CONF_EMS_HEARTBEAT, DEFAULT_HEARTBEAT_INTERVAL
        ),
    }
    return _endpoint_schema(defaults=defaults, control=True, ems=ems)


def _model_selector() -> selector.SelectSelector:
    return selector.SelectSelector(
        selector.SelectSelectorConfig(
            options=[AUTOMATIC, *(profile.key for profile in PROFILES)],
            mode=selector.SelectSelectorMode.DROPDOWN,
            translation_key=MODEL_TRANSLATION_KEY,
        )
    )


def _number_box() -> Any:
    return selector.NumberSelector(
        selector.NumberSelectorConfig(step="any", mode=selector.NumberSelectorMode.BOX)
    )


def _normalized_endpoint(
    *, user_input: dict[str, Any], errors: dict[str, str]
) -> tuple[str, int, int] | None:
    host = user_input.get(CONF_HOST)
    if not isinstance(host, str) or not host.strip():
        errors["base"] = "invalid_host"
        return None
    try:
        port_value = user_input[CONF_PORT]
        unit_id_value = user_input[CONF_UNIT_ID]
        port = int(port_value)
        unit_id = int(unit_id_value)
    except KeyError, TypeError, ValueError, OverflowError:
        errors["base"] = "invalid_endpoint"
        return None
    if port_value != port or not 1 <= port <= MAX_PORT:
        errors[CONF_PORT] = "invalid_port"
        return None
    if unit_id_value != unit_id or not MIN_UNIT_ID <= unit_id <= MAX_UNIT_ID:
        errors[CONF_UNIT_ID] = "invalid_unit_id"
        return None
    return host.strip(), port, unit_id


def _normalized_interval(*, user_input: Mapping[str, Any]) -> int | None:
    try:
        interval_value = user_input[CONF_SCAN_INTERVAL]
        interval = int(interval_value)
    except KeyError, TypeError, ValueError, OverflowError:
        return None
    if interval_value != interval or interval < MIN_INTERVAL:
        return None
    return interval


def _normalized_heartbeat(*, user_input: Mapping[str, Any]) -> int | None:
    try:
        heartbeat_value = user_input[CONF_EMS_HEARTBEAT]
        heartbeat = int(heartbeat_value)
    except KeyError, TypeError, ValueError, OverflowError:
        return None
    if heartbeat_value != heartbeat or not valid_heartbeat_interval(seconds=heartbeat):
        return None
    return heartbeat


def offers_ems(*, entry: ConfigEntry) -> bool:
    profile, device_type = _stored_profile(entry=entry)
    return _has_ems_rows(profile=profile, device_type=device_type)


def offers_ems_device(*, device: Device) -> bool:
    return _has_ems_rows(profile=device.profile, device_type=device.device_type)


def _has_ems_rows(*, profile: Profile, device_type: int) -> bool:
    return any(
        register.key in FUNCTION_BY_ENABLE_KEY
        for register in device_registers(profile=profile, device_type=device_type)
    )


def _stored_profile(*, entry: ConfigEntry) -> tuple[Profile, int]:
    device_type = entry.data[CONF_DEVICE_TYPE]
    resolution = resolve_profile(
        device_type=device_type, selection=entry.data[CONF_MODEL], profiles=PROFILES
    )
    return resolution.profile, device_type


def _entry_owns_endpoint(
    *, entry: ConfigEntry, host: str, port: int, unit_id: int
) -> bool:
    return (
        entry.data.get(CONF_HOST, "").casefold() == host.casefold()
        and entry.data.get(CONF_PORT, DEFAULT_PORT) == port
        and entry.data.get(CONF_UNIT_ID, DEFAULT_UNIT_ID) == unit_id
    )
