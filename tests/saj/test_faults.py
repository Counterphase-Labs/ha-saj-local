import pytest

from saj.faults import FaultWatch, decode
from saj.models.faults import FaultMap, Source

WORD_A = 0x1000
WORD_B = 0x1002
FAULTS = FaultMap(
    words={"word_a": WORD_A, "word_b": WORD_B},
    named={
        "alpha": {WORD_A: (0,)},
        "beta": {WORD_A: (1, 31), WORD_B: (4,)},
        "gamma": {WORD_B: (5,)},
    },
)


def test_a_source_reads_as_its_register_and_bit():
    assert str(Source(register=0x4005, bit=23)) == "0x4005:23"


def test_the_sources_of_a_fault_list_every_register_and_bit_it_reports():
    assert FAULTS.sources_of(key="beta") == (
        Source(register=WORD_A, bit=1),
        Source(register=WORD_A, bit=31),
        Source(register=WORD_B, bit=4),
    )


def test_the_mask_of_a_fault_holds_only_its_bits_of_one_register():
    assert FAULTS.mask_of(key="beta", register=WORD_A) == 0x8000_0002
    assert FAULTS.mask_of(key="beta", register=WORD_B) == 0b10000
    assert FAULTS.mask_of(key="alpha", register=WORD_B) == 0


def test_the_unmapped_mask_is_every_bit_of_the_word_that_no_fault_names():
    assert FAULTS.mapped_mask(register=WORD_A) == 0x8000_0003
    assert FAULTS.unmapped_mask(register=WORD_A) == 0x7FFF_FFFC
    assert FAULTS.unmapped_mask(register=WORD_B) == 0xFFFF_FFFF & ~0b110000


def test_words_are_looked_up_by_register_and_only_whole_numbers_count():
    values = {"word_a": 5, "word_b": None, "other": 7}

    assert FAULTS.registers_of(values=values) == {WORD_A: 5}


@pytest.mark.parametrize(
    ("words", "active", "unrecognised"),
    [
        ({WORD_A: 0, WORD_B: 0}, set(), set()),
        ({WORD_A: 0b1}, {"alpha"}, set()),
        ({WORD_A: 0b10}, {"beta"}, set()),
        ({WORD_B: 0b10000}, {"beta"}, set()),
        ({WORD_A: 0x8000_0001}, {"alpha", "beta"}, set()),
        ({WORD_A: 0b100}, set(), {Source(register=WORD_A, bit=2)}),
        (
            {WORD_B: 0b100001},
            {"gamma"},
            {Source(register=WORD_B, bit=0)},
        ),
        ({WORD_A: 1 << 16}, set(), {Source(register=WORD_A, bit=16)}),
    ],
)
def test_words_decode_to_the_active_faults_and_the_bits_no_fault_names(
    words, active, unrecognised
):
    decoded = decode(fault_map=FAULTS, words=words)

    assert decoded.active == active
    assert decoded.unrecognised == unrecognised


def test_a_watch_reports_what_turned_on_and_off_between_observations():
    watch = FaultWatch(fault_map=FAULTS)

    first = watch.observe(words={WORD_A: 0b101, WORD_B: 0})
    same = watch.observe(words={WORD_A: 0b101, WORD_B: 0})
    later = watch.observe(words={WORD_A: 0b100, WORD_B: 0b100000})

    assert first.raised == {"alpha"}
    assert first.unrecognised_raised == (Source(register=WORD_A, bit=2),)
    assert first.cleared == frozenset()
    assert first.changed
    assert not same.changed
    assert later.raised == {"gamma"}
    assert later.cleared == {"alpha"}
    assert later.unrecognised_cleared == ()


def test_a_watch_clears_unrecognised_bits_that_go_away():
    watch = FaultWatch(fault_map=FAULTS)
    watch.observe(words={WORD_A: 0b100})

    cleared = watch.observe(words={WORD_A: 0})

    assert cleared.unrecognised_cleared == (Source(register=WORD_A, bit=2),)
    assert cleared.changed


def test_a_register_that_is_not_observed_keeps_its_last_known_bits():
    watch = FaultWatch(fault_map=FAULTS)
    watch.observe(words={WORD_A: 0b1, WORD_B: 0b100000})

    unseen = watch.observe(words={WORD_A: 0b1})

    assert not unseen.changed
    assert watch.observe(words={WORD_B: 0}).cleared == {"gamma"}
