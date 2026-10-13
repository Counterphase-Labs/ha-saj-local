# Add Debug Dump And Logging

## Plan Metadata

- **Revision:** 1
- **Status:** Approved
- **Last revised:** 2026-10-13
- **Requirements:** `../requirements.md`
- **Code style:** `../code-style.md`
- **Roadmap item:** "Debug dump and logging" in `../roadmap.md`
- **Builds on:** `add-device-faults-and-repairs.md` and the plans it builds on. Everything in those plans that is not restated or explicitly replaced here continues to apply.

## Outcome And Scope

A user who has a problem can send what the inverter is actually returning and a debug log that shows what the integration did, without giving away who or where they are.

| Need | Today | With this plan |
| --- | --- | --- |
| See the raw registers the system returns | Not possible. Diagnostics show decoded state only | Diagnostics include the latest raw words of every register the integration has read, including registers that are not entities, with their age, and every request that failed and why |
| Tell systems apart in the log | Library lines and most integration lines do not say which system they are about | Every line starts with the system's label, with the serial masked |
| Follow what happened in a debug log | Debug shows the cadence plan and detection at setup, then almost nothing per poll | One line per poll, per connection change, per write and per EMS beat, as set out below |
| Share logs and dumps safely | Diagnostics leave out host, serial and prefix. Logs carry the entry title, which defaults to the full serial | The serial, MAC, network addresses and EV charger serial never appear in a dump or a log line |

Included:

- A register memory in the library client that keeps the latest raw words of every read it makes and the last failure of every request that failed.
- A `private` marker on definitions, used by diagnostics and logging.
- A system label for log lines, passed into the library.
- Debug lines added where the policy below calls for them, and every existing line moved onto the label.
- Diagnostics additions, README and `documentation/development.md`.

Not changed: entities, translations, config and options flows, the mock, the browser smoke tests. No new Modbus request is made for any of this.

## Requirements

| Requirement | How it is met |
| --- | --- |
| Extensive and useful debug dump tools using native HA solutions that are privacy focused | Home Assistant's diagnostics download carries the raw register snapshot. Private rows and the serial are replaced by Home Assistant's redaction marker |
| Option to enable debug logging which will provide clear and helpful debug logs rather than spam | Home Assistant's own "Enable debug logging" on the integration page. Debug output is one line per event, not per request, and repeats nothing that has not changed |
| Use intelligent modbus access that does not put the system in danger of overload | The snapshot reuses words already read. It adds no request |
| SAJ implemented as a stand-alone library | Register memory, the private marker, serial masking and the labelled logger are library code using only the standard library. Diagnostics and the entry title stay in the integration |
| Connecting to multiple different modbus systems can happen | Every log line names its system |

## Decisions

Decisions 1 to 3 and 6 were made by the user on 2026-10-13. The others are set by this plan and listed so they can be challenged.

| # | Decision | Outcome |
| --- | --- | --- |
| 1 | What the register snapshot holds | Decided by the user: the latest reading, with no extra reads. The snapshot is what the integration last read, because a user with a problem has the entities concerned enabled, and showing what is actually happening matters more than covering every register. Registers no enabled entity needs are in it only where a poll bridges a gap inside a block |
| 2 | Models covered | Decided by the user: supported models only. The snapshot is the same on every installation; there is no extra mode for unrecognised devices |
| 3 | How a log line names its system | Decided by the user: the entry title and the serial masked to its last three characters, `xxxxx` plus those characters. Where the title contains the serial, as the default `SAJ <serial>` does, the serial in it is masked: `SAJ xxxxx123`. Otherwise the masked serial follows the title: `Garage (xxxxx123)` |
| 4 | Where reads are remembered | In the Modbus client, so polls, EMS beats, write read-backs, detection and identity reads all feed it. A Configure or repair validation uses its own client and is not remembered |
| 5 | How long the memory lives | For the life of the loaded entry. A reload starts empty. It is not persisted |
| 6 | A failed request | Decided by the user: every failure is remembered, not only refusals, by address, count and outcome with its age. The outcome is the exception code, `timeout`, `connection_lost` or `malformed_reply`. A dump then tells a refusal from no answer, which matters because the inverter accepts one Modbus TCP connection and another client holding it causes timeouts that look like unsupported registers. The entry is removed when the same range later answers. Words remembered earlier at those addresses stay, with their own age |
| 7 | What is private | Rows marked `private`: the Ethernet MAC address, the five Ethernet address rows and the EV charger serial. The inverter serial row (`0x8F03`, 10 words) is always private, because identity reads it and the H2 identity block contains it although it is not a catalogued row |
| 8 | How private words appear in the snapshot | The row is listed with its key, and its words are replaced by Home Assistant's redaction marker. The reader sees that the register exists and answered |
| 9 | Debug logging switch | Home Assistant's own per-integration "Enable debug logging". It already covers the library, whose loggers sit under the integration's package. No Configure option is added |
| 10 | Per-request log lines | None. Each poll logs one line listing its requests and outcomes |
| 11 | Values in log lines | No decoded values. Raw words appear only in the debug line of a write, and never for a private row |

## Behaviour

### Register Snapshot

Diagnostics gain `register_snapshot`:

- `registers`: one entry per remembered address range, ordered by address. A word that belongs to a catalogued row of the device is grouped under that row and carries its key. A word that belongs to no row is listed alone with no key. Each entry has the start address in hex, the words in hex, and the seconds since it was read.
- `failed`: one entry per remembered failed range, with its start address, count, outcome (Decision 6), the exception code when there is one, and the seconds since the failure.
- Private words are replaced as in Decision 8.

Example, abridged:

```json
"register_snapshot": {
  "registers": [
    {"address": "0x4000", "key": "inverter_clock", "words": ["0x07ea", "0x0a0d", "0x1530", "0x0c00"], "age_seconds": 4.1},
    {"address": "0x4004", "key": "operating_mode", "words": ["0x0002"], "age_seconds": 4.1},
    {"address": "0x0f04", "key": "ethernet_mac_address", "words": "**REDACTED**", "age_seconds": 61.0}
  ],
  "failed": [
    {"address": "0x3024", "count": 32, "outcome": "exception", "exception_code": 48, "age_seconds": 4.1},
    {"address": "0xa03c", "count": 32, "outcome": "timeout", "exception_code": null, "age_seconds": 64.3}
  ]
}
```

Diagnostics also gain `serial`, masked as in Decision 3, so a dump can be matched to a log.

### Log Lines

Every line, in the library and the integration, starts with the system label (Decision 3). The `SAJ` prefix on today's lines is replaced by it. Logger names do not change, so Home Assistant's switch still covers them all.

Levels:

| Level | Used for | Rule |
| --- | --- | --- |
| Warning | Something the user should act on or know went wrong | Once per transition, as today |
| Info | A change of state the user would want in a normal log | Once per transition, as today |
| Debug | What the integration did, for following a problem | One line per event below. Nothing else |

Debug events added. Existing debug lines (cadence plan, probe results, late frames, stale reconnect, EMS limits not read, dropped beats) stay, on the label.

| Event | Content |
| --- | --- |
| Identity read at setup and reconnect | Model, device type, rated power, detected or assumed. No serial |
| Connection opened, closed or reopened | The reason: setup, reconnect after failure, stale connection, validation, unload |
| Poll | Cadences due, each request as `address+count` with `ok`, its exception code or `timeout`, the cycle duration and the next wake-up |
| Back-off | The delay chosen and the consecutive failure count |
| Narrowing | The range split and the halves to be tried |
| Write | Key, address and raw words before sending. The outcome stays at its current level |
| EMS beat | The function and the target read back |
| Schedule helper change | The function and the state followed |

### Privacy

- Diagnostics and logs never contain the host, port, unit ID, full serial, MAC address, network addresses, EV charger serial or prefix.
- The existing diagnostics rule for the prefix is unchanged.

## Changes By Module

| Module | Change |
| --- | --- |
| `saj/definitions.py` | `private` on `Definition`, set on the rows in Decision 7 |
| `saj/catalogue.py` | `Register.private`. A function giving the private rows of a fit, plus the serial row |
| `saj/memory.py` (new) | The register memory: record answered words and failed ranges with their outcome and the client's clock, clear a failure when its range answers, and give the snapshot grouped by row with private words replaced |
| `saj/log.py` (new) | Serial masking and a `logging.LoggerAdapter` that prefixes the label, built from each module's own logger |
| `saj/client.py` | Feeds the memory on every read, answered or failed. Takes the labelled logger. Connection debug lines |
| `saj/poller.py` | Poll, back-off, narrowing and identity debug lines. Takes the labelled logger |
| `saj/control.py`, `saj/detection.py` | Take the labelled logger. Write debug line with private words masked |
| `__init__.py` | Builds the label from the entry title and the serial and passes it to the client and library objects |
| `coordinator.py`, `equipment.py`, `issues.py`, `entity.py`, `repairs.py` | Every line on the label. EMS beat and schedule debug lines |
| `diagnostics.py` | `register_snapshot` and `serial` |
| `README.md`, `documentation/development.md` | How to enable debug logging and download diagnostics, and what each contains and leaves out |

## Verification And Acceptance

Unit tests, multivariate where the input varies:

- Memory: words recorded with their read time; a later read replaces them; each failure outcome recorded and removed when its range answers; words grouped by row with keys, gaps listed alone; private rows and the serial row replaced.
- Masking: a title containing the serial, a title without it, a serial of three characters or fewer.
- Log adapter: the label is prefixed and the logger name is the module's.
- Client: answered reads and each kind of failed read reach the memory with their outcome; connection debug lines.
- Poller: one poll line with every request outcome; back-off and narrowing lines.
- Control: the write debug line, masked for a private row.
- Diagnostics: the snapshot and the masked serial; no private value anywhere in the output.
- Coordinator and setup: the label reaches the library objects; EMS beat and schedule lines.

Smoke: the existing per-model smoke test passes unchanged. No new browser test.

Acceptance:

1. An HS3 with default entities: diagnostics list the words of every request the default poll makes, each with its key or none, and an age under one poll interval.
2. Enabling an entity in another block and waiting one poll adds that block's words to the next download.
3. An HS3 with no EV charger and the EV charger set to Fitted in Configure: `failed` lists the EV data request with exception code 48.
4. No dump contains the serial, the MAC address, an IP address or the EV charger serial. The serial appears only as `xxxxx` plus its last three characters.
5. With two systems loaded and debug logging switched on, every line names one of the two labels, a poll writes one line per cadence run, and switching debug logging off downloads a log with no full serial or network address in it.
6. With another Modbus client holding the inverter's only connection, `failed` lists the poll's requests as `timeout` or `connection_lost`, not as exception codes.
7. No poll makes more requests than before this change.

## Implementation Order

1. `private` marker and the private rows in the catalogue.
2. `saj/log.py`: masking and the labelled logger.
3. `saj/memory.py` and feeding it from the client.
4. The label passed from setup into every library object, and every existing line moved onto it.
5. The new debug lines.
6. Diagnostics.
7. README and `documentation/development.md`.

## Revision History

| Revision | Date | Change |
| --- | --- | --- |
| 1 | 2026-10-13 | First draft |
