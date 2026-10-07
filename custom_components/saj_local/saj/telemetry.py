from __future__ import annotations

from collections.abc import Callable, Collection, Iterable, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import ModbusTcpClient
    from .device import Device

OPERATING_MODE = "operating_mode"
BATTERY_SOC = "battery_soc"
LOAD_POWER = "load_power"
PV_POWER = "pv_power"
BATTERY_POWER = "battery_power"
GRID_POWER = "grid_power"

SOC_SCALE = 100
MAX_SOC_RAW = 10000
SIGN_BIT = 0x8000
WORD_MODULUS = 0x10000
OPERATING_MODE_NAMES = {
    0: "initialisation",
    1: "standby",
    2: "operating",
    3: "off_grid",
    4: "grid_connected_load_bypass",
    5: "fault",
    6: "upgrade",
    7: "debugging",
    8: "self_check",
    9: "reset",
}

type Decoder = Callable[[int], int | float | None]


@dataclass(frozen=True)
class Measurement:
    key: str
    address: int
    decoder: Decoder


@dataclass(frozen=True)
class ReadRange:
    address: int
    count: int
    keys: tuple[str, ...]


@dataclass(frozen=True)
class Telemetry:
    values: Mapping[str, int | float | None]

    def get(self, key: str) -> int | float | None:
        return self.values.get(key)


def decode_unsigned(raw: int) -> int:
    return raw


def decode_signed(raw: int) -> int:
    return raw - WORD_MODULUS if raw & SIGN_BIT else raw


def decode_percent(raw: int) -> float | None:
    return raw / SOC_SCALE if 0 <= raw <= MAX_SOC_RAW else None


MEASUREMENTS = {
    measurement.key: measurement
    for measurement in (
        Measurement(key=OPERATING_MODE, address=0x4004, decoder=decode_unsigned),
        Measurement(key=BATTERY_SOC, address=0x406F, decoder=decode_percent),
        Measurement(key=LOAD_POWER, address=0x40A0, decoder=decode_signed),
        Measurement(key=PV_POWER, address=0x40A5, decoder=decode_signed),
        Measurement(key=BATTERY_POWER, address=0x40A6, decoder=decode_signed),
        Measurement(key=GRID_POWER, address=0x40A7, decoder=decode_signed),
    )
}


def plan_ranges(measurements: Iterable[Measurement]) -> list[ReadRange]:
    ranges: list[ReadRange] = []
    for measurement in sorted(measurements, key=lambda item: item.address):
        if ranges and ranges[-1].address + ranges[-1].count == measurement.address:
            last = ranges[-1]
            ranges[-1] = ReadRange(
                address=last.address,
                count=last.count + 1,
                keys=(*last.keys, measurement.key),
            )
        else:
            ranges.append(
                ReadRange(address=measurement.address, count=1, keys=(measurement.key,))
            )
    return ranges


def decode_telemetry(
    raw: Mapping[str, int], measurements: Mapping[str, Measurement]
) -> Telemetry:
    return Telemetry(
        values={key: measurements[key].decoder(word) for key, word in raw.items()}
    )


async def read_telemetry(
    client: ModbusTcpClient,
    device: Device,
    enabled: Collection[str] | None = None,
    measurements: Mapping[str, Measurement] = MEASUREMENTS,
) -> Telemetry:
    requested = measurements.keys() if enabled is None else enabled
    selected = [
        measurement
        for key, measurement in measurements.items()
        if key in requested and key in device.profile.measurement_keys
    ]
    raw: dict[str, int] = {}
    for read_range in plan_ranges(measurements=selected):
        words = await client.read_holding_registers(
            address=read_range.address, count=read_range.count
        )
        raw.update(zip(read_range.keys, words, strict=True))
    return decode_telemetry(raw=raw, measurements=measurements)
