# Simulator Guidance

This folder is the Modbus simulator of a SAJ controller, a standalone service used for development and testing. The root `AGENTS.md` also applies, including the rule that `mock/` has no authority over requirements or Modbus design decisions.

## Feature List

`docs/features.md` lists what the simulator simulates and what a developer can set on the control page or in a scenario. Developers read the file to learn what the simulated system offers.

- Organise the file by simulated model or concern. Under each heading come an overview of one to three sentences, a `Files:` line naming the simulator files that produce the behaviour, and the bullets.
- Write one bullet per simulated behaviour or setting a developer would recognise, such as a model, a piece of equipment, a link fault or a page control. Leave out the detail of a single logic path.
- List only behaviour the simulator has today. A behaviour that is merely wanted, planned or half built stays out.
- Keep to plain words. Leave module, class, function and file names out of the bullets, and leave out dates, plan names and roadmap claims.
- When a developer would trip over a limitation, say so inside the bullet.
- The simulator's features never justify integration design.

## Requirements

`docs/requirements.md` holds the requirements on the simulator and links to the global requirements in `.github/work/requirements.md`. A section of `docs/features.md` with a section of the same name there has a `Requirements:` line, and that section has a `Features:` line pointing back. The requirements on the simulator never become requirements on the integration.

## Simulation Basis

The simulator must not be designed around the integration. It must be built firmly around documented SAJ controller behaviour and specifications.
