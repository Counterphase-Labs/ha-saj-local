import asyncio
import contextlib
import struct
from typing import TYPE_CHECKING

from .transport import MBAP_HEADER_BYTES, PROTOCOL_ID, READ_HOLDING_REGISTERS

if TYPE_CHECKING:
    from .scenario import Scenario

DEVICE_TYPE_ADDRESS = 0x8F00
LENGTH_FIELD_INDEX = 2
VALUE_OFFSET = 2
CHECK_TRANSACTION_ID = 1
CHECK_TIMEOUT_S = 3.0
LOCAL_HOST = "127.0.0.1"
RESPONSE_PDU_BYTES = 4


def _request(*, unit_id: int) -> bytes:
    pdu = struct.pack(">BHH", READ_HOLDING_REGISTERS, DEVICE_TYPE_ADDRESS, 1)
    header = struct.pack(
        ">HHHB", CHECK_TRANSACTION_ID, PROTOCOL_ID, len(pdu) + 1, unit_id
    )
    return header + pdu


async def read_device_type(*, port: int, unit_id: int) -> int:
    reader, writer = await asyncio.open_connection(LOCAL_HOST, port)
    try:
        writer.write(_request(unit_id=unit_id))
        await writer.drain()
        header = await reader.readexactly(MBAP_HEADER_BYTES)
        length = struct.unpack(">HHHB", header)[LENGTH_FIELD_INDEX]
        pdu = await reader.readexactly(length - 1)
    finally:
        writer.close()
        with contextlib.suppress(ConnectionError):
            await writer.wait_closed()
    if len(pdu) != RESPONSE_PDU_BYTES or pdu[0] != READ_HOLDING_REGISTERS:
        return -1
    return int(struct.unpack(">H", pdu[VALUE_OFFSET:])[0])


async def is_healthy(*, scenario: Scenario) -> bool:
    try:
        found = await asyncio.wait_for(
            read_device_type(
                port=scenario.server.port, unit_id=scenario.server.unit_id
            ),
            timeout=CHECK_TIMEOUT_S,
        )
    except OSError, asyncio.IncompleteReadError, TimeoutError:
        return False
    return found == scenario.device.model.device_type
