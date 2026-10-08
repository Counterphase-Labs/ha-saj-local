from contextlib import nullcontext
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol

import voluptuous as vol
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
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

if TYPE_CHECKING:
    from collections.abc import Callable, Collection, Mapping
    from contextlib import AbstractAsyncContextManager

    from homeassistant.config_entries import ConfigEntry, ConfigSubentry
    from homeassistant.core import HomeAssistant

    from .saj.guard import EndpointGuard

from .const import (
    CONF_MODEL,
    CONF_SCAN_INTERVAL,
    CONF_SENSORS,
    CONF_UNIT_ID,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_UNIT_ID,
    DOMAIN,
    MAX_PORT,
    MAX_UNIT_ID,
    MIN_UNIT_ID,
    REQUEST_TIMEOUT,
    SUBENTRY_POLLING_GROUP,
    endpoint_guard,
    sensor_key,
)
from .errors import HANDLED_ERRORS, translate_error
from .saj.client import ClientEnvironment, ModbusTcpClient
from .saj.device import Device, identify
from .saj.device_type import format_device_type
from .saj.profiles import AUTOMATIC, PROFILES
from .saj.schedule import MIN_INTERVAL
from .saj.telemetry import read_telemetry

MODEL_TRANSLATION_KEY = "model"
STEP_CONFIRM_MODEL = "confirm_model"
STEP_CONFIRM_REPLACEMENT = "confirm_replacement"
ABORT_NOT_PENDING = "confirmation_not_pending"
ABORT_ALREADY_CONFIGURED = "already_configured"
ABORT_NO_SENSORS = "no_sensors"
ABORT_ALL_SENSORS_ASSIGNED = "all_sensors_assigned"
ERROR_NO_SENSORS_SELECTED = "no_sensors_selected"
ERROR_SENSOR_IN_OTHER_GROUP = "sensor_in_other_group"


class EndpointCheck(Protocol):
    def __call__(self, *, host: str, port: int, unit_id: int) -> bool: ...


class GuardSource(Protocol):
    def __call__(self, *, host: str, port: int) -> EndpointGuard: ...


class SessionFactory(Protocol):
    def __call__(
        self, *, host: str, port: int, unit_id: int
    ) -> AbstractAsyncContextManager[ModbusTcpClient | None]: ...


@dataclass(frozen=True)
class Submission:
    host: str
    port: int
    unit_id: int
    scan_interval: int
    model: str

    @property
    def entry_data(self) -> dict[str, Any]:
        return {
            CONF_HOST: self.host,
            CONF_PORT: self.port,
            CONF_UNIT_ID: self.unit_id,
            CONF_MODEL: self.model,
        }


@dataclass
class PendingChange:
    submission: Submission
    device: Device
    model_confirmed: bool = False
    replacement_confirmed: bool = False


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
        )
        if validation.change is not None:
            self._pending = validation.change
            if not validation.change.device.detected:
                return self._show_model_confirmation(change=validation.change)
            return await self._async_create_entry(change=validation.change)
        return self.async_show_form(
            step_id="user",
            data_schema=_endpoint_schema(defaults=user_input),
            **validation.feedback,
        )

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
        return await self._async_create_entry(change=change)

    def _show_model_confirmation(self, *, change: PendingChange) -> ConfigFlowResult:
        return self.async_show_form(**_model_confirmation_form(device=change.device))

    async def _async_create_entry(self, *, change: PendingChange) -> ConfigFlowResult:
        submission = change.submission
        await self.async_set_unique_id(change.device.serial)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
            title=f"SAJ {change.device.serial}",
            data=submission.entry_data,
            options={CONF_SCAN_INTERVAL: submission.scan_interval},
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
        )
        change = validation.change
        if change is not None:
            if self._serial_exists_for_other(serial=change.device.serial):
                validation = Validation(errors={"base": ABORT_ALREADY_CONFIGURED})
            else:
                self._pending = change
                return await self._async_advance(change=change)
        return self.async_show_form(
            step_id="init",
            data_schema=_options_schema(entry=self.config_entry, submitted=user_input),
            **validation.feedback,
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
        return self._save_changes(change=change)

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

    def _save_changes(self, *, change: PendingChange) -> ConfigFlowResult:
        submission = change.submission
        if self._endpoint_exists_for_other(
            host=submission.host, port=submission.port, unit_id=submission.unit_id
        ) or self._serial_exists_for_other(serial=change.device.serial):
            return self.async_abort(reason=ABORT_ALREADY_CONFIGURED)
        self.hass.config_entries.async_update_entry(
            self.config_entry,
            data=submission.entry_data,
            options={CONF_SCAN_INTERVAL: submission.scan_interval},
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


class SajPollingGroupFlow(ConfigSubentryFlow):
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        return self._group_step(user_input=user_input, subentry=None)

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        return self._group_step(
            user_input=user_input, subentry=self._get_reconfigure_subentry()
        )

    def _group_step(
        self, *, user_input: dict[str, Any] | None, subentry: ConfigSubentry | None
    ) -> SubentryFlowResult:
        entry = self._get_entry()
        labels = _sensor_labels(hass=self.hass, entry_id=entry.entry_id)
        claimed = _claimed_sensors(
            entry=entry, excluding=None if subentry is None else subentry.subentry_id
        )
        selectable = {key: label for key, label in labels.items() if key not in claimed}
        if not labels:
            return self.async_abort(reason=ABORT_NO_SENSORS)
        if subentry is None and not selectable:
            return self.async_abort(reason=ABORT_ALL_SENSORS_ASSIGNED)
        errors: dict[str, str] = {}
        if user_input is not None:
            group, errors = validate_group(user_input=user_input, claimed=claimed)
            if group is not None and subentry is None:
                return self.async_create_entry(title=group.name, data=group.data)
            if group is not None and subentry is not None:
                return self.async_update_and_abort(
                    entry, subentry, title=group.name, data=group.data
                )
        return self.async_show_form(
            step_id="user" if subentry is None else "reconfigure",
            data_schema=_group_schema(
                options=selectable,
                defaults=_group_defaults(
                    subentry=subentry, submitted=user_input, selectable=selectable
                ),
            ),
            errors=errors,
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


def _sensor_labels(*, hass: HomeAssistant, entry_id: str) -> dict[str, str]:
    labels: dict[str, str] = {}
    registry = er.async_get(hass)
    for registered in er.async_entries_for_config_entry(registry, entry_id):
        key = sensor_key(entry_id=entry_id, unique_id=registered.unique_id)
        if registered.domain == SENSOR_DOMAIN and key is not None:
            labels[key] = registered.name or registered.original_name or key
    return labels


def _claimed_sensors(*, entry: ConfigEntry, excluding: str | None) -> frozenset[str]:
    return frozenset(
        key
        for subentry in entry.subentries.values()
        if subentry.subentry_type == SUBENTRY_POLLING_GROUP
        and subentry.subentry_id != excluding
        for key in subentry.data[CONF_SENSORS]
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
            ): _number_box(minimum=MIN_INTERVAL),
            vol.Required(
                CONF_SENSORS, default=defaults.get(CONF_SENSORS, [])
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        selector.SelectOptionDict(value=key, label=label)
                        for key, label in sorted(
                            options.items(), key=lambda item: item[1]
                        )
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
) -> Validation:
    if user_input is None:
        return Validation()
    errors: dict[str, str] = {}
    endpoint = _normalized_endpoint(user_input=user_input, errors=errors)
    interval = _normalized_interval(user_input=user_input)
    if interval is None:
        errors["base"] = "invalid_scan_interval"
    if endpoint is None or interval is None or errors:
        return Validation(errors=errors)
    host, port, unit_id = endpoint
    submission = Submission(
        host=host,
        port=port,
        unit_id=unit_id,
        scan_interval=interval,
        model=user_input[CONF_MODEL],
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
        readout = await read_telemetry(client=client, device=device)
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


def _endpoint_schema(*, defaults: dict[str, Any] | None = None) -> vol.Schema:
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
        ): _number_box(minimum=1, maximum=MAX_PORT),
        vol.Required(
            CONF_UNIT_ID, default=values.get(CONF_UNIT_ID, DEFAULT_UNIT_ID)
        ): _number_box(minimum=MIN_UNIT_ID, maximum=MAX_UNIT_ID),
        vol.Required(
            CONF_SCAN_INTERVAL,
            default=values.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        ): _number_box(minimum=MIN_INTERVAL),
        vol.Required(CONF_MODEL, default=values.get(CONF_MODEL, AUTOMATIC)): (
            _model_selector()
        ),
    }
    return vol.Schema(schema)


def _options_schema(
    *, entry: ConfigEntry, submitted: dict[str, Any] | None
) -> vol.Schema:
    if submitted is not None:
        return _endpoint_schema(defaults=submitted)
    defaults = {
        **entry.data,
        CONF_SCAN_INTERVAL: entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        ),
    }
    return _endpoint_schema(defaults=defaults)


def _model_selector() -> selector.SelectSelector:
    return selector.SelectSelector(
        selector.SelectSelectorConfig(
            options=[AUTOMATIC, *(profile.key for profile in PROFILES)],
            mode=selector.SelectSelectorMode.DROPDOWN,
            translation_key=MODEL_TRANSLATION_KEY,
        )
    )


def _number_box(*, minimum: int, maximum: int | None = None) -> Any:
    config: selector.NumberSelectorConfig = {
        "min": float(minimum),
        "step": 1,
        "mode": selector.NumberSelectorMode.BOX,
    }
    if maximum is not None:
        config["max"] = float(maximum)
    return selector.NumberSelector(config)


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
        errors["base"] = "invalid_port"
        return None
    if unit_id_value != unit_id or not MIN_UNIT_ID <= unit_id <= MAX_UNIT_ID:
        errors["base"] = "invalid_unit_id"
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


def _entry_owns_endpoint(
    *, entry: ConfigEntry, host: str, port: int, unit_id: int
) -> bool:
    return (
        entry.data.get(CONF_HOST, "").casefold() == host.casefold()
        and entry.data.get(CONF_PORT, DEFAULT_PORT) == port
        and entry.data.get(CONF_UNIT_ID, DEFAULT_UNIT_ID) == unit_id
    )
