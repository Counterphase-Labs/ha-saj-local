from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from .device_type import format_device_type

if TYPE_CHECKING:
    from collections.abc import Mapping

    from .codec import Value
    from .models import Profile


class ModelError(Exception):
    pass


class UnsupportedDeviceError(ModelError):
    def __init__(self, device_type: int) -> None:
        super().__init__(f"Unsupported device type {format_device_type(device_type)}")
        self.device_type = device_type


class ModelMismatchError(ModelError):
    def __init__(self, selected: Profile, detected: Profile) -> None:
        super().__init__(
            f"Selected model {selected.key} contradicts detected model {detected.key}"
        )
        self.selected = selected
        self.detected = detected


class UnknownModelError(ModelError):
    def __init__(self, selection: str) -> None:
        super().__init__(f"Unknown model selection {selection}")
        self.selection = selection


class ValueProblem(StrEnum):
    NOT_A_NUMBER = "not_a_number"
    OUT_OF_RANGE = "out_of_range"
    NOT_AN_OPTION = "not_an_option"
    NOT_A_TIME = "not_a_time"
    NOT_A_CLOCK = "not_a_clock"
    DOES_NOT_FIT = "does_not_fit"
    UNSUPPORTED_ENCODING = "unsupported_encoding"


class WriteError(Exception):
    link_failed = False


class ControlDisabledError(WriteError):
    def __init__(self) -> None:
        super().__init__("Control is not enabled")


class ModelUnverifiedError(WriteError):
    def __init__(self) -> None:
        super().__init__("The model could not be verified")


class ProtectedSettingError(WriteError):
    def __init__(self, key: str) -> None:
        super().__init__(f"Setting {key} is a protected commissioning setting")
        self.key = key


class UnknownSettingError(WriteError):
    def __init__(self, key: str) -> None:
        super().__init__(f"Setting {key} cannot be written on this device")
        self.key = key


class SeparateRegistersError(WriteError):
    def __init__(self) -> None:
        super().__init__("Changes made together must be fields of one register")


class InvalidValueError(WriteError):
    def __init__(self, problem: ValueProblem) -> None:
        super().__init__(f"Value rejected: {problem}")
        self.problem = problem


class LinkUnavailableError(WriteError):
    def __init__(self, *, cause: Exception | None = None) -> None:
        super().__init__("The inverter is not reachable")
        self.cause = cause
        self.link_failed = cause is not None


class WriteAllowanceError(WriteError):
    def __init__(self, *, limit: int, window: float) -> None:
        super().__init__(f"More than {limit} writes in {window:g} seconds")
        self.limit = limit
        self.window = window


class EmsTimeoutError(WriteError):
    def __init__(self, *, timeout: int, interval: int) -> None:
        super().__init__(
            f"Device timeout of {timeout} seconds is not longer than the"
            f" {interval} second heartbeat"
        )
        self.timeout = timeout
        self.interval = interval


class WriteRejectedError(WriteError):
    def __init__(self, *, exception_code: int | None) -> None:
        super().__init__(f"The inverter rejected the write (code {exception_code})")
        self.exception_code = exception_code


class WriteUnconfirmedError(WriteError):
    link_failed = True

    def __init__(self, *, cause: Exception, acknowledged: bool) -> None:
        super().__init__(f"The write may or may not have been applied: {cause}")
        self.cause = cause
        self.acknowledged = acknowledged


class WriteMismatchError(WriteError):
    def __init__(self, *, read_back: Mapping[str, Value]) -> None:
        super().__init__("The inverter holds a different value than was written")
        self.read_back = read_back
