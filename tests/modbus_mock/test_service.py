import asyncio
from types import SimpleNamespace

import pytest

from saj_modbus_mock import service as service_module
from saj_modbus_mock.service import MockService

from .builders import make_scenario


class FakeServer:
    def __init__(self, *, bank, settings):
        self.bank = bank
        self.settings = settings
        self.events = []
        self.bound_port = 4321

    async def start(self):
        self.events.append("start")

    async def close(self):
        self.events.append("close")


@pytest.fixture
def fakes(monkeypatch):
    made = {}

    def machine(*, scenario, monotonic):
        made["machine"] = SimpleNamespace(
            scenario=scenario, monotonic=monotonic, device="the device"
        )
        return made["machine"]

    def server(*, bank, settings):
        made["server"] = FakeServer(bank=bank, settings=settings)
        return made["server"]

    monkeypatch.setattr(service_module, "Machine", machine)
    monkeypatch.setattr(service_module, "ModbusServer", server)
    return made


def test_building_the_service_wires_the_device_into_a_server_from_the_scenario(fakes):
    scenario = make_scenario(
        model="hs3",
        server={"port": 1502, "unit_id": 7, "max_clients": 3, "response_delay_ms": 250},
    )

    def clock():
        return 1.0

    MockService(scenario=scenario, monotonic=clock, host="10.0.0.2")

    assert fakes["machine"].scenario is scenario
    assert fakes["machine"].monotonic is clock
    assert fakes["server"].bank == "the device"
    settings = fakes["server"].settings
    assert (settings.unit_id, settings.max_clients, settings.port, settings.host) == (
        7,
        3,
        1502,
        "10.0.0.2",
    )
    assert settings.response_delay_s == 0.25


def test_the_service_reports_the_port_its_server_is_bound_to(fakes):
    service = MockService(scenario=make_scenario(model="hs3"))

    assert service.port == 4321


async def test_running_starts_the_server_signals_ready_and_closes_it_when_stopped(
    fakes,
):
    service = MockService(scenario=make_scenario(model="hs3"))
    running = asyncio.create_task(service.run())
    await service.ready.wait()
    assert fakes["server"].events == ["start"]
    assert not running.done()

    service.request_stop()
    await running

    assert fakes["server"].events == ["start", "close"]


async def test_the_server_is_closed_even_when_the_wait_is_cancelled(fakes):
    service = MockService(scenario=make_scenario(model="hs3"))
    running = asyncio.create_task(service.run())
    await service.ready.wait()

    running.cancel()
    with pytest.raises(asyncio.CancelledError):
        await running

    assert fakes["server"].events == ["start", "close"]
