"""What the control panel needs to know about a simulated device, as plain data.

Everything here is derived from the device's own fields, fault map and scenario, so
the page needs no model names, addresses or field lists of its own.
"""

import dataclasses
from typing import TYPE_CHECKING

from .registers import Field, FieldValue, raw_range
from .simulation.environment import SEED, SEED_PARAMETER, VARIATION_PARAMETERS
from .simulation.faults import Equipment, FaultMap, FaultState, hex_address
from .simulation.plant import (
    HOLD_FREQUENCY,
    HOLD_LOAD,
    HOLD_PARAMETERS,
    HOLD_PV,
    HOLD_VOLTAGE,
)

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from .device import Block
    from .presets import Preset
    from .scenario import Scenario
    from .simulation.environment import LoadConfig, ParameterSpec, Variation

SOC_BOUNDS = (0, 100)
EV_ENERGY_BOUNDS = (1, 200_000)
SLIDER_MAXIMUM_STEPS = 1_000
HOLD_READINGS = {
    HOLD_PV: ("pv_w", 0),
    HOLD_LOAD: ("load_w", 0),
    HOLD_VOLTAGE: ("grid_r_v", 1),
    HOLD_FREQUENCY: ("frequency_hz", 2),
}
EV_DEFAULT_ENERGY_WH = 20_000
SPEED_BOUNDS = (0, 100_000)
OPERATING_MODES = {
    0: "Initialisation",
    1: "Standby",
    2: "Operating",
    3: "Off-grid",
    4: "Grid-connected load",
    5: "Fault",
    6: "Upgrade",
    7: "Debugging",
    8: "Self-check",
    9: "Reset",
}


def is_setting(*, field: Field) -> bool:
    return field.writable and field.readable and not field.is_clock


def is_command(*, field: Field) -> bool:
    return field.writable and not field.readable and not field.is_clock


def available_fields(*, blocks: Iterable[Block]) -> list[tuple[Block, Field]]:
    """Fields of the blocks the device answers; a refused block has no controls."""
    return [
        (block, field)
        for block in blocks
        if block.unavailable is None
        for field in block.fields
    ]


def block_group(*, block: Block) -> str:
    return block.name or (
        f"{hex_address(address=block.start)}-{hex_address(address=block.end)}"
    )


def options_of(*, field: Field) -> list[dict[str, object]] | None:
    if field.options is None:
        return None
    labels = dict(field.labels)
    return [
        {"value": value, "label": labels.get(value)} for value in sorted(field.options)
    ]


def _bounds(*, field: Field) -> tuple[int | None, int | None]:
    if field.is_text:
        return None, None
    low, high = raw_range(field=field)
    minimum = low if field.minimum is None else field.minimum
    maximum = high if field.maximum is None else field.maximum
    return minimum, maximum


def describe_field(*, block: Block, field: Field) -> dict[str, object]:
    minimum, maximum = _bounds(field=field)
    return {
        "name": field.name,
        "address": hex_address(address=field.address),
        "group": block_group(block=block),
        "encoding": field.encoding.name,
        "scale": field.scale,
        "minimum": minimum,
        "maximum": maximum,
        "text": field.is_text,
        "max_length": field.words * 2 if field.is_text else None,
        "options": options_of(field=field),
    }


def describe_settings(*, blocks: Iterable[Block]) -> list[dict[str, object]]:
    return [
        describe_field(block=block, field=field)
        for block, field in available_fields(blocks=blocks)
        if is_setting(field=field)
    ]


def describe_commands(*, blocks: Iterable[Block]) -> list[dict[str, object]]:
    return [
        describe_field(block=block, field=field)
        for block, field in available_fields(blocks=blocks)
        if is_command(field=field)
    ]


def describe_faults(
    *, fault_map: FaultMap, clear_command: str, clear_value: int
) -> dict[str, object]:
    description: dict[str, object] = {
        equipment.value: [
            {
                "key": entry.bit.key,
                "register": hex_address(address=entry.bit.register),
                "bit": entry.bit.bit,
                "name": entry.name,
                "reserved": entry.reserved,
            }
            for entry in fault_map.for_equipment(equipment=equipment)
        ]
        for equipment in Equipment
    }
    description["packs"] = list(range(1, fault_map.pack_count + 1))
    description["clear_all"] = {"command": clear_command, "value": clear_value}
    return description


def _parameter(*, spec: ParameterSpec, default: float) -> dict[str, object]:
    return {
        "name": spec.name,
        "label": spec.label,
        "group": spec.group,
        "minimum": spec.minimum,
        "maximum": spec.maximum,
        "step": spec.step,
        "unit": spec.unit,
        "default": default,
        "slider": (spec.maximum - spec.minimum) / spec.step <= SLIDER_MAXIMUM_STEPS,
    }


def variation_values(
    *, seed: int, variation: Variation, load: LoadConfig
) -> dict[str, float]:
    values: dict[str, float] = {
        **dataclasses.asdict(variation),
        **dataclasses.asdict(load),
    }
    values[SEED] = seed
    return values


def describe_variation(
    *, seed: int, variation: Variation, load: LoadConfig
) -> list[dict[str, object]]:
    defaults = variation_values(seed=seed, variation=variation, load=load)
    return [
        _parameter(spec=spec, default=defaults[spec.name])
        for spec in (*VARIATION_PARAMETERS, SEED_PARAMETER)
    ]


def describe_holds() -> list[dict[str, object]]:
    return [
        {
            "name": spec.name,
            "label": spec.label,
            "minimum": spec.minimum,
            "maximum": spec.maximum,
            "step": spec.step,
            "unit": spec.unit,
        }
        for spec in HOLD_PARAMETERS
    ]


def describe_presets(*, presets: Iterable[Preset]) -> list[dict[str, str]]:
    return [
        {"key": preset.key, "name": preset.name, "description": preset.description}
        for preset in presets
    ]


def describe_model(*, scenario: Scenario, pack_count: int) -> dict[str, object]:
    device = scenario.device
    charger = scenario.ev_charger
    return {
        "name": device.model.name,
        "rated_power_w": device.rated_power_w,
        "phases": device.model.phases,
        "serial_number": device.serial_number,
        "equipment": {
            "battery": {
                "fitted": bool(scenario.battery.modules),
                "modules": scenario.battery.modules,
                "packs": pack_count,
                "soc_bounds": list(SOC_BOUNDS),
            },
            "meter_a": scenario.meters.meter_a,
            "meter_b": scenario.meters.meter_b,
            "ev_charger": {
                "fitted": charger.installed,
                "energy_bounds_wh": list(EV_ENERGY_BOUNDS),
                "default_energy_wh": EV_DEFAULT_ENERGY_WH,
            },
            "parallel_inverters": scenario.parallel.inverters,
        },
        "clock": {"speed_bounds": list(SPEED_BOUNDS)},
    }


def raw_value(*, field: Field, value: FieldValue) -> FieldValue:
    """What the register holds: the stored value divided by its scale."""
    if field.is_text or field.scale == 1.0:
        return value
    return round(float(value) / field.scale)


def settings_state(
    *, fields: Iterable[Field], settings: Mapping[str, FieldValue]
) -> dict[str, dict[str, FieldValue]]:
    return {
        field.name: {
            "raw": raw_value(field=field, value=settings[field.name]),
            "value": settings[field.name],
        }
        for field in fields
        if is_setting(field=field)
    }


def faults_state(*, faults: FaultState) -> dict[str, object]:
    """Only the active faults, in the shape a fault request is written in."""
    state: dict[str, object] = {
        equipment.value: {
            fault.key: True for fault in sorted(faults.bits(equipment=equipment))
        }
        for equipment in Equipment
    }
    state["packs"] = {
        str(codes.pack): {"fault": codes.fault, "warning": codes.warning}
        for codes in faults.packs
    }
    return state


def hold_values(*, holds: Mapping[str, float]) -> dict[str, float | None]:
    return {spec.name: holds.get(spec.name) for spec in HOLD_PARAMETERS}


def rounded(*, value: float, places: int) -> float:
    """Rounded for display; adding zero turns a negative zero into 0."""
    return round(value, places) + 0.0


def hold_readings(*, data: Mapping[str, float]) -> dict[str, float]:
    """The current value of each reading a hold can fix, from the live telemetry."""
    return {
        name: rounded(value=data[key], places=places)
        for name, (key, places) in HOLD_READINGS.items()
    }
