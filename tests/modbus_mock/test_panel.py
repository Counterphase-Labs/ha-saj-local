import json
from types import SimpleNamespace
from typing import ClassVar

import pytest
from aiohttp import web

from saj_modbus_mock import panel as panel_module
from saj_modbus_mock.exceptions import ControlError
from saj_modbus_mock.panel import Panel, PanelServer, create_app, refuse_control_errors

STATE = {"time": "now"}


class FakeMachine:
    """Records each operation and the values it was given."""

    def __init__(self):
        self.calls = []
        self.refusal = None

    def _record(self, name, **arguments):
        self.calls.append((name, arguments))
        if self.refusal is not None:
            raise self.refusal

    def describe(self):
        return {"model": {"name": "hs3"}}

    def state(self):
        return STATE

    def export_scenario(self):
        return "device:\n  model: hs3\n"

    def set_settings(self, *, values):
        self._record("settings", values=values)

    def run_command(self, *, values):
        self._record("commands", values=values)

    def set_faults(self, *, values):
        self._record("faults", values=values)

    def set_variation(self, *, values):
        self._record("variation", values=values)

    def set_holds(self, *, values):
        self._record("holds", values=values)

    def set_battery(self, *, values):
        self._record("battery", values=values)

    def set_ev(self, *, values):
        self._record("ev", values=values)

    def set_clock(self, *, values):
        self._record("clock", values=values)

    def reset_ledger(self):
        self._record("ledger")

    def reset(self):
        self._record("reset")

    def apply_preset(self, *, key):
        self._record("preset", key=key)


def request(*, body=None, name=None, invalid=False):
    async def json_body():
        if invalid:
            message = "not json"
            raise ValueError(message)
        return body

    return SimpleNamespace(json=json_body, match_info={"name": name})


@pytest.fixture
def machine():
    return FakeMachine()


@pytest.fixture
def panel(machine):
    return Panel(machine=machine, read_page=lambda: "<html>the page</html>")


def answer(*, response):
    return json.loads(response.text)


async def test_the_page_is_served_as_html(panel):
    response = await panel.page(request())

    assert response.text == "<html>the page</html>"
    assert response.content_type == "text/html"


async def test_the_description_and_the_state_are_the_machines(panel):
    assert answer(response=await panel.description(request())) == {
        "model": {"name": "hs3"}
    }
    assert answer(response=await panel.state(request())) == STATE


async def test_the_scenario_is_served_as_a_yaml_download(panel):
    response = await panel.scenario(request())

    assert response.text == "device:\n  model: hs3\n"
    assert response.content_type == "application/yaml"
    assert "scenario.yaml" in response.headers["Content-Disposition"]


@pytest.mark.parametrize(
    ("route", "operation"),
    [
        ("settings", "settings"),
        ("commands", "commands"),
        ("faults", "faults"),
        ("variation", "variation"),
        ("holds", "holds"),
        ("battery", "battery"),
        ("ev", "ev"),
        ("clock", "clock"),
    ],
)
async def test_a_change_passes_its_body_to_the_machine_and_answers_with_the_state(
    panel, machine, route, operation
):
    body = {"some": 1}

    response = await getattr(panel, route)(request(body=body))

    assert machine.calls == [(operation, {"values": body})]
    assert response.status == 200
    assert answer(response=response) == STATE


@pytest.mark.parametrize(
    ("route", "operation"), [("reset_ledger", "ledger"), ("reset", "reset")]
)
async def test_a_reset_takes_no_body(panel, machine, route, operation):
    response = await getattr(panel, route)(request())

    assert machine.calls == [(operation, {})]
    assert answer(response=response) == STATE


async def test_a_preset_is_applied_by_the_name_in_the_path(panel, machine):
    response = await panel.preset(request(name="grid-lost"))

    assert machine.calls == [("preset", {"key": "grid-lost"})]
    assert answer(response=response) == STATE


@pytest.mark.parametrize("body", [[1, 2], "text", 5, None])
async def test_a_body_that_is_not_a_json_object_is_refused_before_the_machine_is_asked(
    panel, machine, body
):
    with pytest.raises(ControlError) as caught:
        await panel.settings(request(body=body))

    assert (caught.value.key, caught.value.reason) == ("body", "must be a JSON object")
    assert machine.calls == []


async def test_a_body_that_is_not_json_is_refused(panel, machine):
    with pytest.raises(ControlError) as caught:
        await panel.settings(request(invalid=True))

    assert (caught.value.key, caught.value.reason) == ("body", "must be JSON")
    assert machine.calls == []


async def test_a_refused_change_answers_400_with_the_reason():
    refusal = ControlError(key="app_mode", reason="value outside enumeration")

    async def refuse(_request):
        raise refusal

    response = await refuse_control_errors(request(), refuse)

    assert response.status == 400
    assert answer(response=response) == {
        "error": "app_mode: value outside enumeration",
        "key": "app_mode",
        "reason": "value outside enumeration",
    }


async def test_an_accepted_change_passes_through_unchanged():
    expected = web.Response(text="fine")

    async def accept(_request):
        return expected

    assert await refuse_control_errors(request(), accept) is expected


async def test_other_failures_are_not_hidden():
    async def fail(_request):
        raise RuntimeError

    with pytest.raises(RuntimeError):
        await refuse_control_errors(request(), fail)


def test_the_app_routes_each_endpoint_to_the_panel_and_refuses_through_the_middleware(
    panel,
):
    app = create_app(panel=panel)

    routes = {
        (route.method, route.resource.canonical)
        for route in app.router.routes()
        if route.method != "HEAD"
    }
    assert routes == {
        ("GET", "/"),
        ("GET", "/api/description"),
        ("GET", "/api/state"),
        ("GET", "/api/scenario"),
        ("POST", "/api/settings"),
        ("POST", "/api/commands"),
        ("POST", "/api/faults"),
        ("POST", "/api/variation"),
        ("POST", "/api/holds"),
        ("POST", "/api/battery"),
        ("POST", "/api/ev"),
        ("POST", "/api/clock"),
        ("POST", "/api/ledger/reset"),
        ("POST", "/api/reset"),
        ("POST", "/api/presets/{name}"),
    }
    assert list(app.middlewares) == [refuse_control_errors]


def test_the_page_is_read_from_the_file_beside_the_package(tmp_path, monkeypatch):
    page = tmp_path / "index.html"
    page.write_text("<html>hello</html>", encoding="utf-8")
    monkeypatch.setattr(panel_module, "PAGE_PATH", page)

    assert panel_module.read_page() == "<html>hello</html>"


class FakeRunner:
    instances: ClassVar[list] = []

    def __init__(self, app, **options):
        self.app = app
        self.options = options
        self.events = []
        self.instances.append(self)

    async def setup(self):
        self.events.append("setup")

    async def cleanup(self):
        self.events.append("cleanup")


class FakeSite:
    instances: ClassVar[list] = []

    def __init__(self, runner, **options):
        self.runner = runner
        self.options = options
        self.started = False
        self.instances.append(self)

    async def start(self):
        self.started = True


@pytest.fixture
def fake_web(monkeypatch):
    FakeRunner.instances = []
    FakeSite.instances = []
    monkeypatch.setattr(panel_module.web, "AppRunner", FakeRunner)
    monkeypatch.setattr(panel_module.web, "TCPSite", FakeSite)


async def test_the_server_serves_the_app_on_its_host_and_port_without_an_access_log(
    machine, fake_web
):
    server = PanelServer(machine=machine, host="10.0.0.1", port=8081)

    await server.start()

    (runner,) = FakeRunner.instances
    (site,) = FakeSite.instances
    assert runner.events == ["setup"]
    assert runner.options == {"access_log": None}
    assert isinstance(runner.app, web.Application)
    assert site.runner is runner
    assert site.options == {"host": "10.0.0.1", "port": 8081}
    assert site.started


async def test_closing_cleans_up_the_runner_and_is_harmless_before_starting(
    machine, fake_web
):
    server = PanelServer(machine=machine, host=None, port=0)
    await server.close()
    await server.start()

    await server.close()

    assert FakeRunner.instances[0].events == ["setup", "cleanup"]
