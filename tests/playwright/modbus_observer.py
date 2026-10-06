import asyncio
import json
from dataclasses import dataclass
from socket import gethostbyname, gethostname

BACKEND_HOST = "modbus-mock"
BACKEND_PORT = 502
MODBUS_PORT = 502
ALTERNATE_MODBUS_PORT = 5022
HTTP_PORT = 8000


class RequestCounter:
    value = 0


@dataclass
class ObserverControls:
    serial: str | None = None


counter = RequestCounter()
controls = ObserverControls()


async def _read_frame(reader: asyncio.StreamReader) -> bytes:
    header = await reader.readexactly(7)
    remaining = int.from_bytes(header[4:6], "big") - 1
    if remaining < 1:
        message = "Invalid Modbus frame length"
        raise ValueError(message)
    return header + await reader.readexactly(remaining)


async def _proxy(
    client_reader: asyncio.StreamReader, client_writer: asyncio.StreamWriter
) -> None:
    upstream_writer: asyncio.StreamWriter | None = None
    try:
        upstream_reader, upstream_writer = await asyncio.open_connection(
            BACKEND_HOST, BACKEND_PORT
        )
        while True:
            request = await _read_frame(client_reader)
            if request[7] == 0x03:
                counter.value += 1
            upstream_writer.write(request)
            await upstream_writer.drain()
            response = await _read_frame(upstream_reader)
            address = int.from_bytes(request[8:10], "big")
            register_count = int.from_bytes(request[10:12], "big")
            if address == 0x8F03 and register_count == 10 and controls.serial:
                encoded_serial = controls.serial.encode("ascii")[:20].ljust(20, b"\x00")
                response = response[:9] + encoded_serial
            client_writer.write(response)
            await client_writer.drain()
    except asyncio.IncompleteReadError, ConnectionError, ValueError:
        pass
    finally:
        if upstream_writer is not None:
            upstream_writer.close()
            await upstream_writer.wait_closed()
        client_writer.close()
        await client_writer.wait_closed()


async def _stats(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    try:
        await reader.readline()
        while await reader.readline() not in (b"\r\n", b"\n", b""):
            pass
        body = json.dumps({"read_requests": counter.value}).encode()
        writer.write(
            b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
            + f"Content-Length: {len(body)}\r\nConnection: close\r\n\r\n".encode()
            + body
        )
        await writer.drain()
    finally:
        writer.close()
        await writer.wait_closed()


async def _control(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    try:
        request_line = await reader.readline()
        headers: dict[str, str] = {}
        while line := await reader.readline():
            if line in (b"\r\n", b"\n"):
                break
            name, _, value = line.decode().partition(":")
            headers[name.casefold()] = value.strip()
        method, _, _path = request_line.decode().partition(" ")
        if method == "POST":
            length = int(headers.get("content-length", "0"))
            body = json.loads(await reader.readexactly(length)) if length else {}
            serial = body.get("serial")
            controls.serial = str(serial) if serial else None
        body = json.dumps({"serial": controls.serial}).encode()
        writer.write(
            b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
            + f"Content-Length: {len(body)}\r\nConnection: close\r\n\r\n".encode()
            + body
        )
        await writer.drain()
    finally:
        writer.close()
        await writer.wait_closed()


async def main() -> None:
    host = gethostbyname(gethostname())
    modbus_server = await asyncio.start_server(_proxy, host, MODBUS_PORT)
    alternate_modbus_server = await asyncio.start_server(
        _proxy, host, ALTERNATE_MODBUS_PORT
    )
    http_server = await asyncio.start_server(_stats, host, HTTP_PORT)
    control_server = await asyncio.start_server(_control, host, HTTP_PORT + 1)
    async with modbus_server, alternate_modbus_server, http_server, control_server:
        await asyncio.gather(
            modbus_server.serve_forever(),
            alternate_modbus_server.serve_forever(),
            http_server.serve_forever(),
            control_server.serve_forever(),
        )


if __name__ == "__main__":
    asyncio.run(main())
