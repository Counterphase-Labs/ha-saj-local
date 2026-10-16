import asyncio
import contextlib
import dataclasses
import itertools
import socket
import struct
import time
from typing import TYPE_CHECKING, Protocol

from .exceptions import ExceptionCode, ModbusError
from .link import (
    Action,
    ConnectionDecision,
    LinkFault,
    RequestDecision,
)
from .traffic import (
    Answer,
    Client,
    ConnectionEvent,
    ConnectionReason,
    ConnectionRecord,
    Operation,
    RequestRecord,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

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
MILLISECONDS_PER_SECOND = 1000
LINK_POLL_INTERVAL_S = 0.5
UNKNOWN_CLIENT = Client(address="unknown", port=0)
SPAN_BYTES = 4


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


def _exception_response(*, function: int, code: int) -> bytes:
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


_OPERATIONS = {
    READ_HOLDING_REGISTERS: Operation.READ,
    WRITE_SINGLE_REGISTER: Operation.WRITE,
    WRITE_MULTIPLE_REGISTERS: Operation.WRITE,
}
_REFUSAL_REASONS = {
    LinkFault.OFFLINE: ConnectionReason.OFFLINE,
    LinkFault.LOCKOUT: ConnectionReason.LOCKOUT,
}


class LinkPolicy(Protocol):
    @property
    def drop_generation(self) -> int: ...

    def is_offline(self, *, now: float) -> bool: ...

    def decide_connection(self, *, client: str, now: float) -> ConnectionDecision: ...

    def decide_request(
        self,
        *,
        client: str,
        sequence: int,
        start: int,
        count: int,
        now: float,
    ) -> RequestDecision: ...


class TrafficSink(Protocol):
    def record_connection(self, *, record: ConnectionRecord) -> None: ...

    def record_request(self, *, record: RequestRecord) -> None: ...


def _request_span(*, function: int, body: bytes) -> tuple[int, int]:
    if function not in _OPERATIONS or len(body) < SPAN_BYTES:
        return 0, 0
    start, second = struct.unpack(">HH", body[:SPAN_BYTES])
    return start, 1 if function == WRITE_SINGLE_REGISTER else second


def _transferred_words(
    *, function: int, body: bytes, response: bytes
) -> tuple[int, ...]:
    if function == READ_HOLDING_REGISTERS:
        data = response[2:]
    elif function == WRITE_SINGLE_REGISTER:
        data = body[2:]
    else:
        data = body[5:]
    return struct.unpack(f">{len(data) // BYTES_PER_REGISTER}H", data)


def _peer(*, writer: asyncio.StreamWriter) -> Client:
    peername = writer.get_extra_info("peername")
    if not peername:
        return UNKNOWN_CLIENT
    return Client(address=str(peername[0]), port=int(peername[1]))


@dataclasses.dataclass(frozen=True, slots=True)
class ServerSettings:
    unit_id: int
    max_clients: int
    host: str | None
    port: int


@dataclasses.dataclass(eq=False, slots=True)
class _Connection:
    number: int
    client: Client
    writer: asyncio.StreamWriter
    closed_by_module: ConnectionReason | None = None
    pending_duplicate: bytes | None = None


@dataclasses.dataclass(slots=True)
class _Exchange:
    connection: _Connection
    transaction_id: int
    unit_id: int
    pdu: bytes
    sequence: int
    received_at: float
    answer: Answer = Answer.ANSWERED
    decision: RequestDecision | None = None
    response: bytes | None = None


@dataclasses.dataclass(frozen=True, slots=True)
class Timing:
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep
    clock: Callable[[], float] = time.time


class ModbusServer:
    def __init__(
        self,
        *,
        bank: RegisterBank,
        settings: ServerSettings,
        link: LinkPolicy,
        recorder: TrafficSink,
        timing: Timing | None = None,
    ) -> None:
        timing = timing or Timing()
        self._bank = bank
        self._unit_id = settings.unit_id
        self._max_clients = settings.max_clients
        self._host = settings.host
        self._port = settings.port
        self._link = link
        self._recorder = recorder
        self._sleep = timing.sleep
        self._clock = timing.clock
        self._listener: asyncio.Server | None = None
        self._bound_port: int | None = None
        self._watcher: asyncio.Task[None] | None = None
        self._connections: set[_Connection] = set()
        self._connection_numbers = itertools.count(1)
        self._request_numbers = itertools.count(1)
        self._seen_drops = link.drop_generation

    @property
    def bound_port(self) -> int:
        if self._bound_port is None:
            message = "server is not started"
            raise RuntimeError(message)
        return self._bound_port

    async def start(self) -> None:
        await self._listen()
        self._watcher = asyncio.create_task(self._watch_link())

    async def close(self) -> None:
        if self._watcher is not None:
            self._watcher.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._watcher
            self._watcher = None
        listener, self._listener = self._listener, None
        if listener is None:
            return
        listener.close()
        for connection in list(self._connections):
            connection.writer.close()
        await listener.wait_closed()

    async def sync_with_link(self) -> None:
        if self._link.drop_generation != self._seen_drops:
            self._seen_drops = self._link.drop_generation
            self._close_connections()
        offline = self._link.is_offline(now=self._clock())
        if offline and self._listener is not None:
            await self._stop_listening(listener=self._listener)
        elif not offline and self._listener is None and self._bound_port is not None:
            await self._listen()

    async def _watch_link(self) -> None:
        while True:
            await self._sleep(LINK_POLL_INTERVAL_S)
            await self.sync_with_link()

    async def _listen(self) -> None:
        listener = await asyncio.start_server(
            self._serve_client,
            host=self._host,
            port=self._port if self._bound_port is None else self._bound_port,
        )
        # With port 0 each address family gets its own port; report the IPv4 one.
        ipv4_first = sorted(
            listener.sockets,
            key=lambda sock: sock.family != socket.AF_INET,
        )
        self._bound_port = int(ipv4_first[0].getsockname()[1])
        self._listener = listener

    async def _stop_listening(self, *, listener: asyncio.Server) -> None:
        self._listener = None
        listener.close()
        self._close_connections()
        await listener.wait_closed()

    def _close_connections(self) -> None:
        for connection in list(self._connections):
            connection.closed_by_module = ConnectionReason.LINK_FAULT
            connection.writer.close()

    def _report_connection(
        self,
        *,
        connection: _Connection,
        event: ConnectionEvent,
        reason: ConnectionReason | None = None,
    ) -> None:
        self._recorder.record_connection(
            record=ConnectionRecord(
                at=self._clock(),
                client=connection.client,
                connection=connection.number,
                event=event,
                reason=reason,
            )
        )

    def _refusal(self, *, client: Client) -> ConnectionReason | None:
        decision = self._link.decide_connection(
            client=client.address, now=self._clock()
        )
        if decision.fault is not None:
            return _REFUSAL_REASONS[decision.fault]
        if len(self._connections) >= self._max_clients:
            return ConnectionReason.CLIENT_LIMIT
        return None

    async def _serve_client(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        connection = _Connection(
            number=next(self._connection_numbers),
            client=_peer(writer=writer),
            writer=writer,
        )
        refusal = self._refusal(client=connection.client)
        if refusal is not None:
            self._report_connection(
                connection=connection,
                event=ConnectionEvent.REFUSED,
                reason=refusal,
            )
            writer.close()
            return
        self._connections.add(connection)
        self._report_connection(connection=connection, event=ConnectionEvent.OPENED)
        try:
            await self._serve_requests(reader=reader, connection=connection)
        except asyncio.IncompleteReadError, ConnectionError:
            pass
        except MalformedFrameError:
            connection.closed_by_module = ConnectionReason.MALFORMED_FRAME
        finally:
            self._connections.discard(connection)
            writer.close()
            self._report_close(connection=connection)
            with contextlib.suppress(ConnectionError):
                await writer.wait_closed()

    def _report_close(self, *, connection: _Connection) -> None:
        if connection.closed_by_module is None:
            self._report_connection(
                connection=connection, event=ConnectionEvent.CLOSED_BY_CLIENT
            )
        else:
            self._report_connection(
                connection=connection,
                event=ConnectionEvent.CLOSED_BY_MODULE,
                reason=connection.closed_by_module,
            )

    async def _serve_requests(
        self,
        *,
        reader: asyncio.StreamReader,
        connection: _Connection,
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
            exchange = _Exchange(
                connection=connection,
                transaction_id=transaction_id,
                unit_id=unit_id,
                pdu=pdu,
                sequence=next(self._request_numbers),
                received_at=self._clock(),
            )
            if not await self._handle(exchange=exchange):
                return

    async def _handle(self, *, exchange: _Exchange) -> bool:
        if exchange.unit_id != self._unit_id:
            exchange.answer = Answer.IGNORED
            self._report_request(exchange=exchange)
            return True
        function, body = exchange.pdu[0], exchange.pdu[1:]
        start, count = _request_span(function=function, body=body)
        decision = self._link.decide_request(
            client=exchange.connection.client.address,
            sequence=exchange.sequence,
            start=start,
            count=count,
            now=exchange.received_at,
        )
        exchange.decision = decision
        if decision.action is Action.DROP:
            exchange.answer = Answer.DROPPED
            exchange.connection.closed_by_module = (
                ConnectionReason.LOCKOUT
                if decision.fault is LinkFault.LOCKOUT
                else ConnectionReason.LINK_FAULT
            )
            self._report_request(exchange=exchange)
            return False
        if decision.action is Action.NO_ANSWER:
            exchange.answer = Answer.NO_ANSWER
        else:
            response = (
                _exception_response(function=function, code=decision.exception_code)
                if decision.action is Action.EXCEPTION
                else respond(bank=self._bank, function=function, body=body)
            )
            exchange.response = response
            await self._send(exchange=exchange, decision=decision, response=response)
        self._report_request(exchange=exchange)
        return True

    async def _send(
        self, *, exchange: _Exchange, decision: RequestDecision, response: bytes
    ) -> None:
        if decision.delay_s > 0:
            await self._sleep(decision.delay_s)
        connection = exchange.connection
        frame = _frame(
            transaction_id=exchange.transaction_id,
            unit_id=exchange.unit_id,
            pdu=response,
        )
        if connection.pending_duplicate is not None:
            connection.writer.write(connection.pending_duplicate)
            connection.pending_duplicate = None
        connection.writer.write(frame)
        await connection.writer.drain()
        if response[0] & EXCEPTION_FLAG:
            exchange.answer = Answer.EXCEPTION
            if decision.late_duplicate:
                connection.pending_duplicate = frame

    def _report_request(self, *, exchange: _Exchange) -> None:
        function = exchange.pdu[0]
        body = exchange.pdu[1:]
        start, count = _request_span(function=function, body=body)
        response = exchange.response
        decision = exchange.decision
        exception_code = None
        words: tuple[int, ...] = ()
        if response is not None and exchange.answer is Answer.EXCEPTION:
            exception_code = response[1]
        elif response is not None:
            words = _transferred_words(function=function, body=body, response=response)
        self._recorder.record_request(
            record=RequestRecord(
                at=exchange.received_at,
                client=exchange.connection.client,
                connection=exchange.connection.number,
                transaction_id=exchange.transaction_id,
                unit_id=exchange.unit_id,
                function=function,
                start=start,
                count=count,
                operation=_OPERATIONS.get(function, Operation.OTHER),
                answer=exchange.answer,
                exception_code=exception_code,
                fault=decision.fault if decision else None,
                late_duplicate=bool(
                    decision
                    and decision.late_duplicate
                    and exchange.answer is Answer.EXCEPTION
                ),
                duration_ms=(self._clock() - exchange.received_at)
                * MILLISECONDS_PER_SECOND,
                words=words,
            )
        )
