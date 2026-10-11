from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .catalogue import Fit
from .models import ALL_EQUIPMENT, Equipment
from .profiles import AUTOMATIC, resolve_profile

if TYPE_CHECKING:
    from .client import RegisterReader
    from .models import Profile

IDENTITY_ADDRESS = 0x8F00
IDENTITY_WORD_COUNT = 2
SERIAL_ADDRESS = 0x8F03
SERIAL_WORD_COUNT = 10


@dataclass(frozen=True)
class Device:
    serial: str
    device_type: int
    rated_power: int
    profile: Profile
    detected: bool
    equipment: frozenset[Equipment] = field(default=ALL_EQUIPMENT)
    pack_limit: int | None = None

    @property
    def fit(self) -> Fit:
        return Fit(
            profile=self.profile,
            device_type=self.device_type,
            equipment=self.equipment,
            pack_limit=self.pack_limit,
        )


async def identify(client: RegisterReader, selection: str = AUTOMATIC) -> Device:
    type_power = await client.read_holding_registers(
        address=IDENTITY_ADDRESS, count=IDENTITY_WORD_COUNT
    )
    device_type, rated_power = type_power
    resolution = resolve_profile(device_type=device_type, selection=selection)
    serial_words = await client.read_holding_registers(
        address=SERIAL_ADDRESS, count=SERIAL_WORD_COUNT
    )
    serial_bytes = b"".join(word.to_bytes(2, "big") for word in serial_words)
    try:
        serial = serial_bytes.rstrip(b"\x00").decode("ascii")
    except UnicodeDecodeError as err:
        message = "Invalid serial number encoding"
        raise ValueError(message) from err
    if not serial or not serial.strip() or not serial.isprintable():
        message = "Invalid serial number"
        raise ValueError(message)
    return Device(
        serial=serial,
        device_type=device_type,
        rated_power=rated_power,
        profile=resolution.profile,
        detected=resolution.detected,
    )
