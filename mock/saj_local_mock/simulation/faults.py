"""Fault state of the simulated equipment and what each fault does to the plant."""

import dataclasses
import enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

BITS_PER_REGISTER = 32
WORD_MAXIMUM = 0xFFFF
MAX_PACKS = 4


def hex_address(*, address: int) -> str:
    """A register address as the SAJ documents print it, for example 0x400B."""
    return f"0x{address:04X}"


class Equipment(enum.StrEnum):
    INVERTER = "inverter"
    BATTERY = "battery"
    EV_CHARGER = "ev_charger"


class Effect(enum.Enum):
    """What a fault does beyond setting its own bit."""

    INVERTER_STOP = enum.auto()
    GRID_LOST = enum.auto()
    METER_A_LOST = enum.auto()
    NO_CHARGE = enum.auto()
    NO_DISCHARGE = enum.auto()
    EV_STOP = enum.auto()


BATTERY_STOP = frozenset({Effect.NO_CHARGE, Effect.NO_DISCHARGE})

REGISTERS: dict[Equipment, tuple[int, ...]] = {
    Equipment.INVERTER: (0x4005, 0x4007, 0x4009),
    Equipment.BATTERY: (0x400B,),
    Equipment.EV_CHARGER: (0x30AB, 0x30AD),
}


@dataclasses.dataclass(frozen=True, slots=True, order=True)
class FaultBit:
    register: int
    bit: int

    @property
    def key(self) -> str:
        return f"{hex_address(address=self.register)}:{self.bit}"


@dataclasses.dataclass(frozen=True, slots=True, order=True)
class PackCodes:
    """Fault and warning words of one battery pack. They are raw codes, not bits."""

    pack: int
    fault: int = 0
    warning: int = 0


def fault_word_key(*, register: int) -> str:
    return f"fault_{register:04x}"


def pack_key(*, pack: int, kind: str) -> str:
    return f"pack{pack}_{kind}"


@dataclasses.dataclass(frozen=True, slots=True)
class FaultState:
    inverter: frozenset[FaultBit] = frozenset()
    battery: frozenset[FaultBit] = frozenset()
    ev_charger: frozenset[FaultBit] = frozenset()
    packs: tuple[PackCodes, ...] = ()

    def bits(self, *, equipment: Equipment) -> frozenset[FaultBit]:
        return {
            Equipment.INVERTER: self.inverter,
            Equipment.BATTERY: self.battery,
            Equipment.EV_CHARGER: self.ev_charger,
        }[equipment]

    def all_bits(self) -> frozenset[FaultBit]:
        return self.inverter | self.battery | self.ev_charger

    def word(self, *, register: int) -> int:
        return sum(
            1 << fault.bit for fault in self.all_bits() if fault.register == register
        )

    def pack(self, *, number: int) -> PackCodes:
        for codes in self.packs:
            if codes.pack == number:
                return codes
        return PackCodes(pack=number)

    def with_bits(
        self, *, equipment: Equipment, bits: Iterable[FaultBit]
    ) -> FaultState:
        changed = frozenset(bits)
        if equipment is Equipment.INVERTER:
            return dataclasses.replace(self, inverter=changed)
        if equipment is Equipment.BATTERY:
            return dataclasses.replace(self, battery=changed)
        return dataclasses.replace(self, ev_charger=changed)

    def with_pack(self, *, codes: PackCodes) -> FaultState:
        others = tuple(known for known in self.packs if known.pack != codes.pack)
        kept = (codes,) if codes.fault or codes.warning else ()
        return dataclasses.replace(self, packs=tuple(sorted(others + kept)))


def active_effects(
    *, state: FaultState, effects: Mapping[FaultBit, frozenset[Effect]]
) -> frozenset[Effect]:
    """Every effect of the set bits, and of any pack fault code other than 0."""
    active: set[Effect] = set()
    for fault in state.all_bits():
        active |= effects.get(fault, frozenset())
    if any(codes.fault for codes in state.packs):
        active |= BATTERY_STOP
    return frozenset(active)


@dataclasses.dataclass(frozen=True, slots=True)
class FaultEntry:
    equipment: Equipment
    bit: FaultBit
    name: str
    effects: frozenset[Effect]
    reserved: bool = False


@dataclasses.dataclass(frozen=True, slots=True)
class FaultMap:
    """Every fault bit a model reports on the equipment fitted, and the packs it has."""

    entries: tuple[FaultEntry, ...]
    pack_count: int

    def for_equipment(self, *, equipment: Equipment) -> tuple[FaultEntry, ...]:
        return tuple(entry for entry in self.entries if entry.equipment is equipment)

    def effects(self) -> dict[FaultBit, frozenset[Effect]]:
        return {entry.bit: entry.effects for entry in self.entries}

    def find(self, *, equipment: Equipment, name: str) -> tuple[FaultBit, ...]:
        """Every bit that reports the named condition, as the fault tables list them."""
        return tuple(
            entry.bit
            for entry in self.for_equipment(equipment=equipment)
            if entry.name == name and not entry.reserved
        )
