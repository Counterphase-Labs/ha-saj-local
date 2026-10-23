# SAJ Local developer documentation

How SAJ Local is built, checked and released, and where the truth about each part lives. The documentation explains why the project is built the way it is and links to the file that holds each fact. Versions, command lists and register maps live in the code and configuration, not here.

To get a working checkout and send a change, start with [CONTRIBUTING.md](../../../CONTRIBUTING.md). SAJ Local is a local-only Home Assistant integration: SAJ Local talks to the inverter over the local network and adds no cloud service or companion SDK.

## Developing without an inverter

The simulator is a stand-in SAJ device, so most work needs no hardware. Each simulator serves a page that shows what the simulated system is doing and lets a developer change the system while Home Assistant is polling, without editing a scenario and restarting.

![The Overview of the HS3 simulator page: the status bar, the power-flow diagram and one card for each piece of fitted equipment](../../images/en-gb/developer-simulator-page-overview.png)

[Modbus simulator](simulator.md) explains what the simulator is for and how to run a scenario. [Simulator page](simulator-page.md) shows every view of the page.

## Pages

- [Modbus simulator](simulator.md): what the simulator is for, scenarios and running another system.
- [Simulator page](simulator-page.md): every view of the page, the register inspector, the traffic log, link faults, presets and saved state.
- [Environment](environment.md): set up a checkout and run the development Home Assistant with the simulators.
- [Checks](checks.md): the make targets, the coverage gate and how to narrow a run.
- [Architecture](architecture.md): the SAJ library and the integration, profiles, the catalogue, polling and stable names.
- [Frontend](frontend.md): the card source, the build and the showcase dashboards.
- [Documentation](documentation.md): how these pages, the generated entity reference and the screenshots are made and checked.
- [Releasing](releasing.md): the Home Assistant version bump and the steps before a release.

User documentation is in the [user documentation](../user/README.md).

## Where the truth lives

| Question | Authority |
| --- | --- |
| What must the project do? | [Global requirements](../../../.github/work/requirements.md), [integration requirements](../../../custom_components/saj_local/docs/requirements.md), [cards requirements](../../../frontend/docs/requirements.md), [simulator requirements](../../../mock/docs/requirements.md) |
| What does each part do today? | [Integration features](../../../custom_components/saj_local/docs/features.md), [card features](../../../frontend/docs/features.md), [simulator features](../../../mock/docs/features.md) |
| How is code, testing and documentation written? | [code-style.md](../../../.github/work/code-style.md) |
| What rules bind everyone working here? | [AGENTS.md](../../../AGENTS.md) |
| What was built, and why? | [done/index.md](../../../.github/work/done/index.md) |
| What is planned? | [.github/work/future/](../../../.github/work/future/) |
| Which commands exist? | [Makefile](../../../Makefile) |
| What does CI run? | [ci.yml](../../../.github/workflows/ci.yml) |
| Python dependencies and tool settings | [pyproject.toml](../../../pyproject.toml) |
| Frontend dependencies and scripts | [frontend/package.json](../../../frontend/package.json) |
| Development services | [compose.yaml](../../../compose.yaml) |

Existing code has no authority over requirements. Where they disagree, the code is wrong or the owner changes the requirement.

## Code style

[code-style.md](../../../.github/work/code-style.md) is the authority. The documentation rule of code-style.md shapes these pages: explain why, not how, and let names and types describe the rest.
