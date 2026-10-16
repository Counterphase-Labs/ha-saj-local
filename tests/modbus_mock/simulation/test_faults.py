import pytest

from saj_modbus_mock.simulation.faults import (
    BATTERY_STOP,
    Effect,
    Equipment,
    FaultBit,
    FaultEntry,
    FaultMap,
    FaultState,
    PackCodes,
    active_effects,
    fault_word_key,
    hex_address,
    pack_key,
)

GRID_LOST_A = FaultBit(register=0x4005, bit=23)
GRID_LOST_B = FaultBit(register=0x4009, bit=23)
RESERVED = FaultBit(register=0x4005, bit=22)
HOT = FaultBit(register=0x400B, bit=10)
EFFECTS = {
    GRID_LOST_A: frozenset({Effect.GRID_LOST}),
    GRID_LOST_B: frozenset({Effect.GRID_LOST}),
    RESERVED: frozenset(),
    HOT: frozenset({Effect.NO_CHARGE}),
}


def test_addresses_and_bits_print_the_way_the_documents_do():
    assert hex_address(address=0x400B) == "0x400B"
    assert hex_address(address=0x3E) == "0x003E"
    assert GRID_LOST_A.key == "0x4005:23"


def test_keys_name_the_telemetry_a_register_or_pack_word_is_read_from():
    assert fault_word_key(register=0x400B) == "fault_400b"
    assert pack_key(pack=2, kind="warning") == "pack2_warning"


@pytest.mark.parametrize(
    ("bits", "register", "word"),
    [
        ((), 0x4005, 0),
        ((GRID_LOST_A,), 0x4005, 1 << 23),
        ((GRID_LOST_A, RESERVED), 0x4005, (1 << 23) | (1 << 22)),
        ((GRID_LOST_A, GRID_LOST_B), 0x4009, 1 << 23),
        ((GRID_LOST_A,), 0x4009, 0),
    ],
)
def test_a_registers_word_has_one_bit_per_fault_set_on_it(bits, register, word):
    state = FaultState().with_bits(equipment=Equipment.INVERTER, bits=bits)

    assert state.word(register=register) == word


def test_bits_of_each_equipment_are_kept_apart_and_replaced_as_a_set():
    state = FaultState()
    state = state.with_bits(equipment=Equipment.INVERTER, bits=[GRID_LOST_A])
    state = state.with_bits(equipment=Equipment.BATTERY, bits=[HOT])
    state = state.with_bits(
        equipment=Equipment.EV_CHARGER, bits=[FaultBit(register=0x30AB, bit=1)]
    )
    state = state.with_bits(equipment=Equipment.INVERTER, bits=[RESERVED])

    assert state.bits(equipment=Equipment.INVERTER) == {RESERVED}
    assert state.bits(equipment=Equipment.BATTERY) == {HOT}
    assert state.bits(equipment=Equipment.EV_CHARGER) == {
        FaultBit(register=0x30AB, bit=1)
    }
    assert state.all_bits() == {
        RESERVED,
        HOT,
        FaultBit(register=0x30AB, bit=1),
    }


def test_pack_codes_are_set_per_pack_and_a_pack_back_at_zero_is_forgotten():
    state = FaultState().with_pack(codes=PackCodes(pack=2, fault=5, warning=1))
    state = state.with_pack(codes=PackCodes(pack=1, warning=3))
    assert state.pack(number=2) == PackCodes(pack=2, fault=5, warning=1)
    assert state.packs == (
        PackCodes(pack=1, warning=3),
        PackCodes(pack=2, fault=5, warning=1),
    )

    state = state.with_pack(codes=PackCodes(pack=2))

    assert state.pack(number=2) == PackCodes(pack=2)
    assert state.packs == (PackCodes(pack=1, warning=3),)


@pytest.mark.parametrize(
    ("bits", "packs", "expected"),
    [
        ((), (), frozenset()),
        ((RESERVED,), (), frozenset()),
        ((GRID_LOST_A, GRID_LOST_B), (), frozenset({Effect.GRID_LOST})),
        ((HOT, GRID_LOST_A), (), frozenset({Effect.NO_CHARGE, Effect.GRID_LOST})),
        ((), (PackCodes(pack=1, fault=1),), BATTERY_STOP),
        ((), (PackCodes(pack=1, warning=4),), frozenset()),
        ((FaultBit(register=0x4007, bit=3),), (), frozenset()),
    ],
)
def test_the_effects_are_those_of_the_set_bits_and_of_any_pack_fault_code(
    bits, packs, expected
):
    state = FaultState(inverter=frozenset(bits), packs=packs)

    assert active_effects(state=state, effects=EFFECTS) == expected


def test_a_fault_map_answers_by_equipment_and_by_the_name_of_a_condition():
    entries = (
        FaultEntry(Equipment.INVERTER, GRID_LOST_A, "Grid lost", EFFECTS[GRID_LOST_A]),
        FaultEntry(Equipment.INVERTER, GRID_LOST_B, "Grid lost", EFFECTS[GRID_LOST_B]),
        FaultEntry(
            Equipment.INVERTER, RESERVED, "reserved", frozenset(), reserved=True
        ),
        FaultEntry(Equipment.BATTERY, HOT, "Battery too hot to charge", EFFECTS[HOT]),
    )
    fault_map = FaultMap(entries=entries, pack_count=1)

    assert fault_map.for_equipment(equipment=Equipment.BATTERY) == (entries[3],)
    assert len(fault_map.for_equipment(equipment=Equipment.INVERTER)) == 3
    assert fault_map.effects() == EFFECTS
    assert fault_map.find(equipment=Equipment.INVERTER, name="Grid lost") == (
        GRID_LOST_A,
        GRID_LOST_B,
    )
    assert fault_map.find(equipment=Equipment.INVERTER, name="reserved") == ()
    assert fault_map.find(equipment=Equipment.BATTERY, name="Grid lost") == ()
