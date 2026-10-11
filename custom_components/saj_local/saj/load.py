from __future__ import annotations

from typing import TYPE_CHECKING

from .budget import requests_per_minute
from .catalogue import device_keys
from .schedule import build_cadences
from .telemetry import plan_requests

if TYPE_CHECKING:
    from collections.abc import Collection, Iterable

    from .catalogue import Fit
    from .health import Break
    from .schedule import Cadence


def requests_per_read(
    *,
    fit: Fit,
    keys: Collection[str],
    breaks: Collection[Break] = (),
) -> int:
    return len(plan_requests(fit=fit, enabled=keys, breaks=breaks))


def planned_load(
    *,
    fit: Fit,
    enabled: Collection[str] | None,
    cadences: Iterable[Cadence],
    breaks: Collection[Break] = (),
) -> float:
    return requests_per_minute(
        reads=(
            (
                cadence.interval,
                requests_per_read(
                    fit=fit,
                    keys=cadence.keys
                    if enabled is None
                    else cadence.keys & set(enabled),
                    breaks=breaks,
                ),
            )
            for cadence in cadences
        )
    )


def installation_load(
    *,
    fit: Fit,
    enabled: Collection[str],
    default_interval: int,
    groups: Iterable[Cadence],
) -> float:
    return planned_load(
        fit=fit,
        enabled=enabled,
        cadences=build_cadences(
            default_interval=default_interval,
            groups=groups,
            supported=device_keys(fit=fit),
        ),
    )
