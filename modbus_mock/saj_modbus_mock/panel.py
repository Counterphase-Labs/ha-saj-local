"""The control panel's HTTP side: routes that turn requests into machine calls."""

from pathlib import Path
from typing import TYPE_CHECKING

from aiohttp import web

from .exceptions import ControlError

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Mapping

    from .machine import Machine

PAGE_PATH = Path(__file__).resolve().parents[1] / "static" / "index.html"
EXPORT_FILENAME = "scenario.yaml"
YAML_CONTENT_TYPE = "application/yaml"
BAD_REQUEST = 400


def read_page() -> str:
    return PAGE_PATH.read_text(encoding="utf-8")


@web.middleware
async def refuse_control_errors(
    request: web.Request,
    handler: Callable[[web.Request], Awaitable[web.StreamResponse]],
) -> web.StreamResponse:
    """A refused change answers 400 with the reason; nothing was changed."""
    try:
        return await handler(request)
    except ControlError as error:
        return web.json_response(
            {"error": str(error), "key": error.key, "reason": error.reason},
            status=BAD_REQUEST,
        )


async def _body(*, request: web.Request) -> Mapping[str, object]:
    try:
        body = await request.json()
    except ValueError as error:
        raise ControlError(key="body", reason="must be JSON") from error
    if not isinstance(body, dict):
        raise ControlError(key="body", reason="must be a JSON object")
    return body


class Panel:
    """Each route calls one machine operation and answers with the state."""

    def __init__(
        self, *, machine: Machine, read_page: Callable[[], str] = read_page
    ) -> None:
        self._machine = machine
        self._read_page = read_page

    def _state(self) -> web.Response:
        return web.json_response(self._machine.state())

    async def page(self, _request: web.Request) -> web.Response:
        return web.Response(text=self._read_page(), content_type="text/html")

    async def description(self, _request: web.Request) -> web.Response:
        return web.json_response(self._machine.describe())

    async def state(self, _request: web.Request) -> web.Response:
        return self._state()

    async def scenario(self, _request: web.Request) -> web.Response:
        return web.Response(
            text=self._machine.export_scenario(),
            content_type=YAML_CONTENT_TYPE,
            headers={
                "Content-Disposition": f'attachment; filename="{EXPORT_FILENAME}"'
            },
        )

    async def settings(self, request: web.Request) -> web.Response:
        self._machine.set_settings(values=await _body(request=request))
        return self._state()

    async def commands(self, request: web.Request) -> web.Response:
        self._machine.run_command(values=await _body(request=request))
        return self._state()

    async def faults(self, request: web.Request) -> web.Response:
        self._machine.set_faults(values=await _body(request=request))
        return self._state()

    async def variation(self, request: web.Request) -> web.Response:
        self._machine.set_variation(values=await _body(request=request))
        return self._state()

    async def holds(self, request: web.Request) -> web.Response:
        self._machine.set_holds(values=await _body(request=request))
        return self._state()

    async def battery(self, request: web.Request) -> web.Response:
        self._machine.set_battery(values=await _body(request=request))
        return self._state()

    async def ev(self, request: web.Request) -> web.Response:
        self._machine.set_ev(values=await _body(request=request))
        return self._state()

    async def clock(self, request: web.Request) -> web.Response:
        self._machine.set_clock(values=await _body(request=request))
        return self._state()

    async def reset_ledger(self, _request: web.Request) -> web.Response:
        self._machine.reset_ledger()
        return self._state()

    async def reset(self, _request: web.Request) -> web.Response:
        self._machine.reset()
        return self._state()

    async def preset(self, request: web.Request) -> web.Response:
        self._machine.apply_preset(key=request.match_info["name"])
        return self._state()


def create_app(*, panel: Panel) -> web.Application:
    app = web.Application(middlewares=[refuse_control_errors])
    app.router.add_get("/", panel.page)
    app.router.add_get("/api/description", panel.description)
    app.router.add_get("/api/state", panel.state)
    app.router.add_get("/api/scenario", panel.scenario)
    app.router.add_post("/api/settings", panel.settings)
    app.router.add_post("/api/commands", panel.commands)
    app.router.add_post("/api/faults", panel.faults)
    app.router.add_post("/api/variation", panel.variation)
    app.router.add_post("/api/holds", panel.holds)
    app.router.add_post("/api/battery", panel.battery)
    app.router.add_post("/api/ev", panel.ev)
    app.router.add_post("/api/clock", panel.clock)
    app.router.add_post("/api/ledger/reset", panel.reset_ledger)
    app.router.add_post("/api/reset", panel.reset)
    app.router.add_post("/api/presets/{name}", panel.preset)
    return app


class PanelServer:
    """Serves the panel beside the Modbus server, on the same event loop."""

    def __init__(
        self,
        *,
        machine: Machine,
        host: str | None,
        port: int,
        read_page: Callable[[], str] = read_page,
    ) -> None:
        self._app = create_app(panel=Panel(machine=machine, read_page=read_page))
        self._host = host
        self._port = port
        self._runner: web.AppRunner | None = None

    async def start(self) -> None:
        # Polling every few seconds would fill the log, so requests are not logged.
        self._runner = web.AppRunner(self._app, access_log=None)
        await self._runner.setup()
        await web.TCPSite(self._runner, host=self._host, port=self._port).start()

    async def close(self) -> None:
        if self._runner is not None:
            await self._runner.cleanup()
