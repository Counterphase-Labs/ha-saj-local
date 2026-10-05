import asyncio
import signal

from .service import MockService

STOP_SIGNALS = (signal.SIGTERM, signal.SIGINT)


async def serve() -> None:
    loop = asyncio.get_running_loop()
    service = MockService()
    for stop_signal in STOP_SIGNALS:
        loop.add_signal_handler(stop_signal, service.request_stop)
    try:
        await service.run()
    finally:
        for stop_signal in STOP_SIGNALS:
            loop.remove_signal_handler(stop_signal)


def main() -> None:
    asyncio.run(serve())


if __name__ == "__main__":
    main()
