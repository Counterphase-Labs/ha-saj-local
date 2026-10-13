from dataclasses import replace

import pytest

from saj.codec import BitRange, Encoding, Range
from saj.definitions import (
    DEFINITIONS,
    FAMILIES,
    FAMILY_BY_NAME,
    FAULT_DEFINITIONS,
    FAULT_KEYS,
    Access,
    Category,
    Combination,
    Definition,
    EntityKind,
    Family,
    Member,
    Operation,
    Quantity,
    Role,
)
from saj.models import Equipment


def _definition(key: str, **changes: object) -> Definition:
    return Definition(
        key=key, quantity=Quantity.COUNT, encoding=Encoding.U16, **changes
    )


def _family(**changes: object) -> Family:
    values: dict[str, object] = {
        "name": "test",
        "stem": "unit_{index}",
        "base": 0x1000,
        "stride": 4,
        "count": 3,
        "members": (
            Member(offset=0, definition=_definition("alpha")),
            Member(offset=2, definition=_definition("beta")),
        ),
    }
    return Family(**{**values, **changes})


def test_a_family_generates_each_key_from_its_stem_index_and_suffix():
    keys = [definition.key for definition in _family().definitions()]

    assert keys == [
        "unit_1_alpha",
        "unit_1_beta",
        "unit_2_alpha",
        "unit_2_beta",
        "unit_3_alpha",
        "unit_3_beta",
    ]


def test_the_same_family_generates_the_addresses_from_base_stride_and_offset():
    addresses = dict(_family().addresses())

    assert addresses == {
        "unit_1_alpha": 0x1000,
        "unit_1_beta": 0x1002,
        "unit_2_alpha": 0x1004,
        "unit_2_beta": 0x1006,
        "unit_3_alpha": 0x1008,
        "unit_3_beta": 0x100A,
    }


def test_a_family_that_starts_at_a_later_index_counts_its_stride_from_that_index():
    family = _family(first_index=2, count=2)

    assert dict(family.addresses()) == {
        "unit_2_alpha": 0x1000,
        "unit_2_beta": 0x1002,
        "unit_3_alpha": 0x1004,
        "unit_3_beta": 0x1006,
    }
    assert list(family.indices) == [2, 3]


def test_a_stem_without_an_index_names_a_single_block():
    family = _family(stem="single", count=1)

    assert [definition.key for definition in family.definitions()] == [
        "single_alpha",
        "single_beta",
    ]


@pytest.mark.parametrize(
    ("role", "phases", "strings", "packs"),
    [
        (Role.NONE, [1, 1, 1], [1, 1, 1], [0, 0, 0]),
        (Role.PHASE, [1, 2, 3], [1, 1, 1], [0, 0, 0]),
        (Role.STRING, [1, 1, 1], [1, 2, 3], [0, 0, 0]),
        (Role.PACK, [1, 1, 1], [1, 1, 1], [1, 2, 3]),
    ],
)
def test_the_role_of_a_family_sets_the_phase_string_or_pack_each_row_needs(
    role: Role, phases: list[int], strings: list[int], packs: list[int]
):
    definitions = [
        definition
        for definition in _family(role=role).definitions()
        if definition.key.endswith("alpha")
    ]

    assert [definition.phases for definition in definitions] == phases
    assert [definition.strings for definition in definitions] == strings
    assert [definition.packs for definition in definitions] == packs


def test_a_member_marked_core_for_the_first_index_only_is_core_for_that_index():
    family = _family(
        members=(
            Member(
                offset=0,
                definition=_definition("alpha", core=True),
                core_first_only=True,
            ),
            Member(offset=1, definition=_definition("beta", core=True)),
        )
    )

    core = {definition.key: definition.core for definition in family.definitions()}

    assert core == {
        "unit_1_alpha": True,
        "unit_1_beta": True,
        "unit_2_alpha": False,
        "unit_2_beta": True,
        "unit_3_alpha": False,
        "unit_3_beta": True,
    }


def test_a_bit_field_that_follows_the_index_moves_one_bit_per_index():
    family = _family(
        stride=0,
        members=(
            Member(
                offset=0,
                definition=_definition("flag", field=BitRange(first=0, last=0)),
                field_follows_index=True,
            ),
        ),
    )

    fields = [definition.field for definition in family.definitions()]

    assert fields == [
        BitRange(first=0, last=0),
        BitRange(first=1, last=1),
        BitRange(first=2, last=2),
    ]
    assert {address for _, address in family.addresses()} == {0x1000}


@pytest.mark.parametrize(
    ("access", "writable", "readable"),
    [
        (Access.READ_ONLY, False, True),
        (Access.READ_WRITE, True, True),
        (Access.WRITE_ONLY, True, False),
    ],
)
def test_access_and_not_the_entity_kind_decides_what_a_row_allows(
    access: Access, *, writable: bool, readable: bool
):
    definition = _definition("x", access=access)

    assert (definition.writable, definition.readable) == (writable, readable)


@pytest.mark.parametrize("kind", list(EntityKind))
def test_the_entity_kind_alone_does_not_make_a_row_writable(kind: EntityKind):
    assert _definition("x", kind=kind).writable is False


@pytest.mark.parametrize(
    ("changes", "expected"),
    [
        ({}, True),
        ({"range": Range(minimum=0, maximum=1)}, True),
        ({"options": {0: "off"}}, True),
        ({"encoding": Encoding.CLOCK}, True),
        ({"encoding": Encoding.MAC}, False),
        ({"encoding": Encoding.MAC, "command_value": 1}, True),
        ({"encoding": Encoding.UNIX_TIME}, False),
        ({"encoding": Encoding.CLOCK, "range": Range(minimum=0, maximum=1)}, True),
        ({"encoding": Encoding.TEXT, "words": 4}, True),
        ({"encoding": Encoding.TIME_OF_DAY}, True),
        ({"encoding": Encoding.ADDRESS_TEXT, "words": 8}, True),
    ],
)
def test_a_definition_can_be_written_with_a_range_options_or_a_writable_encoding(
    changes: dict[str, object],
    *,
    expected: bool,
):
    definition = Definition(
        **{
            "key": "x",
            "quantity": Quantity.COUNT,
            "encoding": Encoding.U16,
            **changes,
        }
    )

    assert definition.has_writable_form is expected


@pytest.mark.parametrize(
    ("changes", "words"),
    [
        ({}, 1),
        ({"encoding": Encoding.U32}, 2),
        ({"encoding": Encoding.CLOCK}, 4),
        ({"encoding": Encoding.TEXT, "words": 16}, 16),
    ],
)
def test_a_definitions_width_follows_its_encoding_unless_declared(
    changes: dict[str, object], words: int
):
    definition = Definition(
        **{
            "key": "x",
            "quantity": Quantity.COUNT,
            "encoding": Encoding.U16,
            **changes,
        }
    )

    assert definition.word_count == words
    assert definition.format.word_count == words


def test_every_shipped_key_is_defined_once_across_singles_and_families():
    keys = [definition.key for definition in DEFINITIONS]

    assert len(keys) == len(set(keys))


def test_every_shipped_family_has_a_unique_name_and_is_found_by_it():
    assert len(FAMILY_BY_NAME) == len(FAMILIES)
    assert all(FAMILY_BY_NAME[family.name] is family for family in FAMILIES)


@pytest.mark.parametrize(
    ("changes", "category"),
    [
        ({}, None),
        ({"quantity": Quantity.VERSION}, Category.DIAGNOSTIC),
        ({"quantity": Quantity.ADDRESS}, Category.DIAGNOSTIC),
        ({"quantity": Quantity.TEXT}, Category.DIAGNOSTIC),
        ({"access": Access.READ_WRITE}, Category.CONFIGURATION),
        ({"access": Access.WRITE_ONLY}, Category.CONFIGURATION),
        ({"kind": EntityKind.NUMBER}, None),
        ({"key": "rs485_address"}, Category.DIAGNOSTIC),
        ({"key": "settings_sequence"}, Category.DIAGNOSTIC),
        (
            {"key": "battery_protocol", "kind": EntityKind.SELECT},
            Category.DIAGNOSTIC,
        ),
    ],
)
def test_settings_are_configuration_and_versions_and_commissioning_diagnostic(
    changes, category
):
    assert replace(_definition("test_row"), **changes).category is category


@pytest.mark.parametrize(
    ("changes", "expected"),
    [
        ({"range": Range(minimum=5, maximum=50)}, (5, 50)),
        ({"encoding": Encoding.U16}, (0, 65535)),
        ({"encoding": Encoding.I16}, (-32768, 32767)),
        ({"encoding": Encoding.U32}, (0, 4294967295)),
        ({"encoding": Encoding.I32}, (-2147483648, 2147483647)),
        ({"encoding": Encoding.U16, "scale": 0.1}, (0, 6553.5)),
        ({"encoding": Encoding.TEXT, "words": 4}, None),
    ],
)
def test_the_settable_range_is_the_documented_range_or_what_the_encoding_holds(
    changes, expected
):
    definition = replace(_definition("test_row"), **changes)

    settable = definition.settable_range

    assert (
        settable is None
        if expected is None
        else (settable.minimum, settable.maximum) == expected
    )


@pytest.mark.parametrize(
    ("family_equipment", "member_equipment", "expected"),
    [
        (None, None, None),
        (Equipment.BATTERY, None, Equipment.BATTERY),
        (Equipment.METER_B, Equipment.BATTERY, Equipment.METER_B),
        (None, Equipment.BATTERY, Equipment.BATTERY),
    ],
)
def test_a_family_tags_every_row_it_generates_with_its_equipment(
    family_equipment: Equipment | None,
    member_equipment: Equipment | None,
    expected: Equipment | None,
):
    family = _family(
        equipment=family_equipment,
        members=(
            Member(
                offset=0,
                definition=_definition("alpha", equipment=member_equipment),
            ),
        ),
    )

    assert {definition.equipment for definition in family.definitions()} == {expected}


def test_a_problem_summary_is_primary_and_every_other_problem_is_diagnostic():
    summary = Definition(
        key="summary",
        quantity=Quantity.PROBLEM,
        encoding=Encoding.U16,
        kind=EntityKind.BINARY_SENSOR,
        summary=True,
    )
    named = replace(summary, key="named", summary=False)

    assert summary.category is None
    assert named.category is Category.DIAGNOSTIC


def test_a_combination_masks_every_bit_of_a_source_it_gives_no_mask():
    combination = Combination(
        operation=Operation.ANY_BIT, sources=("a", "b"), masks={"a": 0b10}
    )

    assert combination.mask_of(source="a") == 0b10
    assert combination.mask_of(source="b") & 0xFFFF_FFFF == 0xFFFF_FFFF


def test_every_shipped_fault_key_is_mapped_by_a_shipped_model():
    from saj.models.h2 import PROFILE as H2
    from saj.models.hs3 import PROFILE as HS3

    mapped = set(HS3.faults.named) | set(H2.faults.named)
    named = {key for keys in FAULT_KEYS.values() for key in keys}

    assert named == mapped


def test_every_shipped_fault_word_and_problem_row_is_defined_once():
    keys = [definition.key for definition in FAULT_DEFINITIONS]

    assert len(keys) == len(set(keys))
    assert not [
        definition.key
        for definition in FAULT_DEFINITIONS
        if definition.exposed != (definition.quantity is Quantity.PROBLEM)
    ]
