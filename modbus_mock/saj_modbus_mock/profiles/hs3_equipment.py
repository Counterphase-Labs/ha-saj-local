"""HS3-only blocks: parallel, averages, EV, Ethernet and EMS."""

from typing import TYPE_CHECKING

from saj_modbus_mock.models import MAX_PV_STRINGS
from saj_modbus_mock.registers import Encoding, Field
from saj_modbus_mock.simulation import control as ctl
from saj_modbus_mock.simulation import ev_charger as ev

from .common import BAUD_CODES, ems_combinations
from .fields import (
    I16,
    I32,
    U16,
    U32,
    ZERO,
    Shape,
    blob,
    counter_group,
    fixed,
    live,
    setting,
    text,
)

if TYPE_CHECKING:
    from saj_modbus_mock.scenario import Scenario

PARALLEL_POWER_REGISTERS = (
    (0x4204, 0x420C, "pv_w", U16),
    (0x4205, 0x420D, "battery_w", I16),
    (0x4206, 0x420E, "grid_w", I16),
    (0x4207, 0x420F, "load_w", U16),
    (0x4208, 0x4210, "backup_w", I16),
    (0x420A, 0x4211, "grid_load_w", I16),
)
PARALLEL_ENERGY_GROUPS = (
    (0x4215, "pv", "pv"),
    (0x421D, "bat_charge", "battery_charge"),
    (0x4225, "bat_discharge", "battery_discharge"),
    (0x422D, "sell", "sell_one"),
    (0x4235, "", "sell_two"),
    (0x423D, "", "sell_three"),
    (0x4245, "feed_in", "feed_in_one"),
    (0x424D, "", "feed_in_two"),
    (0x4255, "", "feed_in_three"),
    (0x425D, "load", "load"),
    (0x4265, "feed_in", "vector_feed_in"),
    (0x426D, "sell", "vector_sell"),
    (0x4275, "ext_pv", "pv_meter"),
)
AVERAGE_GROUPS = (
    (0x513E, "grid", "avg_grid_w"),
    (0x514F, "inv", "avg_inverter_w"),
    (0x5160, "load", "avg_load_w"),
    (0x5171, "gridload", "avg_grid_load_w"),
    (0x5182, "out", "avg_backup_w"),
    (0x51A5, "gen", ZERO),
)
AVERAGE_PV_TOTAL = 0x5193
AVERAGE_TOTAL_WORDS = 2
AVERAGE_PHASE_REGISTERS = 5
AVERAGE_PV_REGISTERS = 4
EV_PHASE_REGISTERS = 2
AVERAGE_BATTERY = 0x51B6
EV_SETTINGS_START = 0x4B00
EV_EMS_COMMAND_MAXIMUM = 0b111
EV_SLOT_START = 0x4B20
EV_SLOT_STRIDE = 5
EV_SETTINGS_LENGTH = 0x48
ETHERNET_TEXT_WORDS = 8
ETHERNET_FIELDS = (
    (0x0F08, "ip_address", "192.168.1.50"),
    (0x0F10, "subnet_mask", "255.255.255.0"),
    (0x0F18, "gateway", "192.168.1.1"),
    (0x0F20, "first_dns", "192.168.1.1"),
    (0x0F28, "alternate_dns", ""),
)
CHECKSUM = 0x4D2B
MAC_ADDRESS = 0x02AA4A000001
MAC_WORDS = 3
EV_TEXT = (
    (0x3024, "ev_serial_number", 16, "EVMOCK0000000001"),
    (0x3034, "ev_model", 8, "EVC-11K"),
    (0x303C, "ev_software", 5, "1.0.0"),
    (0x3041, "ev_hardware", 5, "A1"),
)
EV_MODES = frozenset(range(5))
EV_BAUD = BAUD_CODES
PORT_MODES = frozenset({0, 1, 2})
NET_MODES = frozenset({0, 1})
EMS_DEFAULT_TIMEOUT_S = 300
EMS_DEFAULT_CURRENT = 20.0
EMS_SHARE_SCALE = 0.0001
EMS_ENABLE_INITIAL = 0


def parallel_fields(*, scenario: Scenario) -> list[Field]:
    inverters = scenario.parallel.inverters
    fields = [
        fixed(address=0x4200, name="parallel_mode", value=0),
        fixed(address=0x4201, name="parallel_id", value=0),
        fixed(address=0x4202, name="parallel_count", value=inverters),
        fixed(address=0x4203, name="parallel_real_count", value=inverters),
        live(address=0x4209, name="parallel_soc", source="parallel_soc_percent"),
        live(
            address=0x420B,
            name="parallel_total_capacity",
            source="parallel_capacity_ah",
        ),
        live(address=0x4212, name="parallel_meter_b_power", source="ext_pv_w", enc=I32),
    ]
    for low, high, key, high_encoding in PARALLEL_POWER_REGISTERS:
        fields.append(
            live(address=low, name=f"parallel_{key}_low", source=f"parallel_{key}_low")
        )
        fields.append(
            live(
                address=high,
                name=f"parallel_{key}_high",
                source=f"parallel_{key}_high",
                enc=high_encoding,
            )
        )
    for start, base, name in PARALLEL_ENERGY_GROUPS:
        fields += counter_group(
            start=start,
            base=base,
            name=f"parallel_{name}",
            present=bool(base),
            parallel=True,
        )
    return fields


def _average_group(*, start: int, group: str, total_key: str) -> list[Field]:
    fields = [
        live(address=start, name=f"average_{group}_total", source=total_key, enc=I32)
    ]
    for phase, name in enumerate("rst"):
        base = start + AVERAGE_TOTAL_WORDS + AVERAGE_PHASE_REGISTERS * phase
        prefix = f"avg_{group}_{name}"
        known = group != "gen" and phase < len("rst")
        fields += [
            live(
                address=base,
                name=f"average_{group}_{name}_power",
                source=f"{prefix}_w" if known else ZERO,
                enc=I32,
            ),
            live(
                address=base + 2,
                name=f"average_{group}_{name}_voltage",
                source=f"{prefix}_v" if known else ZERO,
                scale=0.1,
            ),
            live(
                address=base + 3,
                name=f"average_{group}_{name}_current",
                source=f"{prefix}_a" if known else ZERO,
                enc=I16,
                scale=0.01,
            ),
            live(
                address=base + 4,
                name=f"average_{group}_{name}_frequency",
                source=f"{prefix}_hz" if known else ZERO,
                scale=0.01,
            ),
        ]
    return fields


def average_fields() -> list[Field]:
    fields: list[Field] = []
    for start, group, total in AVERAGE_GROUPS:
        fields += _average_group(start=start, group=group, total_key=total)
    fields.append(
        live(
            address=AVERAGE_PV_TOTAL,
            name="average_pv_total",
            source="avg_pv_w",
            enc=I32,
        )
    )
    for index in range(1, MAX_PV_STRINGS + 1):
        base = (
            AVERAGE_PV_TOTAL + AVERAGE_TOTAL_WORDS + AVERAGE_PV_REGISTERS * (index - 1)
        )
        fields += [
            live(
                address=base,
                name=f"average_pv{index}_voltage",
                source=f"avg_pv{index}_v",
                scale=0.1,
            ),
            live(
                address=base + 1,
                name=f"average_pv{index}_current",
                source=f"avg_pv{index}_a",
                scale=0.01,
            ),
            live(
                address=base + 2,
                name=f"average_pv{index}_power",
                source=f"avg_pv{index}_w",
                enc=U32,
            ),
        ]
    fields += [
        live(
            address=AVERAGE_BATTERY,
            name="average_battery_power",
            source="avg_battery_w",
            enc=I32,
        ),
        live(
            address=AVERAGE_BATTERY + 2,
            name="average_battery_soc",
            source="avg_soc_percent",
            scale=0.01,
        ),
        live(
            address=AVERAGE_BATTERY + 3,
            name="average_battery_one_power",
            source="avg_battery_w",
            enc=I32,
        ),
        live(
            address=AVERAGE_BATTERY + 5,
            name="average_battery_one_voltage",
            source="avg_battery_v",
            scale=0.1,
        ),
        live(
            address=AVERAGE_BATTERY + 6,
            name="average_battery_one_current",
            source="avg_battery_a",
            enc=I16,
            scale=0.01,
        ),
        live(
            address=AVERAGE_BATTERY + 7,
            name="average_battery_one_soc",
            source="avg_soc_percent",
            scale=0.01,
        ),
        live(
            address=AVERAGE_BATTERY + 8,
            name="average_battery_one_temperature",
            source="avg_battery_temp_c",
            enc=I16,
            scale=0.1,
        ),
    ]
    return fields


def ethernet_fields() -> list[Field]:
    fields = [
        fixed(address=0x0F00, name="ethernet_checksum", value=CHECKSUM),
        fixed(address=0x0F01, name="ethernet_block_length", value=0x30),
        fixed(address=0x0F02, name="ethernet_sequence", value=1),
        fixed(
            address=0x0F03, name="ethernet_protocol_version", value=1000, scale=0.001
        ),
        blob(address=0x0F04, name="ethernet_mac", value=MAC_ADDRESS, length=MAC_WORDS),
        setting(
            address=0x0F07,
            name="ethernet_net_mode",
            value=1,
            shape=Shape(options=NET_MODES),
        ),
    ]
    for address, name, value in ETHERNET_FIELDS:
        fields.append(
            setting(
                address=address,
                name=name,
                value=value,
                shape=Shape(enc=Encoding.TEXT, length=ETHERNET_TEXT_WORDS),
            )
        )
    return fields


def ev_settings_fields(*, scenario: Scenario) -> list[Field]:
    charger = scenario.ev_charger
    installed = int(charger.installed)
    fields = [
        fixed(address=0x4B00, name="ev_settings_checksum", value=CHECKSUM),
        fixed(address=0x4B01, name="ev_settings_length", value=EV_SETTINGS_LENGTH),
        fixed(address=0x4B02, name="ev_settings_sequence", value=1),
        fixed(address=0x4B03, name="ev_settings_version", value=1000),
        setting(
            address=0x4B04, name=ev.EV_ENABLED, value=installed, shape=Shape(maximum=1)
        ),
        setting(
            address=0x4B05,
            name="ev_address",
            value=1,
            shape=Shape(minimum=1, maximum=127),
        ),
        setting(address=0x4B06, name="ev_baud", value=4, shape=Shape(options=EV_BAUD)),
        setting(
            address=0x4B07,
            name="ev_device_count",
            value=1,
            shape=Shape(minimum=1, maximum=3),
        ),
        setting(
            address=0x4B08,
            name="ev_comm_lost_seconds",
            value=3,
            shape=Shape(minimum=1, maximum=6),
        ),
        setting(
            address=0x4B09,
            name="ev_port_mode",
            value=1,
            shape=Shape(options=PORT_MODES),
        ),
        setting(
            address=0x4B0A,
            name="ev_port_address",
            value=1,
            shape=Shape(minimum=1, maximum=254),
        ),
        setting(
            address=0x4B12,
            name=ev.EV_MODE,
            value=ev.MODE_FORCED,
            shape=Shape(options=EV_MODES),
        ),
        setting(
            address=0x4B14,
            name=ev.EV_CHARGE_POWER,
            value=charger.max_power_w,
            shape=Shape(enc=U32, maximum=charger.max_power_w),
        ),
        setting(address=0x4B43, name=ev.EV_FUNCTION, value=0),
        setting(
            address=0x4B46,
            name=ev.EV_EMS_COMMAND,
            value=1,
            shape=Shape(maximum=EV_EMS_COMMAND_MAXIMUM),
        ),
        setting(
            address=0x4B47,
            name=ev.EV_EMS_CURRENT,
            value=6.0,
            shape=Shape(scale=0.1, minimum=60, maximum=320),
        ),
    ]
    for slot in range(1, ev.SLOTS + 1):
        base = EV_SLOT_START + EV_SLOT_STRIDE * (slot - 1)
        fields += [
            setting(address=base, name=ev.slot_key(index=slot, part="start"), value=0),
            setting(
                address=base + 1, name=ev.slot_key(index=slot, part="end"), value=0
            ),
            setting(
                address=base + 2, name=ev.slot_key(index=slot, part="date"), value=0
            ),
            setting(
                address=base + 3,
                name=ev.slot_key(index=slot, part="power_w"),
                value=0,
                shape=Shape(enc=U32),
            ),
        ]
    return fields


def ev_data_fields() -> list[Field]:
    fields = [
        text(address=address, name=name, value=value, length=length)
        for address, name, length, value in EV_TEXT
    ]
    fields += [
        live(address=0x3046, name="ev_phase_count", source="ev_phases"),
        live(address=0x3047, name="ev_min_power", source="ev_min_power_w"),
        live(address=0x3048, name="ev_max_power", source="ev_max_power_w", enc=U32),
        live(address=0x309C, name="ev_work_mode", source="mirror_ev_mode"),
        live(address=0x309D, name="ev_status", source="ev_state"),
        live(address=0x30A4, name="ev_total_power", source="ev_power_w", enc=U32),
        live(address=0x30A6, name="ev_charge_minutes", source="ev_session_minutes"),
        live(address=0x30A7, name="ev_session_energy", source="ev_session_wh", enc=U32),
        live(address=0x30A9, name="ev_total_energy", source="ev_total_wh", enc=U32),
        fixed(address=0x30AB, name="ev_error_one", value=0, enc=U32),
        fixed(address=0x30AD, name="ev_error_two", value=0, enc=U32),
        live(address=0x30AF, name="ev_control_pilot_voltage", source="ev_cp_v"),
        live(address=0x30B0, name="ev_duty", source="ev_duty_percent", scale=0.001),
        live(address=0x30B6, name="ev_power_state", source="ev_on"),
        live(
            address=0x30B7, name="ev_set_current", source="ev_set_current_a", scale=0.1
        ),
        live(
            address=0x30B8, name="ev_start_time", source="ev_session_start_s", enc=U32
        ),
        live(address=0x30BA, name="ev_end_time", source="ev_session_end_s", enc=U32),
    ]
    for index, name in enumerate("rst"):
        fields.append(
            live(
                address=0x309E + EV_PHASE_REGISTERS * index,
                name=f"ev_{name}_voltage",
                source=f"ev_{name}_v",
                scale=0.1,
            )
        )
        fields.append(
            live(
                address=0x309F + EV_PHASE_REGISTERS * index,
                name=f"ev_{name}_current",
                source=f"ev_{name}_a",
                scale=0.1,
            )
        )
    return fields


def ems_fields() -> list[Field]:
    share = EMS_SHARE_SCALE
    return [
        setting(
            address=0x8400,
            name=ctl.EMS_ENABLE,
            value=EMS_ENABLE_INITIAL,
            shape=Shape(options=ems_combinations()),
        ),
        setting(address=0x8401, name=ctl.EMS_TIMEOUT, value=EMS_DEFAULT_TIMEOUT_S),
        setting(
            address=0x8402,
            name=ctl.EMS_INVERTER_TARGET,
            value=0,
            shape=Shape(enc=I16, scale=share, keepalive_bit=0b001001),
        ),
        setting(
            address=0x8403,
            name=ctl.EMS_BATTERY_CHARGE_CURRENT,
            value=EMS_DEFAULT_CURRENT,
            shape=Shape(scale=0.1),
        ),
        setting(
            address=0x8404,
            name=ctl.EMS_BATTERY_DISCHARGE_CURRENT,
            value=EMS_DEFAULT_CURRENT,
            shape=Shape(scale=0.1),
        ),
        setting(
            address=0x8405,
            name=ctl.EMS_BATTERY_TARGET,
            value=0,
            shape=Shape(enc=I16, scale=share, keepalive_bit=0b000010),
        ),
        setting(
            address=0x840F, name=ctl.EMS_BUY_LIMIT, value=1.0, shape=Shape(scale=share)
        ),
        setting(
            address=0x8410, name=ctl.EMS_SELL_LIMIT, value=1.0, shape=Shape(scale=share)
        ),
        setting(
            address=0x8411,
            name=ctl.EMS_GRID_TARGET,
            value=0,
            shape=Shape(enc=I16, scale=share, keepalive_bit=0b100000),
        ),
        setting(
            address=0x8412,
            name=ctl.EMS_PV_LIMIT,
            value=ctl.EMS_NO_PV_LIMIT,
            shape=Shape(scale=share),
        ),
    ]
