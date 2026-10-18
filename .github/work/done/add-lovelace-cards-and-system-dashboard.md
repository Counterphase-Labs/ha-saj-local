# Add Lovelace Cards

## Plan Metadata

- **Revision:** 3
- **Status:** Approved
- **Last revised:** 2026-10-18
- **Requirements:** `../requirements.md`
- **Code style:** `../code-style.md`
- **Roadmap item:** "Lovelace cards" in the [Roadmap project](https://github.com/orgs/Counterphase-Labs/projects/1)
- **Builds on:** `scaffold-project-foundation.md`, `add-opt-in-register-writes.md`, `add-model-neutral-power-control-with-schedules.md`, `add-device-faults-and-repairs.md`, `add-full-h2-support.md` and the plans they build on. Everything in those plans that is not restated or explicitly replaced here continues to apply.

## Outcome And Scope

A user adds SAJ Local cards, a tile card feature and a badge to any Home Assistant dashboard. Every element is set up by choosing one SAJ system, so a home with two systems adds the same card twice, once per system. Every element shows only what the chosen system has, follows the user's theme and language, and keeps working when the system's prefix changes.

| | Today | With this plan |
| --- | --- | --- |
| SAJ cards on a dashboard | None. The built bundle holds a placeholder card and is not served | Six cards, one tile card feature and one badge, served and registered by the integration with no user step |
| Weekdays of a schedule slot | A number from 0 to 127 | Seven named day buttons in the user's language |
| Whether a system accepts changes | Visible only in Configure | A `control_allowed` binary sensor per system. Cards show controls as locked while the sensor is off |
| Controls on a system with Allow control on | Every schedule slot entity and most controls start disabled and are enabled one at a time, 141 entities on an HS3 with every piece of equipment fitted | Switching Allow control on enables the system's control set. Switching Allow control off disables the control set again |
| Battery and grid power sign | Published as the inverter reports, README says the grid sign is unlabelled | One documented sign on every model, used by the power flow card |
| Development | No dashboard to look at the elements with | One YAML showcase dashboard per supported model (HS3, H2) in the development environment, with every element written out individually, never shipped |

Elements delivered, each described under Behaviour:

| Element | Type | Purpose |
| --- | --- | --- |
| `saj-local-power-flow-card` | Card | Live power between solar, battery, grid, home and the optional equipment |
| `saj-local-status-card` | Card | Operating state, mode, key readings, today's energy, fault and change-lock summary |
| `saj-local-faults-card` | Card | Active faults per piece of equipment, with clear-fault |
| `saj-local-battery-card` | Card | State of charge with reserve and limits, battery readings, one row per pack |
| `saj-local-controls-card` | Card | The shared controls the system offers |
| `saj-local-schedule-card` | Card | Charge, discharge and EV charger slots, with a week timeline and slot editor |
| `saj-local-weekdays` | Tile card feature | Weekday buttons on a slot's weekdays entity |
| `saj-local-status-badge` | Badge | Operating state and active fault count |

Included:

- The frontend bundle, its unit tests and its controlled browser smoke test.
- Serving and registering the bundle from the integration.
- The `control_allowed` binary sensor.
- The control set: a catalogue flag, enabling and disabling with Allow control, and the request cost in the Allow control warning.
- The showcase dashboards, in the development environment only, as YAML dashboards with every element written out individually.
- One `make build`, which replaces `frontend-build`, and one `make test`, which runs every test suite.
- Translations, README and `documentation/development.md`.

Not changed: readings, except that the HS3 gains the shared `backup_load_power` reading (see Integration), the entities enabled by default while Allow control is off, the request load while Allow control is off, the mock.

## Requirements

| Requirement | How it is met |
| --- | --- |
| Expose UI elements for Lovelace dashboards, informational and configuration | The six cards, the feature and the badge |
| Each element is set up by choosing a system, once per system | Every card's and the badge's only required option is `device`, chosen with Home Assistant's device selector filtered to SAJ Local. The weekdays tile card feature takes the tile's entity and finds the system through the entity's device. Nothing is shared between two elements |
| Each element shows only what its system has, and keeps working when the prefix changes | Elements find entities through the entity registry by device and key, never by entity ID (Decision 4). A part whose entity does not exist is not drawn |
| Elements look and behave like standard Home Assistant cards and follow the user's theme and language | Theme variables with fallbacks, the standard card and editor contracts, actions through `hass-action`, values and names through Home Assistant's own formatters (Decisions 5 and 6) |
| Each system shows whether changes are allowed | The `control_allowed` binary sensor |
| Switching writing on enables the system's controls, with the added request load in the warning | The control set (Decision 17) |
| Battery and grid power use one sign on every model | Both models already report the sign. The README states the convention, and the power flow card reads the sign as stated (Decision 3) |
| A single unified interface across models | Cards work from model-neutral keys. No element tests for a model. The showcase dashboards are development configuration and are the one place written per model |
| Full localisation | Entity names, states and integration errors come from the integration's translations through Home Assistant. Card text comes from bundled translations in every language the integration has |
| Writing requires opt in, changes are rate limited, a failed change says what happened | Controls write through the existing entity services, so every existing check applies. A control commits once per user decision, never while dragging. A refusal shows the integration's translated message |
| Intelligent Modbus access | Cards read entity states only. No element adds a Modbus request. The control set adds reads only after the user accepts the cost shown in the Allow control warning |
| The repository contains every element, including Lovelace components and custom dashboards | The bundle ships inside the integration. The showcase dashboards live in the repository's development configuration |
| Playwright tests for UI covering only critical paths | One controlled test that every element renders, and one Home Assistant test that a dashboard with a power flow card loads and shows a value |
| 100 % unit test coverage | Vitest gate at 100 % for the frontend, the existing pytest gate for the integration changes |
| One `make build`, one `make test`, one `make ci` | `make build` builds the product bundle. `make test` runs every test suite, and each suite keeps its own target. No build target exists per feature or part |

## Decisions

Decisions 1, 3, 5, 6, 9, 10, 11, 12, 16, 17, 18 and 19 were made or confirmed by the user on 2026-10-17. The others are set by this plan and listed so they can be challenged.

| # | Decision | Outcome |
| --- | --- | --- |
| 1 | Elements in this item | All of the Elements table, in one plan |
| 2 | How the bundle reaches the browser | The integration serves the built file at `/saj_local/<hashed file name>` with cache headers and adds the URL with `frontend.add_extra_js_url`. The hashed file name changes with every build, so a browser never runs a stale bundle and the user never adds a resource or clears a cache. The registration works for storage and YAML dashboards alike |
| 3 | Battery and grid power sign | One fixed convention for every model, never a configuration option: positive when the battery discharges or the system sends power to the grid, negative when the battery charges or the system takes power from the grid. The convention is the same one the power control targets already use. A future model translates its readings into the convention in its own model file |
| 4 | How an element finds a system's entities | From `hass.entities`: entries with `platform` `saj_local` and the chosen `device_id`, keyed by `translation_key`. The integration sets every entity's translation key to the entity's model-neutral key, and the key is unique within a system. Entity IDs, prefixes and display names are never used |
| 5 | Which Home Assistant frontend APIs are used | Only APIs the Home Assistant frontend documentation describes for custom cards: the card, card feature and badge contracts; `window.customCards`, `window.customCardFeatures` and `window.customBadges`; `getConfigForm` with selectors; `getStubConfig`; `getGridOptions` and `getCardSize`; the `hass-action` event; the documented `hass` members (`states`, `entities`, `devices`, `locale`, `language`, `callService`, `localize`, `loadBackendTranslation`, `formatEntityState`, `formatEntityName`); `window.loadCardHelpers` and the theme variables. No `ha-*` element is used, `ha-card` included, because the frontend makes no promise about them. Every visual part is a project element styled with the theme variables so the parts match standard cards |
| 6 | Localisation | Entity names through `hass.formatEntityName`, states and values through `hass.formatEntityState`, integration error messages through `hass.loadBackendTranslation("exceptions", "saj_local")` and `hass.localize`. Weekday names and relative times from `Intl` with the user's language. Card-only text from translation files bundled with the cards under `frontend/src/i18n/`, one for each language in `custom_components/saj_local/translations/`, chosen by `hass.language` with English as the fallback. Home Assistant gives `getConfigForm` no `hass`, and registers picker entries before any element has `hass`, so editor labels and picker names and descriptions use the page language, which Home Assistant sets to the user's language, with English as the fallback |
| 7 | `control_allowed` entity type | A read-only binary sensor, not a switch. The requirements switch writing on "with a warning first", and a switch on a dashboard would switch writing on with no warning. A card that finds the sensor off shows its controls locked and links to the integration's settings, where the warning is shown |
| 8 | When a control writes | Once per user decision: a slider on pointer release, or on Enter or leaving the slider after keyboard changes; a number field on Enter or leaving the field, never on a spinner click or arrow key; a select or switch on change, a time field on change, the weekday buttons 1.5 seconds after the last press or when focus leaves the buttons. A change in progress disables the control and shows a busy indicator. The control then shows the entity's state, which is the value the inverter holds; nothing is shown optimistically |
| 9 | Slots outside time-of-use mode | The schedule card shows a notice with the application mode next to the notice and never changes the mode itself. Both `time_of_use` and `time_of_use_bms` count as time-of-use modes, because the SAJ app's TOU (BMS) mode keeps its charge settings in the ordinary charge slots (Evidence) |
| 10 | Entities a card needs that are disabled | Home Assistant gives the frontend no disabled entities, so a card cannot list the disabled entities it misses. A card that finds none of its entities shows an empty state that says which kind of entity to enable, with a link to the system's device page. A card that finds some draws what it found. A card with controls on a system whose `control_allowed` is `off` shows the locked message instead of the empty state |
| 11 | Several systems | Every element binds to one system through its own `device` option, so any number of the same element can sit on one dashboard, each with a different system |
| 12 | Showcase dashboards | One per supported model (HS3, H2), in the development configuration only, as YAML dashboards in which every card, tile feature and badge is written out individually with every option, so each element's configuration is visible. No generated dashboard exists, for users or for development |
| 13 | Meter B in the power flow card | Shown as a reading without a flow direction. Meter B readings have no sign evidence on either model, and a wrong arrow is worse than none |
| 14 | Commands on the controls card | Synchronise clock only. Restart inverter stays an entity and is left off the card, so a dashboard tap cannot restart the inverter. Clear current fault sits on the faults card |
| 15 | Placeholder card | `saj-local-card` and its tests are removed. The bundle entry becomes `src/index.ts` and the file name `saj-local-[hash].js` |
| 16 | Week order | The timeline and the weekday buttons start on the user's first weekday from `hass.locale.first_weekday`. When the setting is `language`, the first weekday comes from `Intl.Locale(hass.language).weekInfo.firstDay`, the same rule Home Assistant's own calendars use, and Monday where the browser has no `weekInfo`. The stored bits do not move: bit 0 is Monday on every model |
| 17 | Entities the cards need that start disabled | Every schedule slot entity and most controls are disabled by default, and the poller reads every enabled entity. A control set, flagged in each model's catalogue, is enabled when Allow control is switched on and disabled again when Allow control is switched off. Entities the user disabled stay disabled, and entities the user enabled stay enabled. The Allow control warning shows the request cost before and after. The cards never enable entities themselves. See Control Set |
| 18 | Telling two systems apart | A system's title is the device name (the user's name first) followed by the model, both from `hass.devices`, for example "SAJ HS3 (12000 W)". When two SAJ Local devices share a title, each title adds the device's serial number. No integration change: the device registry already holds the model and serial number |
| 19 | Partly enabled slots | A slot is drawn only when every key of the slot exists. A slot with some keys disabled is left out, and the schedule card's empty state counts the slots left out |

## Evidence

- **Battery power sign:** the hand-verified HS3 readings record battery power negative while charging and positive while discharging. The H2 document defines battery direction −1 as charging. Both models read battery power from the same register.
- **Grid power sign:** the hand-verified HS3 readings record grid power at −2074 W together with a grid direction of −1, and a grid target of −500 gave about 600 W of import. The H2 document defines grid direction −1 as taking power from the grid and 1 as sending power to the grid. Both models read grid power from the same register.
- **Slot weekdays:** the hand-verified HS3 readings record bit 0 of the slot weekday field as Monday. Both models use the same slot layout.
- **TOU (BMS) mode:** the hand-verified HS3 readings record that selecting TOU (BMS) in the SAJ app sets application mode 11 (`time_of_use_bms`), and that charge settings entered in TOU (BMS) are written to the ordinary charge slots and their enable bits, with the mode left at 11.
- **Control set cost:** at the default 60-second interval with every piece of equipment fitted, enabling the register entities of the control set raises the planned load from 14 to 18 requests per minute on an HS3 and from 9 to 10 on an H2, against the budget of 40. The control set enables 141 entities on an HS3 (135 register entities and the switch and target of three power functions) and 87 on an H2 (85 register entities and the switch and target of the battery power function). Slot fields share packed registers, so the 135 HS3 register entities cost 4 requests per read.
- **Enabling entities:** Home Assistant reloads a config entry 30 seconds after any of its entities is enabled in the entity registry, whoever enables the entity.
- **Frontend APIs:** Home Assistant's frontend documentation for custom cards, card features, badges, card editors, resources and the `hass` object, and the `hass-action` event announced for custom cards in Home Assistant 2023.7. Every API in Decision 5 is present in the 2026.9.3 frontend the project pins.

## Behaviour

### Common To Every Element

- **Configuration:** `device` is required. Each element's other options are listed with the element. The visual editor comes from `getConfigForm`: the device selector with `filter: { integration: saj_local }` and one selector per option, with labels from the bundled translations in the page language (Decision 6). Home Assistant gives `getConfigForm` no `hass`, so the editor offers the same options on every system.
- **Starting configuration:** `getStubConfig` picks the first SAJ Local device, so the card picker preview shows a real system. With no SAJ Local device, the stub has no device and the element shows its empty state.
- **Not a SAJ system:** a `device` with no SAJ Local entity shows "Choose a SAJ Local system" in the element.
- **System unavailable:** when every entity the element shows is unavailable, the element shows "Not answering" and dims its values. Single unavailable values show "Unavailable".
- **System title:** wherever an element names its system, the title follows Decision 18.
- **Operating state colours:** used by the power flow card, the status card and the status badge.

  | `operating_mode` state | Colour |
  | --- | --- |
  | `operating` | Primary colour |
  | `off_grid`, `grid_connected_load_bypass` | Warning colour |
  | `fault` | Error colour |
  | `initialisation`, `standby`, `upgrade`, `debugging`, `self_check`, `reset` | Secondary text colour |
  | Unknown or unavailable | Disabled text colour |

- **Values:** shown with `hass.formatEntityState`, so the user's unit, display precision and number format apply. A value whose direction is shown in words (battery, grid) is formatted from its absolute value.
- **Tap:** tapping a value opens Home Assistant's more-info dialog for the entity, through a `hass-action` event with `action: more-info`. Links to settings and device pages use `action: navigate`.
- **Theme:** the card container uses `--ha-card-background` (falling back to `--card-background-color`), `--ha-card-border-radius`, `--ha-card-border-width`, `--ha-card-border-color`, `--ha-card-box-shadow` and the primary text, secondary text, disabled text, primary, divider, error, warning and success colour variables. Power flow colours use the energy colour variables (`--energy-solar-color`, `--energy-battery-in-color`, `--energy-battery-out-color`, `--energy-grid-consumption-color`, `--energy-grid-return-color`). Every variable has a fallback.
- **Icons:** Material Design Icons paths from the `@mdi/js` package, drawn as inline SVG.
- **Motion:** animation stops when the user prefers reduced motion.
- **Accessibility:** every control is reachable by keyboard and has an accessible name. The weekday buttons are toggle buttons with `aria-pressed`. Switches use `role="switch"`.
- **Locked controls:** a card with controls looks up the system's `control_allowed` entity. While the entity is `off`, every control is disabled and the card shows "Changes are off for this system" with a link to `/config/integrations/integration/saj_local`. While the entity is missing or unavailable, controls stay enabled and a refusal explains itself.
- **Locked and empty:** while `control_allowed` is `off`, a card with controls that finds none of its controls shows the locked message and the settings link in place of the empty state of Decision 10, because the control set is enabled by switching Allow control on, not by enabling entities on the device page.
- **Change errors:** a rejected service call shows the message under the control until the next change of the control. A message with a `saj_local` translation key is shown from the integration's exception translations with its placeholders, other messages as given.

### Power Flow Card

Options: `show_strings` (default off), `show_optional` (default on), `scope` (`system` or `parallel`, default `system`). With `scope: parallel` on a system without the parallel readings, no parallel key exists, so the card shows the empty state of Decision 10.

Nodes, each drawn only when the key exists:

| Node | Key (`scope: system`) | Key (`scope: parallel`) | Secondary |
| --- | --- | --- | --- |
| Solar | `pv_power` | `parallel_pv_power` | With `show_strings`, each `pvN_power` key present (N from 1) beneath the node |
| Battery | `battery_power` | `parallel_battery_power` | `battery_soc` or `parallel_battery_soc`, and "Charging", "Discharging" or "Idle" |
| Grid | `grid_power` | `parallel_grid_power` | "Importing", "Exporting" or "Idle" |
| Home | `load_power` | `parallel_load_power` | |
| Inverter | `operating_mode` | `operating_mode` | The state, in the operating state colour (Common To Every Element) |
| EV charger (optional) | `ev_power` | `ev_power` | `ev_status` |
| Backup load (optional) | `backup_load_power` | `parallel_backup_load_power` | |
| Meter B (optional) | `meter_b_power` | `parallel_meter_b_power` | No flow line direction (Decision 13) |

Layout: the inverter in the centre, solar above, grid left, home right, battery below, optional nodes in a row below the battery. Lines run from each node to the inverter. A line animates while the node's absolute power is above 10 W: solar flows towards the inverter; the battery flows towards the inverter when positive and away when negative; the grid flows away from the inverter when positive and towards the inverter when negative; home, EV charger and backup load flow away from the inverter. Animation speed rises with power on a logarithmic scale, so 50 W and 5 kW both read clearly. The drawing is an SVG with a fixed view box, so the card scales to any width. Grid options: 12 columns by default, at least 6.

### Status Card

Options: `show_energy` (default on).

| Part | Keys |
| --- | --- |
| Header | The system title (Decision 18) |
| State | `operating_mode`, in the operating state colour |
| Mode | `application_mode`, and `application_mode_active` when present and different, labelled as the mode running now |
| Readings | `battery_soc`, `inverter_temperature`, `battery_temperature`, `off_grid_mode` |
| Today | `pv_energy_today`, `load_energy_today`, `grid_import_energy_today`, `grid_export_energy_today`, `battery_charge_energy_today`, `battery_discharge_energy_today` |
| Faults | The number of `inverter_fault`, `battery_fault` and `ev_fault` that are on, as "No faults" or "2 faults" in the error colour. Tapping opens more-info of the first summary that is on |
| Changes | `control_allowed` as "Changes allowed" or "Changes off" |

### Faults Card

Options: `show_clear_groups` (default on).

- One group per summary key present: `inverter_fault` (Inverter), `battery_fault` (Battery), `ev_fault` (EV charger).
- A group lists every binary sensor of the system whose key starts with the group's prefix and `_fault_`, plus, for the battery, `battery_packN_fault` and `battery_packN_warning`, while the sensor is on. Each row shows the entity name and how long ago the fault turned on, from `last_changed`.
- A group's `<prefix>_fault_unrecognised` row adds "See the diagnostics download for the register and bit".
- A group with no active fault shows "No active faults" in the success colour, and is hidden when `show_clear_groups` is off.
- `clear_current_fault` (button), when present, is a "Clear fault" action in the inverter group while the inverter summary is on, locked as described under Common.

### Battery Card

Options: `show_packs` (default on).

- A ring gauge of `battery_soc`, with markers for `backup_reserve_soc`, `battery_charge_limit` and `battery_discharge_limit_on_grid` where present.
- `battery_power` as an absolute value with "Charging", "Discharging" or "Idle".
- Rows for `battery_voltage`, `battery_current`, `battery_temperature`, `battery_usable_capacity`.
- With `show_packs`, one row per pack N with any `battery_packN_*` key: state of charge, state of health, voltage, current, temperature and cycles, each where present, and a fault or warning mark from `battery_packN_fault` and `battery_packN_warning`.
- A system without `battery_soc` shows "This system has no battery".

### Controls Card

Options: `sections` (a list of `mode`, `battery`, `grid`, `power_control`, `ev_charger`, `device`; default all).

| Section | Keys |
| --- | --- |
| Mode | `application_mode`, `time_of_use_idle_mode`, `time_of_use_grid_discharge` |
| Battery | `backup_reserve_soc`, `battery_charge_limit`, `battery_discharge_limit_on_grid`, `battery_discharge_limit_off_grid`, `battery_charge_power_limit`, `battery_discharge_power_limit`, `battery_forced_charge_power_limit` |
| Grid | `export_limit_mode`, `export_limit_power`, `export_limit_current`, `grid_import_power_limit`, `grid_export_power_limit` |
| Power control | For each of Battery, Grid and Inverter: `<function>_power_control` and `<function>_power_target` on one row, with the sign shown under the target: "Positive discharges, negative charges" for Battery, "Positive exports, negative imports" for Grid, "Positive puts out, negative takes in" for Inverter |
| EV charger | `ev_enabled`, `ev_mode`, `ev_charge_power` |
| Device | `buzzer`, `led_mode`, `synchronise_clock` |

- Number controls follow the entity's `min`, `max`, `step`, unit and `mode` attributes: `slider` gives a slider with the value beside, `box` a number field, `auto` a slider when the range has at most 256 steps and a number field otherwise.
- Select controls list the entity's `options` with names from `hass.formatEntityState`.
- A section with no key present is not drawn. A card with no section drawn shows the empty state of Decision 10, naming configuration entities.

### Schedule Card

Options: `kinds` (a list of `charge`, `discharge`, `ev`; default all), `show_timeline` (default on).

A slot is the keys `<stem>_start` (time), `<stem>_end` (time), `<stem>_days` (number), `<stem>_power` (number) and `<stem>_enabled` (switch), with stems `charge_slot_N`, `discharge_slot_N` and `ev_slot_N` for N from 1 to 7. An EV slot has no `_enabled` switch and adds `<stem>_mode` (select), `<stem>_grid_charging` and `<stem>_battery_discharge` (switches). A slot is drawn only when every key of the slot exists (Decision 19).

- **Empty state:** a card with no slot drawn shows the empty state of Decision 10. When slots were left out because some of their keys are disabled, the empty state says how many, for example "3 slots have disabled entities". The same count shows under the slot list when some slots are drawn.

- **Timeline:** seven rows in week order (Decision 16), 24 hours across. Each slot of each kind is a bar on every day its weekdays include, coloured by kind; a disabled charge or discharge slot is drawn hatched. A slot whose end is before its start runs to midnight and continues on the next day. Tapping a bar opens that slot in the list.
- **Slot list:** one row per slot: "Slot N", the times, the weekday short names and the power, with the enable switch for charge and discharge slots. Expanding a row only reveals the editor and never writes. The editor holds the start and end time fields, the power control, the weekday buttons and, for EV slots, the mode select and the two switches.
- **Time-of-use notice:** when the card shows charge or discharge slots and `application_mode` exists with a state other than `time_of_use` or `time_of_use_bms` (Decision 9), a notice reads "Charge and discharge slots only run in time-of-use mode" with the `application_mode` select beside the notice.
- **Weekdays:** the weekday buttons convert between the seven named days and the slot's weekday number, bit 0 Monday to bit 6 Sunday.

### Weekdays Tile Card Feature

- Offered by `isSupported` for a `number` entity whose registry entry has `platform` `saj_local` and a translation key ending in `_days`.
- Seven toggle buttons in week order, labelled with short weekday names, using `--feature-height`, `--feature-border-radius` and `--feature-button-spacing`. Click handlers stop propagation so the tile does not open more-info.
- Writes as in Decision 8 and locks with the `control_allowed` entity of the same device.

### Status Badge

- Shows an icon and the `operating_mode` state in the operating state colour, and the number of active fault summaries in the error colour when one or more is on.
- Drawn as a pill matching native badges with the theme variables. Tapping opens more-info of `operating_mode`.

### Control Allowed Sensor

- `binary_sensor.saj_control_allowed` (`binary_sensor.saj_<prefix>_control_allowed` with a prefix): on while the system's Allow control option is on and the model is verified, the same condition that lets the integration write today. Diagnostic category, enabled by default, named "Control allowed".
- The Allow control option already reloads the system, so the sensor changes with the option.
- One more entity per system: the README's entity counts each rise by one.

### Control Set

- **Members:** every entity a card can change, flagged in the model's catalogue next to the existing default-enabled flag:
  - Every key of every charge, discharge and EV charger slot.
  - The power control switches and targets of every function the system offers.
  - The keys of the controls card's Mode, Battery, Grid, EV charger and Device sections.
  - `clear_current_fault`.

  Battery pack readings and other read-only entities are not members. A member that is already enabled by default stays as it is.
- **Switching on:** when a system with Allow control on and a verified model is set up, every member whose registry entry is disabled by the integration is enabled and marked in the entity registry's options for `saj_local` as enabled with control. A member disabled by the user is left disabled. Home Assistant then reloads the system once more 30 seconds later, as it does when a user enables an entity, and the members appear.
- **Second reload:** the reload 30 seconds after the members are enabled unloads the system, and unloading switches off every power control function switched on from Home Assistant, as every reload does today. A power control function switched on between saving and the second reload is therefore switched off again. The same second reload follows whenever a new member is enabled later (New members). The warning tells the user to wait until the entities appear before changing anything.
- **Switching off:** when a system with Allow control off, or with a model that is not verified, is set up, every marked member that is still enabled is disabled by the integration and the mark is removed. A member the user enabled by hand has no mark and stays enabled. Disabling causes no further reload: Home Assistant removes each disabled entity at once, and the poller stops reading an entity once the entity is removed, so the request load returns to the load before Allow control was switched on.
- **User changes win:** while the system is loaded, the integration listens for entity registry updates of its own entities. When the user disables a marked member, the mark is removed, so the member stays the user's choice from then on.
- **New members:** the setup step runs on every setup, so a member that appears later, such as the EV charger slots after an EV charger is detected, follows the same rule.
- **Warning:** the Allow control confirmation, in both the setup flow and Configure, adds: "Allowing control also enables {count} control entities of this system, such as schedule slots and battery limits, so they can be shown and changed on dashboards. Reading them raises the load from {before} to {after} of {budget} requests per minute. The entities appear about 30 seconds after saving. Wait until they appear before changing anything: the system reloads once more when they appear, and the reload switches off any power control function switched on before then." `{count}` counts the members the integration would enable. `{before}` and `{after}` come from the load calculation Configure already uses, with and without those members.
- **Warning in the setup flow:** a new system's equipment is detected only when the system is first set up, after the setup flow ends, so the setup flow counts the members and the load with every piece of equipment the model can have fitted. The setup flow's text therefore reads "up to {count} control entities" and "from {before} to up to {after}". Configure uses the fitted equipment already stored, so Configure's figures are exact.

### Showcase Dashboards (Development Only)

- `config/configuration.yaml` declares two YAML dashboards, `saj-hs3` ("SAJ HS3") and `saj-h2` ("SAJ H2"), shown in the sidebar.
- `config/dashboards/saj-hs3.yaml` and `config/dashboards/saj-h2.yaml` write every element out individually, each with `type`, `device` and every option set explicitly, under a heading naming the element and its options, in four views:
  - **Dashboard:** the status badge and the sections Now (power flow card), Status (status card, faults card), Battery (battery card), Controls (controls card) and Schedules (schedule card).
  - **Cards:** every card in each of its option combinations.
  - **Features and badges:** a tile card with the weekdays feature for every slot weekdays entity of the system, and the status badge.
  - **Empty states:** each card with no device and with a device that is not SAJ Local.
- The dashboards hold the development instance's device IDs. A developer whose instance has other device IDs replaces the two IDs.
- Nothing is built for the showcase, so `make build` builds only the product bundle and no showcase file can reach the release archive.

## Implementation Design

### Frontend

All under `frontend/src/`. Every module has unit tests under `frontend/tests/` mirroring the path.

| Module | Content |
| --- | --- |
| `index.ts` | Defines every element and pushes the picker entries for cards, the feature and the badge |
| `hass.ts` | The project's own TypeScript types for the documented `hass` members the bundle uses |
| `system/entities.ts` | The SAJ Local devices of `hass`, and a system's entities keyed by translation key (Decision 4) |
| `system/power.ts` | Direction of a battery, grid or consumer power under the sign convention and the 10 W threshold |
| `system/weekdays.ts` | Weekday number to days and back, week order from the locale, short names from `Intl` |
| `system/schedule.ts` | Slots of a system by kind, and timeline bars per day including slots past midnight |
| `system/faults.ts` | Fault groups and active rows of a system |
| `system/control.ts` | The lock state of a system, service calls with busy state, and translated error messages |
| `actions.ts` | `hass-action` events for more-info and navigate |
| `i18n/` | `localize.ts` (card text by language with English fallback, `Intl` helpers) and one JSON file per language |
| `ui/` | The card container, value row, notice, empty state, switch, number control, select control, time control, weekday buttons, ring gauge and icons |
| `cards/` | The six cards, each with its `getConfigForm`, `getStubConfig` and `getGridOptions` |
| `features/weekdays-feature.ts` | The tile card feature |
| `badges/status-badge.ts` | The badge |

- `package.json`: `@mdi/js` as a dependency. The one `build` script runs Vite with `vite.config.ts`.
- `vite.config.ts`: entry `src/index.ts`, output file name `saj-local-[hash].js`. Vitest coverage keeps `src/**/*.ts` at 100 %.
- `tests/fakes/hass.ts`: a fake `hass` built from a list of entities (key, domain, state, attributes), with recorded service calls, used by every element test.

### Integration

| Module | Change |
| --- | --- |
| `frontend.py` (new) | Reads `frontend/asset-manifest.json` in the executor, registers the entry file with `StaticPathConfig` (cache headers on) and adds the URL with `add_extra_js_url`. A missing or unreadable manifest logs one error naming the file, and the integration loads without cards |
| `__init__.py` | `async_setup`, which registers the frontend once per Home Assistant start, and `CONFIG_SCHEMA` for a config-entry-only integration. After the platforms are set up, `async_setup_entry` applies the control set and starts the registry listener, removed on unload |
| `controls.py` (new) | The control set of a system: its members from the catalogue flag and the power functions offered, applying the switching-on and switching-off rules to the entity registry, the registry listener that removes a mark when the user disables a member, and the members the integration would enable, for the warning |
| `saj/definitions.py`, `saj/catalogue.py` | A `control` flag on a definition and on a register, beside `core`, set on every member key of HS3 and H2 |
| `saj/models/hs3.py` | The HS3 publishes the shared `backup_load_power` reading, enabled by default as on the H2, translated in the HS3 model as the sum of the HS3's verified live backup phase powers `backup_l1_power`, `backup_l2_power` and `backup_l3_power`. The HS3 has no live total register: `AverBackupPower` (5182H) is a five-minute average, a different quantity. The H2 keeps reading `backup_load_power` from 40ABH |
| `config_flow.py` | The Allow control confirmation of the setup flow and of Configure gets the `count`, `before`, `after` and `budget` placeholders |
| `manifest.json` | `dependencies`: `frontend`, `http` |
| `binary_sensor.py` | The `control_allowed` entity, reading the coordinator's existing `control_allowed` |
| `translations/en.json` | The `control_allowed` entity name and the new Allow control confirmation text, in the setup flow and in Configure |

### Development Environment And Tooling

| File | Change |
| --- | --- |
| `config/configuration.yaml` | The `lovelace` block of the showcase |
| `config/dashboards/saj-hs3.yaml`, `config/dashboards/saj-h2.yaml` (new) | The two showcase dashboards |
| `.gitignore` | Unignores `config/dashboards/` and the two YAML files |
| `Makefile` | `build` replaces `frontend-build`: `build` runs the frontend `build` script, which builds the product bundle. Every target that depended on `frontend-build` depends on `build`. No `showcase-build` or other per-feature build target exists. `test` runs every test suite, and each suite has its own target: the existing pytest run moves to `test-python`, the frontend unit tests get `test-frontend`, and `test-isolated`, `test-browser-controlled`, `test-browser-home-assistant` and `mock-smoke` stay. The partial targets that make up `ci` keep their content, with `python-ci` running `test-python` in place of `test` and `frontend-check` running `test-frontend` in place of its own unit test command. `release-check` matches `saj-local-[A-Za-z0-9_-]+\.js` |
| `frontend/src/card.ts`, `frontend/tests/card.test.ts` (removed) | The placeholder card and its unit tests (Decision 15) |
| `custom_components/saj_local/frontend/` | The committed `saj-local-card-*.js` is replaced by the built `saj-local-*.js`, and `asset-manifest.json` is rebuilt |
| `frontend/tests/browser/controlled/card.spec.ts` | Replaced by the controlled smoke test below |
| `frontend/tests/browser/home-assistant/` | The Home Assistant smoke test below |

## Verification And Acceptance

Unit tests, one module each, with the fake `hass` and every collaborator replaced:

- Entities: devices found by platform; entities keyed by translation key for the chosen device only; a second system's entities never mixed in; a device with no SAJ entity.
- Power: direction of positive, negative, zero and below-threshold values for battery, grid and consumer nodes.
- Weekdays: number to days and back for every bit; week order for each first weekday setting, including `language` with and without `weekInfo`; names follow the language.
- Schedule: slots built per kind only when every key exists; the count of slots left out; EV slots with their extras; bars for a normal slot, a slot past midnight and a slot with no days; disabled slots marked; the time-of-use notice for every application mode, absent for `time_of_use` and `time_of_use_bms`.
- System title: name and model; the user's name first; the serial number added only when two SAJ Local devices share a title.
- Faults: groups per summary present; active rows only; pack rows in the battery group; unrecognised row hint.
- Control: lock from on, off, missing and unavailable `control_allowed`; busy state during a call; translated and plain error messages; the commit rules of Decision 8, including the weekday delay and commit on focus leaving.
- Localisation: a missing key and a missing language fall back to English; every language file has the same keys as English.
- Each card, the feature and the badge: renders the parts for present keys and omits absent ones; empty, not-SAJ and not-answering states; locked controls; the locked message in place of the empty state while `control_allowed` is `off`; a control change calls the right service with the right data; tap dispatches the right `hass-action`; editor schema and stub configuration.
- Integration `frontend.py`: the static path and URL registered from the manifest; a missing manifest logs the error and registers nothing. `control_allowed`: on and off from the coordinator.
- Control set: members per model with every piece of equipment and with none; switching on enables only members disabled by the integration and marks the members; a member disabled by the user stays disabled; switching off disables only marked members and removes the marks; an unverified model counts as switched off; the listener removes the mark when the user disables a marked member; a member that appears after equipment detection follows the rule; switching off schedules no reload; the warning's count, before and after, exact in Configure and counted with every piece of equipment in the setup flow.

Browser smoke, load and function only:

- Controlled: the built bundle in a blank page with a fake `hass` renders each card, the feature and the badge with one value visible.
- Home Assistant: after the existing setup of an HS3 system, the test creates a storage dashboard holding a power flow card for the HS3 system over Home Assistant's websocket API, the dashboard opens and the power flow card shows a solar value. The test does not depend on the showcase dashboards.

Acceptance:

1. After installing the integration and restarting Home Assistant, the SAJ Local cards appear in the card picker with no resource added by the user.
2. A dashboard with two power flow cards, one per system, shows each system's own values, and still does after one system's prefix is changed.
3. On an H2 the controls card has no Grid or Inverter power control row, and the faults card has no EV charger group on a system without an EV charger.
4. With Allow control off, every control on the controls and schedule cards is disabled and the card links to the integration's settings. With Allow control on, changing `backup_reserve_soc` on the card makes one write and the card then shows the value the inverter holds.
5. Pressing Monday, Wednesday and Friday on a slot's weekday buttons writes the slot weekday number once, as 21.
6. A grid power of −2000 W draws the grid line flowing towards the inverter and labels the grid "Importing".
7. Changing Home Assistant's language changes every card's text, entity names, states and weekday names.
8. Two HS3 systems with the default device name get two different card titles, each with the system's serial number.
9. In the development environment, the SAJ HS3 and SAJ H2 dashboards show every element, each written out individually in YAML, against the HS3 and H2 mocks. The `Makefile` has no `frontend-build`, no `showcase-build` and no other per-feature build target, and `make test` runs every test suite.
10. On an HS3 with every piece of equipment fitted and every entity at its default, switching Allow control on shows the warning with 141 entities and the load rising from 14 to 18 requests per minute at the default interval. After saving, the schedule card shows all 21 slots. In a second run, a slot entity disabled by the user before the switch stays disabled, and the schedule card counts the slot as left out.
11. Switching Allow control off again disables every entity the switch enabled, keeps every entity the user enabled by hand, and returns the load to 14 requests per minute.
12. With the application mode at `time_of_use_bms`, the schedule card shows no time-of-use notice.
13. `make ci` passes with both coverage gates.

## Documentation

- README: a "Dashboard cards" section listing each element and its options with a YAML example, that the battery card's pack rows show pack readings only for the pack entities the user has enabled, and that a home with two systems is easier to read with each system's device renamed; the `control_allowed` entity; the control set under Allow control, with its members, the request cost, the second reload that switches off power control functions switched on before the entities appear, and the switching-off rule; the sign convention replaces the grid sign line under Limitations; entity counts updated.
- `documentation/development.md`: the frontend layout, the YAML showcase dashboards and their device IDs, `make build` building the product bundle, `make test` and the target of each test suite, and that a new product bundle needs a Home Assistant restart, because the hashed file name is registered at start.

## Roadmap Changes

The "Lovelace cards" item is removed when delivered.

## Work Sequence

1. Integration: `frontend.py`, `async_setup`, manifest dependencies, `control_allowed`, the control set with its catalogue flag, registry rules, listener and warning, with tests. Bundle entry renamed, placeholder card removed, `release-check` updated.
2. Frontend foundation: `hass.ts`, `system/`, `actions.ts`, `i18n/`, `ui/`, the fake `hass`.
3. Status, power flow, faults and battery cards.
4. Weekday buttons, the tile card feature and the schedule card.
5. Controls card.
6. Status badge.
7. Showcase YAML dashboards, development configuration, and `make test` with one target per test suite.
8. Browser smoke tests, README and `documentation/development.md`.

Each step ends with `make ci` passing, both coverage gates included.

## Revisions

| Revision | Date | Change |
| --- | --- | --- |
| 1 | 2026-10-17 | First draft, with the user's Decisions 1, 3, 5, 6, 9, 10, 11 and 12. |
| 2 | 2026-10-17 | Switching Allow control on enables the system's control set, and switching Allow control off disables the control set again (Decision 17). |
| 3 | 2026-10-18 | At the user's direction, no generated dashboard: the `custom:saj-local` dashboard and view strategies and the showcase strategy are removed, and the showcase dashboards write every element out individually in YAML (Decision 12). |
