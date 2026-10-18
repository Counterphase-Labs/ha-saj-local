from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import StrEnum
from functools import cached_property
from typing import TYPE_CHECKING

from .codec import (
    NUMERIC_ENCODINGS,
    SIGNED_ENCODINGS,
    WORD_BITS,
    WRITABLE_ENCODINGS,
    BitRange,
    Encoding,
    Format,
    Range,
    scaled,
)
from .models import Equipment
from .models.faults import ALL_BITS

if TYPE_CHECKING:
    from collections.abc import Iterator, Mapping

FIRST_INDEX = 1
INVALID_VERSION = 0xFFFF
NO_LIMIT = 0xFFFF
EMPTY_TEXT = 0
SOC_RANGE = Range(minimum=0, maximum=100)
SWITCH_RANGE = Range(minimum=0, maximum=1)
DAYS_RANGE = Range(minimum=0, maximum=127)
PERCENT_RANGE = Range(minimum=0, maximum=100)
SIGNED_PERCENT_RANGE = Range(minimum=-100, maximum=100)
POWER_LIMIT_RANGE = Range(minimum=0, maximum=110)
WORD_RANGE = Range(minimum=0, maximum=65535)
LEAD_ACID_VOLTAGE_RANGE = Range(minimum=85, maximum=450)
FORCED_CHARGE_POWER_RANGE = Range(minimum=10, maximum=100)
LEAD_ACID_CURRENT_RANGE = Range(minimum=0, maximum=30)
PV_VOLTAGE_RANGE = Range(minimum=0, maximum=650)
MPPT_VOLTAGE_RANGE = Range(minimum=90, maximum=500)
EV_POWER_RANGE = Range(minimum=0, maximum=11000)
PHASE_COUNT = 3
STRING_COUNT = 4
PACK_COUNT = 4
IDENTITY_PACK_COUNT = 5
IDENTITY_PACK_STRIDE = 20
IDENTITY_SERIAL_WORDS = 8
SLOT_COUNT = 7
SLOT_STRIDE = 3
EV_SLOT_STRIDE = 5
ADDRESS_WORDS = 8
PERIOD_STRIDE = 2
ENERGY_PERIODS = ("today", "month", "year", "total")
ENERGY_STRIDE = len(ENERGY_PERIODS) * PERIOD_STRIDE
CORE_PERIODS = frozenset({"today", "total"})


class Quantity(StrEnum):
    POWER = "power"
    APPARENT_POWER = "apparent_power"
    REACTIVE_POWER = "reactive_power"
    VOLTAGE = "voltage"
    CURRENT = "current"
    FREQUENCY = "frequency"
    POWER_FACTOR = "power_factor"
    ENERGY = "energy"
    TEMPERATURE = "temperature"
    RESISTANCE = "resistance"
    DURATION = "duration"
    PERCENTAGE = "percentage"
    STATE_OF_CHARGE = "state_of_charge"
    CAPACITY = "capacity"
    COUNT = "count"
    CODE = "code"
    VERSION = "version"
    TEXT = "text"
    ADDRESS = "address"
    TIMESTAMP = "timestamp"
    TIME_OF_DAY = "time_of_day"
    WEEKDAYS = "weekdays"
    TOGGLE = "toggle"
    PROBLEM = "problem"


class Access(StrEnum):
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    WRITE_ONLY = "write_only"


class EntityKind(StrEnum):
    SENSOR = "sensor"
    BINARY_SENSOR = "binary_sensor"
    NUMBER = "number"
    SELECT = "select"
    SWITCH = "switch"
    TIME = "time"
    TEXT = "text"
    BUTTON = "button"


class Category(StrEnum):
    CONFIGURATION = "config"
    DIAGNOSTIC = "diagnostic"


class Unit(StrEnum):
    WATT = "W"
    VOLT_AMPERE = "VA"
    VAR = "var"
    VOLT = "V"
    MILLIVOLT = "mV"
    AMPERE = "A"
    MILLIAMPERE = "mA"
    HERTZ = "Hz"
    KILOWATT_HOUR = "kWh"
    PERCENT = "%"
    CELSIUS = "°C"
    HOUR = "h"
    SECOND = "s"
    MINUTE = "min"
    KILOOHM = "kΩ"
    AMPERE_HOUR = "Ah"


class Role(StrEnum):
    NONE = "none"
    PHASE = "phase"
    STRING = "string"
    PACK = "pack"


class Operation(StrEnum):
    SUM = "sum"
    WORDS = "words"
    ANY_BIT = "any_bit"


@dataclass(frozen=True)
class Combination:
    operation: Operation
    sources: tuple[str, ...]
    masks: Mapping[str, int] = field(default_factory=dict)

    def mask_of(self, *, source: str) -> int:
        return self.masks.get(source, ALL_BITS)


@dataclass(frozen=True)
class Definition:
    key: str
    quantity: Quantity
    encoding: Encoding
    kind: EntityKind = EntityKind.SENSOR
    access: Access = Access.READ_ONLY
    scale: float = 1
    unit: Unit | None = None
    invalid: frozenset[int] = frozenset()
    valid_range: Range | None = None
    options: Mapping[int, str] | None = None
    range: Range | None = None
    core: bool = False
    control: bool = False
    phases: int = 1
    strings: int = 1
    packs: int = 0
    words: int | None = None
    field: BitRange | None = None
    combination: Combination | None = None
    command_value: int | None = None
    equipment: Equipment | None = None
    inverted: bool = False
    exposed: bool = True
    summary: bool = False
    private: bool = False

    @cached_property
    def format(self) -> Format:
        return Format(
            encoding=self.encoding,
            scale=self.scale,
            invalid=self.invalid,
            field=self.field,
            valid_range=self.valid_range,
            words=self.words,
            inverted=self.inverted,
        )

    @property
    def word_count(self) -> int:
        return self.format.word_count

    @property
    def writable(self) -> bool:
        return self.access is not Access.READ_ONLY

    @property
    def readable(self) -> bool:
        return self.access is not Access.WRITE_ONLY

    @property
    def category(self) -> Category | None:
        if (
            self.quantity in DIAGNOSTIC_QUANTITIES
            or self.key in COMMISSIONING_KEYS
            or self.key in HEADER_DERIVED_KEYS
        ):
            return Category.DIAGNOSTIC
        if self.quantity is Quantity.PROBLEM:
            return None if self.summary else Category.DIAGNOSTIC
        if self.writable:
            return Category.CONFIGURATION
        return None

    @property
    def settable_range(self) -> Range | None:
        if self.range is not None:
            return self.range
        if self.encoding not in NUMERIC_ENCODINGS:
            return None
        bit_count = WORD_BITS * self.word_count
        if self.encoding in SIGNED_ENCODINGS:
            lowest, highest = -(1 << (bit_count - 1)), (1 << (bit_count - 1)) - 1
        else:
            lowest, highest = 0, (1 << bit_count) - 1
        return Range(
            minimum=scaled(raw=lowest, scale=self.scale),
            maximum=scaled(raw=highest, scale=self.scale),
        )

    @property
    def has_writable_form(self) -> bool:
        return (
            self.command_value is not None
            or self.range is not None
            or self.options is not None
            or self.encoding in WRITABLE_ENCODINGS
        )


@dataclass(frozen=True)
class Member:
    offset: int
    definition: Definition
    core_first_only: bool = False
    field_follows_index: bool = False


@dataclass(frozen=True)
class Family:
    name: str
    stem: str
    base: int
    members: tuple[Member, ...]
    stride: int = 0
    first_index: int = FIRST_INDEX
    count: int = 1
    role: Role = Role.NONE
    equipment: Equipment | None = None

    @property
    def indices(self) -> range:
        return range(self.first_index, self.first_index + self.count)

    def definitions(self) -> Iterator[Definition]:
        for index in self.indices:
            for member in self.members:
                yield self._definition(index=index, member=member)

    def addresses(self) -> Iterator[tuple[str, int]]:
        for index in self.indices:
            row = self.base + (index - self.first_index) * self.stride
            for member in self.members:
                yield self._key(index=index, member=member), row + member.offset

    def _key(self, *, index: int, member: Member) -> str:
        return f"{self.stem.format(index=index)}_{member.definition.key}"

    def _definition(self, *, index: int, member: Member) -> Definition:
        definition = replace(
            member.definition, key=self._key(index=index, member=member)
        )
        if self.equipment is not None:
            definition = replace(definition, equipment=self.equipment)
        if member.core_first_only and index != self.first_index:
            definition = replace(definition, core=False)
        if self.role is Role.PHASE:
            definition = replace(definition, phases=index)
        if self.role is Role.STRING:
            definition = replace(definition, strings=index)
        if self.role is Role.PACK:
            definition = replace(definition, packs=index)
        if member.field_follows_index and definition.field is not None:
            shift = index - self.first_index
            definition = replace(
                definition,
                field=BitRange(
                    first=definition.field.first + shift,
                    last=definition.field.last + shift,
                ),
            )
        return definition


DIAGNOSTIC_QUANTITIES = frozenset({Quantity.VERSION, Quantity.ADDRESS, Quantity.TEXT})
ETHERNET_ADDRESS_NAMES = (
    "ip_address",
    "subnet_mask",
    "gateway",
    "dns_primary",
    "dns_secondary",
)
COMMISSIONING_KEYS = frozenset(
    {
        "ethernet_mode",
        "meter_configuration",
        "meter_address",
        "rs485_address",
        "rs485_baud_rate",
        "rs485_slave_address",
        "rs485_slave_baud_rate",
        "battery_protocol",
        "ev_address",
        "ev_baud_rate",
        "ev_charger_count",
        "ev_communication_timeout",
        "ev_port_mode",
        "ev_port_address",
        "reverse_flow_mode",
        "fcas_frequency_hysteresis",
        "lead_acid_off_grid_discharge_cutoff_voltage",
        "lead_acid_charge_cutoff_voltage",
        "lead_acid_on_grid_discharge_cutoff_voltage",
        "lead_acid_high_voltage_protection",
        "lead_acid_low_voltage_warning",
        "lead_acid_discharge_current_limit",
        "lead_acid_charge_current_limit",
        "lead_acid_capacity",
        "lead_acid_float_charge_voltage",
        "lead_acid_equalising_charge_voltage",
        "bms_update_id",
        "bms_update_mode",
        "parallel_role",
        "parallel_number",
        "parallel_configured_mode",
        "battery_input_mode",
        "pv_input_mode",
        "off_grid_output_voltage",
        "off_grid_output_frequency",
        "motor_enable",
        "machine_model",
        "rated_power",
        "function_flags_1",
        "function_flags_2",
        "max_dc_current_component",
        "max_dc_voltage_component",
        "insulation_resistance_limit",
        "max_leakage_current",
        "grid_type",
        "pv_start_voltage",
        "pv_shutdown_voltage",
        "mppt_voltage_high",
        "mppt_voltage_low",
        "mppt_scan_time",
    }
)
HEADER_DERIVED_KEYS = frozenset({"settings_sequence"})
ETHERNET_ADDRESS_KEYS = frozenset(f"ethernet_{name}" for name in ETHERNET_ADDRESS_NAMES)
PROTECTED_KEYS = COMMISSIONING_KEYS | HEADER_DERIVED_KEYS | ETHERNET_ADDRESS_KEYS


OPERATING_MODE_OPTIONS = {
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
APPLICATION_MODE_OPTIONS = {0: "self_use", 1: "time_of_use", 2: "backup"}
EXPORT_LIMIT_MODE_OPTIONS = {
    0: "off",
    1: "total_power",
    2: "phase_current",
    3: "phase_power",
}
TIME_OF_USE_IDLE_MODE_OPTIONS = {0: "standby", 1: "self_use"}
LED_MODE_OPTIONS = {0: "all_off", 1: "outer_ring_on", 2: "inner_ring_on", 3: "all_on"}
BATTERY_PROTOCOL_OPTIONS = {0: "not_in_use", 24: "saj_bu3"}
METER_CONFIGURATION_OPTIONS = {
    0: "no_meter_or_ct",
    1: "single_phase_meter",
    2: "three_phase_three_wire_meter",
    3: "three_phase_four_wire_meter_on_single_phase_machine",
    10: "three_phase_four_wire_meter_grid_and_pv",
    11: "two_three_phase_three_wire_meters",
    12: "two_three_phase_four_wire_meters",
    13: "two_single_phase_meters",
    15: "single_phase_meter_with_two_ct_channels",
    20: "one_grid_ct",
    21: "grid_and_pv_cts",
    42: "dual_circuit_three_phase_four_wire_meter_with_six_ct_channels",
}
BAUD_RATE_OPTIONS = {
    0: "115200",
    1: "57600",
    2: "38400",
    3: "19200",
    4: "9600",
    5: "4800",
    6: "2400",
    7: "1200",
}
METER_STATUS_OPTIONS = {0: "offline", 1: "online"}
ETHERNET_MODE_OPTIONS = {0: "manual", 1: "automatic"}
EV_MODE_OPTIONS = {
    0: "disabled",
    1: "standard",
    2: "time_based",
    3: "pv_surplus",
    4: "ems",
}
EV_STATUS_OPTIONS = {
    1: "idle",
    2: "ready",
    3: "charging",
    4: "charger_suspended",
    5: "vehicle_suspended",
    6: "complete",
}
EV_REMOTE_CONTROL_OPTIONS = {0: "shutdown", 1: "on"}
EV_PORT_MODE_OPTIONS = {0: "invalid", 1: "host", 2: "modbus_slave"}
EV_SLOT_MODE_OPTIONS = {0: "not_set", 1: "standard", 2: "pv_mode"}
OFF_GRID_MODE_OPTIONS = {0: "off", 1: "on"}
INVERTER_STOP_OPTIONS = {0: "running", 1: "stopped"}
GRID_TYPE_OPTIONS = {
    0: "single_phase",
    1: "split_phase",
    2: "three_phase_three_wire",
    3: "three_phase_four_wire",
}
REVERSE_FLOW_MODE_OPTIONS = {0: "off", 1: "master", 2: "slave"}
PARALLEL_CONFIGURED_MODE_OPTIONS = {
    0: "not_parallel",
    1: "on_grid",
    2: "off_grid",
    3: "on_and_off_grid",
}
BATTERY_INPUT_MODE_OPTIONS = {1: "independent", 2: "parallel"}
PV_INPUT_MODE_OPTIONS = {0: "automatic", 1: "independent", 2: "parallel"}
BATTERY_TYPE_OPTIONS = {1: "50_ah", 2: "80_ah", 3: "100_ah"}

SLOT_ENABLED_FIELD = BitRange(first=0, last=0)
SLOT_POWER_FIELD = BitRange(first=0, last=7)
SLOT_DAYS_FIELD = BitRange(first=8, last=14)
EV_SLOT_MODE_FIELD = BitRange(first=0, last=2)
EV_SLOT_GRID_CHARGING_FIELD = BitRange(first=3, last=3)
EV_SLOT_BATTERY_DISCHARGE_FIELD = BitRange(first=4, last=4)
EV_MINIMUM_CURRENT_CHARGING_FIELD = BitRange(first=2, last=2)
BUZZER_FIELD = BitRange(first=0, last=0)
EV_EMS_CHARGING_FIELD = BitRange(first=0, last=0)
EV_EMS_PHASE_MODE_FIELD = BitRange(first=1, last=2)
EV_EMS_PHASE_MODE_OPTIONS = {0: "three_phase", 1: "single_phase"}
EV_EMS_CHARGE_CURRENT_RANGE = Range(minimum=6, maximum=32)
EMS_CONTROL_BITS = {
    "ems_inverter_control": 0,
    "ems_battery_control": 1,
    "ems_inverter_control_with_timeout_exit": 3,
    "ems_grid_control": 5,
}
EMS_CONTROL_EQUIPMENT = {"ems_battery_control": Equipment.BATTERY}
FAULT_PREFIXES: Mapping[Equipment | None, str] = {
    None: "inverter",
    Equipment.BATTERY: "battery",
    Equipment.EV_CHARGER: "ev",
}
PARALLEL_POWER_SUBJECTS = ("pv", "battery", "grid", "load", "backup_load", "grid_load")
PARALLEL_CORE_POWER_SUBJECTS = frozenset({"pv", "battery", "grid", "load"})


def _measure(
    *,
    key: str,
    quantity: Quantity,
    encoding: Encoding,
    scale: float = 1,
    unit: Unit | None = None,
) -> Definition:
    return Definition(
        key=key, quantity=quantity, encoding=encoding, scale=scale, unit=unit
    )


def _meter_power(*, meter: str, equipment: Equipment) -> Definition:
    return Definition(
        key=f"meter_{meter}_power",
        equipment=equipment,
        quantity=Quantity.POWER,
        encoding=Encoding.I32,
        unit=Unit.WATT,
        core=True,
        combination=Combination(
            operation=Operation.SUM,
            sources=tuple(
                f"meter_{meter}_l{phase}_power" for phase in range(1, PHASE_COUNT + 1)
            ),
        ),
    )


def _core(*, definition: Definition) -> Definition:
    return replace(definition, core=True)


def _problem(
    *, key: str, equipment: Equipment | None = None, summary: bool = False
) -> Definition:
    return Definition(
        key=key,
        equipment=equipment,
        quantity=Quantity.PROBLEM,
        kind=EntityKind.BINARY_SENSOR,
        encoding=Encoding.U16,
        core=True,
        summary=summary,
    )


def _fault_word(*, key: str, equipment: Equipment | None) -> Definition:
    return Definition(
        key=key,
        equipment=equipment,
        quantity=Quantity.CODE,
        encoding=Encoding.U32,
        exposed=False,
    )


def fault_summary_key(*, equipment: Equipment | None) -> str:
    return f"{FAULT_PREFIXES[equipment]}_fault"


def fault_unrecognised_key(*, equipment: Equipment | None) -> str:
    return f"{fault_summary_key(equipment=equipment)}_unrecognised"


def _voltage(*, key: str = "voltage") -> Definition:
    return _measure(
        key=key,
        quantity=Quantity.VOLTAGE,
        encoding=Encoding.U16,
        scale=0.1,
        unit=Unit.VOLT,
    )


def _current(*, encoding: Encoding = Encoding.I16, scale: float = 0.01) -> Definition:
    return _measure(
        key="current",
        quantity=Quantity.CURRENT,
        encoding=encoding,
        scale=scale,
        unit=Unit.AMPERE,
    )


def _frequency() -> Definition:
    return _measure(
        key="frequency",
        quantity=Quantity.FREQUENCY,
        encoding=Encoding.U16,
        scale=0.01,
        unit=Unit.HERTZ,
    )


def _power(*, key: str = "power", encoding: Encoding = Encoding.I16) -> Definition:
    return _measure(key=key, quantity=Quantity.POWER, encoding=encoding, unit=Unit.WATT)


def _apparent_power() -> Definition:
    return _measure(
        key="apparent_power",
        quantity=Quantity.APPARENT_POWER,
        encoding=Encoding.U16,
        unit=Unit.VOLT_AMPERE,
    )


def _power_factor() -> Definition:
    return _measure(
        key="power_factor",
        quantity=Quantity.POWER_FACTOR,
        encoding=Encoding.I16,
        scale=0.001,
    )


def _state_of_charge() -> Definition:
    return _measure(
        key="soc",
        quantity=Quantity.STATE_OF_CHARGE,
        encoding=Encoding.U16,
        scale=0.01,
        unit=Unit.PERCENT,
    )


def _temperature() -> Definition:
    return _measure(
        key="temperature",
        quantity=Quantity.TEMPERATURE,
        encoding=Encoding.I16,
        scale=0.1,
        unit=Unit.CELSIUS,
    )


def _energy_period(*, period: str, core: bool) -> Definition:
    return replace(
        _measure(
            key=period,
            quantity=Quantity.ENERGY,
            encoding=Encoding.U32,
            scale=0.01,
            unit=Unit.KILOWATT_HOUR,
        ),
        core=core and period in CORE_PERIODS,
    )


def _energy(
    *,
    name: str,
    stem: str,
    base: int,
    core: bool = False,
    equipment: Equipment | None = None,
) -> Family:
    return Family(
        name=name,
        stem=stem,
        base=base,
        equipment=equipment,
        members=tuple(
            Member(
                offset=position * PERIOD_STRIDE,
                definition=_energy_period(period=period, core=core),
            )
            for position, period in enumerate(ENERGY_PERIODS)
        ),
        stride=ENERGY_STRIDE,
    )


def _phased(
    *, family: Family, first_index: int = FIRST_INDEX, count: int = PHASE_COUNT
) -> Family:
    return replace(family, first_index=first_index, count=count, role=Role.PHASE)


def _stringed(
    *, family: Family, first_index: int = FIRST_INDEX, count: int = STRING_COUNT
) -> Family:
    return replace(family, first_index=first_index, count=count, role=Role.STRING)


GRID_PHASE = _phased(
    family=Family(
        name="grid_phase",
        stem="grid_l{index}",
        base=0x4031,
        stride=7,
        members=(
            Member(offset=0, definition=_core(definition=_voltage())),
            Member(offset=1, definition=_current()),
            Member(
                offset=2,
                definition=_core(definition=_frequency()),
                core_first_only=True,
            ),
            Member(
                offset=3,
                definition=_measure(
                    key="dc_current",
                    quantity=Quantity.CURRENT,
                    encoding=Encoding.I16,
                    unit=Unit.MILLIAMPERE,
                ),
            ),
            Member(offset=4, definition=_power()),
            Member(offset=5, definition=_apparent_power()),
            Member(offset=6, definition=_power_factor()),
        ),
    )
)
INVERTER_PHASE = _phased(
    family=Family(
        name="inverter_phase",
        stem="inverter_l{index}",
        base=0x4046,
        stride=5,
        members=(
            Member(offset=0, definition=_voltage()),
            Member(offset=1, definition=_current()),
            Member(offset=2, definition=_frequency()),
            Member(offset=3, definition=_power()),
            Member(offset=4, definition=_apparent_power()),
        ),
    )
)
OUTPUT_LINE_MEMBERS = (
    Member(offset=0, definition=_voltage()),
    Member(offset=1, definition=_current(encoding=Encoding.U16)),
    Member(offset=2, definition=_frequency()),
)
BACKUP_PHASE = _phased(
    family=Family(
        name="backup_phase",
        stem="backup_l{index}",
        base=0x4055,
        stride=6,
        members=(
            *OUTPUT_LINE_MEMBERS,
            Member(
                offset=3,
                definition=_measure(
                    key="dc_voltage",
                    quantity=Quantity.VOLTAGE,
                    encoding=Encoding.I16,
                    unit=Unit.MILLIVOLT,
                ),
            ),
            Member(offset=4, definition=_power(encoding=Encoding.U16)),
            Member(offset=5, definition=_apparent_power()),
        ),
    )
)
GRID_OUTPUT_FIRST_PHASE = Family(
    name="grid_output_first_phase",
    stem="grid_output_l{index}",
    base=0x408D,
    members=(
        *OUTPUT_LINE_MEMBERS,
        Member(offset=3, definition=_power(encoding=Encoding.U16)),
    ),
)
GRID_OUTPUT_OTHER_PHASES = _phased(
    family=Family(
        name="grid_output_other_phases",
        stem="grid_output_l{index}",
        base=0x4091,
        stride=2,
        members=(
            Member(offset=0, definition=_voltage()),
            Member(offset=1, definition=_power(encoding=Encoding.U16)),
        ),
    ),
    first_index=2,
    count=PHASE_COUNT - 1,
)
PV_STRING = _stringed(
    family=Family(
        name="pv_string",
        stem="pv{index}",
        base=0x4071,
        stride=3,
        members=(
            Member(offset=0, definition=_core(definition=_voltage())),
            Member(
                offset=1,
                definition=_core(definition=_current(encoding=Encoding.U16)),
            ),
            Member(
                offset=2,
                definition=_core(definition=_power(encoding=Encoding.U16)),
            ),
        ),
    )
)
PV_INSULATION = _stringed(
    family=Family(
        name="pv_insulation",
        stem="pv{index}_insulation",
        base=0x4013,
        stride=1,
        members=(
            Member(
                offset=0,
                definition=_measure(
                    key="resistance",
                    quantity=Quantity.RESISTANCE,
                    encoding=Encoding.U16,
                    unit=Unit.KILOOHM,
                ),
            ),
        ),
    )
)
PV_ENERGY = _energy(name="pv_energy", stem="pv_energy", base=0x40BF, core=True)
BATTERY_CHARGE_ENERGY = _energy(
    name="battery_charge_energy",
    stem="battery_charge_energy",
    base=0x40C7,
    core=True,
    equipment=Equipment.BATTERY,
)
BATTERY_DISCHARGE_ENERGY = _energy(
    name="battery_discharge_energy",
    stem="battery_discharge_energy",
    base=0x40CF,
    core=True,
    equipment=Equipment.BATTERY,
)
INVERTER_ENERGY = _energy(name="inverter_energy", stem="inverter_energy", base=0x40D7)
LOAD_ENERGY = _energy(name="load_energy", stem="load_energy", base=0x40DF, core=True)
BACKUP_LOAD_ENERGY = _energy(
    name="backup_load_energy", stem="backup_load_energy", base=0x40E7, core=True
)
GRID_EXPORT_ENERGY = _energy(
    name="grid_export_energy", stem="grid_export_energy", base=0x416F, core=True
)
GRID_IMPORT_ENERGY = _energy(
    name="grid_import_energy", stem="grid_import_energy", base=0x4167, core=True
)
GRID_FIRST_PHASE_EXPORT_ENERGY = _energy(
    name="grid_first_phase_export_energy",
    stem="grid_l{index}_export_energy",
    base=0x40EF,
)
GRID_FIRST_PHASE_IMPORT_ENERGY = _energy(
    name="grid_first_phase_import_energy",
    stem="grid_l{index}_import_energy",
    base=0x40F7,
)
GRID_OTHER_PHASES_EXPORT_ENERGY = _phased(
    family=_energy(
        name="grid_other_phases_export_energy",
        stem="grid_l{index}_export_energy",
        base=0x4147,
    ),
    first_index=2,
    count=PHASE_COUNT - 1,
)
GRID_OTHER_PHASES_IMPORT_ENERGY = _phased(
    family=_energy(
        name="grid_other_phases_import_energy",
        stem="grid_l{index}_import_energy",
        base=0x4157,
    ),
    first_index=2,
    count=PHASE_COUNT - 1,
)
PV_OTHER_STRINGS_ENERGY = _stringed(
    family=_energy(
        name="pv_other_strings_energy", stem="pv{index}_energy", base=0x4137
    ),
    first_index=2,
    count=STRING_COUNT - 2,
)
PARALLEL_ENERGY_BASE = 0x4215
PARALLEL_ENERGY_SUBJECTS = (
    "pv",
    "battery_charge",
    "battery_discharge",
    "grid_l1_export",
    "grid_l2_export",
    "grid_l3_export",
    "grid_l1_import",
    "grid_l2_import",
    "grid_l3_import",
    "load",
    "grid_import",
    "grid_export",
    "pv_meter",
)
PARALLEL_ENERGY = tuple(
    _energy(
        name=f"parallel_{subject}_energy",
        stem=f"parallel_{subject}_energy",
        base=PARALLEL_ENERGY_BASE + position * ENERGY_STRIDE,
        equipment=Equipment.PARALLEL,
    )
    for position, subject in enumerate(PARALLEL_ENERGY_SUBJECTS)
)
AVERAGE_TOTAL_BASES = {
    "grid": 0x513E,
    "inverter": 0x514F,
    "load": 0x5160,
    "grid_load": 0x5171,
    "backup": 0x5182,
    "generator": 0x51A5,
}
AVERAGE_TOTAL_WORDS = 2
AVERAGE_PHASE_STRIDE = 5
AVERAGE_LINE_MEMBERS = (
    Member(offset=0, definition=_power(encoding=Encoding.I32)),
    Member(offset=2, definition=_voltage()),
    Member(offset=3, definition=_current()),
)
AVERAGE_TOTALS = tuple(
    Family(
        name=f"average_{subject}",
        stem=f"average_{subject}",
        base=base,
        members=(Member(offset=0, definition=_power(encoding=Encoding.I32)),),
    )
    for subject, base in AVERAGE_TOTAL_BASES.items()
)
AVERAGE_PHASES = tuple(
    _phased(
        family=Family(
            name=f"average_{subject}_phase",
            stem=f"average_{subject}_l{{index}}",
            base=base + AVERAGE_TOTAL_WORDS,
            stride=AVERAGE_PHASE_STRIDE,
            members=(*AVERAGE_LINE_MEMBERS, Member(offset=4, definition=_frequency())),
        )
    )
    for subject, base in AVERAGE_TOTAL_BASES.items()
)
AVERAGE_PV_STRING = _stringed(
    family=Family(
        name="average_pv_string",
        stem="average_pv{index}",
        base=0x5195,
        stride=4,
        members=(
            Member(offset=0, definition=_voltage()),
            Member(offset=1, definition=_current()),
            Member(offset=2, definition=_power(encoding=Encoding.U32)),
        ),
    ),
    count=2,
)
AVERAGE_BATTERY_PACK = Family(
    name="average_battery_pack",
    equipment=Equipment.BATTERY,
    stem="average_battery_pack{index}",
    base=0x51B9,
    members=(
        *AVERAGE_LINE_MEMBERS,
        Member(offset=4, definition=_state_of_charge()),
        Member(offset=5, definition=_temperature()),
    ),
)
BATTERY_PACK = Family(
    name="battery_pack",
    equipment=Equipment.BATTERY,
    stem="battery_pack{index}",
    base=0xA00C,
    stride=6,
    count=PACK_COUNT,
    role=Role.PACK,
    members=(
        Member(offset=0, definition=_state_of_charge()),
        Member(
            offset=1,
            definition=_measure(
                key="soh",
                quantity=Quantity.PERCENTAGE,
                encoding=Encoding.U16,
                scale=0.01,
                unit=Unit.PERCENT,
            ),
        ),
        Member(offset=2, definition=_voltage()),
        Member(offset=3, definition=_current()),
        Member(offset=4, definition=_temperature()),
        Member(
            offset=5,
            definition=_measure(
                key="cycles", quantity=Quantity.COUNT, encoding=Encoding.U16
            ),
        ),
    ),
)
BATTERY_PACK_DISCHARGED_ENERGY = Family(
    name="battery_pack_discharged_energy",
    equipment=Equipment.BATTERY,
    stem="battery_pack{index}",
    base=0xA02A,
    stride=2,
    count=PACK_COUNT,
    role=Role.PACK,
    members=(
        Member(
            offset=0,
            definition=_measure(
                key="discharged_energy",
                quantity=Quantity.ENERGY,
                encoding=Encoding.U32,
                unit=Unit.KILOWATT_HOUR,
            ),
        ),
    ),
)
BATTERY_PACK_FAULTS = Family(
    name="battery_pack_faults",
    equipment=Equipment.BATTERY,
    stem="battery_pack{index}",
    base=0xA002,
    stride=2,
    count=PACK_COUNT,
    role=Role.PACK,
    members=(
        Member(offset=0, definition=_problem(key="fault")),
        Member(offset=1, definition=_problem(key="warning")),
    ),
)


def _pack_serial(*, key: str) -> Definition:
    return Definition(
        key=key,
        quantity=Quantity.TEXT,
        encoding=Encoding.TEXT,
        words=IDENTITY_SERIAL_WORDS,
        invalid=frozenset({EMPTY_TEXT}),
        private=True,
    )


def _pack_version(*, key: str) -> Definition:
    return Definition(
        key=key,
        quantity=Quantity.VERSION,
        encoding=Encoding.U16,
        scale=0.001,
        invalid=frozenset({INVALID_VERSION}),
    )


BATTERY_PACK_IDENTITY = Family(
    name="battery_pack_identity",
    equipment=Equipment.BATTERY,
    stem="battery_pack{index}",
    base=0x8E00,
    stride=IDENTITY_PACK_STRIDE,
    count=IDENTITY_PACK_COUNT,
    role=Role.PACK,
    members=(
        Member(
            offset=0,
            definition=Definition(
                key="bms_type", quantity=Quantity.CODE, encoding=Encoding.U16
            ),
        ),
        Member(offset=1, definition=_pack_serial(key="bms_serial_number")),
        Member(offset=9, definition=_pack_version(key="bms_software_version")),
        Member(offset=10, definition=_pack_version(key="bms_hardware_version")),
        Member(
            offset=11,
            definition=Definition(
                key="type",
                quantity=Quantity.CODE,
                encoding=Encoding.U16,
                options=BATTERY_TYPE_OPTIONS,
            ),
        ),
        Member(offset=12, definition=_pack_serial(key="serial_number")),
    ),
)
METER_PHASE_STRIDE = 6
METER_A_PHASE = _phased(
    family=Family(
        name="meter_a_phase",
        equipment=Equipment.METER_A,
        stem="meter_a_l{index}",
        base=0xA03D,
        stride=METER_PHASE_STRIDE,
        members=(
            Member(offset=0, definition=_voltage()),
            Member(offset=1, definition=_current()),
            Member(offset=2, definition=_power()),
            Member(offset=3, definition=_apparent_power()),
            Member(offset=4, definition=_power_factor()),
            Member(offset=5, definition=_frequency()),
        ),
    )
)
METER_B_PHASE = replace(
    METER_A_PHASE,
    name="meter_b_phase",
    equipment=Equipment.METER_B,
    stem="meter_b_l{index}",
    base=0xA054,
)
METER_A_POWER_HIGH_WORDS = _phased(
    family=Family(
        name="meter_a_power_high_words",
        equipment=Equipment.METER_A,
        stem="meter_a_l{index}",
        base=0xA066,
        stride=1,
        members=(Member(offset=0, definition=_power(key="power_high_word")),),
    )
)
METER_B_POWER_HIGH_WORDS = replace(
    METER_A_POWER_HIGH_WORDS,
    name="meter_b_power_high_words",
    equipment=Equipment.METER_B,
    stem="meter_b_l{index}",
    base=0xA069,
)
METER_A_REACTIVE_POWER = _phased(
    family=Family(
        name="meter_a_reactive_power",
        equipment=Equipment.METER_A,
        stem="meter_a_l{index}",
        base=0xA06C,
        stride=2,
        members=(
            Member(
                offset=0,
                definition=_measure(
                    key="reactive_power",
                    quantity=Quantity.REACTIVE_POWER,
                    encoding=Encoding.I32,
                    unit=Unit.VAR,
                ),
            ),
        ),
    )
)
METER_B_REACTIVE_POWER = replace(
    METER_A_REACTIVE_POWER,
    name="meter_b_reactive_power",
    equipment=Equipment.METER_B,
    stem="meter_b_l{index}",
    base=0xA072,
)
EV_PHASE = Family(
    name="ev_phase",
    equipment=Equipment.EV_CHARGER,
    stem="ev_l{index}",
    base=0x309E,
    stride=2,
    count=PHASE_COUNT,
    members=(
        Member(offset=0, definition=_voltage()),
        Member(offset=1, definition=_current(encoding=Encoding.U16, scale=0.1)),
    ),
)
ETHERNET_ADDRESSES = Family(
    name="ethernet_addresses",
    stem="ethernet",
    base=0x0F08,
    members=tuple(
        Member(
            offset=position * ADDRESS_WORDS,
            definition=Definition(
                key=name,
                quantity=Quantity.ADDRESS,
                kind=EntityKind.TEXT,
                access=Access.READ_WRITE,
                encoding=Encoding.ADDRESS_TEXT,
                words=ADDRESS_WORDS,
                private=True,
            ),
        )
        for position, name in enumerate(ETHERNET_ADDRESS_NAMES)
    ),
)


def _schedule_time(*, offset: int, key: str) -> Member:
    return Member(
        offset=offset,
        definition=Definition(
            key=key,
            quantity=Quantity.TIME_OF_DAY,
            kind=EntityKind.TIME,
            access=Access.READ_WRITE,
            encoding=Encoding.TIME_OF_DAY,
            control=True,
        ),
    )


def _slot_days(*, offset: int) -> Member:
    return Member(
        offset=offset,
        definition=Definition(
            key="days",
            quantity=Quantity.WEEKDAYS,
            kind=EntityKind.NUMBER,
            access=Access.READ_WRITE,
            encoding=Encoding.U16,
            field=SLOT_DAYS_FIELD,
            range=DAYS_RANGE,
            control=True,
        ),
    )


def _slot_switch(*, offset: int, key: str, field: BitRange, follows: bool) -> Member:
    return Member(
        offset=offset,
        definition=Definition(
            key=key,
            quantity=Quantity.TOGGLE,
            kind=EntityKind.SWITCH,
            access=Access.READ_WRITE,
            encoding=Encoding.U16,
            field=field,
            range=SWITCH_RANGE,
            control=True,
        ),
        field_follows_index=follows,
    )


def _schedule_slots(
    *,
    name: str,
    stem: str,
    first_register: int,
    enable_register: int,
    equipment: Equipment,
) -> tuple[Family, Family]:
    slots = Family(
        name=f"{name}_slots",
        equipment=equipment,
        stem=stem,
        base=first_register,
        stride=SLOT_STRIDE,
        count=SLOT_COUNT,
        members=(
            _schedule_time(offset=0, key="start"),
            _schedule_time(offset=1, key="end"),
            _slot_days(offset=2),
            Member(
                offset=2,
                definition=Definition(
                    key="power",
                    quantity=Quantity.PERCENTAGE,
                    kind=EntityKind.NUMBER,
                    access=Access.READ_WRITE,
                    encoding=Encoding.U16,
                    unit=Unit.PERCENT,
                    field=SLOT_POWER_FIELD,
                    range=PERCENT_RANGE,
                    control=True,
                ),
            ),
        ),
    )
    enabled = Family(
        name=f"{name}_slots_enabled",
        equipment=equipment,
        stem=stem,
        base=enable_register,
        count=SLOT_COUNT,
        members=(
            _slot_switch(
                offset=0, key="enabled", field=SLOT_ENABLED_FIELD, follows=True
            ),
        ),
    )
    return slots, enabled


CHARGE_SLOTS, CHARGE_SLOTS_ENABLED = _schedule_slots(
    name="charge",
    stem="charge_slot_{index}",
    first_register=0x3606,
    enable_register=0x3604,
    equipment=Equipment.BATTERY,
)
DISCHARGE_SLOTS, DISCHARGE_SLOTS_ENABLED = _schedule_slots(
    name="discharge",
    stem="discharge_slot_{index}",
    first_register=0x361B,
    enable_register=0x3605,
    equipment=Equipment.BATTERY,
)
EV_SLOTS = Family(
    name="ev_slots",
    equipment=Equipment.EV_CHARGER,
    stem="ev_slot_{index}",
    base=0x4B20,
    stride=EV_SLOT_STRIDE,
    count=SLOT_COUNT,
    members=(
        _schedule_time(offset=0, key="start"),
        _schedule_time(offset=1, key="end"),
        Member(
            offset=2,
            definition=Definition(
                key="mode",
                quantity=Quantity.CODE,
                kind=EntityKind.SELECT,
                access=Access.READ_WRITE,
                encoding=Encoding.U16,
                field=EV_SLOT_MODE_FIELD,
                options=EV_SLOT_MODE_OPTIONS,
                control=True,
            ),
        ),
        _slot_switch(
            offset=2,
            key="grid_charging",
            field=EV_SLOT_GRID_CHARGING_FIELD,
            follows=False,
        ),
        _slot_switch(
            offset=2,
            key="battery_discharge",
            field=EV_SLOT_BATTERY_DISCHARGE_FIELD,
            follows=False,
        ),
        _slot_days(offset=2),
        Member(
            offset=3,
            definition=Definition(
                key="power",
                quantity=Quantity.POWER,
                kind=EntityKind.NUMBER,
                access=Access.READ_WRITE,
                encoding=Encoding.U32,
                unit=Unit.WATT,
                range=EV_POWER_RANGE,
                control=True,
            ),
        ),
    ),
)

FAMILIES = (
    GRID_PHASE,
    INVERTER_PHASE,
    BACKUP_PHASE,
    GRID_OUTPUT_FIRST_PHASE,
    GRID_OUTPUT_OTHER_PHASES,
    PV_STRING,
    PV_INSULATION,
    PV_ENERGY,
    BATTERY_CHARGE_ENERGY,
    BATTERY_DISCHARGE_ENERGY,
    INVERTER_ENERGY,
    LOAD_ENERGY,
    BACKUP_LOAD_ENERGY,
    GRID_EXPORT_ENERGY,
    GRID_IMPORT_ENERGY,
    GRID_FIRST_PHASE_EXPORT_ENERGY,
    GRID_FIRST_PHASE_IMPORT_ENERGY,
    GRID_OTHER_PHASES_EXPORT_ENERGY,
    GRID_OTHER_PHASES_IMPORT_ENERGY,
    PV_OTHER_STRINGS_ENERGY,
    *PARALLEL_ENERGY,
    *AVERAGE_TOTALS,
    *AVERAGE_PHASES,
    AVERAGE_PV_STRING,
    AVERAGE_BATTERY_PACK,
    BATTERY_PACK,
    BATTERY_PACK_DISCHARGED_ENERGY,
    BATTERY_PACK_FAULTS,
    BATTERY_PACK_IDENTITY,
    METER_A_PHASE,
    METER_B_PHASE,
    METER_A_POWER_HIGH_WORDS,
    METER_B_POWER_HIGH_WORDS,
    METER_A_REACTIVE_POWER,
    METER_B_REACTIVE_POWER,
    EV_PHASE,
    ETHERNET_ADDRESSES,
    CHARGE_SLOTS,
    CHARGE_SLOTS_ENABLED,
    DISCHARGE_SLOTS,
    DISCHARGE_SLOTS_ENABLED,
    EV_SLOTS,
)
FAMILY_BY_NAME = {family.name: family for family in FAMILIES}


def _power_limit_setting(
    *,
    key: str,
    equipment: Equipment | None = None,
    value_range: Range = POWER_LIMIT_RANGE,
    control: bool = False,
) -> Definition:
    return Definition(
        key=key,
        equipment=equipment,
        quantity=Quantity.PERCENTAGE,
        kind=EntityKind.NUMBER,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        scale=0.1,
        unit=Unit.PERCENT,
        range=value_range,
        control=control,
    )


def _percent_setting(*, key: str, equipment: Equipment | None = None) -> Definition:
    return replace(
        _power_limit_setting(key=key, equipment=equipment, control=True),
        scale=1,
        range=PERCENT_RANGE,
        core=True,
    )


def _command(*, key: str, value: int, control: bool = False) -> Definition:
    return Definition(
        key=key,
        quantity=Quantity.CODE,
        kind=EntityKind.BUTTON,
        access=Access.WRITE_ONLY,
        encoding=Encoding.U16,
        command_value=value,
        control=control,
    )


def _ems_percentage(
    *,
    key: str,
    encoding: Encoding,
    value_range: Range,
    invalid: frozenset[int] = frozenset(),
    equipment: Equipment | None = None,
) -> Definition:
    return Definition(
        key=key,
        equipment=equipment,
        quantity=Quantity.PERCENTAGE,
        kind=EntityKind.NUMBER,
        access=Access.WRITE_ONLY,
        encoding=encoding,
        scale=0.01,
        unit=Unit.PERCENT,
        invalid=invalid,
        range=value_range,
    )


def _ems_current_limit(
    *, key: str, maximum: float, equipment: Equipment | None = None
) -> Definition:
    return Definition(
        key=key,
        equipment=equipment,
        quantity=Quantity.CURRENT,
        kind=EntityKind.NUMBER,
        access=Access.WRITE_ONLY,
        encoding=Encoding.U16,
        scale=0.1,
        unit=Unit.AMPERE,
        range=Range(minimum=0, maximum=maximum),
    )


def _setting(
    *,
    key: str,
    quantity: Quantity,
    value_range: Range,
    scale: float = 1,
    unit: Unit | None = None,
) -> Definition:
    return replace(
        _measure(
            key=key,
            quantity=quantity,
            encoding=Encoding.U16,
            scale=scale,
            unit=unit,
        ),
        kind=EntityKind.NUMBER,
        access=Access.READ_WRITE,
        range=value_range,
    )


def _of_battery(*, definition: Definition) -> Definition:
    return replace(definition, equipment=Equipment.BATTERY)


def _lead_acid_voltage(*, key: str) -> Definition:
    return _of_battery(
        definition=_setting(
            key=key,
            quantity=Quantity.VOLTAGE,
            scale=0.1,
            unit=Unit.VOLT,
            value_range=LEAD_ACID_VOLTAGE_RANGE,
        )
    )


def _lead_acid_current(*, key: str) -> Definition:
    return _of_battery(
        definition=_setting(
            key=key,
            quantity=Quantity.CURRENT,
            scale=0.1,
            unit=Unit.AMPERE,
            value_range=LEAD_ACID_CURRENT_RANGE,
        )
    )


def _select_setting(*, key: str, options: Mapping[int, str]) -> Definition:
    return Definition(
        key=key,
        quantity=Quantity.CODE,
        kind=EntityKind.SELECT,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        options=options,
    )


def _flag_word(*, key: str) -> Definition:
    return _setting(key=key, quantity=Quantity.CODE, value_range=WORD_RANGE)


def _reading(
    *, key: str, quantity: Quantity, options: Mapping[int, str] | None = None
) -> Definition:
    return replace(
        _measure(key=key, quantity=quantity, encoding=Encoding.U16),
        options=options,
    )


def _battery_controller_current(*, key: str) -> Definition:
    return _of_battery(
        definition=_measure(
            key=key,
            quantity=Quantity.CURRENT,
            encoding=Encoding.I16,
            scale=0.01,
            unit=Unit.AMPERE,
        )
    )


COMMISSIONING_SETTINGS: tuple[Definition, ...] = (
    _select_setting(key="reverse_flow_mode", options=REVERSE_FLOW_MODE_OPTIONS),
    _setting(
        key="fcas_frequency_hysteresis",
        quantity=Quantity.FREQUENCY,
        scale=0.01,
        unit=Unit.HERTZ,
        value_range=Range(minimum=0, maximum=0.15),
    ),
    _lead_acid_voltage(key="lead_acid_off_grid_discharge_cutoff_voltage"),
    _lead_acid_voltage(key="lead_acid_charge_cutoff_voltage"),
    _lead_acid_voltage(key="lead_acid_on_grid_discharge_cutoff_voltage"),
    _lead_acid_voltage(key="lead_acid_high_voltage_protection"),
    _lead_acid_voltage(key="lead_acid_low_voltage_warning"),
    _lead_acid_current(key="lead_acid_discharge_current_limit"),
    _lead_acid_current(key="lead_acid_charge_current_limit"),
    _of_battery(
        definition=_setting(
            key="lead_acid_capacity",
            quantity=Quantity.CAPACITY,
            unit=Unit.AMPERE_HOUR,
            value_range=Range(minimum=0, maximum=1000),
        )
    ),
    _lead_acid_voltage(key="lead_acid_float_charge_voltage"),
    _lead_acid_voltage(key="lead_acid_equalising_charge_voltage"),
    _of_battery(
        definition=_setting(
            key="bms_update_id",
            quantity=Quantity.COUNT,
            value_range=Range(minimum=0, maximum=31),
        )
    ),
    _of_battery(
        definition=_setting(
            key="bms_update_mode",
            quantity=Quantity.CODE,
            value_range=Range(minimum=0, maximum=255),
        )
    ),
    _setting(
        key="parallel_role",
        quantity=Quantity.CODE,
        value_range=Range(minimum=0, maximum=10),
    ),
    _setting(
        key="parallel_number",
        quantity=Quantity.COUNT,
        value_range=Range(minimum=1, maximum=255),
    ),
    _select_setting(
        key="parallel_configured_mode", options=PARALLEL_CONFIGURED_MODE_OPTIONS
    ),
    _select_setting(key="battery_input_mode", options=BATTERY_INPUT_MODE_OPTIONS),
    _select_setting(key="pv_input_mode", options=PV_INPUT_MODE_OPTIONS),
    _setting(
        key="off_grid_output_voltage",
        quantity=Quantity.VOLTAGE,
        scale=0.1,
        unit=Unit.VOLT,
        value_range=Range(minimum=220, maximum=240),
    ),
    _setting(
        key="off_grid_output_frequency",
        quantity=Quantity.FREQUENCY,
        scale=0.01,
        unit=Unit.HERTZ,
        value_range=Range(minimum=50, maximum=60),
    ),
    _flag_word(key="motor_enable"),
    _setting(
        key="machine_model",
        quantity=Quantity.CODE,
        value_range=Range(minimum=90, maximum=96),
    ),
    _setting(
        key="rated_power",
        quantity=Quantity.POWER,
        unit=Unit.WATT,
        value_range=Range(minimum=3000, maximum=6000),
    ),
    _flag_word(key="function_flags_1"),
    _flag_word(key="function_flags_2"),
    _setting(
        key="max_dc_current_component",
        quantity=Quantity.CURRENT,
        unit=Unit.MILLIAMPERE,
        value_range=Range(minimum=0, maximum=3000),
    ),
    _setting(
        key="max_dc_voltage_component",
        quantity=Quantity.VOLTAGE,
        scale=0.1,
        unit=Unit.VOLT,
        value_range=Range(minimum=0, maximum=40),
    ),
    _setting(
        key="insulation_resistance_limit",
        quantity=Quantity.RESISTANCE,
        unit=Unit.KILOOHM,
        value_range=Range(minimum=30, maximum=1000),
    ),
    _setting(
        key="max_leakage_current",
        quantity=Quantity.CURRENT,
        unit=Unit.MILLIAMPERE,
        value_range=Range(minimum=30, maximum=500),
    ),
    _select_setting(key="grid_type", options=GRID_TYPE_OPTIONS),
    _setting(
        key="pv_start_voltage",
        quantity=Quantity.VOLTAGE,
        scale=0.1,
        unit=Unit.VOLT,
        value_range=PV_VOLTAGE_RANGE,
    ),
    _setting(
        key="pv_shutdown_voltage",
        quantity=Quantity.VOLTAGE,
        scale=0.1,
        unit=Unit.VOLT,
        value_range=PV_VOLTAGE_RANGE,
    ),
    _setting(
        key="mppt_voltage_high",
        quantity=Quantity.VOLTAGE,
        scale=0.1,
        unit=Unit.VOLT,
        value_range=MPPT_VOLTAGE_RANGE,
    ),
    _setting(
        key="mppt_voltage_low",
        quantity=Quantity.VOLTAGE,
        scale=0.1,
        unit=Unit.VOLT,
        value_range=MPPT_VOLTAGE_RANGE,
    ),
    _setting(
        key="mppt_scan_time",
        quantity=Quantity.DURATION,
        unit=Unit.MINUTE,
        value_range=Range(minimum=3, maximum=30000),
    ),
)
READINGS: tuple[Definition, ...] = (
    _reading(
        key="off_grid_mode", quantity=Quantity.CODE, options=OFF_GRID_MODE_OPTIONS
    ),
    _reading(
        key="inverter_stop", quantity=Quantity.CODE, options=INVERTER_STOP_OPTIONS
    ),
    _reading(key="inverter_error_count", quantity=Quantity.COUNT),
    _reading(key="drm_hardware_status", quantity=Quantity.CODE),
    _reading(key="drm_software_status", quantity=Quantity.CODE),
    _reading(key="fault_record_sequence", quantity=Quantity.COUNT),
    _reading(
        key="application_mode_active",
        quantity=Quantity.CODE,
        options=APPLICATION_MODE_OPTIONS,
    ),
    _battery_controller_current(key="battery_controller_1_current"),
    _battery_controller_current(key="battery_controller_2_current"),
    _measure(
        key="pv_generation_time_today",
        quantity=Quantity.DURATION,
        encoding=Encoding.U16,
        scale=0.1,
        unit=Unit.HOUR,
    ),
    _measure(
        key="pv_generation_time_total",
        quantity=Quantity.DURATION,
        encoding=Encoding.U32,
        scale=0.1,
        unit=Unit.HOUR,
    ),
    _of_battery(
        definition=_measure(
            key="battery_voltage_low_warning",
            quantity=Quantity.VOLTAGE,
            encoding=Encoding.U16,
            scale=0.1,
            unit=Unit.VOLT,
        )
    ),
)


SINGLES: tuple[Definition, ...] = (
    Definition(
        key="ethernet_protocol_version",
        quantity=Quantity.VERSION,
        encoding=Encoding.U16,
        scale=0.001,
        invalid=frozenset({INVALID_VERSION}),
    ),
    Definition(
        key="ethernet_mac_address",
        quantity=Quantity.ADDRESS,
        encoding=Encoding.MAC,
        private=True,
    ),
    Definition(
        key="ethernet_mode",
        quantity=Quantity.CODE,
        kind=EntityKind.SELECT,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        options=ETHERNET_MODE_OPTIONS,
    ),
    Definition(
        key="ev_serial_number",
        equipment=Equipment.EV_CHARGER,
        quantity=Quantity.TEXT,
        encoding=Encoding.TEXT,
        words=16,
        invalid=frozenset({EMPTY_TEXT}),
        private=True,
    ),
    Definition(
        key="ev_model",
        equipment=Equipment.EV_CHARGER,
        quantity=Quantity.TEXT,
        encoding=Encoding.TEXT,
        words=8,
        invalid=frozenset({EMPTY_TEXT}),
    ),
    Definition(
        key="ev_software_version",
        equipment=Equipment.EV_CHARGER,
        quantity=Quantity.VERSION,
        encoding=Encoding.TEXT,
        words=5,
        invalid=frozenset({EMPTY_TEXT}),
    ),
    Definition(
        key="ev_hardware_version",
        equipment=Equipment.EV_CHARGER,
        quantity=Quantity.VERSION,
        encoding=Encoding.TEXT,
        words=5,
        invalid=frozenset({EMPTY_TEXT}),
    ),
    Definition(
        key="ev_phase_count",
        equipment=Equipment.EV_CHARGER,
        quantity=Quantity.COUNT,
        encoding=Encoding.U16,
    ),
    Definition(
        key="ev_minimum_power",
        equipment=Equipment.EV_CHARGER,
        quantity=Quantity.POWER,
        encoding=Encoding.U16,
        unit=Unit.WATT,
    ),
    Definition(
        key="ev_maximum_power",
        equipment=Equipment.EV_CHARGER,
        quantity=Quantity.POWER,
        encoding=Encoding.U32,
        unit=Unit.WATT,
    ),
    Definition(
        key="ev_work_mode",
        equipment=Equipment.EV_CHARGER,
        quantity=Quantity.CODE,
        encoding=Encoding.U16,
        options=EV_MODE_OPTIONS,
    ),
    Definition(
        key="ev_status",
        core=True,
        equipment=Equipment.EV_CHARGER,
        quantity=Quantity.CODE,
        encoding=Encoding.U16,
        options=EV_STATUS_OPTIONS,
    ),
    Definition(
        key="ev_power",
        core=True,
        equipment=Equipment.EV_CHARGER,
        quantity=Quantity.POWER,
        encoding=Encoding.U32,
        unit=Unit.WATT,
    ),
    Definition(
        key="ev_charge_duration",
        equipment=Equipment.EV_CHARGER,
        quantity=Quantity.DURATION,
        encoding=Encoding.U16,
        unit=Unit.MINUTE,
    ),
    Definition(
        key="ev_session_energy",
        core=True,
        equipment=Equipment.EV_CHARGER,
        quantity=Quantity.ENERGY,
        encoding=Encoding.U32,
        scale=0.001,
        unit=Unit.KILOWATT_HOUR,
    ),
    Definition(
        key="ev_total_energy",
        core=True,
        equipment=Equipment.EV_CHARGER,
        quantity=Quantity.ENERGY,
        encoding=Encoding.U32,
        scale=0.001,
        unit=Unit.KILOWATT_HOUR,
    ),
    Definition(
        key="ev_control_pilot_voltage",
        equipment=Equipment.EV_CHARGER,
        quantity=Quantity.VOLTAGE,
        encoding=Encoding.U16,
        unit=Unit.VOLT,
    ),
    Definition(
        key="ev_duty_cycle",
        equipment=Equipment.EV_CHARGER,
        quantity=Quantity.PERCENTAGE,
        encoding=Encoding.U16,
        scale=0.1,
        unit=Unit.PERCENT,
    ),
    Definition(
        key="ev_remote_control",
        equipment=Equipment.EV_CHARGER,
        quantity=Quantity.CODE,
        encoding=Encoding.U16,
        options=EV_REMOTE_CONTROL_OPTIONS,
    ),
    Definition(
        key="ev_current_setpoint",
        equipment=Equipment.EV_CHARGER,
        quantity=Quantity.CURRENT,
        encoding=Encoding.U16,
        scale=0.1,
        unit=Unit.AMPERE,
    ),
    Definition(
        key="ev_session_start",
        equipment=Equipment.EV_CHARGER,
        quantity=Quantity.TIMESTAMP,
        encoding=Encoding.UNIX_TIME,
    ),
    Definition(
        key="ev_session_end",
        equipment=Equipment.EV_CHARGER,
        quantity=Quantity.TIMESTAMP,
        encoding=Encoding.UNIX_TIME,
    ),
    Definition(
        key="settings_sequence",
        quantity=Quantity.COUNT,
        kind=EntityKind.NUMBER,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        range=Range(minimum=0, maximum=65535),
    ),
    Definition(
        key="settings_protocol_version",
        quantity=Quantity.VERSION,
        encoding=Encoding.U16,
        invalid=frozenset({INVALID_VERSION}),
    ),
    Definition(
        key="meter_configuration",
        quantity=Quantity.CODE,
        kind=EntityKind.SELECT,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        options=METER_CONFIGURATION_OPTIONS,
    ),
    Definition(
        key="meter_address",
        quantity=Quantity.COUNT,
        kind=EntityKind.NUMBER,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        range=Range(minimum=1, maximum=255),
    ),
    Definition(
        key="rs485_address",
        quantity=Quantity.COUNT,
        kind=EntityKind.NUMBER,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        range=Range(minimum=1, maximum=127),
    ),
    Definition(
        key="rs485_baud_rate",
        quantity=Quantity.COUNT,
        kind=EntityKind.NUMBER,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        range=Range(minimum=0, maximum=65535),
    ),
    Definition(
        key="passive_mode",
        quantity=Quantity.COUNT,
        kind=EntityKind.NUMBER,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        range=Range(minimum=0, maximum=2),
    ),
    _power_limit_setting(key="passive_grid_charge_power"),
    _power_limit_setting(key="passive_grid_discharge_power"),
    _power_limit_setting(
        key="passive_battery_charge_power", equipment=Equipment.BATTERY
    ),
    _power_limit_setting(
        key="passive_battery_discharge_power", equipment=Equipment.BATTERY
    ),
    Definition(
        key="battery_protocol",
        quantity=Quantity.CODE,
        kind=EntityKind.SELECT,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        options=BATTERY_PROTOCOL_OPTIONS,
    ),
    Definition(
        key="battery_auto_wake",
        equipment=Equipment.BATTERY,
        quantity=Quantity.TOGGLE,
        kind=EntityKind.SWITCH,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        range=SWITCH_RANGE,
    ),
    _percent_setting(
        key="battery_discharge_limit_on_grid", equipment=Equipment.BATTERY
    ),
    _percent_setting(
        key="battery_discharge_limit_off_grid", equipment=Equipment.BATTERY
    ),
    _percent_setting(key="battery_charge_limit", equipment=Equipment.BATTERY),
    Definition(
        key="application_mode",
        control=True,
        quantity=Quantity.CODE,
        kind=EntityKind.SELECT,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        options=APPLICATION_MODE_OPTIONS,
        core=True,
    ),
    _power_limit_setting(
        key="battery_charge_power_limit", equipment=Equipment.BATTERY, control=True
    ),
    _power_limit_setting(
        key="battery_discharge_power_limit", equipment=Equipment.BATTERY, control=True
    ),
    _power_limit_setting(key="grid_import_power_limit", control=True),
    _power_limit_setting(key="grid_export_power_limit", control=True),
    Definition(
        key="backup_reserve_soc",
        control=True,
        equipment=Equipment.BATTERY,
        quantity=Quantity.STATE_OF_CHARGE,
        kind=EntityKind.NUMBER,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        unit=Unit.PERCENT,
        range=Range(minimum=0, maximum=100),
        core=True,
    ),
    Definition(
        key="export_limit_power",
        control=True,
        quantity=Quantity.PERCENTAGE,
        kind=EntityKind.NUMBER,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        scale=0.1,
        unit=Unit.PERCENT,
        range=Range(minimum=0, maximum=100),
    ),
    Definition(
        key="export_limit_current",
        control=True,
        quantity=Quantity.CURRENT,
        kind=EntityKind.NUMBER,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        scale=0.01,
        unit=Unit.AMPERE,
        range=Range(minimum=0, maximum=3),
    ),
    Definition(
        key="export_limit_mode",
        control=True,
        quantity=Quantity.CODE,
        kind=EntityKind.SELECT,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        options=EXPORT_LIMIT_MODE_OPTIONS,
    ),
    Definition(
        key="time_of_use_idle_mode",
        control=True,
        quantity=Quantity.CODE,
        kind=EntityKind.SELECT,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        options=TIME_OF_USE_IDLE_MODE_OPTIONS,
    ),
    Definition(
        key="time_of_use_grid_discharge",
        control=True,
        quantity=Quantity.TOGGLE,
        kind=EntityKind.SWITCH,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        range=SWITCH_RANGE,
    ),
    Definition(
        key="buzzer",
        control=True,
        quantity=Quantity.TOGGLE,
        kind=EntityKind.SWITCH,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        field=BUZZER_FIELD,
        inverted=True,
        range=SWITCH_RANGE,
    ),
    _power_limit_setting(
        key="battery_forced_charge_power_limit",
        equipment=Equipment.BATTERY,
        value_range=FORCED_CHARGE_POWER_RANGE,
        control=True,
    ),
    Definition(
        key="led_mode",
        control=True,
        quantity=Quantity.CODE,
        kind=EntityKind.SELECT,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        options=LED_MODE_OPTIONS,
    ),
    Definition(
        key="rs485_slave_address",
        quantity=Quantity.COUNT,
        kind=EntityKind.NUMBER,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        range=Range(minimum=1, maximum=1),
    ),
    Definition(
        key="rs485_slave_baud_rate",
        quantity=Quantity.CODE,
        kind=EntityKind.SELECT,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        options=BAUD_RATE_OPTIONS,
    ),
    Definition(
        key="inverter_clock", quantity=Quantity.TIMESTAMP, encoding=Encoding.CLOCK
    ),
    Definition(
        key="operating_mode",
        quantity=Quantity.CODE,
        encoding=Encoding.U16,
        options=OPERATING_MODE_OPTIONS,
        core=True,
    ),
    Definition(
        key="inverter_temperature",
        quantity=Quantity.TEMPERATURE,
        encoding=Encoding.I16,
        scale=0.1,
        unit=Unit.CELSIUS,
        core=True,
    ),
    Definition(
        key="ambient_temperature",
        quantity=Quantity.TEMPERATURE,
        encoding=Encoding.I16,
        scale=0.1,
        unit=Unit.CELSIUS,
    ),
    Definition(
        key="leakage_current",
        quantity=Quantity.CURRENT,
        encoding=Encoding.U16,
        unit=Unit.MILLIAMPERE,
    ),
    Definition(
        key="grid_connection_countdown",
        quantity=Quantity.DURATION,
        encoding=Encoding.U16,
        unit=Unit.SECOND,
    ),
    Definition(
        key="inverter_discharge_power_setpoint",
        quantity=Quantity.POWER,
        encoding=Encoding.I16,
        unit=Unit.WATT,
    ),
    Definition(
        key="inverter_charge_power_setpoint",
        quantity=Quantity.POWER,
        encoding=Encoding.I16,
        unit=Unit.WATT,
    ),
    Definition(
        key="battery_discharge_current_setpoint",
        equipment=Equipment.BATTERY,
        quantity=Quantity.CURRENT,
        encoding=Encoding.I16,
        scale=0.1,
        unit=Unit.AMPERE,
    ),
    Definition(
        key="battery_charge_current_setpoint",
        equipment=Equipment.BATTERY,
        quantity=Quantity.CURRENT,
        encoding=Encoding.I16,
        scale=0.1,
        unit=Unit.AMPERE,
    ),
    Definition(
        key="battery_status_code",
        equipment=Equipment.BATTERY,
        quantity=Quantity.CODE,
        encoding=Encoding.U16,
    ),
    Definition(
        key="battery_protocol_active", quantity=Quantity.CODE, encoding=Encoding.I16
    ),
    Definition(
        key="battery_charge_limit_active",
        equipment=Equipment.BATTERY,
        quantity=Quantity.COUNT,
        encoding=Encoding.I16,
    ),
    Definition(
        key="battery_discharge_limit_active",
        equipment=Equipment.BATTERY,
        quantity=Quantity.COUNT,
        encoding=Encoding.I16,
    ),
    Definition(
        key="battery_depth_of_discharge_active",
        equipment=Equipment.BATTERY,
        quantity=Quantity.COUNT,
        encoding=Encoding.I16,
    ),
    Definition(
        key="backup_reserve_soc_active",
        equipment=Equipment.BATTERY,
        quantity=Quantity.STATE_OF_CHARGE,
        encoding=Encoding.I16,
        unit=Unit.PERCENT,
    ),
    Definition(
        key="meter_configuration_active", quantity=Quantity.CODE, encoding=Encoding.I16
    ),
    Definition(
        key="dc_bus_voltage",
        quantity=Quantity.VOLTAGE,
        encoding=Encoding.U16,
        scale=0.1,
        unit=Unit.VOLT,
    ),
    Definition(
        key="dc_bus_slave_voltage",
        quantity=Quantity.VOLTAGE,
        encoding=Encoding.U16,
        scale=0.1,
        unit=Unit.VOLT,
    ),
    Definition(
        key="battery_voltage",
        equipment=Equipment.BATTERY,
        quantity=Quantity.VOLTAGE,
        encoding=Encoding.U16,
        scale=0.1,
        unit=Unit.VOLT,
        core=True,
    ),
    Definition(
        key="battery_current",
        equipment=Equipment.BATTERY,
        quantity=Quantity.CURRENT,
        encoding=Encoding.I16,
        scale=0.01,
        unit=Unit.AMPERE,
        core=True,
    ),
    Definition(
        key="battery_port_power",
        equipment=Equipment.BATTERY,
        quantity=Quantity.POWER,
        encoding=Encoding.I16,
        unit=Unit.WATT,
    ),
    Definition(
        key="battery_temperature",
        equipment=Equipment.BATTERY,
        quantity=Quantity.TEMPERATURE,
        encoding=Encoding.I16,
        scale=0.1,
        unit=Unit.CELSIUS,
        core=True,
    ),
    Definition(
        key="battery_soc",
        equipment=Equipment.BATTERY,
        quantity=Quantity.STATE_OF_CHARGE,
        encoding=Encoding.U16,
        scale=0.01,
        unit=Unit.PERCENT,
        valid_range=SOC_RANGE,
        core=True,
    ),
    Definition(key="pv_direction", quantity=Quantity.CODE, encoding=Encoding.U16),
    Definition(
        key="battery_direction",
        equipment=Equipment.BATTERY,
        quantity=Quantity.CODE,
        encoding=Encoding.I16,
    ),
    Definition(key="grid_direction", quantity=Quantity.CODE, encoding=Encoding.I16),
    Definition(key="output_direction", quantity=Quantity.CODE, encoding=Encoding.U16),
    Definition(
        key="load_power",
        quantity=Quantity.POWER,
        encoding=Encoding.I16,
        unit=Unit.WATT,
        core=True,
    ),
    Definition(
        key="pv_power",
        quantity=Quantity.POWER,
        encoding=Encoding.I16,
        unit=Unit.WATT,
        core=True,
    ),
    Definition(
        key="battery_power",
        equipment=Equipment.BATTERY,
        quantity=Quantity.POWER,
        encoding=Encoding.I16,
        unit=Unit.WATT,
        core=True,
    ),
    Definition(
        key="grid_power",
        quantity=Quantity.POWER,
        encoding=Encoding.I16,
        unit=Unit.WATT,
        core=True,
    ),
    Definition(
        key="inverter_power",
        quantity=Quantity.POWER,
        encoding=Encoding.I16,
        unit=Unit.WATT,
        core=True,
    ),
    Definition(
        key="grid_load_power",
        quantity=Quantity.POWER,
        encoding=Encoding.I16,
        unit=Unit.WATT,
    ),
    Definition(key="parallel_mode", quantity=Quantity.CODE, encoding=Encoding.U16),
    Definition(
        key="parallel_id",
        equipment=Equipment.PARALLEL,
        quantity=Quantity.COUNT,
        encoding=Encoding.U16,
    ),
    Definition(
        key="parallel_count",
        equipment=Equipment.PARALLEL,
        quantity=Quantity.COUNT,
        encoding=Encoding.U16,
    ),
    Definition(
        key="parallel_online_count", quantity=Quantity.COUNT, encoding=Encoding.U16
    ),
    Definition(
        key="parallel_pv_power_low_word",
        equipment=Equipment.PARALLEL,
        quantity=Quantity.POWER,
        encoding=Encoding.U16,
        unit=Unit.WATT,
    ),
    Definition(
        key="parallel_battery_power_low_word",
        equipment=Equipment.PARALLEL,
        quantity=Quantity.POWER,
        encoding=Encoding.U16,
        unit=Unit.WATT,
    ),
    Definition(
        key="parallel_grid_power_low_word",
        equipment=Equipment.PARALLEL,
        quantity=Quantity.POWER,
        encoding=Encoding.U16,
        unit=Unit.WATT,
    ),
    Definition(
        key="parallel_load_power_low_word",
        equipment=Equipment.PARALLEL,
        quantity=Quantity.POWER,
        encoding=Encoding.U16,
        unit=Unit.WATT,
    ),
    Definition(
        key="parallel_backup_load_power_low_word",
        equipment=Equipment.PARALLEL,
        quantity=Quantity.POWER,
        encoding=Encoding.U16,
        unit=Unit.WATT,
    ),
    Definition(
        key="parallel_battery_soc",
        core=True,
        equipment=Equipment.PARALLEL,
        quantity=Quantity.STATE_OF_CHARGE,
        encoding=Encoding.U16,
        unit=Unit.PERCENT,
    ),
    Definition(
        key="parallel_grid_load_power_low_word",
        equipment=Equipment.PARALLEL,
        quantity=Quantity.POWER,
        encoding=Encoding.U16,
        unit=Unit.WATT,
    ),
    Definition(
        key="parallel_battery_capacity",
        equipment=Equipment.PARALLEL,
        quantity=Quantity.CAPACITY,
        encoding=Encoding.U16,
        unit=Unit.AMPERE_HOUR,
    ),
    Definition(
        key="parallel_pv_power_high_word",
        equipment=Equipment.PARALLEL,
        quantity=Quantity.POWER,
        encoding=Encoding.U16,
        unit=Unit.WATT,
    ),
    Definition(
        key="parallel_battery_power_high_word",
        equipment=Equipment.PARALLEL,
        quantity=Quantity.POWER,
        encoding=Encoding.I16,
        unit=Unit.WATT,
    ),
    Definition(
        key="parallel_grid_power_high_word",
        equipment=Equipment.PARALLEL,
        quantity=Quantity.POWER,
        encoding=Encoding.I16,
        unit=Unit.WATT,
    ),
    Definition(
        key="parallel_load_power_high_word",
        equipment=Equipment.PARALLEL,
        quantity=Quantity.POWER,
        encoding=Encoding.U16,
        unit=Unit.WATT,
    ),
    Definition(
        key="parallel_backup_load_power_high_word",
        equipment=Equipment.PARALLEL,
        quantity=Quantity.POWER,
        encoding=Encoding.I16,
        unit=Unit.WATT,
    ),
    Definition(
        key="parallel_grid_load_power_high_word",
        equipment=Equipment.PARALLEL,
        quantity=Quantity.POWER,
        encoding=Encoding.I16,
        unit=Unit.WATT,
    ),
    Definition(
        key="parallel_meter_b_power",
        equipment=Equipment.PARALLEL,
        quantity=Quantity.POWER,
        encoding=Encoding.I32,
        unit=Unit.WATT,
    ),
    Definition(
        key="ev_settings_protocol_version",
        equipment=Equipment.EV_CHARGER,
        quantity=Quantity.VERSION,
        encoding=Encoding.U16,
        invalid=frozenset({INVALID_VERSION}),
    ),
    Definition(
        key="ev_enabled",
        control=True,
        quantity=Quantity.TOGGLE,
        kind=EntityKind.SWITCH,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        range=SWITCH_RANGE,
    ),
    Definition(
        key="ev_address",
        equipment=Equipment.EV_CHARGER,
        quantity=Quantity.COUNT,
        kind=EntityKind.NUMBER,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        range=Range(minimum=1, maximum=127),
    ),
    Definition(
        key="ev_baud_rate",
        equipment=Equipment.EV_CHARGER,
        quantity=Quantity.CODE,
        kind=EntityKind.SELECT,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        options=BAUD_RATE_OPTIONS,
    ),
    Definition(
        key="ev_charger_count",
        equipment=Equipment.EV_CHARGER,
        quantity=Quantity.COUNT,
        kind=EntityKind.NUMBER,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        range=Range(minimum=1, maximum=3),
    ),
    Definition(
        key="ev_communication_timeout",
        equipment=Equipment.EV_CHARGER,
        quantity=Quantity.DURATION,
        kind=EntityKind.NUMBER,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        unit=Unit.SECOND,
        range=Range(minimum=1, maximum=6),
    ),
    Definition(
        key="ev_port_mode",
        equipment=Equipment.EV_CHARGER,
        quantity=Quantity.CODE,
        kind=EntityKind.SELECT,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        options=EV_PORT_MODE_OPTIONS,
    ),
    Definition(
        key="ev_port_address",
        equipment=Equipment.EV_CHARGER,
        quantity=Quantity.COUNT,
        kind=EntityKind.NUMBER,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        range=Range(minimum=1, maximum=254),
    ),
    Definition(
        key="ev_mode",
        control=True,
        core=True,
        equipment=Equipment.EV_CHARGER,
        quantity=Quantity.CODE,
        kind=EntityKind.SELECT,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        options=EV_MODE_OPTIONS,
    ),
    Definition(
        key="ev_charge_power",
        control=True,
        equipment=Equipment.EV_CHARGER,
        quantity=Quantity.POWER,
        kind=EntityKind.NUMBER,
        access=Access.READ_WRITE,
        encoding=Encoding.U32,
        unit=Unit.WATT,
        range=EV_POWER_RANGE,
    ),
    Definition(
        key="average_pv_power",
        quantity=Quantity.POWER,
        encoding=Encoding.I32,
        unit=Unit.WATT,
    ),
    Definition(
        key="average_battery_power",
        equipment=Equipment.BATTERY,
        quantity=Quantity.POWER,
        encoding=Encoding.I32,
        unit=Unit.WATT,
    ),
    Definition(
        key="average_battery_soc",
        equipment=Equipment.BATTERY,
        quantity=Quantity.STATE_OF_CHARGE,
        encoding=Encoding.U16,
        scale=0.01,
        unit=Unit.PERCENT,
    ),
    Definition(
        key="ems_timeout",
        quantity=Quantity.DURATION,
        kind=EntityKind.NUMBER,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        unit=Unit.SECOND,
        range=Range(minimum=0, maximum=65534),
    ),
    _command(key="clear_fault_history", value=1),
    _command(key="clear_current_fault", value=2, control=True),
    _command(key="restart_inverter", value=1),
    Definition(
        key="synchronise_clock",
        control=True,
        quantity=Quantity.TIMESTAMP,
        kind=EntityKind.BUTTON,
        access=Access.WRITE_ONLY,
        encoding=Encoding.CLOCK,
    ),
    _ems_percentage(
        key="ems_inverter_power_target",
        encoding=Encoding.I16,
        value_range=SIGNED_PERCENT_RANGE,
    ),
    _ems_current_limit(
        key="ems_battery_charge_current_limit", maximum=200, equipment=Equipment.BATTERY
    ),
    _ems_current_limit(
        key="ems_battery_discharge_current_limit",
        maximum=20,
        equipment=Equipment.BATTERY,
    ),
    _ems_percentage(
        key="ems_battery_power_target",
        equipment=Equipment.BATTERY,
        encoding=Encoding.I16,
        value_range=SIGNED_PERCENT_RANGE,
    ),
    _ems_percentage(
        key="ems_inverter_import_power_limit",
        encoding=Encoding.U16,
        value_range=PERCENT_RANGE,
    ),
    _ems_percentage(
        key="ems_inverter_export_power_limit",
        encoding=Encoding.U16,
        value_range=PERCENT_RANGE,
    ),
    _ems_percentage(
        key="ems_grid_power_target",
        encoding=Encoding.I16,
        value_range=SIGNED_PERCENT_RANGE,
    ),
    _ems_percentage(
        key="ems_pv_power_limit",
        encoding=Encoding.U16,
        value_range=PERCENT_RANGE,
        invalid=frozenset({NO_LIMIT}),
    ),
    _command(key="ems_pv_power_limit_remove", value=NO_LIMIT),
    Definition(
        key="product_code",
        quantity=Quantity.TEXT,
        encoding=Encoding.TEXT,
        words=10,
        invalid=frozenset({EMPTY_TEXT}),
    ),
    Definition(
        key="display_software_version",
        quantity=Quantity.VERSION,
        encoding=Encoding.U16,
        scale=0.001,
        invalid=frozenset({INVALID_VERSION}),
    ),
    Definition(
        key="master_software_version",
        quantity=Quantity.VERSION,
        encoding=Encoding.U16,
        scale=0.001,
        invalid=frozenset({INVALID_VERSION}),
    ),
    Definition(
        key="slave_software_version",
        quantity=Quantity.VERSION,
        encoding=Encoding.U16,
        scale=0.001,
        invalid=frozenset({INVALID_VERSION}),
    ),
    Definition(
        key="display_hardware_version",
        quantity=Quantity.VERSION,
        encoding=Encoding.U16,
        scale=0.001,
        invalid=frozenset({INVALID_VERSION}),
    ),
    Definition(
        key="control_hardware_version",
        quantity=Quantity.VERSION,
        encoding=Encoding.U16,
        scale=0.001,
        invalid=frozenset({INVALID_VERSION}),
    ),
    Definition(
        key="power_hardware_version",
        quantity=Quantity.VERSION,
        encoding=Encoding.U16,
        scale=0.001,
        invalid=frozenset({INVALID_VERSION}),
    ),
    Definition(
        key="battery_pack_count",
        quantity=Quantity.COUNT,
        encoding=Encoding.U16,
    ),
    Definition(
        key="battery_capacity",
        equipment=Equipment.BATTERY,
        quantity=Quantity.CAPACITY,
        encoding=Encoding.U16,
    ),
    Definition(
        key="battery_usable_capacity",
        equipment=Equipment.BATTERY,
        quantity=Quantity.CAPACITY,
        encoding=Encoding.U16,
    ),
    Definition(
        key="battery_online_code",
        equipment=Equipment.BATTERY,
        quantity=Quantity.CODE,
        encoding=Encoding.U16,
    ),
    Definition(
        key="battery_discharge_current_limit",
        equipment=Equipment.BATTERY,
        quantity=Quantity.CURRENT,
        encoding=Encoding.U16,
        scale=0.1,
        unit=Unit.AMPERE,
    ),
    Definition(
        key="battery_charge_current_limit",
        equipment=Equipment.BATTERY,
        quantity=Quantity.CURRENT,
        encoding=Encoding.U16,
        scale=0.1,
        unit=Unit.AMPERE,
    ),
    Definition(
        key="meter_a_status",
        quantity=Quantity.CODE,
        encoding=Encoding.U16,
        options=METER_STATUS_OPTIONS,
    ),
    Definition(
        key="meter_b_status",
        quantity=Quantity.CODE,
        encoding=Encoding.U16,
        options=METER_STATUS_OPTIONS,
    ),
    Definition(
        key="ct_grid_power",
        quantity=Quantity.POWER,
        encoding=Encoding.I16,
        unit=Unit.WATT,
    ),
    Definition(
        key="ct_grid_apparent_power",
        quantity=Quantity.APPARENT_POWER,
        encoding=Encoding.I16,
        unit=Unit.VOLT_AMPERE,
    ),
    Definition(
        key="ct_pv_power",
        quantity=Quantity.POWER,
        encoding=Encoding.I16,
        unit=Unit.WATT,
    ),
    Definition(
        key="ct_pv_apparent_power",
        quantity=Quantity.APPARENT_POWER,
        encoding=Encoding.I16,
        unit=Unit.VOLT_AMPERE,
    ),
    Definition(
        key="grid_apparent_power",
        quantity=Quantity.APPARENT_POWER,
        encoding=Encoding.I16,
        unit=Unit.VOLT_AMPERE,
    ),
    Definition(
        key="inverter_apparent_power",
        quantity=Quantity.APPARENT_POWER,
        encoding=Encoding.I16,
        unit=Unit.VOLT_AMPERE,
    ),
    Definition(
        key="backup_load_power",
        quantity=Quantity.POWER,
        encoding=Encoding.U16,
        unit=Unit.WATT,
        core=True,
        combination=Combination(
            operation=Operation.SUM,
            sources=tuple(
                f"backup_l{phase}_power" for phase in range(1, PHASE_COUNT + 1)
            ),
        ),
    ),
    Definition(
        key="backup_load_apparent_power",
        quantity=Quantity.APPARENT_POWER,
        encoding=Encoding.U16,
        unit=Unit.VOLT_AMPERE,
    ),
    Definition(
        key="protocol_version",
        quantity=Quantity.VERSION,
        encoding=Encoding.U16,
        scale=0.001,
        invalid=frozenset({INVALID_VERSION}),
    ),
    Definition(
        key="battery_voltage_high_protection",
        equipment=Equipment.BATTERY,
        quantity=Quantity.VOLTAGE,
        encoding=Encoding.U16,
        scale=0.1,
        unit=Unit.VOLT,
    ),
    Definition(
        key="battery_charge_voltage",
        equipment=Equipment.BATTERY,
        quantity=Quantity.VOLTAGE,
        encoding=Encoding.U16,
        scale=0.1,
        unit=Unit.VOLT,
    ),
    Definition(
        key="battery_discharge_cutoff_voltage",
        equipment=Equipment.BATTERY,
        quantity=Quantity.VOLTAGE,
        encoding=Encoding.U16,
        scale=0.1,
        unit=Unit.VOLT,
    ),
    Definition(
        key="ev_minimum_current_charging",
        equipment=Equipment.EV_CHARGER,
        quantity=Quantity.TOGGLE,
        kind=EntityKind.SWITCH,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        field=EV_MINIMUM_CURRENT_CHARGING_FIELD,
        range=SWITCH_RANGE,
    ),
    Definition(
        key="ev_ems_charging",
        equipment=Equipment.EV_CHARGER,
        quantity=Quantity.TOGGLE,
        kind=EntityKind.SWITCH,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        field=EV_EMS_CHARGING_FIELD,
        inverted=True,
        range=SWITCH_RANGE,
    ),
    Definition(
        key="ev_ems_phase_mode",
        equipment=Equipment.EV_CHARGER,
        quantity=Quantity.CODE,
        kind=EntityKind.SELECT,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        field=EV_EMS_PHASE_MODE_FIELD,
        options=EV_EMS_PHASE_MODE_OPTIONS,
    ),
    Definition(
        key="ev_ems_charge_current",
        equipment=Equipment.EV_CHARGER,
        quantity=Quantity.CURRENT,
        kind=EntityKind.NUMBER,
        access=Access.READ_WRITE,
        encoding=Encoding.U16,
        scale=0.1,
        unit=Unit.AMPERE,
        range=EV_EMS_CHARGE_CURRENT_RANGE,
    ),
    *(
        Definition(
            key=key,
            equipment=EMS_CONTROL_EQUIPMENT.get(key),
            quantity=Quantity.TOGGLE,
            kind=EntityKind.SWITCH,
            access=Access.READ_WRITE,
            encoding=Encoding.U16,
            field=BitRange(first=bit, last=bit),
            range=SWITCH_RANGE,
        )
        for key, bit in EMS_CONTROL_BITS.items()
    ),
    _meter_power(meter="a", equipment=Equipment.METER_A),
    _meter_power(meter="b", equipment=Equipment.METER_B),
    *COMMISSIONING_SETTINGS,
    *READINGS,
    *(
        Definition(
            key=f"parallel_{subject}_power",
            equipment=Equipment.PARALLEL,
            core=subject in PARALLEL_CORE_POWER_SUBJECTS,
            quantity=Quantity.POWER,
            encoding=Encoding.I32,
            unit=Unit.WATT,
            combination=Combination(
                operation=Operation.WORDS,
                sources=(
                    f"parallel_{subject}_power_high_word",
                    f"parallel_{subject}_power_low_word",
                ),
            ),
        )
        for subject in PARALLEL_POWER_SUBJECTS
    ),
)
INVERTER_FAULT_KEYS = (
    "inverter_fault_internal_communication",
    "inverter_fault_meter_communication",
    "inverter_fault_display_memory",
    "inverter_fault_display_clock",
    "inverter_fault_bms_device",
    "inverter_fault_bms_communication",
    "inverter_fault_ct_device",
    "inverter_fault_afci_communication",
    "inverter_fault_slave_communication",
    "inverter_fault_pv_meter_communication",
    "inverter_fault_ev_charger_communication",
    "inverter_fault_grid_phase_r_overvoltage",
    "inverter_fault_grid_phase_r_undervoltage",
    "inverter_fault_grid_phase_s_overvoltage",
    "inverter_fault_grid_phase_s_undervoltage",
    "inverter_fault_grid_phase_t_overvoltage",
    "inverter_fault_grid_phase_t_undervoltage",
    "inverter_fault_grid_overfrequency",
    "inverter_fault_grid_underfrequency",
    "inverter_fault_dcdc_communication",
    "inverter_fault_dcdc_device",
    "inverter_fault_parallel_communication",
    "inverter_fault_grid_lost",
    "inverter_fault_pv_input_mode",
    "inverter_fault_pv_hardware_overcurrent",
    "inverter_fault_pv_overvoltage",
    "inverter_fault_bus_hardware_overvoltage",
    "inverter_fault_bus_overvoltage",
    "inverter_fault_bus_undervoltage",
    "inverter_fault_grid_phase",
    "inverter_fault_islanding",
    "inverter_fault_arc_device",
    "inverter_fault_pv_input",
    "inverter_fault_hardware_overcurrent",
    "inverter_fault_neutral_earth_voltage",
    "inverter_fault_drm0",
    "inverter_fault_fan_1",
    "inverter_fault_fan_2",
    "inverter_fault_fan_3",
    "inverter_fault_fan_4",
    "inverter_fault_arc",
    "inverter_fault_pv_software_overcurrent",
    "inverter_fault_battery_overvoltage",
    "inverter_fault_battery_overcurrent",
    "inverter_fault_battery_charge_overvoltage",
    "inverter_fault_battery_overload",
    "inverter_fault_battery_soft_start",
    "inverter_fault_output_overload",
    "inverter_fault_battery_open_circuit",
    "inverter_fault_battery_discharge_undervoltage",
    "inverter_fault_authorisation_expired",
    "inverter_fault_display_communication",
    "inverter_fault_relay",
    "inverter_fault_controller_memory",
    "inverter_fault_over_temperature",
    "inverter_fault_under_temperature",
    "inverter_fault_leakage_current_device",
    "inverter_fault_dc_injection_device",
    "inverter_fault_current_sensor",
    "inverter_fault_grid_average_overvoltage",
    "inverter_fault_off_grid_undervoltage",
    "inverter_fault_grid_phase_r_dc_voltage",
    "inverter_fault_grid_phase_s_dc_voltage",
    "inverter_fault_grid_phase_t_dc_voltage",
    "inverter_fault_leakage_current",
    "inverter_fault_grid_phase_r_dc_injection",
    "inverter_fault_grid_phase_s_dc_injection",
    "inverter_fault_grid_phase_t_dc_injection",
    "inverter_fault_insulation",
    "inverter_fault_bus_imbalance",
)
BATTERY_FAULT_KEYS = (
    "battery_fault_internal_communication",
    "battery_fault_pack_sequence",
    "battery_fault_discharge_overcurrent",
    "battery_fault_charge_overcurrent",
    "battery_fault_total_undervoltage",
    "battery_fault_total_overvoltage",
    "battery_fault_cell_undervoltage",
    "battery_fault_cell_overvoltage",
    "battery_fault_hardware",
    "battery_fault_charge_cold",
    "battery_fault_charge_hot",
    "battery_fault_discharge_cold",
    "battery_fault_discharge_hot",
    "battery_fault_relay",
    "battery_fault_precharge",
    "battery_fault_insulation",
    "battery_fault_bms_incompatible",
    "battery_fault_cell_supplier_incompatible",
    "battery_fault_cell_incompatible",
    "battery_fault_voltage_level_mismatch",
    "battery_fault_breaker_open",
    "battery_fault_cell_temperature_difference",
    "battery_fault_cell_voltage_difference_2",
    "battery_fault_cell_voltage_difference_1",
    "battery_fault_cell_over_temperature",
    "battery_fault_short_circuit",
    "battery_fault_total_voltage_matching",
    "battery_fault_system_locked",
    "battery_fault_fuse",
    "battery_fault_charging_port_overvoltage",
)
EV_FAULT_KEYS = (
    "ev_fault_relay_over_temperature",
    "ev_fault_overload",
    "ev_fault_ac_overvoltage",
    "ev_fault_ac_undervoltage",
    "ev_fault_ac_overcurrent",
    "ev_fault_ac_overfrequency",
    "ev_fault_ac_underfrequency",
    "ev_fault_dc_residual_current_a",
    "ev_fault_emergency_stop",
    "ev_fault_under_temperature",
    "ev_fault_ac_residual_current",
    "ev_fault_input_terminal_over_temperature",
    "ev_fault_bluetooth",
    "ev_fault_dc_residual_current_b",
    "ev_fault_relay",
    "ev_fault_grounding",
    "ev_fault_phase_sequence",
    "ev_fault_rcd_circuit",
    "ev_fault_rs485_timeout",
    "ev_fault_supply",
    "ev_fault_meter",
    "ev_fault_control_pilot",
    "ev_fault_connector_lock",
    "ev_fault_connector_current",
    "ev_fault_dc_residual_current_c",
)
FAULT_KEYS: Mapping[Equipment | None, tuple[str, ...]] = {
    None: INVERTER_FAULT_KEYS,
    Equipment.BATTERY: BATTERY_FAULT_KEYS,
    Equipment.EV_CHARGER: EV_FAULT_KEYS,
}
FAULT_WORD_KEYS: Mapping[Equipment | None, tuple[str, ...]] = {
    None: tuple(f"inverter_fault_word_{index}" for index in range(1, 4)),
    Equipment.BATTERY: ("battery_fault_word_1",),
    Equipment.EV_CHARGER: tuple(f"ev_fault_word_{index}" for index in range(1, 3)),
}
FAULT_DEFINITIONS: tuple[Definition, ...] = tuple(
    definition
    for equipment, named in FAULT_KEYS.items()
    for definition in (
        *(
            _fault_word(key=key, equipment=equipment)
            for key in FAULT_WORD_KEYS[equipment]
        ),
        _problem(
            key=fault_summary_key(equipment=equipment),
            equipment=equipment,
            summary=True,
        ),
        _problem(key=fault_unrecognised_key(equipment=equipment), equipment=equipment),
        *(_problem(key=key, equipment=equipment) for key in named),
    )
)
DEFINITIONS: tuple[Definition, ...] = (
    *SINGLES,
    *(definition for family in FAMILIES for definition in family.definitions()),
    *FAULT_DEFINITIONS,
)
