"""Fault bits each model reports, written from the SAJ documents' bit tables.

A bit the document does not name is listed as reserved, so a client's
"unrecognised fault" path can be exercised. Where two registers report the same
condition, both appear under the condition's name. Where the H2 English wording
contradicts its Chinese, the Chinese meaning is used.
"""

import dataclasses
from typing import TYPE_CHECKING

from saj_modbus_mock.models import H2, HS3
from saj_modbus_mock.simulation.faults import (
    BATTERY_STOP,
    BITS_PER_REGISTER,
    REGISTERS,
    Effect,
    Equipment,
    FaultBit,
    FaultEntry,
    FaultMap,
    hex_address,
)

if TYPE_CHECKING:
    from saj_modbus_mock.scenario import Scenario

NO_SOURCES = ""
NO_CHARGE = frozenset({Effect.NO_CHARGE})
NO_DISCHARGE = frozenset({Effect.NO_DISCHARGE})
INVERTER_STOP = frozenset({Effect.INVERTER_STOP})
OFF_GRID = frozenset({Effect.GRID_LOST})
METER_A_LOST = frozenset({Effect.METER_A_LOST})
CHARGER_STOP = frozenset({Effect.EV_STOP})
NO_EFFECT: frozenset[Effect] = frozenset()


@dataclasses.dataclass(frozen=True, slots=True)
class Condition:
    """An inverter condition, its `register:bit` sources and what it does."""

    name: str
    hs3: str
    h2: str
    effects: frozenset[Effect] = NO_EFFECT

    def sources(self, *, model: str) -> tuple[FaultBit, ...]:
        text = {HS3: self.hs3, H2: self.h2}[model]
        return tuple(_source(text=part) for part in text.split())


def _source(*, text: str) -> FaultBit:
    register, bit = text.split(":")
    return FaultBit(register=int(register, 16), bit=int(bit))


INVERTER_CONDITIONS = (
    Condition("Internal communication lost", "4005:0 4009:4", "4005:0 4009:4"),
    Condition(
        "Meter communication lost", "4005:1 4007:7", "4005:1 4007:7", METER_A_LOST
    ),
    Condition("Display board memory fault", "4005:2", "4005:2"),
    Condition("Display board clock fault", "4005:3", "4005:3"),
    Condition("BMS device fault", "4005:4", "4005:4"),
    Condition("BMS communication lost", "4005:5", "4005:5"),
    Condition("CT device fault", "4005:6", NO_SOURCES),
    Condition("Arc detection board communication lost", "4005:7", NO_SOURCES),
    Condition("Slave controller communication lost", "4005:8", NO_SOURCES),
    Condition("PV meter communication lost", "4005:9", NO_SOURCES),
    Condition("EV charger communication lost", "4005:10", NO_SOURCES),
    Condition(
        "Grid phase R overvoltage", "4005:11 4009:8", "4005:11 4009:8", INVERTER_STOP
    ),
    Condition(
        "Grid phase R undervoltage", "4005:12 4009:9", "4005:12 4009:9", INVERTER_STOP
    ),
    Condition("Grid phase S overvoltage", "4005:13", "4005:13 4009:10", INVERTER_STOP),
    Condition("Grid phase S undervoltage", "4005:14", "4005:14 4009:11", INVERTER_STOP),
    Condition(
        "Grid phase T overvoltage", "4005:15 4009:12", "4005:15 4009:12", INVERTER_STOP
    ),
    Condition(
        "Grid phase T undervoltage", "4005:16 4009:13", "4005:16 4009:13", INVERTER_STOP
    ),
    Condition(
        "Grid overfrequency", "4005:17 4009:17", "4005:17 4009:17", INVERTER_STOP
    ),
    Condition(
        "Grid underfrequency", "4005:18 4009:18", "4005:18 4009:18", INVERTER_STOP
    ),
    Condition("DC-DC unit communication lost", "4005:19", NO_SOURCES),
    Condition("DC-DC unit fault", "4005:20", NO_SOURCES),
    Condition("Parallel system communication lost", "4005:21 4009:25", NO_SOURCES),
    Condition("Grid lost", "4005:23 4009:23", "4005:23 4009:23", OFF_GRID),
    Condition("PV input mode fault", "4005:24", "4005:24", INVERTER_STOP),
    Condition(
        "PV hardware overcurrent", "4005:25 4007:9", "4005:25 4007:9", INVERTER_STOP
    ),
    Condition("PV overvoltage", "4005:26", "4005:26 4007:3", INVERTER_STOP),
    Condition(
        "DC bus hardware overvoltage", "4005:27 4007:8", "4005:27 4007:8", INVERTER_STOP
    ),
    Condition("DC bus overvoltage", NO_SOURCES, "4007:0", INVERTER_STOP),
    Condition("DC bus undervoltage", NO_SOURCES, "4007:1", INVERTER_STOP),
    Condition("Grid phase fault", NO_SOURCES, "4007:2", INVERTER_STOP),
    Condition("Islanding", NO_SOURCES, "4007:4", INVERTER_STOP),
    Condition("Arc detection device fault", "4007:5", NO_SOURCES, INVERTER_STOP),
    Condition("PV input fault", "4007:6", "4007:6", INVERTER_STOP),
    Condition("Inverter hardware overcurrent", "4007:11", "4007:11", INVERTER_STOP),
    Condition("Neutral to earth voltage fault", "4007:14", "4007:14", INVERTER_STOP),
    Condition("DRM0 fault", "4007:15", "4007:15"),
    Condition("Fan 1 fault", "4007:16", "4007:16"),
    Condition("Fan 2 fault", "4007:17", "4007:17"),
    Condition("Fan 3 fault", "4007:18", "4007:18"),
    Condition("Fan 4 fault", "4007:19", "4007:19"),
    Condition("Arc fault", "4007:20", "4007:20", INVERTER_STOP),
    Condition("PV software overcurrent", "4007:21", "4007:21", INVERTER_STOP),
    Condition("Battery port overvoltage", "4007:22", "4007:22", INVERTER_STOP),
    Condition("Battery port overcurrent", "4007:23", "4007:23", INVERTER_STOP),
    Condition("Battery charge voltage high", "4007:24", "4007:24", INVERTER_STOP),
    Condition("Battery port overload", "4007:25", "4007:25", INVERTER_STOP),
    Condition("Battery soft start timeout", "4007:26", "4007:26", INVERTER_STOP),
    Condition("Output overload", "4007:27", "4007:27", INVERTER_STOP),
    Condition("Battery open circuit", "4007:28", "4007:28", INVERTER_STOP),
    Condition("Battery discharge voltage low", "4007:29", "4007:29", INVERTER_STOP),
    Condition("Authorisation expired", "4007:30", "4007:30"),
    Condition("Display board communication lost", "4007:31", "4007:31"),
    Condition("Relay fault", "4009:0", "4009:0", INVERTER_STOP),
    Condition("Controller memory fault", "4009:1", "4009:1", INVERTER_STOP),
    Condition("Over temperature", "4009:2", "4009:2", INVERTER_STOP),
    Condition("Under temperature", "4009:3", "4009:3", INVERTER_STOP),
    Condition("Leakage current sensor fault", "4009:5", "4009:5", INVERTER_STOP),
    Condition("DC injection sensor fault", "4009:6", "4009:6", INVERTER_STOP),
    Condition("Current sensor fault", "4009:7", "4009:7", INVERTER_STOP),
    Condition(
        "Grid 10-minute average overvoltage", "4009:14", "4009:14", INVERTER_STOP
    ),
    Condition("Off-grid output undervoltage", "4009:15", "4009:15", INVERTER_STOP),
    Condition("Grid phase R DC voltage high", "4009:20", "4009:20", INVERTER_STOP),
    Condition("Grid phase S DC voltage high", "4009:21", "4009:21", INVERTER_STOP),
    Condition("Grid phase T DC voltage high", "4009:22", "4009:22", INVERTER_STOP),
    Condition("Leakage current fault", "4009:26", "4009:26", INVERTER_STOP),
    Condition("Grid phase R DC injection high", "4009:27", "4009:27", INVERTER_STOP),
    Condition("Grid phase S DC injection high", "4009:28", "4009:28", INVERTER_STOP),
    Condition("Grid phase T DC injection high", "4009:29", "4009:29", INVERTER_STOP),
    Condition("Insulation fault", "4009:30", "4009:30", INVERTER_STOP),
    Condition("DC bus voltage imbalance", "4009:31", "4009:31", INVERTER_STOP),
)

BATTERY_REGISTER = REGISTERS[Equipment.BATTERY][0]
# HS3 0x400B, the BMS table. The H2 document has no table, so every bit is reserved.
BATTERY_BITS = {
    0: "Battery BMS internal communication lost",
    1: "Battery pack addressing fault",
    2: "Battery discharge overcurrent",
    3: "Battery charge overcurrent",
    4: "Battery total voltage low",
    5: "Battery total voltage high",
    6: "Battery cell undervoltage",
    7: "Battery cell overvoltage",
    8: "Battery BMS hardware fault",
    9: "Battery too cold to charge",
    10: "Battery too hot to charge",
    11: "Battery too cold to discharge",
    12: "Battery too hot to discharge",
    13: "Battery BMS relay fault",
    14: "Battery pre-charge fault",
    15: "Battery BMS insulation fault",
    16: "Battery BMS manufacturer incompatible",
    17: "Battery cell manufacturer mismatch",
    18: "Battery cell mismatch",
    19: "Battery voltage level mismatch",
    20: "Battery circuit breaker open",
    21: "Battery cell temperature difference too large",
    22: "Battery cell voltage difference too large, level 2",
    23: "Battery cell voltage difference too large, level 1",
    24: "Battery cell over temperature",
    25: "Battery short circuit",
    26: "Battery total voltage matching failure",
    27: "Battery system locked",
    28: "Battery fuse fault",
    29: "Battery charging port overvoltage",
}
BATTERY_EFFECTS = {
    4: NO_DISCHARGE,
    5: NO_CHARGE,
    6: NO_DISCHARGE,
    7: NO_CHARGE,
    9: NO_CHARGE,
    10: NO_CHARGE,
    11: NO_DISCHARGE,
    12: NO_DISCHARGE,
}

EV_REGISTER = REGISTERS[Equipment.EV_CHARGER][0]
# HS3 table 4.10.1 laid out as bit = 8 x byte + row. The second register is reserved.
EV_BITS = {
    0: "EV charger relay over temperature",
    1: "EV charger overload",
    2: "EV charger AC overvoltage",
    3: "EV charger AC undervoltage",
    4: "EV charger AC overcurrent",
    5: "EV charger AC overfrequency",
    6: "EV charger AC underfrequency",
    7: "EV charger DC residual current fault A",
    8: "EV charger emergency stop",
    9: "EV charger under temperature",
    10: "EV charger AC residual current",
    11: "EV charger input terminal over temperature",
    12: "EV charger Bluetooth fault",
    13: "EV charger DC residual current fault B",
    14: "EV charger relay fault",
    15: "EV charger grounding fault",
    16: "EV charger phase sequence fault",
    17: "EV charger RCD circuit fault",
    18: "EV charger RS485 communication timeout",
    19: "EV charger electricity supply fault",
    22: "EV charger meter fault",
    23: "EV charger control pilot fault (below 2 V)",
    29: "EV charger connector lock fault",
    30: "EV charger connector current fault",
    31: "EV charger DC residual current fault C",
}


def _reserved(*, equipment: Equipment, bit: FaultBit) -> FaultEntry:
    return FaultEntry(
        equipment=equipment,
        bit=bit,
        name=f"{hex_address(address=bit.register)} bit {bit.bit} reserved",
        effects=NO_EFFECT,
        reserved=True,
    )


def _entries(
    *,
    equipment: Equipment,
    named: dict[FaultBit, tuple[str, frozenset[Effect]]],
) -> list[FaultEntry]:
    """Every bit of the equipment's registers, named where the document names it."""
    entries = []
    for register in REGISTERS[equipment]:
        for bit_number in range(BITS_PER_REGISTER):
            bit = FaultBit(register=register, bit=bit_number)
            if bit not in named:
                entries.append(_reserved(equipment=equipment, bit=bit))
                continue
            name, effects = named[bit]
            entries.append(
                FaultEntry(equipment=equipment, bit=bit, name=name, effects=effects)
            )
    return entries


def _inverter_entries(*, model: str) -> list[FaultEntry]:
    named = {}
    for condition in INVERTER_CONDITIONS:
        for bit in condition.sources(model=model):
            named[bit] = (condition.name, condition.effects)
    return _entries(equipment=Equipment.INVERTER, named=named)


def _battery_entries(*, model: str) -> list[FaultEntry]:
    named = {}
    if model == HS3:
        named = {
            FaultBit(register=BATTERY_REGISTER, bit=bit): (
                name,
                BATTERY_EFFECTS.get(bit, BATTERY_STOP),
            )
            for bit, name in BATTERY_BITS.items()
        }
    return _entries(equipment=Equipment.BATTERY, named=named)


def _ev_entries() -> list[FaultEntry]:
    named = {
        FaultBit(register=EV_REGISTER, bit=bit): (name, CHARGER_STOP)
        for bit, name in EV_BITS.items()
    }
    return _entries(equipment=Equipment.EV_CHARGER, named=named)


def build_fault_map(*, scenario: Scenario) -> FaultMap:
    """The fault bits of the equipment this scenario fits, and its battery packs."""
    model = scenario.device.model
    entries = _inverter_entries(model=model.name)
    if scenario.battery.modules:
        entries += _battery_entries(model=model.name)
    if scenario.ev_charger.installed:
        entries += _ev_entries()
    return FaultMap(
        entries=tuple(entries),
        pack_count=min(scenario.battery.modules, model.max_fault_packs),
    )
