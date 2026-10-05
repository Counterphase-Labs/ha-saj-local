import asyncio

from saj_modbus_mock.service import MockService


async def test_service_runs_until_stop_is_requested():
    service = MockService()
    running = asyncio.create_task(service.run())

    await asyncio.sleep(0)
    assert not running.done()

    service.request_stop()
    await asyncio.wait_for(running, timeout=1)
    assert running.done()
