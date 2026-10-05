import asyncio
import runpy
import signal
import sys
from typing import ClassVar

import pytest

from saj_modbus_mock import __main__ as entry_point
from saj_modbus_mock import scenario as scenario_module
from saj_modbus_mock.scenario import ScenarioError

from .builders import make_scenario

SCENARIO = make_scenario(model="hs3")


class FakeService:
    instances: ClassVar[list] = []

    def __init__(self, *, scenario):
        self.scenario = scenario
        self.stops = 0
        self.ran = False
        self.instances.append(self)

    async def run(self):
        self.ran = True
        for handler in loop_state["handlers"].values():
            handler()

    def request_stop(self):
        self.stops += 1


loop_state = {}


class FakeLoop:
    def __init__(self):
        self.handlers = {}
        self.removed = []
        loop_state["handlers"] = self.handlers

    def add_signal_handler(self, number, handler):
        self.handlers[number] = handler

    def remove_signal_handler(self, number):
        self.removed.append(number)


@pytest.fixture
def fake_loop(monkeypatch):
    loop = FakeLoop()
    FakeService.instances = []
    monkeypatch.setattr(asyncio, "get_running_loop", lambda: loop)
    monkeypatch.setattr(entry_point, "MockService", FakeService)
    return loop


async def test_serving_registers_the_stop_signals_runs_the_service_and_unregisters(
    fake_loop,
):
    await entry_point.serve(scenario=SCENARIO)

    service = FakeService.instances[0]
    assert service.scenario is SCENARIO
    assert service.ran
    assert set(fake_loop.handlers) == {signal.SIGTERM, signal.SIGINT}
    assert service.stops == 2
    assert set(fake_loop.removed) == {signal.SIGTERM, signal.SIGINT}


async def test_signals_are_unregistered_even_when_the_service_fails(
    fake_loop, monkeypatch
):
    async def failing(self):
        raise RuntimeError

    monkeypatch.setattr(FakeService, "run", failing)

    with pytest.raises(RuntimeError):
        await entry_point.serve(scenario=SCENARIO)

    assert set(fake_loop.removed) == {signal.SIGTERM, signal.SIGINT}


@pytest.fixture
def loaded(monkeypatch):
    seen = {}

    def load_scenario(*, path):
        seen["path"] = path
        return SCENARIO

    monkeypatch.setattr(entry_point, "load_scenario", load_scenario)
    return seen


def run_coroutine_stub(*, monkeypatch, result=None):
    ran = []

    def run(coroutine):
        ran.append(coroutine.cr_code.co_name)
        coroutine.close()
        return result

    monkeypatch.setattr(asyncio, "run", run)
    return ran


def test_the_scenario_path_comes_from_the_environment(loaded, monkeypatch):
    monkeypatch.setenv("SAJ_MOCK_CONFIG", "/somewhere/else.yaml")
    run_coroutine_stub(monkeypatch=monkeypatch)

    entry_point.main(arguments=[])

    assert str(loaded["path"]) == "/somewhere/else.yaml"


def test_the_scenario_path_defaults_to_the_mounted_location(loaded, monkeypatch):
    monkeypatch.delenv("SAJ_MOCK_CONFIG", raising=False)
    run_coroutine_stub(monkeypatch=monkeypatch)

    entry_point.main(arguments=[])

    assert str(loaded["path"]) == "/config/config.yaml"


def test_main_serves_the_scenario_until_stopped(loaded, monkeypatch):
    ran = run_coroutine_stub(monkeypatch=monkeypatch)

    assert entry_point.main(arguments=[]) == entry_point.EXIT_OK
    assert ran == ["serve"]


def test_an_invalid_scenario_exits_with_the_reason_and_serves_nothing(
    monkeypatch, capsys
):
    def refuse(*, path):
        raise ScenarioError(key="device.model", reason="is required")

    monkeypatch.setattr(entry_point, "load_scenario", refuse)
    ran = run_coroutine_stub(monkeypatch=monkeypatch)

    assert entry_point.main(arguments=[]) == entry_point.EXIT_INVALID_SCENARIO
    assert "device.model: is required" in capsys.readouterr().err
    assert ran == []


@pytest.mark.parametrize(("healthy", "code"), [(True, 0), (False, 1)])
def test_the_healthcheck_exit_status_reports_the_verdict(
    loaded, monkeypatch, healthy, code
):
    async def verdict(*, scenario):
        return healthy

    monkeypatch.setattr(entry_point, "is_healthy", verdict)

    assert entry_point.main(arguments=["healthcheck"]) == code


def test_main_reads_the_command_line_when_no_arguments_are_given(loaded, monkeypatch):
    async def verdict(*, scenario):
        return True

    monkeypatch.setattr(entry_point, "is_healthy", verdict)
    monkeypatch.setattr(sys, "argv", ["saj_modbus_mock", "healthcheck"])

    assert entry_point.main() == 0


def test_running_the_module_exits_with_the_status_of_main(monkeypatch):
    def refuse(*, path):
        raise ScenarioError(key="device.model", reason="is required")

    monkeypatch.setattr(scenario_module, "load_scenario", refuse)
    monkeypatch.delitem(sys.modules, "saj_modbus_mock.__main__", raising=False)

    with pytest.raises(SystemExit) as caught:
        runpy.run_module("saj_modbus_mock", run_name="__main__")

    assert caught.value.code == entry_point.EXIT_INVALID_SCENARIO
