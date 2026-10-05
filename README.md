# SAJ Modbus

A local-only Home Assistant integration for SAJ inverters over Modbus.

This project is unreleased and under development. It currently provides an empty foundation: no device functionality yet.

## Development

`uv` and `npm` run on the host; Home Assistant, the Modbus mock and the Home Assistant browser tests run in Docker. Run `make setup` once, then `make ci` before sending changes.

| Target | Description |
| --- | --- |
| `setup` | Install Python and frontend dependencies and the Playwright Chromium browser |
| `up` | Build and start Home Assistant with the integration mounted, alongside the Modbus mock |
| `down` | Stop the development containers |
| `logs` | Follow the Home Assistant log |
| `lint` | Run ruff format check, ruff check, mypy, import-linter and complexipy |
| `copy-paste` | Detect copied code with jscpd |
| `test` | Run the Python tests with the 100 percent coverage gate |
| `test-isolated` | Run the library and mock tests in an environment without Home Assistant |
| `python-ci` | Run `lint`, `copy-paste`, `test` and `test-isolated` |
| `frontend-check` | Run the frontend format check, type check, lint and unit tests |
| `frontend-build` | Build the frontend asset into the integration |
| `test-browser-controlled` | Build the frontend and run the controlled Playwright suite |
| `test-browser-home-assistant` | Run the Playwright suite against a clean containerised Home Assistant |
| `frontend-ci` | Run `frontend-check` and `test-browser-controlled` |
| `release-check` | Verify the HACS archive contains the built frontend asset |
| `mock-build` | Build the Modbus mock image |
| `ci` | Run every check above that CI runs |
