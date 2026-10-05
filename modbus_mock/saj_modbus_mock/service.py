import asyncio
import time
from typing import TYPE_CHECKING

from .machine import Machine
from .transport import ModbusServer, ServerSettings

if TYPE_CHECKING:
    from collections.abc import Callable

    from .scenario import Scenario

MILLISECONDS_PER_SECOND = 1000


class MockService:
    def __init__(
        self,
        *,
        scenario: Scenario,
        monotonic: Callable[[], float] = time.monotonic,
        host: str | None = None,
    ) -> None:
        self._stop_requested = asyncio.Event()
        self.ready = asyncio.Event()
        server = scenario.server
        self._server = ModbusServer(
            bank=Machine(scenario=scenario, monotonic=monotonic).device,
            settings=ServerSettings(
                unit_id=server.unit_id,
                max_clients=server.max_clients,
                response_delay_s=server.response_delay_ms / MILLISECONDS_PER_SECOND,
                host=host,
                port=server.port,
            ),
        )

    @property
    def port(self) -> int:
        return self._server.bound_port

    async def run(self) -> None:
        await self._server.start()
        self.ready.set()
        try:
            await self._stop_requested.wait()
        finally:
            await self._server.close()

    def request_stop(self) -> None:
        self._stop_requested.set()
