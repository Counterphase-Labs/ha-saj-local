from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .equipment import Detection, evaluate
from .telemetry import read_telemetry

if TYPE_CHECKING:
    from collections.abc import Collection, Mapping

    from .client import RegisterReader
    from .codec import Value
    from .device import Device
    from .models import Equipment

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class Detected:
    detections: Mapping[Equipment, Detection]
    readings: Mapping[str, Value]


async def detect(
    *,
    client: RegisterReader,
    device: Device,
    probed: Collection[Equipment],
    also: Collection[str] = (),
) -> Detected:
    probes = [probe for probe in device.profile.probes if probe.equipment in probed]
    keys = tuple(
        dict.fromkeys([*(key for probe in probes for key in probe.keys), *also])
    )
    if not keys:
        return Detected(detections={}, readings={})
    readout = await read_telemetry(client=client, device=device, enabled=keys)
    detections: dict[Equipment, Detection] = {}
    for probe in probes:
        detection = evaluate(
            probe=probe,
            values={
                key: readout.values[key] for key in probe.keys if key in readout.values
            },
        )
        _LOGGER.debug(
            "SAJ %s probe read %s and found it %s",
            probe.equipment,
            dict(detection.values),
            "fitted" if detection.fitted else "not fitted",
        )
        detections[probe.equipment] = detection
    return Detected(
        detections=detections,
        readings={key: readout.values[key] for key in also if key in readout.values},
    )
