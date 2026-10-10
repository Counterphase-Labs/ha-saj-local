from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .errors import ModelMismatchError, UnknownModelError, UnsupportedDeviceError
from .models.h2 import PROFILE as H2
from .models.hs3 import PROFILE as HS3

if TYPE_CHECKING:
    from collections.abc import Sequence

    from .models import Profile

AUTOMATIC = "automatic"


@dataclass(frozen=True)
class Resolution:
    profile: Profile
    detected: bool


PROFILES = (HS3, H2)


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
