from __future__ import annotations

from dataclasses import replace
from importlib import import_module
from itertools import pairwise
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
    chosen = [register for register in catalogue.registers if register.key in keys]
    template = base.placements[0]
    unread = sorted(
        {register.row for register in chosen if not register.readable if register.row},
        key=lambda row: row.address,
    )
    bounds = [
        (0, unread[0].address - 1) if unread else (0, LAST_ADDRESS),
        *((before.end, after.address - 1) for before, after in pairwise(unread)),
        *([(unread[-1].end, LAST_ADDRESS)] if unread else []),
    ]
    spans = tuple(
        replace(base.spans[0], name="everything", first=first, last=last)
        for first, last in bounds
        if first <= last
    )
    return replace(
        base,
        key=key,
        display_name=key.capitalize(),
        device_types=dict.fromkeys(device_types, shape),
        hand_verified=hand_verified,
        maximum_shape=shape,
        spans=spans,
        placements=tuple(
            replace(
                template,
                key=register.key,
                address=register.address,
                evidence=register.evidence,
            )
            for register in chosen
        ),
        families=(),
        replacements=(),
        probes=(),
    )
