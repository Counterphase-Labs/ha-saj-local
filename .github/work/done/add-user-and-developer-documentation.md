# Add User And Developer Documentation

## Plan Metadata

- **Revision:** 2
- **Status:** Approved
- **Roadmap item:** User documentation
- **Last revised:** 2026-10-23
- **Requirements:** `../requirements.md` and the part requirement documents the global document links to: `custom_components/saj_local/docs/requirements.md`, `frontend/docs/requirements.md` and `mock/docs/requirements.md`
- **Feature lists:** `custom_components/saj_local/docs/features.md`, `frontend/docs/features.md` and `mock/docs/features.md`
- **Depends on:** `add-feature-lists-and-part-requirements.md`. This plan starts only after the feature lists and part requirement documents of that plan exist.
- **Source design:** ha-energy-mpc's done plan `add-user-and-developer-documentation.md`, revision 3. Layout, checks, screenshot rules and phases follow ha-energy-mpc wherever this project allows, and "Differences From ha-energy-mpc" names each departure.
- **Code style:** `../code-style.md`
- **Approval record:** On 2026-10-23 the user asked for the simulator page screenshots of Revision 2 to be added to the plan and implemented.

## Outcome And Acceptance

SAJ Local gets user documentation and developer documentation as Markdown in this repository, read on GitHub, with screenshots taken from a real Home Assistant by Playwright, and a short overview page on `counterphase.dev` that links to the user documentation. The user documentation describes SAJ Local for every supported model and marks where the HS3 and the H2 differ.

The work is accepted when:

1. `docs/en-gb/user/` and `docs/en-gb/developer/` exist, each with a `README.md` index, and every page covers one topic.
2. No written page is longer than 300 lines. `docs-check` fails a written page over the limit. The generated entity pages are exempt, see "Generated entity reference".
3. Every fact has one owner, listed in the Single Source Table below. Every other place links to the owner instead of restating the fact.
4. The entity reference is generated from the SAJ library catalogue and `custom_components/saj_local/translations/en.json`, and `make ci` fails when the committed reference is stale or when an entity in `en.json` is missing from the reference.
5. Every screenshot in `docs/images/en-gb/` is produced by `make docs-images` from a real Home Assistant in Docker with the Home Assistant user language set to English (GB), or from the simulator page of a simulator in the same run. No screenshot is edited or captured by hand.
6. The developer documentation shows every view of the simulator page and the page's key elements in screenshots, and the developer index puts the simulator first, as the way to develop and test SAJ Local without an inverter.
7. `make ci` fails when a doc links to a missing file, image or heading anchor, or when an image in `docs/images/` is referenced by no doc.
8. `README.md` is a short sales pitch for SAJ Local with links to the user index, the developer index, the supported equipment page and the licence. The Disclaimer and the Acknowledgements move to the user index. `CONTRIBUTING.md` keeps the short setup and send-a-change steps and links to the developer pages instead of `documentation/development.md`.
9. `documentation/development.md` is gone. Every fact in the guide is in a developer page or in an `AGENTS.md`, and nothing links to `documentation/`.
10. The `documentation` link in `custom_components/saj_local/manifest.json` points at `docs/en-gb/user/README.md` on GitHub.
11. The SAJ Local overview page for `counterphase.dev` builds in `website` and links to the user documentation on GitHub. The overview page goes live when the repository `Counterphase-Labs/ha-saj-local` is public.
12. Every `##` section of the three feature lists is covered by the page or pages named for the section in the Feature Coverage Table, and each of those pages links to the feature list section by the section's heading anchor. `docs-check` reads the Feature Coverage Table and fails when a named page does not link to the page's feature list section, or when a feature list section has no row.
13. `make ci` passes, including `docs-check`.

## Existing Baseline

- `README.md` (372 lines) mixes the pitch, the supported equipment table, installation, behaviour detail (polling, entity IDs, changing settings, power control, protecting the inverter, faults, diagnostics), the cards, the disclaimer, the acknowledgements and the licence.
- `documentation/development.md` (449 lines) is the only developer guide. The guide covers where the truth lives, the project division, the stack, commands and CI, testing, the frontend and the showcase dashboards, Docker, and about 230 lines on the Modbus simulator and the simulator page.
- The root `AGENTS.md` carries the make-target options, the coverage of a subset run and the Home Assistant version-bump steps that developers also need. `AGENTS.md` line 122 describes `documentation/` as "the development guide and user documentation".
- The plan `add-feature-lists-and-part-requirements.md` gives each part a feature list with a `Files:` line per section and a `Requirements:` line where a requirement section of the same name exists.
- SAJ Local registers no Home Assistant actions and has no `services.yaml`. The cards call Home Assistant's own actions.
- The entities a device gets depend on the model (HS3 or H2), the fitted equipment, the phase, string and pack counts, and the shape of the device type. The SAJ library catalogue (`catalogue_of` in `custom_components/saj_local/saj/catalogue.py`) holds, per row, the key, the entity type, the unit, the equipment, whether the row is enabled by default (`core`), and the phase, string and pack counts. `en.json` holds about 860 entity names across seven platforms. Entities outside the catalogue, such as `control_allowed` in `binary_sensor.py` and the power control entities from `saj/power_control.py`, are defined by the integration or by other library modules.
- `make test-browser-home-assistant` runs Playwright against a throwaway Home Assistant from `compose.playwright.yaml`. The Home Assistant image is built from `Dockerfile.playwright-home-assistant`, which builds the card bundle and copies the integration into the image, with an HS3 simulator (`mock/scenarios/hs3-battery.yaml`) and an H2 simulator (`mock/scenarios/h2-battery.yaml`). Both Playwright configurations take screenshots only on failure.
- `mock/scenarios/` also ships `hs3-full-house.yaml`, `hs3-ev.yaml`, `hs3-no-battery.yaml`, `hs3-off-grid.yaml` and `h2-no-battery.yaml`.
- The development environment has two hand-written showcase dashboards, `config/dashboards/saj-hs3.yaml` and `config/dashboards/saj-h2.yaml`, with every card in every option. The dashboards hold device IDs of one developer's instance.
- The site is the Hugo project `website` (repository `website`). The content lives in `content/en/`. `content/en/blog/saj-local.md` is a SAJ Local blog post. `content/en/energy-mpc/_index.md` is the Energy MPC product page, linked from `config/_default/menus.en.toml`. No SAJ Local product page exists.
- The repository `Counterphase-Labs/ha-saj-local` is private. GitHub links from the site and from the manifest only work for the public once the repository is public.

## Boundaries And Decisions

- Documentation only. No integration behaviour changes. The only production file touched is `manifest.json` (the documentation link).
- Markdown rendered by GitHub. No site generator, no docs hosting in this repository.
- Locale folders use lowercase BCP 47 tags: `docs/en-gb/` and `docs/images/en-gb/`. A second language adds sibling folders with the same file names; nothing moves.
- The feature lists are the basis for investigating and writing every page. A feature list section says what is built and names the files to read; the writer confirms each statement against those files before documenting the statement. The requirement documents say what is intended and are read only for intent. A behaviour that appears in a requirement document but in no feature list is not built, and the user documentation does not describe the behaviour as available.
- Where a feature list and the code disagree, the code is what users get. The writer corrects the feature list in the same change, under the root `AGENTS.md` rule for feature lists, and reports each correction.
- The feature lists stay the owner of the capability list of each part. User pages explain how to install, set up, read and operate SAJ Local, and link to the matching feature list section for the full list of what the feature does, instead of copying the list. A user page links to a requirement section only where the requirement explains a behaviour the reader sees, for example the rule that commissioning settings are read-only.
- The user documentation is written for SAJ in general. Where the HS3 and the H2 differ, the page says so in a marked note at the point of difference, for example "HS3 only: the EV charger controls." A page never splits into one page per model.
- `.github/work/requirements.md` and the three part requirement documents stay the internal source of truth for intended behaviour and are not restated in the user documentation.
- Writing follows the project's tone-of-voice guide, British spelling, and the terms the integration's translations show to users.
- Screenshots are not compared pixel for pixel in CI. Home Assistant renders live values and fonts differently between runs, so a pixel gate would fail without a real change.

## Differences From ha-energy-mpc

| ha-energy-mpc | This plan | Reason |
| --- | --- | --- |
| Generated `actions.md` from `services.yaml` | No actions page | SAJ Local registers no actions |
| Generated `entities.md` from `translations/en.json`, with a hand-kept `ENTITY_CONDITIONS` list | Generated entity pages from the SAJ library catalogue and `en.json`, one page per area | Which entities exist depends on model, equipment and counts, and the catalogue already holds those conditions for about 860 entities |
| A test sets up Energy MPC in four setups and compares the sensors created with `ENTITY_CONDITIONS` | `docs-check` fails when an entity key in `en.json` is missing from the generated pages; unit tests use fake catalogue rows and fake translations | The requirements forbid unit tests that assemble real modules or read project files, and the catalogue is the source, so no condition list exists to drift |
| Generated pages fall under the 300-line limit | Generated entity pages are exempt from the limit | An area such as the battery has more entities than fit in 300 lines, and readers search the page instead of reading the page |
| A `homeassistant-docs` service on the stock image with read-only mounts, plus stub Nord Pool and solar forecast integrations | A docs run on the existing image from `Dockerfile.playwright-home-assistant` with an HS3 simulator on `hs3-full-house.yaml` and an H2 simulator on `h2-battery.yaml`, no stubs | The existing image already builds the current card bundle and copies the integration; SAJ Local needs no outside service |
| `docs-images` runs `frontend-build` first | `docs-images` needs no build step | The image build compiles the card bundle, and the requirements allow only one `make build` |
| The spec waits for a current MPC plan | The spec waits until both systems are loaded and report solar power | SAJ Local has no MPC plan; a reading shows the system is polled |
| `README.md` an overview of at most 40 lines | `README.md` a short sales pitch with links, and the Disclaimer and Acknowledgements on the user index | The user decided the README is a sales pitch that links to everything else |
| The developer guide was spread over `README.md` and `AGENTS.md` | `documentation/development.md` is split into the developer pages and deleted | This project already has a developer guide, longer than the page limit |
| `releasing.md` covers release-please, the HACS archive and the Home Assistant version bump | `releasing.md` covers the Home Assistant version bump, `make docs-images` before a release and the website screenshot copy | This project has no release workflow yet; the roadmap item "Release workflow and versioning" adds the release steps to `releasing.md` |
| Site page linked from the navigation and the homepage call-to-action | Site page linked from the footer Product menu and from the SAJ Local blog post | The main navigation has no space, and the homepage call-to-action already points at Energy MPC |

## Page Layout

```
README.md                         short sales pitch, links to the indexes, supported equipment and licence
CONTRIBUTING.md                   setup and send-a-change steps, links to the developer pages
docs/
  en-gb/
    user/
      README.md                   what SAJ Local does, what it needs, page index, disclaimer, acknowledgements
      installation.md             HACS install, supported Home Assistant version
      supported-equipment.md      the supported equipment table, limitations
      getting-started.md          adding a system, automatic and manual model, first readings
      optional-equipment.md       detection, Equipment in Configure, missing equipment, H2 packs
      entities-and-prefix.md      entity types, enabled by default, sign of power, entity IDs, prefix
      polling.md                  update interval, polling groups, request load
      protecting-the-inverter.md  request ceiling, waits, refused registers
      changing-settings.md        Allow control, the control set, read-back, failures, EMS heartbeat
      power-control.md            power control and schedules
      replacing-the-inverter.md   moving a system between an H2 and an HS3
      faults-and-repairs.md       fault entities, repair issues
      troubleshooting.md          diagnostics download, debug dump, debug logging, common log messages
      cards/
        README.md                 adding an element, choosing a system, theme and language
        power-flow-card.md
        status-card.md
        faults-card.md
        battery-card.md
        controls-card.md
        schedule-card.md
        weekdays-feature.md
        status-badge.md
      entities/                   generated, see "Generated entity reference"
    developer/
      README.md                   page index, project boundary, where the truth lives
      environment.md              make setup/up/down, compose override, ports
      checks.md                   make targets, coverage gate, ARGS/ONLY/V, subset coverage
      architecture.md             the SAJ library and the integration, profiles, catalogue, polling, stable names
      frontend.md                 card source, build, Vitest, Playwright, showcase dashboards
      simulator.md                what the simulator is for, scenarios, running another system
      simulator-page.md           the simulator page, register inspector, traffic log, link faults
      documentation.md            how these docs and screenshots are made
      releasing.md                Home Assistant version bump, docs-images, site screenshot copy
  images/
    en-gb/                        generated by make docs-images only
```

The card pages may merge or split where a feature list section covers more or less than one element. A page added, merged or split updates the Feature Coverage Table in the same change.

## Generated Entity Reference

- `docs/en-gb/user/entities/` holds one generated page per area, plus a `README.md` index that links each area page and the integration feature list section Devices and entities, which owns the entity types, the enabled-by-default rules and the sign conventions. The generated pages give each entity's name from `en.json` and no per-entity description. The starting areas are inverter and PV, grid and Meter A, Meter B, battery, battery packs, EV charger, parallel system, settings, faults and the entities the integration adds outside the catalogue. The Developer confirms the areas against the catalogue families and equipment, and the generator names each area in one table in `.github/scripts/docs_check.py`.
- Each area page has one table row per entity key with: the name from `en.json`, the entity ID without a prefix (`<domain>.saj_<key>`), the entity type, the unit, the models that have the entity (HS3, H2), the equipment that must be fitted, and whether the entity is enabled by default. A row for an entity that exists only with a phase, string or pack count above one states the count, for example "PV string 3 and above".
- Each area page opens with one line linking the feature list section that covers the area and one line on adding the prefix to the entity ID when a prefix is set. The prefix example is built from the first row of the page, so a page of switches shows a switch, for example `switch.saj_house_charge_slot_1_enabled` with the prefix `house`. An area page with no rows has no prefix line.
- The rows come from the catalogue of every shipped profile. The entities outside the catalogue come from the integration and library code that defines the entities. The Developer finds every such source in the code and lists the sources in `docs/en-gb/developer/documentation.md`.
- `docs-check` fails when an entity key in the `entity` block of `en.json` appears on no area page, so a new entity cannot ship without a row.
- The generator imports only the SAJ library and reads `en.json`, so the generator needs no Home Assistant.

## Feature Coverage Table

Each feature list section is investigated from the section's `Files:` line and covered by the pages named here. Every named page links to the section. A page name is relative to `docs/en-gb/`. Phase 1 copies the table into `docs/en-gb/developer/documentation.md`, which owns the table from then on and is the copy `docs-check` reads. The section names are those of the plan `add-feature-lists-and-part-requirements.md`; a section renamed or split there is renamed or split here in the same change.

| Feature list | Section | Pages |
| --- | --- | --- |
| Integration | Setup and detection | `user/installation.md`, `user/supported-equipment.md`, `user/getting-started.md` |
| Integration | Devices and entities | `user/entities-and-prefix.md`, `user/entities/README.md`, `developer/architecture.md` |
| Integration | Optional equipment | `user/optional-equipment.md` |
| Integration | Entity IDs and prefix | `user/entities-and-prefix.md` |
| Integration | Polling | `user/polling.md`, `developer/architecture.md` |
| Integration | Protecting the inverter | `user/protecting-the-inverter.md`, `developer/architecture.md` |
| Integration | Changing settings | `user/changing-settings.md` |
| Integration | EMS | `user/changing-settings.md` |
| Integration | Power control | `user/power-control.md` |
| Integration | Model replacement | `user/replacing-the-inverter.md` |
| Integration | Device faults and repairs | `user/faults-and-repairs.md` |
| Integration | Diagnostics and debug logging | `user/troubleshooting.md` |
| Integration | Cards | `user/cards/README.md`, `developer/frontend.md` |
| Cards | Elements and setup | `user/cards/README.md` |
| Cards | Power flow card, Status card, Faults card, Battery card, Controls card, Schedule card, Weekdays tile card feature, Status badge | the card page of the same name under `user/cards/` |
| Cards | Theme and language | `user/cards/README.md`, `developer/frontend.md` |
| Simulator | Simulated models, Scenarios, Variation | `developer/simulator.md` |
| Simulator | Control page, State and presets, Register inspector and traffic log, Link faults | `developer/simulator-page.md` |

## Single Source Table

| Fact | Owner | Places that link instead of restating |
| --- | --- | --- |
| What SAJ Local does, in one short summary | `docs/en-gb/user/README.md` | `README.md` |
| What each part can do, section by section | the three feature lists | user and developer pages through the Feature Coverage Table |
| Supported models and equipment | `docs/en-gb/user/supported-equipment.md` | `README.md`, `user/README.md` |
| Entity names, entity IDs, models, equipment and defaults | the catalogue and `translations/en.json` → generated `user/entities/` | user pages that mention an entity |
| Entity types, enabled-by-default rules and sign conventions | integration feature list section Devices and entities | generated `user/entities/README.md` (one link), user pages |
| Development setup | `docs/en-gb/developer/environment.md` | `README.md`, `CONTRIBUTING.md` |
| Make targets and check rules | `docs/en-gb/developer/checks.md` | `README.md`, `AGENTS.md` |
| Home Assistant version bump | `docs/en-gb/developer/releasing.md` | `AGENTS.md` |
| Licence terms | `LICENSE` | `README.md` (one line), `CONTRIBUTING.md` |
| Site overview screenshot | `docs/images/en-gb/cards-power-flow-card.png` | `assets/images/saj-local-power-flow.png`, a copy refreshed at each release, because the private repository and the Hugo `image` partial rule out a link |
| Intended product behaviour | `.github/work/requirements.md` and the three part requirement documents | `docs/en-gb/developer/README.md`, user pages where a requirement explains what the reader sees |

The root `AGENTS.md` and the part `AGENTS.md` files keep the agent-only rules (agent use of the make targets, the forbidden verbose options, reporting format, the feature list rules). The sections Options and Coverage of a subset run and the version-bump steps move from the root `AGENTS.md` to the developer pages, and the root `AGENTS.md` links to `checks.md` and `releasing.md` in their place. The rest of `documentation/development.md` moves into the developer pages, apart from any rule only agents need, which moves to the matching `AGENTS.md`.

## Phases

### Phase 1 — Skeleton and README

- Create the folders and every page in the Page Layout with the page's heading, a one-line purpose and the links to the page's feature list sections from the Feature Coverage Table.
- Rewrite `README.md` as a short sales pitch: what SAJ Local does for the reader, the supported models in one line, and links to the user index, the developer index, the supported equipment page and the licence. Move the Disclaimer and the Acknowledgements to `docs/en-gb/user/README.md`.
- Move the supported equipment table, installation and the behaviour sections of `README.md` into the user pages, and the development content of `documentation/development.md` into the developer pages, then delete `documentation/development.md` and the `documentation/` folder.
- Replace the four links in `CONTRIBUTING.md` to `documentation/development.md` (lines 11, 36, 44 and 52) with links to the developer index, `simulator.md` and `checks.md`.
- In `CONTRIBUTING.md`, replace the list of test folders and the `V=1` explanation in the section Check your change with a link to `checks.md`, which owns both.
- In the root `AGENTS.md`, replace the sections Options, Coverage of a subset run and Bumping the Home Assistant version with links to `checks.md` and `releasing.md`, keeping the agent-only rules.
- In the root `AGENTS.md`, replace `documentation/` with `docs/en-gb/` and `docs/images/` in the sections Repository Layout and Project Documentation, and add to the section Feature Lists the rule that a capability change also updates every user page that links to the changed feature list section, in the same change.
- Change the `documentation` link in `manifest.json`.

### Phase 2 — Generated reference and `docs-check`

- Add `.github/scripts/docs_check.py`:
  - `--write` regenerates `docs/en-gb/user/entities/` from the catalogue of every shipped profile, the other entity sources and `en.json`.
  - Without `--write`, the script compares the generated text with the committed files and reports each stale file.
  - The script reports each entity key in `en.json` that appears on no area page.
  - The script reports each relative link, image or `#anchor` that does not resolve, in the pages, `README.md`, `CONTRIBUTING.md` and every `AGENTS.md`, including links into the feature lists and requirement documents, each image in `docs/images/` that no doc references, and each written page over 300 lines.
  - The script reads the `##` headings of the three feature lists and the Feature Coverage Table in `docs/en-gb/developer/documentation.md`, and reports each feature list section with no row and each named page that does not link to the page's feature list section.
- Add the `docs-check` step to `.github/scripts/check_steps.py` with a parser in `check_parsers.py` and the help text `make help` prints, the `docs-check` and `docs` (runs `--write`) make targets, and add `docs-check` to `make ci`. GitHub runs `make ci`, so the CI workflow needs no change.
- Add `tests/scripts/test_docs_check.py` covering stale reference, missing entity key, broken link, broken anchor, orphan image, oversized page, the exempt generated pages and uncovered feature list section, with fake catalogue rows and fake translations, and a parser test in `tests/scripts/test_check_parsers.py`. The tests keep `.github/scripts` at 100 % line and branch coverage and pass `test-modules`.

### Phase 3 — Screenshots

- Add `frontend/playwright.docs.config.ts` and `frontend/tests/browser/docs/screenshots.spec.ts`:
  - The spec runs against a throwaway Home Assistant built from `Dockerfile.playwright-home-assistant`.
  - The spec sets the Home Assistant user language to English (GB). The locale is a parameter only for the image folder and the language picked on the profile page. The spec finds Home Assistant controls by their English labels, so screenshots in a second language also need spec selectors for that language.
  - Fixed viewport (1280 × 800), light theme, real time.
  - Each screenshot is written to `docs/images/en-gb/<page>-<subject>.png`, where `<page>` is the page path with `/` replaced by `-`, for example `cards-battery-card-pack-detail.png`.
- Add to `compose.playwright.yaml` a `mock-docs` simulator service on `mock/scenarios/hs3-full-house.yaml` and a `playwright-docs` service that depends on `homeassistant`, `mock-docs` and `mock-h2`, mounts `./docs/images` into the runner, and runs the docs spec. Add `tests/playwright/run-docs-images.sh`, modelled on `tests/playwright/run-home-assistant.sh`, which starts only those services and removes the services afterwards.
- The spec adds the HS3 system through the add-system dialog of the Home Assistant frontend, which the add-system screenshots need, and adds the H2 system through the config flow API. The spec creates a dashboard with the SAJ Local elements for each system through the Home Assistant WebSocket API, because driving the dashboard editor adds run time and nothing a screenshot shows. The spec takes every screenshot that needs Allow control off first, the add-system dialog and the locked controls card, then switches Allow control on for both systems. Before the first dashboard screenshot the spec waits until both systems report solar power. A run with no reading from both systems within two minutes fails, and no screenshots are written.
- Small changes to a shipped scenario or a new docs scenario are allowed where screenshots need them, for example a fixed start state. A simulator change keeps the simulator's own tests passing and does not alter how the simulator models devices.
- Add the `docs-images` step and make target. The target is not part of `make ci` and has the same timeout as `test-browser-home-assistant`. `releasing.md` makes copying the site screenshot to the website part of the same release step, after `make docs-images`.
- Screenshots planned, one per subject, on the HS3 unless named:
  - config flow: add a system, the manual model choice, the Allow control warning, the prefix change warning, the Equipment section and a polling group in Configure
  - each card, the weekdays tile card feature and the status badge, on the HS3; the power flow card and the battery card also on the H2, and any other element whose H2 screen differs in a way a user would notice
  - the controls card locked with Allow control off
  - a power control entity with a schedule helper
  - the repair issue for readings the inverter refuses, the diagnostics download
- Simulator page screenshots, taken last so that nothing done on the simulator page changes a Home Assistant screenshot. The spec opens the page of the HS3 simulator at `http://mock-docs:8080/`, with the refused register of the repair screenshot still in force, sets the fault "Fan 1 fault" through the Faults view, a fault that only sets its bit and stops nothing, and takes, at 1280 × 800 unless named:
  - the Overview view of the HS3 at 1280 × 1600: the status bar, the view tabs, the power-flow diagram and the equipment cards
  - the Overview view of the H2 simulator at `http://mock-h2:8080/`, at 1280 × 1600
  - the status bar, with the chips for the changes from the scenario that are in force
  - the equipment card that shows the active fault, with the card's readings, controls and fault list
  - the Faults, Settings, Registers, Traffic, Link and Scenario views, each as the page shows the view
  - the traffic log with one refused request opened to show the request's detail
- Each simulator page screenshot is named `developer-simulator-page-<subject>.png`, because the screenshot belongs to the developer page `developer/simulator-page.md` and the `developer-` prefix keeps the name apart from the user page names.
- The spec waits for a screen by checking for the state the screen shows, never by a fixed sleep. SAJ Local raises no repair issue for a device fault, so the repair screenshot shows the issue for readings the inverter refuses. For the repair issue, the spec makes the simulator refuse one register through the simulator's HTTP interface, reads the register in its own short polling group, and checks the open repair issues until the SAJ Local `registers_refused` issue is present, and fails at a two-minute limit with a message naming the missing issue.

### Phase 4 — Write the pages

- Investigate each page from the page's feature list sections in the Feature Coverage Table: read the section, then the files on the section's `Files:` line, and confirm every statement against the code before writing the statement. Read the linked requirement section only for intent.
- Correct any feature list statement the code contradicts, in the same change, and list each correction in the report.
- Write every user page and developer page in the tone of the project's tone-of-voice guide.
- Each user page states what the reader can do, the steps, the screenshot, a marked note wherever the HS3 and the H2 differ, a link to the feature list section for the full list of what the feature does, and a link to the generated entity reference for names.
- Each developer page that describes code links to the feature list section whose `Files:` line names the code, instead of repeating the file list.
- `developer/simulator-page.md` shows the screenshot of each view beside the view's description, and the status bar, equipment card and traffic log detail screenshots beside the text that describes each element. `developer/simulator.md` opens with the HS3 Overview screenshot. `developer/README.md` opens with a section on developing without an inverter, which shows the HS3 Overview screenshot and links to `simulator.md` and `simulator-page.md`, and lists the two simulator pages first in the page index.
- Each user page states plainly what is not supported yet, without roadmap claims. A requirement with no feature list bullet is not described as available.
- `user/changing-settings.md` ends with a section Tested on hardware, which states only what hardware tests and field reports established and cites no test record. The section holds exactly these items:
  - HS3, written one register at a time on a real HS3 and read back: the Application mode, the Backup reserve state of charge, the Passive battery charge power, the EMS timeout, the four EMS enable bits that power control writes, and the three EMS targets and five EMS limits.
  - HS3: the Passive battery charge power sets the power of Backup mode.
  - HS3: application mode EMS on its own leaves the inverter idle, with the house running from the grid, and the inverter does not leave EMS by itself.
  - HS3: the EMS timeout ended EMS after 5 seconds, but did not end EMS at 20 or 60 seconds while another client polled the inverter; SAJ Local does not rely on the timeout.
  - HS3: the solar power limit has an effect only while an EMS function is on.
  - HS3: when an EMS function stops, the inverter goes back to the application mode it ran before.
  - HS3: Time-of-use (BMS) is the mode the HS3 reports when the SAJ app selects the app's TOU (BMS) mode, which is not the app's time-of-use mode; SAJ Local has never written Time-of-use (BMS).
  - H2, built from field reports and the H2 protocol document and not tried by this project: power control through passive mode, the schedule slots, the application mode, the passive mode powers, the battery limits, the grid power limits and the export limit.
  - H2: field reports show Peak shaving selected in the SAJ app, read back and written over Modbus; the H2 protocol document does not list Peak shaving.
  - H2: AI saving is the mode the H2 reports when the SAJ app selects AI saving; SAJ Local has never written AI saving.
  - Never tried on a real inverter: the LED mode, the H2 buzzer, the H2 battery forced charge power limit, every other setting not named in the section, every change that writes more than one register, and every command.
- The integration feature list section Device faults and repairs gets a bullet saying a device fault raises no repair issue and naming each repair issue with a link to the section that owns the issue: Model replacement, Protecting the inverter and Optional equipment.

### Phase 5 — Site overview page

- In `website`, add `content/en/saj-local/_index.md`: what SAJ Local does in three short paragraphs, the supported models, what SAJ Local needs, the site screenshot copied to `assets/images/saj-local-power-flow.png`, and a link to the user documentation on GitHub. Content and front matter follow `content/en/energy-mpc/_index.md`.
- Rename the layout `layouts/energy-mpc/` to `layouts/product-info/`, a shared product page layout, and set `type: product-info` in the front matter of both `content/en/energy-mpc/_index.md` and `content/en/saj-local/_index.md`. No new layout is added.
- Link the page from the footer `[[product]]` menu in `config/_default/menus.en.toml`, after Energy MPC, and from `content/en/blog/saj-local.md`. The `[[main]]` navigation does not change.
- Follow the website's agent rules and run the site's checks there.

## Verification Strategy

- `make ci` passes, including `docs-check`.
- `make docs-images` produces every image referenced by the docs, and `docs-check` reports no orphan image.
- Read every page on GitHub (a pushed branch or preview) to confirm images, relative links and anchors render.
- The site builds with the new page, and the page's GitHub link opens the user index.

## Risks And Guardrails

- **Screenshots drift from the UI.** `documentation.md` and `releasing.md` make `make docs-images` a release step. A UI change that adds or removes a screenshot fails `docs-check` through the orphan or missing image rule. No check can catch a stale website copy, because the CI of this repository cannot see the website repository.
- **Prose drifts from behaviour.** Prose names no entity by hand; prose links to the generated reference. Pages link to the feature list section instead of copying the list, and the feature list is updated with every capability change under the root `AGENTS.md` rule.
- **New features go undocumented.** A capability change that adds a feature list section fails `docs-check` until a page links to the new section. A new entity fails `docs-check` until the entity has a row.
- **Entities outside the catalogue are missed.** The missing-key rule catches an entity source the generator does not read, because every entity has a name in `en.json`.
- **H2 statements rest on documents.** The H2 behaviour comes from SAJ protocol documentation and field reports and has not been verified by hand on an H2. The user pages say so where the feature list says so, and screenshots of the H2 show the simulator.
- **Simulator values.** Screenshots show simulated readings. `documentation.md` states that the screenshots come from the simulator.
- **Private repository.** The site and manifest links fail for the public until the repository is public. The site page is built and checked in `website` now, and goes live only when the repository is public.
- **Repository size.** PNG screenshots are committed. Keep the set to the subjects listed in Phase 3 and compress with Playwright's default PNG output.

## Settled Decisions

- **Feature lists first (2026-10-22):** The documentation is built on the feature lists of `add-feature-lists-and-part-requirements.md`, which is done first.
- **Entity reference (2026-10-22):** The entity reference is generated from the SAJ library catalogue and links to the feature lists for what entities mean.
- **Models (2026-10-22):** The documentation is written for SAJ in general and marks where the HS3 and the H2 differ.
- **Site overview (2026-10-22):** A new page at `/saj-local/` on `counterphase.dev`, linked from the footer Product menu and the SAJ Local blog post.
- **README (2026-10-22):** `README.md` is a short sales pitch with links.
- **Entity pages (2026-10-22):** The generated entity pages are exempt from the 300-line page limit, which applies to written pages only.
- **Same approach as ha-energy-mpc (2026-10-22):** The plan follows the ha-energy-mpc documentation plan, with only the differences listed.
- **Repair screenshot (2026-10-23):** The repair screenshot shows the issue for readings the inverter refuses, because SAJ Local raises no repair issue for a device fault.
- **Screenshot order and set-up (2026-10-23):** Screenshots that need Allow control off come first. The H2 system is added through the config flow API and the dashboards through the WebSocket API.
- **Hardware notes (2026-10-23):** `user/changing-settings.md` carries the hardware-tested notes, corrected against the HS3 hardware tests, with no reference to the test record.
- **Prefix examples (2026-10-23):** Each generated area page builds its prefix example from the page's first row.
- **Product page layout (2026-10-23):** The Energy MPC layout of the website is renamed `product-info` and shared by both product pages; no new layout.
- **Repairs in the feature list (2026-10-23):** The section Device faults and repairs names the repair issues and links to the owning sections.
- **Simulator page screenshots (2026-10-23):** The developer documentation shows every view and the key elements of the simulator page, and the developer index puts the simulator first, because the simulator is critical to developing SAJ Local.

## Developer Task After User Approval

After the user approves this exact revision, and after `add-feature-lists-and-part-requirements.md` is implemented, implement the phases in order. Before coding, read the root `AGENTS.md`, `.github/work/code-style.md`, the part `AGENTS.md` files, this feature plan, the three feature lists and the project's tone-of-voice guide. Report the page list with line counts, the generated area pages with row counts, the screenshot list, each feature list correction, the `make ci` result and the site build result.

## Revision History

- **Revision 1 — 2026-10-22:** Initial draft. Splits user and developer documentation under `docs/en-gb/`, moves `documentation/development.md` into developer pages, generates the entity reference from the catalogue, adds Playwright screenshots of the HS3 and the H2, a `docs-check` gate and a site overview page.
- **Revision 2 — 2026-10-23:** Adds screenshots of every view and the key elements of the simulator page to the developer documentation, and makes the developer index put the simulator first.
