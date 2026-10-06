from __future__ import annotations

import asyncio
import struct
from contextlib import suppress
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

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


class ModbusError(Exception):
    def __init__(self, message: str, *, exception_code: int | None = None) -> None:
        super().__init__(message)
        self.exception_code = exception_code


class ModbusTcpClient:
    def __init__(
        self,
        host: str,
        port: int,
        unit_id: int,
        *,
        timeout: float = 5,
        connector: Callable[
            [str, int], Awaitable[tuple[asyncio.StreamReader, asyncio.StreamWriter]]
        ] = asyncio.open_connection,
    ) -> None:
        self.host = host
        self.port = port
        self.unit_id = unit_id
        self.timeout = timeout
        self._connector = connector
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
                self._connector(self.host, self.port), timeout=self.timeout
            )
        except TimeoutError as err:
            raise ModbusError(ModbusErrorMessage.CONNECTION_TIMEOUT) from err
        except OSError as err:
            raise ModbusError(ModbusErrorMessage.CONNECTION_FAILED) from err

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
                if self._has_read:
                    await asyncio.sleep(REQUEST_PAUSE)
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
                await self.close()
                raise ModbusError(ModbusErrorMessage.INCOMPLETE_RESPONSE) from err
            except ModbusError, asyncio.CancelledError:
                await self.close()
                raise
            else:
                self._has_read = True
                return result

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
        header = await reader.readexactly(MBAP_HEADER_SIZE)
        response_transaction, protocol, length, unit = struct.unpack(">HHHB", header)
        if (
            response_transaction != transaction
            or protocol != PROTOCOL_IDENTIFIER
            or unit != self.unit_id
        ):
            raise ModbusError(ModbusErrorMessage.MISMATCHED_HEADER)
        if not MIN_RESPONSE_LENGTH <= length <= MAX_RESPONSE_LENGTH:
            raise ModbusError(ModbusErrorMessage.MALFORMED_LENGTH)
        body = await reader.readexactly(length - 1)
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

    def is_connected(self) -> bool:
        return self._writer is not None and not self._writer.is_closing()

    async def close(self) -> None:
        writer, self._writer = self._writer, None
        self._reader = None
        self._has_read = False
        if writer is None:
            return
        writer.close()
        with suppress(OSError):
            await writer.wait_closed()
