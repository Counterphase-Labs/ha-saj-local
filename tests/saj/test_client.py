import asyncio
import struct
from contextlib import suppress
from types import SimpleNamespace

import pytest

from saj.budget import RequestBudget
from saj.client import (
    REQUEST_PAUSE,
    ClientEnvironment,
    ModbusError,
    ModbusErrorMessage,
    ModbusTcpClient,
)

ANSWER = "0302 0001"


def _frame(
    body: str,
    *,
    transaction: int = 1,
    protocol: int = 0,
    unit_id: int = 1,
    length: int | None = None,
) -> bytes:
    payload = bytes.fromhex(body)
    return (
        struct.pack(
            ">HHHB",
            transaction,
            protocol,
            length if length is not None else len(payload) + 1,
            unit_id,
        )
        + payload
    )


class FakeWriter:
    def __init__(self, *, drain_error: Exception | None = None) -> None:
        self.requests: list[bytes] = []
        self.closed = False
        self.drain_error = drain_error
        self.on_write = lambda _request: None

    def write(self, data: bytes) -> None:
        self.requests.append(data)
        self.on_write(data)

    async def drain(self) -> None:
        if self.drain_error is not None:
            raise self.drain_error

    def close(self) -> None:
        self.closed = True

    async def wait_closed(self) -> None:
        return

    def is_closing(self) -> bool:
        return self.closed


class FakeDevice:
    """Answers each request written with the next scripted reply."""

    def __init__(self, *replies: bytes, eof_on_request: int | None = None) -> None:
        self.reader = asyncio.StreamReader()
        self.writer = FakeWriter()
        self.replies = list(replies)
        self.eof_on_request = eof_on_request
        self.writer.on_write = self._answer

    def _answer(self, _request: bytes) -> None:
        if self.eof_on_request == len(self.writer.requests):
            self.reader.feed_eof()
        elif self.replies:
            self.reader.feed_data(self.replies.pop(0))


class RecordingBudget:
    def __init__(self, delay: float = 0.0, events: list[str] | None = None) -> None:
        self.events = [] if events is None else events
        self._delay = delay

    def delay(self, *, now: float) -> float:
        self.events.append(f"delay@{now}")
        return self._delay

    def record(self, *, now: float) -> None:
        self.events.append(f"record@{now}")

    def worst_case_delay(self, *, requests: int) -> float:
        return requests * 100.0


def _client(
    device: FakeDevice,
    *,
    timeout: float = 1,
    budget=None,
    sleeps: list[float] | None = None,
) -> ModbusTcpClient:
    async def connector(_host: str, _port: int):
        return device.reader, device.writer

    async def sleep(seconds: float) -> None:
        if sleeps is not None:
            sleeps.append(seconds)
            device.writer.requests.append(b"")

    return ModbusTcpClient(
        "inverter",
        502,
        1,
        timeout=timeout,
        environment=ClientEnvironment(
            connector=connector,
            sleep=sleep,
            clock=lambda: 7.0,
            budget=RequestBudget() if budget is None else budget,
        ),
    )


@pytest.fixture
def exchange_stalls(monkeypatch):
    original_wait_for = asyncio.wait_for
    control = SimpleNamespace(exchanges_answered_first=0)

    async def wait_for(awaitable, **options):
        if "_exchange" not in getattr(awaitable, "__qualname__", ""):
            return await original_wait_for(awaitable, **options)
        if control.exchanges_answered_first > 0:
            control.exchanges_answered_first -= 1
            return await original_wait_for(awaitable, **options)
        task = asyncio.ensure_future(awaitable)
        for _ in range(20):
            await asyncio.sleep(0)
        assert not task.done()
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task
        raise TimeoutError

    monkeypatch.setattr(asyncio, "wait_for", wait_for)
    return control


async def test_read_sends_one_holding_register_request_and_decodes_words():
    device = FakeDevice(_frame("0304 1234 abcd"))
    client = _client(device)

    assert await client.read_holding_registers(0x4004, 2) == (0x1234, 0xABCD)
    assert device.writer.requests == [bytes.fromhex("0001 0000 0006 01 03 4004 0002")]
    assert client.is_connected()
    await client.close()
    assert not client.is_connected()


async def test_connect_reuses_an_open_connection():
    connections = []

    async def connector(_host: str, _port: int):
        connections.append(object())
        return asyncio.StreamReader(), FakeWriter()

    client = ModbusTcpClient(
        "inverter", 502, 1, environment=ClientEnvironment(connector=connector)
    )

    await client.connect()
    await client.connect()

    assert len(connections) == 1
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

    client = ModbusTcpClient(
        "host", 502, 1, environment=ClientEnvironment(connector=connector)
    )
    with pytest.raises(ModbusError, match=expected):
        await client.connect()


@pytest.mark.parametrize(
    "reply",
    [
        _frame("0304 1234 abcd", transaction=2),
        _frame("0304 1234 abcd", protocol=1),
        _frame("0304 1234 abcd", unit_id=2),
        _frame("0304 1234 abcd", length=254),
        _frame("0304 1234 abcd", length=1),
        _frame("83"),
        _frame("8302 00"),
        _frame("0302 1234"),
        _frame("0404 1234 abcd"),
        _frame("0305 1234 abcd"),
    ],
)
async def test_read_rejects_invalid_protocol_responses_and_closes(reply: bytes):
    device = FakeDevice(reply)
    client = _client(device)

    with pytest.raises(ModbusError) as caught:
        await client.read_holding_registers(0x4004, 2)

    assert caught.value.exception_code is None
    assert not caught.value.peer_closed
    assert device.writer.closed


@pytest.mark.parametrize("code", [0, 1, 2, 4, 6, 0x0B, 0x7F])
async def test_exception_response_keeps_the_connection_and_the_code(code: int):
    device = FakeDevice(_frame(f"83{code:02x}"), _frame(ANSWER, transaction=2))
    client = _client(device)

    with pytest.raises(ModbusError) as caught:
        await client.read_holding_registers(0x4004, 1)

    assert caught.value.exception_code == code
    assert not device.writer.closed
    assert client.is_connected()
    assert await client.read_holding_registers(0x4004, 1) == (1,)


@pytest.mark.parametrize(
    ("code", "unavailable"),
    [(4, True), (6, True), (0, False), (2, False), (0x7F, False), (None, False)],
)
def test_busy_and_device_failure_codes_mean_the_device_cannot_serve_requests(
    code: int | None, *, unavailable: bool
):
    error = ModbusError("failed", exception_code=code)

    assert error.device_unavailable is unavailable


async def test_a_late_frame_is_discarded_and_the_outstanding_answer_returned():
    late_duplicate = _frame("0302 beef", transaction=1)
    device = FakeDevice(
        _frame("8302"), late_duplicate + _frame("0302 0007", transaction=2)
    )
    client = _client(device)
    with pytest.raises(ModbusError):
        await client.read_holding_registers(0x4004, 1)

    assert await client.read_holding_registers(0x4005, 1) == (7,)
    assert client.late_frames_discarded == 1
    assert not device.writer.closed


async def test_a_late_frame_arriving_between_requests_is_discarded_unread():
    device = FakeDevice(_frame("8302"), _frame("0302 0007", transaction=2))
    client = _client(device)
    with pytest.raises(ModbusError):
        await client.read_holding_registers(0x4004, 1)
    device.reader.feed_data(_frame("0302 beef", transaction=1))

    assert await client.read_holding_registers(0x4005, 1) == (7,)
    assert client.late_frames_discarded == 0


async def test_a_late_frame_followed_by_silence_times_out_and_closes(exchange_stalls):
    exchange_stalls.exchanges_answered_first = 1
    device = FakeDevice(_frame("8302"), _frame("0302 beef", transaction=1))
    client = _client(device)
    with pytest.raises(ModbusError):
        await client.read_holding_registers(0x4004, 1)

    with pytest.raises(ModbusError, match="Modbus request timed out"):
        await client.read_holding_registers(0x4005, 1)

    assert client.late_frames_discarded == 1
    assert device.writer.closed


async def test_a_frame_for_a_transaction_never_issued_is_not_treated_as_late():
    device = FakeDevice(_frame(ANSWER), _frame("0302 beef", transaction=9))
    client = _client(device)
    await client.read_holding_registers(0x4004, 1)

    with pytest.raises(ModbusError, match="Mismatched Modbus response header"):
        await client.read_holding_registers(0x4005, 1)

    assert client.late_frames_discarded == 0


async def test_late_frame_memory_does_not_survive_a_reconnect():
    device = FakeDevice(_frame(ANSWER))
    client = _client(device)
    await client.read_holding_registers(0x4004, 1)
    await client.close()
    device.reader = asyncio.StreamReader()
    device.writer = FakeWriter()
    device.writer.on_write = device._answer
    device.replies = [_frame("0302 beef", transaction=1)]

    with pytest.raises(ModbusError, match="Mismatched Modbus response header"):
        await client.read_holding_registers(0x4004, 1)


@pytest.mark.parametrize(
    "stray",
    [
        _frame("0302 beef", transaction=1),
        b"\x00",
        _frame("0302 beef", transaction=1) * 3,
        b"x" * 10_000,
    ],
)
async def test_unsolicited_input_is_discarded_before_a_request_is_sent(stray: bytes):
    device = FakeDevice(_frame("0302 0007"))
    client = _client(device)
    await client.connect()
    device.reader.feed_data(stray)

    assert await client.read_holding_registers(0x4004, 1) == (7,)


@pytest.mark.parametrize(
    ("kept", "expected_peer_closed"), [(True, True), (False, False)]
)
async def test_a_connection_closed_by_the_peer_before_a_request_is_reported(
    *, kept: bool, expected_peer_closed: bool
):
    device = FakeDevice(_frame(ANSWER))
    client = _client(device)
    if kept:
        await client.read_holding_registers(0x4004, 1)
    else:
        await client.connect()
    device.reader.feed_eof()

    with pytest.raises(ModbusError) as caught:
        await client.read_holding_registers(0x4004, 1)

    assert caught.value.peer_closed is expected_peer_closed
    assert device.writer.closed


@pytest.mark.parametrize(
    ("kept", "peer_closing", "expected_peer_closed"),
    [
        (True, "eof", True),
        (False, "eof", False),
        (True, "partial", False),
        (True, "reset", True),
        (False, "reset", False),
        (True, "broken_pipe", True),
    ],
)
async def test_peer_close_is_reported_only_for_a_kept_connection_that_ended_cleanly(
    *, kept: bool, peer_closing: str, expected_peer_closed: bool
):
    device = FakeDevice(_frame(ANSWER))
    client = _client(device)
    if kept:
        await client.read_holding_registers(0x4004, 1)
    else:
        await client.connect()
    if peer_closing == "eof":
        device.writer.on_write = lambda _request: device.reader.feed_eof()
    elif peer_closing == "partial":
        device.writer.on_write = lambda _request: (
            device.reader.feed_data(b"\x00\x02\x00"),
            device.reader.feed_eof(),
        )
    else:
        device.writer.drain_error = (
            ConnectionResetError() if peer_closing == "reset" else BrokenPipeError()
        )

    with pytest.raises(ModbusError, match="Incomplete Modbus response") as caught:
        await client.read_holding_registers(0x4004, 1)

    assert caught.value.peer_closed is expected_peer_closed
    assert device.writer.closed


async def test_read_closes_connection_after_timeout(exchange_stalls):
    device = FakeDevice()
    client = _client(device)

    with pytest.raises(ModbusError, match="Modbus request timed out"):
        await client.read_holding_registers(0x4004, 1)

    assert device.writer.closed


async def test_read_closes_connection_when_cancelled():
    device = FakeDevice()
    client = _client(device)
    task = asyncio.create_task(client.read_holding_registers(0x4004, 1))
    await asyncio.sleep(0)
    await asyncio.sleep(0)
    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task
    assert device.writer.closed


async def test_read_wraps_writer_os_error_and_closes():
    device = FakeDevice(_frame(ANSWER))
    device.writer.drain_error = OSError()
    client = _client(device)

    with pytest.raises(ModbusError, match="Incomplete Modbus response"):
        await client.read_holding_registers(0x4004, 1)
    assert device.writer.closed


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

    device = FakeDevice()
    device.writer = CloseErrorWriter()
    client = _client(device)
    await client.connect()

    await client.close()
    assert device.writer.closed


async def test_close_gives_up_on_a_connection_that_never_finishes_closing():
    class StuckWriter(FakeWriter):
        async def wait_closed(self) -> None:
            await asyncio.Event().wait()

    device = FakeDevice()
    device.writer = StuckWriter()
    client = _client(device)
    await client.connect()
    client.timeout = 0

    await client.close()

    assert device.writer.closed
    assert not client.is_connected()


async def test_close_without_connection_is_safe():
    client = ModbusTcpClient("host", 502, 1)

    await client.close()


async def test_consecutive_reads_are_paced_without_waiting_in_the_test():
    device = FakeDevice(_frame("0302 0014"), _frame("0302 001e", transaction=2))
    sleeps: list[float] = []
    client = _client(device, sleeps=sleeps)

    assert await client.read_holding_registers(address=0x8F00, count=1) == (20,)
    assert sleeps == []
    assert await client.read_holding_registers(address=0x8F01, count=1) == (30,)
    assert sleeps == [REQUEST_PAUSE]


@pytest.mark.parametrize("delay", [0.0, 2.5])
async def test_the_budget_is_consulted_and_charged_before_every_request(delay: float):
    events: list[str] = []
    budget = RecordingBudget(delay=delay, events=events)
    device = FakeDevice(_frame(ANSWER))
    device.writer.on_write = lambda _request: (
        events.append("sent"),
        device.reader.feed_data(_frame(ANSWER)),
    )
    sleeps: list[float] = []
    client = _client(device, budget=budget, sleeps=sleeps)

    await client.read_holding_registers(0x4004, 1)

    assert events == ["delay@7.0", "record@7.0", "sent"]
    assert [seconds for seconds in sleeps if seconds > 0] == ([delay] if delay else [])


async def test_every_request_of_a_connection_is_charged_to_the_budget():
    budget = RecordingBudget()
    device = FakeDevice(_frame(ANSWER), _frame(ANSWER, transaction=2))
    client = _client(device, budget=budget)

    await client.read_holding_registers(0x4004, 1)
    await client.read_holding_registers(0x4004, 1)

    assert [event for event in budget.events if event.startswith("record")] == [
        "record@7.0",
        "record@7.0",
    ]


def test_the_worst_case_duration_counts_each_request_and_the_budget_wait():
    client = ModbusTcpClient(
        "host",
        502,
        1,
        timeout=5,
        environment=ClientEnvironment(budget=RequestBudget(limit=2, window=10)),
    )
    pace = 5 + REQUEST_PAUSE

    durations = [client.worst_case_duration(requests=count) for count in (1, 2, 3)]

    assert durations[1] - durations[0] == pace
    assert durations[2] - durations[1] == pace + 10
