# Frontend

How the card bundle is organised and built, and how to look at every card in the development instance.

The full list of what the frontend covers is in the feature list sections [Cards](../../../custom_components/saj_local/docs/features.md#cards) of the integration and [Elements and setup](../../../frontend/docs/features.md#elements-and-setup) and [Theme and language](../../../frontend/docs/features.md#theme-and-language) of the cards.

## Build

The cards, the tile card feature and the badge are one Lit and TypeScript bundle under `frontend/`. `make build` runs Vite and writes the bundle into `custom_components/saj_local/frontend/` as `saj-local-<hash>.js` with an `asset-manifest.json`, because HACS ships the integration directory as one archive. Git tracks the built bundle and the manifest, so a change to the cards is committed together with a new build. The integration reads the manifest, serves the file the manifest names and adds the URL of the file to the Home Assistant frontend, so users add no dashboard resource.

The hash changes with every build so a browser never runs a stale bundle. The cost is that Home Assistant registers the hashed file name once, at start: a new bundle needs a Home Assistant restart before the browser is offered the new file. The development instance mounts the integration directory, so run `make build` and restart Home Assistant to see a change.

## Source layout

The layout follows what changes together:

- `src/system/` holds everything that is not drawing: finding a system's entities in `hass`, power direction, weekdays, schedule slots, faults, the control lock and service calls. The folder never touches the DOM, so the rules are tested without a browser.
- `src/ui/` holds the parts every card draws, styled only with Home Assistant's theme variables, because the Home Assistant frontend promises no `ha-*` element to custom cards.
- `src/cards/`, `src/features/` and `src/badges/` hold the elements and register the elements with the Home Assistant picker.
- `src/i18n/` holds the text only the cards need, one file per language, with English as the fallback. Entity names, states and values come from Home Assistant.
- `tests/fakes/` holds a fake `hass`, built from a list of entities, and the replacements for the modules an element uses. Each unit test exercises one module with every collaborator replaced by one of the fakes.

An element finds the entities of a system by device and translation key, never by entity ID, so a card never depends on an entity ID prefix.

## Tests

`make test-frontend` runs the Vitest unit tests with the coverage gate. `make test-browser-controlled` runs Playwright against the built bundle with controlled data, and `make test-browser-home-assistant` runs Playwright against a real Home Assistant, see the [checks page](checks.md#make-targets). The screenshots of the user documentation come from a third Playwright configuration, see [Screenshots](documentation.md#screenshots).

## Showcase dashboards

Looking at every card in every option needs a Home Assistant with real systems, so the development environment declares two dashboards, `saj-hs3` and `saj-h2`, from `config/dashboards/saj-hs3.yaml` and `config/dashboards/saj-h2.yaml`, through the `lovelace: dashboards:` block of `config/configuration.yaml`. The dashboards are plain YAML written by hand, and no script generates the dashboards. Each SAJ Local element is a custom element configured by its own YAML, so every card, tile feature and badge is written out individually with every option set, under a heading that names the card and its options.

- Each dashboard has four views: Dashboard (the cards of a typical system dashboard, written out as plain cards), Cards (every card in each of its option combinations), Features and badges (a tile card with the `custom:saj-local-weekdays-feature` feature for each slot weekdays entity, and the status badge) and Empty states (each card with no `device` and with the device of something that is not SAJ Local).
- The dashboards hold the device IDs of one development instance. A developer whose instance has different device IDs replaces the two `device` IDs in each file, the ID of the system and the ID of a device that is not SAJ Local for the Empty states view, and the slot weekdays entity IDs when the entity ID prefix differs.
- Home Assistant reads the dashboard declarations when Home Assistant starts, so restart Home Assistant after changing `config/configuration.yaml`. A change to a dashboard file shows after a reload of the page.
