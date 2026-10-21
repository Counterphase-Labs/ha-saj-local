import pytest

from saj_local_mock.profiles import fault_tables
from saj_local_mock.simulation.faults import Effect, Equipment, FaultBit
from tests.mock.builders import make_scenario

REGISTER_COUNT = {Equipment.INVERTER: 3, Equipment.BATTERY: 1, Equipment.EV_CHARGER: 2}


def build(*, model="hs3", modules=2, ev=False):
    return fault_tables.build_fault_map(
        scenario=make_scenario(
            model=model,
            battery={"modules": modules},
            ev_charger={"installed": ev},
        )
    )


def named(*, fault_map, equipment):
    return [
        entry
        for entry in fault_map.for_equipment(equipment=equipment)
        if not entry.reserved
    ]


def test_a_source_is_a_hex_register_and_a_bit():
    assert fault_tables.Condition("x", "4005:0 4009:4", "").sources(model="hs3") == (
        FaultBit(register=0x4005, bit=0),
        FaultBit(register=0x4009, bit=4),
    )
    assert fault_tables.Condition("x", "4005:0", "").sources(model="h2") == ()


@pytest.mark.parametrize("model", ["hs3", "h2"])
def test_every_bit_of_every_register_of_the_fitted_equipment_is_listed_once(model):
    fault_map = build(model=model, ev=model == "hs3")

    for equipment in Equipment:
        if equipment is Equipment.EV_CHARGER and model == "h2":
            assert fault_map.for_equipment(equipment=equipment) == ()
            continue
        bits = [e.bit for e in fault_map.for_equipment(equipment=equipment)]
        assert len(bits) == len(set(bits)) == 32 * REGISTER_COUNT[equipment]


def test_only_the_equipment_that_is_fitted_has_faults():
    fault_map = build(modules=0, ev=False)

    assert fault_map.for_equipment(equipment=Equipment.BATTERY) == ()
    assert fault_map.for_equipment(equipment=Equipment.EV_CHARGER) == ()
    assert len(fault_map.for_equipment(equipment=Equipment.INVERTER)) == 96
    assert fault_map.pack_count == 0


@pytest.mark.parametrize(
    ("model", "modules", "packs"),
    [("hs3", 1, 1), ("hs3", 4, 1), ("h2", 2, 2), ("h2", 5, 4), ("h2", 0, 0)],
)
def test_the_pack_count_is_the_battery_count_limited_by_the_model(
    model, modules, packs
):
    assert build(model=model, modules=modules).pack_count == packs


def test_a_bit_the_document_does_not_name_is_listed_as_reserved_and_has_no_effect():
    fault_map = build()
    reserved = [
        entry
        for entry in fault_map.for_equipment(equipment=Equipment.INVERTER)
        if entry.reserved
    ]

    assert reserved
    assert all(entry.effects == frozenset() for entry in reserved)
    assert "0x4005 bit 22 reserved" in {entry.name for entry in reserved}


def test_a_condition_reported_by_two_registers_appears_under_one_name_for_both():
    bits = build().find(equipment=Equipment.INVERTER, name="Grid lost")

    assert bits == (
        FaultBit(register=0x4005, bit=23),
        FaultBit(register=0x4009, bit=23),
    )


INVERTER_STOP = frozenset({Effect.INVERTER_STOP})
BIT_ONLY = (
    "Internal communication lost",
    "Display board memory fault",
    "Display board clock fault",
    "BMS device fault",
    "BMS communication lost",
    "EV charger communication lost",
    "DC-DC unit communication lost",
    "Parallel system communication lost",
    "DRM0 fault",
    "Fan 1 fault",
    "Authorisation expired",
    "Display board communication lost",
)
STOPPING = (
    "Grid phase R overvoltage",
    "Grid overfrequency",
    "Islanding",
    "PV overvoltage",
    "DC bus voltage imbalance",
    "Battery port overload",
    "Relay fault",
    "Insulation fault",
    "Arc fault",
    "Over temperature",
    "Controller memory fault",
)


def inverter_effects(*, model):
    return {
        entry.name: entry.effects
        for entry in named(fault_map=build(model=model), equipment=Equipment.INVERTER)
    }


@pytest.mark.parametrize("model", ["hs3", "h2"])
def test_a_grid_power_stage_temperature_or_safety_fault_stops_the_inverter(model):
    effects = inverter_effects(model=model)

    reported = set(STOPPING) & set(effects)
    assert len(reported) >= 10
    for name in reported:
        assert effects[name] == INVERTER_STOP


@pytest.mark.parametrize("model", ["hs3", "h2"])
def test_a_communication_display_fan_or_licence_fault_only_sets_its_bit(model):
    effects = inverter_effects(model=model)

    reported = set(BIT_ONLY) & set(effects)
    assert len(reported) >= 9
    for name in reported:
        assert effects[name] == frozenset()


@pytest.mark.parametrize("model", ["hs3", "h2"])
def test_grid_lost_puts_the_inverter_off_grid(model):
    assert inverter_effects(model=model)["Grid lost"] == {Effect.GRID_LOST}


@pytest.mark.parametrize("model", ["hs3", "h2"])
def test_meter_communication_lost_silences_meter_a_without_stopping_the_inverter(
    model,
):
    assert inverter_effects(model=model)["Meter communication lost"] == {
        Effect.METER_A_LOST
    }


def test_the_models_name_conditions_the_other_does_not_report():
    hs3 = {
        e.name
        for e in named(fault_map=build(model="hs3"), equipment=Equipment.INVERTER)
    }
    h2 = {
        e.name for e in named(fault_map=build(model="h2"), equipment=Equipment.INVERTER)
    }

    assert "CT device fault" in hs3 - h2
    assert "DC bus overvoltage" in h2 - hs3
    assert hs3 & h2


def test_the_hs3_battery_table_names_the_bms_bits_and_the_h2_has_none():
    hs3 = build(model="hs3")
    h2 = build(model="h2")

    assert len(named(fault_map=hs3, equipment=Equipment.BATTERY)) == 30
    assert named(fault_map=h2, equipment=Equipment.BATTERY) == []
    assert len(h2.for_equipment(equipment=Equipment.BATTERY)) == 32


@pytest.mark.parametrize(
    ("name", "effects"),
    [
        ("Battery too cold to charge", {Effect.NO_CHARGE}),
        ("Battery too hot to charge", {Effect.NO_CHARGE}),
        ("Battery total voltage high", {Effect.NO_CHARGE}),
        ("Battery cell overvoltage", {Effect.NO_CHARGE}),
        ("Battery too cold to discharge", {Effect.NO_DISCHARGE}),
        ("Battery too hot to discharge", {Effect.NO_DISCHARGE}),
        ("Battery total voltage low", {Effect.NO_DISCHARGE}),
        ("Battery cell undervoltage", {Effect.NO_DISCHARGE}),
        ("Battery short circuit", {Effect.NO_CHARGE, Effect.NO_DISCHARGE}),
        ("Battery system locked", {Effect.NO_CHARGE, Effect.NO_DISCHARGE}),
    ],
)
def test_battery_faults_stop_the_charging_or_discharging_their_name_describes(
    name, effects
):
    (bit,) = build().find(equipment=Equipment.BATTERY, name=name)
    entry = next(
        e for e in build().for_equipment(equipment=Equipment.BATTERY) if e.bit == bit
    )

    assert entry.effects == effects


def test_the_ev_charger_faults_stop_the_charger_and_the_second_register_is_reserved():
    fault_map = build(ev=True)
    entries = fault_map.for_equipment(equipment=Equipment.EV_CHARGER)

    assert {e.effects for e in entries if not e.reserved} == {
        frozenset({Effect.EV_STOP})
    }
    assert {e.bit.register for e in entries if e.reserved} == {0x30AB, 0x30AD}
    assert {e.bit.register for e in entries if not e.reserved} == {0x30AB}


def test_a_name_repeats_only_for_a_condition_that_two_registers_report():
    fault_map = build(ev=True)

    for equipment in Equipment:
        names = [e.name for e in named(fault_map=fault_map, equipment=equipment)]
        repeated = {name for name in names if names.count(name) > 1}
        assert repeated <= {
            condition.name
            for condition in fault_tables.INVERTER_CONDITIONS
            if len(condition.sources(model="hs3")) > 1
        }
