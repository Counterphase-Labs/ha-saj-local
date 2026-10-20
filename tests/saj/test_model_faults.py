import pytest

from saj.models.faults import FaultMap, Source

FIRST_WORD = 0x1000
SECOND_WORD = 0x1002
FAULTS = FaultMap(
    words={"first": FIRST_WORD, "second": SECOND_WORD},
    named={
        "alpha": {FIRST_WORD: (0, 3)},
        "beta": {FIRST_WORD: (1,), SECOND_WORD: (4,)},
    },
)


def test_sources_order_by_register_then_bit():
    assert sorted([Source(register=2, bit=1), Source(register=1, bit=9)]) == [
        Source(register=1, bit=9),
        Source(register=2, bit=1),
    ]


def test_a_source_reads_as_its_padded_register_and_bit():
    assert str(Source(register=0x4005, bit=23)) == "0x4005:23"


def test_the_sources_of_a_key_list_every_register_and_bit_it_uses():
    assert FAULTS.sources_of(key="beta") == (
        Source(register=FIRST_WORD, bit=1),
        Source(register=SECOND_WORD, bit=4),
    )


def test_the_mask_of_a_key_sets_only_its_bits_in_that_register():
    assert FAULTS.mask_of(key="alpha", register=FIRST_WORD) == 0b1001


def test_the_mask_of_a_key_in_a_register_it_does_not_use_is_empty():
    assert FAULTS.mask_of(key="alpha", register=SECOND_WORD) == 0


def test_the_mapped_mask_combines_the_bits_of_every_key_in_the_register():
    assert FAULTS.mapped_mask(register=FIRST_WORD) == 0b1011


def test_the_unmapped_mask_is_every_bit_of_the_word_that_no_key_uses():
    mapped = FAULTS.mapped_mask(register=FIRST_WORD)

    unmapped = FAULTS.unmapped_mask(register=FIRST_WORD)

    assert unmapped & mapped == 0
    assert unmapped | mapped == 0xFFFFFFFF


def test_an_empty_map_leaves_the_whole_word_unmapped():
    assert FaultMap().unmapped_mask(register=FIRST_WORD) == 0xFFFFFFFF


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        ({"first": 5, "second": 7}, {FIRST_WORD: 5, SECOND_WORD: 7}),
        ({"first": 0}, {FIRST_WORD: 0}),
        ({"first": 5}, {FIRST_WORD: 5}),
        ({"first": "text", "second": None}, {}),
        ({"other": 3}, {}),
        ({}, {}),
    ],
)
def test_registers_are_taken_only_from_integer_values_of_known_words(
    values: dict[str, object], expected: dict[int, int]
):
    assert FAULTS.registers_of(values=values) == expected
