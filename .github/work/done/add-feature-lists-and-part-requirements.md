# Add Feature Lists And Part Requirements For The Integration, Cards And Simulator

## Plan Metadata

- **Revision:** 1
- **Status:** Approved
- **Roadmap item:** None. The feature lists are the base of the roadmap item "User documentation", planned in `add-user-and-developer-documentation.md`.
- **Last revised:** 2026-10-22
- **Requirements:** None are added, changed or removed. The feature lists record what is built. The requirements in `../requirements.md` move, byte for byte, into one global and three part requirement documents.
- **Code style:** `../code-style.md`
- **Source design:** the done plan `add-feature-lists.md` of the sibling project ha-energy-mpc (revision 4). The format, rules and phases below are copied from ha-energy-mpc as closely as this project allows. Every difference is named under "Differences From ha-energy-mpc".
- **Approval record:** None. Revision 1 has not been approved by the user.

## Outcome And Acceptance

Each of the three parts of the repository gets a plain-language list of what the part does today, and the agent instructions make every change keep the lists current. The requirements are split the same way: each part gets a requirement document whose sections match the part's feature list, and the requirements that span parts stay in one global requirement document. The feature lists and requirement documents link to each other section by section.

The work is accepted when:

1. These files exist:
   - `custom_components/saj_local/docs/features.md` (the integration, including the SAJ library in `custom_components/saj_local/saj/`)
   - `frontend/docs/features.md` (the cards, the tile card feature and the badge)
   - `mock/docs/features.md` (the simulator and the simulator page)
2. Each `features.md` is split into sections. Each section has a heading, an overview of one to three sentences, a `Files:` line linking to one or more files that implement the section, and a bullet list of implemented features and capabilities.
3. Every bullet describes something a user or developer can observe, in plain words, without module, class, function or file names. Every bullet is true of the code at the time of the change. Nothing that is only required, planned or partly built is listed.
4. Where the HS3 and the H2 differ, the bullet says so, for example "The EV charger controls exist on the HS3 only."
5. Each part has an `AGENTS.md` beside the part's `docs/` folder: `custom_components/saj_local/AGENTS.md`, `frontend/AGENTS.md` and `mock/AGENTS.md`. Each nested `AGENTS.md` holds the rules for the part's feature list and the rules that concern only that part.
6. The root `AGENTS.md` holds only general rules, including the general feature list rule, and no rule that concerns one part only.
7. These requirement documents exist:
   - `.github/work/requirements.md` (global)
   - `custom_components/saj_local/docs/requirements.md` (the integration)
   - `frontend/docs/requirements.md` (the cards)
   - `mock/docs/requirements.md` (the simulator)
8. Every requirement block of the current `.github/work/requirements.md` is in exactly one of the four requirement documents, byte for byte identical, except that Prettier may change the indentation of nested bullets in `frontend/docs/requirements.md`. No requirement block is dropped, changed, added or duplicated. The byte check in "Verification Strategy" proves the move.
9. Each part requirement document follows "Requirement Document Format" and links to the global requirement document.
10. Each `features.md` section with a matching requirement section links to the requirement section, and each requirement section with a matching feature section links back.
11. Every reference to `.github/work/requirements.md` outside `.github/work/done/` names the right document after the split.
12. `make ci` passes, including `prettier`, `copy-paste`, `release-check` and `validate`.

## Existing Baseline

- No feature list exists. What is built is spread across `README.md` (372 lines), `documentation/development.md` (449 lines), the done plans in `.github/work/done/`, the code and `custom_components/saj_local/translations/en.json`.
- `README.md` contradicts itself on the entity count of an HS3 with every optional piece of equipment: 712 entities at line 87 and 742 at line 103. The feature lists take the number from the code.
- The root `AGENTS.md` holds every agent rule. No nested `AGENTS.md` exists. `CLAUDE.md` is listed in `.gitignore` and no `CLAUDE.md` is in the repository.
- `.github/work/requirements.md` (110 lines) has the headings Functional (with Main Integration, Entity IDs, Writing and Modbus Mock), Non Functional and Assumptions. The headings carry no numbers, and no requirement text cites another section by number.
- The requirements are bullet lists. Some top-level bullets carry nested bullets, for example "Expose UI elements that can be added to lovelace dashboards" and "Dangerous changes are never made from Home Assistant".
- `.github/scripts/release_check.py` zips the whole `custom_components/saj_local/` folder, so files added under the folder ship in the HACS archive. `mock/Dockerfile` copies only `saj_local_mock/`, `static/` and one scenario, so `mock/docs/` stays out of the simulator image.
- `make prettier` runs `prettier --check` inside `frontend/`, so Markdown in `frontend/` must be Prettier-formatted.
- `make copy-paste` (jscpd, `.jscpd.json`, 5 lines and 50 tokens minimum) scans Markdown too, and `.github/work/` is never excluded.
- `.github/work/requirements.md` is named in the root `AGENTS.md` (lines 29, 120 and 134), `CONTRIBUTING.md` (line 53) and `documentation/development.md` (line 11, and line 161 names "the Non Functional section of `requirements.md`").

## Boundaries And Decisions

- Documentation and agent instructions only. No integration, card or simulator behaviour changes.
- The feature lists are written from the code, never copied from `requirements.md`, `README.md`, `documentation/development.md` or done plans. A requirement that is not built is not a feature. `README.md` and `documentation/development.md` are read only as pointers to what to check in the code.
- The SAJ library is part of the integration's feature list, because a user sees what the library does only through the integration. The library's own requirements (separation from Home Assistant) go into the integration requirement document.
- The simulator's feature list describes the simulator only. The root `AGENTS.md` rule that `mock/` has no authority over requirements or Modbus design decisions still applies: the simulator's features never justify integration design.
- Writing follows the project's tone-of-voice guide, with British spelling and the terms the integration's translations use, for example "Allow control", "Meter A" and "power control".
- `custom_components/saj_local/docs/features.md`, `custom_components/saj_local/docs/requirements.md` and `custom_components/saj_local/AGENTS.md` ship in the HACS archive. `release_check.py` and the release archive do not change.
- The requirement split moves text only. Every requirement keeps the requirement's exact bytes and meaning, except the nested-bullet indentation Prettier sets in `frontend/docs/requirements.md`. The new headings, blank lines, the link to the global requirement document, the part links and the section cross-links are the only new text in the requirement documents.
- The split never edits requirement text, to fix wording or a misplaced requirement. A problem found during the move is reported to the user, never fixed in the same change.
- Done plans in `.github/work/done/` are history and are not edited.
- The plan `add-user-and-developer-documentation.md` builds on the feature lists and is not changed by this plan.

## Differences From ha-energy-mpc

| ha-energy-mpc | This plan | Reason |
| --- | --- | --- |
| A requirement block is a paragraph, a list with the sentence that introduces the list, or a table | A requirement block is a paragraph, or one top-level bullet together with the bullet's nested bullets | The requirements of this project are long bullet lists that mix topics, so a whole list cannot move into one section |
| The old headings move with their blocks as `###` headings, and a Phase 5 cleanup round removes the old headings and rewrites section number references | No old heading moves and there is no cleanup round | The old headings carry no numbers and no requirement text cites a section by number, so nothing needs the old headings to stay findable |
| `.github/work/nfrs.md` is merged in and deleted | Not applicable | The non-functional requirements already sit in `.github/work/requirements.md` |
| The local `CLAUDE.md` link is deleted | Not applicable | No `CLAUDE.md` is in the repository |
| `.github/work/nomenclature.md` governs wording | The integration's translations and the project's tone-of-voice guide govern wording | This project has no nomenclature document |
| Simulator in `dev/custom_components/energy_mpc_simulator/` | Simulator in `mock/` | The simulator of this project is a standalone Modbus service, not a Home Assistant integration |

## Feature List Format

Each `features.md` follows this shape:

```markdown
# <Part> Features

What the part is, in one or two sentences.

## <Section>

What the area does overall, in one to three sentences.

Files: [<file>](<relative path>), [<file>](<relative path>)

Requirements: [<Section>](requirements.md#<anchor>)

- <A concrete capability, in plain words.>
- <Another capability.>
```

Rules for the content:

- One bullet per capability a user or developer would recognise. Detail of a single logic path is left out.
- No technical vocabulary where a plain word exists. Terms the integration shows to users, such as Allow control, Meter A, Meter B and power control, are used as the translations spell the terms.
- A limitation a user would trip over is stated inside the bullet, for example "Commissioning settings are shown but cannot be changed."
- A difference between the HS3 and the H2 is stated inside the bullet.
- No requirement wording, dates, plan names or roadmap claims.
- Every section has a `Files:` line, after the overview, with one or more Markdown links to the files that implement the section. Each link is a path relative to the `features.md` file and points to a whole file: no line numbers, line ranges or anchors, because those go stale as the code changes. The bullets themselves name no file.
- A section that has a matching section in the part's `requirements.md` has a `Requirements:` line after the `Files:` line, linking to the matching section by the section's heading anchor. Section names match exactly, so the heading anchor stays valid. A section with no matching requirement section has no `Requirements:` line.

## Initial Sections

The sections below are the starting outline from the investigation. The Developer confirms each section and every bullet against the code, merges or splits sections where the code makes the split clearer, and leaves out anything the code does not do. A section that is renamed is renamed in the matching requirement section and in the "Placement" table of this plan in the same change.

### Integration (`custom_components/saj_local/docs/features.md`)

1. **Setup and detection:** adding a system by host, port and unit ID, automatic detection of the HS3 and the single-phase H2, choosing a model by hand and the checks on a manual choice, the six core readings setup needs, several systems in one Home Assistant.
2. **Devices and entities:** one device per system, the eight entity types, which entities are enabled by default, entity categories, packed registers read once, the shared sign for battery and grid power, values outside a range and unknown codes.
3. **Optional equipment:** detection of the battery, Meter A, Meter B, the parallel system and the EV charger (HS3), remembered equipment and the repair issue when equipment goes missing, the Equipment section of Configure, H2 battery pack count.
4. **Entity IDs and prefix:** the fixed entity ID form, the optional unique prefix, changing the prefix with the warning, history kept across a rename.
5. **Polling:** the default update interval and the 10-second floor, polling groups with their own cadence, a disabled entity not being read, the request load shown before saving.
6. **Protecting the inverter:** one connection and one request at a time, the ceiling of 40 requests in any 60 seconds, no retries inside a cycle and the growing wait after a failed cycle, neighbouring registers read in one request, refused registers and the repair issue naming the entities.
7. **Changing settings:** Allow control per system and the warning with the added request load, controls enabled and disabled with Allow control, the control set, read-back after a change, the three failure outcomes, commissioning settings read-only, rate-limited changes, a system with an unverified model never written to.
8. **EMS:** EMS functions switched on from Home Assistant kept alive by the heartbeat, the configurable heartbeat interval, EMS functions switched off when Home Assistant stops, EMS on the HS3.
9. **Power control:** holding the battery, the grid connection point or the inverter at a set power in watts on every model that can, following a schedule helper.
10. **Model replacement:** moving a system between an H2 and an HS3 through Configure, keeping the device, entities, names and history.
11. **Device faults and repairs:** fault entities for the inverter, the battery and the EV charger, fault summaries, repair issues for faults.
12. **Diagnostics and debug logging:** the diagnostics download and what is kept private, the debug dump, debug logging, error messages.
13. **Cards:** one bullet saying the integration serves the card bundle with no resource to add, linking to `frontend/docs/features.md`.

### Cards (`frontend/docs/features.md`)

1. **Elements and setup:** the elements in the card picker, choosing a system, an element showing only what the system has, keeping working when the prefix changes, the card editors.
2. **Power flow card**
3. **Status card**
4. **System card**
5. **Faults card**
6. **Battery card**
7. **Controls card:** including the control lock shown when Allow control is off.
8. **Schedule card**
9. **Weekdays tile card feature**
10. **Status badge**
11. **Theme and language:** Home Assistant theme variables, the card texts per language with English as the fallback, entity names and states from Home Assistant.

### Simulator (`mock/docs/features.md`)

1. **Simulated models:** the HS3 and the H2 as standalone Modbus TCP services, the registers each model serves.
2. **Scenarios:** the shipped scenarios in `mock/scenarios/`, optional equipment, battery size, parallel inverters, off-grid mode.
3. **Variation:** deterministic random variation from a seed, the bounds, depth and speed of the variation.
4. **Control page:** setting every writable setting, faults on and off, forcing readings, resetting counters and the clock, the refresh of current values.
5. **State and presets:** changes kept across restarts, resetting the whole simulator or one piece of equipment, presets, exporting the running state as a scenario.
6. **Register inspector and traffic log:** every register with raw and decoded value, every connection and request with answers, counts and rates per client.
7. **Link faults:** slow and missing answers, busy and non-standard exceptions, refused blocks, dropped connections, late duplicates, an offline or unresponsive module, the lockout, set in the scenario or on the page.

## Agent Files

### Root `AGENTS.md`

- Add a section **Feature Lists**:
  - Each part keeps `docs/features.md` and the part's own `AGENTS.md`: the integration, `frontend/` and `mock/`. Name the three paths.
  - A change that adds, changes or removes a capability updates the part's `features.md` in the same change. A change with no observable effect does not.
  - Every section of every `features.md` links to one or more files that implement the section, as whole files with no line numbers.
  - Matching sections of a `features.md` and the part's `requirements.md` link to each other. The ban on anchors applies to code links only.
  - The feature lists record what is built. The requirement documents record the goal. Neither is written from the other.
  - Before working in a part, read the part's `AGENTS.md`.
- Update "Project Requirements Authority" and "Project Documentation" to name the global requirement document first and the three part requirement documents after the global one, and say that a requirement change goes into the part document whose section the change concerns, or the global document when the change spans parts.
- Update "Repository Layout" with each part's `docs/features.md`, `docs/requirements.md` and `AGENTS.md`.
- Move out the part-only rules listed below. Moved text is removed from the root, not copied, so `make copy-paste` finds no duplicate.

### Rules moved out of the root

| Rule in root `AGENTS.md` today | Moves to |
| --- | --- |
| "Stored Forms" section, whole | `custom_components/saj_local/AGENTS.md` |
| Project Requirements Authority: "`mock/` on the other hand, must not be designed around the integration. It must be built firmly around documented SAJ controller behaviour and specifications." | `mock/AGENTS.md` |

Rules that stay in the root because the rules span parts: Critical Rules, Backwards Compatibility, the rest of Project Requirements Authority (including the rule that `mock/` has no authority), Feedback, Requesting Decisions, Verification workflow, Efficient reading, Bumping the Home Assistant version, Repository Layout, Completed Work Index, Project Documentation, Implementation Plans and Commit Message Guidelines.

### Nested `AGENTS.md` files

Each nested file holds, in this order:

1. One sentence on what the part is and that the root `AGENTS.md` also applies.
2. **Feature list:** the path of the part's `features.md`, who reads the list, what belongs in the list for the part (for the integration: what a Home Assistant user sees and can do, with HS3 and H2 differences; for the cards: what the user sees and can set on each element; for the simulator: what is simulated and what can be set on the page or in a scenario), and the format rules from this plan.
3. **Requirements:** the path of the part's `docs/requirements.md` and the cross-link rule.
4. The part-only rules moved from the root.

Each nested file words the feature list rules for the file's own part, so no block of five lines repeats across the files.

## Requirement Split

### Documents

| Document | Holds |
| --- | --- |
| `.github/work/requirements.md` | Requirements that span parts, and links to the three part documents |
| `custom_components/saj_local/docs/requirements.md` | Integration requirements, including the SAJ library and the integration's non-functional requirements |
| `frontend/docs/requirements.md` | Card requirements |
| `mock/docs/requirements.md` | Simulator requirements |

### What moves

- A requirement block is a paragraph, or one top-level bullet together with the bullet's nested bullets. A block moves whole and is never split.
- The old headings (Functional, Main Integration, Entity IDs, Writing, Modbus Mock, Non Functional and Assumptions) do not move. The new section headings replace the old headings.
- Inside a new section, blocks keep the order the blocks had in the old document.

### Requirement Document Format

```markdown
# <Part> Requirements

Global requirements: [requirements.md](<relative path to .github/work/requirements.md>)

## <Section>

Features: [<Section>](features.md#<anchor>)

<moved requirement blocks, byte for byte>
```

- A section whose name matches a section of the part's `features.md` uses exactly the matching name and has a `Features:` line. A section for something with no feature list section has no `Features:` line. Feature-matched sections come first, in the order of `features.md`, then the other sections.
- No overview or other new prose is added, so nothing new can be read as a requirement.
- The global document keeps the title "SAJ Integration" and gains a section "Part Requirements" that links to the three part documents.

### Placement

Blocks are named by the first words of the block. "All" means every block under the old heading.

**Global (`.github/work/requirements.md`)**

| New section | Blocks |
| --- | --- |
| Purpose and scope | Preamble: "High level requirements is to provide", "Development is done with HS3", "Platform stability and correctness"; Non Functional: "This HACS repository will be the sole repository" |
| Compatibility | Non Functional: "Backwards compatibility MUST drive", "**CRITICAL**: While this line is in place" |
| Model abstraction | Non Functional: "The different implementations of SAJ systems", "A feature is left out only on a model" |
| Language | Main Integration: "Full localisation and internalisation support", "English texts and keys use British spelling" |
| Development environment | Non Functional: "Development in completely isolated docker environment" |
| Testing | Non Functional: "100% unit test coverage", "**CRITICAL**: The 100% coverage MUST come", "A unit test exercises a single module", "Unit tests MUST be fast", "Integration tests MUST ONLY be used", "noqa or any other inline test", "DO NOT write unit tests that test hard coded values", "Playwright tests for UI covering only critical paths", "Playwright tests split into" |
| Verification | Non Functional: "All commands for things like building", "Once a release exists, `make ci` fails", "All testing and verification can run in github workflows" |

**Integration (`custom_components/saj_local/docs/requirements.md`)**

| New section | Blocks |
| --- | --- |
| Setup and detection | Main Integration: "Integration domain", "Convention over configuration", "Avoid extensive configuration options", "Automatic detection where possible"; Assumptions: "Connecting to multiple different modbus systems" |
| Devices and entities | Main Integration: "Each system is one Home Assistant device"; Non Functional: "Battery and grid power use one sign" |
| Entity IDs and prefix | Entity IDs: all |
| Polling | Main Integration: "Ability to read only certain sensors", "Ability to configure default sensor update cadence", "Ability to read selected sensors at a higher or lower cadence", "Ability to create one or more different sensor reading cadences" |
| Protecting the inverter | Main Integration: "Use intelligent modbus access" |
| Changing settings | Main Integration: "Target both reading and writing of registries"; Writing: "Writing is off for every new system", "Each system shows whether changes are allowed", "Switching writing on also enables", "A system whose model could not be verified", "Dangerous changes are never made from Home Assistant", "After a change, the entity shows", "A failed change says clearly", "Changes are rate limited"; Non Functional: "Controls are shared, not built per model" |
| EMS | Writing: "EMS functions switched on from Home Assistant" |
| Power control | Writing: "Power control (holding the battery", "Optionally, a power control function can follow" |
| Model replacement | Assumptions: "Users may upgrade, for example from H2 to HS3" |
| Diagnostics and debug logging | Main Integration: "clear and detailed errors", "extensive and useful debug dump tools"; Non Functional: "option to enable debug logging" |
| Cards | No blocks. The section links to `frontend/docs/requirements.md`. |
| SAJ library | Non Functional: "There must be a clear separation of concerns", "Despite SAJ being implemented as a stand alone" |

The integration sections Optional equipment and Device faults and repairs have no requirement block, so the integration requirement document has no section for either one and the two feature list sections have no `Requirements:` line.

**Cards (`frontend/docs/requirements.md`)**

| New section | Blocks |
| --- | --- |
| Elements and setup | Main Integration: "Expose UI elements that can be added to lovelace dashboards", with the four nested bullets |

**Simulator (`mock/docs/requirements.md`)**

| New section | Blocks |
| --- | --- |
| Simulated models | Modbus Mock: "A completely stand alone docker service", "This simulator must be able to be configured to simulate different", "We do not need to completely replicate" |
| Scenarios | Modbus Mock: "It must be able to be configured in various ways" |
| Variation | Modbus Mock: "Deterministic randomised behaviour" |
| Control page | Modbus Mock: "Each running simulator offers a web page", "The page can set every setting", "The page builds every control", "The page shows the current value" |
| State and presets | Modbus Mock: "Changes made on the page to the simulated system" |
| Register inspector and traffic log | Modbus Mock: "The page shows every register" |
| Link faults | Modbus Mock: "The simulator can reproduce the communication failures" |
| Code structure | Modbus Mock: "The page is a development tool" |

### References to the old document

- Root `AGENTS.md`: as listed under "Root `AGENTS.md`".
- `CONTRIBUTING.md` line 53: links the global document and the three part documents.
- `documentation/development.md` line 11: links the global document and the three part documents. Line 161: "the Non Functional section of `requirements.md`" becomes a link to the section Testing of the global document. No other word of the guide changes.
- Done plans are not edited.

## Phases

### Phase 1 — Agent files

- Edit the root `AGENTS.md` as listed above.
- Create the three nested `AGENTS.md` files with the moved rules and the feature list rules.

### Phase 2 — Feature lists

- Write the three `features.md` files from the code, starting from the sections above. Use `custom_components/saj_local/translations/en.json`, the catalogue and profiles in `custom_components/saj_local/saj/`, the config flow, the cards in `frontend/src/` and the simulator in `mock/` to check each bullet.
- Format `frontend/docs/features.md` and `frontend/AGENTS.md` with Prettier.

### Phase 3 — Requirement split

- Create the three part requirement documents and rewrite `.github/work/requirements.md` as the global document, placing every block as "Placement" lists.
- Format `frontend/docs/requirements.md` with Prettier and confirm the byte check still passes. Prettier re-indents nested bullets, which is the one difference the byte check allows.
- Update the references listed in "References to the old document".

### Phase 4 — Cross-links

- Add the `Requirements:` lines to each `features.md` and the `Features:` lines to each part requirement document.

## Verification Strategy

- `make ci` passes, with `prettier`, `copy-paste`, `release-check` and `validate` in particular.
- **Byte check.** A one-off script, kept in the scratchpad and not committed, splits the old `.github/work/requirements.md` (from `git show HEAD:`) and the four new requirement documents into blocks, a block being a paragraph or a top-level bullet with the bullet's nested bullets. The script drops the old headings from the old document, and the new headings and the `Global requirements:`, `Features:` and part-link lines from the new documents. The script ignores the leading whitespace of nested bullet lines, because Prettier re-indents them in `frontend/docs/requirements.md`. Apart from that, the two collections must be equal, byte for byte, with each block appearing once. Any difference fails the split. The script also confirms that each block sits in the section "Placement" names for the block.
- Every `Requirements:`, `Features:`, global and part link resolves to an existing file and an existing heading.
- In a new Claude Code session, read one file in each of the three parts and confirm the part's `AGENTS.md` is attached, and that the root `AGENTS.md` loads at start.
- The primary agent reviews every bullet of each `features.md` against the code and lists any bullet that is not true, not built, or technical.

## Risks And Guardrails

- **Lists drift from the code.** The root rule and the review check make the update part of every change. The plan `add-user-and-developer-documentation.md` adds a `docs-check` rule that fails when a feature list section has no documentation page.
- **A moved rule is missed.** A nested `AGENTS.md` loads only when a file in the part is read. The Stored Forms rule applies at the point the integration is changed, so the rule still loads when the rule matters.
- **A requirement is lost or altered in the move.** The byte check compares every block of the old document with the new documents and fails on any difference, including whitespace, other than the indentation of nested bullets.
- **Duplicate text.** The nested `AGENTS.md` files and the feature lists are scanned by `make copy-paste`. Each nested file words the rules for the file's own part.
- **Files ship to users.** The integration's `features.md`, `requirements.md` and `AGENTS.md` are installed with every release. All three are small text files Home Assistant ignores.

## Settled Decisions

- **Separate plan (2026-10-22):** The feature lists come in this plan, before the documentation plan, as in ha-energy-mpc.
- **Scope (2026-10-22):** The same scope as the ha-energy-mpc plan: feature lists, nested `AGENTS.md` files and the requirement split.

## Developer Task After User Approval

After the user approves this exact revision, carry out Phase 1, then Phase 2, then Phase 3, then Phase 4, then stop and report. Before starting, read `AGENTS.md` including the Code Style reference, `.github/work/code-style.md`, this feature plan and the project's tone-of-voice guide. Report the files changed, the sections and bullet count of each `features.md`, each statement in `README.md` or `documentation/development.md` that the code contradicts, the rules moved, the sections and block count of each requirement document, the byte check result and the `make ci` result.

## Revision History

- **Revision 1 — 2026-10-22:** Initial draft. Adds a feature list, a requirement document and an `AGENTS.md` to the integration, the cards and the simulator, splits `.github/work/requirements.md` into a global and three part documents byte for byte, and moves part-only rules out of the root `AGENTS.md`.
