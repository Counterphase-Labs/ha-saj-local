# Simulator Features

The simulator is a standalone Docker service that answers Modbus TCP like an SAJ HS3 or H2 inverter, with a web page to watch and steer the simulated system. Developers use it to run the integration without real hardware.

## Simulated models

The simulator serves the registers of one inverter, with energy flows that follow the inverter's settings.

Files: [models.py](../saj_local_mock/models.py), [service.py](../saj_local_mock/service.py), [transport.py](../saj_local_mock/transport.py), [registers.py](../saj_local_mock/registers.py), [device.py](../saj_local_mock/device.py), [hs3.py](../saj_local_mock/profiles/hs3.py), [h2.py](../saj_local_mock/profiles/h2.py), [hs3_equipment.py](../saj_local_mock/profiles/hs3_equipment.py), [h2_extras.py](../saj_local_mock/profiles/h2_extras.py), [undocumented.py](../saj_local_mock/profiles/undocumented.py), [plant.py](../saj_local_mock/simulation/plant.py), [control.py](../saj_local_mock/simulation/control.py)

Requirements: [Simulated models](requirements.md#simulated-models)

- The simulator plays a three-phase HS3 of 5 to 12 kW, or a single-phase H2 of 3 to 6 kW, each reporting its own device type and serial.
- Each simulator answers Modbus TCP reads and writes on its own port and unit ID, and accepts two clients at once by default.
- The simulator serves the registers each model documents. The HS3 also answers a set of undocumented settings registers with fixed values.
- Solar, household load, battery, grid, backup load, meters, EV charger and parallel readings are worked out together, so the readings balance.
- Written settings change what the simulated system does: the self-use, time-of-use, backup and EMS application modes, the time-of-use slots, the battery limits, the export limits and EMS control all steer the energy flows.
- A Docker health check confirms the simulator answers a Modbus read of the device type.
- Commands act on the simulated system: clear fault clears the current faults, restart takes the inverter offline for 30 seconds, clear power history zeroes the energy counters, factory reset returns the settings to the scenario, and set clock moves the simulated clock.
- The HS3 takes up to eight battery modules and one battery pack's faults. The H2 takes up to five battery modules and four packs' faults. The EV charger exists on the HS3 only.

## Scenarios

A scenario file sets up the simulated system: the model, its equipment and how it starts.

Files: [scenario.py](../saj_local_mock/scenario.py), [hs3-full-house.yaml](../scenarios/hs3-full-house.yaml)

Requirements: [Scenarios](requirements.md#scenarios)

- Seven scenarios ship with the simulator: an HS3 with a battery, without a battery, with an EV charger, off grid, and with everything fitted, and an H2 with and without a battery.
- A scenario sets the model, rated power and serial; the Modbus port, unit ID, client limit and page port; the seed, start time and clock speed; whether the grid is connected; the solar strings; and the household load.
- A scenario sets the battery's module count, module capacity and starting state of charge, Meter A and Meter B, the EV charger with its plug-in sessions, and one or two parallel inverters.
- A scenario can also set the variation, faults and link faults the simulator starts with.
- A scenario with a mistake is refused with the key and the reason, for example an unknown key or a value out of range.

## Variation

Readings vary over time in a way that repeats exactly for the same seed.

Files: [environment.py](../saj_local_mock/simulation/environment.py), [telemetry.py](../saj_local_mock/simulation/telemetry.py), [balance.py](../saj_local_mock/simulation/balance.py)

Requirements: [Variation](requirements.md#variation)

- The same seed and start time give the same readings on every run.
- Solar follows the time of day, with a peak scale, slow cloud cover, passing clouds and jitter between strings.
- Household load moves between a base and a peak, with drift and sudden spikes of a set chance, size and length.
- Grid voltage and frequency swing around their nominal values, with an imbalance between phases.
- Every variation setting has bounds, and depth and speed can be changed while the simulator runs.
- The simulated clock can run faster or slower than real time.

## Control page

Each running simulator offers a web page to watch the simulated system and change it.

Files: [panel.py](../saj_local_mock/panel.py), [machine.py](../saj_local_mock/machine.py), [main.js](../static/main.js), [overview.js](../static/views/overview.js), [settings.js](../static/views/settings.js), [faults.js](../static/views/faults.js), [statusbar.js](../static/shared/statusbar.js)

Requirements: [Control page](requirements.md#control-page)

- The overview shows the simulated system's current readings, refreshed every three seconds.
- A status bar shows whether the page reaches the simulator, the module's link state, the connected clients and the simulated time, and can pause, resume or change the speed of the simulated clock.
- The page builds its controls from the simulated model's own description, and shows each raw value with a short name.
- Every writable setting of the model can be set from the page, with a control that fits the setting, and every command can be run.
- Each fault of the inverter, battery packs and EV charger can be switched on and off, and pack fault codes can be set.
- Solar power, household load, grid voltage and grid frequency can be held at a fixed value and released again.
- The battery's state of charge can be set, and an EV can be plugged in with the energy it needs, or unplugged.
- The simulated clock can be moved to a time and its speed changed, and the energy counters can be reset.
- A change the simulator cannot make is refused with the reason, and nothing is changed.

## State and presets

The simulator keeps what was changed on the page, and offers ready-made situations.

Files: [persistence.py](../saj_local_mock/persistence.py), [presets.py](../saj_local_mock/presets.py), [machine.py](../saj_local_mock/machine.py), [scenario.js](../static/views/scenario.js)

Requirements: [State and presets](requirements.md#state-and-presets)

- Changes made on the page survive a restart when a state folder is mounted. A saved state for a different scenario is ignored.
- The whole simulator can be reset to the scenario, which forgets the saved state.
- One part of the page can be reset to the scenario on its own, leaving the settings, battery charge, car, clock and counters as they are.
- Presets set up a situation in one step: clear sky, overcast, high load, low load, unstable grid, grid lost, inverter over temperature, battery empty, battery full, battery too hot to charge, battery pack fault, meter communication lost, EV charging, slow link, flaky link, busy module, module offline and module locked out. Only presets that fit the fitted equipment are offered.
- The running state can be exported as a scenario file.

## Register inspector and traffic log

The page shows what the simulator holds and what clients have asked for.

Files: [registers.js](../static/views/registers.js), [traffic.js](../static/views/traffic.js), [traffic.py](../saj_local_mock/traffic.py), [description.py](../saj_local_mock/description.py)

Requirements: [Register inspector and traffic log](requirements.md#register-inspector-and-traffic-log)

- The register inspector lists every register with its raw words and decoded value, and can be filtered by name or address.
- The traffic log lists every connection and every request, with the answer each got.
- Counts and request rates are shown for all clients and for each client, over the last 10 and 60 seconds and as a 30-minute history.
- The traffic log can be filtered by Modbus function, address range, client and errors only, paused, and cleared.

## Link faults

The simulator reproduces the communication failures of a real communication module.

Files: [link.py](../saj_local_mock/link.py), [link.js](../static/views/link.js), [exceptions.py](../saj_local_mock/exceptions.py)

Requirements: [Link faults](requirements.md#link-faults)

- Answers can be delayed by a set latency and jitter.
- A share of requests can get no answer, a busy exception, a device failure exception or a dropped connection, and a share of answers can arrive twice, late.
- Blocks of registers can be set to be refused with an exception.
- The module can be unresponsive, or offline for a time on a repeating period.
- A lockout stops answering a client that sends too many requests in a time window, for one client or for the whole port.
- Every link fault can be set in the scenario or on the page. The page can also drop every connection at once and reset the module.
