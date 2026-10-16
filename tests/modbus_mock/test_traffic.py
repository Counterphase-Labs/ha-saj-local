import json

import pytest

from saj_modbus_mock.traffic import (
    Answer,
    Client,
    ConnectionEvent,
    ConnectionReason,
    ConnectionRecord,
    DecodedField,
    Operation,
    Recorder,
    RequestRecord,
)

CLIENT = Client(address="10.0.0.9", port=5555)
OTHER = Client(address="10.0.0.10", port=6666)
START = 10_000.0


def request(**changes):
    values = {
        "at": START,
        "client": CLIENT,
        "connection": 1,
        "transaction_id": 1,
        "unit_id": 1,
        "function": 3,
        "start": 0x10,
        "count": 2,
        "operation": Operation.READ,
        "answer": Answer.ANSWERED,
        "exception_code": None,
        "fault": None,
        "late_duplicate": False,
        "duration_ms": 1.5,
        "words": (7, 8),
    }
    values.update(changes)
    return RequestRecord(**values)


def connection(**changes):
    values = {
        "at": START,
        "client": CLIENT,
        "connection": 1,
        "event": ConnectionEvent.OPENED,
    }
    values.update(changes)
    return ConnectionRecord(**values)


class FakeDecoder:
    def __init__(self):
        self.calls = []

    def decode(self, *, start, words):
        self.calls.append((start, words))
        return [
            DecodedField(
                address=start, name="battery_soc", words=words[:1], value=5.5, label="x"
            )
        ]


def total(*, recorder, now=START):
    return recorder.counters(now=now)["total"]


def test_a_connection_event_is_recorded_with_its_fields_and_a_sequence_number():
    recorder = Recorder()

    recorder.record_connection(
        record=connection(
            event=ConnectionEvent.REFUSED, reason=ConnectionReason.LOCKOUT
        )
    )
    recorder.record_connection(record=connection(event=ConnectionEvent.OPENED))

    assert recorder.entries_after(after=0) == [
        {
            "sequence": 1,
            "kind": "connection",
            "at": START,
            "client": "10.0.0.9",
            "port": 5555,
            "connection": 1,
            "event": "refused",
            "reason": "lockout",
        },
        {
            "sequence": 2,
            "kind": "connection",
            "at": START,
            "client": "10.0.0.9",
            "port": 5555,
            "connection": 1,
            "event": "opened",
            "reason": None,
        },
    ]


def test_a_request_is_recorded_with_its_fields_and_the_decoded_detail():
    decoder = FakeDecoder()
    recorder = Recorder(decoder=decoder)

    recorder.record_request(
        record=request(fault="busy", late_duplicate=True, transaction_id=9)
    )

    assert recorder.entries_after(after=0) == [
        {
            "sequence": 1,
            "kind": "request",
            "at": START,
            "client": "10.0.0.9",
            "port": 5555,
            "connection": 1,
            "transaction_id": 9,
            "unit_id": 1,
            "function": 3,
            "start": 0x10,
            "count": 2,
            "operation": "read",
            "answer": "answered",
            "exception_code": None,
            "fault": "busy",
            "late_duplicate": True,
            "duration_ms": 1.5,
            "detail": {
                "words": [7, 8],
                "fields": [
                    {
                        "address": 0x10,
                        "name": "battery_soc",
                        "words": [7],
                        "value": 5.5,
                        "label": "x",
                    }
                ],
            },
        }
    ]
    assert decoder.calls == [(0x10, (7, 8))]


@pytest.mark.parametrize(
    ("decoder", "words"),
    [(None, (7, 8)), (FakeDecoder(), ())],
)
def test_the_detail_has_no_fields_without_a_decoder_or_without_words(decoder, words):
    recorder = Recorder(decoder=decoder)

    recorder.record_request(record=request(words=words))

    assert recorder.entries_after(after=0)[0]["detail"] == {
        "words": list(words),
        "fields": [],
    }


def test_entries_are_json_serialisable_with_the_counters_and_history():
    recorder = Recorder(decoder=FakeDecoder())
    recorder.record_connection(record=connection())
    recorder.record_request(record=request())
    recorder.record_request(
        record=request(answer=Answer.EXCEPTION, exception_code=0x81, words=())
    )

    json.dumps(recorder.traffic(after=0, now=START))


def test_the_log_keeps_only_the_last_two_thousand_entries():
    recorder = Recorder()

    for _ in range(2005):
        recorder.record_request(record=request())

    kept = recorder.entries_after(after=0)
    assert len(recorder._log) == 2000
    assert kept[0]["sequence"] == 6
    assert recorder.traffic(after=0, now=START)["latest"] == 2005


def test_after_returns_only_later_entries_and_at_most_five_hundred():
    recorder = Recorder()
    for _ in range(700):
        recorder.record_request(record=request())

    first = recorder.entries_after(after=0)
    later = recorder.entries_after(after=650)

    assert len(first) == 500
    assert first[0]["sequence"] == 1
    assert [entry["sequence"] for entry in later] == list(range(651, 701))
    assert recorder.entries_after(after=700) == []


def test_connection_events_are_counted_in_total_and_per_client():
    recorder = Recorder()
    events = [
        (CLIENT, 1, ConnectionEvent.OPENED),
        (CLIENT, 1, ConnectionEvent.CLOSED_BY_CLIENT),
        (CLIENT, 2, ConnectionEvent.OPENED),
        (CLIENT, 2, ConnectionEvent.CLOSED_BY_MODULE),
        (OTHER, 3, ConnectionEvent.REFUSED),
        (OTHER, 4, ConnectionEvent.OPENED),
    ]
    for client, number, event in events:
        recorder.record_connection(
            record=connection(client=client, connection=number, event=event)
        )

    counters = recorder.counters(now=START)

    def seen(scope):
        return (
            scope["connections_opened"],
            scope["connections_closed"],
            scope["connections_refused"],
        )

    assert seen(counters["total"]) == (3, 2, 1)
    assert seen(counters["clients"]["10.0.0.9"]) == (2, 2, 0)
    assert seen(counters["clients"]["10.0.0.10"]) == (1, 0, 1)


def test_connected_clients_are_those_opened_and_not_yet_closed():
    recorder = Recorder()
    recorder.record_connection(record=connection(connection=1, at=START))
    recorder.record_connection(
        record=connection(connection=2, client=OTHER, at=START + 1)
    )
    recorder.record_connection(
        record=connection(connection=3, event=ConnectionEvent.REFUSED)
    )
    recorder.record_connection(
        record=connection(connection=1, event=ConnectionEvent.CLOSED_BY_CLIENT)
    )
    recorder.record_connection(
        record=connection(connection=9, event=ConnectionEvent.CLOSED_BY_MODULE)
    )

    assert recorder.counters(now=START)["connected"] == [
        {"connection": 2, "client": "10.0.0.10", "port": 6666, "since": START + 1}
    ]


def test_requests_reads_writes_and_registers_are_counted_per_client_and_in_total():
    recorder = Recorder()
    recorder.record_request(record=request())
    recorder.record_request(record=request(words=(1, 2, 3), count=3))
    recorder.record_request(
        record=request(operation=Operation.WRITE, function=6, words=(4,), count=1)
    )
    recorder.record_request(
        record=request(
            client=OTHER, operation=Operation.WRITE, function=16, words=(1, 2), count=2
        )
    )
    recorder.record_request(record=request(operation=Operation.OTHER, words=()))

    counters = recorder.counters(now=START)

    def seen(scope):
        return tuple(
            scope[key]
            for key in (
                "requests",
                "reads",
                "writes",
                "registers_read",
                "registers_written",
            )
        )

    assert seen(counters["total"]) == (5, 2, 2, 5, 3)
    assert seen(counters["clients"]["10.0.0.9"]) == (4, 2, 1, 5, 1)
    assert seen(counters["clients"]["10.0.0.10"]) == (1, 0, 1, 0, 2)


def test_registers_are_only_counted_for_requests_that_were_answered():
    recorder = Recorder()
    recorder.record_request(
        record=request(answer=Answer.EXCEPTION, exception_code=2, words=(1, 2))
    )

    assert total(recorder=recorder)["registers_read"] == 0


def test_exceptions_no_answers_and_dropped_connections_are_counted():
    recorder = Recorder()
    outcomes = [
        (Answer.EXCEPTION, 2),
        (Answer.EXCEPTION, 2),
        (Answer.EXCEPTION, 0),
        (Answer.EXCEPTION, 0x81),
        (Answer.NO_ANSWER, None),
        (Answer.IGNORED, None),
        (Answer.DROPPED, None),
        (Answer.ANSWERED, None),
    ]
    for answer, code in outcomes:
        recorder.record_request(
            record=request(answer=answer, exception_code=code, words=())
        )

    counters = total(recorder=recorder)

    assert counters["exceptions"] == {"0": 1, "2": 2, "129": 1}
    assert counters["no_answers"] == 2
    assert counters["dropped_connections"] == 1


@pytest.mark.parametrize(
    ("seconds_after_start", "last_10", "last_60"),
    [(9, 3, 3), (12, 2, 3), (14.5, 1, 3), (20, 0, 3), (61, 0, 2), (69, 0, 0)],
)
def test_the_ten_and_sixty_second_windows_slide_with_the_time_asked(
    seconds_after_start, last_10, last_60
):
    recorder = Recorder()
    for offset in (0, 4, 8):
        recorder.record_request(record=request(at=START + offset))

    counters = total(recorder=recorder, now=START + seconds_after_start)

    assert counters["requests_last_10_seconds"] == last_10
    assert counters["requests_last_60_seconds"] == last_60


@pytest.mark.parametrize(
    ("seconds_after_start", "registers"), [(9, 6), (61, 3), (69, 0)]
)
def test_registers_moved_in_the_last_sixty_seconds_slide_per_client_and_in_total(
    seconds_after_start, registers
):
    recorder = Recorder()
    recorder.record_request(record=request(at=START, words=(1, 2, 3)))
    recorder.record_request(
        record=request(at=START + 8, operation=Operation.WRITE, words=(1, 2, 3))
    )
    recorder.record_request(record=request(at=START + 8, operation=Operation.OTHER))
    recorder.record_request(
        record=request(at=START + 8, answer=Answer.EXCEPTION, exception_code=2)
    )
    recorder.record_request(record=request(at=START + 8, client=OTHER, words=()))

    counters = recorder.counters(now=START + seconds_after_start)

    assert counters["total"]["registers_last_60_seconds"] == registers
    assert counters["clients"]["10.0.0.9"]["registers_last_60_seconds"] == registers
    assert counters["clients"]["10.0.0.10"]["registers_last_60_seconds"] == 0


def test_the_peak_sixty_second_count_is_kept_after_the_rate_falls():
    recorder = Recorder()
    for offset in range(5):
        recorder.record_request(record=request(at=START + offset))
    recorder.record_request(record=request(at=START + 500))

    counters = total(recorder=recorder, now=START + 500)

    assert counters["peak_requests_per_60_seconds"] == 5
    assert counters["requests_last_60_seconds"] == 1


def test_the_time_of_the_last_request_is_reported_per_client_and_in_total():
    recorder = Recorder()
    assert total(recorder=recorder)["last_request_at"] is None
    recorder.record_request(record=request(at=START + 1))
    recorder.record_request(record=request(at=START + 9, client=OTHER))

    counters = recorder.counters(now=START + 10)

    assert counters["total"]["last_request_at"] == START + 9
    assert counters["clients"]["10.0.0.9"]["last_request_at"] == START + 1


def test_requests_land_in_ten_second_buckets_by_outcome_in_total_and_per_client():
    recorder = Recorder()
    recorder.record_request(record=request(at=10_001.0))
    recorder.record_request(record=request(at=10_009.9))
    recorder.record_request(
        record=request(at=10_012.0, answer=Answer.EXCEPTION, exception_code=2)
    )
    recorder.record_request(
        record=request(at=10_013.0, client=OTHER, answer=Answer.NO_ANSWER)
    )
    recorder.record_request(
        record=request(at=10_014.0, client=OTHER, answer=Answer.DROPPED)
    )
    recorder.record_request(
        record=request(at=10_015.0, client=OTHER, answer=Answer.IGNORED)
    )

    history = recorder.history(now=10_020.0)

    assert history["bucket_seconds"] == 10
    assert history["total"] == [
        {"start": 10_000, "answered": 2, "exception": 0, "unanswered": 0},
        {"start": 10_010, "answered": 0, "exception": 1, "unanswered": 3},
    ]
    assert history["clients"]["10.0.0.10"] == [
        {"start": 10_010, "answered": 0, "exception": 0, "unanswered": 3}
    ]
    assert history["clients"]["10.0.0.9"][0]["answered"] == 2


def test_buckets_older_than_thirty_minutes_are_dropped():
    recorder = Recorder()
    recorder.record_request(record=request(at=START))
    recorder.record_request(record=request(at=START + 1000))

    assert [b["start"] for b in recorder.history(now=START + 1799)["total"]] == [
        10_000,
        11_000,
    ]
    assert [b["start"] for b in recorder.history(now=START + 1805)["total"]] == [11_000]


def test_a_later_request_forgets_buckets_more_than_thirty_minutes_older():
    recorder = Recorder()
    recorder.record_request(record=request(at=START))
    recorder.record_request(record=request(at=START + 2000))

    assert [b["start"] for b in recorder.history(now=START + 100)["total"]] == [12_000]


def test_the_last_read_time_is_kept_for_each_address_an_answered_read_covered():
    recorder = Recorder()
    recorder.record_request(record=request(at=START, start=0x10, words=(1, 2, 3)))
    recorder.record_request(record=request(at=START + 5, start=0x11, words=(1,)))
    recorder.record_request(
        record=request(at=START + 6, start=0x40, answer=Answer.EXCEPTION, words=())
    )
    recorder.record_request(
        record=request(at=START + 7, operation=Operation.WRITE, start=0x50, words=(1,))
    )

    assert recorder.last_read_times() == {0x10: START, 0x11: START + 5, 0x12: START}


def test_the_last_read_of_one_address_is_looked_up_without_copying_them_all():
    recorder = Recorder()
    recorder.record_request(record=request(at=START, start=0x10, words=(1, 2)))

    assert recorder.last_read(address=0x11) == START
    assert recorder.last_read(address=0x12) is None


def test_reset_clears_the_log_counters_history_and_read_times_but_keeps_the_sequence():
    recorder = Recorder()
    recorder.record_connection(record=connection())
    recorder.record_request(record=request())

    recorder.reset()
    recorder.record_request(record=request())

    assert [entry["sequence"] for entry in recorder.entries_after(after=0)] == [3]
    assert total(recorder=recorder)["requests"] == 1
    assert total(recorder=recorder)["peak_requests_per_60_seconds"] == 1
    assert len(recorder.history(now=START)["total"]) == 1
    assert recorder.counters(now=START)["connected"] != []
    recorder.reset()
    assert recorder.last_read_times() == {}
    assert recorder.counters(now=START)["clients"] == {}
