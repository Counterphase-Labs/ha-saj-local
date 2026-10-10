from dataclasses import replace

import pytest

from saj.catalogue import (
    CATALOGUES,
    Catalogue,
    CatalogueError,
    Row,
    blocks_by_key,
    catalogue_of,
    device_keys,
    device_read_registers,
    device_registers,
    device_unread_registers,
    known_keys,
)
from saj.codec import BitRange, Encoding, Range
from saj.definitions import (
    Access,
    Combination,
    Definition,
    EntityKind,
    Family,
    Member,
    Operation,
    Quantity,
    Role,
    Unit,
)
from saj.models import (
    Evidence,
    FamilyPlacement,
    Placement,
    Profile,
    Replacement,
    Shape,
    Span,
)
from saj.models.h2 import PROFILE as H2
from saj.models.hs3 import PROFILE as HS3
from tests.profiles import profile

SPAN = Span(name="all", first=0x1000, last=0x10FF)
SHAPE = Shape(phases=1, strings=1)
UNKNOWN_TYPE = 0x7777


def _definition(key: str, **changes: object) -> Definition:
    values: dict[str, object] = {
        "key": key,
        "quantity": Quantity.COUNT,
        "encoding": Encoding.U16,
    }
    return Definition(**{**values, **changes})


def _profile(*placements: Placement, **changes: object) -> Profile:
    values: dict[str, object] = {
        "key": "test",
        "display_name": "Test",
        "device_types": {1: SHAPE},
        "hand_verified": True,
        "maximum_shape": Shape(phases=3, strings=4),
        "largest_request": 32,
        "spans": (SPAN,),
        "placements": placements,
    }
    return Profile(**{**values, **changes})


def _at(
    key: str, address: int | None, evidence: Evidence = Evidence.VERIFIED
) -> Placement:
    return Placement(key=key, address=address, evidence=evidence)


def _build(
    *definitions: Definition,
    profile: Profile,
    families: dict[str, Family] | None = None,
) -> Catalogue:
    return Catalogue(profile=profile, definitions=definitions, families=families or {})


def _combined(key: str, operation: Operation, *sources: str) -> Definition:
    return _definition(
        key,
        encoding=Encoding.I32,
        combination=Combination(operation=operation, sources=sources),
    )


def test_a_register_joins_a_definition_with_the_address_and_evidence_of_a_profile():
    catalogue = _build(
        _definition("alpha", scale=0.1, encoding=Encoding.U32),
        profile=_profile(_at("alpha", 0x1010, Evidence.DOCUMENTED)),
    )

    (register,) = catalogue.registers

    assert (register.key, register.address, register.words) == ("alpha", 0x1010, 2)
    assert register.evidence is Evidence.DOCUMENTED
    assert register.scale == 0.1
    assert register.row == Row(address=0x1010, words=2)
    assert register.row.end == 0x1012


def test_a_register_exposes_what_its_definition_says():
    definition = _definition(
        "alpha",
        quantity=Quantity.POWER,
        kind=EntityKind.NUMBER,
        access=Access.READ_WRITE,
        unit=Unit.WATT,
        range=Range(minimum=0, maximum=9),
        options={0: "off"},
        field=BitRange(first=2, last=3),
    )

    (register,) = _build(definition, profile=_profile(_at("alpha", 0x1010))).registers

    assert register.quantity is Quantity.POWER
    assert register.kind is EntityKind.NUMBER
    assert register.unit is Unit.WATT
    assert register.writable is True
    assert register.range == Range(minimum=0, maximum=9)
    assert register.options == {0: "off"}
    assert register.field == BitRange(first=2, last=3)
    assert register.format is definition.format


@pytest.mark.parametrize(
    ("evidence", "marked_core", "enabled"),
    [
        (Evidence.VERIFIED, True, True),
        (Evidence.IMPLEMENTED, True, True),
        (Evidence.DOCUMENTED, True, False),
        (Evidence.RESPONDS_UNCHECKED, True, False),
        (Evidence.RESPONDS_UNDOCUMENTED, True, False),
        (Evidence.VERIFIED, False, False),
        (Evidence.IMPLEMENTED, False, False),
    ],
)
def test_a_row_is_enabled_by_default_only_when_marked_core_and_verified_or_implemented(
    evidence: Evidence,
    *,
    marked_core: bool,
    enabled: bool,
):
    catalogue = _build(
        _definition("alpha", core=marked_core),
        profile=_profile(_at("alpha", 0x1010, evidence)),
    )

    assert catalogue.registers[0].core is enabled


def test_registers_are_listed_in_address_order_with_fields_by_bit_and_combined_last():
    catalogue = _build(
        _definition("late"),
        _definition("flag_high", field=BitRange(first=1, last=1)),
        _definition("flag_low", field=BitRange(first=0, last=0)),
        _definition("early"),
        _combined("total", Operation.SUM, "early"),
        profile=_profile(
            _at("late", 0x1030),
            _at("flag_high", 0x1020),
            _at("flag_low", 0x1020),
            _at("early", 0x1010),
            _at("total", None),
        ),
    )

    assert [register.key for register in catalogue.registers] == [
        "early",
        "flag_low",
        "flag_high",
        "late",
        "total",
    ]


@pytest.mark.parametrize(
    ("definitions", "placements", "message"),
    [
        ([_definition("alpha")], [_at("ghost", 0x1010)], "no definition"),
        (
            [_definition("alpha"), _definition("alpha")],
            [_at("alpha", 0x1010)],
            "Duplicate definition",
        ),
        (
            [_definition("alpha")],
            [_at("alpha", 0x1010), _at("alpha", 0x1020)],
            "Duplicate key",
        ),
        (
            [_definition("alpha"), _definition("beta")],
            [_at("alpha", 0x1010), _at("beta", 0x1010)],
            "share",
        ),
        (
            [_definition("alpha", encoding=Encoding.U32), _definition("beta")],
            [_at("alpha", 0x1010), _at("beta", 0x1011)],
            "overlap",
        ),
        (
            [
                _definition("alpha", field=BitRange(first=0, last=0)),
                _definition("beta"),
            ],
            [_at("alpha", 0x1010), _at("beta", 0x1010)],
            "share",
        ),
        ([_definition("alpha")], [_at("alpha", 0x2000)], "outside every span"),
        (
            [_definition("alpha", encoding=Encoding.U32)],
            [_at("alpha", 0x10FF)],
            "outside every span",
        ),
        (
            [_definition("alpha", encoding=Encoding.TEXT, words=33)],
            [_at("alpha", 0x1010)],
            "wider than the largest request",
        ),
        (
            [_combined("total", Operation.WORDS, "high", "low"), _definition("high")],
            [_at("total", None), _at("high", 0x1010)],
            "lacks sources",
        ),
        (
            [
                _definition(
                    "setting",
                    kind=EntityKind.NUMBER,
                    access=Access.READ_WRITE,
                    encoding=Encoding.MAC,
                )
            ],
            [_at("setting", 0x1010)],
            "no range, options or writable encoding",
        ),
        ([_definition("alpha")], [_at("alpha", None)], "must have an address"),
        (
            [_combined("total", Operation.SUM, "alpha"), _definition("alpha")],
            [_at("total", 0x1020), _at("alpha", 0x1010)],
            "must have an address unless",
        ),
    ],
    ids=[
        "address-without-definition",
        "duplicate-definition",
        "duplicate-placement",
        "same-address-without-fields",
        "partial-overlap",
        "field-and-plain-row-share",
        "outside-span",
        "row-runs-past-span",
        "row-wider-than-largest-request",
        "combined-lacks-sources",
        "writable-without-form",
        "plain-row-without-address",
        "combined-row-with-address",
    ],
)
def test_construction_rejects(
    definitions: list[Definition], placements: list[Placement], message: str
):
    with pytest.raises(CatalogueError, match=message):
        _build(*definitions, profile=_profile(*placements))


def test_fields_of_one_packed_register_may_share_an_address():
    catalogue = _build(
        _definition("flag_a", field=BitRange(first=0, last=0)),
        _definition("flag_b", field=BitRange(first=1, last=1)),
        profile=_profile(_at("flag_a", 0x1010), _at("flag_b", 0x1010)),
    )

    assert [register.key for register in catalogue.registers] == ["flag_a", "flag_b"]
    assert catalogue.rows_for(shape=SHAPE) == (Row(address=0x1010, words=1),)


def test_a_family_that_does_not_exist_is_rejected():
    profile = _profile(
        families=(FamilyPlacement(family="ghost", evidence=Evidence.VERIFIED),)
    )

    with pytest.raises(CatalogueError, match="Unknown family"):
        _build(profile=profile)


def test_a_replacement_for_a_key_without_a_definition_is_rejected():
    profile = _profile(replacements=(Replacement(key="ghost", scale=2),))

    with pytest.raises(CatalogueError, match="no definition"):
        _build(profile=profile)


def test_a_profile_replaces_range_options_encoding_and_scale_but_not_quantity():
    definition = _definition(
        "alpha",
        kind=EntityKind.NUMBER,
        range=Range(minimum=0, maximum=10),
        options={0: "off"},
        scale=1,
    )
    profile = _profile(
        _at("alpha", 0x1010),
        replacements=(
            Replacement(
                key="alpha",
                range=(5, 50),
                options={0: "off", 1: "on"},
                encoding="i16",
                scale=0.1,
            ),
        ),
    )

    (register,) = _build(definition, profile=profile).registers

    assert register.range == Range(minimum=5, maximum=50)
    assert register.options == {0: "off", 1: "on"}
    assert register.encoding is Encoding.I16
    assert register.scale == 0.1
    assert register.quantity is Quantity.COUNT


def test_a_replacement_applies_to_that_profile_only():
    definition = _definition("alpha", scale=1)
    plain = _profile(_at("alpha", 0x1010))
    replaced = _profile(
        _at("alpha", 0x1010), replacements=(Replacement(key="alpha", scale=0.5),)
    )

    scales = [
        _build(definition, profile=profile).registers[0].scale
        for profile in (plain, replaced)
    ]

    assert scales == [1, 0.5]


def test_a_family_placement_limits_its_count_moves_its_base_and_overrides_evidence():
    family = Family(
        name="block",
        stem="unit_{index}",
        base=0x1000,
        stride=4,
        count=3,
        members=(Member(offset=0, definition=_definition("alpha")),),
    )
    profile = _profile(
        families=(
            FamilyPlacement(
                family="block",
                evidence=Evidence.IMPLEMENTED,
                count=2,
                base=0x1040,
                exceptions={"unit_2_alpha": Evidence.DOCUMENTED},
            ),
        )
    )

    catalogue = _build(
        *family.definitions(), profile=profile, families={"block": family}
    )

    assert [
        (register.key, register.address, register.evidence)
        for register in catalogue.registers
    ] == [
        ("unit_1_alpha", 0x1040, Evidence.IMPLEMENTED),
        ("unit_2_alpha", 0x1044, Evidence.DOCUMENTED),
    ]


def test_a_key_given_by_a_single_and_a_family_is_a_duplicate():
    family = Family(
        name="block",
        stem="unit",
        base=0x1000,
        members=(Member(offset=0, definition=_definition("alpha")),),
    )
    profile = _profile(
        _at("unit_alpha", 0x1020),
        families=(FamilyPlacement(family="block", evidence=Evidence.VERIFIED),),
    )

    with pytest.raises(CatalogueError, match="Duplicate key"):
        _build(*family.definitions(), profile=profile, families={"block": family})


def _shaped_catalogue() -> Catalogue:
    return _build(
        _definition("base"),
        _definition("second_phase", phases=2),
        _definition("third_phase", phases=3),
        _definition("second_string", strings=2),
        _definition("fourth_string", strings=4),
        _definition("core_base", core=True),
        _definition("core_second_phase", core=True, phases=2),
        _definition("core_third_string", core=True, strings=3),
        _definition("core_second_string", core=True, strings=2),
        profile=_profile(
            *(
                _at(key, 0x1010 + position)
                for position, key in enumerate(
                    (
                        "base",
                        "second_phase",
                        "third_phase",
                        "second_string",
                        "fourth_string",
                        "core_base",
                        "core_second_phase",
                        "core_third_string",
                        "core_second_string",
                    )
                )
            )
        ),
    )


@pytest.mark.parametrize(
    ("shape", "keys"),
    [
        (Shape(phases=1, strings=1), {"base", "core_base"}),
        (
            Shape(phases=1, strings=2),
            {"base", "second_string", "core_base", "core_second_string"},
        ),
        (
            Shape(phases=2, strings=1),
            {"base", "second_phase", "core_base", "core_second_phase"},
        ),
        (
            Shape(phases=3, strings=4),
            {
                "base",
                "second_phase",
                "third_phase",
                "second_string",
                "fourth_string",
                "core_base",
                "core_second_phase",
                "core_third_string",
                "core_second_string",
            },
        ),
    ],
)
def test_a_recognised_device_gets_only_the_rows_that_fit_its_shape(
    shape: Shape, keys: set[str]
):
    registers = _shaped_catalogue().registers_for(shape=shape)

    assert {register.key for register in registers} == keys


@pytest.mark.parametrize(
    ("assumed", "enabled"),
    [
        (
            False,
            {
                "core_base",
                "core_second_phase",
                "core_third_string",
                "core_second_string",
            },
        ),
        (True, {"core_base", "core_second_string"}),
    ],
)
def test_an_assumed_shape_enables_only_rows_within_one_phase_and_two_strings(
    *, assumed: bool, enabled: set[str]
):
    shape = Shape(phases=3, strings=4, assumed=assumed)

    registers = _shaped_catalogue().registers_for(shape=shape)

    assert len(registers) == 9
    assert {register.key for register in registers if register.core} == enabled


def test_a_shape_gets_its_registers_once():
    catalogue = _shaped_catalogue()
    shape = Shape(phases=2, strings=2)

    assert catalogue.registers_for(shape=shape) is catalogue.registers_for(shape=shape)


def _meter_catalogue() -> Catalogue:
    sources = [
        _definition(f"power_{phase}", phases=phase, encoding=Encoding.I16)
        for phase in (1, 2, 3)
    ]
    return _build(
        *sources,
        _combined("total", Operation.SUM, "power_1", "power_2", "power_3"),
        profile=_profile(
            _at("power_1", 0x1010),
            _at("power_2", 0x1011),
            _at("power_3", 0x1012),
            _at("total", None),
        ),
    )


@pytest.mark.parametrize(
    ("phases", "sources"),
    [
        (1, ("power_1",)),
        (2, ("power_1", "power_2")),
        (3, ("power_1", "power_2", "power_3")),
    ],
)
def test_a_sum_adds_over_the_phases_the_device_has(
    phases: int, sources: tuple[str, ...]
):
    registers = _meter_catalogue().registers_for(shape=Shape(phases=phases, strings=1))

    (total,) = [register for register in registers if register.key == "total"]

    assert total.sources == sources
    assert total.combination == Combination(operation=Operation.SUM, sources=sources)


def test_a_combined_row_is_dropped_when_none_of_its_sources_fit():
    catalogue = _build(
        _definition("power_2", phases=2),
        _combined("total", Operation.SUM, "power_2"),
        profile=_profile(_at("power_2", 0x1010), _at("total", None)),
    )

    registers = catalogue.registers_for(shape=SHAPE)

    assert registers == ()


def test_a_word_pair_is_dropped_when_one_of_its_words_does_not_fit():
    catalogue = _build(
        _definition("high", phases=2),
        _definition("low"),
        _combined("total", Operation.WORDS, "high", "low"),
        profile=_profile(_at("high", 0x1010), _at("low", 0x1011), _at("total", None)),
    )

    keys = {register.key for register in catalogue.registers_for(shape=SHAPE)}

    assert keys == {"low"}


def test_a_register_without_combination_has_no_sources():
    catalogue = _build(_definition("alpha"), profile=_profile(_at("alpha", 0x1010)))

    assert catalogue.registers[0].sources == ()
    assert catalogue.registers[0].combination is None


def test_rows_for_a_shape_are_the_distinct_rows_in_address_order():
    catalogue = _build(
        _definition("late"),
        _definition("wide", encoding=Encoding.U32),
        _definition("flag_a", field=BitRange(first=0, last=0)),
        _definition("flag_b", field=BitRange(first=1, last=1)),
        _combined("total", Operation.SUM, "late"),
        profile=_profile(
            _at("late", 0x1030),
            _at("wide", 0x1020),
            _at("flag_a", 0x1010),
            _at("flag_b", 0x1010),
            _at("total", None),
        ),
    )

    assert catalogue.rows_for(shape=SHAPE) == (
        Row(address=0x1010, words=1),
        Row(address=0x1020, words=2),
        Row(address=0x1030, words=1),
    )


def test_a_device_gets_the_registers_of_its_types_shape():
    profile = _profile(
        _at("alpha", 0x1010),
        _at("second", 0x1011),
        device_types={1: Shape(phases=1, strings=1), 2: Shape(phases=2, strings=1)},
    )
    definitions = [_definition("alpha"), _definition("second", phases=2)]
    catalogue = Catalogue(profile=profile, definitions=definitions)

    assert [
        r.key for r in catalogue.registers_for(shape=profile.shape_of(device_type=1))
    ] == ["alpha"]
    assert [
        r.key for r in catalogue.registers_for(shape=profile.shape_of(device_type=2))
    ] == ["alpha", "second"]


SHIPPED_SHAPES = [
    ("hs3", Shape(phases=3, strings=2), 537, 607, 39),
    ("h2", Shape(phases=1, strings=2), 235, 266, 36),
    ("h2", Shape(phases=1, strings=3), 243, 274, 39),
    ("h2", Shape(phases=3, strings=4, assumed=True), 327, 358, 36),
]


@pytest.mark.parametrize(("key", "shape", "rows", "entities", "core"), SHIPPED_SHAPES)
def test_shipped_profiles_have_the_catalogued_totals(
    key: str, shape: Shape, rows: int, entities: int, core: int
):
    catalogue = CATALOGUES[key]

    registers = catalogue.registers_for(shape=shape)

    assert len(catalogue.rows_for(shape=shape)) == rows
    assert len(registers) == entities
    assert sum(register.core for register in registers) == core


def test_the_two_shipped_models_share_274_catalogued_rows():
    hs3 = {
        register.row
        for register in CATALOGUES["hs3"].read_registers_for(shape=HS3.maximum_shape)
        if register.row
    }
    h2 = {
        register.row
        for register in CATALOGUES["h2"].read_registers_for(shape=H2.maximum_shape)
        if register.row
    }
    hs3_keys = {r.key for r in CATALOGUES["hs3"].registers if r.readable}
    h2_keys = {r.key for r in CATALOGUES["h2"].registers if r.readable}

    assert len(hs3 & h2) == 274
    assert len(hs3_keys & h2_keys) == 301


def test_the_grid_counters_have_a_different_address_in_each_model():
    def address(key: str, name: str) -> int | None:
        return {r.key: r.address for r in CATALOGUES[key].registers}[name]

    assert address("hs3", "grid_export_energy_today") == 0x416F
    assert address("h2", "grid_export_energy_today") == 0x40EF
    assert address("hs3", "grid_import_energy_today") == 0x4167
    assert address("h2", "grid_import_energy_today") == 0x40F7


def test_every_shipped_profile_has_a_catalogue_built_at_import():
    from saj.profiles import PROFILES

    assert set(CATALOGUES) == {profile.key for profile in PROFILES}
    assert all(CATALOGUES[profile.key].profile is profile for profile in PROFILES)


def test_the_shipped_catalogue_serves_a_shipped_profile():
    assert catalogue_of(profile=HS3) is CATALOGUES["hs3"]


def test_a_profile_that_is_not_shipped_gets_a_catalogue_of_its_own():
    other = replace(HS3, placements=(), families=(), replacements=())

    catalogue = catalogue_of(profile=other)

    assert catalogue is not CATALOGUES["hs3"]
    assert catalogue.registers == ()


@pytest.mark.parametrize(
    ("device_type", "shape"),
    [
        (0x005A, Shape(phases=1, strings=2)),
        (0x005B, Shape(phases=1, strings=3)),
        (UNKNOWN_TYPE, Shape(phases=3, strings=4, assumed=True)),
    ],
)
def test_device_registers_follow_the_shape_of_the_device_type(
    device_type: int, shape: Shape
):
    registers = device_registers(profile=H2, device_type=device_type)

    assert registers == CATALOGUES["h2"].registers_for(shape=shape)


def test_a_roles_family_marks_rows_beyond_the_first_phase_or_string():
    family = Family(
        name="phased",
        stem="grid_l{index}",
        base=0x1000,
        count=3,
        role=Role.PHASE,
        stride=1,
        members=(Member(offset=0, definition=_definition("voltage")),),
    )
    profile = _profile(
        families=(FamilyPlacement(family="phased", evidence=Evidence.VERIFIED),)
    )

    catalogue = _build(
        *family.definitions(), profile=profile, families={"phased": family}
    )

    assert [register.definition.phases for register in catalogue.registers] == [1, 2, 3]


def _blocks_profile(*keys: str) -> Profile:
    return replace(
        profile(
            base=HS3, key="blocks", device_types={1}, keys=keys, hand_verified=True
        ),
        spans=(
            Span(name="realtime", first=0x4000, last=0x40FF),
            Span(name="settings", first=0x3600, last=0x36FF),
            Span(name="parallel", first=0x4200, last=0x427C),
        ),
    )


def test_blocks_name_the_span_of_each_row_in_register_order_with_energy_split_out():
    selected = _blocks_profile(
        "backup_reserve_soc", "pv_energy_today", "pv_power", "operating_mode"
    )

    blocks = blocks_by_key(profile=selected, device_type=1)

    assert list(blocks.items()) == [
        ("backup_reserve_soc", "settings"),
        ("operating_mode", "realtime"),
        ("pv_power", "realtime"),
        ("pv_energy_today", "energy"),
    ]


def test_a_combined_row_sits_with_its_lowest_source_in_register_order():
    selected = replace(
        _blocks_profile(
            "parallel_pv_power_high_word",
            "parallel_pv_power_low_word",
            "parallel_pv_power",
            "operating_mode",
        ),
        spans=(
            Span(name="realtime", first=0x4000, last=0x40FF),
            Span(name="parallel", first=0x4200, last=0x427C),
        ),
    )

    blocks = blocks_by_key(profile=selected, device_type=1)

    assert list(blocks.items()) == [
        ("operating_mode", "realtime"),
        ("parallel_pv_power_low_word", "parallel"),
        ("parallel_pv_power", "parallel"),
        ("parallel_pv_power_high_word", "parallel"),
    ]


def test_the_keys_of_a_device_are_those_of_its_registers():
    selected = _blocks_profile("pv_power", "operating_mode")

    assert device_keys(profile=selected, device_type=1) == {
        "pv_power",
        "operating_mode",
    }


def test_the_known_keys_cover_every_given_profile():
    first = _blocks_profile("pv_power")
    second = replace(_blocks_profile("operating_mode"), key="second")

    assert known_keys(profiles=[first, second]) == {"pv_power", "operating_mode"}
    assert known_keys(profiles=[]) == frozenset()


def _command(key: str, value: int, **changes: object) -> Definition:
    return _definition(
        key,
        kind=EntityKind.BUTTON,
        access=Access.WRITE_ONLY,
        command_value=value,
        **changes,
    )


def _write_only(key: str, **changes: object) -> Definition:
    return _definition(
        key,
        kind=EntityKind.NUMBER,
        access=Access.WRITE_ONLY,
        range=Range(minimum=0, maximum=9),
        **changes,
    )


OUTSIDE = 0x2010
SPAN_END = 0x10FF


def test_a_write_only_row_outside_every_span_is_accepted():
    catalogue = _build(
        _definition("alpha"),
        _write_only("target"),
        profile=_profile(_at("alpha", 0x1010), _at("target", OUTSIDE)),
    )

    assert [register.key for register in catalogue.registers] == ["alpha", "target"]


@pytest.mark.parametrize(
    ("address", "words"),
    [(0x1010, 1), (SPAN_END, 1), (SPAN_END, 2), (0x0FFF, 2), (0x0FFF, 0x200)],
)
def test_a_write_only_row_touching_a_span_is_rejected(address: int, words: int):
    with pytest.raises(CatalogueError, match="lies inside a span"):
        _build(
            _write_only("target", words=words, encoding=Encoding.TEXT),
            profile=_profile(_at("target", address)),
        )


@pytest.mark.parametrize("address", [0x0FFE, 0x1100])
def test_a_write_only_row_next_to_a_span_is_accepted(address: int):
    catalogue = _build(_write_only("target"), profile=_profile(_at("target", address)))

    assert catalogue.registers[0].address == address


def test_a_write_only_row_is_not_held_to_the_largest_read_request():
    catalogue = _build(
        _write_only("target", words=40, encoding=Encoding.TEXT),
        profile=_profile(_at("target", OUTSIDE)),
    )

    assert catalogue.registers[0].words == 40


def test_a_row_that_is_read_must_still_lie_inside_a_span():
    with pytest.raises(CatalogueError, match="outside every span"):
        _build(_definition("alpha"), profile=_profile(_at("alpha", OUTSIDE)))


def test_commands_with_different_values_may_share_a_register():
    catalogue = _build(
        _command("clear_history", 1),
        _command("clear_current", 2),
        profile=_profile(_at("clear_history", OUTSIDE), _at("clear_current", OUTSIDE)),
    )

    assert catalogue.unread_rows_for(shape=SHAPE) == (Row(address=OUTSIDE, words=1),)
    assert {register.command_value for register in catalogue.registers} == {1, 2}


def test_a_command_may_share_a_register_with_one_write_only_number():
    catalogue = _build(
        _write_only("limit"),
        _command("limit_remove", 0xFFFF),
        profile=_profile(_at("limit", OUTSIDE), _at("limit_remove", OUTSIDE)),
    )

    assert len(catalogue.registers) == 2


@pytest.mark.parametrize(
    "definitions",
    [
        [_command("one", 1), _command("same", 1)],
        [_write_only("one"), _write_only("two")],
        [_write_only("one"), _write_only("two"), _command("three", 3)],
        [_definition("one"), _command("two", 2)],
        [_command("one", 1), _definition("two", field=BitRange(first=0, last=0))],
    ],
    ids=[
        "same-value",
        "two-numbers",
        "two-numbers-and-a-command",
        "read-row-and-command",
        "command-and-packed-field",
    ],
)
def test_other_ways_of_sharing_a_register_are_rejected(definitions: list[Definition]):
    placements = [_at(definition.key, OUTSIDE) for definition in definitions]

    with pytest.raises(CatalogueError, match="share"):
        _build(*definitions, profile=_profile(*placements))


def test_a_write_only_row_cannot_be_a_packed_field():
    with pytest.raises(CatalogueError, match="cannot be a packed field"):
        _build(
            _write_only("flag", field=BitRange(first=0, last=0)),
            profile=_profile(_at("flag", OUTSIDE)),
        )


def test_a_row_with_a_fixed_command_value_must_be_write_only():
    with pytest.raises(CatalogueError, match="must be write-only"):
        _build(
            _definition("alpha", command_value=1),
            profile=_profile(_at("alpha", 0x1010)),
        )


def test_the_rows_of_a_shape_split_into_those_read_and_those_not_read():
    catalogue = _build(
        _definition("alpha"),
        _definition("wide", encoding=Encoding.U32),
        _write_only("target"),
        _command("restart", 1),
        _command("reset", 2),
        profile=_profile(
            _at("alpha", 0x1010),
            _at("wide", 0x1020),
            _at("target", OUTSIDE),
            _at("restart", OUTSIDE + 4),
            _at("reset", OUTSIDE + 4),
        ),
    )

    assert [r.key for r in catalogue.read_registers_for(shape=SHAPE)] == [
        "alpha",
        "wide",
    ]
    assert [r.key for r in catalogue.unread_registers_for(shape=SHAPE)] == [
        "target",
        "reset",
        "restart",
    ]
    assert catalogue.rows_for(shape=SHAPE) == (
        Row(address=0x1010, words=1),
        Row(address=0x1020, words=2),
    )
    assert catalogue.unread_rows_for(shape=SHAPE) == (
        Row(address=OUTSIDE, words=1),
        Row(address=OUTSIDE + 4, words=1),
    )
    assert [r.key for r in catalogue.registers_for(shape=SHAPE)] == [
        "alpha",
        "wide",
        "target",
        "reset",
        "restart",
    ]


def test_the_keys_a_device_reads_leave_out_the_rows_that_are_only_written():
    selected = _blocks_profile("pv_power", "operating_mode", "ems_grid_power_target")

    assert device_keys(profile=selected, device_type=1) == {
        "pv_power",
        "operating_mode",
    }
    assert known_keys(profiles=[selected]) == {
        "pv_power",
        "operating_mode",
        "ems_grid_power_target",
    }


def test_the_registers_of_a_device_split_into_those_read_and_those_not():
    selected = _blocks_profile(
        "pv_power", "clear_fault_history", "clear_current_fault", "operating_mode"
    )

    assert {r.key for r in device_read_registers(profile=selected, device_type=1)} == {
        "pv_power",
        "operating_mode",
    }
    assert {
        r.key for r in device_unread_registers(profile=selected, device_type=1)
    } == {"clear_fault_history", "clear_current_fault"}
    assert {r.key for r in device_registers(profile=selected, device_type=1)} == {
        "pv_power",
        "operating_mode",
        "clear_fault_history",
        "clear_current_fault",
    }


def test_blocks_are_listed_only_for_rows_that_are_read():
    selected = _blocks_profile("pv_power", "ems_grid_power_target")

    assert blocks_by_key(profile=selected, device_type=1) == {"pv_power": "realtime"}
