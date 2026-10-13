import pytest

from saj.catalogue import SERIAL_ADDRESS, SERIAL_WORD_COUNT, Fit, device_registers
from saj.memory import FailureOutcome, RegisterMemory
from saj.models import ALL_EQUIPMENT
from saj.models.hs3 import PROFILE as HS3

HS3_DEVICE_TYPE = 0x1610
FIT = Fit(profile=HS3, device_type=HS3_DEVICE_TYPE, equipment=ALL_EQUIPMENT)
PRIVATE_KEYS = {
    "ethernet_mac_address",
    "ethernet_ip_address",
    "ethernet_subnet_mask",
    "ethernet_gateway",
    "ethernet_dns_primary",
    "ethernet_dns_secondary",
    "ev_serial_number",
}
UNCATALOGUED_ADDRESS = 0x7777


class Clock:
    def __init__(self) -> None:
        self.now = 100.0

    def __call__(self) -> float:
        return self.now


@pytest.fixture
def clock() -> Clock:
    return Clock()


@pytest.fixture
def memory(clock: Clock) -> RegisterMemory:
    return RegisterMemory(clock=clock)


def _register(key: str):
    return next(
        register for register in device_registers(fit=FIT) if register.key == key
    )


def _entries(memory: RegisterMemory):
    return memory.snapshot(fit=FIT).registers


def test_answered_words_are_remembered_with_the_time_they_were_read(
    memory: RegisterMemory, clock: Clock
):
    clock_row = _register("inverter_clock")
    memory.record_answer(
        address=clock_row.row.address, words=[1, 2, 3, 4][: clock_row.words]
    )
    clock.now += 4.5

    (entry,) = _entries(memory)

    assert (entry.address, entry.key, entry.age_seconds) == (
        clock_row.row.address,
        "inverter_clock",
        4.5,
    )
    assert entry.words == (1, 2, 3, 4)[: clock_row.words]
    assert not entry.private


def test_a_later_read_replaces_the_words_and_restarts_their_age(
    memory: RegisterMemory, clock: Clock
):
    address = _register("operating_mode").row.address
    memory.record_answer(address=address, words=[1])
    clock.now += 30
    memory.record_answer(address=address, words=[2])
    clock.now += 1

    (entry,) = _entries(memory)

    assert (entry.words, entry.age_seconds) == ((2,), 1.0)


def test_words_in_a_catalogued_row_are_grouped_under_its_key_and_the_rest_listed_alone(
    memory: RegisterMemory,
):
    row = _register("inverter_clock").row
    memory.record_answer(address=row.address - 1, words=[9])
    memory.record_answer(address=row.address, words=list(range(row.words)))
    memory.record_answer(address=UNCATALOGUED_ADDRESS, words=[5, 6])

    entries = _entries(memory)

    assert [(entry.address, entry.key, entry.words) for entry in entries] == [
        (row.address - 1, None, (9,)),
        (row.address, "inverter_clock", tuple(range(row.words))),
        (UNCATALOGUED_ADDRESS, None, (5,)),
        (UNCATALOGUED_ADDRESS + 1, None, (6,)),
    ]


def test_entries_are_ordered_by_address_whatever_the_order_they_were_read(
    memory: RegisterMemory,
):
    for address in (0x7003, 0x7001, 0x7002):
        memory.record_answer(address=address, words=[address])

    assert [entry.address for entry in _entries(memory)] == [0x7001, 0x7002, 0x7003]


@pytest.mark.parametrize("key", sorted(PRIVATE_KEYS))
def test_private_rows_keep_their_key_and_never_expose_their_words(
    memory: RegisterMemory, key: str
):
    row = _register(key).row
    memory.record_answer(address=row.address, words=[0xBEEF] * row.words)

    (entry,) = _entries(memory)

    assert (entry.key, entry.private, entry.words) == (key, True, ())


def test_the_serial_range_is_private_although_no_row_covers_it(
    memory: RegisterMemory,
):
    memory.record_answer(address=SERIAL_ADDRESS, words=[0x4142] * SERIAL_WORD_COUNT)

    (entry,) = _entries(memory)

    assert (entry.address, entry.key, entry.private, entry.words) == (
        SERIAL_ADDRESS,
        None,
        True,
        (),
    )


@pytest.mark.parametrize(
    ("start_offset", "length"), [(0, 2), (1, 2), (2, 3), (-1, 2), (3, 5)]
)
def test_a_read_covering_only_part_of_a_private_row_exposes_none_of_its_words(
    memory: RegisterMemory, start_offset: int, length: int
):
    row = _register("ev_serial_number").row
    start = row.address + start_offset
    memory.record_answer(address=start, words=[0xBEEF + n for n in range(length)])

    entries = _entries(memory)

    exposed = {word for entry in entries for word in entry.words}
    inside = {
        0xBEEF + (address - start)
        for address in range(row.address, row.end)
        if start <= address < start + length
    }
    assert not exposed & inside


def test_a_row_with_a_gap_in_what_was_read_is_listed_as_separate_runs(
    memory: RegisterMemory, clock: Clock
):
    row = _register("ev_model").row
    memory.record_answer(address=row.address, words=[1])
    clock.now += 2
    memory.record_answer(address=row.address + 2, words=[3])

    entries = _entries(memory)

    assert [(entry.address, entry.words, entry.key) for entry in entries] == [
        (row.address, (1,), "ev_model"),
        (row.address + 2, (3,), "ev_model"),
    ]


def test_a_run_of_words_read_at_different_times_is_as_old_as_its_oldest_word(
    memory: RegisterMemory, clock: Clock
):
    row = _register("inverter_clock").row
    memory.record_answer(address=row.address, words=[1])
    clock.now += 10
    memory.record_answer(address=row.address + 1, words=[2])
    clock.now += 1

    (entry,) = _entries(memory)

    assert entry.age_seconds == 11.0


@pytest.mark.parametrize(
    ("outcome", "code"),
    [
        (FailureOutcome.EXCEPTION, 48),
        (FailureOutcome.TIMEOUT, None),
        (FailureOutcome.CONNECTION_LOST, None),
        (FailureOutcome.MALFORMED_REPLY, None),
    ],
)
def test_each_failure_outcome_is_remembered_with_its_range_and_age(
    memory: RegisterMemory, clock: Clock, outcome: FailureOutcome, code: int | None
):
    memory.record_failure(
        address=0x3024, count=32, outcome=outcome, exception_code=code
    )
    clock.now += 4

    (failure,) = memory.snapshot(fit=FIT).failed

    assert (
        failure.address,
        failure.count,
        failure.outcome,
        failure.exception_code,
        failure.age_seconds,
    ) == (0x3024, 32, outcome, code, 4.0)


def test_a_range_that_fails_again_keeps_only_its_latest_failure(
    memory: RegisterMemory, clock: Clock
):
    memory.record_failure(
        address=0x3024, count=32, outcome=FailureOutcome.EXCEPTION, exception_code=48
    )
    clock.now += 60
    memory.record_failure(address=0x3024, count=32, outcome=FailureOutcome.TIMEOUT)

    (failure,) = memory.snapshot(fit=FIT).failed

    assert (failure.outcome, failure.exception_code, failure.age_seconds) == (
        FailureOutcome.TIMEOUT,
        None,
        0.0,
    )


def test_a_failure_is_removed_when_the_same_range_answers_but_older_words_stay(
    memory: RegisterMemory, clock: Clock
):
    memory.record_answer(address=UNCATALOGUED_ADDRESS, words=[7] * 4)
    clock.now += 10
    memory.record_failure(
        address=UNCATALOGUED_ADDRESS, count=4, outcome=FailureOutcome.TIMEOUT
    )
    memory.record_failure(
        address=UNCATALOGUED_ADDRESS, count=2, outcome=FailureOutcome.TIMEOUT
    )
    clock.now += 5

    still_failed = memory.snapshot(fit=FIT)
    memory.record_answer(address=UNCATALOGUED_ADDRESS, words=[8] * 4)
    answered = memory.snapshot(fit=FIT)

    assert [entry.words for entry in still_failed.registers] == [(7,), (7,), (7,), (7,)]
    assert [entry.age_seconds for entry in still_failed.registers] == [15.0] * 4
    assert [(f.address, f.count) for f in answered.failed] == [
        (UNCATALOGUED_ADDRESS, 2)
    ]


def test_a_failure_leaves_words_remembered_at_those_addresses_with_their_own_age(
    memory: RegisterMemory, clock: Clock
):
    memory.record_answer(address=UNCATALOGUED_ADDRESS, words=[7])
    clock.now += 20
    memory.record_failure(
        address=UNCATALOGUED_ADDRESS, count=1, outcome=FailureOutcome.TIMEOUT
    )

    snapshot = memory.snapshot(fit=FIT)

    assert [(entry.words, entry.age_seconds) for entry in snapshot.registers] == [
        ((7,), 20.0)
    ]
    assert snapshot.failed[0].age_seconds == 0.0


def test_failures_are_ordered_by_address_then_count(memory: RegisterMemory):
    for address, count in ((0xA03C, 32), (0x3024, 32), (0x3024, 4)):
        memory.record_failure(
            address=address, count=count, outcome=FailureOutcome.TIMEOUT
        )

    assert [
        (failure.address, failure.count) for failure in memory.snapshot(fit=FIT).failed
    ] == [(0x3024, 4), (0x3024, 32), (0xA03C, 32)]


def test_nothing_is_remembered_while_paused_and_remembering_resumes_afterwards(
    memory: RegisterMemory,
):
    with memory.paused():
        with memory.paused():
            memory.record_answer(address=0x7001, words=[1])
        memory.record_answer(address=0x7002, words=[2])
        memory.record_failure(address=0x7003, count=1, outcome=FailureOutcome.TIMEOUT)
    memory.record_answer(address=0x7004, words=[4])

    snapshot = memory.snapshot(fit=FIT)

    assert [entry.address for entry in snapshot.registers] == [0x7004]
    assert snapshot.failed == ()
