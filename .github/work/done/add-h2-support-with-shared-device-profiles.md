# Add H2 Support With Shared Device Profiles

## Plan Metadata

- **Revision:** 5
- **Status:** Approved
- **Last revised:** 2026-10-07
- **Requirements:** `../requirements.md`
- **Code style:** `../code-style.md`
- **Builds on:** `../future/implement-hs3-read-only-integration.md`. Everything in that plan that is not restated here continues to apply to both models.

## Outcome And Scope

SAJ Local reads an H2 at the same level as an HS3: the same six read-only sensors, the same polling, availability, diagnostics and logging behaviour. The model is detected from the device by default. A model field, defaulting to **Automatic**, lets the user override detection; a wrong selection is rejected and an unverifiable one must be confirmed. An installation can be moved from one model to the other through Configure and keeps its device, entities, names and history.

The library is restructured so that both models run through one implementation. A model is a declaration, not a code path.

Included:

- A model-neutral SAJ library: one identity reader, one telemetry reader and decoder, a small table of device profiles, one model-resolution function and one module of model errors. The HS3-specific module and types are removed.
- H2 profile, automatic detection, and the model override with its verification, errors and confirmation.
- Replacement across models (H2 to HS3 and HS3 to H2) with unchanged installation, device and entity identities.
- One validation path shared by initial setup and Configure.
- Model-neutral user-facing text wherever it currently names HS3.
- A browser tier reduced to load-and-function smoke for both models, as the requirements define it.

Deferred, unchanged from the HS3 plan: register writes, energy counters, faults, optional equipment, per-pack battery data, multiple cadences, include/exclude UI and custom frontend behaviour. Also deferred: dedicated profiles for AS2, HS2 and other H2 variants, and any sensor that exists on only one model.

## H2 Protocol Contract

The H2 contract comes from SAJ protocol documentation for the single-phase H2, cross-checked against field observations from H2-family and HS3 units. It has not been hand-verified on an H2 by this project; the HS3 contract has. Each profile declares which of the two applies, and diagnostics and the README report it.

### Connection And Framing

Identical to HS3: Modbus TCP, function `0x03`, wire addresses without offset, big-endian words, exception responses as function `0x83` with the code preserved. H2 documents exception codes `0x01`, `0x02`, `0x03`, `0x04`, `0x06`, `0x10`, `0x11`, `0x12` and `0x13`; the client already preserves any code and needs no change.

### Identity

| Meaning | Address | Width | Encoding |
| --- | --- | --- | --- |
| Device type | `0x8F00` | 1 word | Unsigned 16-bit |
| Rated power | `0x8F01` | 1 word | Unsigned 16-bit, W |
| Serial number | `0x8F03` | 10 words | 20-byte string; zero is invalid |

Same addresses, widths, serial rules and read sequence as HS3: type and rating together, then the serial, never `0x8F02`.

`0x8F01` is documented for H2 only as the "power section". It is rated power in W across the family: HS3 units report 12000 and 10000 for the 12 kW and 10 kW models, an 8 kW H2 reports 8000, and existing H2-family tooling uses the value directly as rated watts. Both profiles therefore treat it as W.

Device types:

| Type | Model | Automatic detection |
| --- | --- | --- |
| `0x1610` | HS3 | HS3 (hand-verified) |
| `0x005A` | H2 single-phase hybrid, 3–6 kW, two MPPT | H2 (documented) |
| `0x005B` | H2 single-phase hybrid, 5–10 kW, three MPPT | H2 (documented) |
| `0x0055`, `0x0056` | AS2 AC-coupled | Not recognised |
| `0x005C`, `0x005D` | HS2 all-in-one | Not recognised |
| anything else | — | Not recognised |

The documented type table is credible: a fielded HS2 has been observed reporting `0x005C`, exactly as listed. It is also incomplete: H2-family units exist that report types outside it, the three-phase 8 kW and 10 kW H2 among them. Automatic detection therefore covers only the listed codes, and the model override exists for the rest. Detection never uses a serial prefix, register probing or a simulator constant.

### Sensors

All six semantic keys exist on H2 at the same addresses with the same encodings as HS3:

| Semantic key | Address | Encoding | Scale | Unit | H2 documentation |
| --- | --- | --- | --- | --- | --- |
| `operating_mode` | `0x4004` | Unsigned 16-bit enumeration | 1 | None | Values 0–9 with the same meanings as HS3 |
| `battery_soc` | `0x406F` | Unsigned 16-bit | 0.01 | % | Battery energy percent |
| `load_power` | `0x40A0` | Signed 16-bit | 1 | W | Total system load |
| `pv_power` | `0x40A5` | Signed 16-bit | 1 | W | Total PV power |
| `battery_power` | `0x40A6` | Signed 16-bit | 1 | W | Above zero discharging, below zero charging |
| `grid_power` | `0x40A7` | Signed 16-bit | 1 | W | Total grid real power; sign not documented |

Read ranges, range splitting for disabled sensors, the out-of-range charge rule and unknown-mode handling are identical to HS3. `0x40A0`–`0x40AD` is fully documented on H2, but the read plan stays as it is: one shared plan is worth more than saving a request.

### Grid Power Sign

The sign of `0x40A7` is undocumented on both models and published unmodified under `grid_power`. Field observations agree across the two: on an HS3 it tracked the inverter's AC output (positive while PV exceeded battery charging), and on an H2 it read positive while the battery alone supplied the house and slightly negative while the house ran from the grid with the battery idle. On both it behaves as power at the inverter's grid-side port, positive out of the inverter, not as utility-meter import or export. That is enough to expect continuous history across an H2/HS3 replacement and not enough to label import or export; no such labelling is added here.

## Implementation Design

### SAJ Library

Replace `saj/hs3.py` with five model-neutral modules. Nothing named after a model remains in the library's public surface.

| Module | Responsibility |
| --- | --- |
| `saj/profiles.py` | The `Profile` declaration, the supported profiles, and model resolution. A profile states its key, display name, recognised device type codes, the semantic keys it supports and whether its contract is hand-verified. |
| `saj/device.py` | `Device` (serial, raw device type, rated power in W, effective profile, and whether the profile was detected or assumed) and `identify`. Reads the shared identity registers, validates the serial and resolves the profile for a given model selection. |
| `saj/telemetry.py` | `Telemetry`, the measurement declarations (key, address, decoder), read-range planning and decoding. Reads only the keys that are both enabled and supported by the device's profile. Owns the operating-mode names. |
| `saj/errors.py` | The model errors raised by resolution: unsupported device, model mismatch and unknown model, under one common base. Kept apart from `profiles.py` so that an import rule can restrict who handles them. |
| `saj/device_type.py` | The one textual form of a raw device type, shared by error messages and user-facing text. |

Model resolution is one pure function taking the reported device type and the model selection (automatic or a profile key):

| Selection | Reported type | Result |
| --- | --- | --- |
| Automatic | Recognised | That profile, detected |
| Automatic | Not recognised | Unsupported-device error carrying the raw type |
| A profile | Recognised as that profile | That profile, detected |
| A profile | Recognised as a different profile | Model-mismatch error carrying the selected and detected profiles |
| A profile | Not recognised | That profile, assumed |
| Not Automatic and not a known profile | Any | Unknown-model error carrying the selection |

Rules:

- One implementation serves every profile. Adding a model with the same registers must be a new `Profile` value and nothing else. A profile-specific branch (`if profile is H2`) anywhere in the library or the integration is a defect.
- Measurements are declared once and shared. A profile selects from them by key; it does not redeclare addresses. When a future model needs a different address or decoder for an existing key, that is the point to let a profile supply its own measurement, not before.
- A recognised device type is authoritative. No selection can make the library treat a recognised device as another model.
- No Home Assistant import, no simulator import, no per-model module, no plugin or registration mechanism. `saj/__init__.py` exports the neutral names only and does not export the model errors, so they can be reached only through `saj/errors.py`.

### Model Selection, Verification And Confirmation

Setup and Configure both gain one field, **Model**, as a translated dropdown: **Automatic** (default), then one option per profile. The forms are otherwise unchanged: host, port, unit ID, polling interval, model. The selection is stored in config-entry data with the connection settings; the detected model is never stored and is derived from the device on every identification.

Every submission of either form runs the same validation: normalise input, check ownership, identify with the submitted selection, read the required telemetry, then act on the outcome.

| Outcome | Behaviour |
| --- | --- |
| Profile detected | Continue. |
| Unsupported device (Automatic, unrecognised type) | Form error on the model field stating the reported type and that a model can be chosen manually. Nothing is saved. |
| Model mismatch (selection contradicts a recognised type) | Form error on the model field naming the detected model and telling the user to choose it or Automatic. Nothing is saved. There is no way to confirm past this. |
| Profile assumed (selection applied to an unrecognised type) and required telemetry reads succeed | Confirmation step naming the selected model and the reported type, warning that the device could not be verified as that model and readings may be wrong. Saved only on confirmation. |
| Profile assumed and a required read is rejected or undecodable | The existing read-rejected or invalid-data error. Nothing is saved. |
| Unknown model (the selection is not Automatic or a known profile) | Form error on the model field. Nothing is saved. |

The telemetry read is the verification available for an assumed profile: every register the profile needs must answer. A register that answers with an out-of-range value is not a verification failure; it is an unknown reading for that sensor, exactly as on a detected profile. Confirmation is required in addition because a successful read proves the registers exist, not that they mean the same thing.

In Configure, model confirmation and the existing hardware-replacement confirmation are separate steps. When both apply, model confirmation comes first and replacement second; cancelling either leaves saved and running state untouched, and ownership is rechecked before the final save as today.

At entry load and on reconnect, `identify` runs with the stored selection. An unsupported device, a model mismatch or an unknown model is a translated entry error naming the reported type, the detected model or the stored selection. An assumed profile loads without prompting, because it was confirmed when saved; any change of serial still goes back through Configure and its confirmations.

### Integration

- **Types.** `SajRuntimeData`, `SajCoordinator`, the config flow, sensors and diagnostics use `Device` and `Telemetry`. No module outside `saj/` references a specific model; the model dropdown is built from the library's profile list.
- **Shared validation.** Initial setup and Configure call one validation routine that returns the device and the outcome above. The two flows differ only in what they do with a success: create an entry, or update one (with replacement confirmation when the serial differs). The duplicated normalise-validate-check sequences in the two flows are removed.
- **Identity checks.** Entry load and reconnect compare the detected serial with the approved serial exactly as today. A different serial is an identity mismatch regardless of model.
- **Entities.** The sensor platform creates one entity per semantic key supported by the effective profile. Both profiles support all six, so every installation has the same six entities with the same unique IDs (`{entry_id}_{key}`) and the same `sensor.saj_*` IDs. No entity removal or migration code is added, because no key differs between the supported profiles.
- **Error mapping.** One integration module, `errors.py`, turns library errors into a translation key and placeholders: the three model errors, invalid device data, and the timeout, read-rejected and cannot-connect classification of communication errors. The config flow, entry load and the coordinator all call it and keep only their own decision: which form field the error attaches to, which entry exception to raise, and the update failure. A model error without a mapping fails loudly instead of being reported as a connection problem. An import-linter contract allows only this module to import `saj/errors.py`, so a second place that handles model errors fails lint.
- **Device metadata.** Model is the profile display name with the rated power, marked as unverified when the profile was assumed. Serial, model and rated power are refreshed from the device on every load through native device registration.
- **Diagnostics.** Report the model selection, the effective profile key, whether it was detected or assumed, whether its contract is hand-verified, the raw device type and rated power in W. The structured last error keeps a model error's own message, so the reported type, detected model or stored selection is not lost. Everything else is unchanged, including redaction.
- **Translations.** Remove HS3 from every string that applies to both models: the setup title, the read-rejected error and the replacement confirmation, which now names the model and serial being adopted and makes no claim about a fixed number of sensors. Add the model field label, its options, the unsupported-device and model-mismatch errors with placeholders, the model confirmation step, and the matching entry-load exceptions.

### Switching Between Models

1. The user opens Configure and submits. The endpoint may be new or unchanged; with Model on Automatic nothing else needs changing.
2. Validation identifies the device. A serial different from the approved one triggers the replacement confirmation, naming the detected model and serial.
3. On confirmation the entry keeps its ID; the approved serial, connection settings and model selection are saved; the entry reloads once with the new model.

If the saved selection names the old model explicitly, step 2 reports a model mismatch naming the new model, and the user corrects the dropdown in the same form.

Because installation, device and entity identities come from the config-entry ID and the semantic key, and both models expose the same six keys, an H2-to-HS3 or HS3-to-H2 replacement changes no entity ID, unique ID, user-assigned name, disabled state or history identity. Only device metadata changes. This is the guarantee the HS3 plan gives for HS3-to-HS3, extended across models without additional machinery.

### What Is Removed

- `saj/hs3.py`, `Hs3Device`, `Hs3Telemetry`, `decode_hs3`, `HS3_DEVICE_TYPE` and the hard-coded `"HS3"` strings in sensors and diagnostics.
- `SENSOR_KEYS` in `const.py`; the profile is the source of supported keys.
- The separate validation sequences in the setup and options flows.
- `tests/saj/test_hs3.py`, replaced by per-module tests.

Nothing is aliased, re-exported under an old name or kept for an earlier layout. Existing development entries that lack the model field are not migrated or defaulted; they are recreated or corrected by hand.

## Verification And Acceptance

The unit-test rules of the requirements and the HS3 plan apply unchanged: 100% line and branch coverage from isolated unit tests, one module per test through its public interface, collaborators replaced, no sockets, files, real time or constant-restating assertions.

Cover:

- **Profiles.** The full resolution table above as one multivariate test, including the data carried by each error.
- **Device.** Identity decoding, serial validation, the read sequence, and propagation of selection, detected-or-assumed state and resolution errors, with the client and profile resolution replaced.
- **Telemetry.** Decoding, range planning and enabled/supported key selection, driven by measurement declarations supplied by the test rather than by the production tables.
- **Coordinator, entry lifecycle, sensors, diagnostics.** Existing behaviour re-expressed against the neutral types and parametrised over both profiles where the profile affects the outcome; entry load with a stored explicit selection for detected, assumed, mismatched and unsupported devices.
- **Config flow.** Setup of an H2 and of an HS3 on Automatic through the same path; every row of the outcome table in both setup and Configure; model confirmation accepted and cancelled; model confirmation followed by replacement confirmation; cross-model replacement in both directions; error placeholders; no saved-state change on any error or cancellation.
- **Error mapping.** Every mapped error with its key and placeholders as one multivariate test, and the loud failure for an unmapped model error. Tests of the config flow, entry load and coordinator replace the mapping and prove only how each applies its result.
- **Import boundary.** The library still imports without Home Assistant.

### Browser Tier

The requirements limit integration tests to critical-path smoke: can it be connected to and does it return a value. They must be few and must not prove application logic. Unit tests cover every behaviour in this plan; the browser proves only that the integration loads and functions in a real Home Assistant.

The browser tier is therefore exactly this, for each of the two simulators (the existing HS3 battery scenario and the existing H2 battery scenario):

1. Add the endpoint through the setup form with Model left on Automatic.
2. The entry loads.
3. Its sensors report values.

Nothing else is asserted in the browser. In particular: no error paths, no Configure edits, no replacement, no model override, no registry, identity, name or history comparisons, no disable or re-enable checks, no read counting and no assertions on simulated values.

This replaces the browser section of `implement-hs3-read-only-integration.md`, which asked for lifecycle, replacement, identity, history and read-omission checks in the browser and does not meet the requirement. Those checks are removed from the browser test; each is already covered by unit tests. The request-recording proxy and its serial and endpoint controls exist only to serve the removed checks and are removed with them; Home Assistant talks to the simulators directly. The per-test timeout returns to its previous value. The simulator is not changed by this plan and remains outside protocol authority.

Acceptance requires:

1. With Model on Automatic, adding an H2 endpoint and adding an HS3 endpoint both succeed through the same form, and each creates one device with six `sensor.saj_*` entities.
2. Setup and Configure show the same five fields, with Model defaulting to Automatic on setup and to the saved selection in Configure.
3. A selection that contradicts a recognised device is rejected with an error naming the detected model, in setup, Configure and at entry load, and cannot be confirmed past.
4. A selection applied to an unrecognised device type is saved only after its required reads succeed and the user confirms; Automatic against an unrecognised type is rejected with an error that states the reported type and points to manual selection.
5. Device metadata and diagnostics show the effective model and whether it was detected or assumed; no user-facing text names a model other than the one in effect.
6. H2-to-HS3 and HS3-to-H2 replacement through Configure, proven by unit tests, keeps the config entry, device registry entry, entity registry entries, entity IDs, unique IDs, user-assigned names, disabled state and history. Only hardware metadata, the approved serial and the saved settings change.
7. No module outside `saj/profiles.py` names a model, no code branches on a specific profile, and setup and Configure share one validation routine.
8. No alias, shim, alternate identity format, entry migration or fallback lookup exists anywhere in the change.
9. `make ci` passes, including lint, the duplicate-code gate, the coverage gate, import boundaries and the browser smoke.
10. README support matrix and limitations, and `documentation/development.md`, describe H2 at the delivered level, the model field, and that the H2 contract is documented and field-observed rather than hand-verified.
11. The browser tier contains only the load-and-function smoke described above, for an HS3 and an H2 endpoint, and no test-only proxy or control service remains.
12. A stored or submitted model selection that is neither Automatic nor a known profile produces a translated error, never an unhandled exception.
13. Library errors are translated in one integration module, and lint fails when any other integration module imports the library's model errors.

## Work Sequence

1. Restructure the library into `profiles`, `device` and `telemetry` with HS3 as the only profile and model resolution in place; move and rewrite its unit tests.
2. Move the integration onto the neutral types; remove every model name outside `saj/profiles.py`; update unit tests.
3. Add the H2 profile; extend the multivariate tests to both profiles.
4. Extract the shared validation routine; add the model field, its errors and the model confirmation step to setup and Configure; store and apply the selection at entry load and reconnect.
5. Make translations and the replacement confirmation model-neutral; update diagnostics.
6. Reduce the browser tier to the load-and-function smoke for the HS3 and H2 endpoints and remove the recording proxy.
7. Update README and development documentation.
8. Verify with `make ci` until the whole gate passes, without touching the git index or history.

## Revisions

| Revision | Date | What changed |
| --- | --- | --- |
| 1 | 2026-10-06 | Initial draft: model-neutral library with declared profiles, H2 at HS3 level through shared code, automatic detection, and cross-model replacement through the existing Configure flow. |
| 2 | 2026-10-06 | At the user's direction, added the model override: a Model field defaulting to Automatic in setup and Configure, rejection of a selection that contradicts a recognised device, and confirmation for a selection applied to an unrecognised type. Settled from field evidence that `0x8F01` is rated power in W on H2, that both documented H2 type codes are detected, and that the grid power sign agrees across models. Setup and Configure now share one validation routine. Open decisions removed. |
| 3 | 2026-10-07 | At the user's direction, brought the browser tier in line with the requirements: load-and-function smoke only for an HS3 and an H2 endpoint, replacing the earlier plan's browser lifecycle checks and removing the recording proxy. Added a translated error for an unknown model selection. |
| 4 | 2026-10-07 | At the user's direction, status set to Approved and the plan moved to completed work. No change to scope or design. |
| 5 | 2026-10-07 | At the user's direction after review of the implementation: library errors are translated in one integration module, enforced by an import contract, which moves the model errors into `saj/errors.py` and the device-type text form into `saj/device_type.py`; device metadata marks an assumed profile as unverified; diagnostics keep a model error's message; device tests replace profile resolution. Clarified that an out-of-range value during verification of an assumed profile is an unknown reading, not a rejection, after the stricter check was judged over-engineered. Status and location unchanged. |
