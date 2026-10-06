from typing import TYPE_CHECKING, Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import callback
from homeassistant.helpers import selector

if TYPE_CHECKING:
    from contextlib import AbstractAsyncContextManager

    from homeassistant.config_entries import ConfigEntry

from .const import (
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_UNIT_ID,
    DOMAIN,
    MAX_UNIT_ID,
    MIN_UNIT_ID,
    REQUEST_TIMEOUT,
)
from .saj.client import ModbusError, ModbusErrorMessage, ModbusTcpClient
from .saj.hs3 import Hs3Device, UnsupportedDeviceError, identify, read_telemetry

CONF_UNIT_ID = "unit_id"
CONF_SCAN_INTERVAL = "scan_interval"
MAX_PORT = 65535
_CONNECTION_FIELDS = (CONF_HOST, CONF_PORT, CONF_UNIT_ID)


class SajLocalConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            endpoint = _normalized_endpoint(user_input=user_input, errors=errors)
            interval = _normalized_interval(user_input=user_input, errors=errors)
            if endpoint is not None and interval is not None and not errors:
                host, port, unit_id = endpoint
                if self._endpoint_exists(host=host, port=port, unit_id=unit_id):
                    errors["base"] = "already_configured"
                else:
                    device = await _validate_endpoint(
                        host=host, port=port, unit_id=unit_id, errors=errors
                    )
                    if device is not None:
                        if self._endpoint_exists(host=host, port=port, unit_id=unit_id):
                            errors["base"] = "already_configured"
                        else:
                            await self.async_set_unique_id(device.serial)
                            self._abort_if_unique_id_configured()
                            return self.async_create_entry(
                                title=f"SAJ {device.serial}",
                                data={
                                    CONF_HOST: host,
                                    CONF_PORT: port,
                                    CONF_UNIT_ID: unit_id,
                                },
                                options={CONF_SCAN_INTERVAL: interval},
                            )
        return self.async_show_form(
            step_id="user", data_schema=_endpoint_schema(), errors=errors
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
    _replacement_device: Hs3Device | None = None
    _replacement_values: dict[str, Any] | None = None

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            result = await self._async_process_input(
                user_input=user_input, errors=errors
            )
            if result is not None:
                return result
        return self.async_show_form(
            step_id="init",
            data_schema=_options_schema(entry=self.config_entry),
            errors=errors,
        )

    async def _async_process_input(
        self, *, user_input: dict[str, Any], errors: dict[str, str]
    ) -> ConfigFlowResult | None:
        endpoint = _normalized_endpoint(user_input=user_input, errors=errors)
        interval = _normalized_interval(user_input=user_input, errors=errors)
        if endpoint is None or interval is None or errors:
            return None
        host, port, unit_id = endpoint
        values = {
            CONF_HOST: host,
            CONF_PORT: port,
            CONF_UNIT_ID: unit_id,
            CONF_SCAN_INTERVAL: interval,
        }
        return await self._async_validate_connection(values=values, errors=errors)

    async def _async_validate_connection(
        self, *, values: dict[str, Any], errors: dict[str, str]
    ) -> ConfigFlowResult | None:
        host, port, unit_id = (values[field] for field in _CONNECTION_FIELDS)
        if self._endpoint_exists_for_other(host=host, port=port, unit_id=unit_id):
            errors["base"] = "already_configured"
            return None
        validation_session = self._same_endpoint_validation_session(
            host=host, port=port, unit_id=unit_id
        )
        if validation_session is None:
            device = await _validate_endpoint(
                host=host, port=port, unit_id=unit_id, errors=errors
            )
        else:
            async with validation_session:
                device = await _validate_endpoint(
                    host=host, port=port, unit_id=unit_id, errors=errors
                )
        if device is None:
            return None
        if self._endpoint_exists_for_other(host=host, port=port, unit_id=unit_id):
            errors["base"] = "already_configured"
            return None
        if self._serial_exists_for_other(serial=device.serial):
            errors["base"] = "already_configured"
            return None
        if device.serial != self.config_entry.unique_id:
            self._replacement_device = device
            self._replacement_values = values
            return self._show_replacement_confirmation(device=device)
        return self._save_changes(device=device, values=values)

    def _same_endpoint_validation_session(
        self, *, host: str, port: int, unit_id: int
    ) -> AbstractAsyncContextManager[None] | None:
        entry = self.config_entry
        if not _entry_owns_endpoint(entry=entry, host=host, port=port, unit_id=unit_id):
            return None
        runtime_data = getattr(entry, "runtime_data", None)
        coordinator = getattr(runtime_data, "coordinator", None)
        if coordinator is None:
            return None
        return coordinator.async_validation_session()

    def _show_replacement_confirmation(self, *, device: Hs3Device) -> ConfigFlowResult:
        return self.async_show_form(
            step_id="confirm_replacement",
            data_schema=vol.Schema({}),
            errors={},
            description_placeholders={"serial": device.serial},
        )

    async def async_step_confirm_replacement(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is None:
            return self.async_show_form(
                step_id="confirm_replacement",
                data_schema=vol.Schema({}),
                errors={},
                description_placeholders={
                    "serial": self._replacement_device.serial
                    if self._replacement_device
                    else ""
                },
            )
        device = self._replacement_device
        values = self._replacement_values
        if device is None or values is None:
            return self.async_abort(reason="replacement_not_pending")
        host, port, unit_id = (values[field] for field in _CONNECTION_FIELDS)
        if self._endpoint_exists_for_other(host=host, port=port, unit_id=unit_id):
            return self.async_abort(reason="already_configured")
        if self._serial_exists_for_other(serial=device.serial):
            return self.async_abort(reason="already_configured")
        return self._save_changes(device=device, values=values)

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

    def _save_changes(
        self, *, device: Hs3Device | None, values: dict[str, Any]
    ) -> ConfigFlowResult:
        entry = self.config_entry
        connection = {field: values[field] for field in _CONNECTION_FIELDS}
        self.hass.config_entries.async_update_entry(
            entry,
            data=connection,
            options={CONF_SCAN_INTERVAL: values[CONF_SCAN_INTERVAL]},
            unique_id=device.serial if device is not None else entry.unique_id,
        )
        return self.async_abort(reason="changes_saved")


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
        ): _number_box(minimum=1, maximum=65535),
        vol.Required(
            CONF_UNIT_ID, default=values.get(CONF_UNIT_ID, DEFAULT_UNIT_ID)
        ): _number_box(minimum=MIN_UNIT_ID, maximum=MAX_UNIT_ID),
        vol.Required(
            CONF_SCAN_INTERVAL,
            default=values.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        ): _number_box(minimum=DEFAULT_SCAN_INTERVAL),
    }
    return vol.Schema(schema)


def _options_schema(*, entry: ConfigEntry) -> vol.Schema:
    defaults = dict(entry.data)
    defaults[CONF_SCAN_INTERVAL] = entry.options.get(
        CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
    )
    return _endpoint_schema(defaults=defaults)


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


async def _validate_endpoint(
    *, host: str, port: int, unit_id: int, errors: dict[str, str]
) -> Hs3Device | None:
    client = ModbusTcpClient(
        host=host, port=port, unit_id=unit_id, timeout=REQUEST_TIMEOUT
    )
    try:
        device = await identify(client=client)
        await read_telemetry(client=client)
    except UnsupportedDeviceError:
        errors["base"] = "unsupported_device"
    except ValueError:
        errors["base"] = "invalid_device_data"
    except ModbusError as err:
        errors["base"] = _read_error_reason(error=err)
    else:
        return device
    finally:
        await client.close()
    return None


def _entry_owns_endpoint(
    *, entry: ConfigEntry, host: str, port: int, unit_id: int
) -> bool:
    return (
        entry.data.get(CONF_HOST, "").casefold() == host.casefold()
        and entry.data.get(CONF_PORT, DEFAULT_PORT) == port
        and entry.data.get(CONF_UNIT_ID, DEFAULT_UNIT_ID) == unit_id
    )


def _read_error_reason(*, error: ModbusError) -> str:
    if error.exception_code is not None:
        return "read_rejected"
    if str(error) in {
        ModbusErrorMessage.CONNECTION_TIMEOUT,
        ModbusErrorMessage.REQUEST_TIMEOUT,
    }:
        return "timeout"
    return "cannot_connect"
