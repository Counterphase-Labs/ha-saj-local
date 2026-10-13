from __future__ import annotations

import asyncio
import logging
import struct
import time
from collections import deque
from contextlib import contextmanager, suppress
from dataclasses import dataclass, field
from enum import StrEnum
from functools import partial
from typing import TYPE_CHECKING, Protocol

from .budget import RequestBudget
from .log import LabelledLogger
from .memory import FailureOutcome, RegisterMemory

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Iterator, Sequence

_LOGGER = logging.getLogger(__name__)

MBAP_HEADER_SIZE = 7
PROTOCOL_IDENTIFIER = 0
READ_HOLDING_REGISTERS = 0x03
WRITE_SINGLE_REGISTER = 0x06
WRITE_MULTIPLE_REGISTERS = 0x10
EXCEPTION_FLAG = 0x80
MAX_READ_REGISTERS = 125
MAX_WRITE_REGISTERS = 123
MAX_REGISTER_VALUE = 0xFFFF
MULTIPLE_WRITE_ACKNOWLEDGEMENT_LENGTH = 5
MAX_REGISTER_ADDRESS = 0xFFFF
TRANSACTION_ID_MASK = 0xFFFF
MIN_RESPONSE_LENGTH = 2
MAX_RESPONSE_LENGTH = 253
EXCEPTION_BODY_LENGTH = 2
REGISTER_WORD_SIZE = 2
REQUEST_PAUSE = 0.25
UNSOLICITED_CHUNK_SIZE = 4096
LATE_FRAME_MEMORY = 64
DEVICE_UNAVAILABLE_CODES = frozenset({0x04, 0x06})


class ModbusErrorMessage(StrEnum):
    CONNECTION_TIMEOUT = "Connection timed out"
    CONNECTION_FAILED = "Connection failed"
    INVALID_RANGE = "Invalid register range"
    CONNECTION_UNAVAILABLE = "Connection is unavailable"
    REQUEST_TIMEOUT = "Modbus request timed out"
    INCOMPLETE_RESPONSE = "Incomplete Modbus response"
    MISMATCHED_HEADER = "Mismatched Modbus response header"
    MALFORMED_LENGTH = "Malformed Modbus response length"
    EXCEPTION_RESPONSE = "Modbus exception response"
    MALFORMED_REGISTERS = "Malformed Modbus register response"
    MALFORMED_ACKNOWLEDGEMENT = "Malformed Modbus write acknowledgement"
    INVALID_VALUE = "Invalid register value"
    CONNECTION_CLOSED = "Connection closed by the device"


FAILURE_OUTCOMES: dict[str, FailureOutcome] = {
    ModbusErrorMessage.CONNECTION_TIMEOUT: FailureOutcome.TIMEOUT,
    ModbusErrorMessage.REQUEST_TIMEOUT: FailureOutcome.TIMEOUT,
    ModbusErrorMessage.CONNECTION_FAILED: FailureOutcome.CONNECTION_LOST,
    ModbusErrorMessage.CONNECTION_UNAVAILABLE: FailureOutcome.CONNECTION_LOST,
    ModbusErrorMessage.CONNECTION_CLOSED: FailureOutcome.CONNECTION_LOST,
    ModbusErrorMessage.INCOMPLETE_RESPONSE: FailureOutcome.CONNECTION_LOST,
    ModbusErrorMessage.MISMATCHED_HEADER: FailureOutcome.MALFORMED_REPLY,
    ModbusErrorMessage.MALFORMED_LENGTH: FailureOutcome.MALFORMED_REPLY,
    ModbusErrorMessage.MALFORMED_REGISTERS: FailureOutcome.MALFORMED_REPLY,
    ModbusErrorMessage.MALFORMED_ACKNOWLEDGEMENT: FailureOutcome.MALFORMED_REPLY,
    ModbusErrorMessage.EXCEPTION_RESPONSE: FailureOutcome.EXCEPTION,
}


class ConnectionReason(StrEnum):
    SETUP = "setup"
    RECONNECT = "reconnect after failure"
    STALE = "stale connection"
    VALIDATION = "validation"
    UNLOAD = "unload"


class ModbusError(Exception):
    def __init__(
        self,
        message: str,
        *,
        exception_code: int | None = None,
        peer_closed: bool = False,
    ) -> None:
        super().__init__(message)
        self.exception_code = exception_code
        self.peer_closed = peer_closed

    @property
    def device_unavailable(self) -> bool:
        return self.exception_code in DEVICE_UNAVAILABLE_CODES

    @property
    def failure_outcome(self) -> FailureOutcome:
        if self.exception_code is not None:
            return FailureOutcome.EXCEPTION
        return FAILURE_OUTCOMES[str(self)]


class RegisterReader(Protocol):
    async def read_holding_registers(
        self, address: int, count: int
    ) -> tuple[int, ...]: ...


class RegisterWriter(Protocol):
    async def write_single_register(self, address: int, value: int) -> None: ...

    async def write_multiple_registers(
        self, address: int, values: Sequence[int]
    ) -> None: ...


type Connector = Callable[
    [str, int], Awaitable[tuple[asyncio.StreamReader, asyncio.StreamWriter]]
]


@dataclass(frozen=True)
class ClientEnvironment:
    label: str
    first_open: ConnectionReason = ConnectionReason.SETUP
    connector: Connector = asyncio.open_connection
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep
    clock: Callable[[], float] = time.monotonic
    budget: RequestBudget = field(default_factory=RequestBudget)


class ModbusTcpClient:
    def __init__(
        self,
        host: str,
        port: int,
        unit_id: int,
        *,
        environment: ClientEnvironment,
        timeout: float = 5,
    ) -> None:
        self.host = host
        self.port = port
        self.unit_id = unit_id
        self.timeout = timeout
        self._environment = environment
        self._log = LabelledLogger(logger=_LOGGER, label=environment.label)
        self.memory = RegisterMemory(clock=environment.clock)
        self._reason = environment.first_open
        self._retired: deque[int] = deque(maxlen=LATE_FRAME_MEMORY)
        self.late_frames_discarded = 0
        self._has_answered = False
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._transaction = 0
        self._lock = asyncio.Lock()

    async def connect(self) -> None:
        if self._writer is not None and not self._writer.is_closing():
            return
        try:
            self._reader, self._writer = await asyncio.wait_for(
                self._environment.connector(self.host, self.port), timeout=self.timeout
            )
        except TimeoutError as err:
            raise ModbusError(ModbusErrorMessage.CONNECTION_TIMEOUT) from err
        except OSError as err:
            raise ModbusError(ModbusErrorMessage.CONNECTION_FAILED) from err
        self._has_answered = False
        self._retired.clear()
        self._log.debug("Connection opened (%s)", self._reason)
        self._reason = ConnectionReason.RECONNECT

    async def read_holding_registers(self, address: int, count: int) -> tuple[int, ...]:
        self._require_span(address=address, count=count, limit=MAX_READ_REGISTERS)
        pdu = struct.pack(">BHH", READ_HOLDING_REGISTERS, address, count)
        try:
            words = await self._request(
                pdu=pdu, interpret=partial(_registers_of, count=count)
            )
        except ModbusError as err:
            self.memory.record_failure(
                address=address,
                count=count,
                outcome=err.failure_outcome,
                exception_code=err.exception_code,
            )
            raise
        except asyncio.CancelledError:
            self.memory.record_failure(
                address=address, count=count, outcome=FailureOutcome.TIMEOUT
            )
            raise
        self.memory.record_answer(address=address, words=words)
        return words

    @contextmanager
    def unremembered(self) -> Iterator[None]:
        with self.memory.paused():
            yield

    async def write_single_register(self, address: int, value: int) -> None:
        self._require_span(address=address, count=1, limit=1)
        self._require_values(values=(value,))
        pdu = struct.pack(">BHH", WRITE_SINGLE_REGISTER, address, value)
        await self._request(pdu=pdu, interpret=partial(_echoes, expected=pdu))

    async def write_multiple_registers(
        self, address: int, values: Sequence[int]
    ) -> None:
        self._require_span(
            address=address, count=len(values), limit=MAX_WRITE_REGISTERS
        )
        self._require_values(values=values)
        pdu = struct.pack(
            f">BHHB{len(values)}H",
            WRITE_MULTIPLE_REGISTERS,
            address,
            len(values),
            len(values) * REGISTER_WORD_SIZE,
            *values,
        )
        await self._request(
            pdu=pdu,
            interpret=partial(
                _echoes, expected=pdu[:MULTIPLE_WRITE_ACKNOWLEDGEMENT_LENGTH]
            ),
        )

    def _require_span(self, *, address: int, count: int, limit: int) -> None:
        if (
            not 1 <= count <= limit
            or not 0 <= address <= MAX_REGISTER_ADDRESS
            or address + count - 1 > MAX_REGISTER_ADDRESS
        ):
            raise ModbusError(ModbusErrorMessage.INVALID_RANGE)

    def _require_values(self, *, values: Sequence[int]) -> None:
        if not all(0 <= value <= MAX_REGISTER_VALUE for value in values):
            raise ModbusError(ModbusErrorMessage.INVALID_VALUE)

    async def _request[Result](
        self, *, pdu: bytes, interpret: Callable[[bytes], Result]
    ) -> Result:
        async with self._lock:
            await self.connect()
            if self._reader is None or self._writer is None:
                raise ModbusError(ModbusErrorMessage.CONNECTION_UNAVAILABLE)
            self._transaction = (self._transaction + 1) & TRANSACTION_ID_MASK
            transaction = self._transaction
            try:
                await self._await_budget()
                if self._has_answered:
                    await self._environment.sleep(REQUEST_PAUSE)
                await self._discard_unsolicited(reader=self._reader)
                result = await asyncio.wait_for(
                    self._exchange(
                        pdu=pdu,
                        interpret=interpret,
                        transaction=transaction,
                        reader=self._reader,
                        writer=self._writer,
                    ),
                    timeout=self.timeout,
                )
            except TimeoutError as err:
                await self.close(reason=ConnectionReason.RECONNECT)
                raise ModbusError(ModbusErrorMessage.REQUEST_TIMEOUT) from err
            except (asyncio.IncompleteReadError, OSError) as err:
                peer_closed = self._peer_closed(error=err)
                await self.close(reason=ConnectionReason.RECONNECT)
                raise ModbusError(
                    ModbusErrorMessage.INCOMPLETE_RESPONSE, peer_closed=peer_closed
                ) from err
            except ModbusError as err:
                if err.exception_code is None:
                    await self.close(reason=ConnectionReason.RECONNECT)
                else:
                    self._answered(transaction=transaction)
                raise
            except asyncio.CancelledError:
                await self.close(reason=ConnectionReason.RECONNECT)
                raise
            else:
                self._answered(transaction=transaction)
                return result

    def worst_case_duration(self, *, requests: int) -> float:
        pace = self.timeout + REQUEST_PAUSE
        return (
            self.timeout * 2
            + requests * pace
            + self._environment.budget.worst_case_delay(requests=requests)
        )

    def _answered(self, *, transaction: int) -> None:
        self._has_answered = True
        self._retired.append(transaction)

    def _peer_closed(self, *, error: BaseException) -> bool:
        ended = isinstance(error, ConnectionResetError | BrokenPipeError) or (
            isinstance(error, asyncio.IncompleteReadError) and not error.partial
        )
        return ended and self._has_answered

    async def _await_budget(self) -> None:
        delay = self._environment.budget.delay(now=self._environment.clock())
        if delay > 0:
            await self._environment.sleep(delay)
        self._environment.budget.record(now=self._environment.clock())

    async def _discard_unsolicited(self, *, reader: asyncio.StreamReader) -> None:
        while True:
            try:
                async with asyncio.timeout(0):
                    chunk = await reader.read(UNSOLICITED_CHUNK_SIZE)
            except TimeoutError:
                return
            if not chunk:
                raise ConnectionResetError

    async def _exchange[Result](
        self,
        *,
        pdu: bytes,
        interpret: Callable[[bytes], Result],
        transaction: int,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> Result:
        request = (
            struct.pack(
                ">HHHB", transaction, PROTOCOL_IDENTIFIER, len(pdu) + 1, self.unit_id
            )
            + pdu
        )
        writer.write(request)
        await writer.drain()
        body = await self._outstanding_body(reader=reader, transaction=transaction)
        if body[0] == pdu[0] | EXCEPTION_FLAG and len(body) == EXCEPTION_BODY_LENGTH:
            raise ModbusError(
                ModbusErrorMessage.EXCEPTION_RESPONSE, exception_code=body[1]
            )
        return interpret(body)

    async def _outstanding_body(
        self, *, reader: asyncio.StreamReader, transaction: int
    ) -> bytes:
        while True:
            header = await reader.readexactly(MBAP_HEADER_SIZE)
            response_transaction, protocol, length, unit = struct.unpack(
                ">HHHB", header
            )
            if protocol != PROTOCOL_IDENTIFIER or unit != self.unit_id:
                raise ModbusError(ModbusErrorMessage.MISMATCHED_HEADER)
            if not MIN_RESPONSE_LENGTH <= length <= MAX_RESPONSE_LENGTH:
                raise ModbusError(ModbusErrorMessage.MALFORMED_LENGTH)
            body = await reader.readexactly(length - 1)
            if response_transaction == transaction:
                return body
            if response_transaction not in self._retired:
                raise ModbusError(ModbusErrorMessage.MISMATCHED_HEADER)
            self.late_frames_discarded += 1
            self._log.debug("Discarded a late frame for an earlier request")

    def is_connected(self) -> bool:
        return self._writer is not None and not self._writer.is_closing()

    async def close(self, *, reason: ConnectionReason) -> None:
        writer, self._writer = self._writer, None
        self._reader = None
        self._has_answered = False
        self._retired.clear()
        if writer is None:
            return
        self._reason = reason
        self._log.debug("Connection closed (%s)", reason)
        writer.close()
        with suppress(TimeoutError, OSError):
            await asyncio.wait_for(writer.wait_closed(), timeout=self.timeout)


def _registers_of(body: bytes, *, count: int) -> tuple[int, ...]:
    expected_bytes = count * REGISTER_WORD_SIZE
    if (
        body[0] != READ_HOLDING_REGISTERS
        or len(body) != expected_bytes + 2
        or body[1] != expected_bytes
    ):
        raise ModbusError(ModbusErrorMessage.MALFORMED_REGISTERS)
    return struct.unpack(f">{count}H", body[2:])


def _echoes(body: bytes, *, expected: bytes) -> None:
    if body != expected:
        raise ModbusError(ModbusErrorMessage.MALFORMED_ACKNOWLEDGEMENT)
