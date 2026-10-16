"""What the control panel needs to know about a simulated device, as plain data.

Everything here is derived from the device's own fields, fault map and scenario, so
the page needs no model names, addresses or field lists of its own.
"""

import dataclasses
from datetime import timedelta
from decimal import Decimal
from typing import TYPE_CHECKING, Protocol

from .link import (
    ADDRESS_BOUNDS,
    CODE_BOUNDS,
    LINK_PARAMETERS,
    REFUSED_BLOCKS,
    link_values,
)
from .presets import Needs
from .registers import EPOCH, Access, Field, FieldValue, decode, decode_raw, raw_range
from .simulation import control as ctl
from .simulation.environment import (
    GROUP_GRID,
    GROUP_LOAD,
    GROUP_SOLAR,
    LOAD_BASE,
    LOAD_PEAK,
    SEED,
    SEED_PARAMETER,
    VARIATION_PARAMETERS,
)
from .simulation.faults import (
    BATTERY_STOP,
    Effect,
    Equipment,
    FaultMap,
    FaultState,
    hex_address,
)
from .simulation.plant import (
    HOLD_FREQUENCY,
    HOLD_LOAD,
    HOLD_PARAMETERS,
    HOLD_PV,
    HOLD_VOLTAGE,
)
from .traffic import DecodedField

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence

    from .device import Block
    from .link import LinkSettings
    from .presets import Fitted, Preset
    from .scenario import Scenario
    from .simulation.environment import LoadConfig, ParameterSpec, Variation

SOC_BOUNDS = (0, 100)
EV_ENERGY_BOUNDS = (1, 200_000)
SLIDER_MAXIMUM_STEPS = 1_000
HOUSEHOLD_LOAD = "household_load_w"
PLANT_LOAD = "load_w"
CHARGER_POWER = "ev_power_w"
HOLD_READINGS = {
    HOLD_PV: ("pv_w", 0),
    HOLD_LOAD: (HOUSEHOLD_LOAD, 0),
    HOLD_VOLTAGE: ("grid_r_v", 1),
    HOLD_FREQUENCY: ("frequency_hz", 2),
}
EV_DEFAULT_ENERGY_WH = 20_000
SPEED_BOUNDS = (0, 100_000)
CARD_SOLAR = "solar"
CARD_HOUSE = "house"
CARD_GRID = "grid"
CARD_BATTERY = "battery"
CARD_EV_CHARGER = "ev_charger"
CARD_INVERTER = "inverter"
CARD_EXTERNAL_PV = "external_pv"
PACKS_KEY = "packs"
BIT_ONLY = "Bit only"
BATTERY_STOP_LABEL = "No charging or discharging"
EFFECT_LABELS = {
    Effect.INVERTER_STOP: "Inverter stops",
    Effect.GRID_LOST: "Runs off-grid",
    Effect.METER_A_LOST: "Meter A lost",
    Effect.NO_CHARGE: "No charging",
    Effect.NO_DISCHARGE: "No discharging",
    Effect.EV_STOP: "Charger stops",
}
ACCESS_LABELS = {
    Access.READ_ONLY: "read-only",
    Access.READ_WRITE: "writable",
    Access.WRITE_ONLY: "command",
}
PRIMARY_PARAMETERS = frozenset(
    {
        "peak_scale_percent",
        "cloud_depth",
        LOAD_BASE,
        LOAD_PEAK,
        "nominal_voltage_v",
        "nominal_frequency_hz",
    }
)
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


@dataclasses.dataclass(frozen=True, slots=True)
class Reading:
    """A value a card or node shows, named as the state names it.

    A text reading has its value given by the machine, because the device's own
    labels or the charger decide it."""

    name: str
    label: str
    unit: str
    places: int
    text: bool = False


PV_POWER = Reading(name="pv_w", label="PV power", unit="W", places=0)
HOUSEHOLD_POWER = Reading(
    name=HOUSEHOLD_LOAD, label="Household load", unit="W", places=0
)
EXTERNAL_PV_POWER = Reading(
    name="ext_pv_w", label="External PV power", unit="W", places=0
)
GRID_POWER = Reading(name="grid_w", label="Grid power", unit="W", places=0)
GRID_VOLTAGE = Reading(name="grid_r_v", label="Grid voltage", unit="V", places=1)
GRID_FREQUENCY = Reading(
    name="frequency_hz", label="Grid frequency", unit="Hz", places=2
)
BATTERY_POWER = Reading(name="battery_w", label="Battery power", unit="W", places=0)
STATE_OF_CHARGE = Reading(
    name="soc_percent", label="Battery state of charge", unit="%", places=1
)
CHARGER_READING = Reading(
    name=CHARGER_POWER, label="EV charger power", unit="W", places=0
)
CAR = Reading(name="car", label="Car", unit="", places=0, text=True)
OPERATING_MODE = Reading(
    name="operating_mode", label="Operating mode", unit="", places=0, text=True
)
APPLICATION_MODE = Reading(
    name="application_mode", label="Application mode", unit="", places=0, text=True
)
CONTROL_STATE_OF_CHARGE = "state_of_charge"
CONTROL_CAR = "car"


@dataclasses.dataclass(frozen=True, slots=True)
class Card:
    """One piece of equipment on the page: the variation group, holds and fault
    equipment it owns, the readings it shows and the special controls it has."""

    key: str
    label: str
    readings: tuple[Reading, ...]
    needs: Needs = Needs.NOTHING
    group: str | None = None
    holds: tuple[str, ...] = ()
    equipment: Equipment | None = None
    controls: tuple[str, ...] = ()
    hub: bool = False


CARDS = (
    Card(
        key=CARD_SOLAR,
        label="Solar",
        readings=(PV_POWER,),
        group=GROUP_SOLAR,
        holds=(HOLD_PV,),
    ),
    Card(
        key=CARD_EXTERNAL_PV,
        label="External PV",
        readings=(EXTERNAL_PV_POWER,),
        needs=Needs.METER_B,
    ),
    Card(
        key=CARD_HOUSE,
        label="House",
        readings=(HOUSEHOLD_POWER,),
        group=GROUP_LOAD,
        holds=(HOLD_LOAD,),
    ),
    Card(
        key=CARD_GRID,
        label="Grid",
        readings=(GRID_POWER, GRID_VOLTAGE, GRID_FREQUENCY),
        group=GROUP_GRID,
        holds=(HOLD_VOLTAGE, HOLD_FREQUENCY),
    ),
    Card(
        key=CARD_BATTERY,
        label="Battery",
        readings=(BATTERY_POWER, STATE_OF_CHARGE),
        needs=Needs.BATTERY,
        equipment=Equipment.BATTERY,
        controls=(CONTROL_STATE_OF_CHARGE,),
    ),
    Card(
        key=CARD_EV_CHARGER,
        label="EV charger",
        readings=(CHARGER_READING, CAR),
        needs=Needs.EV_CHARGER,
        equipment=Equipment.EV_CHARGER,
        controls=(CONTROL_CAR,),
    ),
    Card(
        key=CARD_INVERTER,
        label="Inverter",
        readings=(OPERATING_MODE, APPLICATION_MODE),
        group=SEED_PARAMETER.group,
        equipment=Equipment.INVERTER,
        hub=True,
    ),
)
GROUP_CARDS = {card.group: card.key for card in CARDS if card.group is not None}
HOLD_CARDS = {name: card.key for card in CARDS for name in card.holds}
EQUIPMENT_CARDS = {
    card.equipment.value: card.key for card in CARDS if card.equipment is not None
}
SETTING_CARDS = {ctl.APP_MODE: CARD_INVERTER}


@dataclasses.dataclass(frozen=True, slots=True)
class Node:
    kind: str
    label: str
    card: str
    readings: tuple[Reading, ...]
    needs: Needs = Needs.NOTHING


NODES = (
    Node(kind="solar", label="Solar", card=CARD_SOLAR, readings=(PV_POWER,)),
    Node(
        kind="external_pv",
        label="External PV",
        card=CARD_EXTERNAL_PV,
        needs=Needs.METER_B,
        readings=(EXTERNAL_PV_POWER,),
    ),
    Node(kind="grid", label="Grid", card=CARD_GRID, readings=(GRID_POWER,)),
    Node(kind="house", label="House", card=CARD_HOUSE, readings=(HOUSEHOLD_POWER,)),
    Node(
        kind="battery",
        label="Battery",
        card=CARD_BATTERY,
        needs=Needs.BATTERY,
        readings=(BATTERY_POWER, STATE_OF_CHARGE),
    ),
    Node(
        kind="ev_charger",
        label="EV charger",
        card=CARD_EV_CHARGER,
        needs=Needs.EV_CHARGER,
        readings=(CHARGER_READING,),
    ),
)


def applicable_cards(*, fitted: Fitted) -> tuple[Card, ...]:
    return tuple(card for card in CARDS if fitted.has(needs=card.needs))


def applicable_nodes(*, fitted: Fitted) -> tuple[Node, ...]:
    return tuple(node for node in NODES if fitted.has(needs=node.needs))


def _described(*, reading: Reading) -> dict[str, str]:
    return {"name": reading.name, "label": reading.label, "unit": reading.unit}


def describe_cards(*, fitted: Fitted) -> list[dict[str, object]]:
    return [
        {
            "key": card.key,
            "label": card.label,
            "hub": card.hub,
            "controls": list(card.controls),
            "readings": [_described(reading=reading) for reading in card.readings],
        }
        for card in applicable_cards(fitted=fitted)
    ]


def describe_nodes(*, fitted: Fitted) -> list[dict[str, object]]:
    return [
        {
            "kind": node.kind,
            "label": node.label,
            "card": node.card,
            "readings": [_described(reading=reading) for reading in node.readings],
        }
        for node in applicable_nodes(fitted=fitted)
    ]


def with_household_load(*, data: Mapping[str, float]) -> dict[str, float]:
    """The telemetry plus the household's own load.

    The plant's load counts the EV charger's power too, so the household is what is
    left once the charger is taken off, and the flows then add up."""
    household = max(0.0, data[PLANT_LOAD] - data[CHARGER_POWER])
    return {**data, HOUSEHOLD_LOAD: household}


def _reading_value(
    *, reading: Reading, data: Mapping[str, float], texts: Mapping[str, str]
) -> float | str:
    if reading.text:
        return texts[reading.name]
    return rounded(value=data[reading.name], places=reading.places)


def node_readings(*, fitted: Fitted, data: Mapping[str, float]) -> dict[str, float]:
    """The readings the nodes show, by the names the description gives them."""
    return {
        reading.name: rounded(value=data[reading.name], places=reading.places)
        for node in applicable_nodes(fitted=fitted)
        for reading in node.readings
    }


def card_readings(
    *, fitted: Fitted, data: Mapping[str, float], texts: Mapping[str, str]
) -> dict[str, float | str]:
    """The readings the cards show, by the names the description gives them."""
    return {
        reading.name: _reading_value(reading=reading, data=data, texts=texts)
        for card in applicable_cards(fitted=fitted)
        for reading in card.readings
    }


def scale_places(*, scale: float) -> int:
    """The decimal places a scale has, for example 4 for 0.0001."""
    exponent = Decimal(str(scale)).normalize().as_tuple().exponent
    return -exponent if isinstance(exponent, int) and exponent < 0 else 0


def display_value(*, field: Field, value: FieldValue) -> FieldValue:
    """A stored value without the floating-point noise the scale multiplication adds."""
    if field.is_text or field.scale == 1.0:
        return value
    return round(float(value), scale_places(scale=field.scale))


def fault_effect(*, effects: frozenset[Effect]) -> str:
    if not effects:
        return BIT_ONLY
    both_battery = effects >= BATTERY_STOP
    labels = [
        EFFECT_LABELS[effect]
        for effect in Effect
        if effect in effects and not (both_battery and effect in BATTERY_STOP)
    ]
    if both_battery:
        labels.append(BATTERY_STOP_LABEL)
    return ", ".join(labels)


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


def describe_settings(
    *, blocks: Iterable[Block], initial: Mapping[str, FieldValue]
) -> list[dict[str, object]]:
    return [
        {
            **describe_field(block=block, field=field),
            "card": SETTING_CARDS.get(field.name),
            "primary": field.name in SETTING_CARDS,
            "scenario": setting_value(field=field, value=initial[field.name]),
        }
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
                "effect": fault_effect(effects=entry.effects),
            }
            for entry in fault_map.for_equipment(equipment=equipment)
        ]
        for equipment in Equipment
    }
    description[PACKS_KEY] = list(range(1, fault_map.pack_count + 1))
    description["cards"] = {**EQUIPMENT_CARDS, PACKS_KEY: EQUIPMENT_CARDS["battery"]}
    description["clear_all"] = {"command": clear_command, "value": clear_value}
    return description


def _parameter(*, spec: ParameterSpec, scenario: float) -> dict[str, object]:
    return {
        "card": GROUP_CARDS[spec.group],
        "primary": spec.name in PRIMARY_PARAMETERS,
        "name": spec.name,
        "label": spec.label,
        "group": spec.group,
        "minimum": spec.minimum,
        "maximum": spec.maximum,
        "step": spec.step,
        "unit": spec.unit,
        "scenario": scenario,
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
    scenario = variation_values(seed=seed, variation=variation, load=load)
    return [
        _parameter(spec=spec, scenario=scenario[spec.name])
        for spec in (*VARIATION_PARAMETERS, SEED_PARAMETER)
    ]


def describe_link(*, scenario: LinkSettings) -> dict[str, object]:
    values = link_values(settings=scenario)
    settings: list[dict[str, object]] = [
        {
            "name": parameter.name,
            "kind": parameter.kind.value,
            "minimum": parameter.minimum,
            "maximum": parameter.maximum,
            "unit": parameter.unit,
            "scenario": values[parameter.name],
        }
        for parameter in LINK_PARAMETERS
    ]
    settings.append(
        {
            "name": REFUSED_BLOCKS,
            "kind": "blocks",
            "address_bounds": list(ADDRESS_BOUNDS),
            "code_bounds": list(CODE_BOUNDS),
            "scenario": values[REFUSED_BLOCKS],
        }
    )
    return {"settings": settings}


def describe_holds() -> list[dict[str, object]]:
    return [
        {
            "name": spec.name,
            "label": spec.label,
            "card": HOLD_CARDS[spec.name],
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


def setting_value(*, field: Field, value: FieldValue) -> dict[str, FieldValue]:
    return {
        "raw": raw_value(field=field, value=value),
        "value": display_value(field=field, value=value),
    }


def settings_state(
    *, fields: Iterable[Field], settings: Mapping[str, FieldValue]
) -> dict[str, dict[str, FieldValue]]:
    return {
        field.name: setting_value(field=field, value=settings[field.name])
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


def fault_counts(*, faults: FaultState) -> dict[str, int]:
    """Active fault bits per equipment, with a pack's non-zero codes on the battery."""
    counts = {
        equipment.value: len(faults.bits(equipment=equipment))
        for equipment in Equipment
    }
    counts[Equipment.BATTERY.value] += sum(
        bool(codes.fault) + bool(codes.warning) for codes in faults.packs
    )
    return counts


def changed_settings(
    *,
    fields: Iterable[Field],
    settings: Mapping[str, FieldValue],
    initial: Mapping[str, FieldValue],
) -> list[str]:
    return [
        field.name
        for field in fields
        if is_setting(field=field) and settings[field.name] != initial[field.name]
    ]


def changed_variation(
    *, variation: Mapping[str, float], scenario: Mapping[str, float]
) -> list[str]:
    return [name for name, value in variation.items() if value != scenario[name]]


def held_names(*, holds: Mapping[str, float]) -> list[str]:
    return [spec.name for spec in HOLD_PARAMETERS if spec.name in holds]


class LastRead(Protocol):
    """When a client last read an address, or None if none has."""

    def __call__(self, *, address: int) -> float | None: ...


class LinkRefusal(Protocol):
    """The exception code a link fault answers a block with, or None."""

    def __call__(self, *, block: Block) -> int | None: ...


def never_read(*, address: int) -> float | None:  # noqa: ARG001
    return None


def not_refused_by_link(*, block: Block) -> int | None:  # noqa: ARG001
    return None


def _last_read_of(*, field: Field, last_read: LastRead) -> float | None:
    times = [
        time
        for address in range(field.address, field.last_address + 1)
        if (time := last_read(address=address)) is not None
    ]
    return max(times, default=None)


def _decoded(*, field: Field, words: list[int]) -> tuple[FieldValue, str | None]:
    value = decode(field=field, words=words)
    if field.is_clock:
        return (EPOCH + timedelta(seconds=float(value))).isoformat(), None
    if field.is_text:
        return value, None
    label = dict(field.labels).get(decode_raw(field=field, words=words))
    return display_value(field=field, value=value), label


def _field_snapshot(
    *, field: Field, words: list[int] | None, last_read: LastRead
) -> dict[str, object]:
    value, label = (None, None) if words is None else _decoded(field=field, words=words)
    return {
        "address": hex_address(address=field.address),
        "last_address": hex_address(address=field.last_address),
        "name": field.name,
        "encoding": field.encoding.name,
        "scale": field.scale,
        "access": ACCESS_LABELS[field.access],
        "words": words,
        "value": value,
        "label": label,
        "last_read": _last_read_of(field=field, last_read=last_read),
    }


def _block_snapshot(
    *,
    block: Block,
    words: Mapping[str, list[int]],
    last_read: LastRead,
    link_refusal: LinkRefusal,
) -> dict[str, object]:
    link_code = link_refusal(block=block)
    code = int(block.unavailable) if block.unavailable is not None else link_code
    refusal = (
        None
        if code is None
        else {
            "code": code,
            "model": block.unavailable is not None,
            "link": link_code is not None,
        }
    )
    fields = (
        []
        if block.unavailable is not None
        else [
            _field_snapshot(
                field=field, words=words.get(field.name), last_read=last_read
            )
            for field in block.fields
        ]
    )
    return {
        "start": hex_address(address=block.start),
        "end": hex_address(address=block.end),
        "name": block_group(block=block),
        "refusal": refusal,
        "fields": fields,
    }


def register_snapshot(
    *,
    blocks: Iterable[Block],
    words: Mapping[str, list[int]],
    last_read: LastRead = never_read,
    link_refusal: LinkRefusal = not_refused_by_link,
) -> dict[str, object]:
    """Every block and the fields of those that answer, as a client would see them.

    A link fault that refuses a block is reported through link_refusal.
    """
    return {
        "blocks": [
            _block_snapshot(
                block=block, words=words, last_read=last_read, link_refusal=link_refusal
            )
            for block in blocks
        ]
    }


class DeviceFieldDecoder:
    """Decodes the words of a request into the fields they cover."""

    def __init__(self, *, blocks: Iterable[Block]) -> None:
        self._blocks = tuple(blocks)

    def decode(self, *, start: int, words: tuple[int, ...]) -> Sequence[DecodedField]:
        end = start + len(words)
        covered: dict[str, DecodedField] = {}
        for block in self._blocks:
            for field in block.fields:
                if field.address >= start and field.last_address < end:
                    field_words = words[
                        field.address - start : field.last_address - start + 1
                    ]
                    value, label = _decoded(field=field, words=list(field_words))
                    covered[field.name] = DecodedField(
                        address=field.address,
                        name=field.name,
                        words=tuple(field_words),
                        value=value,
                        label=label,
                    )
        return sorted(covered.values(), key=lambda field: field.address)
