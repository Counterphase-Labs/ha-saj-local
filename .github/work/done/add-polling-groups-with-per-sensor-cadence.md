# Add Polling Groups With Per-Sensor Cadence

## Plan Metadata

- **Revision:** 6
- **Status:** Approved
- **Last revised:** 2026-10-08
- **Requirements:** `../requirements.md`
- **Code style:** `../code-style.md`
- **Builds on:** `../future/implement-hs3-read-only-integration.md` and `add-h2-support-with-shared-device-profiles.md`. Everything in those plans that is not restated or explicitly replaced here continues to apply.

## Outcome And Scope

A user can create any number of named polling groups on an installation. Each group has its own interval and a set of sensors. Sensors in a group are read at the group's interval; every other sensor is read at the installation's default interval. With no groups, the integration polls as it does today.

Faster cadences are only safe if the device is protected whatever the user configures and whatever goes wrong on the link. This plan therefore delivers the cadences and the protection together: one scheduler and one connection per installation, a hard request budget, no retry storms, and failure handling that keeps one refused register or one late frame from taking the installation down.

Requirements delivered:

| Requirement | Delivered by |
| --- | --- |
| Read selected sensors at a higher or lower cadence | Assigning sensors to a polling group |
| Create one or more different sensor reading cadences | Any number of polling groups per installation |
| Intelligent Modbus access that does not put the system in danger of overload, especially AIO3 | The device protection rules below |
| Clear and detailed errors with good error handling | Failures classified by what they mean, each with its own scope and recovery |
| Convention over configuration, without pages of config flow | No groups by default; one three-field form per group, outside setup and Configure |

Included:

- Polling groups as native Home Assistant config subentries: add, edit and delete from the integration page.
- A polling engine in the SAJ library: cadence schedule, request budget, read health and failure back-off, with no Home Assistant code.
- Client changes: budgeted requests, late-frame handling, exception responses that keep the connection, one reconnect for a stale connection.
- Per-sensor availability for refused registers, alongside the existing installation-wide availability.
- One connection per endpoint, including while Configure validates the active endpoint.
- Diagnostics, logging, translations and documentation for the above.

Not changed:

- Setup and Configure keep their five fields.
- Sensor selection stays the native enable and disable of an entity, which already removes a disabled sensor's register from the read set. No include or exclude form is added.
- The six sensors, their keys, names, units and identities.
- The browser tier. It remains load-and-function smoke for an HS3 and an H2 endpoint and gains no step.

Deferred: register writes, further sensors, optional equipment, faults, custom frontend behaviour, and groups shipped as defaults.

## Rules Replaced From Earlier Plans

This plan does not replace an earlier plan. It replaces these rules of `../future/implement-hs3-read-only-integration.md`; the rest of that plan stands.

| Earlier rule | Now |
| --- | --- |
| The polling interval is at least 30 seconds. | Every interval is at least 10 seconds. |
| The polling interval defaults to 30 seconds. | It defaults to 60 seconds. |
| Any transport or protocol failure stops the cycle, closes the connection and makes every sensor of the entry unavailable. | Each response is classified; see Failure Handling. A refused register affects only its own sensors and keeps the connection. |
| A failed cycle is retried on the next scheduled cycle. | Consecutive failed cycles back off, up to 300 seconds. |
| Every cycle reads every enabled sensor. | A cycle reads the sensors that are due. |
| Configure validates over a connection of its own. | The active endpoint is validated over the installation's connection. |

## Field Evidence

No protocol document states a polling limit. The rules below come from field reports of SAJ inverters behind their communication modules, the AIO3 above all. Each lesson is stated with what this plan does about it.

| Observed in the field | Consequence for this design |
| --- | --- |
| A module polled too hard stops serving the client: port 502 closes or the client address is refused, and it has stayed that way until the module was given a new address. A full scan every 15 seconds with retries was enough. | Overload is not a transient error to recover from. Request volume has a hard ceiling that no configuration, failure or retry can exceed. |
| The configuration that runs reliably is a full scan every 60 seconds, itself a burst of a few dozen requests over about 8 seconds, optionally with a handful of registers every 10 seconds. One-second reads are fielded only for a single register block. | The budget and the minimum interval are set inside that envelope. |
| Read failures were retried three times with back-off inside a cycle. Cycles lengthened, overlapped the next one, and the retries themselves flooded the module. | No retry inside a cycle. Consecutive failed cycles back off instead of repeating at the cadence. |
| One register block refused by a firmware made every poll fail. Every entity of the installation flapped between a value and unavailable on a two-minute rhythm. | A refusal is an answer, not a link failure. It affects only the sensors in that request. |
| A refused block was requested again on every poll indefinitely, producing an exception each time. Later it was excluded after three refusals and re-tested daily, so a firmware update is picked up. | Refused sensors are suspended after three consecutive refusals and re-tested once a day. |
| After being excluded, a block left no trace, and a partly degraded device looked healthy. | Suspended sensors are unavailable, listed in diagnostics and logged once on each transition. |
| A module sent a second, late response to a request it had already answered with an exception. Every later response was then matched one position off and garbage was decoded as energy values. Seen on several registers and on both network interfaces of the module. | A frame for a transaction that is no longer outstanding is discarded. It never fails the cycle and is never decoded. |
| A connect to an unresponsive module never returned. Home Assistant puts no time limit on an update, so polling stopped for ten hours with nothing logged. | Every wait in a cycle is bounded, and the cycle as a whole has a deadline. |
| Modules were unstable when more than one party talked to them, and they also serve the vendor's cloud. | One connection per endpoint, without exception. |
| Devices answer with exception codes outside the standard set, including code 0. | Classification never assumes a standard code. |
| A cycle that returned little replaced the whole cache and blanked every other sensor. | A cycle updates only what it read. |

## Behaviour

### Cadences

An installation has one default cadence and zero or more group cadences.

| Cadence | Interval | Sensors |
| --- | --- | --- |
| Default | The existing polling interval from setup and Configure | Every supported sensor that is in no group |
| Group | The group's interval | The sensors assigned to the group |

A sensor belongs to exactly one cadence. A group's interval may be shorter or longer than the default.

Every interval, the default included, is a whole number of seconds with a minimum of **10**. Ten seconds is the shortest cadence with sustained field use against these modules; nothing shorter is offered.

The default interval offered at setup is **60** seconds. That is the full-scan interval with sustained reliable field use, and it keeps a full read of a much larger sensor set inside the request budget.

### Scheduling

All cadences of an installation share one time grid that starts when the entry loads. A cadence is due at the grid origin and at every multiple of its interval after it.

| Rule | Behaviour |
| --- | --- |
| One cycle per wake-up | Every cadence that is due is read in the same cycle. Their sensors are planned together, so registers that are contiguous across groups share one request and no register is read twice. |
| Shared grid | A 10-second and a 60-second cadence coincide on every sixth fast tick. Cadences are never offset from each other. |
| No backlog | If a cycle overruns one or more ticks of a cadence, the cadence is read once on the next wake-up and continues on the grid. Missed ticks are dropped, never queued. |
| No overlap | A cycle never starts while another is running. |
| Only what is needed | A cycle reads the sensors that are due, enabled and not suspended. A wake-up with nothing to read sends no request. With no enabled sensors there are no scheduled reads. |
| Full read | The first cycle after load, and the first cycle after a failed cycle or a reconnect, reads every enabled sensor that is not suspended. |

Example with the default at 60 seconds and one group "Power" at 10 seconds holding solar, battery and grid power:

| Time | Due | Requests |
| --- | --- | --- |
| 0 s | Everything | `0x4004`, `0x406F`, `0x40A0`, `0x40A5`–`0x40A7` |
| 10 s | Power | `0x40A5`–`0x40A7` |
| 20 s | Power | `0x40A5`–`0x40A7` |
| 30 s, 40 s, 50 s | Power | `0x40A5`–`0x40A7` |
| 60 s | Default and Power | `0x4004`, `0x406F`, `0x40A0`, `0x40A5`–`0x40A7` |

### Device Protection

These hold for every request the installation sends: telemetry, identity, reconnect and the Configure probe of the active endpoint.

| Rule | Behaviour |
| --- | --- |
| One connection | One TCP connection per endpoint, one request in flight, and the existing pause between requests. |
| Request budget | At most **40 requests in any 60 seconds** per endpoint. A request that would exceed it waits until it fits. The cycle lengthens; nothing is dropped and nothing is sent early. A burst up to the budget is allowed, so a full read is not slowed in normal operation. |
| No retry in a cycle | A request is sent once per cycle, with the single exception of the stale-connection rule below. |
| Failure back-off | After each consecutive failed cycle the wait before the next attempt doubles, starting at the shortest configured interval and capped at **300 seconds**. The first successful cycle returns to the grid. |
| Bounded cycle | Connecting, each request and closing are individually time-limited, and the cycle has an overall deadline derived from its read plan. A cycle that passes its deadline is cancelled, the connection is closed, and it counts as a failed cycle. |
| Planned load is visible | At load the steady-state requests per minute of the configured cadences are computed. If they exceed the budget, one warning says that cadences will run slower than configured. Diagnostics report the planned load and the budget. |

The budget and the failure back-off belong to the endpoint, not to a loaded entry. They are kept for as long as Home Assistant runs and are inherited by every load of the installation, so a reload, a group edit or a setup retry starts with the requests already sent and the failures already counted. Every client for an endpoint draws on that endpoint's budget, including the temporary one used by setup and by Configure for an endpoint that is not loaded.

Back-off also governs loading. Home Assistant retries a failed load on its own timer, which is shorter than the back-off. A load attempted before the back-off has elapsed ends as not ready without contacting the device, and a load that fails counts as a failed cycle. Validation started by the user in setup or Configure is not held back by the back-off; the budget still applies to it. A validation that passes clears the endpoint's back-off, because the device has just answered, so the load that follows is not held back. A validation that fails leaves the back-off as it was.

The budget counts Modbus requests, not sensors and not registers. One request reads one contiguous block of registers, however many sensors it holds: a full read of the six sensors is four requests. Registers that are not contiguous are read in separate requests; gaps are not bridged. Field reports describe module load in requests only, so whether the size of a block also matters is unknown, and no rule here depends on it.

The budget is a property of the device, not of the configuration. It sits inside the envelope that runs reliably in the field and well below the load at which modules have stopped serving clients.

### Failure Handling

This replaces the earlier rule that any transport or protocol failure fails the whole cycle. Each response is classified by what it means.

| What happens | Meaning | Connection | Effect | Recovery |
| --- | --- | --- | --- | --- |
| Registers returned | Success | Kept | Values published for the sensors read | — |
| Exception `0x04` (device failure) or `0x06` (busy) | The device cannot serve requests now | Kept | The cycle stops at once and nothing further is sent. Failed cycle: every sensor unavailable. | Back-off, then a full read |
| Any other exception code, standard or not | The device refuses these registers | Kept | Only the sensors in that request become unavailable. The cycle continues with its other requests. | Refusal handling below |
| A frame for a transaction that is no longer outstanding | A late duplicate | Kept | Discarded. The client keeps waiting for the outstanding response within the same request timeout. | — |
| The peer closed the connection, seen on the first request of a cycle over a connection kept from an earlier cycle | A stale connection, not a device failure | Reopened once | Identity is verified and the cycle becomes a full read on the new connection: every enabled sensor that is not suspended is read, so no published value predates the reconnect. | If it fails, a failed cycle |
| Timeout, connection failure, or a frame that is malformed or does not match the request's protocol, unit, function or length | The link cannot be trusted | Closed | Failed cycle: every sensor unavailable, nothing from the cycle is published. | Back-off, reconnect with identity verification, then a full read |

A late duplicate is recognised by its transaction: it must belong to one of the last 64 requests answered on the current connection. A frame for any other transaction is a mismatched frame. The memory is cleared when the connection closes.

Unsolicited bytes waiting on the connection before a request is sent are discarded.

A snapshot never combines values from before and after a failed cycle. Reconnect still verifies identity before any value is published.

### Refused Registers

| Step | Behaviour |
| --- | --- |
| First refusal | Every sensor in the refused request is unavailable. From the next cycle, each of them is read in a request of its own, so one refused register cannot hide its neighbours. |
| Success | The sensor is available again and may share requests again. |
| Third consecutive refusal of a sensor | The sensor is suspended: it is unavailable and no longer read. One warning names it and the exception code. |
| Suspended | Re-tested with one request every 24 hours, and at every load. A success lifts the suspension, with one informational log line. |

A re-test never causes a wake-up of its own. Once due, it is added to the next cycle that runs for a cadence, so it can be later than 24 hours by up to the wait for that cycle. With no enabled sensor on any cadence there are no cycles and so no re-tests until the next load.

Refusals do not count as failed cycles and do not cause back-off: the device is answering.

Setup and Configure validation is unchanged. A required register that is refused still fails validation with the existing error, and nothing is saved. Suspension applies only to a loaded installation, so that a firmware change does not take a working installation down.

### Sensor State

| Condition | State |
| --- | --- |
| Read in the last cycle that included it | Its value, or unknown for an invalid value as today |
| Failed cycle | Unavailable, for every sensor of the installation |
| Refused or suspended | Unavailable, for that sensor only |

A sensor writes its state only in a cycle that read it, and on any change of its availability. A slow sensor is not reported as refreshed each time a fast group is read.

### Polling Groups In Home Assistant

Polling groups are config subentries of the installation, of one type, `polling_group`. Home Assistant lists them under the installation with native add, edit and delete controls. Setup and Configure are not touched.

The add form and the edit form are the same single form:

| Field | Input | Rule |
| --- | --- | --- |
| Name | Text | Required. Becomes the subentry title. |
| Seconds between updates | Numeric box | Whole number, at least 10. |
| Sensors | Multi-select | At least one. Lists this installation's sensors that are in no other group, plus the group's own when editing. |

Sensor options are built from the entity registry entries of the installation, so they carry the names the user sees, including renamed and disabled sensors. The stored value is the semantic key, never an entity ID, so renaming an entity or replacing the hardware model does not break a group.

| Outcome | Behaviour |
| --- | --- |
| Valid submission | The group is saved and the installation reloads once through its existing update listener. |
| Interval below the minimum or not a whole number | Translated error on the interval field. Nothing is saved. |
| No sensor selected | Translated error on the sensors field. Nothing is saved. |
| A submitted sensor already belongs to another group | Translated error on the sensors field. Nothing is saved. The form cannot produce this; the check guards the stored state. |
| The installation has no registered sensors, or none left unassigned when adding | Translated abort explaining why no group can be created. |
| Group deleted | Its sensors return to the default cadence after the reload. |
| Sensor moved to another group | Two edits: remove it from the first group, then add it to the second. Each edit reloads once. Between the edits the sensor is on the default cadence. |
| Sensor removed from a group | It returns to the default cadence after the reload. |

Group membership is not part of a sensor's identity. Adding a sensor to a group, moving it, removing it and deleting its group all leave the entity, its ID, name, customisations and history untouched; the only visible effect is the brief unavailability of a reload.

Adding or editing a group does not contact the device.

At load, a stored key that the effective profile does not support is ignored, and a group left with no supported sensors contributes nothing. Editing such a group shows only the sensors that still exist, and saving drops the rest.

Entities are never attached to a subentry. Home Assistant removes the entities of a deleted subentry, and deleting a polling group must not delete a sensor or its history.

### Configure On The Active Endpoint

When Configure validates the endpoint the installation is already connected to, the probe runs through the installation's own connection, lock and budget. It does not open a second connection. Validation of any other endpoint opens a temporary connection as today, drawing on that endpoint's budget.

## Implementation Design

### Division Of Roles

The library decides; the integration presents. The library can be run and tested with no Home Assistant present, and the integration has no way around the library's protection rules.

| Concern | SAJ library | Integration |
| --- | --- | --- |
| What to read and when | Decides which keys are due, builds the read plan and computes the next wake-up. | Wakes the library at the time it asked for. |
| Device protection | Owns the budget, back-off, cycle deadline, late-frame handling and the connection. | None. Every request it causes goes through the library. |
| Refused registers | Counts refusals, isolates, suspends and re-tests. | Shows the sensor as unavailable. |
| Groups | Receives an interval and a set of keys per cadence. | Owns the group as a user concept: the subentry, its form, name, validation and storage. |
| Enabled sensors | Receives the set of enabled keys for each cycle. | Derives that set from the entity registry. |
| Results | Returns values, keys read, refusals, suspensions and the next wake-up, or one failed-cycle error with its cause. | Publishes state, translates the error, fills diagnostics. |
| Limits | Defines them as constants: they are statements about the device. | Imports the minimum interval for form validation. |

### SAJ Library

All polling logic lives in the library, with no Home Assistant import. Time and waiting are injected; no module reads a clock or sleeps on its own.

| Module | Responsibility |
| --- | --- |
| `saj/schedule.py` | `Cadence` (interval and keys), cadence building from the default interval, group definitions and supported keys, and `Schedule`: what is due at a given time on the shared grid, the next due time, coalescing, the full-read request, and the failure back-off delay. |
| `saj/budget.py` | `RequestBudget`: how long a request must wait at a given time to stay within the budget, and recording a request. Also the steady-state load of a set of cadences. |
| `saj/guard.py` | `EndpointGuard`: the protection state of one endpoint that outlives a connection and a load: its `RequestBudget`, the count of consecutive failures and the earliest time of the next attempt. The poller reports each failed and successful cycle to it; the back-off delay is computed here. |
| `saj/health.py` | `ReadHealth`: per-key consecutive refusals, which keys must be read alone, which are suspended, and when a suspended key is due for its re-test. |
| `saj/poller.py` | `Poller`: runs one cycle. Asks the schedule what is due, removes disabled and suspended keys, adds due re-tests, reads, feeds outcomes to the health tracker, and returns a `CycleResult`: values read, keys read, keys refused with their codes, keys suspended, and the next wake-up time. Raises one error type for a failed cycle, carrying its cause. Owns the cycle deadline. |
| `saj/telemetry.py` | Read-range planning gains keys that must not be merged. Reading returns values and refusals per key instead of raising on a refusal. |
| `saj/client.py` | Applies the budget before every request. Discards frames for transactions that are no longer outstanding and unsolicited input. Leaves the connection open after an exception response. Reports whether a failure was the peer closing a kept connection. Bounds closing. Exception responses are classified by code in one place. |

Rules:

- The library deals in intervals, keys and times. It knows nothing about groups as a user concept, entities, subentries or enabled state beyond the set of keys it is handed.
- No profile-specific branch anywhere.
- The minimum interval, the budget, the back-off cap, the refusal threshold and the re-test period are named library constants: they are statements about the device. The integration imports the minimum interval for form validation.
- Each module is tested alone with its collaborators replaced. The poller is tested with a fake schedule, health tracker and reader.

### Integration

- **Coordinator.** Becomes a thin adapter. It builds the poller at load from the entry's default interval and its `polling_group` subentries, calls it once per wake-up with the enabled keys, publishes the result, and sets its next wake-up from the result. A failed cycle is translated through the existing error mapping into the update failure. Home Assistant schedules a coordinator on whole seconds; the wake-up must be computed so that it lands on or after the intended time, so a wake-up never finds nothing due because it fired early.
- **Sensors.** Availability combines the installation's and the sensor's own. State is written when the last cycle read the key or when availability changed.
- **Subentry flow.** One flow class serves add and edit through one form builder and one validation function. `SajLocalConfigFlow` declares the supported subentry type. The flow reads the entity registry for the installation's sensors and the entry's other subentries for ownership; it does not use runtime data, so it works while the entry is not loaded. Saving uses the native subentry update without a flow-initiated reload, because the entry's update listener already reloads.
- **Configure.** The probe takes the client to use from the same hook that today supplies the validation session, so the active endpoint is probed over the installation's connection.
- **Endpoint guards.** The integration keeps one `EndpointGuard` per host and port for the lifetime of Home Assistant and hands it to every client and poller for that endpoint. Entry load asks the guard first: before the earliest next attempt it raises not ready without opening a connection, and a failed load is reported to the guard with the entry's shortest configured interval as the back-off base.
- **Constants.** `DEFAULT_SCAN_INTERVAL` becomes 60 and stops being used as a lower bound. The subentry type and its data keys are named constants.
- **Diagnostics.** Add: each cadence with its interval, keys and requests per read, the default marked; planned requests per minute and the budget; keys read by the last cycle; refused and suspended keys with their exception codes and next re-test; consecutive failed cycles and the current back-off; counts of discarded late frames and stale-connection reconnects since load. Group names are user text and are not included.
- **Logging.** Debug at load: the cadences and their read plans. Warning once: planned load above the budget; a sensor suspended; the existing update-failed transition. Info once: a suspension lifted; the existing recovery transition. Debug: a discarded late frame, a stale-connection reconnect. Nothing is logged per successful cycle.
- **Translations.** The subentry type name, its forms, field labels, the three field errors and the abort reasons. The minimum in the existing interval error text changes to 10 in setup and Configure.

### What Is Removed

- The fixed `update_interval` as the coordinator's cadence, its `interval` attribute, and the cycle logic now owned by the poller.
- Closing the connection on an exception response.
- Failing a cycle on a frame for an earlier transaction.
- The second connection opened by Configure against the active endpoint.

## Verification And Acceptance

The unit-test rules of the requirements apply unchanged: 100% line and branch coverage from isolated unit tests, one module per test through its public interface, collaborators replaced, no sockets, files, real time or constant-restating assertions. Time is a plain number supplied by the test and waiting is a recorded call.

Cover:

- **Schedule.** As multivariate tests: what is due across a sequence of times for one cadence, for intervals that are multiples and for intervals that are not; coalescing after an overrun of one and of several ticks; the next due time; the full-read request; nothing due; the back-off sequence, its cap and its reset.
- **Cadence building.** Ungrouped keys fall to the default; unsupported keys are dropped; an emptied group disappears; a key claimed twice is rejected; no groups yields one cadence.
- **Budget.** A burst up to the limit passes without waiting; the next request waits exactly until it fits; the window slides; steady-state load of cadences.
- **Health.** Refusal counts, reset on success, isolation after a first refusal, suspension at the threshold, re-test timing, lifting.
- **Guard.** The back-off sequence, its cap and its reset; the earliest next attempt; a guard reused by a second client and poller keeps its budget history and failure count.
- **Entry load.** A load before the earliest next attempt is not ready and sends nothing; a failed load counts as a failure; a passed user validation clears the back-off and a failed one leaves it; a reload reuses the endpoint's guard; two endpoints have separate guards.
- **Identity and history.** With the real entity registry: moving a sensor between groups, removing it from a group, deleting a group, and replacing the model each leave every entity's ID, unique ID, name, customisation and disabled state unchanged, and delete no entity.
- **Re-test scheduling.** A due re-test joins the next cycle and never changes the next wake-up time.
- **Telemetry.** Isolated keys are planned alone; a refused request yields refusals for its keys and the remaining requests are still sent; busy and device-failure codes stop the read.
- **Client.** The budget is consulted before every request; a late frame is discarded and the outstanding response is still returned; a late frame followed by silence times out; unsolicited input is discarded; an exception response leaves the connection open; a peer close on a kept connection is reported as such; every existing malformed-frame case still fails and closes.
- **Poller.** Only due, enabled, unsuspended keys are read; due re-tests are added; the result carries values, read keys, refusals, suspensions and the next wake-up; each row of the failure table; the stale-connection reopen with identity verification, used once and followed by a full read; the deadline; a full read after a failed cycle.
- **Coordinator.** The result is published and merged; a disabled key leaves the snapshot; the next wake-up follows the result and never precedes it; a failed cycle is translated and makes the update fail; identity mismatch and cancellation behave as today.
- **Sensors.** Per-sensor and installation availability; state written when read, not written when not, and on each availability change.
- **Subentry flow.** Add and edit through the same form; each row of the outcome table; a sensor released by one group is offered by another; options exclude sensors owned by other groups and include the group's own when editing; labels from registry names for renamed and disabled sensors; behaviour with the entry not loaded; stale keys dropped on save; no entity attached to a subentry.
- **Setup and Configure.** The interval minimum is 10 in both; the active endpoint is probed over the installation's client and any other endpoint over a temporary one; a refused required register still fails validation.
- **Diagnostics.** Every added item is reported; no group name, host or serial appears.
- **Import boundary.** The library still imports without Home Assistant.

Acceptance requires:

1. With no polling groups, an installation polls every enabled sensor at the default interval.
2. A group can be added, edited and deleted from the integration page through one three-field form, and each change takes effect after a single reload.
3. Sensors in a group update at the group's interval and all others at the default, for intervals shorter and longer than the default. Several groups coexist, and separate installations are independent.
4. Cadences due together are read in one cycle with one combined plan, and no register is read twice in a cycle.
5. No configuration, failure, reconnect, reload, setup retry or Configure probe makes an endpoint receive more than 40 requests in any 60 seconds, start a second cycle while one runs, or open a second connection to its endpoint.
6. No request is retried within a cycle except the single stale-connection reopen, and consecutive failed cycles and failed loads are spaced by the back-off up to 300 seconds, across reloads. A validation the user starts is never held back, and one that passes clears the back-off.
7. No cycle can run past its deadline; a stalled connect, request or close ends as a failed cycle and polling continues.
8. A refused register makes only its own sensor unavailable. After three consecutive refusals the sensor is suspended, re-tested daily and at load, and restored when the register answers. Its neighbours keep updating throughout.
9. A late frame for an earlier transaction changes no sensor value and no availability.
10. A busy or device-failure exception stops the cycle without further requests and without closing the connection.
11. After a failed cycle every sensor is unavailable; after recovery every enabled, unsuspended sensor carries a value read after the failure.
12. A sensor's state is written only when it was read or its availability changed.
13. Every interval in setup, Configure and a group is rejected below 10 seconds with a translated error, and setup offers 60 seconds as the default interval.
14. Moving a sensor between groups, removing it from a group, deleting a group, renaming an entity, disabling a sensor, editing the connection and replacing an H2 with an HS3 or the reverse leave every entity, its ID, name and history intact, and groups keep applying to the sensors that still exist.
15. Diagnostics show cadences, planned load against the budget, refused and suspended sensors, back-off state and link counters, with no group name, host or serial.
16. All polling logic lives in the SAJ library with no Home Assistant import, and no code branches on a specific profile.
17. `make ci` passes, including lint, the duplicate-code gate, the coverage gate, import boundaries and the unchanged browser smoke.
18. The README and `documentation/development.md` describe polling groups, the shared schedule, the device protection rules and how refused registers are handled, at the delivered level.

## Work Sequence

1. Client: budget hook, late-frame and unsolicited-input handling, exception responses that keep the connection, stale-connection reporting, bounded close. Add `saj/budget.py`.
2. Telemetry: per-key refusals and unmerged keys. Add `saj/health.py`.
3. Add `saj/schedule.py` with cadences, grid, coalescing and back-off.
4. Add `saj/poller.py` with the cycle, the failure table, the deadline and the stale-connection reopen.
5. Move the coordinator onto the poller with only the default cadence; add per-sensor availability and state writes only when read.
6. Apply the shared minimum interval to setup and Configure, and probe the active endpoint over the installation's client.
7. Add the `polling_group` subentry flow, its validation and translations; build cadences from the subentries.
8. Extend diagnostics and logging.
9. Update the README and the development guide.
10. Run `make ci` and fix what it reports until every gate passes. The git index and history stay untouched.

## Revisions

| Revision | Date | Change |
| --- | --- | --- |
| 1 | 2026-10-07 | Initial draft: polling groups as config subentries, one shared scheduler in the SAJ library, combined read plans, a 10-second minimum for every interval, and state writes only for sensors that were read. |
| 2 | 2026-10-07 | At the user's direction, built the design on field reports of SAJ communication modules, the AIO3 in particular. Added a hard request budget, failure back-off, a bounded cycle, late-frame handling, per-sensor handling and suspension of refused registers, a single stale-connection reopen, and one connection per endpoint during Configure. Replaced the whole-cycle failure rule with a classification of each response. Moved all polling logic into a library poller. |
| 3 | 2026-10-08 | At the user's direction, the default interval offered at setup is 60 seconds instead of 30. Following the user's review questions, stated explicitly: which rules of the earlier plan are replaced, that the budget counts requests of one contiguous block each, how a sensor moves between groups without affecting its identity or history, and the division of roles between the library and the integration. |
| 4 | 2026-10-08 | At the user's direction, stated that a suspended sensor's re-test joins the next regular cycle and never schedules a wake-up of its own. |
| 5 | 2026-10-08 | After review of the implementation, at the user's direction: the budget and the back-off belong to the endpoint and survive reloads, and back-off governs loading; a stale-connection reopen is followed by a full read; the late-frame rule states its 64-transaction memory; tests of entity identity and history across group changes and model replacement are required. |
| 6 | 2026-10-08 | At the user's direction, a validation started by the user that passes clears the endpoint's back-off. |
