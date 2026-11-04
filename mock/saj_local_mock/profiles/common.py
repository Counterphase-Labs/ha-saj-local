"""Register layout shared by both models."""

from typing import TYPE_CHECKING

from saj_local_mock.models import MAX_PV_STRINGS, ModelSpec
from saj_local_mock.registers import Encoding, Field
from saj_local_mock.simulation import control as ctl
from saj_local_mock.simulation.faults import fault_word_key, pack_key

from .fields import (
    I16,
    I32,
    U16,
    U32,
    ZERO,
    Shape,
    command,
    counter_group,
    fixed,
    labelled,
    live,
    phase_key,
    setting,
    text,
)

if TYPE_CHECKING:
    from saj_local_mock.scenario import Scenario

SLOTS = 7
SLOT_STRIDE = 3
CHARGE_SLOTS_START = 0x3606
DISCHARGE_SLOTS_START = 0x361B
MAX_MODULES = 4
PERCENT_MAX = 100
TENTH_PERCENT_MAX = 1100
ANTI_REFLUX_RAW_MAX = 1000
FULL_SHARE_PERCENT = 100.0
BACKUP_CHARGE_PERCENT = 4.2
ISO_OPEN = 32767
SOFTWARE_VERSION = 1.002
PROTOCOL_VERSION = 1.0
VERSION_STEP = 0.001
CLEAR_FAULT_HISTORY = 1
CLEAR_CURRENT_FAULT = 2
CLEAR_FAULT_LABELS = {
    CLEAR_FAULT_HISTORY: "Clear fault history",
    CLEAR_CURRENT_FAULT: "Clear current fault",
}
RESTART_LABELS = {1: "Restart"}
CLEAR_POWER_HISTORY_LABELS = {1: "Clear energy history"}
FACTORY_RESET_LABELS = {1: "Factory reset"}
METER_MODES = {
    0: "No meter or CT",
    1: "Single-phase meter",
    2: "Three-phase three-wire meter",
    3: "Three-phase four-wire meter",
    10: "Three-phase four-wire meter, grid and PV",
    11: "Two three-phase three-wire meters",
    12: "Two three-phase four-wire meters",
    13: "Two single-phase meters",
    15: "Single-phase meter with two CT channels",
    20: "Grid CT",
    21: "Grid and PV CTs",
    42: "Dual-circuit three-phase four-wire meter",
}
BAUD_RATES = {
    0: "115200",
    1: "57600",
    2: "38400",
    3: "19200",
    4: "9600",
    5: "4800",
    6: "2400",
    7: "1200",
}
LED_MODES = {0: "All off", 1: "Outer ring on", 2: "Inner ring on", 3: "All on"}
ANTI_REFLUX_MODES = {
    0: "Off",
    1: "Total power",
    2: "Phase current",
    3: "Phase power",
}
TOU_OUTSIDE_MODES = {0: "Standby", 1: "Self-use"}
BATTERY_PROTOCOLS = {0: "Not in use", 22: "B2 CAN", 24: "SAJ-BU3"}
METER_MODE_THREE_PHASE_FOUR_WIRE = 3
# Registers each phase occupies in its group, so the next phase starts after them.
GRID_PORT_PHASE_REGISTERS = 7
INVERTER_PORT_PHASE_REGISTERS = 5
OFF_GRID_PORT_PHASE_REGISTERS = 6
STRING_REGISTERS = 3
METER_PHASE_REGISTERS = 6
METER_PHASES = 3
REACTIVE_POWER_WORDS = 2
MODULE_STATE_REGISTERS = 6
MODULE_ALARM_REGISTERS = 2
MODULE_DISCHARGE_WORDS = 2
THIRD_PHASE = 2
NO_BATTERY_PROTOCOL = 0
FACTORY_BLOCK_START = 0x8015
FACTORY_BLOCK_END = 0x8023
EMS_ENABLE_BIT_NAMES = (
    (ctl.EMS_STANDARD_BIT, "Inverter"),
    (ctl.EMS_BATTERY_BIT, "Battery"),
    (ctl.EMS_EXIT_BIT, "Inverter timeout exit"),
    (ctl.EMS_GRID_BIT, "Grid"),
)
EMS_ENABLE_OFF_LABEL = "Off"
EMS_ENABLE_LABEL_SEPARATOR = " + "


def _battery_protocol(*, scenario: Scenario, code: int) -> int:
    return code if scenario.battery.modules else NO_BATTERY_PROTOCOL


def ems_labels() -> dict[int, str]:
    """Every combination of the enable bits, named by the bits it sets."""
    labels = {0: EMS_ENABLE_OFF_LABEL}
    for bit, name in EMS_ENABLE_BIT_NAMES:
        labels |= {
            value | bit: (
                name if value == 0 else f"{label}{EMS_ENABLE_LABEL_SEPARATOR}{name}"
            )
            for value, label in labels.items()
        }
    return dict(sorted(labels.items()))


def information_fields(*, scenario: Scenario, spec: ModelSpec) -> list[Field]:
    fields = [
        fixed(address=0x8F00, name="device_type", value=spec.device_type),
        fixed(address=0x8F01, name="rated_power", value=scenario.device.rated_power_w),
        fixed(
            address=0x8F02,
            name="comms_protocol_version",
            value=PROTOCOL_VERSION,
            scale=0.001,
        ),
        text(
            address=0x8F03,
            name="serial_number",
            value=scenario.device.serial_number,
            length=10,
        ),
        text(
            address=0x8F0D,
            name="product_code",
            value=f"{spec.name.upper()}-MOCK",
            length=10,
        ),
    ]
    names = (
        "display_software",
        "master_software",
        "slave_software",
        "display_hardware",
        "control_hardware",
        "power_hardware",
    )
    fields += [
        fixed(
            address=0x8F17 + index,
            name=name,
            value=SOFTWARE_VERSION + index * VERSION_STEP,
            scale=0.001,
        )
        for index, name in enumerate(names)
    ]
    return fields


def factory_command_fields() -> list[Field]:
    return [
        command(address=0x8015, name="cmd_clear_faults", labels=CLEAR_FAULT_LABELS),
        command(address=0x801A, name="cmd_restart", labels=RESTART_LABELS),
        command(
            address=0x801B,
            name="cmd_clear_power_history",
            labels=CLEAR_POWER_HISTORY_LABELS,
        ),
        command(address=0x801C, name="cmd_factory_reset", labels=FACTORY_RESET_LABELS),
        command(address=0x8020, name="cmd_set_clock", enc=Encoding.CLOCK),
    ]


def _grid_ports(*, phases: int, house_flows: bool) -> list[Field]:
    fields: list[Field] = []
    grid_power_group = "inv" if house_flows else "grid"
    side_power_group = "load" if house_flows else "side"

    def key(*, group: str, phase: int, suffix: str) -> str:
        return phase_key(group=group, phase=phase, suffix=suffix, phases=phases)

    for phase, name in enumerate("RST"):
        base = 0x4031 + GRID_PORT_PHASE_REGISTERS * phase
        fields += [
            live(
                address=base,
                name=f"{name}_grid_voltage",
                source=key(group="grid", phase=phase, suffix="v"),
                scale=0.1,
            ),
            live(
                address=base + 1,
                name=f"{name}_grid_current",
                source=key(group="grid", phase=phase, suffix="a"),
                enc=I16,
                scale=0.01,
            ),
            live(
                address=base + 2,
                name=f"{name}_grid_frequency",
                source=key(group="grid", phase=phase, suffix="hz"),
                scale=0.01,
            ),
            live(
                address=base + 3,
                name=f"{name}_grid_dc",
                source=key(group="grid", phase=phase, suffix="dc"),
                enc=I16,
            ),
            live(
                address=base + 4,
                name=f"{name}_grid_power",
                source=key(group=grid_power_group, phase=phase, suffix="w"),
                enc=I16,
            ),
            live(
                address=base + 5,
                name=f"{name}_grid_apparent",
                source=key(group=grid_power_group, phase=phase, suffix="va"),
            ),
            live(
                address=base + 6,
                name=f"{name}_grid_power_factor",
                source=key(group="grid", phase=phase, suffix="pf"),
                enc=I16,
                scale=0.001,
            ),
        ]
        base = 0x4046 + INVERTER_PORT_PHASE_REGISTERS * phase
        fields += [
            live(
                address=base,
                name=f"{name}_inverter_voltage",
                source=key(group="inv", phase=phase, suffix="v"),
                scale=0.1,
            ),
            live(
                address=base + 1,
                name=f"{name}_inverter_current",
                source=key(group="inv", phase=phase, suffix="a"),
                enc=I16,
                scale=0.01,
            ),
            live(
                address=base + 2,
                name=f"{name}_inverter_frequency",
                source=key(group="inv", phase=phase, suffix="hz"),
                scale=0.01,
            ),
            live(
                address=base + 3,
                name=f"{name}_inverter_power",
                source=key(group="inv", phase=phase, suffix="w"),
                enc=I16,
            ),
            live(
                address=base + 4,
                name=f"{name}_inverter_apparent",
                source=key(group="inv", phase=phase, suffix="va"),
            ),
        ]
        base = 0x4055 + OFF_GRID_PORT_PHASE_REGISTERS * phase
        fields += [
            live(
                address=base,
                name=f"{name}_output_voltage",
                source=key(group="out", phase=phase, suffix="v"),
                scale=0.1,
            ),
            live(
                address=base + 1,
                name=f"{name}_output_current",
                source=key(group="out", phase=phase, suffix="a"),
                scale=0.01,
            ),
            live(
                address=base + 2,
                name=f"{name}_output_frequency",
                source=key(group="out", phase=phase, suffix="hz"),
                scale=0.01,
            ),
            live(
                address=base + 3,
                name=f"{name}_output_dvi",
                source=key(group="out", phase=phase, suffix="dc"),
                enc=I16,
            ),
            live(
                address=base + 4,
                name=f"{name}_output_power",
                source=key(group="out", phase=phase, suffix="w"),
            ),
            live(
                address=base + 5,
                name=f"{name}_output_apparent",
                source=key(group="out", phase=phase, suffix="va"),
            ),
        ]
    fields += [
        live(
            address=0x408D,
            name="R_side_voltage",
            source=key(group="side", phase=0, suffix="v"),
            scale=0.1,
        ),
        live(
            address=0x408E,
            name="R_side_current",
            source=key(group="side", phase=0, suffix="a"),
            scale=0.01,
        ),
        live(
            address=0x408F,
            name="R_side_frequency",
            source=key(group="side", phase=0, suffix="hz"),
            scale=0.01,
        ),
        live(
            address=0x4090,
            name="R_side_power",
            source=key(group=side_power_group, phase=0, suffix="w"),
        ),
        live(
            address=0x4091,
            name="S_side_voltage",
            source=key(group="side", phase=1, suffix="v"),
            scale=0.1,
        ),
        live(
            address=0x4092,
            name="S_side_power",
            source=key(group=side_power_group, phase=1, suffix="w"),
        ),
        live(
            address=0x4093,
            name="T_side_voltage",
            source=key(group="side", phase=THIRD_PHASE, suffix="v"),
            scale=0.1,
        ),
        live(
            address=0x4094,
            name="T_side_power",
            source=key(group=side_power_group, phase=THIRD_PHASE, suffix="w"),
        ),
    ]
    return fields


def _strings() -> list[Field]:
    fields: list[Field] = []
    for index in range(MAX_PV_STRINGS):
        number = index + 1
        base = 0x4071 + STRING_REGISTERS * index
        fields += [
            fixed(address=0x4013 + index, name=f"pv{number}_isolation", value=ISO_OPEN),
            live(
                address=base,
                name=f"pv{number}_voltage",
                source=f"pv{number}_v",
                scale=0.1,
            ),
            live(
                address=base + 1,
                name=f"pv{number}_current",
                source=f"pv{number}_a",
                scale=0.01,
            ),
            live(address=base + 2, name=f"pv{number}_power", source=f"pv{number}_w"),
        ]
    return fields


def _fault_register(*, address: int, name: str) -> Field:
    return live(
        address=address,
        name=name,
        source=fault_word_key(register=address),
        enc=U32,
    )


def _status_and_mirrors(*, scenario: Scenario) -> list[Field]:
    rated = scenario.device.rated_power_w
    return [
        live(address=0x4000, name="device_clock", source="clock_s", enc=Encoding.CLOCK),
        live(address=0x4004, name="operating_mode", source="operating_mode"),
        _fault_register(address=0x4005, name="main_fault_one"),
        _fault_register(address=0x4007, name="main_fault_two"),
        _fault_register(address=0x4009, name="main_fault_three"),
        _fault_register(address=0x400B, name="battery_fault"),
        live(
            address=0x4010,
            name="sink_temperature",
            source="sink_temp_c",
            enc=I16,
            scale=0.1,
        ),
        live(
            address=0x4011,
            name="ambient_temperature",
            source="ambient_temp_c",
            enc=I16,
            scale=0.1,
        ),
        fixed(address=0x4012, name="gfci", value=0, enc=I16),
        live(address=0x4019, name="connection_countdown", source="conn_time_s"),
        live(address=0x4022, name="running_mode", source="running_mode", enc=I16),
        fixed(
            address=0x4023, name="inverter_discharge_power_set", value=rated, enc=I16
        ),
        fixed(address=0x4024, name="inverter_charge_power_set", value=rated, enc=I16),
        fixed(
            address=0x4025,
            name="battery_discharge_current_set",
            value=300,
            enc=I16,
            scale=0.1,
        ),
        fixed(
            address=0x4026,
            name="battery_charge_current_set",
            value=300,
            enc=I16,
            scale=0.1,
        ),
        fixed(address=0x4027, name="battery_status_display", value=2048),
        fixed(
            address=0x4028,
            name="battery_protocol_set",
            value=_battery_protocol(
                scenario=scenario,
                code=scenario.device.model.battery_protocol_active,
            ),
            enc=I16,
        ),
        live(
            address=0x4029,
            name="charge_limit_mirror",
            source="mirror_charge_ceiling",
            enc=I16,
        ),
        live(
            address=0x402A,
            name="discharge_limit_mirror",
            source="mirror_discharge_floor",
            enc=I16,
        ),
        fixed(
            address=0x402B, name="depth_of_discharge_set", value=PERCENT_MAX, enc=I16
        ),
        live(address=0x402C, name="reserve_mirror", source="mirror_reserve", enc=I16),
        live(
            address=0x4030,
            name="meter_mode_mirror",
            source="mirror_meter_mode",
            enc=I16,
        ),
    ]


def _battery_and_power(*, house_flows: bool) -> list[Field]:
    dc_input_source = "inverter_w" if house_flows else "load_w"
    grid_total = "inverter_w" if house_flows else "grid_export_w"
    return [
        live(address=0x4067, name="bus_voltage_master", source="bus_v", scale=0.1),
        live(address=0x4068, name="bus_voltage_slave", source="bus_v", scale=0.1),
        live(address=0x4069, name="battery_voltage", source="battery_v", scale=0.1),
        live(
            address=0x406A,
            name="battery_current",
            source="battery_a",
            enc=I16,
            scale=0.01,
        ),
        live(address=0x406D, name="battery_power", source="battery_w", enc=I16),
        live(
            address=0x406E,
            name="battery_temperature",
            source="battery_temp_c",
            enc=I16,
            scale=0.1,
        ),
        live(
            address=0x406F,
            name="battery_energy_percent",
            source="soc_percent",
            scale=0.01,
        ),
        live(address=0x4095, name="direction_pv", source="direction_pv"),
        live(
            address=0x4096,
            name="direction_battery",
            source="direction_battery",
            enc=I16,
        ),
        live(address=0x4097, name="direction_grid", source="direction_grid", enc=I16),
        live(address=0x4098, name="direction_output", source="direction_output"),
        live(address=0x40A0, name="total_load_power", source=dc_input_source, enc=I16),
        live(address=0x40A1, name="ct_grid_power", source="ct_grid_w", enc=I16),
        live(address=0x40A2, name="ct_grid_apparent", source="ct_grid_w", enc=I16),
        live(address=0x40A3, name="ct_pv_power", source="ext_pv_w", enc=I16),
        live(address=0x40A4, name="ct_pv_apparent", source="ext_pv_w", enc=I16),
        live(address=0x40A5, name="pv_power", source="pv_w", enc=I16),
        live(address=0x40A6, name="battery_total_power", source="battery_w", enc=I16),
        live(address=0x40A7, name="grid_total_power", source=grid_total, enc=I16),
        live(address=0x40A8, name="grid_total_apparent", source=grid_total, enc=I16),
        live(address=0x40A9, name="inverter_total_power", source="inverter_w", enc=I16),
        live(
            address=0x40AA, name="inverter_total_apparent", source="inverter_w", enc=I16
        ),
        live(address=0x40AB, name="backup_load_power", source="backup_w"),
        live(address=0x40AC, name="backup_load_apparent", source="backup_w"),
        live(address=0x40AD, name="grid_load_power", source="grid_load_w", enc=I16),
    ]


def realtime_energy_fields(
    *,
    scenario: Scenario,
    phases: int,
    extended: bool,
    house_flows: bool = False,
) -> list[Field]:
    fields = _status_and_mirrors(scenario=scenario) + _grid_ports(
        phases=phases, house_flows=house_flows
    )
    fields += _strings() + _battery_and_power(house_flows=house_flows)
    groups = [
        (0x40BF, "pv", "pv_energy"),
        (0x40C7, "bat_charge", "battery_charge_energy"),
        (0x40CF, "bat_discharge", "battery_discharge_energy"),
        (0x40D7, "pv", "inverter_generation_energy"),
        (0x40DF, "load", "load_energy"),
        (0x40E7, "backup_load", "backup_load_energy"),
        (0x40EF, "sell", "sell_energy"),
        (0x40F7, "feed_in", "feed_in_energy"),
        (0x4137, "pv_2", "pv_energy_two"),
        (0x413F, "pv_3", "pv_energy_three"),
    ]
    for start, base, name in groups:
        fields += counter_group(start=start, base=base, name=name)
    for start, base, name, phase in (
        (0x4147, "sell_phase2", "sell_energy_two", 1),
        (0x414F, "sell_phase3", "sell_energy_three", 2),
        (0x4157, "feed_in_phase2", "feed_in_energy_two", 1),
        (0x415F, "feed_in_phase3", "feed_in_energy_three", 2),
    ):
        fields += counter_group(
            start=start, base=base, name=name, present=phase < phases
        )
    if extended:
        fields += counter_group(start=0x4167, base="sum_feed_in", name="sum_feed_in")
        fields += counter_group(start=0x416F, base="sum_sell", name="sum_sell")
    return fields


def schedule_fields() -> list[Field]:
    fields = [
        setting(
            address=0x3604,
            name=ctl.CHARGE_ENABLE_MASK,
            value=0,
            shape=Shape(maximum=127),
        ),
        setting(
            address=0x3605,
            name=ctl.DISCHARGE_ENABLE_MASK,
            value=0,
            shape=Shape(maximum=127),
        ),
    ]
    for kind, first in (
        ("charge", CHARGE_SLOTS_START),
        ("discharge", DISCHARGE_SLOTS_START),
    ):
        for slot in range(1, SLOTS + 1):
            base = first + SLOT_STRIDE * (slot - 1)
            for offset, part in enumerate(("start", "end", "days_power")):
                name = ctl.slot_key(kind=kind, index=slot, part=part)
                fields.append(setting(address=base + offset, name=name, value=0))
    return fields


def _power_share_fields() -> list[Field]:
    """Passive and battery power shares, in percent with one decimal."""
    share = Shape(scale=0.1, maximum=TENTH_PERCENT_MAX)
    return [
        setting(
            address=0x3637,
            name="passive_grid_charge_power",
            value=FULL_SHARE_PERCENT,
            shape=share,
        ),
        setting(
            address=0x3638,
            name="passive_grid_discharge_power",
            value=FULL_SHARE_PERCENT,
            shape=share,
        ),
        setting(
            address=0x3639,
            name=ctl.BACKUP_CHARGE_POWER,
            value=BACKUP_CHARGE_PERCENT,
            shape=share,
        ),
        setting(
            address=0x363A,
            name="passive_battery_discharge_power",
            value=FULL_SHARE_PERCENT,
            shape=share,
        ),
        setting(
            address=0x364D,
            name="battery_charge_power",
            value=FULL_SHARE_PERCENT,
            shape=share,
        ),
        setting(
            address=0x364E,
            name="battery_discharge_power",
            value=FULL_SHARE_PERCENT,
            shape=share,
        ),
        setting(
            address=0x364F,
            name="grid_charge_power",
            value=FULL_SHARE_PERCENT,
            shape=share,
        ),
        setting(
            address=0x3650,
            name="grid_discharge_power",
            value=FULL_SHARE_PERCENT,
            shape=share,
        ),
    ]


def settings_fields(
    *, scenario: Scenario, modes: dict[int, str], extended: bool
) -> list[Field]:
    meter_mode = METER_MODE_THREE_PHASE_FOUR_WIRE if scenario.meters.meter_a else 0
    percent = Shape(maximum=PERCENT_MAX)
    fields = [
        *schedule_fields(),
        *_power_share_fields(),
        setting(
            address=0x3630,
            name="meter_enable",
            value=meter_mode,
            shape=labelled(labels=METER_MODES),
        ),
        setting(
            address=0x3631,
            name="meter_address",
            value=1,
            shape=Shape(minimum=1, maximum=255),
        ),
        setting(
            address=0x3633,
            name="master_rs485_address",
            value=1,
            shape=Shape(minimum=1, maximum=127),
        ),
        setting(
            address=0x3634,
            name="master_rs485_baud",
            value=0,
            shape=labelled(labels=BAUD_RATES),
        ),
        setting(
            address=0x3636,
            name="passive_charge_enable",
            value=0,
            shape=Shape(maximum=2),
        ),
        setting(
            address=0x363B,
            name="battery_protocol",
            value=_battery_protocol(
                scenario=scenario,
                code=scenario.device.model.battery_protocol_setting,
            ),
            shape=labelled(
                labels={
                    code: BATTERY_PROTOCOLS[code]
                    for code in (
                        NO_BATTERY_PROTOCOL,
                        scenario.device.model.battery_protocol_setting,
                    )
                }
            ),
        ),
        setting(
            address=0x3643, name="battery_auto_wake", value=0, shape=Shape(maximum=1)
        ),
        setting(
            address=0x3644, name=ctl.DISCHARGE_FLOOR_ON_GRID, value=10, shape=percent
        ),
        setting(
            address=0x3645, name=ctl.DISCHARGE_FLOOR_OFF_GRID, value=10, shape=percent
        ),
        setting(
            address=0x3646, name=ctl.CHARGE_CEILING, value=PERCENT_MAX, shape=percent
        ),
        setting(
            address=0x3647,
            name=ctl.APP_MODE,
            value=0,
            shape=labelled(labels=modes),
        ),
        setting(address=0x3651, name=ctl.BACKUP_RESERVE, value=50, shape=percent),
        setting(
            address=0x365A,
            name=ctl.ANTI_REFLUX_POWER_LIMIT,
            value=0,
            shape=Shape(scale=0.001, maximum=ANTI_REFLUX_RAW_MAX),
        ),
        setting(
            address=0x365B,
            name="anti_reflux_current_limit",
            value=0,
            shape=Shape(scale=0.01, maximum=300),
        ),
        setting(
            address=0x365C,
            name=ctl.ANTI_REFLUX_MODE,
            value=0,
            shape=labelled(labels=ANTI_REFLUX_MODES),
        ),
        setting(
            address=0x365F,
            name=ctl.TOU_OUTSIDE_MODE,
            value=1,
            shape=labelled(labels=TOU_OUTSIDE_MODES),
        ),
        setting(
            address=0x3660,
            name="time_sharing_discharge_allow",
            value=0,
            shape=Shape(maximum=1),
        ),
        setting(
            address=0x3675,
            name="led_switch",
            value=3,
            shape=labelled(labels=LED_MODES),
        ),
    ]
    if extended:
        fields += [
            setting(
                address=0x3602,
                name="settings_serial",
                value=156,
                shape=Shape(maximum=0xFFFF),
            ),
            fixed(address=0x3603, name="settings_protocol_version", value=1004),
            setting(
                address=0x3680,
                name="slave_rs485_address",
                value=1,
                shape=Shape(minimum=1, maximum=1),
            ),
            setting(
                address=0x3681,
                name="slave_rs485_baud",
                value=4,
                shape=labelled(labels=BAUD_RATES),
            ),
        ]
    return fields


def meter_fields(*, phases: int, extended: bool) -> list[Field]:
    fields = [
        live(address=0xA03C, name="meter_a_status", source="meter_a_status"),
        live(address=0xA053, name="meter_b_status", source="meter_b_status"),
    ]
    for meter, status_base in (("a", 0xA03D), ("b", 0xA054)):
        for phase in range(METER_PHASES):
            present = phase < phases

            def key(
                *,
                suffix: str,
                meter: str = meter,
                phase: int = phase,
                present: bool = present,
            ) -> str:
                return f"meter_{meter}_{'rst'[phase]}_{suffix}" if present else ZERO

            base = status_base + METER_PHASE_REGISTERS * phase
            fields += [
                live(
                    address=base,
                    name=f"meter_{meter}_voltage_{phase + 1}",
                    source=key(suffix="v"),
                    scale=0.1,
                ),
                live(
                    address=base + 1,
                    name=f"meter_{meter}_current_{phase + 1}",
                    source=key(suffix="a"),
                    enc=I16,
                    scale=0.01,
                ),
                live(
                    address=base + 2,
                    name=f"meter_{meter}_power_{phase + 1}",
                    source=key(suffix="w"),
                    enc=I16,
                ),
                live(
                    address=base + 3,
                    name=f"meter_{meter}_apparent_{phase + 1}",
                    source=key(suffix="va"),
                ),
                live(
                    address=base + 4,
                    name=f"meter_{meter}_power_factor_{phase + 1}",
                    source=key(suffix="pf"),
                    enc=I16,
                    scale=0.001,
                ),
                live(
                    address=base + 5,
                    name=f"meter_{meter}_frequency_{phase + 1}",
                    source=key(suffix="hz"),
                    scale=0.01,
                ),
            ]
    if extended:
        for index in range(METER_PHASES):
            fields.append(
                fixed(
                    address=0xA066 + index,
                    name=f"meter_a_power_high_{index + 1}",
                    value=0,
                    enc=I16,
                )
            )
            fields.append(
                fixed(
                    address=0xA069 + index,
                    name=f"meter_b_power_high_{index + 1}",
                    value=0,
                    enc=I16,
                )
            )
            fields.append(
                fixed(
                    address=0xA06C + REACTIVE_POWER_WORDS * index,
                    name=f"meter_a_reactive_{index + 1}",
                    value=0,
                    enc=I32,
                )
            )
            fields.append(
                fixed(
                    address=0xA072 + REACTIVE_POWER_WORDS * index,
                    name=f"meter_b_reactive_{index + 1}",
                    value=0,
                    enc=I32,
                )
            )
    return fields


def battery_fields(*, populated: bool) -> list[Field]:
    def reading(
        *,
        address: int,
        name: str,
        source: str,
        enc: Encoding = U16,
        scale: float = 1.0,
    ) -> Field:
        return live(
            address=address,
            name=name,
            source=source if populated else ZERO,
            enc=enc,
            scale=scale,
        )

    fields = [
        reading(address=0xA000, name="battery_count", source="battery_modules"),
        reading(address=0xA001, name="battery_capacity", source="battery_capacity_ah"),
        reading(
            address=0xA00A,
            name="battery_user_capacity",
            source="battery_user_capacity_ah",
        ),
        reading(address=0xA00B, name="battery_online", source="battery_online_mask"),
        reading(
            address=0xA032,
            name="battery_voltage_high_protection",
            source="battery_protect_high_v",
            scale=0.1,
        ),
        reading(
            address=0xA033,
            name="battery_voltage_low_warning",
            source="battery_warn_low_v",
            scale=0.1,
        ),
        reading(
            address=0xA034,
            name="battery_charge_voltage",
            source="battery_charge_v",
            scale=0.1,
        ),
        reading(
            address=0xA035,
            name="battery_discharge_cutoff",
            source="battery_cutoff_v",
            scale=0.1,
        ),
        reading(
            address=0xA036,
            name="battery_discharge_current_limit",
            source="battery_current_limit_a",
            scale=0.1,
        ),
        reading(
            address=0xA037,
            name="battery_charge_current_limit",
            source="battery_current_limit_a",
            scale=0.1,
        ),
    ]
    for module in range(MAX_MODULES):
        number = module + 1
        base = 0xA00C + MODULE_STATE_REGISTERS * module
        prefix = f"module{number}"
        fields += [
            live(
                address=0xA002 + MODULE_ALARM_REGISTERS * module,
                name=f"battery{number}_fault",
                source=pack_key(pack=number, kind="fault"),
            ),
            live(
                address=0xA003 + MODULE_ALARM_REGISTERS * module,
                name=f"battery{number}_warning",
                source=pack_key(pack=number, kind="warning"),
            ),
            reading(
                address=base,
                name=f"battery{number}_soc",
                source=f"{prefix}_soc_percent",
                scale=0.01,
            ),
            reading(
                address=base + 1,
                name=f"battery{number}_soh",
                source=f"{prefix}_soh_percent",
                scale=0.01,
            ),
            reading(
                address=base + 2,
                name=f"battery{number}_voltage",
                source=f"{prefix}_v",
                scale=0.1,
            ),
            reading(
                address=base + 3,
                name=f"battery{number}_current",
                source=f"{prefix}_a",
                enc=I16,
                scale=0.01,
            ),
            reading(
                address=base + 4,
                name=f"battery{number}_temperature",
                source=f"{prefix}_temp_c",
                enc=I16,
                scale=0.1,
            ),
            reading(
                address=base + 5,
                name=f"battery{number}_cycles",
                source=f"{prefix}_cycles",
            ),
            reading(
                address=0xA02A + MODULE_DISCHARGE_WORDS * module,
                name=f"battery{number}_discharged_high",
                source=f"{prefix}_discharge_kwh_high",
            ),
            reading(
                address=0xA02B + MODULE_DISCHARGE_WORDS * module,
                name=f"battery{number}_discharged_low",
                source=f"{prefix}_discharge_kwh_low",
            ),
        ]
    return fields
