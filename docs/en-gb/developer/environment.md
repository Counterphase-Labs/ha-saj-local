# Development environment

How to set up a checkout and run the development Home Assistant instance with the simulators.

## Set up a checkout

A checkout needs [uv](https://docs.astral.sh/uv/) for the Python tools, Node.js and npm for the cards, Docker with Docker Compose for Home Assistant and the simulators, and `make`. The required versions are set in `pyproject.toml` and `frontend/package.json`. After cloning, `make setup` installs the Python dependencies, the frontend dependencies and the Chromium browser that the Playwright tests use.

## Run Home Assistant

`make up` starts Home Assistant with the integration and two Modbus simulators, an HS3 and an H2. `make logs` follows the Home Assistant log and `make down` stops everything.

Home Assistant is on port 8123. The HS3 simulator answers Modbus on the host port 5020 and the H2 simulator on 5021, and the simulator pages are on 5080 and 5081. Inside Docker, Home Assistant reaches the simulators by the service names `mock` and `mock-h2` on port 502. No real inverter is needed. The [simulator page](simulator.md) explains how to connect to the simulators and change what the simulators simulate.

To use other host ports, another time zone or other scenarios, copy [compose.override.yaml.example](../../../compose.override.yaml.example) to the ignored `compose.override.yaml` and change what differs. Do not edit `compose.yaml` for local needs, because `make mock-smoke` starts `compose.yaml` too.

## Docker

Development runs in containers so Home Assistant is a known, pinned release with a clean configuration. The services are defined in these files:

- [compose.yaml](../../../compose.yaml): the interactive environment, with Home Assistant, the HS3 simulator `mock` and the H2 simulator `mock-h2`. The integration is mounted read-only into Home Assistant, so the container never writes into the source tree. The simulators keep their changes in `mock/state/hs3/` and `mock/state/h2/`, which Git ignores.
- [compose.playwright.yaml](../../../compose.playwright.yaml): a throwaway Home Assistant built from `Dockerfile.playwright-home-assistant`, with an HS3 simulator, an H2 simulator and Playwright runners. `make test-browser-home-assistant` uses the services `homeassistant`, `mock`, `mock-h2` and `playwright` to prove that each endpoint can be added, loads, reports sensor values, shows solar power on a power flow card and, once control is allowed, accepts a changed setting. `make docs-images` uses the services `homeassistant`, `mock-docs`, `mock-h2` and `playwright-docs`, see [Screenshots](documentation.md#screenshots). The services share no state with the interactive environment.
- `compose.override.yaml`: the ports, time zone and scenarios of your machine. Git ignores the file, and `compose.override.yaml.example` shows the shape.

Under `config/`, Git tracks only `configuration.yaml` and the two showcase dashboards in `config/dashboards/`. The rest is local Home Assistant state.

The [checks page](checks.md) lists what each make target runs, and the [frontend page](frontend.md#showcase-dashboards) describes the two showcase dashboards.
