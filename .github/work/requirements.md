# SAJ Integration

High level requirements is to provide a stable integration with wide SAJ support for common household inverter, battery and related equipment.

Development is done with HS3 system for reference

Platform stability and correctness is paramount.

## Functional

### Main Integration

- Integration domain: `saj_local`; display name: **SAJ Local**.

- Convention over configuration. Configuration options carry sensible defaults
- Avoid extensive configuration options that result in pages of complex config flows
- Automatic detection where possible, with override an option. AKA detect system automatically.
- Target both reading and writing of registries. Write requires opt in
- Ability to read only certain sensors or exclude certain sensors
- Ability to configure default sensor update cadence
- Ability to read selected sensors at a higher or lower cadence
- Ability to create one or more different sensor reading cadences
- Use intelligent modbus access that does not put the system in danger of overload, especially AIO3 systems
- Expose UI elements that can be added to lovelace dashboards, including informational and configuration
- Full localisation and internalisation support
- clear and detailed errors with good error handling
- extensive and useful debug dump tools using native HA solutions that are privacy focused

### Entity IDs

- Entity IDs are fixed by code, never derived from display text: `<domain>.saj_<key>`, or `<domain>.saj_<prefix>_<key>` when a prefix is set. `<domain>` is the Home Assistant entity type, for example `sensor.saj_pv_power` or `number.saj_backup_reserve_soc`
- Each system has an optional prefix, empty by default
- Prefixes must be unique across systems. Empty counts as a value, so only one system can have no prefix
- A prefix can be added, changed or removed later. The user is warned about the consequences before it is applied
- Changing a prefix renames the entities and must keep their history

### Writing

- Writing is off for every new system. It is switched on per system, with a warning first
- A system whose model could not be verified is never written to
- Dangerous changes are never made from Home Assistant. Users make them in the SAJ elekeeper app. This covers:
  - Commissioning settings (meter, RS485, battery protocol, network, EV charger link). They are read-only: a wrong value can cut the inverter off from its meter, battery, charger or Home Assistant
  - Actions that cannot be undone (factory reset, clearing energy history). They are not offered
- After a change, the entity shows the value the inverter actually holds
- A failed change says clearly whether the inverter was changed, was not changed, or is in an unknown state
- Changes are rate limited so they cannot overload the inverter
- EMS functions switched on from Home Assistant are kept alive by a heartbeat, every 60 seconds by default and configurable, and are switched off when Home Assistant stops
- Power control (holding the battery, the grid connection point or the inverter at a set power) is offered the same way on every model that can do it: the same entities, in watts. How it is done on the inverter belongs to its model
- Optionally, a power control function can follow a Home Assistant schedule helper the user picks. The integration switches the function on when the schedule turns on and off when it turns off

### Modbus Mock

- A completely stand alone docker service that simulates the behaviour of an actual SAJ modbus device.
- This simulator must be able to be configured to simulate different SAJ modbus devices and their behaviours.
- It must be able to be configured in various ways like an actual system (eg: HS3 can have optional EV charger, different size battery banks, dual inverters, off-grid mode etc.)
- We do not need to completely replicate every detail of the actual hardware, but it's behaviour should be believable and consistent.
- Deterministic randomised behaviour to simulate real world conditions (eg: fluctuating solar output that uses known seed values that are reproducible and predictable)
- Each running simulator offers a simple web page, served by the simulator itself, that changes the simulated system while it runs, without editing its scenario or restarting it.
- The page can set every setting a client can write, put the device into and out of every fault the model reports, shape the random variation (its bounds, depth, speed and seed), force readings such as power, state of charge and line voltage, and reset counters and the clock.
- The page builds every control from the simulated model's own description, so a new model needs no page of its own. Each raw value is shown with a short name, so the page can be used without the protocol document at hand.
- The page shows the current value of everything it controls, refreshed every few seconds, so a change made from Home Assistant is visible on it.
- Changes made on the page are kept across restarts. The page can reset the simulator to its scenario, apply ready-made presets for quick smoke testing, and export the running state as a scenario.
- The page is a development tool: plain HTML and JavaScript with no libraries, no build step and no tests of its own. The simulator code behind it is held to the same test rules as the rest of the project.

## Non Functional

- Backwards compatibility MUST drive architecture decisions. Sensor names must remain stable. Architecture decisions should limit the possibility of being boxed into creating breaking changes.
- **CRITICAL**: While this line is in place, DO NOT create backwards compatibility layers. The integration is not released yet. Breaking changes to address the backwards compatible architecture are acceptable while this line is in place (before release). Build as if it is released.

- The different implementations of SAJ systems form an abstraction layer. There is a single unified interface (entities, controls, Lovelace elements) that does the same thing across all models, as closely as each model allows: consistent names, values, units and behaviour. Where models differ, each model's implementation translates to and from the common form.
- A feature is left out only on a model that lacks the possibility to do it.
- Controls are shared, not built per model. A control such as a state of charge limit, an export limit or EV charging is defined once and offered by every model that can do it. On a model that cannot do it, or where the equipment is not fitted, the control is not shown.

- option to enable debug logging which will provide clear and helpful debug logs rather than spam that creates log fatigue

- There must be a clear separation of concerns between SAJ modbus integration logic and the Home Assistant platform logic. SAJ must be implemented as a stand alone "library" that is included by the integration. The SAJ module MUST NOT contain any Home Assistant specific code and MUST be able to be tested completely isolated from any HA modules, classes, environment or otherwise.
- Despite SAJ being implemented as a stand alone library, it will not be used anywhere else outside of the integration.

- 100% unit test coverage for all lines, statements and paths.
- **CRITICAL**: The 100% coverage MUST come from unit tests alone. Integration tests are NOT an acceptable replacement and MUST NOT count towards the coverage requirement.
- A unit test exercises a single module in isolation through its own public interface, with plain inputs and every collaborating module replaced by a stub, fake or mock. A test is NOT a unit test if it assembles several real modules together, opens a socket or network connection, starts a server, reads fixture or configuration files from the project, depends on real time, or runs a long simulation to reach its assertion.
- Unit tests MUST be fast. A unit test that takes more than a few milliseconds is not a unit test.
- Integration tests MUST ONLY be used as critical path smoke tests, for example: can the service be connected to and does it return a value. They MUST be few, MUST NOT be used to prove application logic or behaviour, and MUST be kept separate from the unit tests.
- noqa or any other inline test or lint bypass is FORBIDDEN in this project. Exceptions can be granted by the user on a case by case basis.
- DO NOT write unit tests that test hard coded values, constants or similar. Tests MUST focus on application logic, behaviour and interactions.
- Development in completely isolated docker environment
- Playwright tests for UI covering only critical paths
- Playwright tests split into 1. fake UI with controlled data 2. actual HA development environment through docker
- All commands for things like building, running, testing, linting, etc are exposed as make targets
- All testing and verification can run in github workflows using the same make targets
- This HACS repository will be the sole repository and must contain all elements of the integration, including the SAJ stand alone library, the actual SAJ integration, any lovelace components and custom dashboards

## Assumptions

- Connecting to multiple different modbus systems can happen
- Users may upgrade, for example from H2 to HS3. Data loss should be minimal and restricted to cases where sensors are incompatible. A if both systems have solar, total PV power should have continuity. If old had battery and new does not, it is reasonable to expect sensors for battery are no longer available.