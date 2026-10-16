import asyncio
import contextlib
import logging
import time
from pathlib import Path
from typing import TYPE_CHECKING

from .exceptions import ControlError
from .machine import Machine
from .panel import PanelServer
from .persistence import DEFAULT_STATE_PATH, Saver, StateStore, scenario_hash
from .transport import ModbusServer, ServerSettings

if TYPE_CHECKING:
    from collections.abc import Callable

    from .scenario import Scenario

MILLISECONDS_PER_SECOND = 1000
LOGGER = logging.getLogger(__name__)


class MockService:
    def __init__(
        self,
        *,
        scenario: Scenario,
        monotonic: Callable[[], float] = time.monotonic,
        host: str | None = None,
        state_path: Path = Path(DEFAULT_STATE_PATH),
    ) -> None:
        self._stop_requested = asyncio.Event()
        self.ready = asyncio.Event()
        server = scenario.server
        self._store = StateStore(
            path=state_path, scenario_hash=scenario_hash(scenario=scenario)
        )
        self._saver = Saver(
            store=self._store, snapshot=self._snapshot, monotonic=monotonic
        )
        self._machine = Machine(
            scenario=scenario,
            monotonic=monotonic,
            on_change=self._saver.changed,
            on_reset=self._store.delete,
        )
        self._restore_saved_state()
        self._panel = PanelServer(
            machine=self._machine, host=host, port=server.panel_port
        )
        self._server = ModbusServer(
            bank=self._machine.device,
            settings=ServerSettings(
                unit_id=server.unit_id,
                max_clients=server.max_clients,
                response_delay_s=server.response_delay_ms / MILLISECONDS_PER_SECOND,
                host=host,
                port=server.port,
            ),
        )

    def _snapshot(self) -> dict[str, object]:
        return self._machine.snapshot()

    def _restore_saved_state(self) -> None:
        saved = self._store.load()
        if saved is None:
            return
        try:
            self._machine.restore(snapshot=saved)
        except ControlError as error:
            LOGGER.warning(
                "saved state was refused (%s); starting from the scenario", error
            )

    @property
    def port(self) -> int:
        return self._server.bound_port

    async def run(self) -> None:
        saving = asyncio.create_task(self._saver.run())
        try:
            await self._server.start()
            await self._panel.start()
            self.ready.set()
            await self._stop_requested.wait()
        finally:
            saving.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await saving
            self._saver.flush()
            await self._panel.close()
            await self._server.close()

    def request_stop(self) -> None:
        self._stop_requested.set()
