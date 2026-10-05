import asyncio
import struct
from types import SimpleNamespace

import pytest

from saj_modbus_mock.exceptions import ExceptionCode, ModbusError
from saj_modbus_mock.transport import ModbusServer, ServerSettings, respond

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
    def __init__(self, *, close_error=None):
        self.frames = []
        self.closed = False
        self.close_error = close_error

    def write(self, data):
        self.frames.append(data)

    async def drain(self):
        return None

    def close(self):
        self.closed = True

    async def wait_closed(self):
        if self.close_error:
            raise self.close_error


def mbap(*, pdu, transaction=1, protocol=0, unit=1, length=None):
    length = len(pdu) + 1 if length is None else length
    return struct.pack(">HHHB", transaction, protocol, length, unit) + pdu


def make_server(*, bank=None, **overrides):
    settings = {
        "unit_id": 1,
        "max_clients": 2,
        "response_delay_s": 0.0,
        "host": "127.0.0.1",
        "port": 0,
    }
    settings.update(overrides)
    return ModbusServer(bank=bank or MemoryBank(), settings=ServerSettings(**settings))


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


async def test_replies_wait_for_the_configured_delay(monkeypatch):
    delays = []

    async def sleep(seconds):
        delays.append(seconds)

    monkeypatch.setattr(asyncio, "sleep", sleep)

    writer = await serve(
        server=make_server(response_delay_s=0.25),
        data=mbap(pdu=read_pdu(start=0, count=1)),
    )

    assert delays == [0.25]
    assert len(writer.frames) == 1


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
    created = {}

    async def start_server(handler, *, host, port):
        created.update(handler=handler, host=host, port=port)
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
