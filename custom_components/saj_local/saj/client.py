from __future__ import annotations

import asyncio
import logging
import struct
import time
from collections import deque
from contextlib import suppress
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Protocol

from .budget import RequestBudget

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

_LOGGER = logging.getLogger(__name__)

MBAP_HEADER_SIZE = 7
PROTOCOL_IDENTIFIER = 0
READ_HOLDING_REGISTERS = 0x03
READ_EXCEPTION_FUNCTION = 0x83
MAX_READ_REGISTERS = 125
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
    CONNECTION_CLOSED = "Connection closed by the device"


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


class RegisterReader(Protocol):
    async def read_holding_registers(
        self, address: int, count: int
    ) -> tuple[int, ...]: ...


type Connector = Callable[
    [str, int], Awaitable[tuple[asyncio.StreamReader, asyncio.StreamWriter]]
]


@dataclass(frozen=True)
class ClientEnvironment:
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
        timeout: float = 5,
        environment: ClientEnvironment | None = None,
    ) -> None:
        self.host = host
        self.port = port
        self.unit_id = unit_id
        self.timeout = timeout
        self._environment = ClientEnvironment() if environment is None else environment
        self._retired: deque[int] = deque(maxlen=LATE_FRAME_MEMORY)
        self.late_frames_discarded = 0
        self._has_read = False
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
        self._has_read = False
        self._retired.clear()

    async def read_holding_registers(self, address: int, count: int) -> tuple[int, ...]:
        if (
            not 1 <= count <= MAX_READ_REGISTERS
            or not 0 <= address <= MAX_REGISTER_ADDRESS
            or address + count - 1 > MAX_REGISTER_ADDRESS
        ):
            raise ModbusError(ModbusErrorMessage.INVALID_RANGE)
        async with self._lock:
            await self.connect()
            if self._reader is None or self._writer is None:
                raise ModbusError(ModbusErrorMessage.CONNECTION_UNAVAILABLE)
            self._transaction = (self._transaction + 1) & TRANSACTION_ID_MASK
            transaction = self._transaction
            try:
                await self._await_budget()
                if self._has_read:
                    await self._environment.sleep(REQUEST_PAUSE)
                await self._discard_unsolicited(reader=self._reader)
                result = await asyncio.wait_for(
                    self._exchange(
                        address=address,
                        count=count,
                        transaction=transaction,
                        reader=self._reader,
                        writer=self._writer,
                    ),
                    timeout=self.timeout,
                )
            except TimeoutError as err:
                await self.close()
                raise ModbusError(ModbusErrorMessage.REQUEST_TIMEOUT) from err
            except (asyncio.IncompleteReadError, OSError) as err:
                peer_closed = self._peer_closed(error=err)
                await self.close()
                raise ModbusError(
                    ModbusErrorMessage.INCOMPLETE_RESPONSE, peer_closed=peer_closed
                ) from err
            except ModbusError as err:
                if err.exception_code is None:
                    await self.close()
                else:
                    self._answered(transaction=transaction)
                raise
            except asyncio.CancelledError:
                await self.close()
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
        self._has_read = True
        self._retired.append(transaction)

    def _peer_closed(self, *, error: BaseException) -> bool:
        ended = isinstance(error, ConnectionResetError | BrokenPipeError) or (
            isinstance(error, asyncio.IncompleteReadError) and not error.partial
        )
        return ended and self._has_read

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

    async def _exchange(
        self,
        *,
        address: int,
        count: int,
        transaction: int,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> tuple[int, ...]:
        pdu = struct.pack(">BHH", READ_HOLDING_REGISTERS, address, count)
        request = (
            struct.pack(
                ">HHHB", transaction, PROTOCOL_IDENTIFIER, len(pdu) + 1, self.unit_id
            )
            + pdu
        )
        writer.write(request)
        await writer.drain()
        body = await self._outstanding_body(reader=reader, transaction=transaction)
        function = body[0]
        if function == READ_EXCEPTION_FUNCTION and len(body) == EXCEPTION_BODY_LENGTH:
            raise ModbusError(
                ModbusErrorMessage.EXCEPTION_RESPONSE, exception_code=body[1]
            )
        expected_bytes = count * REGISTER_WORD_SIZE
        if (
            function != READ_HOLDING_REGISTERS
            or len(body) != expected_bytes + 2
            or body[1] != expected_bytes
        ):
            raise ModbusError(ModbusErrorMessage.MALFORMED_REGISTERS)
        return struct.unpack(f">{count}H", body[2:])

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
            _LOGGER.debug("Discarded a late frame for an earlier request")

    def is_connected(self) -> bool:
        return self._writer is not None and not self._writer.is_closing()

    async def close(self) -> None:
        writer, self._writer = self._writer, None
        self._reader = None
        self._has_read = False
        self._retired.clear()
        if writer is None:
            return
        writer.close()
        with suppress(TimeoutError, OSError):
            await asyncio.wait_for(writer.wait_closed(), timeout=self.timeout)
