import asyncio
import struct
from types import SimpleNamespace

import pytest

from saj_modbus_mock.exceptions import ExceptionCode, ModbusError
from saj_modbus_mock.link import (
    Action,
    ConnectionDecision,
    LinkFault,
    RequestDecision,
)
from saj_modbus_mock.traffic import (
    Answer,
    Client,
    ConnectionEvent,
    ConnectionReason,
    Operation,
)
from saj_modbus_mock.transport import (
    ModbusServer,
    ServerSettings,
    Timing,
    respond,
)

IPV4_FAMILY = 2
IPV6_FAMILY = 10


class MemoryBank:
    def __init__(self):
        self.words = {address: address for address in range(0x100)}
        self.writes = []

    def read(self, *, start, count):
        if start + count > 0x100:
            raise ModbusError(code=ExceptionCode.ILLEGAL_DATA_ADDRESS)
        return [self.words[address] for address in range(start, start + count)]

    def write(self, *, start, words):
        if start >= 0x80:
            raise ModbusError(code=ExceptionCode.ILLEGAL_DATA_VALUE)
        self.writes.append((start, words))


def read_pdu(*, start, count):
    return struct.pack(">BHH", 3, start, count)


def respond_to(*, pdu, bank=None):
    return respond(bank=bank or MemoryBank(), function=pdu[0], body=pdu[1:])


def test_a_read_returns_the_requested_registers_as_big_endian_words():
    assert respond_to(pdu=read_pdu(start=0x10, count=3)) == bytes(
        [3, 6, 0, 0x10, 0, 0x11, 0, 0x12]
    )


def test_a_single_register_write_is_forwarded_and_echoed():
    bank = MemoryBank()
    pdu = struct.pack(">BHH", 6, 0x20, 0xABCD)

    assert respond_to(pdu=pdu, bank=bank) == pdu
    assert bank.writes == [(0x20, [0xABCD])]


def test_a_multiple_register_write_is_forwarded_and_acknowledged():
    bank = MemoryBank()
    pdu = struct.pack(">BHHB2H", 0x10, 0x20, 2, 4, 7, 8)

    assert respond_to(pdu=pdu, bank=bank) == struct.pack(">BHH", 0x10, 0x20, 2)
    assert bank.writes == [(0x20, [7, 8])]


@pytest.mark.parametrize(
    ("pdu", "code"),
    [
        (bytes([0x2B, 0]), 0x01),
        (read_pdu(start=0, count=0), 0x03),
        (read_pdu(start=0, count=126), 0x03),
        (read_pdu(start=0xF0, count=0x20), 0x02),
        (struct.pack(">BHHB", 0x10, 0, 0, 0), 0x03),
        (struct.pack(">BHH", 6, 0x90, 1), 0x03),
        (struct.pack(">BHHB", 0x10, 0x90, 1, 2) + bytes(2), 0x03),
    ],
)
def test_unserviceable_requests_get_an_exception_response(pdu, code):
    assert respond_to(pdu=pdu) == bytes([pdu[0] | 0x80, code])


@pytest.mark.parametrize(
    "pdu",
    [
        bytes([3, 0, 0, 0]),
        bytes([3]) + bytes(5),
        bytes([6, 0, 0, 0]),
        bytes([0x10, 0, 0]),
        struct.pack(">BHHB", 0x10, 0, 1, 4) + bytes(2),
        struct.pack(">BHHB", 0x10, 0, 2, 2) + bytes(2),
    ],
)
def test_frames_that_do_not_fit_their_function_are_reported_as_malformed(pdu):
    from saj_modbus_mock.transport import MalformedFrameError

    with pytest.raises(MalformedFrameError):
        respond_to(pdu=pdu)


class FakeWriter:
    def __init__(self, *, close_error=None, peername=("10.0.0.9", 5555)):
        self.frames = []
        self.closed = False
        self.close_error = close_error
        self.peername = peername

    def write(self, data):
        self.frames.append(data)

    async def drain(self):
        return None

    def close(self):
        self.closed = True

    async def wait_closed(self):
        if self.close_error:
            raise self.close_error

    def get_extra_info(self, name):
        assert name == "peername"
        return self.peername


class FakeTime:
    def __init__(self):
        self.now = 1000.0
        self.sleeps = []

    async def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds
        await asyncio.sleep(0)

    def clock(self):
        return self.now


def decision(*, action=Action.ANSWER, fault=None, code=0, delay=0.0, duplicate=False):
    return RequestDecision(
        action=action,
        fault=fault,
        exception_code=code,
        delay_s=delay,
        late_duplicate=duplicate,
    )


class FakeLink:
    def __init__(self, *, decisions=(), connection_fault=None, offline=False):
        self.decisions = list(decisions)
        self.connection_fault = connection_fault
        self.offline = offline
        self.drop_generation = 0
        self.requests = []

    def decide_connection(self, **_arguments):
        return ConnectionDecision(fault=self.connection_fault)

    def decide_request(self, *, client, sequence, start, count, now):
        self.requests.append((client, sequence, start, count, now))
        return self.decisions.pop(0) if self.decisions else decision()

    def is_offline(self, **_arguments):
        return self.offline


class FakeRecorder:
    def __init__(self):
        self.connections = []
        self.requests = []

    def record_connection(self, *, record):
        self.connections.append(record)

    def record_request(self, *, record):
        self.requests.append(record)


def mbap(*, pdu, transaction=1, protocol=0, unit=1, length=None):
    length = len(pdu) + 1 if length is None else length
    return struct.pack(">HHHB", transaction, protocol, length, unit) + pdu


def make_server(*, bank=None, link=None, recorder=None, fake_time=None, **overrides):
    settings = {"unit_id": 1, "max_clients": 2, "host": "127.0.0.1", "port": 0}
    settings.update(overrides)
    fake_time = fake_time or FakeTime()
    return ModbusServer(
        bank=bank or MemoryBank(),
        settings=ServerSettings(**settings),
        link=link or FakeLink(),
        recorder=recorder or FakeRecorder(),
        timing=Timing(sleep=fake_time.sleep, clock=fake_time.clock),
    )


async def serve(*, server, data, eof=True, writer=None):
    reader = asyncio.StreamReader()
    reader.feed_data(data)
    if eof:
        reader.feed_eof()
    writer = writer or FakeWriter()
    await server._serve_client(reader, writer)
    return writer


async def test_each_request_is_answered_in_turn_with_its_own_transaction_id():
    data = mbap(pdu=read_pdu(start=0x10, count=1), transaction=0xBEEF) + mbap(
        pdu=read_pdu(start=0x20, count=2), transaction=7
    )

    writer = await serve(server=make_server(), data=data)

    assert writer.frames == [
        mbap(pdu=bytes([3, 2, 0, 0x10]), transaction=0xBEEF),
        mbap(pdu=bytes([3, 4, 0, 0x20, 0, 0x21]), transaction=7),
    ]
    assert writer.closed


async def test_requests_for_another_unit_get_no_reply_but_the_connection_carries_on():
    data = mbap(pdu=read_pdu(start=0, count=1), unit=9) + mbap(
        pdu=read_pdu(start=0, count=1), transaction=2
    )

    writer = await serve(server=make_server(), data=data)

    assert writer.frames == [mbap(pdu=bytes([3, 2, 0, 0]), transaction=2)]


@pytest.mark.parametrize(
    "frame",
    [
        mbap(pdu=read_pdu(start=0, count=1), protocol=7),
        struct.pack(">HHHB", 1, 0, 1, 1),
        struct.pack(">HHHB", 1, 0, 255, 1),
        mbap(pdu=bytes([3, 0, 0, 0])),
    ],
)
async def test_malformed_frames_close_the_connection_without_a_reply(frame):
    writer = await serve(server=make_server(), data=frame, eof=False)

    assert writer.frames == []
    assert writer.closed


async def test_a_truncated_frame_ends_the_connection_quietly():
    writer = await serve(
        server=make_server(), data=mbap(pdu=read_pdu(start=0, count=1))[:-2]
    )

    assert writer.frames == []
    assert writer.closed


async def test_a_connection_error_while_closing_is_swallowed():
    writer = await serve(
        server=make_server(),
        data=b"",
        writer=FakeWriter(close_error=ConnectionResetError()),
    )

    assert writer.closed


async def test_clients_beyond_the_limit_are_dropped_until_one_leaves():
    server = make_server(max_clients=1)
    first_reader = asyncio.StreamReader()
    first_writer = FakeWriter()
    first = asyncio.create_task(server._serve_client(first_reader, first_writer))
    await asyncio.sleep(0)

    second = await serve(server=server, data=mbap(pdu=read_pdu(start=0, count=1)))

    assert second.frames == []
    assert second.closed
    assert not first_writer.closed
    first_reader.feed_eof()
    await first
    assert first_writer.closed
    third = await serve(server=server, data=mbap(pdu=read_pdu(start=0, count=1)))
    assert len(third.frames) == 1


class FakeServer:
    def __init__(self, ports):
        self.sockets = [
            SimpleNamespace(
                family=family, getsockname=lambda port=port: ("127.0.0.1", port)
            )
            for family, port in ports
        ]
        self.closed = False
        self.waited = False

    def close(self):
        self.closed = True

    async def wait_closed(self):
        self.waited = True


@pytest.fixture
def fake_listener(monkeypatch):
    created = {"starts": []}

    async def start_server(handler, *, host, port):
        created.update(handler=handler, host=host, port=port)
        created["starts"].append((host, port))
        created["server"] = FakeServer(ports=[(IPV6_FAMILY, 6000), (IPV4_FAMILY, 5000)])
        return created["server"]

    monkeypatch.setattr(asyncio, "start_server", start_server)
    return created


async def test_starting_listens_on_the_configured_address_and_reports_the_ipv4_port(
    fake_listener,
):
    server = make_server(host="10.0.0.1", port=1502)

    await server.start()

    assert (fake_listener["host"], fake_listener["port"]) == ("10.0.0.1", 1502)
    assert server.bound_port == 5000
    await server.close()


async def test_closing_stops_listening_and_disconnects_connected_clients(fake_listener):
    server = make_server()
    await server.start()
    reader = asyncio.StreamReader()
    writer = FakeWriter()
    client = asyncio.create_task(server._serve_client(reader, writer))
    await asyncio.sleep(0)

    await server.close()

    assert fake_listener["server"].closed
    assert fake_listener["server"].waited
    assert writer.closed
    reader.feed_eof()
    await client


async def test_a_server_that_never_started_has_no_port_and_closes_quietly():
    server = make_server()

    with pytest.raises(RuntimeError, match="not started"):
        _ = server.bound_port
    await server.close()


def read_frame(*, transaction=1):
    return mbap(pdu=read_pdu(start=0x10, count=1), transaction=transaction)


async def test_every_answer_waits_for_the_latency_the_link_decided_before_it_is_sent():
    fake_time = FakeTime()
    link = FakeLink(decisions=[decision(delay=0.25), decision()])

    writer = await serve(
        server=make_server(link=link, fake_time=fake_time),
        data=read_frame() + read_frame(transaction=2),
    )

    assert fake_time.sleeps == [0.25]
    assert len(writer.frames) == 2


async def test_the_link_is_asked_about_each_request_with_its_client_span_and_sequence():
    link = FakeLink()
    data = (
        read_frame()
        + mbap(pdu=struct.pack(">BHH", 6, 0x20, 5))
        + mbap(pdu=struct.pack(">BHHB2H", 0x10, 0x30, 2, 4, 1, 2))
        + mbap(pdu=bytes([0x2B, 0]))
    )

    await serve(server=make_server(link=link), data=data)

    assert [request[:4] for request in link.requests] == [
        ("10.0.0.9", 1, 0x10, 1),
        ("10.0.0.9", 2, 0x20, 1),
        ("10.0.0.9", 3, 0x30, 2),
        ("10.0.0.9", 4, 0, 0),
    ]


async def test_an_unanswered_request_gets_no_reply_and_the_connection_stays_open():
    link = FakeLink(decisions=[decision(action=Action.NO_ANSWER), decision()])
    bank = MemoryBank()
    data = mbap(pdu=struct.pack(">BHH", 6, 0x20, 5)) + read_frame(transaction=2)

    writer = await serve(server=make_server(link=link, bank=bank), data=data)

    assert writer.frames == [mbap(pdu=bytes([3, 2, 0, 0x10]), transaction=2)]
    assert bank.writes == []


@pytest.mark.parametrize(
    ("fault", "reason"),
    [
        (LinkFault.DROPPED_CONNECTION, ConnectionReason.LINK_FAULT),
        (LinkFault.OFFLINE, ConnectionReason.LINK_FAULT),
        (LinkFault.LOCKOUT, ConnectionReason.LOCKOUT),
    ],
)
async def test_a_dropped_request_closes_the_connection_and_ignores_what_follows(
    fault, reason
):
    link = FakeLink(decisions=[decision(action=Action.DROP, fault=fault)])
    recorder = FakeRecorder()

    writer = await serve(
        server=make_server(link=link, recorder=recorder),
        data=read_frame() + read_frame(transaction=2),
        eof=False,
    )

    assert writer.frames == []
    assert writer.closed
    assert len(link.requests) == 1
    assert recorder.requests[0].answer is Answer.DROPPED
    assert recorder.requests[0].fault is fault
    assert (recorder.connections[-1].event, recorder.connections[-1].reason) == (
        ConnectionEvent.CLOSED_BY_MODULE,
        reason,
    )


@pytest.mark.parametrize("code", [0x00, 0x04, 0x06, 0x7F, 0x81, 0xFF])
async def test_the_link_can_answer_any_byte_as_an_exception_code(code):
    link = FakeLink(
        decisions=[decision(action=Action.EXCEPTION, fault=LinkFault.BUSY, code=code)]
    )
    recorder = FakeRecorder()

    writer = await serve(
        server=make_server(link=link, recorder=recorder), data=read_frame()
    )

    assert writer.frames == [mbap(pdu=bytes([0x83, code]))]
    record = recorder.requests[0]
    assert (record.answer, record.exception_code) == (Answer.EXCEPTION, code)
    assert record.words == ()


async def test_a_late_duplicate_of_an_exception_is_sent_just_before_the_next_answer():
    link = FakeLink(
        decisions=[
            decision(
                action=Action.EXCEPTION, fault=LinkFault.BUSY, code=6, duplicate=True
            ),
            decision(),
        ]
    )
    recorder = FakeRecorder()

    writer = await serve(
        server=make_server(link=link, recorder=recorder),
        data=read_frame(transaction=5) + read_frame(transaction=6),
    )

    exception = mbap(pdu=bytes([0x83, 6]), transaction=5)
    assert writer.frames == [
        exception,
        exception,
        mbap(pdu=bytes([3, 2, 0, 0x10]), transaction=6),
    ]
    assert [record.late_duplicate for record in recorder.requests] == [True, False]


async def test_a_late_duplicate_is_only_made_of_exception_answers_and_only_once():
    link = FakeLink(decisions=[decision(duplicate=True), decision(), decision()])

    writer = await serve(
        server=make_server(link=link),
        data=read_frame() + read_frame(transaction=2) + read_frame(transaction=3),
    )

    assert len(writer.frames) == 3


async def test_a_late_duplicate_made_of_a_model_exception_is_sent_too():
    link = FakeLink(decisions=[decision(duplicate=True), decision()])
    data = mbap(pdu=read_pdu(start=0xF0, count=0x20)) + read_frame(transaction=2)

    writer = await serve(server=make_server(link=link), data=data)

    assert [frame[7:] for frame in writer.frames] == [
        bytes([0x83, 2]),
        bytes([0x83, 2]),
        bytes([3, 2, 0, 0x10]),
    ]


async def test_a_pending_duplicate_waits_through_requests_that_are_not_answered():
    link = FakeLink(
        decisions=[
            decision(action=Action.EXCEPTION, code=6, duplicate=True),
            decision(action=Action.NO_ANSWER),
            decision(),
        ]
    )

    writer = await serve(
        server=make_server(link=link),
        data=read_frame() + read_frame(transaction=2) + read_frame(transaction=3),
    )

    assert [frame[7:] for frame in writer.frames] == [
        bytes([0x83, 6]),
        bytes([0x83, 6]),
        bytes([3, 2, 0, 0x10]),
    ]


@pytest.mark.parametrize(
    ("fault", "reason"),
    [
        (LinkFault.OFFLINE, ConnectionReason.OFFLINE),
        (LinkFault.LOCKOUT, ConnectionReason.LOCKOUT),
    ],
)
async def test_a_connection_the_link_refuses_is_closed_unanswered_and_recorded(
    fault, reason
):
    recorder = FakeRecorder()
    server = make_server(link=FakeLink(connection_fault=fault), recorder=recorder)

    writer = await serve(server=server, data=read_frame())

    assert writer.frames == []
    assert writer.closed
    assert [(r.event, r.reason) for r in recorder.connections] == [
        (ConnectionEvent.REFUSED, reason)
    ]
    assert recorder.requests == []


async def test_connections_beyond_the_limit_are_recorded_as_refused():
    recorder = FakeRecorder()
    server = make_server(max_clients=0, recorder=recorder)

    await serve(server=server, data=b"")

    assert [(r.event, r.reason) for r in recorder.connections] == [
        (ConnectionEvent.REFUSED, ConnectionReason.CLIENT_LIMIT)
    ]


async def test_a_connection_is_recorded_when_opened_and_when_the_client_closes_it():
    recorder = FakeRecorder()
    fake_time = FakeTime()

    await serve(server=make_server(recorder=recorder, fake_time=fake_time), data=b"")

    assert [(r.event, r.reason) for r in recorder.connections] == [
        (ConnectionEvent.OPENED, None),
        (ConnectionEvent.CLOSED_BY_CLIENT, None),
    ]
    first = recorder.connections[0]
    assert (first.at, first.client, first.connection) == (
        1000.0,
        Client(address="10.0.0.9", port=5555),
        1,
    )


async def test_connections_are_numbered_in_order_of_arrival():
    recorder = FakeRecorder()
    server = make_server(recorder=recorder)

    await serve(server=server, data=b"")
    await serve(server=server, data=b"")

    assert [r.connection for r in recorder.connections] == [1, 1, 2, 2]


async def test_a_malformed_frame_is_recorded_as_closed_by_the_module():
    recorder = FakeRecorder()

    await serve(
        server=make_server(recorder=recorder),
        data=mbap(pdu=read_pdu(start=0, count=1), protocol=7),
        eof=False,
    )

    assert (recorder.connections[-1].event, recorder.connections[-1].reason) == (
        ConnectionEvent.CLOSED_BY_MODULE,
        ConnectionReason.MALFORMED_FRAME,
    )
    assert recorder.requests == []


async def test_a_peer_with_no_address_is_recorded_as_unknown():
    recorder = FakeRecorder()

    await serve(
        server=make_server(recorder=recorder),
        data=b"",
        writer=FakeWriter(peername=None),
    )

    assert recorder.connections[0].client == Client(address="unknown", port=0)


async def test_an_answered_read_is_recorded_with_its_span_words_and_time_to_answer():
    recorder = FakeRecorder()
    link = FakeLink(decisions=[decision(delay=0.5)])

    await serve(
        server=make_server(link=link, recorder=recorder),
        data=mbap(pdu=struct.pack(">BHH", 3, 0x10, 2), transaction=0x1234),
    )

    record = recorder.requests[0]
    assert (
        record.at,
        record.client,
        record.connection,
        record.transaction_id,
        record.unit_id,
        record.function,
        record.start,
        record.count,
        record.operation,
        record.answer,
        record.exception_code,
        record.fault,
        record.late_duplicate,
        record.duration_ms,
        record.words,
    ) == (
        1000.0,
        Client(address="10.0.0.9", port=5555),
        1,
        0x1234,
        1,
        3,
        0x10,
        2,
        Operation.READ,
        Answer.ANSWERED,
        None,
        None,
        False,
        500.0,
        (0x10, 0x11),
    )


@pytest.mark.parametrize(
    ("pdu", "start", "count", "words"),
    [
        (struct.pack(">BHH", 6, 0x20, 0xABCD), 0x20, 1, (0xABCD,)),
        (struct.pack(">BHHB2H", 0x10, 0x20, 2, 4, 7, 8), 0x20, 2, (7, 8)),
    ],
)
async def test_an_answered_write_is_recorded_with_the_words_written(
    pdu, start, count, words
):
    recorder = FakeRecorder()

    await serve(server=make_server(recorder=recorder), data=mbap(pdu=pdu))

    record = recorder.requests[0]
    assert (record.operation, record.start, record.count, record.words) == (
        Operation.WRITE,
        start,
        count,
        words,
    )


async def test_a_refused_write_is_recorded_as_an_exception_with_no_words():
    recorder = FakeRecorder()
    pdu = struct.pack(">BHH", 6, 0x90, 1)

    await serve(server=make_server(recorder=recorder), data=mbap(pdu=pdu))

    record = recorder.requests[0]
    assert (record.answer, record.exception_code, record.words) == (
        Answer.EXCEPTION,
        ExceptionCode.ILLEGAL_DATA_VALUE,
        (),
    )


async def test_other_functions_and_unanswered_requests_are_recorded_by_their_outcome():
    recorder = FakeRecorder()
    link = FakeLink(
        decisions=[
            decision(),
            decision(action=Action.NO_ANSWER, fault=LinkFault.NO_ANSWER),
        ]
    )
    data = mbap(pdu=bytes([0x2B, 0])) + read_frame(transaction=2)

    await serve(server=make_server(link=link, recorder=recorder), data=data)

    assert [(r.operation, r.answer, r.fault) for r in recorder.requests] == [
        (Operation.OTHER, Answer.EXCEPTION, None),
        (Operation.READ, Answer.NO_ANSWER, LinkFault.NO_ANSWER),
    ]


async def test_another_units_request_is_recorded_as_ignored_without_asking_the_link():
    recorder = FakeRecorder()
    link = FakeLink()

    await serve(
        server=make_server(link=link, recorder=recorder),
        data=mbap(pdu=read_pdu(start=0, count=1), unit=9),
    )

    assert link.requests == []
    record = recorder.requests[0]
    assert (record.answer, record.unit_id, record.fault) == (Answer.IGNORED, 9, None)


async def test_going_offline_stops_listening_and_closes_every_connection(
    fake_listener,
):
    link = FakeLink()
    recorder = FakeRecorder()
    server = make_server(link=link, recorder=recorder)
    await server.start()
    reader = asyncio.StreamReader()
    writer = FakeWriter()
    client = asyncio.create_task(server._serve_client(reader, writer))
    await asyncio.sleep(0)

    link.offline = True
    await server.sync_with_link()
    reader.feed_eof()
    await client

    assert fake_listener["server"].closed
    assert writer.closed
    assert (recorder.connections[-1].event, recorder.connections[-1].reason) == (
        ConnectionEvent.CLOSED_BY_MODULE,
        ConnectionReason.LINK_FAULT,
    )
    await server.sync_with_link()
    assert len(fake_listener["starts"]) == 1
    assert server.bound_port == 5000
    await server.close()


async def test_coming_back_online_listens_again_on_the_same_port(fake_listener):
    link = FakeLink()
    server = make_server(link=link, port=0, host="10.0.0.1")
    await server.start()
    link.offline = True
    await server.sync_with_link()

    link.offline = False
    await server.sync_with_link()
    await server.sync_with_link()

    assert fake_listener["starts"] == [("10.0.0.1", 0), ("10.0.0.1", 5000)]
    assert not fake_listener["server"].closed
    await server.close()


async def test_nothing_is_started_by_syncing_before_the_server_was_started(
    fake_listener,
):
    server = make_server(link=FakeLink())

    await server.sync_with_link()

    assert fake_listener["starts"] == []


async def test_dropping_connections_now_closes_them_once_and_listening_continues(
    fake_listener,
):
    link = FakeLink()
    server = make_server(link=link)
    await server.start()
    reader = asyncio.StreamReader()
    writer = FakeWriter()
    client = asyncio.create_task(server._serve_client(reader, writer))
    await asyncio.sleep(0)

    link.drop_generation += 1
    await server.sync_with_link()
    reader.feed_eof()
    await client

    assert writer.closed
    assert not fake_listener["server"].closed
    later = FakeWriter()
    await server.sync_with_link()
    assert not later.closed
    await server.close()


async def test_a_started_server_follows_the_link_without_being_asked(fake_listener):
    link = FakeLink()
    fake_time = FakeTime()
    server = make_server(link=link, fake_time=fake_time)
    await server.start()

    link.offline = True
    for _ in range(3):
        await asyncio.sleep(0)

    assert fake_listener["server"].closed
    assert fake_time.sleeps[0] == 0.5
    await server.close()
