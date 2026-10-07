from contextlib import nullcontext
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import callback
from homeassistant.helpers import selector

if TYPE_CHECKING:
    from collections.abc import Callable
    from contextlib import AbstractAsyncContextManager

    from homeassistant.config_entries import ConfigEntry

from .const import (
    CONF_MODEL,
    CONF_SCAN_INTERVAL,
    CONF_UNIT_ID,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_UNIT_ID,
    DOMAIN,
    MAX_PORT,
    MAX_UNIT_ID,
    MIN_UNIT_ID,
    REQUEST_TIMEOUT,
)
from .errors import HANDLED_ERRORS, translate_error
from .saj.client import ModbusTcpClient
from .saj.device import Device, identify
from .saj.device_type import format_device_type
from .saj.profiles import AUTOMATIC, PROFILES
from .saj.telemetry import read_telemetry

MODEL_TRANSLATION_KEY = "model"
STEP_CONFIRM_MODEL = "confirm_model"
STEP_CONFIRM_REPLACEMENT = "confirm_replacement"
ABORT_NOT_PENDING = "confirmation_not_pending"
ABORT_ALREADY_CONFIGURED = "already_configured"


class EndpointCheck(Protocol):
    def __call__(self, *, host: str, port: int, unit_id: int) -> bool: ...


class SessionFactory(Protocol):
    def __call__(
        self, *, host: str, port: int, unit_id: int
    ) -> AbstractAsyncContextManager[None]: ...


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


class SajOptionsFlow(OptionsFlow):
    _pending: PendingChange | None = None

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        validation = await validate_submission(
            user_input=user_input,
            endpoint_taken=self._endpoint_exists_for_other,
            validation_session=self._validation_session,
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

    def _validation_session(
        self, *, host: str, port: int, unit_id: int
    ) -> AbstractAsyncContextManager[None]:
        entry = self.config_entry
        if not _entry_owns_endpoint(entry=entry, host=host, port=port, unit_id=unit_id):
            return nullcontext()
        runtime_data = getattr(entry, "runtime_data", None)
        coordinator = getattr(runtime_data, "coordinator", None)
        if coordinator is None:
            return nullcontext()
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


async def validate_submission(
    *,
    user_input: dict[str, Any] | None,
    endpoint_taken: EndpointCheck,
    validation_session: SessionFactory,
) -> Validation:
    if user_input is None:
        return Validation()
    errors: dict[str, str] = {}
    endpoint = _normalized_endpoint(user_input=user_input, errors=errors)
    interval = _normalized_interval(user_input=user_input, errors=errors)
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
    async with validation_session(host=host, port=port, unit_id=unit_id):
        probe = await _probe_device(submission=submission)
    if probe.change is None:
        return probe
    if endpoint_taken(host=host, port=port, unit_id=unit_id):
        return Validation(errors={"base": ABORT_ALREADY_CONFIGURED})
    return probe


async def _probe_device(*, submission: Submission) -> Validation:
    client = ModbusTcpClient(
        host=submission.host,
        port=submission.port,
        unit_id=submission.unit_id,
        timeout=REQUEST_TIMEOUT,
    )
    try:
        device = await identify(client=client, selection=submission.model)
        await read_telemetry(client=client, device=device)
    except HANDLED_ERRORS as err:
        translation = translate_error(error=err)
        field_name = CONF_MODEL if translation.concerns_model else "base"
        return Validation(
            errors={field_name: translation.key},
            placeholders=translation.placeholders,
        )
    else:
        return Validation(change=PendingChange(submission=submission, device=device))
    finally:
        await client.close()


def _confirm_model(change: PendingChange) -> None:
    change.model_confirmed = True


def _confirm_replacement(change: PendingChange) -> None:
    change.replacement_confirmed = True


def _unguarded_session(
    *, host: str, port: int, unit_id: int
) -> AbstractAsyncContextManager[None]:
    del host, port, unit_id
    return nullcontext()


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
        ): _number_box(minimum=DEFAULT_SCAN_INTERVAL),
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


def _normalized_interval(
    *, user_input: dict[str, Any], errors: dict[str, str]
) -> int | None:
    try:
        interval_value = user_input[CONF_SCAN_INTERVAL]
        interval = int(interval_value)
    except KeyError, TypeError, ValueError, OverflowError:
        errors["base"] = "invalid_scan_interval"
        return None
    if interval_value != interval or interval < DEFAULT_SCAN_INTERVAL:
        errors["base"] = "invalid_scan_interval"
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
