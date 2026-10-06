# Implement HS3 Read-Only Integration

## Plan Metadata

- **Revision:** 5
- **Status:** Draft — awaiting implementation approval
- **Last revised:** 2026-10-06
- **Requirements:** `../requirements.md`
- **Code style:** `../code-style.md`
- **Scope record:** The user authorised implementation and subsequent remediation. On 2026-10-06 the user explicitly instructed revision 3 and its implementation: polling interval during setup, editable connection settings, and HS3 replacement with no impact on historical data. The user subsequently instructed revision 4 and implementation of model-neutral naming by a new agent, then instructed revision 5's simplification through an agent: one Configure form, validation on every submission, and no replacement checkbox or separate interval-only editing mode. The recorded status and document location remain unchanged because no status change or move was requested.

## Outcome And Scope

Make SAJ Local usable in the isolated Docker development environment: add an HS3 endpoint through Home Assistant, identify the device, and display six read-only sensors that update and recover from communication failures.

HS3 is the first supported profile because the requirements name it as the development reference. This iteration establishes communication, decoding and Home Assistant lifecycle behavior without implementing the full product roadmap.

Included:

- Endpoint configuration and editing, serial-based duplicate prevention, and independent entries for multiple systems.
- Explicit HS3 replacement within an existing installation, preserving every sensor's identity and historical data even when the hardware serial changes.
- Identity and six telemetry sensors, with consistent semantic keys rather than protocol variable names.
- One polling interval configurable during initial setup and subsequent editing, sequential requests, explicit availability and recovery behavior.
- Native Home Assistant entities, translated user-facing text, native redacted diagnostics and useful debug logging.
- Isolated unit coverage and a small Docker browser smoke test against the existing simulator.

Deferred: H2 and other models, register writes, energy counters, detailed faults, optional equipment discovery, individual battery packs, parallel-system aggregation, multiple sensor cadences, an explicit include/exclude configuration UI, and custom frontend functionality. This is an incremental delivery of the requirements, not a replacement of them. Standard Home Assistant entity disabling provides the initial sensor selection mechanism.

## HS3 Protocol And Register Contract

The register meanings below follow hand-verified behavior. They are the implementation contract for this iteration and are included directly so development needs no external documents. Unverified interpretations must not replace them.

### Connection And Framing

- Modbus TCP; inverter is the server. Setup defaults are port **502** and unit ID **1**. Use one connection per configured endpoint and one outstanding request at a time.
- Use function **0x03** to read holding registers. All addresses below are the hexadecimal addresses sent on the wire, without a one-based offset.
- The MBAP header carries a two-byte transaction identifier, two-byte protocol identifier fixed to zero, two-byte length including the unit identifier and following PDU, and one-byte unit identifier. Responses must match the request transaction, unit and function.
- Each register contains two bytes, high byte first. The response byte count must equal twice the requested register count; truncated, mismatched or malformed responses are failures, not measurements.
- Exception responses set the function's high bit, producing **0x83** for a read. Preserve the received exception code in the library error and diagnostics. Handle invalid address **0x02**, illegal data **0x03**, server error **0x04**, and server busy **0x06** without losing other codes. Do not assume every exception uses a standard code.
- No write function is exposed or sent. Do not read settings, EMS targets or unrelated blocks as part of detection or polling.

### Identity

| Meaning | Address | Width | Encoding and meaning |
| --- | --- | --- | --- |
| Device type | `0x8F00` | 1 word | Unsigned 16-bit. HS3 type **5648 (`0x1610`)** is verified. |
| Rated power | `0x8F01` | 1 word | Unsigned 16-bit, W. Represents current maximum rated power. |
| Serial number | `0x8F03` | 10 words | 20-byte string; zero is invalid. |

Read type and rating together, then the serial separately; do not read the undocumented intervening `0x8F02`. Remove terminal zero padding from the serial, reject an empty or invalid identifier, and reject undecodable text rather than inventing an identity. Include the detected model and rated power in W in device metadata and diagnostics.

Detect **HS3** from the verified type **`0x1610`**, then validate its identity and required telemetry before creating the entry. An unsupported type produces a translated unsupported-device error; do not guess from a serial prefix, a successful generic read or a simulator constant. This iteration recognises this verified type only and does not claim support for every SAJ model.

### Sensors

| Semantic key | Display name | Address | Encoding | Scale | Unit |
| --- | --- | --- | --- | --- | --- |
| `operating_mode` | Operating mode | `0x4004` | Unsigned 16-bit enumeration | 1 | None |
| `pv_power` | Solar power | `0x40A5` | Signed 16-bit | 1 | W |
| `battery_power` | Battery power | `0x40A6` | Signed 16-bit | 1 | W |
| `battery_soc` | Battery charge | `0x406F` | Unsigned 16-bit | 0.01 | % |
| `grid_power` | Grid power | `0x40A7` | Signed 16-bit | 1 | W |
| `load_power` | Household load | `0x40A0` | Signed 16-bit | 1 | W |

Battery charge is a percentage: raw **10000 means 100%**. A value outside 0–100% is invalid; do not clamp it into an apparently valid measurement. Decode signed values using 16-bit two's complement.

For battery power, positive means discharge and negative means charge. Preserve the signed reading without adding separate directional entities. `0x40A7` is total measured grid power; retain its device-defined sign without assigning import/export labels. `0x40AD` is a separate grid-supplied load reading and must not be substituted for total measured grid power. The confirmed import-positive/export-negative convention of the Meter A phase sum must not be transferred to `0x40A7`. Meter-derived grid sensors remain outside this iteration.

Operating mode values:

| Value | Meaning |
| --- | --- |
| 0 | Initialisation |
| 1 | Standby |
| 2 | Operating |
| 3 | Off-grid |
| 4 | Grid-connected load / bypass |
| 5 | Fault |
| 6 | Upgrade |
| 7 | Debugging |
| 8 | Self-check |
| 9 | Reset |

Preserve an unrecognised mode code in diagnostics and expose an unknown sensor state; it must not crash the update or become a known mode by default.

## Implementation Design

### SAJ Library

Implement a narrow asynchronous read-only TCP client and HS3 decoding inside `custom_components/saj_local/saj/`. Keep transport framing separate from device interpretation so each can be tested with its collaborator replaced. Use plain typed identity and telemetry values at the boundary. Add modules only for these concrete responsibilities; no generic profile registry, equipment tree, transport abstraction framework or separately distributed package.

The client owns its connection, bounded request timeout, response validation and cleanup. HS3 logic owns addresses, decoding and the bounded reads. Neither imports Home Assistant or simulator code. Do not reuse the simulator's register definitions, framing helpers, models or fixtures.

### Setup And Lifecycle

- Initial setup must show host, port, unit ID and polling interval together. Default port to 502, unit ID to 1 and polling interval to 30 seconds. Permit integer unit IDs 1–247, reject broadcast zero, and require an integer polling interval of at least 30 seconds. Connection numbers and interval use native numeric entry boxes, not sliders. Detect the supported HS3 profile from the returned device type; no model selector is needed for this iteration.
- Use translated field labels and errors for invalid input, connection failure, timeout, rejected read and invalid identity/data and unsupported device type. Do not present raw exception text as the sole explanation.
- Validate identity and an initial telemetry read before creating the entry. Always close temporary validation connections, including on failure or cancellation.
- Separate installation identity from hardware identity. The existing config-entry ID identifies the logical installation and remains unchanged for its lifetime. Use that ID as the native device identifier and combine it with each semantic sensor key for entity unique IDs; neither the hardware serial nor connection settings may determine those identifiers. Keep the current validated hardware serial as the config-entry unique ID for serial-based duplicate detection and as device metadata. Prevent duplicate serials and duplicate host/port/unit endpoints. Separate entries must have separate clients, coordinators and state.
- Default installation and sensor naming must be model-neutral from the first setup. Use **SAJ** as the default native device name and **SAJ {serial}** as the initial config-entry title. With the existing translated sensor names, a fresh installation must produce entity IDs such as `sensor.saj_solar_power`, `sensor.saj_battery_power` and `sensor.saj_grid_power`, never `sensor.saj_hs3_*`. Keep the current model and rated power in device metadata; supported-profile instructions and errors may still identify HS3. Do not put a model, rated power, endpoint or hardware serial into the default device name or sensor naming prefix. Native Home Assistant collision suffixes for separate installations are acceptable.
- A system change must not rename compatible sensors, recompute entity IDs or replace registry records. Existing entity IDs, user-assigned names, device customisations and history remain attached to the logical installation; the default naming scheme must not require renaming when support for another model is added. H2 implementation remains outside this iteration.
- During entry setup, obtain fresh identity and initial data and compare the detected serial with the currently approved hardware serial. A temporarily unreachable device causes Home Assistant's setup retry behavior rather than a loaded entry with fabricated values. An unexpected different serial during setup or background polling remains an error; only the explicit editing and replacement workflow below may approve a new hardware serial.
- Store per-entry runtime state through Home Assistant's config-entry runtime mechanism. Unload entities, cancel polling and close the connection on unload or failed setup.

### Editing Connection Settings And Replacing Hardware

The existing native Configure/options flow must expose exactly four editable fields: host, port, unit ID and polling interval, prefilled with the current saved values. Every submission follows the same validation and save path, including unchanged settings or an interval-only change. There is no replacement checkbox, editing mode selector or offline-save branch. A connection change must not require deleting and recreating the integration or finding a separate hidden workflow. Save connection settings in config-entry data and cadence in config-entry options consistently during both initial setup and editing.

- Validate all submitted fields, then open a temporary client to the entered endpoint and validate supported type, identity and required telemetry before changing saved state. This applies equally to interval-only edits, unchanged endpoints and changed endpoints. A validation failure leaves all saved values unchanged. Close this client on every success, error or cancellation. Exclude the entry being edited from duplicate checks, but reject an endpoint or serial already owned by another entry. At the active endpoint, reuse the existing coordinator's validation session to serialize the probe with polling.
- If the verified serial matches the approved serial, save the new endpoint and interval, retain all installation and entity identifiers, and reload once. Changing IP address, port or unit ID must not change sensor history, names, user customisations or disabled state.
- Detect a supported HS3 with a different serial automatically during submission and show a clear translated confirmation that the user is replacing the hardware for this existing installation. This works identically whether the endpoint has changed or is unchanged. Confirmation is the only additional user action; no advance replacement selection is required, and no submission may silently adopt a different serial.
- Until replacement is explicitly confirmed, leave all saved settings and identities unchanged. Rejected validation, duplicates and a cancelled flow must not change or unload the running entry. Recheck ownership before saving the confirmed replacement so another entry cannot acquire that endpoint or serial while confirmation is pending.
- On confirmation, retain the same config entry, device registry identity, entity registry records, entity unique IDs, entity IDs and sensor semantics. Update only the approved hardware serial, current hardware metadata and requested connection/cadence settings, then reload once. The coordinator must subsequently compare against the newly approved serial.
- Replacing HS3 with HS3, including a different serial or rated power, must have **no impact on historical data** for any of the six sensors: no deleted or recreated entities, no renamed entity IDs, no new history/statistics identities, no erased recorder data and no copied history. Existing history remains associated with the same sensors, and readings after replacement continue under those identities. Preserve user customisations and entity disabled state as well. Ordinary communication downtime can produce unavailable states; it must not reset or detach recorded history.

Use one clean identity scheme and native registry/config-entry operations. Do not add alternate identity formats, fallback lookup paths, history transfer code, a hardware profile framework or a custom frontend. H2 and other model support remain deferred; the identity design must not tie the logical installation to its current hardware model or serial.

### Polling And Sensor Selection

Use one Home Assistant coordinator per entry. Proposed project defaults are **30 seconds between update cycles**, a **5-second request timeout**, and **250 milliseconds between completed requests**. These are conservative project defaults, not device timing guarantees. Expose the cycle interval during initial setup and in the same native editing form as connection settings, with a minimum of 30 seconds in this iteration.

For all six enabled sensors, one cycle reads exactly these ranges sequentially:

| Start | Count | Purpose |
| --- | --- | --- |
| `0x4004` | 1 | Operating mode |
| `0x406F` | 1 | Battery charge |
| `0x40A0` | 1 | Household load |
| `0x40A5` | 3 | Solar, battery and total measured grid power |

Do not combine across undocumented address gaps. After entity setup, omit disabled sensors from the read set; split the three-word range into contiguous runs of enabled registers so a disabled sensor does not require its own register to be read. With no enabled sensors, stop scheduled telemetry reads. Re-enabling a sensor resumes its reads without requiring manual restart.

Commit a new snapshot only after the requested reads complete successfully. On a transport or protocol failure, stop the cycle, discard partial results, close the affected connection and mark the entry's sensors unavailable. Retry on the next scheduled cycle, with no immediate retry loop or extra retry scheduler. Reconnect as needed and verify identity before publishing data from the replacement connection. A valid response containing an invalid individual value makes that sensor unknown while allowing other valid values to update.

Expose power sensors with the power device class and measurement state class; battery charge with the battery device class and measurement state class; operating mode as translated enumeration values. Do not apply energy or cumulative statistics semantics to these readings.

### Diagnostics And Logging

Provide native diagnostics containing the detected profile, raw type and rated power in W, polling interval, enabled semantic keys, connection/update status and structured last error. Redact host and serial wherever included, including inside identifiers. Do not include credentials, complete config entries or arbitrary register dumps.

Use Home Assistant's native debug-logging controls. Log connection, failure and recovery transitions with actionable context; avoid repeating the same warning every cycle or logging successful register payloads routinely.

## Verification And Acceptance

Unit tests must provide 100% line and branch coverage on their own. Each test exercises one module through its public interface with every collaborating module stubbed or mocked. No unit test opens a socket, starts a simulator, reads project fixtures, waits for real time or assembles the library and Home Assistant integration together. Inject or mock connection I/O and pacing waits. Test behavior and interactions rather than restating addresses and constants.

Cover:

- Correct string, signed-value and percentage decoding, including battery charge/discharge signs; automatic HS3 detection, unsupported types, invalid identity, charge and unknown-mode handling.
- Read framing, partial in-memory stream reads, mismatched headers, malformed lengths, exception codes, timeout, cancellation and connection cleanup.
- Config-flow validation, initial cadence persistence and duplicate handling; exactly four editable connection/cadence fields; validation on interval-only and unchanged submissions as well as endpoint changes; independent runtime state; setup retry and serial mismatch; unload cleanup.
- Explicit HS3 replacement at the same and a changed endpoint; confirmation and cancellation; rejection of another entry's endpoint or serial, including before final save; unchanged installation/device/entity identifiers and registry records; updated approved serial and hardware metadata; preserved names, disabled state and sensor history identities; no saved-state mutation on failed validation.
- Sequential bounded polling, disabled-sensor read omission, no overlapping cycles, discarded partial snapshots, failure availability and recovery.
- Sensor units, classes and translated states, option updates and diagnostic redaction.
- Model-neutral default device and sensor naming through native Home Assistant registration, including all six generated entity IDs on a fresh installation; stable identity and preserved user-assigned names after connection editing and hardware replacement. Keep unit tests isolated and extend the existing lifecycle smoke rather than adding another end-to-end suite.

Use the isolated Docker Home Assistant browser environment with an HS3 endpoint based on the existing battery scenario. The current test-only request observer may remain in front of that endpoint. Confirm the setup form accepts the polling interval and numeric unit ID, adding SAJ Local creates six usable sensors, and the native editing form contains the saved connection and interval settings. Retain the existing disable/re-enable smoke check. Extend only the critical native lifecycle smoke needed to verify a connection edit and explicitly confirmed HS3 replacement: capture native registry identifiers and a recorded state before the change, then verify the same sensor/entity identities, pre-change recorded state and working readings afterward. Check both a changed endpoint with the same serial and a new serial at the same endpoint where feasible within one lifecycle smoke. Test-only endpoint/serial controls must remain outside production code and must not import simulator definitions into the integration or establish protocol authority. Do not build a broad end-to-end behavior suite or assert exact simulated measurements; unit tests establish application logic. Keep all browser smoke tests outside the Python coverage gate and retain the controlled frontend tier without new custom-card behavior.

The interactive environment already supplies `modbus-mock:502` and `modbus-mock-h2:502`. Use the HS3 endpoint for this iteration; the presence of the H2 service does not make H2 support part of this work. No development or acceptance step requires a physical inverter or access to another Home Assistant installation.

Acceptance requires:

1. Initial setup exposes host, port, unit ID and polling interval, persists the selected cadence, and creates a device and six correctly typed sensor entities in isolated Docker Home Assistant. Native editing exposes the same settings with current values.
2. Multiple entries remain independent and duplicate devices are rejected.
3. Reads obey the register contract, encodings and read-only scope, with bounded sequential communication.
4. Communication failure removes availability and later successful polling restores it without fabricated or partially updated measurements.
5. Disabled entities stop unnecessary reads and re-enabling them restores updates.
6. Native diagnostics redact endpoint and device identity, and errors are translated and actionable.
7. `make ci` passes, including lint, isolated unit coverage, import boundaries and the updated Docker browser smoke test. No simulator definitions are imported or used as protocol authority.
8. Configure contains exactly host, port, unit ID and polling interval. Every submission validates the entered endpoint, without a checkbox or separate editing modes. Successful edits retain the existing installation and all sensor identifiers/history; failed edits and cancelled flows leave the saved and running configuration unchanged. A different serial at an unchanged endpoint is detected automatically and requires confirmation.
9. Explicitly confirmed HS3-to-HS3 replacement, including a different serial at the same endpoint, retains the same device and entity registry identities and all historical data without resetting names, user customisations or disabled state. Unconfirmed serial changes remain errors, duplicate ownership remains prevented, and the newly approved serial is used after reload.
10. A fresh installation uses the model-neutral device name SAJ and generates `sensor.saj_*` entity IDs for all six measurements. Hardware model and rated power remain visible in device metadata. Connection editing and replacement retain those entity IDs and any user-assigned names. Do not automatically rename existing registered entities, delete persisted development registry records, reset Home Assistant, or add alternate identity lookup or history-transfer machinery to implement this naming correction.

## Work Sequence

1. Implement and unit-test the read-only transport and HS3 identity/telemetry decoding from the protocol details above.
2. Implement and unit-test configuration, entry lifecycle, coordinator and sensors.
3. Add initial and editable interval/connection settings, the explicit replacement workflow and stable installation-based sensor identities; retain entity-selection behavior, translations, diagnostics and transition logging.
4. Extend the isolated browser environment and its existing smoke test; document supported scope and development setup.
5. Run `make ci`, fix failures within this scope and repeat until it passes. Leave the git index and history untouched.

## Revisions

| Revision | Date | Change |
| --- | --- | --- |
| 1 | 2026-10-06 | Initial draft following the revised overview: small HS3 read-only integration, register information incorporated directly, isolated unit coverage and Docker simulator smoke testing. |
| 2 | 2026-10-06 | At the user’s direction, removed detailed source attribution and aligned the contract with hand-verified behavior: automatic HS3 type detection, rated power in W, battery sign meaning, and total grid power at `0x40A7` instead of grid-supplied load at `0x40AD`. |
| 3 | 2026-10-06 | At the user’s direction, added polling interval to initial setup, made connection/cadence editing explicit, and required confirmed HS3 replacement to preserve all sensor history and registry identities. Replaced serial-derived installation/entity identity with a single stable config-entry-based scheme; retained serial validation and duplicate prevention for current hardware. Added focused lifecycle and isolation acceptance checks. |
| 4 | 2026-10-06 | At the user’s direction, made model-neutral installation and sensor naming explicit: default device name SAJ, model-neutral entry title and `sensor.saj_*` IDs on fresh setup. Hardware model remains metadata; existing identities, custom names and history must survive system changes. Added focused native naming and customisation acceptance checks without expanding model support or altering persisted development records. |
| 5 | 2026-10-06 | At the user’s direction, simplified Configure to four fields with one validation path for every submission. Removed the replacement checkbox and the separate offline interval-save requirement. Detect changed hardware automatically, including at an unchanged endpoint, and confirm only when its serial differs. |
