"""H2 registers outside the layout both models share."""

from typing import TYPE_CHECKING

from .fields import I16, U32, Shape, blob, fixed, live, setting

if TYPE_CHECKING:
    from saj_modbus_mock.registers import Field
    from saj_modbus_mock.scenario import Scenario

RUNNING_DATA_WORDS = 6
RESERVED_WORDS = 12
HOURS_SCALE = 0.1
VOLTS = 0.1
AMPS = 0.1
MILLIAMPS = 0.001
HERTZ = 0.01


def _bounded(*, address: int, name: str, raw_default: int, shape: Shape) -> Field:
    return setting(
        address=address, name=name, value=raw_default * shape.scale, shape=shape
    )


def realtime_fields() -> list[Field]:
    return [
        fixed(address=0x400D, name="reserved_error_words", value=0, enc=U32),
        live(address=0x400F, name="error_count", source="fault_count"),
        fixed(address=0x4017, name="drm_hardware_status", value=0),
        fixed(address=0x4018, name="drm_software_status", value=0),
        fixed(address=0x401A, name="fault_record_serial", value=0),
        live(
            address=0x401B,
            name="settings_change_serial",
            source="settings_change_serial",
        ),
        blob(address=0x401C, name="running_data", value=0, length=RUNNING_DATA_WORDS),
        live(
            address=0x406B,
            name="battery_current_controller_one",
            source="battery_half_a",
            enc=I16,
            scale=0.01,
        ),
        live(
            address=0x406C,
            name="battery_current_controller_two",
            source="battery_half_a",
            enc=I16,
            scale=0.01,
        ),
        fixed(address=0x4070, name="reserved_battery_word", value=0),
        blob(
            address=0x40B0, name="reserved_power_words", value=0, length=RESERVED_WORDS
        ),
        live(
            address=0x40BC,
            name="generation_hours_today",
            source="pv_hours_today_kwh",
            scale=HOURS_SCALE,
        ),
        live(
            address=0x40BD,
            name="generation_hours_total",
            source="pv_hours_total_kwh",
            enc=U32,
            scale=HOURS_SCALE,
        ),
    ]


def settings_fields(*, scenario: Scenario) -> list[Field]:
    return [
        _bounded(
            address=0x3632,
            name="buzzer_forbid",
            raw_default=0,
            shape=Shape(minimum=0, maximum=1),
        ),
        _bounded(
            address=0x3635,
            name="prevent_reverse_flow_mode",
            raw_default=1,
            shape=Shape(minimum=0, maximum=2),
        ),
        _bounded(
            address=0x3642,
            name="return_frequency_hysteresis",
            raw_default=15,
            shape=Shape(minimum=0, maximum=15, scale=HERTZ),
        ),
        _bounded(
            address=0x3652,
            name="battery_off_grid_discharge_cutoff_voltage",
            raw_default=850,
            shape=Shape(minimum=850, maximum=4500, scale=VOLTS),
        ),
        _bounded(
            address=0x3653,
            name="battery_charge_cutoff_voltage",
            raw_default=4500,
            shape=Shape(minimum=850, maximum=4500, scale=VOLTS),
        ),
        _bounded(
            address=0x3654,
            name="battery_on_grid_discharge_cutoff_voltage",
            raw_default=850,
            shape=Shape(minimum=850, maximum=4500, scale=VOLTS),
        ),
        _bounded(
            address=0x3655,
            name="battery_voltage_protection",
            raw_default=4500,
            shape=Shape(minimum=850, maximum=4500, scale=VOLTS),
        ),
        _bounded(
            address=0x3656,
            name="battery_low_voltage_warning",
            raw_default=850,
            shape=Shape(minimum=850, maximum=4500, scale=VOLTS),
        ),
        _bounded(
            address=0x3657,
            name="battery_discharge_current_limit_setting",
            raw_default=300,
            shape=Shape(minimum=0, maximum=300, scale=AMPS),
        ),
        _bounded(
            address=0x3658,
            name="battery_charge_current_limit_setting",
            raw_default=300,
            shape=Shape(minimum=0, maximum=300, scale=AMPS),
        ),
        _bounded(
            address=0x3659,
            name="battery_total_capacity_setting",
            raw_default=0,
            shape=Shape(
                minimum=0,
                maximum=1000,
            ),
        ),
        _bounded(
            address=0x365D,
            name="bms_update_id",
            raw_default=0,
            shape=Shape(minimum=0, maximum=31),
        ),
        _bounded(
            address=0x365E,
            name="bms_update_mode",
            raw_default=0,
            shape=Shape(minimum=0, maximum=255),
        ),
        _bounded(
            address=0x3661,
            name="parallel_master_role",
            raw_default=0,
            shape=Shape(minimum=0, maximum=10),
        ),
        _bounded(
            address=0x3662,
            name="parallel_number_setting",
            raw_default=1,
            shape=Shape(minimum=1, maximum=255),
        ),
        _bounded(
            address=0x3663,
            name="parallel_mode_setting",
            raw_default=0,
            shape=Shape(minimum=0, maximum=3),
        ),
        _bounded(
            address=0x3664,
            name="battery_discharge_voltage",
            raw_default=4500,
            shape=Shape(minimum=850, maximum=4500, scale=VOLTS),
        ),
        _bounded(
            address=0x3665,
            name="battery_average_charge_voltage",
            raw_default=4500,
            shape=Shape(minimum=850, maximum=4500, scale=VOLTS),
        ),
        _bounded(
            address=0x3666,
            name="battery_input_mode",
            raw_default=1,
            shape=Shape(minimum=1, maximum=2),
        ),
        _bounded(
            address=0x3667,
            name="pv_input_mode",
            raw_default=0,
            shape=Shape(minimum=0, maximum=2),
        ),
        _bounded(
            address=0x3668,
            name="off_grid_mode_enable",
            raw_default=0,
            shape=Shape(minimum=0, maximum=1),
        ),
        _bounded(
            address=0x3669,
            name="off_grid_voltage",
            raw_default=2200,
            shape=Shape(minimum=2200, maximum=2400, scale=VOLTS),
        ),
        _bounded(
            address=0x366A,
            name="off_grid_frequency",
            raw_default=5000,
            shape=Shape(minimum=5000, maximum=6000, scale=HERTZ),
        ),
        _bounded(
            address=0x366B,
            name="motor_enable_bits",
            raw_default=0,
            shape=Shape(minimum=0, maximum=0xFFFF),
        ),
        fixed(
            address=0x366C,
            name="machine_model",
            value=scenario.device.model.device_type,
        ),
        fixed(address=0x366D, name="power_rated", value=scenario.device.rated_power_w),
        _bounded(
            address=0x366E,
            name="function_flags_one",
            raw_default=0,
            shape=Shape(minimum=0, maximum=0xFFFF),
        ),
        _bounded(
            address=0x366F,
            name="function_flags_two",
            raw_default=0,
            shape=Shape(minimum=0, maximum=0xFFFF),
        ),
        _bounded(
            address=0x3670,
            name="max_dc_current_component",
            raw_default=1000,
            shape=Shape(minimum=0, maximum=3000, scale=MILLIAMPS),
        ),
        _bounded(
            address=0x3671,
            name="max_dc_voltage_component",
            raw_default=100,
            shape=Shape(minimum=0, maximum=400, scale=VOLTS),
        ),
        _bounded(
            address=0x3672,
            name="max_iso_limit",
            raw_default=150,
            shape=Shape(minimum=30, maximum=1000),
        ),
        _bounded(
            address=0x3673,
            name="max_leakage_current",
            raw_default=200,
            shape=Shape(minimum=30, maximum=500, scale=MILLIAMPS),
        ),
        _bounded(
            address=0x3674,
            name="grid_type",
            raw_default=0,
            shape=Shape(minimum=0, maximum=3),
        ),
        _bounded(
            address=0x3676,
            name="battery_forced_charge_power",
            raw_default=200,
            shape=Shape(minimum=100, maximum=1000, scale=0.1),
        ),
        _bounded(
            address=0x3677,
            name="inverter_stop",
            raw_default=0,
            shape=Shape(minimum=0, maximum=1),
        ),
        _bounded(
            address=0x3678,
            name="pv_start_voltage",
            raw_default=1200,
            shape=Shape(minimum=0, maximum=6500, scale=VOLTS),
        ),
        _bounded(
            address=0x3679,
            name="pv_shutdown_voltage",
            raw_default=700,
            shape=Shape(minimum=0, maximum=6500, scale=VOLTS),
        ),
        _bounded(
            address=0x367A,
            name="mppt_voltage_high",
            raw_default=5000,
            shape=Shape(minimum=900, maximum=5000, scale=VOLTS),
        ),
        _bounded(
            address=0x367B,
            name="mppt_voltage_low",
            raw_default=900,
            shape=Shape(minimum=900, maximum=5000, scale=VOLTS),
        ),
        _bounded(
            address=0x367C,
            name="mppt_scan_interval_minutes",
            raw_default=30,
            shape=Shape(minimum=3, maximum=30000),
        ),
    ]
