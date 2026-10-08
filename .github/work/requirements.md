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

- Entity IDs are fixed by code, never derived from display text: `sensor.saj_<key>`, or `sensor.saj_<prefix>_<key>` when a prefix is set
- Each system has an optional prefix, empty by default
- Prefixes must be unique across systems. Empty counts as a value, so only one system can have no prefix
- A prefix can be added, changed or removed later. The user is warned about the consequences before it is applied
- Changing a prefix renames the entities and must keep their history

### Modbus Mock

- A completely stand alone docker service that simulates the behaviour of an actual SAJ modbus device.
- This simulator must be able to be configured to simulate different SAJ modbus devices and their behaviours.
- It must be able to be configured in various ways like an actual system (eg: HS3 can have optional EV charger, different size battery banks, dual inverters, off-grid mode etc.)
- We do not need to completely replicate every detail of the actual hardware, but it's behaviour should be believable and consistent.
- Deterministic randomised behaviour to simulate real world conditions (eg: fluctuating solar output that uses known seed values that are reproducible and predictable)

## Non Functional

- Backwards compatibility MUST drive architecture decisions. Sensor names must remain stable. Architecture decisions should limit the possibility of being boxed into creating breaking changes.
- **CRITICAL**: While this line is in place, DO NOT create backwards compatibility layers. The integration is not released yet. Breaking changes to address the backwards compatible architecture are acceptable while this line is in place (before release). Build as if it is released.

- In some sense providing an abstraction layer across SAJ systems to ensure consistent sensor names, values, formats etc. In some cases that might mean translating or massaging into a common format.

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