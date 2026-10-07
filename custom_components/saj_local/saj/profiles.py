from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .errors import ModelMismatchError, UnknownModelError, UnsupportedDeviceError
from .telemetry import (
    BATTERY_POWER,
    BATTERY_SOC,
    GRID_POWER,
    LOAD_POWER,
    OPERATING_MODE,
    PV_POWER,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

AUTOMATIC = "automatic"


@dataclass(frozen=True)
class Profile:
    key: str
    display_name: str
    device_types: frozenset[int]
    measurement_keys: frozenset[str]
    hand_verified: bool


@dataclass(frozen=True)
class Resolution:
    profile: Profile
    detected: bool


_SHARED_MEASUREMENT_KEYS = frozenset(
    {OPERATING_MODE, BATTERY_SOC, LOAD_POWER, PV_POWER, BATTERY_POWER, GRID_POWER}
)

PROFILES = (
    Profile(
        key="hs3",
        display_name="HS3",
        device_types=frozenset({0x1610}),
        measurement_keys=_SHARED_MEASUREMENT_KEYS,
        hand_verified=True,
    ),
    Profile(
        key="h2",
        display_name="H2",
        device_types=frozenset({0x005A, 0x005B}),
        measurement_keys=_SHARED_MEASUREMENT_KEYS,
        hand_verified=False,
    ),
)


def resolve_profile(
    device_type: int,
    selection: str,
    profiles: Sequence[Profile] = PROFILES,
) -> Resolution:
    recognised = next(
        (profile for profile in profiles if device_type in profile.device_types),
        None,
    )
    if selection == AUTOMATIC:
        if recognised is None:
            raise UnsupportedDeviceError(device_type)
        return Resolution(profile=recognised, detected=True)
    selected = next((profile for profile in profiles if profile.key == selection), None)
    if selected is None:
        raise UnknownModelError(selection)
    if recognised is None:
        return Resolution(profile=selected, detected=False)
    if recognised != selected:
        raise ModelMismatchError(selected=selected, detected=recognised)
    return Resolution(profile=selected, detected=True)
