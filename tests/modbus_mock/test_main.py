import asyncio
import os
import runpy
import signal
import sys
from unittest.mock import patch

import pytest

from saj_modbus_mock import __main__ as entry_point
from saj_modbus_mock.service import MockService


@pytest.mark.parametrize("stop_signal", [signal.SIGTERM, signal.SIGINT])
async def test_serve_returns_when_process_receives_stop_signal(stop_signal):
    serving = asyncio.create_task(entry_point.serve())
    await asyncio.sleep(0)
    assert not serving.done()

    os.kill(os.getpid(), stop_signal)
    await asyncio.wait_for(serving, timeout=1)

    assert serving.done()


async def test_serve_restores_signal_handling_after_stopping():
    serving = asyncio.create_task(entry_point.serve())
    await asyncio.sleep(0)
    os.kill(os.getpid(), signal.SIGTERM)
    await serving

    loop = asyncio.get_running_loop()
    assert not any(loop.remove_signal_handler(sig) for sig in entry_point.STOP_SIGNALS)


def test_running_module_serves_until_stopped():
    async def stop_immediately(self: MockService) -> None:
        return

    with patch.dict(sys.modules), patch.object(MockService, "run", stop_immediately):
        sys.modules.pop("saj_modbus_mock.__main__")
        runpy.run_module("saj_modbus_mock", run_name="__main__")
