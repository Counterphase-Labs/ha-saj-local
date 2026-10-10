from __future__ import annotations

from typing import TYPE_CHECKING

from .device_type import format_device_type

if TYPE_CHECKING:
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
