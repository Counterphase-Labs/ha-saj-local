from __future__ import annotations

from dataclasses import dataclass, field
from functools import singledispatch

from .saj.client import ModbusError, ModbusErrorMessage
from .saj.device_type import format_device_type
from .saj.errors import (
    ModelError,
    ModelMismatchError,
    UnknownModelError,
    UnsupportedDeviceError,
)

TIMEOUT_MESSAGES = frozenset(
    {ModbusErrorMessage.CONNECTION_TIMEOUT, ModbusErrorMessage.REQUEST_TIMEOUT}
)
HANDLED_ERRORS: tuple[type[Exception], ...] = (ModelError, ValueError, ModbusError)


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
