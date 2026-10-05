import asyncio
import contextlib
import dataclasses
import socket
import struct
from typing import Protocol

from .exceptions import ExceptionCode, ModbusError

MBAP_HEADER_BYTES = 7
PROTOCOL_ID = 0
MIN_LENGTH_FIELD = 2
MAX_LENGTH_FIELD = 254
EXCEPTION_FLAG = 0x80
READ_HOLDING_REGISTERS = 0x03
WRITE_SINGLE_REGISTER = 0x06
WRITE_MULTIPLE_REGISTERS = 0x10
MAX_READ_COUNT = 125
MAX_WRITE_COUNT = 123
BYTES_PER_REGISTER = 2
UNIT_ID_BYTES = 1


class RegisterBank(Protocol):
    def read(self, *, start: int, count: int) -> list[int]: ...

    def write(self, *, start: int, words: list[int]) -> None: ...


class MalformedFrameError(Exception):
    pass


def _register_bytes(*, words: list[int]) -> bytes:
    return struct.pack(f">{len(words)}H", *words)


def _read_response(*, bank: RegisterBank, body: bytes) -> bytes:
    if len(body) != struct.calcsize(">HH"):
        raise MalformedFrameError
    start, count = struct.unpack(">HH", body)
    if not 1 <= count <= MAX_READ_COUNT:
        raise ModbusError(code=ExceptionCode.ILLEGAL_DATA_VALUE)
    payload = _register_bytes(words=bank.read(start=start, count=count))
    return bytes([READ_HOLDING_REGISTERS, len(payload)]) + payload


def _write_single_response(*, bank: RegisterBank, body: bytes) -> bytes:
    if len(body) != struct.calcsize(">HH"):
        raise MalformedFrameError
    address, value = struct.unpack(">HH", body)
    bank.write(start=address, words=[value])
    return bytes([WRITE_SINGLE_REGISTER]) + body


def _write_multiple_response(*, bank: RegisterBank, body: bytes) -> bytes:
    header = struct.calcsize(">HHB")
    if len(body) < header:
        raise MalformedFrameError
    start, count, byte_count = struct.unpack(">HHB", body[:header])
    data = body[header:]
    if byte_count != len(data) or byte_count != count * BYTES_PER_REGISTER:
        raise MalformedFrameError
    if not 1 <= count <= MAX_WRITE_COUNT:
        raise ModbusError(code=ExceptionCode.ILLEGAL_DATA_VALUE)
    words = list(struct.unpack(f">{count}H", data))
    bank.write(start=start, words=words)
    return bytes([WRITE_MULTIPLE_REGISTERS]) + struct.pack(">HH", start, count)


_HANDLERS = {
    READ_HOLDING_REGISTERS: _read_response,
    WRITE_SINGLE_REGISTER: _write_single_response,
    WRITE_MULTIPLE_REGISTERS: _write_multiple_response,
}


def _exception_response(*, function: int, code: ExceptionCode) -> bytes:
    return bytes([function | EXCEPTION_FLAG, code])


def respond(*, bank: RegisterBank, function: int, body: bytes) -> bytes:
    handler = _HANDLERS.get(function)
    if handler is None:
        return _exception_response(
            function=function,
            code=ExceptionCode.ILLEGAL_FUNCTION,
        )
    try:
        return handler(bank=bank, body=body)
    except ModbusError as error:
        return _exception_response(function=function, code=error.code)


def _frame(*, transaction_id: int, unit_id: int, pdu: bytes) -> bytes:
    header = struct.pack(
        ">HHHB",
        transaction_id,
        PROTOCOL_ID,
        len(pdu) + UNIT_ID_BYTES,
        unit_id,
    )
    return header + pdu


@dataclasses.dataclass(frozen=True, slots=True)
class ServerSettings:
    unit_id: int
    max_clients: int
    response_delay_s: float
    host: str | None
    port: int


class ModbusServer:
    def __init__(self, *, bank: RegisterBank, settings: ServerSettings) -> None:
        self._bank = bank
        self._unit_id = settings.unit_id
        self._max_clients = settings.max_clients
        self._response_delay_s = settings.response_delay_s
        self._host = settings.host
        self._port = settings.port
        self._server: asyncio.Server | None = None
        self._writers: set[asyncio.StreamWriter] = set()

    @property
    def bound_port(self) -> int:
        if self._server is None:
            message = "server is not started"
            raise RuntimeError(message)
        # With port 0 each address family gets its own port; report the IPv4 one.
        ipv4_first = sorted(
            self._server.sockets,
            key=lambda sock: sock.family != socket.AF_INET,
        )
        return int(ipv4_first[0].getsockname()[1])

    async def start(self) -> None:
        self._server = await asyncio.start_server(
            self._serve_client,
            host=self._host,
            port=self._port,
        )

    async def close(self) -> None:
        if self._server is None:
            return
        self._server.close()
        for writer in list(self._writers):
            writer.close()
        await self._server.wait_closed()

    async def _serve_client(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        if len(self._writers) >= self._max_clients:
            writer.close()
            return
        self._writers.add(writer)
        try:
            await self._serve_requests(reader=reader, writer=writer)
        except asyncio.IncompleteReadError, ConnectionError, MalformedFrameError:
            pass
        finally:
            self._writers.discard(writer)
            writer.close()
            with contextlib.suppress(ConnectionError):
                await writer.wait_closed()

    async def _serve_requests(
        self,
        *,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        while True:
            header = await reader.readexactly(MBAP_HEADER_BYTES)
            transaction_id, protocol_id, length, unit_id = struct.unpack(
                ">HHHB", header
            )
            if (
                protocol_id != PROTOCOL_ID
                or not MIN_LENGTH_FIELD <= length <= MAX_LENGTH_FIELD
            ):
                raise MalformedFrameError
            pdu = await reader.readexactly(length - UNIT_ID_BYTES)
            if unit_id != self._unit_id:
                continue
            response = respond(bank=self._bank, function=pdu[0], body=pdu[1:])
            if self._response_delay_s:
                await asyncio.sleep(self._response_delay_s)
            writer.write(
                _frame(transaction_id=transaction_id, unit_id=unit_id, pdu=response),
            )
            await writer.drain()
