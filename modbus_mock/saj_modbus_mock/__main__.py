import asyncio
import os
import signal
import sys
from pathlib import Path

from .healthcheck import is_healthy
from .scenario import Scenario, ScenarioError, load_scenario
from .service import MockService

STOP_SIGNALS = (signal.SIGTERM, signal.SIGINT)
CONFIG_ENVIRONMENT_VARIABLE = "SAJ_MOCK_CONFIG"
DEFAULT_CONFIG_PATH = "/config/config.yaml"
HEALTHCHECK_COMMAND = "healthcheck"
EXIT_OK = 0
EXIT_UNHEALTHY = 1
EXIT_INVALID_SCENARIO = 2


async def serve(*, scenario: Scenario) -> None:
    loop = asyncio.get_running_loop()
    service = MockService(scenario=scenario)
    for stop_signal in STOP_SIGNALS:
        loop.add_signal_handler(stop_signal, service.request_stop)
    try:
        await service.run()
    finally:
        for stop_signal in STOP_SIGNALS:
            loop.remove_signal_handler(stop_signal)


def main(*, arguments: list[str] | None = None) -> int:
    args = sys.argv[1:] if arguments is None else arguments
    path = Path(os.environ.get(CONFIG_ENVIRONMENT_VARIABLE, DEFAULT_CONFIG_PATH))
    try:
        scenario = load_scenario(path=path)
    except ScenarioError as error:
        sys.stderr.write(f"invalid scenario: {error}\n")
        return EXIT_INVALID_SCENARIO
    if args == [HEALTHCHECK_COMMAND]:
        return EXIT_OK if asyncio.run(is_healthy(scenario=scenario)) else EXIT_UNHEALTHY
    asyncio.run(serve(scenario=scenario))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
