from . import (
    DERIVED_PLACEMENTS,
    METER_A_PROBE,
    METER_B_PROBE,
    PARALLEL_PROBE,
    Comparison,
    Condition,
    EnableBitMethod,
    Equipment,
    Evidence,
    FamilyPlacement,
    FunctionCode,
    PowerFunction,
    Probe,
    Profile,
    Replacement,
    Shape,
    Span,
    placements_by_evidence,
)
from .faults import FaultMap
from .shared_faults import INVERTER_FAULT_WORDS, SHARED_INVERTER_FAULTS

PHASES = (1, 2, 3)


def _phase_keys(pattern: str) -> tuple[str, ...]:
    return tuple(pattern.format(phase) for phase in PHASES)


EMS_TIMEOUT = "ems_timeout"
EMS_LIMITS = (
    "ems_battery_charge_current_limit",
    "ems_battery_discharge_current_limit",
    "ems_inverter_import_power_limit",
    "ems_inverter_export_power_limit",
    "ems_pv_power_limit",
)

FAULTS = FaultMap(
    words={
        **INVERTER_FAULT_WORDS,
        "ev_fault_word_1": 0x30AB,
        "ev_fault_word_2": 0x30AD,
    },
    named={
        **SHARED_INVERTER_FAULTS,
        "inverter_fault_ct_device": {0x4005: (6,)},
        "inverter_fault_afci_communication": {0x4005: (7,)},
        "inverter_fault_slave_communication": {0x4005: (8,)},
        "inverter_fault_pv_meter_communication": {0x4005: (9,)},
        "inverter_fault_ev_charger_communication": {0x4005: (10,)},
        "inverter_fault_grid_phase_s_overvoltage": {0x4005: (13,)},
        "inverter_fault_grid_phase_s_undervoltage": {0x4005: (14,)},
        "inverter_fault_dcdc_communication": {0x4005: (19,)},
        "inverter_fault_dcdc_device": {0x4005: (20,)},
        "inverter_fault_parallel_communication": {0x4005: (21,), 0x4009: (25,)},
        "inverter_fault_pv_overvoltage": {0x4005: (26,)},
        "inverter_fault_arc_device": {0x4007: (5,)},
        "battery_fault_internal_communication": {0x400B: (0,)},
        "battery_fault_pack_sequence": {0x400B: (1,)},
        "battery_fault_discharge_overcurrent": {0x400B: (2,)},
        "battery_fault_charge_overcurrent": {0x400B: (3,)},
        "battery_fault_total_undervoltage": {0x400B: (4,)},
        "battery_fault_total_overvoltage": {0x400B: (5,)},
        "battery_fault_cell_undervoltage": {0x400B: (6,)},
        "battery_fault_cell_overvoltage": {0x400B: (7,)},
        "battery_fault_hardware": {0x400B: (8,)},
        "battery_fault_charge_cold": {0x400B: (9,)},
        "battery_fault_charge_hot": {0x400B: (10,)},
        "battery_fault_discharge_cold": {0x400B: (11,)},
        "battery_fault_discharge_hot": {0x400B: (12,)},
        "battery_fault_relay": {0x400B: (13,)},
        "battery_fault_precharge": {0x400B: (14,)},
        "battery_fault_insulation": {0x400B: (15,)},
        "battery_fault_bms_incompatible": {0x400B: (16,)},
        "battery_fault_cell_supplier_incompatible": {0x400B: (17,)},
        "battery_fault_cell_incompatible": {0x400B: (18,)},
        "battery_fault_voltage_level_mismatch": {0x400B: (19,)},
        "battery_fault_breaker_open": {0x400B: (20,)},
        "battery_fault_cell_temperature_difference": {0x400B: (21,)},
        "battery_fault_cell_voltage_difference_2": {0x400B: (22,)},
        "battery_fault_cell_voltage_difference_1": {0x400B: (23,)},
        "battery_fault_cell_over_temperature": {0x400B: (24,)},
        "battery_fault_short_circuit": {0x400B: (25,)},
        "battery_fault_total_voltage_matching": {0x400B: (26,)},
        "battery_fault_system_locked": {0x400B: (27,)},
        "battery_fault_fuse": {0x400B: (28,)},
        "battery_fault_charging_port_overvoltage": {0x400B: (29,)},
        "ev_fault_relay_over_temperature": {0x30AB: (0,)},
        "ev_fault_overload": {0x30AB: (1,)},
        "ev_fault_ac_overvoltage": {0x30AB: (2,)},
        "ev_fault_ac_undervoltage": {0x30AB: (3,)},
        "ev_fault_ac_overcurrent": {0x30AB: (4,)},
        "ev_fault_ac_overfrequency": {0x30AB: (5,)},
        "ev_fault_ac_underfrequency": {0x30AB: (6,)},
        "ev_fault_dc_residual_current_a": {0x30AB: (7,)},
        "ev_fault_emergency_stop": {0x30AB: (8,)},
        "ev_fault_under_temperature": {0x30AB: (9,)},
        "ev_fault_ac_residual_current": {0x30AB: (10,)},
        "ev_fault_input_terminal_over_temperature": {0x30AB: (11,)},
        "ev_fault_bluetooth": {0x30AB: (12,)},
        "ev_fault_dc_residual_current_b": {0x30AB: (13,)},
        "ev_fault_relay": {0x30AB: (14,)},
        "ev_fault_grounding": {0x30AB: (15,)},
        "ev_fault_phase_sequence": {0x30AB: (16,)},
        "ev_fault_rcd_circuit": {0x30AB: (17,)},
        "ev_fault_rs485_timeout": {0x30AB: (18,)},
        "ev_fault_supply": {0x30AB: (19,)},
        "ev_fault_meter": {0x30AB: (22,)},
        "ev_fault_control_pilot": {0x30AB: (23,)},
        "ev_fault_connector_lock": {0x30AB: (29,)},
        "ev_fault_connector_current": {0x30AB: (30,)},
        "ev_fault_dc_residual_current_c": {0x30AB: (31,)},
    },
)

PROFILE = Profile(
    key="hs3",
    display_name="HS3",
    device_types={0x1610: Shape(phases=3, strings=2)},
    hand_verified=True,
    maximum_shape=Shape(phases=3, strings=2),
    largest_request=32,
    spans=(
        Span(name="network", first=0x0F03, last=0x0F2F),
        Span(name="ev_data", first=0x3024, last=0x30BB, function=FunctionCode.INPUT),
        Span(name="settings", first=0x3600, last=0x36EF),
        Span(name="realtime", first=0x4000, last=0x4176),
        Span(name="parallel", first=0x4200, last=0x427C),
        Span(name="ev_settings", first=0x4B03, last=0x4B47),
        Span(name="averages", first=0x513E, last=0x51BE),
        Span(name="ems", first=0x8400, last=0x8401),
        Span(name="identity", first=0x8F0D, last=0x8F1C),
        Span(name="battery", first=0xA000, last=0xA037),
        Span(name="meters", first=0xA03C, last=0xA077),
    ),
    placements=placements_by_evidence(
        groups={
            Evidence.IMPLEMENTED: DERIVED_PLACEMENTS,
            Evidence.VERIFIED: {
                "ethernet_protocol_version": 0x0F03,
                "ethernet_mac_address": 0x0F04,
                "ethernet_mode": 0x0F07,
                "settings_sequence": 0x3602,
                "settings_protocol_version": 0x3603,
                "meter_configuration": 0x3630,
                "meter_address": 0x3631,
                "rs485_address": 0x3633,
                "rs485_baud_rate": 0x3634,
                "passive_battery_charge_power": 0x3639,
                "battery_protocol": 0x363B,
                "battery_auto_wake": 0x3643,
                "battery_discharge_soc_limit_on_grid": 0x3644,
                "application_mode": 0x3647,
                "backup_reserve_soc": 0x3651,
                "export_limit_power": 0x365A,
                "export_limit_current": 0x365B,
                "export_limit_mode": 0x365C,
                "time_of_use_idle_mode": 0x365F,
                "led_mode": 0x3675,
                "rs485_slave_address": 0x3680,
                "rs485_slave_baud_rate": 0x3681,
                "inverter_clock": 0x4000,
                "operating_mode": 0x4004,
                "inverter_fault_word_1": 0x4005,
                "inverter_fault_word_2": 0x4007,
                "inverter_fault_word_3": 0x4009,
                "inverter_temperature": 0x4010,
                "ambient_temperature": 0x4011,
                "leakage_current": 0x4012,
                "grid_connection_countdown": 0x4019,
                "battery_discharge_limit_active": 0x402A,
                "dc_bus_voltage": 0x4067,
                "dc_bus_slave_voltage": 0x4068,
                "battery_voltage": 0x4069,
                "battery_current": 0x406A,
                "battery_port_power": 0x406D,
                "battery_temperature": 0x406E,
                "battery_soc": 0x406F,
                "pv_direction": 0x4095,
                "battery_direction": 0x4096,
                "grid_direction": 0x4097,
                "load_power": None,
                "pv_power": 0x40A5,
                "battery_power": 0x40A6,
                "grid_power": None,
                "inverter_power": 0x40A9,
                "grid_load_power": 0x40AD,
                "ev_settings_protocol_version": 0x4B03,
                "ev_enabled": 0x4B04,
                "ev_address": 0x4B05,
                "ev_baud_rate": 0x4B06,
                "ev_charger_count": 0x4B07,
                "ev_communication_timeout": 0x4B08,
                "ev_port_mode": 0x4B09,
                "ev_port_address": 0x4B0A,
                "ev_mode": 0x4B12,
                "ev_charge_power": 0x4B14,
                "ev_minimum_current_charging": 0x4B43,
                "five_minute_average_pv_power": 0x5193,
                "five_minute_average_battery_power": 0x51B6,
                "five_minute_average_battery_soc": 0x51B8,
                "ems_battery_control": 0x8400,
                "ems_grid_control": 0x8400,
                "ems_inverter_control": 0x8400,
                "ems_inverter_control_with_timeout_exit": 0x8400,
                "ems_timeout": 0x8401,
                "ems_inverter_power_target": 0x8402,
                "ems_battery_charge_current_limit": 0x8403,
                "ems_battery_discharge_current_limit": 0x8404,
                "ems_battery_power_target": 0x8405,
                "ems_inverter_import_power_limit": 0x840F,
                "ems_inverter_export_power_limit": 0x8410,
                "ems_grid_power_target": 0x8411,
                "ems_pv_power_limit": 0x8412,
                "product_code": 0x8F0D,
                "display_software_version": 0x8F17,
                "master_software_version": 0x8F18,
                "display_hardware_version": 0x8F1A,
                "control_hardware_version": 0x8F1B,
                "power_hardware_version": 0x8F1C,
                "meter_a_status": 0xA03C,
                "meter_a_power": None,
                "backup_load_power": None,
                "ev_serial_number": 0x3024,
                "ev_model": 0x3034,
                "ev_software_version": 0x303C,
                "ev_hardware_version": 0x3041,
                "ev_phase_count": 0x3046,
                "ev_minimum_power": 0x3047,
                "ev_work_mode": 0x309C,
                "ev_status": 0x309D,
                "ev_total_energy": 0x30A9,
                "ev_control_pilot_voltage": 0x30AF,
                "ev_remote_control": 0x30B6,
                "ev_current_setpoint": 0x30B7,
            },
            Evidence.RESPONDS_UNCHECKED: {
                "parallel_mode": 0x4200,
                "parallel_id": 0x4201,
                "parallel_count": 0x4202,
                "parallel_online_count": 0x4203,
                "parallel_pv_power_low_word": 0x4204,
                "parallel_battery_power_low_word": 0x4205,
                "parallel_grid_power_low_word": 0x4206,
                "parallel_load_power_low_word": 0x4207,
                "parallel_backup_load_power_low_word": 0x4208,
                "parallel_battery_soc": 0x4209,
                "parallel_grid_load_power_low_word": 0x420A,
                "parallel_battery_capacity": 0x420B,
                "parallel_pv_power_high_word": 0x420C,
                "parallel_battery_power_high_word": 0x420D,
                "parallel_grid_power_high_word": 0x420E,
                "parallel_load_power_high_word": 0x420F,
                "parallel_backup_load_power_high_word": 0x4210,
                "parallel_grid_load_power_high_word": 0x4211,
                "parallel_meter_b_power": 0x4212,
                "ev_fault_word_1": 0x30AB,
                "ev_fault_word_2": 0x30AD,
                "ev_maximum_power": 0x3048,
                "ev_power": 0x30A4,
                "ev_charge_duration": 0x30A6,
                "ev_session_energy": 0x30A7,
                "ev_duty_cycle": 0x30B0,
                "ev_session_start": 0x30B8,
                "ev_session_end": 0x30BA,
                "meter_b_status": 0xA053,
                "meter_b_power": None,
                "parallel_backup_load_power": None,
                "parallel_battery_power": None,
                "parallel_grid_load_power": None,
                "parallel_grid_power": None,
                "parallel_load_power": None,
                "parallel_pv_power": None,
            },
            Evidence.RESPONDS_UNDOCUMENTED: {
                "passive_mode": 0x3636,
                "passive_grid_charge_power": 0x3637,
                "passive_grid_discharge_power": 0x3638,
                "passive_battery_discharge_power": 0x363A,
                "battery_discharge_soc_limit_off_grid": 0x3645,
                "battery_charge_power_limit": 0x364D,
                "battery_discharge_power_limit": 0x364E,
                "grid_import_power_limit": 0x364F,
                "grid_export_power_limit": 0x3650,
                "time_of_use_grid_discharge": 0x3660,
                "inverter_discharge_power_setpoint": 0x4023,
                "inverter_charge_power_setpoint": 0x4024,
                "battery_discharge_current_setpoint": 0x4025,
                "battery_charge_current_setpoint": 0x4026,
                "battery_status_code": 0x4027,
                "battery_protocol_active": 0x4028,
                "battery_charge_limit_active": 0x4029,
                "battery_depth_of_discharge_active": 0x402B,
                "backup_reserve_soc_active": 0x402C,
                "meter_configuration_active": 0x4030,
                "output_direction": 0x4098,
                "battery_pack_count": 0xA000,
                "battery_capacity": 0xA001,
                "battery_usable_capacity": 0xA00A,
                "battery_online_code": 0xA00B,
                "battery_discharge_current_limit": 0xA036,
                "battery_charge_current_limit": 0xA037,
            },
            Evidence.DOCUMENTED: {
                "battery_fault_word_1": 0x400B,
                "clear_current_fault": 0x8015,
                "restart_inverter": 0x801A,
                "synchronise_clock": 0x8020,
                "ems_pv_power_limit_remove": 0x8412,
                "battery_charge_soc_limit": 0x3646,
                "slave_software_version": 0x8F19,
                "ev_ems_charging": 0x4B46,
                "ev_ems_phase_mode": 0x4B46,
                "ev_ems_charge_current": 0x4B47,
            },
        }
    ),
    families=(
        FamilyPlacement(family="grid_phase", evidence=Evidence.VERIFIED),
        FamilyPlacement(family="inverter_phase", evidence=Evidence.VERIFIED),
        FamilyPlacement(family="backup_phase", evidence=Evidence.VERIFIED),
        FamilyPlacement(family="grid_output_first_phase", evidence=Evidence.VERIFIED),
        FamilyPlacement(family="grid_output_other_phases", evidence=Evidence.VERIFIED),
        FamilyPlacement(family="pv_string", evidence=Evidence.VERIFIED, count=2),
        FamilyPlacement(family="pv_insulation", evidence=Evidence.VERIFIED, count=2),
        FamilyPlacement(family="pv_energy", evidence=Evidence.VERIFIED),
        FamilyPlacement(family="battery_charge_energy", evidence=Evidence.VERIFIED),
        FamilyPlacement(family="battery_discharge_energy", evidence=Evidence.VERIFIED),
        FamilyPlacement(family="load_energy", evidence=Evidence.VERIFIED),
        FamilyPlacement(family="backup_load_energy", evidence=Evidence.VERIFIED),
        FamilyPlacement(family="grid_export_energy", evidence=Evidence.VERIFIED),
        FamilyPlacement(family="grid_import_energy", evidence=Evidence.VERIFIED),
        FamilyPlacement(
            family="grid_first_phase_export_energy", evidence=Evidence.VERIFIED
        ),
        FamilyPlacement(
            family="grid_first_phase_import_energy", evidence=Evidence.VERIFIED
        ),
        FamilyPlacement(
            family="grid_other_phases_export_energy", evidence=Evidence.VERIFIED
        ),
        FamilyPlacement(
            family="grid_other_phases_import_energy", evidence=Evidence.VERIFIED
        ),
        FamilyPlacement(
            family="parallel_pv_energy", evidence=Evidence.RESPONDS_UNCHECKED
        ),
        FamilyPlacement(
            family="parallel_battery_charge_energy",
            evidence=Evidence.RESPONDS_UNCHECKED,
        ),
        FamilyPlacement(
            family="parallel_battery_discharge_energy",
            evidence=Evidence.RESPONDS_UNCHECKED,
        ),
        FamilyPlacement(
            family="parallel_grid_l1_export_energy",
            evidence=Evidence.RESPONDS_UNCHECKED,
        ),
        FamilyPlacement(
            family="parallel_grid_l2_export_energy",
            evidence=Evidence.RESPONDS_UNCHECKED,
        ),
        FamilyPlacement(
            family="parallel_grid_l3_export_energy",
            evidence=Evidence.RESPONDS_UNCHECKED,
        ),
        FamilyPlacement(
            family="parallel_grid_l1_import_energy",
            evidence=Evidence.RESPONDS_UNCHECKED,
        ),
        FamilyPlacement(
            family="parallel_grid_l2_import_energy",
            evidence=Evidence.RESPONDS_UNCHECKED,
        ),
        FamilyPlacement(
            family="parallel_grid_l3_import_energy",
            evidence=Evidence.RESPONDS_UNCHECKED,
        ),
        FamilyPlacement(
            family="parallel_load_energy", evidence=Evidence.RESPONDS_UNCHECKED
        ),
        FamilyPlacement(
            family="parallel_grid_import_energy", evidence=Evidence.RESPONDS_UNCHECKED
        ),
        FamilyPlacement(
            family="parallel_grid_export_energy", evidence=Evidence.RESPONDS_UNCHECKED
        ),
        FamilyPlacement(
            family="parallel_pv_meter_energy", evidence=Evidence.RESPONDS_UNCHECKED
        ),
        FamilyPlacement(family="five_minute_average_grid", evidence=Evidence.VERIFIED),
        FamilyPlacement(
            family="five_minute_average_inverter", evidence=Evidence.VERIFIED
        ),
        FamilyPlacement(family="five_minute_average_load", evidence=Evidence.VERIFIED),
        FamilyPlacement(
            family="five_minute_average_grid_load", evidence=Evidence.VERIFIED
        ),
        FamilyPlacement(
            family="five_minute_average_backup", evidence=Evidence.VERIFIED
        ),
        FamilyPlacement(
            family="five_minute_average_generator", evidence=Evidence.VERIFIED
        ),
        FamilyPlacement(
            family="five_minute_average_grid_phase", evidence=Evidence.VERIFIED
        ),
        FamilyPlacement(
            family="five_minute_average_inverter_phase", evidence=Evidence.VERIFIED
        ),
        FamilyPlacement(
            family="five_minute_average_load_phase", evidence=Evidence.VERIFIED
        ),
        FamilyPlacement(
            family="five_minute_average_grid_load_phase", evidence=Evidence.VERIFIED
        ),
        FamilyPlacement(
            family="five_minute_average_backup_phase", evidence=Evidence.VERIFIED
        ),
        FamilyPlacement(
            family="five_minute_average_generator_phase", evidence=Evidence.VERIFIED
        ),
        FamilyPlacement(
            family="five_minute_average_pv_string", evidence=Evidence.VERIFIED
        ),
        FamilyPlacement(
            family="five_minute_average_battery_pack", evidence=Evidence.VERIFIED
        ),
        FamilyPlacement(
            family="battery_pack", evidence=Evidence.RESPONDS_UNDOCUMENTED, count=1
        ),
        FamilyPlacement(
            family="battery_pack_discharged_energy",
            evidence=Evidence.RESPONDS_UNDOCUMENTED,
            count=1,
        ),
        FamilyPlacement(
            family="battery_pack_faults",
            evidence=Evidence.RESPONDS_UNDOCUMENTED,
            count=1,
        ),
        FamilyPlacement(family="meter_a_phase", evidence=Evidence.VERIFIED),
        FamilyPlacement(family="meter_b_phase", evidence=Evidence.RESPONDS_UNCHECKED),
        FamilyPlacement(family="meter_a_power_high_words", evidence=Evidence.VERIFIED),
        FamilyPlacement(
            family="meter_b_power_high_words", evidence=Evidence.RESPONDS_UNCHECKED
        ),
        FamilyPlacement(family="meter_a_reactive_power", evidence=Evidence.VERIFIED),
        FamilyPlacement(
            family="meter_b_reactive_power", evidence=Evidence.RESPONDS_UNCHECKED
        ),
        FamilyPlacement(
            family="ev_phase",
            evidence=Evidence.RESPONDS_UNCHECKED,
            exceptions={f"ev_l{phase}_voltage": Evidence.VERIFIED for phase in PHASES},
        ),
        FamilyPlacement(family="ethernet_addresses", evidence=Evidence.VERIFIED),
        FamilyPlacement(
            family="charge_slots",
            evidence=Evidence.DOCUMENTED,
            exceptions={"charge_slot_1_start": Evidence.VERIFIED},
        ),
        FamilyPlacement(family="charge_slots_enabled", evidence=Evidence.VERIFIED),
        FamilyPlacement(family="discharge_slots", evidence=Evidence.DOCUMENTED),
        FamilyPlacement(family="discharge_slots_enabled", evidence=Evidence.VERIFIED),
        FamilyPlacement(family="ev_slots", evidence=Evidence.VERIFIED),
    ),
    replacements=(
        Replacement(
            key="application_mode",
            options={
                0: "self_use",
                1: "time_of_use",
                2: "backup",
                6: "ems",
                11: "time_of_use_bms",
            },
        ),
        Replacement(key="load_power", sum_of=_phase_keys("grid_output_l{}_power")),
        Replacement(
            key="grid_power",
            equipment=Equipment.METER_A,
            sum_of=_phase_keys("meter_a_l{}_power"),
        ),
        *(
            Replacement(
                key=f"grid_l{phase}_{member}",
                equipment=Equipment.METER_A,
                sum_of=(f"meter_a_l{phase}_{member}",),
            )
            for phase in PHASES
            for member in ("power", "apparent_power", "current", "power_factor")
        ),
    ),
    probes=(
        Probe(
            equipment=Equipment.BATTERY,
            conditions=(
                Condition(
                    key="battery_protocol", comparison=Comparison.DIFFERS, reference=0
                ),
            ),
            unanswered=True,
        ),
        METER_A_PROBE,
        METER_B_PROBE,
        Probe(
            equipment=Equipment.EV_CHARGER,
            conditions=(
                Condition(key="ev_enabled", comparison=Comparison.EQUALS, reference=1),
            ),
            unanswered=False,
        ),
        PARALLEL_PROBE,
    ),
    faults=FAULTS,
    power_control={
        PowerFunction.BATTERY: EnableBitMethod(
            enable_key="ems_battery_control",
            target_key="ems_battery_power_target",
            timeout_key=EMS_TIMEOUT,
            limit_keys=EMS_LIMITS,
        ),
        PowerFunction.GRID: EnableBitMethod(
            enable_key="ems_grid_control",
            target_key="ems_grid_power_target",
            timeout_key=EMS_TIMEOUT,
            limit_keys=EMS_LIMITS,
        ),
        PowerFunction.INVERTER: EnableBitMethod(
            enable_key="ems_inverter_control_with_timeout_exit",
            target_key="ems_inverter_power_target",
            alternate_keys=("ems_inverter_control",),
            timeout_key=EMS_TIMEOUT,
            limit_keys=EMS_LIMITS,
        ),
    },
)
