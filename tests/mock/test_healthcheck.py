import asyncio
import struct

import pytest

from saj_local_mock import healthcheck
from saj_local_mock.healthcheck import is_healthy, read_device_type

from .builders import make_scenario


class FakeWriter:
    def __init__(self, *, close_error=None):
        self.sent = b""
        self.closed = False
        self.close_error = close_error

    def write(self, data):
        self.sent += data

    async def drain(self):
        return None

    def close(self):
        self.closed = True

    async def wait_closed(self):
        if self.close_error:
            raise self.close_error


def response(*, pdu, transaction=1, unit=1):
    return struct.pack(">HHHB", transaction, 0, len(pdu) + 1, unit) + pdu


def device_type_response(*, value):
    return response(pdu=struct.pack(">BBH", 3, 2, value))


@pytest.fixture
def connection(monkeypatch):
    state = {"data": b"", "error": None, "hang": False}
    writer = FakeWriter()
    state["writer"] = writer

    async def open_connection(host, port):
        state["target"] = (host, port)
        if state["error"]:
            raise state["error"]
        reader = asyncio.StreamReader()
        reader.feed_data(state["data"])
        if not state["hang"]:
            reader.feed_eof()
        return reader, writer

    monkeypatch.setattr(asyncio, "open_connection", open_connection)
    return state


async def test_the_check_asks_the_local_device_for_its_type_and_returns_the_answer(
    connection,
):
    connection["data"] = device_type_response(value=0x1610)

    found = await read_device_type(port=1502, unit_id=5)

    assert found == 0x1610
    assert connection["target"] == (healthcheck.LOCAL_HOST, 1502)
    assert connection["writer"].sent == struct.pack(
        ">HHHBBHH", 1, 0, 6, 5, 3, 0x8F00, 1
    )
    assert connection["writer"].closed


@pytest.mark.parametrize(
    "data",
    [
        response(pdu=bytes([0x83, 0x02])),
        response(pdu=bytes([4, 2, 0, 1])),
        response(pdu=struct.pack(">BBHH", 3, 4, 1, 2)),
    ],
)
async def test_an_answer_that_is_not_a_one_register_read_is_reported_as_minus_one(
    connection, data
):
    connection["data"] = data

    assert await read_device_type(port=1, unit_id=1) == -1


async def test_a_connection_error_while_closing_is_swallowed(connection):
    connection["data"] = device_type_response(value=5)
    connection["writer"].close_error = ConnectionResetError()

    assert await read_device_type(port=1, unit_id=1) == 5


@pytest.mark.parametrize(
    ("model", "device_type", "healthy"),
    [("hs3", 0x1610, True), ("hs3", 0x005A, False), ("h2", 0x005A, True)],
)
async def test_the_device_is_healthy_when_it_reports_the_scenarios_model(
    connection, model, device_type, healthy
):
    connection["data"] = device_type_response(value=device_type)

    assert await is_healthy(scenario=make_scenario(model=model)) is healthy


async def test_a_wrong_pdu_is_unhealthy(connection):
    connection["data"] = response(pdu=bytes([0x83, 0x02]))

    assert not await is_healthy(scenario=make_scenario(model="hs3"))


@pytest.mark.parametrize("error", [ConnectionRefusedError(), OSError()])
async def test_an_unreachable_device_is_unhealthy(connection, error):
    connection["error"] = error

    assert not await is_healthy(scenario=make_scenario(model="hs3"))


async def test_a_connection_closed_mid_answer_is_unhealthy(connection):
    connection["data"] = device_type_response(value=0x1610)[:-3]

    assert not await is_healthy(scenario=make_scenario(model="hs3"))


async def test_a_device_that_never_answers_is_unhealthy_once_the_timeout_passes(
    connection, monkeypatch
):
    connection["hang"] = True
    monkeypatch.setattr(healthcheck, "CHECK_TIMEOUT_S", 0.0)

    assert not await is_healthy(scenario=make_scenario(model="hs3"))
