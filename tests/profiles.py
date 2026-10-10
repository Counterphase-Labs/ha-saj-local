from __future__ import annotations

from dataclasses import replace
from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Collection

    from custom_components.saj_local.saj.models import Profile

LAST_ADDRESS = 0xFFFF


def profile(
    *,
    base: Profile,
    key: str,
    device_types: Collection[int],
    hand_verified: bool,
    keys: Collection[str] = (),
) -> Profile:
    library = type(base).__module__.rsplit(".", maxsplit=1)[0]
    catalogue = import_module(f"{library}.catalogue").catalogue_of(profile=base)
    shape = replace(base.maximum_shape, phases=1, strings=1, assumed=False)
    everything = replace(base.spans[0], name="everything", first=0, last=LAST_ADDRESS)
    template = base.placements[0]
    return replace(
        base,
        key=key,
        display_name=key.capitalize(),
        device_types=dict.fromkeys(device_types, shape),
        hand_verified=hand_verified,
        maximum_shape=shape,
        spans=(everything,),
        placements=tuple(
            replace(
                template,
                key=register.key,
                address=register.address,
                evidence=register.evidence,
            )
            for register in catalogue.registers
            if register.key in keys
        ),
        families=(),
        replacements=(),
    )
