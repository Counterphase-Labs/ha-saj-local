import asyncio
import struct

import pytest

import saj.client as client_module
from saj.client import (
    ModbusError,
    ModbusErrorMessage,
    ModbusTcpClient,
)


class FakeWriter:
    def __init__(self, *, drain_error: Exception | None = None) -> None:
        self.data = b""
        self.closed = False
        self.drain_error = drain_error

    def write(self, data: bytes) -> None:
        self.data += data

    async def drain(self) -> None:
        if self.drain_error is not None:
            raise self.drain_error

    def close(self) -> None:
        self.closed = True

    async def wait_closed(self) -> None:
        return

    def is_closing(self) -> bool:
        return self.closed


def _endpoint(
    body: bytes,
    *,
    transaction: int = 1,
    protocol: int = 0,
    unit_id: int = 1,
    length: int | None = None,
) -> asyncio.StreamReader:
    reader = asyncio.StreamReader()
    reader.feed_data(
        struct.pack(
            ">HHHB",
            transaction,
            protocol,
            length if length is not None else len(body) + 1,
            unit_id,
        )
        + body
    )
    reader.feed_eof()
    return reader


def _client(
    reader: asyncio.StreamReader, writer: FakeWriter, *, timeout: float = 0.1
) -> ModbusTcpClient:
    async def connector(
        _host: str, _port: int
    ) -> tuple[asyncio.StreamReader, FakeWriter]:
        return reader, writer

    return ModbusTcpClient("inverter", 502, 1, timeout=timeout, connector=connector)


async def test_read_sends_one_holding_register_request_and_decodes_words():
    reader = _endpoint(bytes.fromhex("0304 1234 abcd"))
    writer = FakeWriter()
    client = _client(reader, writer)

    assert await client.read_holding_registers(0x4004, 2) == (0x1234, 0xABCD)
    assert writer.data == bytes.fromhex("0001 0000 0006 01 03 4004 0002")
    assert client.is_connected()
    await client.close()
    assert not client.is_connected()


async def test_connect_reuses_an_open_connection():
    reader = _endpoint(bytes.fromhex("0302 0001"))
    writer = FakeWriter()
    client = _client(reader, writer)

    await client.connect()
    await client.connect()

    assert client.is_connected()


@pytest.mark.parametrize(
    ("address", "count"), [(0x10000, 1), (0, 0), (0, 126), (0xFFFF, 2)]
)
async def test_read_rejects_invalid_register_ranges(address: int, count: int):
    client = ModbusTcpClient("host", 502, 1)

    with pytest.raises(ModbusError, match="Invalid register range"):
        await client.read_holding_registers(address, count)


@pytest.mark.parametrize(
    ("connector_error", "expected"),
    [
        (TimeoutError(), ModbusErrorMessage.CONNECTION_TIMEOUT),
        (OSError(), ModbusErrorMessage.CONNECTION_FAILED),
    ],
)
async def test_connect_wraps_timeout_and_socket_errors(
    connector_error: Exception, expected: str
):
    async def connector(_host: str, _port: int):
        raise connector_error

    client = ModbusTcpClient("host", 502, 1, connector=connector)
    with pytest.raises(ModbusError, match=expected):
        await client.connect()


@pytest.mark.parametrize(
    ("body", "header"),
    [
        (bytes.fromhex("0304 1234 abcd"), {"transaction": 2}),
        (bytes.fromhex("0304 1234 abcd"), {"protocol": 1}),
        (bytes.fromhex("0304 1234 abcd"), {"unit_id": 2}),
        (bytes.fromhex("0304 1234 abcd"), {"length": 254}),
        (bytes.fromhex("8302"), {}),
        (bytes.fromhex("0302 1234"), {}),
    ],
)
async def test_read_rejects_invalid_protocol_responses(
    body: bytes, header: dict[str, int]
):
    reader = _endpoint(body, **header)
    writer = FakeWriter()
    client = _client(reader, writer)

    with pytest.raises(ModbusError):
        await client.read_holding_registers(0x4004, 2)
    assert writer.closed


async def test_read_preserves_modbus_exception_code():
    client = _client(_endpoint(bytes.fromhex("8306")), FakeWriter())

    with pytest.raises(ModbusError) as error:
        await client.read_holding_registers(0x4004, 1)

    assert error.value.exception_code == 6


async def test_read_closes_connection_after_partial_response():
    reader = asyncio.StreamReader()
    reader.feed_data(struct.pack(">HHHB", 1, 0, 5, 1) + b"\x03")
    reader.feed_eof()
    writer = FakeWriter()
    client = _client(reader, writer)

    with pytest.raises(ModbusError, match="Incomplete Modbus response"):
        await client.read_holding_registers(0x4004, 1)
    assert writer.closed


async def test_read_closes_connection_after_timeout():
    reader = _endpoint(bytes.fromhex("0302 0001"))
    writer = FakeWriter()
    client = _client(reader, writer)
    original_wait_for = asyncio.wait_for
    wait_count = 0

    async def timeout_exchange(awaitable, **options):
        nonlocal wait_count
        wait_count += 1
        if wait_count == 2:
            awaitable.close()
            raise TimeoutError
        return await original_wait_for(awaitable, **options)

    client_module.asyncio.wait_for = timeout_exchange

    try:
        with pytest.raises(ModbusError, match="Modbus request timed out"):
            await client.read_holding_registers(0x4004, 1)
    finally:
        client_module.asyncio.wait_for = original_wait_for
    assert writer.closed


async def test_read_closes_connection_when_cancelled():
    reader = asyncio.StreamReader()
    writer = FakeWriter()
    client = _client(reader, writer, timeout=1)
    task = asyncio.create_task(client.read_holding_registers(0x4004, 1))
    await asyncio.sleep(0)
    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task
    assert writer.closed


async def test_read_wraps_writer_os_error_and_closes():
    writer = FakeWriter(drain_error=OSError())
    client = _client(_endpoint(bytes.fromhex("0302 0001")), writer)

    with pytest.raises(ModbusError, match="Incomplete Modbus response"):
        await client.read_holding_registers(0x4004, 1)
    assert writer.closed


async def test_read_fails_if_connect_returns_without_streams():
    client = ModbusTcpClient("host", 502, 1)

    async def connect_without_streams() -> None:
        return

    client.connect = connect_without_streams
    with pytest.raises(ModbusError, match="Connection is unavailable"):
        await client.read_holding_registers(0x4004, 1)


async def test_close_suppresses_writer_close_error():
    class CloseErrorWriter(FakeWriter):
        async def wait_closed(self) -> None:
            raise OSError

    writer = CloseErrorWriter()
    client = _client(_endpoint(bytes.fromhex("0302 0001")), writer)
    await client.connect()

    await client.close()
    assert writer.closed


async def test_close_without_connection_is_safe():
    client = ModbusTcpClient("host", 502, 1)

    await client.close()


async def test_consecutive_reads_are_paced_without_waiting_in_the_test(monkeypatch):
    reader = asyncio.StreamReader()
    for transaction, value in ((1, 20), (2, 30)):
        reader.feed_data(struct.pack(">HHHBBB H", transaction, 0, 5, 1, 3, 2, value))
    reader.feed_eof()
    writer = FakeWriter()
    client = _client(reader=reader, writer=writer)
    pauses = []

    async def pause(seconds):
        pauses.append((seconds, len(writer.data)))

    monkeypatch.setattr(client_module.asyncio, "sleep", pause)
    assert await client.read_holding_registers(address=0x8F00, count=1) == (20,)
    assert pauses == []
    assert await client.read_holding_registers(address=0x8F01, count=1) == (30,)
    assert len(pauses) == 1
    assert pauses[0][0] > 0
    assert pauses[0][1] == len(writer.data) // 2
    await client.close()
