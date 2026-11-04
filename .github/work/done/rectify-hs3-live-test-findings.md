# Rectify HS3 Live Test Findings

## Plan Metadata

- **Revision:** 1
- **Status:** Approved
- **Last revised:** 2026-11-04
- **Requirements:** `.github/work/requirements.md` (Compatibility, Model abstraction, Testing), `custom_components/saj_local/docs/requirements.md` (Devices and entities, Protecting the inverter, Diagnostics and debug logging), `mock/docs/requirements.md` (Simulated models, Scenarios)
- **Code style:** `../code-style.md`
- **Builds on:** [Add Register Catalogue With Full Sensor Coverage](../done/add-register-catalogue-with-full-sensor-coverage.md), [Add Optional Equipment Detection](../done/add-optional-equipment-detection.md)

## Goal

On an HS3, Grid power and Home power show the real grid exchange and the real house load. The EV charger data reads correctly.

## Live Test Findings

The first live test on an HS3 rated at 12000 W, with a CU2-11K-T-I charger, took place on 2026-11-04, with Allow control off. Direct reads ran beside Home Assistant.

- Grid power `0x40A7` equals inverter power `0x40A9` to within 7 W. The grid direction `0x4097` read 0, and the SAJ app showed a grid near 0 W.
- The grid phase power `0x4035`, `0x403C` and `0x4043`, and the grid phase apparent power, equal the inverter phase values.
- The Meter A sum moved between −76 W and +67 W, with changes of sign, and agrees with the SAJ app.
- Load power `0x40A0` equals PV `0x40A5` plus battery `0x40A6` to the watt. It is DC input, not house load.
- On each phase, on-grid output power `0x4090`, `0x4092` and `0x4094` equals inverter phase power plus the Meter A phase import. The sum is the house load.
- The charger data span `0x3024`–`0x30BB` refuses function code 03 with exception 48 and answers function code 04. Function code 04 gave the charger model, firmware, 233 V on each phase, total energy 162.4 kWh as a 32-bit value, and a control pilot raw 122 with no vehicle.
- Every exception code of the unit equals the high byte of the address: 48 for `0x30xx`, 49 for `0x3100`, 75 for `0x4Bxx`.

## Scope

In scope:

- The SAJ library: input register reads, and the HS3 power and EV rows.
- The integration: entity availability and diagnostics that follow from the library change.
- The simulator: the HS3 profile, for the registers in Live Test Findings.
- The feature lists, the user pages that link to the changed feature sections, and the generated entity reference.

## Settled Decisions

- On an HS3, Grid power is the Meter A total with the grid sign. Source: record, the grid sign rule in Devices and entities, and Live Test Findings.
- On an HS3, grid phase power, apparent power, current and power factor come from the matching Meter A phase. Grid phase voltage and frequency stay on the grid phase registers. Source: record, Model abstraction, because the grid phase registers carry inverter values.
- On an HS3 without Meter A, Grid power and the grid phase power, apparent power, current and power factor are not created. Source: record, Model abstraction, because no other proven grid measurement exists.
- On an HS3, Home power is the sum of the three on-grid output phase powers. Source: record, Model abstraction, because `0x40A0` carries DC input and not house load.
- On an HS3, `0x40A0` and `0x40A7` are not read. Source: agent, because neither register has a meaning that a key needs.
- The Meter A entities stay as they are, and Grid load power `0x40AD` stays as it is. Source: agent, because no finding asks for a change.
- On an HS3, the charger data span uses function code 04, with no function code 03 fallback. The charger settings span stays on function code 03. Source: agent, from Live Test Findings.
- A function code 04 request counts against the request budget the same as a function code 03 request. Source: record, Protecting the inverter.
- Control pilot voltage uses a factor of 0.1. Source: agent, because raw 122 with no vehicle gives the IEC 61851 no-vehicle level of 12 V.
- The EV status options stay as the SAJ document gives them. Source: agent, because the one reading, 1 with no vehicle, agrees with the document.
- On the HS3, these EV rows become Verified: serial number, model, software version, hardware version, phase count, minimum power, work mode, status, phase voltages, total energy, remote control, current setpoint and control pilot voltage. The other EV data rows become Responds, unchecked. Source: agent, from Live Test Findings.
- On the HS3, Grid power and Home power become Verified. Source: agent, from Live Test Findings.
- Diagnostics and debug logs name the function code of each request and each refusal. Source: record, Diagnostics and debug logging.
- The HS3 simulator profile serves the registers in Live Test Findings as the real HS3 does. Source: user, question tool, 2026-11-04.
- Entity keys do not change, and no compatibility layer is added. Source: record, Compatibility, before the first beta.

## Work

1. **Input register reads.** The SAJ library reads input registers. Each profile span declares its function code. Narrowing, refusal suspension and health tracking keep a function code 03 result apart from a function code 04 result. Outcome: a planned read of the HS3 charger data span sends function code 04, and every other span sends function code 03.
2. **HS3 EV rows.** The charger data span uses function code 04. Control pilot voltage uses the factor 0.1. The EV rows take the evidence levels in Settled Decisions. Outcome: with the charger fitted, the EV entities have values, and no EV request is refused.
3. **HS3 grid and home power.** Grid power, the grid phase power, apparent power, current and power factor, and Home power use the sources in Settled Decisions. Outcome: on the HS3 profile, Grid power equals the Meter A total with the grid sign, and Home power equals the sum of the on-grid output phase powers.
4. **Simulator.** The HS3 profile serves `0x40A0` as PV plus battery and `0x40A7` as inverter power. The grid phase power and apparent power serve the inverter phase values. On each phase, on-grid output power serves the house load. The charger data span answers function code 04 and refuses function code 03 with exception 48. Outcome: the `mock` and `mock-full-house` systems show a Grid power and a Home power that balance with PV, battery and inverter power.
5. **Documentation.** The integration and simulator feature lists, the user pages that link to the changed sections, and the entity reference from `make docs` describe the new behaviour. Outcome: `make docs-check` passes.

## Errors and Failure Behaviour

- If an HS3 refuses the charger data span with function code 04, the existing refusal handling suspends the EV data rows. The EV settings rows keep working.
- If a Meter A phase read fails, Grid power is unavailable, by the existing rule for combined values.
- If an on-grid output phase read fails, Home power is unavailable, by the existing rule for combined values.

## Data Changes

No stored form changes. The recorder keeps the old Grid power and Home power history of HS3 systems, with the earlier meanings. Before the first beta, a reset of this history is acceptable, and the plan does not migrate the history.

## Compatibility

All changed surfaces are before the first beta (no `1.0.0b1` tag). Changed entity meanings are acceptable, and no compatibility layer is added (Compatibility in `.github/work/requirements.md`).

## Tests and Verification

- Unit tests cover input register reads, the function code of each planned request, and narrowing and suspension for each function code. They also cover the HS3 grid and home sources, the Meter A gating, the control pilot factor, and the simulator answers for each function code.
- `make ci` passes with the 100 % line and branch coverage gate.
- Live check by the main session: on the `mock` and `mock-full-house` systems, Grid power and Home power balance, and the EV entities of `mock-full-house` have values.
- Live check by the main session on the real HS3, with Allow control off: add the entry again, with the EV charger on Automatic. Grid power must follow Meter A and the SAJ app. Home power must equal the on-grid output sum. The EV entities must have values. Remove the entry after the check.
- Physical check by the user: with a vehicle plugged in and then charging, compare EV status, EV power and control pilot voltage with the SAJ app. Expected control pilot levels are 9 V for plugged in and 6 V for charging. If a value differs, this plan gets an amendment.

## Dependencies and Risks

- The EV status values and the duty cycle factor have no reading with a vehicle. The physical check settles them.
- Grid power on an HS3 now depends on Meter A. A Meter A fault removes the grid figure.

## Open Questions

None.

## Revision History

| Revision | Date | Change |
| --- | --- | --- |
| 1 | 2026-11-04 | First draft from the live test on the HS3. |
