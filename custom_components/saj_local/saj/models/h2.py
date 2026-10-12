from . import (
    METER_A_PROBE,
    METER_B_PROBE,
    PARALLEL_PROBE,
    Comparison,
    Condition,
    Equipment,
    Evidence,
    FamilyPlacement,
    OperatingModeMethod,
    PowerFunction,
    Probe,
    Profile,
    Replacement,
    Shape,
    Span,
    placements_by_evidence,
)

PARALLEL_ENERGY_FAMILIES = (
    "parallel_pv_energy",
    "parallel_battery_charge_energy",
    "parallel_battery_discharge_energy",
    "parallel_grid_l1_export_energy",
    "parallel_grid_l2_export_energy",
    "parallel_grid_l3_export_energy",
    "parallel_grid_l1_import_energy",
    "parallel_grid_l2_import_energy",
    "parallel_grid_l3_import_energy",
    "parallel_load_energy",
)
PARALLEL_POWER_ENCODINGS = {
    "parallel_pv_power": "u16",
    "parallel_battery_power": "i16",
    "parallel_grid_power": "i16",
    "parallel_load_power": "i16",
    "parallel_backup_load_power": "u16",
    "parallel_grid_load_power": "u16",
}

PROFILE = Profile(
    key="h2",
    display_name="H2",
    device_types={
        0x005A: Shape(phases=1, strings=2),
        0x005B: Shape(phases=1, strings=3),
    },
    hand_verified=False,
    maximum_shape=Shape(phases=3, strings=4),
    largest_request=56,
    spans=(
        Span(name="settings", first=0x3604, last=0x367C),
        Span(name="realtime", first=0x4000, last=0x4166),
        Span(name="identity", first=0x8F00, last=0x8F1C),
        Span(name="battery", first=0xA000, last=0xA037),
        Span(name="parallel", first=0x4200, last=0x4264),
        Span(name="meters", first=0xA03C, last=0xA065),
    ),
    placements=placements_by_evidence(
        groups={
            Evidence.IMPLEMENTED: {
                "passive_mode": 0x3636,
                "passive_grid_charge_power": 0x3637,
                "passive_grid_discharge_power": 0x3638,
                "passive_battery_charge_power": 0x3639,
                "passive_battery_discharge_power": 0x363A,
                "battery_discharge_limit_on_grid": 0x3644,
                "battery_discharge_limit_off_grid": 0x3645,
                "battery_charge_limit": 0x3646,
                "application_mode": 0x3647,
                "battery_charge_power_limit": 0x364D,
                "battery_discharge_power_limit": 0x364E,
                "grid_import_power_limit": 0x364F,
                "grid_export_power_limit": 0x3650,
                "export_limit_power": 0x365A,
                "export_limit_current": 0x365B,
                "export_limit_mode": 0x365C,
                "time_of_use_idle_mode": 0x365F,
                "time_of_use_grid_discharge": 0x3660,
                "operating_mode": 0x4004,
                "inverter_temperature": 0x4010,
                "ambient_temperature": 0x4011,
                "leakage_current": 0x4012,
                "inverter_discharge_power_setpoint": 0x4023,
                "inverter_charge_power_setpoint": 0x4024,
                "battery_discharge_current_setpoint": 0x4025,
                "battery_charge_current_setpoint": 0x4026,
                "battery_status_code": 0x4027,
                "battery_protocol_active": 0x4028,
                "battery_charge_limit_active": 0x4029,
                "battery_discharge_limit_active": 0x402A,
                "battery_depth_of_discharge_active": 0x402B,
                "backup_reserve_soc_active": 0x402C,
                "meter_configuration_active": 0x4030,
                "battery_temperature": 0x406E,
                "battery_soc": 0x406F,
                "pv_direction": 0x4095,
                "battery_direction": 0x4096,
                "grid_direction": 0x4097,
                "output_direction": 0x4098,
                "load_power": 0x40A0,
                "ct_grid_power": 0x40A1,
                "ct_grid_apparent_power": 0x40A2,
                "ct_pv_power": 0x40A3,
                "ct_pv_apparent_power": 0x40A4,
                "pv_power": 0x40A5,
                "battery_power": 0x40A6,
                "grid_power": 0x40A7,
                "grid_apparent_power": 0x40A8,
                "inverter_power": 0x40A9,
                "inverter_apparent_power": 0x40AA,
                "backup_load_power": 0x40AB,
                "backup_load_apparent_power": 0x40AC,
                "grid_load_power": 0x40AD,
                "protocol_version": 0x8F02,
                "product_code": 0x8F0D,
                "display_software_version": 0x8F17,
                "master_software_version": 0x8F18,
                "slave_software_version": 0x8F19,
                "display_hardware_version": 0x8F1A,
                "control_hardware_version": 0x8F1B,
                "power_hardware_version": 0x8F1C,
                "battery_pack_count": 0xA000,
                "battery_capacity": 0xA001,
                "battery_usable_capacity": 0xA00A,
                "battery_online_code": 0xA00B,
                "battery_voltage_high_protection": 0xA032,
                "battery_charge_voltage": 0xA034,
                "battery_discharge_cutoff_voltage": 0xA035,
                "battery_discharge_current_limit": 0xA036,
                "battery_charge_current_limit": 0xA037,
            },
            Evidence.DOCUMENTED: {
                "clear_fault_history": 0x8015,
                "clear_current_fault": 0x8015,
                "restart_inverter": 0x801A,
                "synchronise_clock": 0x8020,
                "meter_configuration": 0x3630,
                "meter_address": 0x3631,
                "rs485_address": 0x3633,
                "rs485_baud_rate": 0x3634,
                "battery_protocol": 0x363B,
                "battery_auto_wake": 0x3643,
                "backup_reserve_soc": 0x3651,
                "inverter_clock": 0x4000,
                "dc_bus_voltage": 0x4067,
                "dc_bus_slave_voltage": 0x4068,
                "battery_voltage": 0x4069,
                "battery_current": 0x406A,
                "battery_port_power": 0x406D,
                "meter_a_status": 0xA03C,
                "meter_b_status": 0xA053,
                "meter_a_power": None,
                "meter_b_power": None,
                "parallel_mode": 0x4200,
                "parallel_id": 0x4201,
                "parallel_count": 0x4202,
                "parallel_online_count": 0x4203,
                "parallel_pv_power": 0x4204,
                "parallel_battery_power": 0x4205,
                "parallel_grid_power": 0x4206,
                "parallel_load_power": 0x4207,
                "parallel_backup_load_power": 0x4208,
                "parallel_battery_soc": 0x4209,
                "parallel_grid_load_power": 0x420A,
                "parallel_battery_capacity": 0x420B,
            },
        }
    ),
    families=(
        FamilyPlacement(family="grid_phase", evidence=Evidence.IMPLEMENTED),
        FamilyPlacement(family="inverter_phase", evidence=Evidence.IMPLEMENTED),
        FamilyPlacement(family="backup_phase", evidence=Evidence.IMPLEMENTED),
        FamilyPlacement(
            family="grid_output_first_phase", evidence=Evidence.IMPLEMENTED
        ),
        FamilyPlacement(
            family="grid_output_other_phases", evidence=Evidence.IMPLEMENTED
        ),
        FamilyPlacement(family="pv_string", evidence=Evidence.IMPLEMENTED),
        FamilyPlacement(family="pv_insulation", evidence=Evidence.IMPLEMENTED),
        FamilyPlacement(family="pv_energy", evidence=Evidence.IMPLEMENTED),
        FamilyPlacement(family="battery_charge_energy", evidence=Evidence.IMPLEMENTED),
        FamilyPlacement(
            family="battery_discharge_energy", evidence=Evidence.IMPLEMENTED
        ),
        FamilyPlacement(family="inverter_energy", evidence=Evidence.IMPLEMENTED),
        FamilyPlacement(family="load_energy", evidence=Evidence.IMPLEMENTED),
        FamilyPlacement(family="backup_load_energy", evidence=Evidence.IMPLEMENTED),
        FamilyPlacement(
            family="grid_export_energy", evidence=Evidence.IMPLEMENTED, base=0x40EF
        ),
        FamilyPlacement(
            family="grid_import_energy", evidence=Evidence.IMPLEMENTED, base=0x40F7
        ),
        FamilyPlacement(
            family="grid_other_phases_export_energy", evidence=Evidence.IMPLEMENTED
        ),
        FamilyPlacement(
            family="grid_other_phases_import_energy", evidence=Evidence.IMPLEMENTED
        ),
        FamilyPlacement(
            family="pv_other_strings_energy", evidence=Evidence.IMPLEMENTED
        ),
        FamilyPlacement(family="battery_pack", evidence=Evidence.IMPLEMENTED),
        FamilyPlacement(
            family="battery_pack_discharged_energy", evidence=Evidence.IMPLEMENTED
        ),
        FamilyPlacement(family="meter_a_phase", evidence=Evidence.IMPLEMENTED),
        FamilyPlacement(family="meter_b_phase", evidence=Evidence.DOCUMENTED),
        *(
            FamilyPlacement(family=family, evidence=Evidence.DOCUMENTED)
            for family in PARALLEL_ENERGY_FAMILIES
        ),
        FamilyPlacement(family="charge_slots", evidence=Evidence.IMPLEMENTED),
        FamilyPlacement(family="charge_slots_enabled", evidence=Evidence.IMPLEMENTED),
        FamilyPlacement(family="discharge_slots", evidence=Evidence.IMPLEMENTED),
        FamilyPlacement(
            family="discharge_slots_enabled", evidence=Evidence.IMPLEMENTED
        ),
    ),
    replacements=(
        Replacement(
            key="battery_protocol",
            options={
                0: "not_in_use",
                2: "lead_acid",
                20: "dyness_h",
                21: "pylon_sc0500",
                22: "b2_can",
            },
        ),
        *(
            Replacement(key=key, encoding=encoding, uncombined=True)
            for key, encoding in PARALLEL_POWER_ENCODINGS.items()
        ),
        Replacement(
            key="application_mode",
            options={
                0: "self_use",
                1: "time_of_use",
                2: "backup",
                3: "passive",
                12: "ai_saving",
                14: "legacy",
            },
        ),
    ),
    probes=(
        Probe(
            equipment=Equipment.BATTERY,
            conditions=(
                Condition(
                    key="battery_protocol_active",
                    comparison=Comparison.DIFFERS,
                    reference=0,
                ),
            ),
            unanswered=True,
        ),
        METER_A_PROBE,
        METER_B_PROBE,
        PARALLEL_PROBE,
    ),
    power_control={
        PowerFunction.BATTERY: OperatingModeMethod(
            mode_key="application_mode",
            passive_mode=3,
            default_mode=0,
            direction_key="passive_mode",
            standby=0,
            discharge=1,
            charge=2,
            charge_power_key="passive_battery_charge_power",
            discharge_power_key="passive_battery_discharge_power",
        ),
    },
)
