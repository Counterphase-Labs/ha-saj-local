from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import ModbusTcpClient

HS3_DEVICE_TYPE = 0x1610
SOC_SCALE = 100
MAX_SOC_RAW = 10000
MODE_NAMES = {
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


class UnsupportedDeviceError(Exception):
    pass


@dataclass(frozen=True)
class Hs3Device:
    serial: str
    device_type: int
    rated_power: int


@dataclass(frozen=True)
class Hs3Telemetry:
    operating_mode: int | None = None
    pv_power: int | None = None
    battery_power: int | None = None
    battery_soc: float | None = None
    grid_power: int | None = None
    load_power: int | None = None


async def identify(client: ModbusTcpClient) -> Hs3Device:
    type_power = await client.read_holding_registers(address=0x8F00, count=2)
    device_type, rated_power = type_power
    if device_type != HS3_DEVICE_TYPE:
        message = f"Unsupported device type {device_type:#06x}"
        raise UnsupportedDeviceError(message)
    serial_words = await client.read_holding_registers(address=0x8F03, count=10)
    serial_bytes = b"".join(word.to_bytes(2, "big") for word in serial_words)
    try:
        serial = serial_bytes.rstrip(b"\x00").decode("ascii")
    except UnicodeDecodeError as err:
        message = "Invalid serial number encoding"
        raise ValueError(message) from err
    if not serial or not serial.strip() or not serial.isprintable():
        message = "Invalid serial number"
        raise ValueError(message)
    return Hs3Device(serial=serial, device_type=device_type, rated_power=rated_power)


async def read_telemetry(
    client: ModbusTcpClient,
    enabled: set[str] | None = None,
) -> Hs3Telemetry:
    selected = enabled if enabled is not None else set(MEASUREMENTS)
    ranges = _ranges(enabled=selected)
    raw: dict[str, int] = {}
    for address, count, keys in ranges:
        words = await client.read_holding_registers(address=address, count=count)
        raw.update(zip(keys, words, strict=True))
    return decode_hs3(values=raw)


MEASUREMENTS = {
    "operating_mode": 0x4004,
    "battery_soc": 0x406F,
    "load_power": 0x40A0,
    "pv_power": 0x40A5,
    "battery_power": 0x40A6,
    "grid_power": 0x40A7,
}


def decode_hs3(values: dict[str, int]) -> Hs3Telemetry:
    mode = values.get("operating_mode")
    soc_raw = values.get("battery_soc")
    soc = (
        soc_raw / SOC_SCALE
        if soc_raw is not None and 0 <= soc_raw <= MAX_SOC_RAW
        else None
    )
    return Hs3Telemetry(
        operating_mode=mode,
        pv_power=_signed(value=values.get("pv_power")),
        battery_power=_signed(value=values.get("battery_power")),
        battery_soc=soc,
        grid_power=_signed(value=values.get("grid_power")),
        load_power=_signed(value=values.get("load_power")),
    )


def _signed(value: int | None) -> int | None:
    if value is None:
        return None
    return value - 0x10000 if value & 0x8000 else value


def _ranges(enabled: set[str]) -> list[tuple[int, int, list[str]]]:
    selected = sorted(
        (address, key) for key, address in MEASUREMENTS.items() if key in enabled
    )
    ranges: list[tuple[int, int, list[str]]] = []
    for address, key in selected:
        if ranges and ranges[-1][0] + ranges[-1][1] == address:
            start, count, keys = ranges[-1]
            ranges[-1] = (start, count + 1, [*keys, key])
        else:
            ranges.append((address, 1, [key]))
    return ranges
