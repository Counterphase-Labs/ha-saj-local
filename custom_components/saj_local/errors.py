from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from functools import singledispatch
from typing import TYPE_CHECKING

from homeassistant.exceptions import HomeAssistantError, ServiceValidationError

from .const import DOMAIN
from .saj.client import ModbusError, ModbusErrorMessage
from .saj.device_type import format_device_type
from .saj.errors import (
    AnotherFunctionRunningError,
    ControlDisabledError,
    EmsTimeoutError,
    InvalidValueError,
    LinkUnavailableError,
    ModelError,
    ModelMismatchError,
    ModelUnverifiedError,
    NoPowerTargetError,
    ProtectedSettingError,
    SeparateRegistersError,
    UnknownModelError,
    UnknownSettingError,
    UnsupportedDeviceError,
    UnusablePowerError,
    WriteAllowanceError,
    WriteError,
    WriteMismatchError,
    WriteRejectedError,
    WriteUnconfirmedError,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from .saj.codec import Value

TIMEOUT_MESSAGES = frozenset(
    {ModbusErrorMessage.CONNECTION_TIMEOUT, ModbusErrorMessage.REQUEST_TIMEOUT}
)
HANDLED_ERRORS: tuple[type[Exception], ...] = (ModelError, ValueError, ModbusError)
WRITE_ERRORS: tuple[type[WriteError], ...] = (WriteError,)
UNKNOWN_EXCEPTION_CODE = "unknown"
FUNCTION_PLACEHOLDERS = frozenset({"function", "running"})


class WriteOutcome(StrEnum):
    ACKNOWLEDGED = "acknowledged"
    REJECTED = "rejected"
    UNCONFIRMED = "unconfirmed"
    MISMATCHED = "mismatched"


@dataclass(frozen=True)
class Translation:
    key: str
    concerns_model: bool = False
    placeholders: dict[str, str] = field(default_factory=dict)


def translate_error(*, error: Exception) -> Translation:
    if isinstance(error, ModelError):
        return _translate_model_error(error)
    if isinstance(error, ValueError):
        return Translation(key="invalid_device_data")
    if isinstance(error, TimeoutError) or (
        isinstance(error, ModbusError) and str(error) in TIMEOUT_MESSAGES
    ):
        return Translation(key="timeout")
    if isinstance(error, ModbusError) and error.exception_code is not None:
        return Translation(key="read_rejected")
    return Translation(key="cannot_connect")


def has_safe_message(*, error: Exception) -> bool:
    return isinstance(error, ModelError | ModbusError)


@singledispatch
def _translate_model_error(error: ModelError) -> Translation:
    message = f"No translation for model error {type(error).__name__}"
    raise NotImplementedError(message)


@_translate_model_error.register
def _unsupported_device(error: UnsupportedDeviceError) -> Translation:
    return Translation(
        key="unsupported_device",
        concerns_model=True,
        placeholders={"device_type": format_device_type(error.device_type)},
    )


@_translate_model_error.register
def _model_mismatch(error: ModelMismatchError) -> Translation:
    return Translation(
        key="model_mismatch",
        concerns_model=True,
        placeholders={
            "selected_model": error.selected.display_name,
            "detected_model": error.detected.display_name,
        },
    )


@_translate_model_error.register
def _unknown_model(error: UnknownModelError) -> Translation:
    return Translation(
        key="unknown_model",
        concerns_model=True,
        placeholders={"selection": error.selection},
    )


def write_outcome(*, error: WriteError) -> WriteOutcome | None:
    if isinstance(error, WriteRejectedError):
        return WriteOutcome.REJECTED
    if isinstance(error, WriteUnconfirmedError):
        return WriteOutcome.UNCONFIRMED
    if isinstance(error, WriteMismatchError):
        return WriteOutcome.MISMATCHED
    return None


def rejection_code(*, error: WriteError) -> int | None:
    return error.exception_code if isinstance(error, WriteRejectedError) else None


def read_back_values(*, error: WriteError) -> Mapping[str, Value]:
    return error.read_back if isinstance(error, WriteMismatchError) else {}


def write_failure(
    *, error: WriteError, function_names: Mapping[str, str] | None = None
) -> HomeAssistantError:
    failure = _write_failure(error)
    names = function_names or {}
    placeholders = failure.translation_placeholders
    if placeholders:
        failure.translation_placeholders = {
            key: names.get(value, value) if key in FUNCTION_PLACEHOLDERS else value
            for key, value in placeholders.items()
        }
    return failure


def _refusal(
    *, key: str, placeholders: dict[str, str] | None = None
) -> ServiceValidationError:
    return ServiceValidationError(
        translation_domain=DOMAIN,
        translation_key=key,
        translation_placeholders=placeholders,
    )


def _device_failure(
    *, key: str, placeholders: dict[str, str] | None = None
) -> HomeAssistantError:
    return HomeAssistantError(
        translation_domain=DOMAIN,
        translation_key=key,
        translation_placeholders=placeholders,
    )


@singledispatch
def _write_failure(error: WriteError) -> HomeAssistantError:
    message = f"No translation for write error {type(error).__name__}"
    raise NotImplementedError(message)


@_write_failure.register
def _control_disabled(error: ControlDisabledError) -> HomeAssistantError:
    del error
    return _refusal(key="control_not_enabled")


@_write_failure.register
def _model_unverified(error: ModelUnverifiedError) -> HomeAssistantError:
    del error
    return _refusal(key="model_unverified")


@_write_failure.register
def _protected_setting(error: ProtectedSettingError) -> HomeAssistantError:
    return _refusal(key="protected_setting", placeholders={"setting": error.key})


@_write_failure.register
def _unknown_setting(error: UnknownSettingError) -> HomeAssistantError:
    return _refusal(key="unknown_setting", placeholders={"setting": error.key})


@_write_failure.register
def _separate_registers(error: SeparateRegistersError) -> HomeAssistantError:
    del error
    return _refusal(key="separate_registers")


@_write_failure.register
def _invalid_value(error: InvalidValueError) -> HomeAssistantError:
    return _refusal(key=f"invalid_value_{error.problem}")


@_write_failure.register
def _link_unavailable(error: LinkUnavailableError) -> HomeAssistantError:
    del error
    return _refusal(key="link_unavailable")


@_write_failure.register
def _write_allowance(error: WriteAllowanceError) -> HomeAssistantError:
    return _refusal(
        key="write_allowance",
        placeholders={"limit": str(error.limit), "window": f"{error.window:g}"},
    )


@_write_failure.register
def _ems_timeout(error: EmsTimeoutError) -> HomeAssistantError:
    return _refusal(
        key="ems_timeout_too_short",
        placeholders={
            "timeout": str(error.timeout),
            "interval": str(error.interval),
        },
    )


@_write_failure.register
def _no_power_target(error: NoPowerTargetError) -> HomeAssistantError:
    return _refusal(key="no_power_target", placeholders={"function": error.function})


@_write_failure.register
def _another_function_running(error: AnotherFunctionRunningError) -> HomeAssistantError:
    return _refusal(
        key="another_function_running", placeholders={"running": error.running}
    )


@_write_failure.register
def _unusable_power(error: UnusablePowerError) -> HomeAssistantError:
    return _refusal(
        key="unusable_power",
        placeholders={"minimum": str(error.minimum), "maximum": str(error.maximum)},
    )


@_write_failure.register
def _write_rejected(error: WriteRejectedError) -> HomeAssistantError:
    code = (
        UNKNOWN_EXCEPTION_CODE if error.exception_code is None else error.exception_code
    )
    return _device_failure(
        key="write_rejected", placeholders={"exception_code": str(code)}
    )


@_write_failure.register
def _write_unconfirmed(error: WriteUnconfirmedError) -> HomeAssistantError:
    del error
    return _device_failure(key="write_unconfirmed")


@_write_failure.register
def _write_mismatch(error: WriteMismatchError) -> HomeAssistantError:
    del error
    return _device_failure(key="write_mismatch")
