en | [de](../../de/developer/documentation.md) | [nl](../../nl/developer/documentation.md) | [fr](../../fr/developer/documentation.md) | [zh](../../zh-hans/developer/documentation.md) | [es](../../es/developer/documentation.md) | [it](../../it/developer/documentation.md) | [pl](../../pl/developer/documentation.md) | [sv](../../sv/developer/documentation.md)

# Documentation

How the documentation pages are organised, how the entity reference and the screenshots are made, and what `make docs-check` fails on.

## Layout

User pages live in `docs/en-gb/user/` and developer pages in `docs/en-gb/developer/`. Each folder has a `README.md` index, and every page covers one topic. No written page is longer than 300 lines. Each fact has one owner, listed under [Sources](#sources), and every other page links to the owner instead of restating the fact.

Screenshots live in `docs/images/en-gb/`. Every image must be referenced by a page.

Write pages in British English, in the tone of voice of Counterphase, and use the terms the integration's translations show to users. The user pages describe SAJ in general and mark, at the point of difference, where the HS3 and the H2 differ. A page never splits into one page per model.

## Feature lists first

The three feature lists are the basis for every page: [integration](../../../custom_components/saj_local/docs/features.md), [cards](../../../frontend/docs/features.md) and [simulator](../../../mock/docs/features.md). A feature list section says what is built and names the files to read on the `Files:` line of the section. Confirm each statement against those files before documenting the statement. The requirement documents say what is intended and are read only for intent. A behaviour that appears in a requirement document but in no feature list is not built, and a user page does not describe the behaviour as available. Where a feature list and the code disagree, the code is what users get, so correct the feature list in the same change.

A page that describes code links to the feature list section whose `Files:` line names the code, and does not repeat the file list.

A capability change updates the feature list of the part and every user page that links to the changed section, in the same change. The root `AGENTS.md` holds the rule.

## Generated entity reference

`docs/en-gb/user/entities/` holds one generated page per area and a `README.md` index. Run `make docs` to regenerate the pages, then commit the regenerated pages. Prose pages never name an entity by hand; the prose pages link to the generated pages. Generated pages are exempt from the 300-line limit, because readers search an area such as the battery instead of reading the area.

The generator is `.github/scripts/docs_check.py`, run with `--write` by `make docs`. The generator imports only the SAJ library and reads `custom_components/saj_local/translations/en.json`, so the generator needs no Home Assistant. Each area page opens with a link to the feature list sections that cover the area and a line on the entity ID prefix, and then has one row per entity with the name from `en.json`, the entity ID without a prefix, the type, the unit, the models that have the entity, the equipment that must be fitted with any phase, string or pack count, and whether the entity is enabled by default. An entity that two models define differently, for example with another unit, gets one row for each definition.

### Entity sources

Every entity comes from one of these sources, and the generator reads all of them:

| Source | Code | Entities |
| --- | --- | --- |
| The register catalogue of every shipped model | `catalogue_of` in [catalogue.py](../../../custom_components/saj_local/saj/catalogue.py), called for each profile in `PROFILES` of [profiles.py](../../../custom_components/saj_local/saj/profiles.py), skipping rows that are not exposed | Sensors, binary sensors (the faults), numbers, selects, switches, times and buttons |
| The control allowed sensor | `CONTROL_ALLOWED_KEY` in [binary_sensor.py](../../../custom_components/saj_local/binary_sensor.py) | `binary_sensor.saj_control_allowed`, on both models |
| The power control switches and numbers | `power_control` of each profile ([hs3.py](../../../custom_components/saj_local/saj/models/hs3.py) and [h2.py](../../../custom_components/saj_local/saj/models/h2.py)), the `PowerFunction` keys in [models/\_\_init\_\_.py](../../../custom_components/saj_local/saj/models/__init__.py) and `FUNCTION_EQUIPMENT` in [power_control.py](../../../custom_components/saj_local/saj/power_control.py), created by [switch.py](../../../custom_components/saj_local/switch.py) and [number.py](../../../custom_components/saj_local/number.py) | A switch and a number for each power function of a model: battery on both models, grid and inverter on the HS3 |

`make docs-check` fails when an entity in the `entity` block of `en.json` is on no area page, so an entity source that the generator does not read is found at once. A new source needs the generator to read the source and a row in the table above.

### Areas

An entity lands on the first area that matches, in this order:

1. Entities outside the catalogue: Added by the integration.
2. Binary sensors from the catalogue, which are the faults: Faults.
3. Entities with a battery pack index: Battery packs.
4. Entities of optional equipment: Battery, Grid and Meter A, Meter B, EV charger or Parallel system.
5. Writable entities with no equipment: Settings.
6. Entities whose key starts with `grid_`: Grid and Meter A.
7. Everything else: Inverter and PV.

The `AREAS` table of `.github/scripts/docs_check.py` names the areas, their summaries and the feature list sections that each area page links.

## Checks

`make docs-check` runs `.github/scripts/docs_check.py` without `--write` and reports one line per finding:

- a generated page that differs from what `make docs` would write;
- an entity in `en.json` that is on no area page, and a generated entity with no name in `en.json`;
- a relative link, image or heading anchor that does not resolve, in the pages, `README.md`, `CONTRIBUTING.md`, `SECURITY.md` and every `AGENTS.md`, including links into the feature lists and the requirement documents;
- an image in `docs/images/` that no page references;
- a written page over 300 lines;
- a feature list section with no row in the [Feature Coverage Table](#feature-coverage-table), a section named in the table that the feature list does not have, a page named in the table that does not exist, and a page that does not link to the feature list section named in the row, by the heading anchor of the section.

`make docs-check` is a step of `make ci`, and GitHub runs `make ci`, so the check needs no workflow change. The check reads no screenshot beyond the link and orphan rules and starts no browser.

## Screenshots

Every screenshot in `docs/images/<code>/` is made by `make docs-images` from a real Home Assistant in Docker with the user language set to the language of the folder, or from the simulator pages of the same run. `make docs-images` runs every language, English first, with fresh containers for each run, and `ARGS=<code>` selects one language. No screenshot is edited or captured by hand, so the set can be rebuilt whenever the interface changes. The screenshots show the simulators, so every reading in a screenshot is a simulated value.

The target runs `tests/playwright/run-docs-images.sh`, which builds the `homeassistant` and `playwright-docs` services of [compose.playwright.yaml](../../../compose.playwright.yaml), starts the throwaway Home Assistant and two simulators, runs the spec and then removes the containers, volumes and local images. The target needs Docker, has the same time limit as `make test-browser-home-assistant` and takes options through `ARGS`, which the script receives. The Home Assistant image is built from `Dockerfile.playwright-home-assistant`, which builds the card bundle and copies the integration into the image, so no integration code is mounted. The spec is `frontend/tests/browser/docs/screenshots.spec.ts`, configured by `frontend/playwright.docs.config.ts`.

- **Systems.** The HS3 is the simulator `mock-docs` on `mock/scenarios/hs3-full-house.yaml`, which has every equipment fitted. The H2 is the simulator `mock-h2` on `mock/scenarios/h2-battery.yaml` and gets the entity prefix `h2`. Neither simulator mounts a state folder, so each run starts from the scenario.
- **Fixed conditions.** The viewport is 1280 by 800 pixels, the theme is light and the clock is real. A tall dialog or card is taken in a window 1600 pixels high, because the fixed header of Home Assistant would cover the top of the element.
- **Language.** Each run sets both the Home Assistant server language, before SAJ Local is set up so the entities are created with names in that language, and the user language, by language code and not by the label of the language picker. The run fails when a SAJ Local entity name is not in the language of the run. The images go to `docs/images/<code>/`. The spec opens screens by URL route, finds the fields of SAJ Local forms by their `name` attribute, and finds Home Assistant controls that have only text by the text read at run time from the running Home Assistant with `hass.localize`. The spec holds no table of labels, so every language runs the same steps.
- **Names.** Each file is named `<page>-<subject>.png`, where `<page>` is the page path with `/` replaced by `-`, for example `cards-battery-card.png`, and the page that shows the image links to the file.
- **Simulator pages.** The screenshots of the simulator pages come from the two simulators of the same run, `mock-docs` and `mock-h2`, and use the name prefix `developer-simulator-page-`. They are taken last, after every Home Assistant screenshot, so nothing done on a simulator page changes a Home Assistant screenshot. The spec sets the fault "Fan 1 fault" on the HS3 page, and the register that the repair screenshot makes the simulator refuse stays refused, so the Link view, the traffic log and the changes in the status bar show real changes.
- **Setup.** The spec creates a user through the onboarding API, adds the HS3 through the config flow in the browser, adds the H2 through the config flow API, switches Allow control on for both systems and adds one dashboard for each system with every SAJ Local card and the status badge, through the Home Assistant WebSocket API.
- **All or nothing.** The spec waits up to two minutes for both systems to report solar power. The spec writes the images only after every step has passed, so a failed run leaves the committed images as they were.
- **Waits.** The spec waits for a screen by checking for the state the screen shows, never by a fixed sleep.
- **Repair.** The repair screenshot shows the refused-registers repair. The spec adds a polling group for the inverter temperature with an interval of 10 seconds, makes the simulator refuse that register through `POST /api/link` of the simulator page, and waits up to two minutes until `repairs/list_issues` lists the `registers_refused` issue of SAJ Local. The run fails with a message naming the missing issue when the issue does not appear.
- **Forms.** The prefix change warning is captured and then the form is closed, which aborts the flow, so no prefix is saved. The Allow control warning is captured and then confirmed, because the cards need control allowed.
- **Failures.** The HTML report is in `frontend/playwright-report/docs/`, and a failed run saves the Home Assistant log as `frontend/test-results/docs/home-assistant.log`.

Screenshots are not compared pixel for pixel, in CI or anywhere else. Home Assistant renders live values and fonts differently between runs, so a pixel comparison would fail without a real change. Review a changed image by looking at the image.

### Adding or changing a screenshot

1. Add or change the capture in the spec, with the file name in the `<page>-<subject>.png` form.
2. Reference the image from the page that explains the subject.
3. Run `make docs-images`, look at the changed images and commit the changed images.
4. Run `make docs-check`. An image that no page references, and a link to an image that does not exist, are both reported.

`make docs-images` is not a step of `make ci`, and CI does not regenerate images. Run the target before each release, see the [releasing page](releasing.md).

## Adding a page

1. Create the page under `docs/en-gb/user/` or `docs/en-gb/developer/` and link the page from the index of the folder.
2. Link the page to the feature list section whose `Files:` line names the code the page describes.
3. Add the page to the row of that section in the Feature Coverage Table, or add a row. A new feature list section needs a row before `make docs-check` passes.
4. Run `make docs-check`.

Keep the pages useful: link to the file that holds a fact instead of copying the fact, record the reason for a decision because reasons change rarely and details constantly, and keep examples few and run each example again when the example changes.

## Languages

The documentation exists in English and in every target language of the [global requirements](../../../.github/work/requirements.md#language). The feature lists and the requirement documents stay English only.

- **Layout.** Each language has the sibling folders `docs/<code>/user/`, `docs/<code>/developer/` and `docs/images/<code>/`, with the same file names in every language. The codes are `en-gb`, `de`, `nl`, `fr`, `zh-hans`, `es`, `it`, `pl` and `sv`. A code block that is the same in several languages stays inline on every page and is wrapped in a `jscpd:ignore-start` and `jscpd:ignore-end` marker pair, only under an exception the user approved in a plan, as `AGENTS.md` says. A marker pair wraps one code block and nothing else.
- **Generator.** `make docs` writes `docs/<code>/user/entities/` for each language from the matching file in `custom_components/saj_local/translations/`. The equipment names come from the same translation file, and the other texts of the generator come from `.github/scripts/docs_text/<code>.json`.
- **Docs check.** `make docs-check` runs every rule on every language folder. The [Feature Coverage Table](#feature-coverage-table) on this page applies to every language under the same page names, and the orphan image rule checks `docs/images/<code>/` against the pages of the same language.
- **Language bar.** The first line of every page under `docs/<code>/user/` and `docs/<code>/developer/`, the generated entity pages included, is the language bar `en | de | nl | fr | zh | es | it | pl | sv`, always in that order. Each label except the current language links to the same page in that language's folder, and the current language is plain text. `make docs` writes the bar, and `make docs-check` reports a page whose first line is not the expected bar and a bar link to a page that does not exist.
- **Translated README.** The root `README.md` stays English in the repository root and is translated at `docs/<code>/README.md`, whose links point to the pages of that language. The root `README.md` and every `docs/<code>/README.md` carry the same bar as their first line, and `make docs-check` reports a missing `docs/<code>/README.md`.
- **Screenshots.** `make docs-images` runs the spec once for each language, English first, with fresh containers for each run. `ARGS=<code>` selects one language, see [Screenshots](#screenshots).
- **Nomenclature.** The `user/nomenclature.md` page of each language is the list of terms that every translation of the integration, the cards and the pages of the language follows. The English [nomenclature](../user/nomenclature.md) is the source.
- **Changing English.** A change to an English text, page or screenshot updates every language in the same change. No check keeps the languages in step.

## Feature Coverage Table

Each feature list section is investigated from the `Files:` line of the section and covered by the pages named here. Every named page links to the section by the heading anchor of the section. A page name is relative to `docs/en-gb/` and links to the page. This page owns the table, and `docs-check` reads the table from this page. A page added, merged or split updates the table in the same change.

| Feature list | Section | Pages |
| --- | --- | --- |
| Integration | Setup and detection | [`user/installation.md`](../user/installation.md), [`user/supported-equipment.md`](../user/supported-equipment.md), [`user/getting-started.md`](../user/getting-started.md) |
| Integration | Devices and entities | [`user/entities-and-prefix.md`](../user/entities-and-prefix.md), [`user/entities/README.md`](../user/entities/README.md), [`developer/architecture.md`](architecture.md) |
| Integration | Optional equipment | [`user/optional-equipment.md`](../user/optional-equipment.md) |
| Integration | Entity IDs and prefix | [`user/entities-and-prefix.md`](../user/entities-and-prefix.md) |
| Integration | Polling | [`user/polling.md`](../user/polling.md), [`developer/architecture.md`](architecture.md) |
| Integration | Protecting the inverter | [`user/protecting-the-inverter.md`](../user/protecting-the-inverter.md), [`developer/architecture.md`](architecture.md) |
| Integration | Changing settings | [`user/changing-settings.md`](../user/changing-settings.md) |
| Integration | EMS | [`user/changing-settings.md`](../user/changing-settings.md) |
| Integration | Power control | [`user/power-control.md`](../user/power-control.md) |
| Integration | Model replacement | [`user/replacing-the-inverter.md`](../user/replacing-the-inverter.md) |
| Integration | Device faults and repairs | [`user/faults-and-repairs.md`](../user/faults-and-repairs.md) |
| Integration | Diagnostics and debug logging | [`user/troubleshooting.md`](../user/troubleshooting.md) |
| Integration | Languages | [`user/nomenclature.md`](../user/nomenclature.md) |
| Integration | Cards | [`user/cards/README.md`](../user/cards/README.md), [`developer/frontend.md`](frontend.md) |
| Cards | Elements and setup | [`user/cards/README.md`](../user/cards/README.md) |
| Cards | Power flow card | [`user/cards/power-flow-card.md`](../user/cards/power-flow-card.md) |
| Cards | Status card | [`user/cards/status-card.md`](../user/cards/status-card.md) |
| Cards | Faults card | [`user/cards/faults-card.md`](../user/cards/faults-card.md) |
| Cards | Battery card | [`user/cards/battery-card.md`](../user/cards/battery-card.md) |
| Cards | Controls card | [`user/cards/controls-card.md`](../user/cards/controls-card.md) |
| Cards | Schedule card | [`user/cards/schedule-card.md`](../user/cards/schedule-card.md) |
| Cards | Weekdays tile card feature | [`user/cards/weekdays-feature.md`](../user/cards/weekdays-feature.md) |
| Cards | Status badge | [`user/cards/status-badge.md`](../user/cards/status-badge.md) |
| Cards | Theme and language | [`user/cards/README.md`](../user/cards/README.md), [`developer/frontend.md`](frontend.md) |
| Simulator | Simulated models, Scenarios, Variation | [`developer/simulator.md`](simulator.md) |
| Simulator | Control page, State and presets, Register inspector and traffic log, Link faults | [`developer/simulator-page.md`](simulator-page.md) |

## Sources

| Fact | Owner |
| --- | --- |
| What SAJ Local does, in one short summary | [user index](../user/README.md) |
| What each part can do | the three feature lists |
| Supported models and equipment | [supported equipment](../user/supported-equipment.md) |
| Entity names, entity IDs, models, equipment and defaults | the catalogue and `translations/en.json`, through the [entity reference](../user/entities/README.md) |
| Entity types, enabled-by-default rules and sign conventions | the integration feature list section Devices and entities |
| Development setup | [environment](environment.md) |
| Make targets and check rules | [checks](checks.md) |
| Release process and Home Assistant version bump | [releasing](releasing.md) |
| Site overview screenshot | `docs/images/en-gb/cards-power-flow-card.png`, copied by the maintainers to the project website at each release, see the [releasing page](releasing.md) |
| How to report a security problem | `SECURITY.md` |
| Issue labels and the rules for labels | `.github/labels.yml` and `CONTRIBUTING.md` |
| Licence terms | `LICENSE` |
| Intended product behaviour | `.github/work/requirements.md` and the three part requirement documents |
