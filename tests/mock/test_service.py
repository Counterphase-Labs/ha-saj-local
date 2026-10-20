import asyncio
import logging
from pathlib import Path
from types import SimpleNamespace

import pytest

from saj_modbus_mock import profiles
from saj_modbus_mock import service as service_module
from saj_modbus_mock.exceptions import ControlError
from saj_modbus_mock.link import LinkSettings
from saj_modbus_mock.service import MockService
from saj_modbus_mock.traffic import Answer, Client, Operation, RequestRecord

from .builders import make_scenario


class FakeServer:
    def __init__(self, *, bank, settings, link, recorder, events):
        self.bank = bank
        self.settings = settings
        self.link = link
        self.recorder = recorder
        self.events = events
        self.bound_port = 4321

    async def start(self):
        self.events.append("modbus start")

    async def close(self):
        self.events.append("modbus close")


class FakePanel:
    def __init__(self, *, machine, recorder, address, events, fail=False):
        self.machine = machine
        self.recorder = recorder
        self.host, self.port = address
        self.events = events
        self.fail = fail

    async def start(self):
        if self.fail:
            message = "port busy"
            raise OSError(message)
        self.events.append("panel start")

    async def close(self):
        self.events.append("panel close")


class FakeStore:
    def __init__(self, *, path, scenario_hash, saved):
        self.path = path
        self.scenario_hash = scenario_hash
        self.saved = saved
        self.deleted = 0

    def load(self):
        return self.saved

    def delete(self):
        self.deleted += 1


class FakeSaver:
    def __init__(self, *, store, snapshot, monotonic, events):
        self.store = store
        self.snapshot = snapshot
        self.monotonic = monotonic
        self.events = events
        self.changes = 0

    def changed(self):
        self.changes += 1

    async def run(self):
        self.events.append("saver run")
        try:
            await asyncio.Event().wait()
        finally:
            self.events.append("saver stopped")

    def flush(self):
        self.events.append("flush")


@pytest.fixture
def fakes(monkeypatch):
    made = SimpleNamespace(events=[], saved=None, restore_error=None, panel_fails=False)

    class FakeMachine:
        def __init__(self, *, scenario, monotonic, wiring):
            self.scenario = scenario
            self.monotonic = monotonic
            self.wiring = wiring
            self.on_change = wiring.on_change
            self.on_reset = wiring.on_reset
            self.device = "the device"
            self.restored = []
            made.machine = self

        def restore(self, *, snapshot):
            if made.restore_error is not None:
                raise made.restore_error
            self.restored.append(snapshot)

        def snapshot(self):
            return {"snapshot": "of the machine"}

    def server(*, bank, settings, link, recorder):
        made.server = FakeServer(
            bank=bank,
            settings=settings,
            link=link,
            recorder=recorder,
            events=made.events,
        )
        return made.server

    def panel(*, machine, recorder, host, port):
        made.panel = FakePanel(
            machine=machine,
            recorder=recorder,
            address=(host, port),
            events=made.events,
            fail=made.panel_fails,
        )
        return made.panel

    def store(*, path, scenario_hash):
        made.store = FakeStore(path=path, scenario_hash=scenario_hash, saved=made.saved)
        return made.store

    def saver(*, store, snapshot, monotonic):
        made.saver = FakeSaver(
            store=store, snapshot=snapshot, monotonic=monotonic, events=made.events
        )
        return made.saver

    monkeypatch.setattr(service_module, "Machine", FakeMachine)
    monkeypatch.setattr(service_module, "ModbusServer", server)
    monkeypatch.setattr(service_module, "PanelServer", panel)
    monkeypatch.setattr(service_module, "StateStore", store)
    monkeypatch.setattr(service_module, "Saver", saver)
    monkeypatch.setattr(
        service_module, "scenario_hash", lambda **_arguments: "hash-of-scenario"
    )
    return made


def test_building_the_service_wires_the_device_into_a_server_from_the_scenario(fakes):
    scenario = make_scenario(
        model="hs3",
        server={
            "port": 1502,
            "unit_id": 7,
            "max_clients": 3,
            "panel_port": 8081,
        },
        link=LinkSettings(latency_ms=250),
    )

    def clock():
        return 1.0

    MockService(scenario=scenario, monotonic=clock, host="10.0.0.2")

    assert fakes.machine.scenario is scenario
    assert fakes.machine.monotonic is clock
    assert fakes.server.bank == "the device"
    settings = fakes.server.settings
    assert (settings.unit_id, settings.max_clients, settings.port, settings.host) == (
        7,
        3,
        1502,
        "10.0.0.2",
    )
    assert fakes.server.link.settings.latency_ms == 250
    assert fakes.server.link.is_offline(now=0) is False
    assert fakes.server.link is fakes.machine.wiring.link
    assert fakes.server.recorder is fakes.panel.recorder
    assert fakes.panel.machine is fakes.machine
    assert (fakes.panel.host, fakes.panel.port) == ("10.0.0.2", 8081)


def test_the_recorder_decodes_requests_into_the_fields_of_the_device(fakes):
    scenario = make_scenario(model="hs3")
    MockService(scenario=scenario)
    field = next(
        field
        for block in profiles.build_blocks(scenario=scenario)
        if block.unavailable is None
        for field in block.fields
        if field.readable
    )
    recorder = fakes.server.recorder

    recorder.record_request(
        record=RequestRecord(
            at=5.0,
            client=Client(address="10.0.0.1", port=1),
            connection=1,
            transaction_id=1,
            unit_id=1,
            function=3,
            start=field.address,
            count=field.words,
            operation=Operation.READ,
            answer=Answer.ANSWERED,
            exception_code=None,
            fault=None,
            late_duplicate=False,
            duration_ms=1.0,
            words=(0,) * field.words,
        )
    )

    (entry,) = recorder.traffic(after=0, now=6.0)["entries"]
    assert [covered["name"] for covered in entry["detail"]["fields"]] == [field.name]
    assert fakes.machine.wiring.last_read(address=field.address) == 5.0


def test_the_machines_changes_and_resets_reach_the_saver_and_the_store(fakes):
    MockService(scenario=make_scenario(model="hs3"))

    fakes.machine.on_change()
    fakes.machine.on_reset()

    assert fakes.saver.changes == 1
    assert fakes.store.deleted == 1


def test_the_state_file_and_the_saver_are_set_up_for_this_scenario(fakes):
    def clock():
        return 1.0

    MockService(
        scenario=make_scenario(model="hs3"),
        monotonic=clock,
        state_path=Path("/somewhere/state.json"),
    )

    assert fakes.store.path == Path("/somewhere/state.json")
    assert fakes.store.scenario_hash == "hash-of-scenario"
    assert fakes.saver.store is fakes.store
    assert fakes.saver.monotonic is clock
    assert fakes.saver.snapshot() == {"snapshot": "of the machine"}


def test_the_state_file_defaults_to_the_data_volume(fakes):
    MockService(scenario=make_scenario(model="hs3"))

    assert fakes.store.path == Path("/data/state.json")


def test_a_saved_state_is_restored_into_the_machine(fakes):
    fakes.saved = {"settings": {}}

    MockService(scenario=make_scenario(model="hs3"))

    assert fakes.machine.restored == [{"settings": {}}]


def test_nothing_is_restored_when_nothing_was_saved(fakes):
    MockService(scenario=make_scenario(model="hs3"))

    assert fakes.machine.restored == []


def test_a_saved_state_the_machine_refuses_is_logged_and_the_service_still_starts(
    fakes, caplog
):
    fakes.saved = {"settings": {}}
    fakes.restore_error = ControlError(key="settings", reason="must be a mapping")

    with caplog.at_level(logging.WARNING):
        MockService(scenario=make_scenario(model="hs3"))

    assert [record.getMessage() for record in caplog.records] == [
        (
            "saved state was refused (settings: must be a mapping);"
            " starting from the scenario"
        )
    ]


def test_the_service_reports_the_port_its_server_is_bound_to(fakes):
    service = MockService(scenario=make_scenario(model="hs3"))

    assert service.port == 4321


async def test_running_starts_both_servers_and_the_saver_and_stops_them_in_order(fakes):
    service = MockService(scenario=make_scenario(model="hs3"))
    running = asyncio.create_task(service.run())
    await service.ready.wait()
    assert fakes.events == ["modbus start", "panel start", "saver run"]
    assert not running.done()

    service.request_stop()
    await running

    assert fakes.events[-4:] == [
        "saver stopped",
        "flush",
        "panel close",
        "modbus close",
    ]


async def test_everything_is_closed_even_when_the_wait_is_cancelled(fakes):
    service = MockService(scenario=make_scenario(model="hs3"))
    running = asyncio.create_task(service.run())
    await service.ready.wait()

    running.cancel()
    with pytest.raises(asyncio.CancelledError):
        await running

    assert fakes.events[-4:] == [
        "saver stopped",
        "flush",
        "panel close",
        "modbus close",
    ]


async def test_a_panel_that_cannot_start_still_closes_what_was_started_and_saves(fakes):
    fakes.panel_fails = True
    service = MockService(scenario=make_scenario(model="hs3"))

    with pytest.raises(OSError, match="port busy"):
        await service.run()

    assert not service.ready.is_set()
    assert "modbus start" in fakes.events
    assert fakes.events[-3:] == ["flush", "panel close", "modbus close"]
