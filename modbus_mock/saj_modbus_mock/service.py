import asyncio


class MockService:
    def __init__(self) -> None:
        self._stop_requested = asyncio.Event()

    async def run(self) -> None:
        await self._stop_requested.wait()

    def request_stop(self) -> None:
        self._stop_requested.set()
