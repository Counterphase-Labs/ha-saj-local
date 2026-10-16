# Redesign Simulator Panel With Inspector And Link Faults

## Plan Metadata

- **Revision:** 1
- **Status:** Approved
- **Last revised:** 2026-10-16
- **Requirements:** `../requirements.md`
- **Code style:** `../code-style.md`
- **Roadmap item:** None. A follow-up to the simulator control panel.
- **Builds on:** `../done/add-simulator-control-panel.md` and the plans it builds on. Everything in those plans that is not restated or explicitly replaced here continues to apply.
- **Field evidence:** "Field Evidence" in `../done/add-polling-groups-with-per-sensor-cadence.md`, the reports of SAJ communication modules (the AIO3 above all) that the link faults reproduce.

## Outcome And Scope

A developer debugging the integration against the simulator sees at a glance what the simulated system is doing, whether it is running as its scenario or has been changed, what every register holds, and every request a client sent with the answer it got. They can make the simulator's communication module misbehave the way real modules do in the field, and watch how the client copes.

| Need | Today | With this plan |
| --- | --- | --- |
| Read the page comfortably | Small, low-contrast text, mismatched control colours, one long narrow column | A readable type scale with tested contrast, matching controls and a layout that uses the window (see Visual Design) |
| See what the system is doing | One line of readings in the header | A power-flow diagram of the fitted equipment, coloured and animated by direction, above one card per piece of equipment |
| Work on one piece of equipment | Its variation, hold, state and faults sit in four separate sections | One card per piece of equipment holds its live reading, controls and faults, with a reset to the scenario for that card |
| Know whether the simulator has been changed | Nothing shows it | A status bar on every view shows running or paused, speed, time, active faults and what differs from the scenario |
| Find a fault, a setting or a register | Open collapsed groups one by one | Search and filter in each view |
| Know a change worked | Silent unless refused | A short confirmation for every change, and the reason for every refusal |
| See what the device holds | Decoded settings and eight readings | Every register the device serves, raw and decoded, with changes highlighted and when a client last read it |
| See what a client asked | Nothing is recorded | Every connection and request with its answer, filterable, plus request counts and rates per client |
| Test a misbehaving link | A fixed response delay in the scenario | Latency, missing answers, busy and non-standard exceptions, refused blocks, dropped connections, late duplicate answers, offline and unresponsive modules, and a module that locks out a client that polls too hard |

Included:

- A page split into views with a persistent status bar, built from the model's description as today.
- Equipment cards, a power-flow diagram, a fault catalogue, filtering, confirmations and the visual design below.
- A register inspector and a traffic recorder in the simulator, with the views that show them.
- Link faults in the simulator's Modbus server, in a new `link` scenario section and on the page, with presets.
- Vendored Tabler icons, the requirement changes below, `documentation/development.md` and the smoke test.

Not changed: the integration, its tests and the browser smoke tests. The simulated plant, its registers and its write handling are unchanged. With no link fault set, the Modbus behaviour is unchanged apart from `server.response_delay_ms` moving to `link.latency_ms`.

## Requirements

| Requirement | How it is met |
| --- | --- |
| The page builds every control from the model's description | Cards, the diagram, the fault catalogue, the register table and the traffic log are all built from the description and the state. The page still holds no model names, addresses or field lists |
| Behaviour believable and consistent | Link faults reproduce what field reports describe of SAJ communication modules. Nothing the field has not shown is modelled. The register table only shows; it cannot set a value a client could not write |
| Deterministic randomised behaviour | Every link fault given as a chance is drawn from the simulation seed and the request's sequence number, so the same seed and the same requests give the same faults |
| A standalone docker service | Everything, including the icons, is served by the simulator. Nothing is loaded from outside |
| `modbus_mock` is built around documented SAJ behaviour, not the integration | Link faults come from field reports of the modules. The traffic counters count requests and registers, as those reports do, and use no limit of the integration |
| 100% unit test coverage | Applies to all new Python: the recorder, the link, the register snapshot, the description and state additions, the routes, the scenario section and persistence. The page is exempt |
| Integration tests only as smoke tests | `make mock-smoke` also fetches the register snapshot, the traffic and one static file |

## Requirement Changes

Under "Modbus Mock" in `requirements.md`:

- Changed: "Each running simulator offers a simple web page" becomes "Each running simulator offers a web page". With views, a diagram, a register table and a traffic log it is no longer simple, and the next lines say what it must do.
- Replaced: "The page is a development tool: plain HTML and JavaScript with no libraries, no build step and no tests of its own." with: "The page is a development tool: plain HTML, CSS and JavaScript files served as they are, with no libraries, no build step and no tests of its own. Icons may be vendored from a set under the MIT or ISC licence, with its licence beside them."
- Added: "The page shows every register the simulated device serves with its raw and decoded value, and every Modbus connection and request the simulator receives with its answer, with request counts and rates per client."
- Added: "The simulator can reproduce the communication failures field reports describe of SAJ communication modules: slow and missing answers, busy and non-standard exception answers, refused register blocks, dropped connections, late duplicate answers, a module that is offline or unresponsive, and a module that locks out a client that polls too hard. They are set in the scenario and on the page, and are deterministic for a seed."
- Replaced: "Changes made on the page are kept across restarts. The page can reset the simulator to its scenario, apply ready-made presets for quick smoke testing, and export the running state as a scenario." with: "Changes made on the page to the simulated system, its link included, are kept across restarts; the traffic record is not. The page can reset the whole simulator or one piece of equipment to its scenario, apply ready-made presets for quick smoke testing, and export the running state as a scenario."

## Decisions

Decisions 1 to 6 were made by the user on 2026-10-16. The others are set by this plan and listed so they can be challenged.

| # | Decision | Outcome |
| --- | --- | --- |
| 1 | Icons | Tabler Icons (MIT), only the icons used, vendored as their original SVG files with the licence and the release they came from. No icon font, no emoji |
| 2 | Page files | `index.html`, one stylesheet and one ES module per view and per shared part, served as they are. Replaces Decision 5 of the control panel plan ("one HTML file") |
| 3 | Writing registers from the page | Not offered. The register table shows values only. Every change still goes through the same validation as a Modbus write (control panel Decision 11) |
| 4 | Keyboard shortcuts, command palette (a searchable list of actions opened with a key), undo | Not part of the page |
| 5 | Traffic, counters and register inspection | Included, as below |
| 6 | Link faults | Included, as below |
| 7 | Navigation | A tab bar of views, with the current view in the URL fragment (`#registers`) so a reload keeps it. Nothing is stored in the browser |
| 8 | Theme | The automatic light and dark theme stays. Colours are tokens with a value for each theme |
| 9 | Clock for link faults | Latency, intermittent offline and lockout windows run on wall time, not simulated time. They describe the link as the client sees it, so the clock speed does not change them |
| 10 | Traffic memory | The last 2000 entries and the counters are kept in memory, not saved. A restart or "Reset traffic" starts them again |
| 11 | Lockout | Saved across restarts and cleared only by "Reset module" or Reset to the scenario. Field reports describe a lockout that lasted until the module was given a new address. "Reset module" stands for that |
| 12 | Page reads | The register snapshot reads without the device observer, so it is not a client read: it causes no keep-alive, no field touch and no traffic entry |
| 13 | Refresh | State every 3 seconds as today. The Registers and Traffic views also refresh every second while they are open |
| 14 | Presets and link | A preset returns the link to the scenario like everything else (control panel Decision 17), then applies its own link changes. A lockout is cleared by a preset |

## Behaviour

### Layout

Every view shares a status bar at the top. Below it is a tab bar, then the view. At phone width the tab bar scrolls sideways and cards stack in one column.

| View | Content |
| --- | --- |
| Overview | The power-flow diagram and the equipment cards |
| Faults | The fault catalogue |
| Settings | Settings and commands, with a filter |
| Registers | The register table |
| Traffic | Counters, connected clients and the request log |
| Link | The link faults and the module state |
| Scenario | Presets, set the simulated time, reset the energy counters, reset to the scenario, export |

### Status Bar

| Item | Shows | Does |
| --- | --- | --- |
| Simulator | Answering or not answering | — |
| Module | Online, or the link fault in force: offline, unresponsive, locked out | Opens the Link view |
| Clients | Connected client count, the live request rate and the time since the last request, for example `1 client · 38/min · 2 s ago` | Opens the Traffic view |
| Time | Simulated date and time | Opens the Scenario view |
| Run | Running or paused | Play and pause. Pause sets the speed to 0, play restores the speed from before the pause, or 1 if there was none |
| Speed | The current speed | 1×, 10× and 60× buttons and a field for any other speed |
| Faults | Count of active fault bits and non-zero pack codes | Opens the Faults view filtered to active faults |
| Changed | One chip for each kind of change from the scenario that is in force: holds, faults, settings, variation, link, each with a count | Opens the place where it was changed |
| Reset | — | Reset to the scenario, after a confirmation |

The state gains a `changes` summary from the machine: the holds in force, the active fault count per equipment, the settings, variation parameters and link settings that differ from the scenario, by name. The page uses it for the chips and to mark each changed row and card.

### Power-Flow Diagram

An inline SVG with the inverter in the middle and a node for each piece of fitted equipment: solar, grid, house, and the battery and EV charger where fitted. Each node shows its power, and the battery its state of charge.

| Flow | Colour token | Direction |
| --- | --- | --- |
| Solar | `--solar` (amber) | Solar to inverter |
| Grid import, export | `--grid` (blue) | Grid to inverter when grid power is positive, inverter to grid when negative |
| Battery charging | `--charge` (green) | Inverter to battery when battery power is negative |
| Battery discharging | `--discharge` (purple) | Battery to inverter when battery power is positive |
| EV charging | `--ev` (teal) | Inverter to EV charger |
| House | `--text` | Inverter to house |
| No flow | `--idle` (grey) | A line without movement when the rounded power is 0 |
| Fault | `--fault` (red) | The node's outline when its equipment has an active fault |

The description lists the nodes of the fitted equipment, each with its kind and the readings it shows, and the state gives those readings by the same names. The page holds the drawing of each kind of node, but no reading names and no list of equipment.

Direction is shown by dashes moving along the line, with a CSS animation. The same colour tokens are used for these flows everywhere on the page. Clicking a node scrolls to its card and opens it.

### Equipment Cards

One card per fitted piece of equipment. Each card has a large live value, its primary controls, a disclosure with the rest, its active faults with a link to the Faults view, a mark when it differs from the scenario, and a reset.

| Card | Live value | Primary controls | Behind the disclosure |
| --- | --- | --- | --- |
| Solar | PV power | PV hold, peak scale, cloud cover depth | The other solar variation parameters |
| House | Household load | Load hold, base and peak load | The other load variation parameters |
| Grid | Grid power, voltage and frequency | Voltage and frequency holds, nominal voltage and frequency | The other grid variation parameters |
| Battery | Battery power, state of charge | State of charge | Pack fault and warning codes |
| EV charger | Charger power, car plugged in or not | Plug in with an energy need, unplug | — |
| Inverter | Operating mode and application mode | Application mode | Seed |

Setting values and live readings are kept apart on every card: a control is labelled with what it sets, and the reading it produces sits beside it under its own label. For example, the solar card shows peak scale 100% and cloud cover depth 25% as settings, and PV power 8970 W as the reading.

Each variation row keeps its slider and number field in step, shows its scenario value, and has a reset to that value. The description lists the cards. Each variation parameter, hold and piece of fault equipment names its card, and each parameter says whether it is primary. The page therefore holds no list of parameters and no card contents; the table above is what the description gives for today's models.

A card's reset returns its variation parameters, holds and fault bits to the scenario with `POST /api/reset/<card>`. The state of charge, the car, the clock and the energy counters carry on, as with a preset. The inverter card's reset covers the seed and the inverter's fault bits. Settings are not reset by a card.

### Fault Catalogue

One list of every fault bit of the fitted equipment, with a search over name, register and bit, a filter by equipment, and an "active only" switch.

| Column | Content |
| --- | --- |
| Fault | The name, for example "Battery overtemperature" |
| Equipment | Inverter, battery, EV charger |
| Register and bit | For example `0x400B` bit 4 |
| Effect | What the simulator does when it is set, from the fault table: "Inverter stops", "Runs off-grid", "Meter A lost", "No charging", "No discharging", "No charging or discharging", "Charger stops" or "Bit only" |
| State | A switch |

Reserved bits come after the named ones, grouped by register and collapsed. Pack fault and warning codes stay number fields per pack, because no bit table names them. "Clear all faults" stays at the top. The description gains each bit's effect.

### Settings

Settings and commands as today, with a filter over name and address, a mark on each setting that differs from the scenario, its scenario value, and a reset to it. The description gains each setting's scenario value.

### Register Inspector

`GET /api/registers` returns every block of the device: its start, end, name and, if it is refused, the exception code and whether the model or a link fault refuses it. For each field of a block that answers: address, name, encoding, scale, access (read-only, writable, command), the raw words and the decoded value with its label, and when a client last read it.

The table shows one row per field, grouped by block.

| Column | Content |
| --- | --- |
| Address | `0x4031`, and the end address for a field of more than one word |
| Name | The field name |
| Raw | The words in hexadecimal |
| Value | The decoded value with its unit scale applied and its label, for example `6 EMS` |
| Type | Encoding and access |
| Read | Time since a client last read it, or "never" |

- A filter over name and address, a block filter, an access filter and a "changed only" switch.
- A cell whose value changed since the last refresh is highlighted for two seconds.
- Each row can copy its raw words or its value.
- A writable row links to its control in the Settings view.
- A switch shows the words inside a block that have no field, as `reserved`, reading 0 as the device serves them.

### Traffic

The simulator's Modbus server records every connection event and every request, in order, with a sequence number.

| Entry | Content |
| --- | --- |
| Connection | Time, client address and port, connection number, and the event: opened, closed by the client, closed by the module (and why: link fault, lockout, malformed frame), refused (offline, lockout, client limit) |
| Request | Time, client, connection, transaction id, unit id, function code, start address, count, the answer (registers returned, exception and code, no answer, connection dropped, ignored for another unit), the link fault applied, any late duplicate sent, and the time to answer in milliseconds |
| Request detail | For a read, the fields covered and the words returned. For a write, the words written and each field with its decoded value |

`GET /api/traffic?after=<sequence>` returns the entries after that sequence, at most 500, and the counters. `POST /api/traffic/reset` clears both.

Counters, in total and per client address:

- Connections opened, closed and refused.
- Requests, reads, writes, registers read and registers written.
- Exceptions by code, no answers and dropped connections.
- Requests in the last 10 seconds and the last 60 seconds, and the highest 60-second count since the counters started.
- The time of the last request.

- A history of request counts in 10-second buckets for the last 30 minutes, in total and per client, split into answered, exception and no answer or dropped.

The Traffic view shows, from the top:

- The live rate in requests per minute (the last 60 seconds), large, with the registers per minute and the peak beside it.
- A graph of requests over time from the history: an inline SVG bar per 10-second bucket, stacked by answered, exception and no answer or dropped, with a per-client filter. While a lockout is set, its threshold is drawn on the graph as a line, scaled to the bucket, so you can see how close a client comes to it.
- The other counters and a list of connected clients.
- The log, newest first.

The status bar's Clients item also shows the live rate, for example `1 client · 38/min · 2 s ago`. The log can be filtered by function code, address range, client and "errors only", and paused so it stops scrolling. A row opens to its detail.

Field reports describe module load in requests, and whether the size of a request also matters is unknown. The counters show both, so either can be compared with what a module tolerates.

### Link Faults

The simulator's Modbus server stands for the communication module the client connects to. The link settings make it behave as modules have in the field. All are off in a scenario that does not set them.

| Setting | Behaviour | Field report it reproduces |
| --- | --- | --- |
| Latency and jitter (ms) | Each answer waits the latency plus or minus up to the jitter | Modules that answer slowly |
| No answer (chance) | The request is read and never answered. The connection stays open | A module that stops answering |
| Busy (chance) | The answer is exception `0x06` | Busy answers |
| Device failure (chance) | The answer is exception `0x04` | Device failure answers |
| Dropped connection (chance) | The module closes the connection instead of answering | Modules that close the connection |
| Late duplicate (chance) | After an exception answer, the same frame is sent again before the next answer | A module that sent a second, late answer to a request it had answered with an exception |
| Refused blocks | A list of register blocks, each with an exception code from 0 to 255. A read or write of the block answers that code | A firmware that refuses one block; devices that answer non-standard codes, including 0 |
| Unresponsive | Connections are accepted and nothing is ever answered | An unresponsive module |
| Offline | The module stops listening and closes every connection. A connect is refused | A module that is gone |
| Intermittent offline | Offline for a set number of seconds in every period of a set length | A module that drops off the network |
| Lockout | When a client sends more than a set number of requests in a set window, the module closes its connection and refuses that client's address, or every client when "whole port" is chosen, until "Reset module" | A module polled too hard that closed port 502 or refused the client's address until it was given a new address |

Exception codes become plain byte values in the transport instead of the closed set of named codes, so any code a device sends can be served. The named codes stay as named constants.

A chance is a percentage. Whether it applies to a request is drawn from a generator seeded by the simulation seed and the request's sequence number since start. The checks run in this order, and the first that applies decides the answer: offline, unresponsive, lockout, dropped connection, no answer, refused block, device failure, busy. Latency applies to every answer that is sent.

The `link` scenario section holds these settings and replaces `server.response_delay_ms` with `link.latency_ms`. The Link view sets them, shows the module's current state, and has "Drop connections now" and "Reset module". Link settings and a lockout are saved with the running state and exported with the scenario.

New presets, offered on every model:

| Preset | Link changes from the scenario |
| --- | --- |
| Slow link | Latency 800 ms, jitter 400 ms |
| Flaky link | No answer 5%, dropped connection 2% |
| Busy module | Busy 10%, late duplicate 100% |
| Module offline | Offline |
| Module locked out | Lockout at more than 120 requests in 60 seconds, whole port |

No field report gives the load at which a module locks out. It only says a full scan every 15 seconds with retries was enough. The preset's threshold is a starting point that can be changed on the page. It is not taken from any limit of the integration.

### Visual Design

The current page is hard to read. These problems are on it today, and each one has a fix:

| Today | Change |
| --- | --- |
| Small, low-contrast grey text on a dark background, with addresses and scenario values smaller still | Every text and its background meet WCAG AA contrast (4.5:1, and 3:1 for large values), muted text included, in both themes. Nothing smaller than 12px |
| Sliders and checkboxes in the browser's default orange beside blue buttons | `accent-color` set to the page accent, so every native control matches |
| One narrow 1100px column with empty space either side, and a very long scroll | The content uses the window width: cards in a responsive grid, two or three columns on a desktop, one at phone width |
| The label at the far left and its control in the middle of the row, with the value far from both | Label, control, unit and scaled value sit together. Long rows of sliders become cards (see Equipment Cards) |
| Raw field names such as `ems_battery_charge_current_limit` as the only label | The name is shown as words ("Ems battery charge current limit") with the field name and address beside it in the monospace face. The page derives this; the description is unchanged |
| A scaled value shown with floating-point noise, for example `= 6.5535000000000005` | The state rounds each scaled value to the decimal places of its scale, so it reads `= 6.5535` |
| Every button the same filled blue whatever it does, including "Run" on factory reset and "Reset to scenario" | Three button kinds: primary for the main action of a card, secondary for the rest, and danger, with a confirmation, for factory reset, restart, clear fault history, reset to the scenario and reset energy counters |
| Fault and hold checkboxes in dense columns | Switches with the fault name as the label, in the catalogue's rows |
| Readings run together on one line in the header | The status bar and the diagram replace them |

- Colour tokens on `:root` with light and dark values: background, surface, raised surface, line, text, muted text, accent, the flow colours above, fault and idle. The dark theme is a soft slate rather than near-black, with clearly lighter cards.
- An 8px spacing scale. Cards on a raised surface with a border and a heading.
- A type scale: 14px body, 16px card headings, 20px view headings, 24px live values on cards, and a monospace face for addresses and raw words.
- Number fields wide enough for their largest value. Inputs, selects and buttons share one height.
- Toasts in a corner for each change: what changed on success, the reason on refusal. At most three at once, each gone after four seconds. A refusal also stays next to its control as today.
- Icons from the vendored Tabler set, inlined so they take the text colour.

## Code Changes

| Area | Change |
| --- | --- |
| New `traffic.py` | The recorder: entries with sequence numbers in a bounded log, the counters, the rolling windows, and the last read time per address. Takes time as an input |
| New `link.py` | The link settings, the module state (offline, unresponsive, lockout), the seeded draw per request, and the decision for each connection and request. Takes time as an input |
| `transport.py` | Asks the link before accepting a connection and before answering a request, applies its decision, sends late duplicates, and reports every connection event and request to the recorder. Exception codes as byte values. Offline stops and restarts listening |
| `exceptions.py` | `ModbusError` carries any byte as its code. The named codes stay |
| `device.py` | A read of every field without the observer, for the register snapshot |
| `description.py` | Whether each variation parameter is primary, each setting's scenario value, each fault bit's effect, the cards that apply, the link settings with their bounds, and the register snapshot |
| `machine.py` | Scaled setting values rounded to their scale's decimals, the `changes` summary in the state, the card resets, link settings in the state and the snapshot, presets that set the link |
| `presets.py` | The link presets |
| `scenario.py` | The `link` section, `server.response_delay_ms` removed, export of the link |
| `persistence.py` | Link settings and the lockout in the saved state |
| `service.py` | Builds the recorder and the link and hands them to the server and the panel |
| `panel.py` | Static files under `/static/`, `GET /api/registers`, `GET /api/traffic`, `POST /api/traffic/reset`, `POST /api/link`, `POST /api/link/drop`, `POST /api/link/reset`, `POST /api/reset/<card>` |
| `static/` | `index.html`, `panel.css`, and modules for the shared parts (requests, state, toasts, icons, status bar) and each view |
| `static/vendor/tabler/` | The SVG files used, Tabler's `LICENSE`, and a `README.md` naming the release they came from |
| `Dockerfile` | Copies the whole `static/` folder |
| `tests/modbus_mock/smoke.sh` | Also fetches `/api/registers`, `/api/traffic` and `/static/panel.css` |
| `documentation/development.md` | The views, the inspector, the traffic log, the link faults and their scenario section, the new presets, and the vendored icons |

## Verification And Acceptance

Unit tests, each on one module with collaborators replaced:

- Traffic: each kind of entry is recorded with its fields; the log keeps the last 2000; `after` returns only later entries and at most 500; each counter, per client and in total; the 10- and 60-second windows slide; the peak is kept; each request lands in its 10-second bucket by outcome, and buckets older than 30 minutes are dropped; reset clears everything; the last read time per address.
- Link: each setting gives its decision; the order of checks; a chance of 0 never applies and 100 always does; the same seed and sequence give the same draws; intermittent offline follows its period; lockout starts above the threshold in the window, refuses the client or the whole port, and ends only on reset.
- Transport, over fake streams and a fake sleep as its tests do today, with no socket and no real time: each link decision is carried out on the wire (no answer, dropped connection, exception codes including 0 and codes above `0x80`, late duplicate after an exception, refused connection, latency); every connection event and request reaches the recorder; with no link fault the answers are as today.
- Device: the snapshot read returns the same words as a client read and does not call the observer.
- Description: the new fields for each model; only fitted equipment's cards.
- Machine: a scaled setting value has no more decimals than its scale, for example raw 65535 at scale 0.0001 gives 6.5535; `changes` reports each kind of change and clears on reset; each card reset returns only its parameters, holds and faults and keeps the state of charge, the car, the clock and the counters; presets return and set the link and clear a lockout.
- Scenario: the `link` section parses, refuses bad values with the key, and exports back to the same settings.
- Persistence: link settings and a lockout survive a restart.
- Panel: each new route calls its module and answers; a refused request answers 400 and changes nothing; static files are served.

Smoke: `make mock-smoke` as above.

Manual acceptance, in `make up`:

1. Both pages are comfortable to read in light and dark themes and at phone width, every native control is in the accent colour, and every danger button asks first.
1. Both pages open on Overview, each with only its fitted equipment. The diagram's flows move in the right direction and colour, and change when PV is held at 0 or the state of charge is set to 100%.
2. Hold PV. The status bar shows a hold chip and the solar card is marked. The card's reset releases it and the chip goes.
3. Pause, then play. The time stops and resumes at the earlier speed.
4. Search the Faults view for "temperature", set one, and see it counted in the status bar, on its card's node and in Home Assistant. "Clear all faults" clears it.
5. The Registers view shows the battery state of charge changing, highlighted, with the time Home Assistant last read it.
6. The Traffic view shows Home Assistant's connection and reads, with counters, its live requests per minute and a graph of its requests over time that grows every 10 seconds. A setting changed from Home Assistant shows as a write with its decoded value.
7. Apply "Busy module". Home Assistant sees busy answers and late duplicates, and the Traffic view shows both.
8. Refuse one block with code 0. Home Assistant shows only that block's entities unavailable.
9. Apply "Module locked out". Home Assistant's connection is refused and the status bar shows the lockout. "Reset module" lets it reconnect.
10. Restart the containers. Link settings and a lockout are kept; the traffic starts empty.

`make ci` passes.

## Roadmap Changes

None.

## Revision History

| Revision | Date | Change |
| --- | --- | --- |
| 1 | 2026-10-16 | First draft |
