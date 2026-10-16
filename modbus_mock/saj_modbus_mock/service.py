import asyncio
import contextlib
import logging
import time
from pathlib import Path
from typing import TYPE_CHECKING

from . import profiles
from .description import DeviceFieldDecoder
from .exceptions import ControlError
from .link import Link
from .machine import Machine, Wiring
from .panel import PanelServer
from .persistence import DEFAULT_STATE_PATH, Saver, StateStore, scenario_hash
from .traffic import Recorder
from .transport import ModbusServer, ServerSettings

if TYPE_CHECKING:
    from collections.abc import Callable

    from .scenario import Scenario

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
        self._link = Link(seed=scenario.simulation.seed, settings=scenario.link)
        self._recorder = Recorder(
            decoder=DeviceFieldDecoder(blocks=profiles.build_blocks(scenario=scenario))
        )
        self._machine = Machine(
            scenario=scenario,
            monotonic=monotonic,
            wiring=Wiring(
                on_change=self._saver.changed,
                on_reset=self._store.delete,
                last_read=self._recorder.last_read,
                link=self._link,
            ),
        )
        self._restore_saved_state()
        self._panel = PanelServer(
            machine=self._machine,
            recorder=self._recorder,
            host=host,
            port=server.panel_port,
        )
        self._server = ModbusServer(
            bank=self._machine.device,
            settings=ServerSettings(
                unit_id=server.unit_id,
                max_clients=server.max_clients,
                host=host,
                port=server.port,
            ),
            link=self._link,
            recorder=self._recorder,
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
