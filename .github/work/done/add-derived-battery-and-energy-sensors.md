# Add Derived Battery And Energy Sensors

## Plan Metadata

- **Revision:** 1
- **Status:** Approved
- **Last revised:** 2026-11-10
- **Roadmap:** "Derived battery and energy sensors" (Kind Roadmap, Product `saj-local`)
- **Requirements:** `.github/work/requirements.md` (Compatibility, Model abstraction, Language, Testing, Verification), `custom_components/saj_local/docs/requirements.md` (Setup and detection, Devices and entities, Polling, Protecting the inverter, Languages, SAJ library), `frontend/docs/requirements.md` (Elements and setup)
- **Governing entries:** integration requirements, Devices and entities: the estimated time until the battery is full or empty, and the values computed from a system's own readings.
- **Code style:** `../code-style.md`
- **Builds on:** [Add Register Catalogue With Full Sensor Coverage](../done/add-register-catalogue-with-full-sensor-coverage.md), [Add Optional Equipment Detection](../done/add-optional-equipment-detection.md), [Add Lovelace Cards](../done/add-lovelace-cards-and-system-dashboard.md), [Rectify HS3 Live Test Findings](../done/rectify-hs3-live-test-findings.md)

## Goal

Each system shows how long the battery needs to become full or empty, how much energy the battery holds, and four other values that SAJ Local computes from the readings it already has. The estimates stay steady when the household load changes for a short time.

## Scope

In scope:

- Eight new sensors per system on every supported model: battery time to full, battery time to empty, battery stored energy, battery available energy, self-sufficiency today, self-consumption today, solar surplus power and battery round-trip efficiency.
- An estimator in the SAJ library that keeps a smoothed battery power across polls, and gets the battery energy from the model's usable capacity, or from a learned capacity when the model does not give one.
- One row on the battery card for the time estimates.
- Translations in the nine languages, the feature lists, the generated entity reference and the user pages that link to the changed feature sections.

Out of scope:

- Estimates for the whole parallel system. The roadmap item and the request name the system's own battery only.
- A capacity setting entered by the user. The usable capacity of a model and the learned capacity below replace the setting.

## Settled Decisions

- **Smoothed power.** The estimates divide the remaining energy by an exponentially weighted average of battery power, weighted by the time between readings, with a time constant of 10 minutes. Every model behaves the same, and a short load peak does not make the estimate jump. Reason: not every model gives an average battery power, and the latest reading jumps with each load change.
- **Time-weighted average.** The weight of each reading depends on the seconds since the reading before, so the default interval, a polling group and a slow cycle give the same average. Reason: the poll interval differs between users.
- **Average kept in memory only.** A reload or a restart starts the average again from the first reading. Reason: 10 minutes of history returns in 10 minutes.
- **Battery energy by model.** The usable energy of the battery in kWh comes through the model abstraction, and the sensors above the abstraction are the same on every model. A model that gives a usable capacity gives the usable capacity (Ah) times the live battery voltage. A model that does not give a usable capacity uses a learned capacity. No setting exists. Record: the model abstraction rule in the global requirements.
- **Learned capacity.** The learned capacity comes from battery power and the change in state of charge, and needs no reading beyond those two. The model abstraction states for each model if the model gives a usable capacity. Reason: a model can lack a usable capacity reading, and the integration requirements ask for convention over configuration.
- **Two totals.** The learner keeps an energy total in kWh and a state-of-charge total in points for each system. After every poll, the learned capacity is the energy total divided by the state-of-charge total, times 100. Reason: the value exists from the second poll, and becomes more accurate as the totals grow.
- **Energy between two polls.** The energy between two polls is the mean of the two battery power readings times the seconds between the polls, with the sign. Reason: a short change of power direction that does not move the state of charge cancels.
- **Each charge and each discharge.** For each charge and each discharge, the integration adds the latest state of charge minus the first, without the sign, to the state-of-charge total, and the energy of the charge or discharge, without the sign, to the energy total. The charge or discharge in progress counts after every poll. Reason: inside one direction, the 0.01-point rounding of the state of charge occurs only at the two ends, so the error does not grow with the totals.
- **Direction change.** A charge ends at its highest reading, and a discharge ends at its lowest reading. The direction changes only when the state of charge moves 0.1 points or more back from that reading, and the next charge or discharge starts at that reading. Reason: a small back-and-forth movement of the state of charge at rest does not add rounding error.
- **Pairs left out.** When two polls are more than 10 minutes apart, or the state of charge changes by more than 5 points between two polls, the charge or discharge ends at the earlier poll, the pair does not count, and a new one starts at the later poll. Reason: a gap leaves the energy unknown, and a jump shows a recalibration by the battery.
- **No ageing.** The totals never decrease. Reason: battery ageing changes the capacity by a few percent each year, which does not matter to a time estimate.
- **Totals kept.** A store of the config entry keeps, for each system that uses the learned capacity, the two totals and the charge or discharge in progress: its first state of charge, its highest or lowest reading, its energy so far, and the time, battery power and state of charge of the latest poll. The integration saves the store at most once every 10 minutes and when the config entry unloads. After a restart, the next poll continues the charge or discharge in progress, unless the gap rule leaves the pair out. Reason: a restart keeps the learned capacity and loses no charge or discharge, and the save rate keeps disk writes low.
- **Before the first value.** On a system that uses the learned capacity, battery stored energy, battery available energy and the two time estimates are unknown until the state of charge changes between two polls. Reason: no change gives no capacity.
- **Full and empty limits.** Full is the charge state-of-charge limit. Empty is the backup reserve while the application mode is backup. In the other application modes, empty is the on-grid discharge limit. While the operating mode is off grid, empty is the off-grid discharge limit on a model that gives one, and the on-grid discharge limit on a model that does not. Reason: the inverter stops at these limits, the backup reserve applies in backup mode only, and not every model gives an off-grid discharge limit.
- **Presentation.** The time estimates are duration sensors in minutes. Reason: a duration is easy to graph and to compare in automations.
- **When an estimate has no value.** Time to full has a value only while the average power charges the battery. Time to empty has a value only while the average power discharges the battery. Each estimate is unknown when the average power is zero, or when the result is longer than 48 hours. An estimate is 0 when the state of charge is at or past its limit. Reason: a time that grows without limit near zero power has no use, and 48 hours is longer than any daily cycle.
- **Stored and available energy.** Stored energy is the state of charge times the battery energy that the model gives, in kWh. Available energy is the energy above the empty limit, in kWh, and never below 0. Reason: the time to empty already needs both values.
- **Ratios.** Self-sufficiency today is the share of today's load energy that did not come from the grid. Self-consumption today is the share of today's solar energy that was not exported. Round-trip efficiency is total battery discharge energy over total battery charge energy. Each ratio is a percentage from 0 to 100, and is unknown when the divisor is 0. Reason: these are the common definitions of the terms.
- **Solar surplus.** Solar surplus power is solar power minus household load power, in watts, and can be negative. Reason: automations that start loads on excess solar need the value, and a negative value shows the deficit.
- **Default state.** Battery time to full, battery time to empty, battery stored energy and battery available energy are enabled by default. The other four sensors are created disabled. Reason: the battery values are the request, and the others are additions.
- **Equipment.** The four battery sensors and round-trip efficiency belong to the battery and exist only when a battery is fitted. Self-consumption and solar surplus need no battery. Record: the optional equipment rule in the integration feature list, and the model abstraction rule in the global requirements.
- **Readings behind a derived sensor.** An enabled derived sensor makes the integration read every reading the sensor needs, also when the entities of those readings are disabled. The load shown in the polling group and Configure forms counts these reads. Record: integration requirements (Protecting the inverter).
- **Stateless sensors use the existing combined readings.** The ratios and the surplus are computed in each poll from that poll's readings, as the existing combined readings are. The time estimates, the stored energy and the available energy use the estimator. Reason: the existing mechanism already plans the reads.
- **Battery card.** The battery card shows time to full while the battery charges and time to empty while the battery discharges, as one row in the existing reading rows. Reason: users see the estimate without a card of their own.
- **Entity keys.** `battery_time_to_full`, `battery_time_to_empty`, `battery_stored_energy`, `battery_available_energy`, `self_sufficiency_today`, `self_consumption_today`, `solar_surplus_power` and `battery_round_trip_efficiency`. Reason: the names follow the existing key pattern and are frozen at `1.0.0`.

## Work

1. **SAJ library: combined values.** The catalogue gains the operations that the stateless sensors need: difference and share as a percentage. The two ratios of today, round-trip efficiency and solar surplus are combined readings on every model that gives their inputs. Outcome: unit tests show each value from plain inputs, the unknown cases and the bounds.
2. **SAJ library: battery estimator.** A new module keeps the smoothed battery power for each system, and gives stored energy, available energy, time to full and time to empty from one poll's readings, the battery energy and the reading time. The model abstraction says if a model gives a usable capacity. A model that gives one uses the usable capacity and battery voltage. A model that does not give one uses a learner that keeps the two totals and the charge or discharge in progress, and takes and gives the stored totals. The module has no Home Assistant code. Outcome: unit tests cover the weighting by time, the first reading, a direction change, zero power, the 48-hour bound, the limit rules for each application mode and off grid, a missing input, the battery energy from a usable capacity, and for the learner the value after two polls, the 15-minute and 5-minute examples below, a charge then a discharge, a back-and-forth movement below 0.1 points, a gap, a jump, a restart in the middle of a charge, and a restart after a crash with a gap below and above 10 minutes.
3. **Integration: sensors and store.** For each system that uses the learned capacity, the coordinator loads the stored totals at start and saves the totals by the save rule. For every system, the coordinator feeds the estimator after each poll that reads battery power. Removal of the config entry removes the store. The eight sensors exist with the device classes, units and state classes in the decisions, and with the equipment and default rules. Outcome: unit tests for the sensor values, the unknown state, the equipment rule, the store load and save, and the removal. `make freeze-check` passes.
4. **Translations.** The eight entity names exist in all nine languages. Outcome: `make docs-check` passes.
5. **Battery card.** The battery card shows the time row by the battery direction, hidden when the system has no estimate entity. Outcome: card unit tests for charge, discharge, idle and a missing entity. The existing Playwright battery card test still passes.
6. **Simulator.** In every model simulator, the state of charge changes by battery power and a fixed battery energy, and the limits have believable values. Each simulator serves the capacity readings that its real model gives: a usable capacity that agrees with the fixed battery energy, or 0 where the real model reads 0. Outcome: the development Home Assistant shows both estimates against each simulator, and learns a capacity near the fixed battery energy against each simulator without a usable capacity.
7. **Documentation.** `make docs` regenerates the entity reference. The integration and card feature lists and the user pages that link to the changed sections describe the new sensors and the card row. Outcome: `make docs-check` passes.

## Errors and Failure Behaviour

- A reading the estimator needs is unavailable or refused: the estimates, the stored energy and the available energy are unavailable for that poll. The smoothed power keeps its value.
- No change of state of charge yet on a system that uses the learned capacity, or usable capacity or battery voltage reads 0 on a model that gives a usable capacity: the battery energy sensors and the estimates are unknown, not 0.
- A failed poll: the estimator gets no reading. The next good reading weights by the full time since the last good reading. For the learner, a gap longer than 10 minutes is a pair left out.
- The store cannot be read or holds a version the integration does not know: the integration logs a warning and starts with empty totals.
- The store cannot be written: the integration logs a warning and keeps the totals in memory.
- The battery power reading is refused three times and suspended: the estimates stay unavailable until the reading returns.

## Data Changes

- A new store for each config entry holds the energy total, the state-of-charge total and the charge or discharge in progress of each system that uses the learned capacity, at store version 1.
- No existing stored form changes, so no backup and no migration are necessary. The config entry version and the power control store stay the same.
- Removal of the config entry removes the new store, as removal does for the power control store today.
- The smoothed power is not stored.

## Compatibility

- Entities: beta (`1.0.0b1`). The work only adds entity keys, so nothing breaks. The release notes of the next beta name the eight new entities and the card row.
- Battery card settings: no change.

## Tests and Verification

- Unit tests for every new behaviour in steps 1 to 3 and 5, with 100 % line and branch coverage.
- `make ci`.
- Unit tests for the learner use two examples. A charge from 40.94 % to 44.79 % at a constant 4990 W for 15 minutes gives 32.40 kWh. A charge from 40.94 % to 42.21 % at a constant 4990 W for 5 minutes gives 32.74 kWh.
- In the development environment, both estimates move steadily against each simulator while the simulated load changes.

## Dependencies and Risks

- Model facts today: on a real HS3, 0xA001 and 0xA00A read 0, and the HS3 protocol document does not list them, so the HS3 model states no usable capacity. H2 field tooling reads both registers, so the H2 model states a usable capacity, but no H2 value is recorded. A reading from a real H2 must show that usable capacity covers all packs.
- The first values of the learned capacity have a large error: about ±4 % after 0.26 points, ±1 % after 1 point and ±0.1 % after 10 points of state of charge.
- Battery power is measured at the battery, so a charge gives a slightly larger value than a discharge. Both directions in the totals reduce the error.
- After an added battery pack, the old totals keep the learned capacity too low until enough new charge and discharge adds to the totals.
- The empty rule is not proven on a real device. A real device test must show that discharge stops at the backup reserve in backup mode and at the on-grid limit in the other modes.
- A model without an off-grid discharge limit uses the on-grid limit while off grid. Today the HS3 is such a model, and a real device test must show where an off-grid HS3 stops.
- A battery charges slower near full. Time to full is too short in the last part of a charge.
- The estimates update only as fast as battery power is polled.

## Open Questions

None.

## Revision History

| Revision | Date | Change |
| --- | --- | --- |
| 1 | 2026-11-10 | First draft. |
