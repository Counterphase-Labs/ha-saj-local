import json
from types import SimpleNamespace
from typing import ClassVar

import pytest
from aiohttp import web

from saj_local_mock import panel as panel_module
from saj_local_mock.exceptions import ControlError
from saj_local_mock.panel import Panel, PanelServer, create_app, refuse_control_errors

STATE = {"time": "now"}
WALL_TIME = 1234.5


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

    def reset_card(self, *, key):
        self._record("reset_card", key=key)

    def registers(self):
        return {"blocks": []}

    def set_link(self, *, values):
        self._record("link", values=values)

    def drop_connections(self):
        self._record("drop")

    def reset_module(self):
        self._record("module")

    def apply_preset(self, *, key):
        self._record("preset", key=key)


class FakeRecorder:
    def __init__(self):
        self.calls = []

    def traffic(self, *, after, now):
        self.calls.append(("traffic", after, now))
        return {"entries": [], "latest": 0, "counters": {}, "history": {}}

    def reset(self):
        self.calls.append(("reset",))


def request(*, body=None, name=None, invalid=False, query=None):
    async def json_body():
        if invalid:
            message = "not json"
            raise ValueError(message)
        return body

    return SimpleNamespace(
        json=json_body,
        match_info={"name": name, "card": name, "path": name},
        query=query or {},
    )


@pytest.fixture
def machine():
    return FakeMachine()


@pytest.fixture
def recorder():
    return FakeRecorder()


@pytest.fixture
def static_root(tmp_path):
    root = tmp_path / "static"
    (root / "vendor").mkdir(parents=True)
    (root / "panel.css").write_text("body{}", encoding="utf-8")
    (root / "vendor" / "icon.svg").write_text("<svg/>", encoding="utf-8")
    (root / "notes.md").write_text("# notes", encoding="utf-8")
    (root / "view.js").write_text("export {}", encoding="utf-8")
    (root / "other.html").write_text("<p>other</p>", encoding="utf-8")
    (root / "data.bin").write_bytes(b"\x00")
    (tmp_path / "secret.css").write_text("secret", encoding="utf-8")
    (root / "escape.css").symlink_to(tmp_path / "secret.css")
    return root


@pytest.fixture
def panel(machine, recorder, static_root):
    return Panel(
        machine=machine,
        recorder=recorder,
        wall_clock=lambda: WALL_TIME,
        read_page=lambda: "<html>the page</html>",
        static_root=static_root,
    )


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


async def test_a_card_is_reset_by_the_name_in_the_path_and_the_state_answers(
    panel, machine
):
    response = await panel.reset_card(request(name="solar"))

    assert machine.calls == [("reset_card", {"key": "solar"})]
    assert answer(response=response) == STATE


async def test_a_refused_card_reset_answers_400_and_changes_nothing(panel, machine):
    machine.refusal = ControlError(key="nope", reason="is not a card of this device")
    response = await refuse_control_errors(request(name="nope"), panel.reset_card)

    assert response.status == 400
    assert answer(response=response)["key"] == "nope"


@pytest.mark.parametrize(
    ("route", "operation", "body"),
    [
        ("link", "link", {"latency_ms": 5}),
        ("drop_connections", "drop", None),
        ("reset_module", "module", None),
    ],
)
async def test_a_link_route_asks_the_machine_and_answers_with_the_state(
    panel, machine, route, operation, body
):
    response = await getattr(panel, route)(request(body=body))

    expected = {"values": body} if body else {}
    assert machine.calls == [(operation, expected)]
    assert answer(response=response) == STATE


async def test_a_refused_link_setting_answers_400_with_its_key(panel, machine):
    machine.refusal = ControlError(key="busy_percent", reason="must be 0..100")

    response = await refuse_control_errors(
        request(body={"busy_percent": 500}), panel.link
    )

    assert response.status == 400
    assert answer(response=response)["key"] == "busy_percent"


@pytest.mark.parametrize(
    ("query", "after"), [({}, 0), ({"after": "0"}, 0), ({"after": "42"}, 42)]
)
async def test_the_traffic_is_the_recorders_after_a_sequence_with_the_wall_time(
    panel, recorder, query, after
):
    response = await panel.traffic(request(query=query))

    assert recorder.calls == [("traffic", after, WALL_TIME)]
    assert answer(response=response) == {
        "entries": [],
        "latest": 0,
        "counters": {},
        "history": {},
        "now": WALL_TIME,
    }


@pytest.mark.parametrize("after", ["-1", "x", "1.5", ""])
async def test_a_sequence_that_is_not_a_number_is_refused(panel, recorder, after):
    response = await refuse_control_errors(
        request(query={"after": after}), panel.traffic
    )

    assert response.status == 400
    assert answer(response=response)["key"] == "after"
    assert recorder.calls == []


async def test_resetting_the_traffic_clears_the_recorder_and_answers_with_nothing(
    panel, recorder
):
    response = await panel.reset_traffic(request())

    assert recorder.calls == [("reset",), ("traffic", 0, WALL_TIME)]
    assert answer(response=response)["entries"] == []


async def test_the_register_snapshot_is_the_machines(panel):
    assert answer(response=await panel.registers(request())) == {"blocks": []}


@pytest.mark.parametrize(
    ("path", "content_type", "text"),
    [
        ("panel.css", "text/css", "body{}"),
        ("view.js", "text/javascript", "export {}"),
        ("vendor/icon.svg", "image/svg+xml", "<svg/>"),
        ("notes.md", "text/markdown", "# notes"),
        ("other.html", "text/html", "<p>other</p>"),
    ],
)
async def test_a_static_file_is_served_with_its_content_type(
    panel, path, content_type, text
):
    response = await panel.static(request(name=path))

    assert response.content_type == content_type
    assert response.charset == "utf-8"
    assert response.text == text


@pytest.mark.parametrize(
    "path",
    [
        "../secret.css",
        "vendor/../../secret.css",
        "escape.css",
        "data.bin",
        "vendor",
        "missing.css",
        "bad\x00name.css",
    ],
)
async def test_a_static_path_outside_the_folder_or_of_another_kind_is_not_found(
    panel, path
):
    with pytest.raises(web.HTTPNotFound):
        await panel.static(request(name=path))


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
        ("GET", "/api/registers"),
        ("GET", "/api/traffic"),
        ("POST", "/api/traffic/reset"),
        ("POST", "/api/link"),
        ("POST", "/api/link/drop"),
        ("POST", "/api/link/reset"),
        ("GET", "/static/{path}"),
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
        ("POST", "/api/reset/{card}"),
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
    machine, recorder, fake_web
):
    server = PanelServer(machine=machine, recorder=recorder, host="10.0.0.1", port=8081)

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
    machine, recorder, fake_web
):
    server = PanelServer(machine=machine, recorder=recorder, host=None, port=0)
    await server.close()
    await server.start()

    await server.close()

    assert FakeRunner.instances[0].events == ["setup", "cleanup"]
