# Simulator Requirements

Global requirements: [requirements.md](../../.github/work/requirements.md)

## Simulated models

Features: [Simulated models](features.md#simulated-models)

- A completely stand alone docker service that simulates the behaviour of an actual SAJ modbus device.

- This simulator must be able to be configured to simulate different SAJ modbus devices and their behaviours.

- We do not need to completely replicate every detail of the actual hardware, but it's behaviour should be believable and consistent.

## Scenarios

Features: [Scenarios](features.md#scenarios)

- It must be able to be configured in various ways like an actual system (eg: HS3 can have optional EV charger, different size battery banks, dual inverters, off-grid mode etc.)

## Variation

Features: [Variation](features.md#variation)

- Deterministic randomised behaviour to simulate real world conditions (eg: fluctuating solar output that uses known seed values that are reproducible and predictable)

## Control page

Features: [Control page](features.md#control-page)

- Each running simulator offers a web page, served by the simulator itself, that changes the simulated system while it runs, without editing its scenario or restarting it.

- The page can set every setting a client can write, put the device into and out of every fault the model reports, shape the random variation (its bounds, depth, speed and seed), force readings such as power, state of charge and line voltage, and reset counters and the clock.

- The page builds every control from the simulated model's own description, so a new model needs no page of its own. Each raw value is shown with a short name, so the page can be used without the protocol document at hand.

- The page shows the current value of everything it controls, refreshed every few seconds, so a change made from Home Assistant is visible on it.

## State and presets

Features: [State and presets](features.md#state-and-presets)

- Changes made on the page to the simulated system, its link included, are kept across restarts; the traffic record is not. The page can reset the whole simulator or one piece of equipment to its scenario, apply ready-made presets for quick smoke testing, and export the running state as a scenario.

## Register inspector and traffic log

Features: [Register inspector and traffic log](features.md#register-inspector-and-traffic-log)

- The page shows every register the simulated device serves with its raw and decoded value, and every Modbus connection and request the simulator receives with its answer, with request counts and rates per client.

## Link faults

Features: [Link faults](features.md#link-faults)

- The simulator can reproduce the communication failures field reports describe of SAJ communication modules: slow and missing answers, busy and non-standard exception answers, refused register blocks, dropped connections, late duplicate answers, a module that is offline or unresponsive, and a module that locks out a client that polls too hard. They are set in the scenario and on the page, and are deterministic for a seed.

## Code structure

- The page is a development tool: plain HTML, CSS and JavaScript files served as they are, with no libraries, no build step and no tests of its own. Icons may be vendored from a set under the MIT or ISC licence, with its licence beside them. The simulator code behind it is held to the same test rules as the rest of the project.
