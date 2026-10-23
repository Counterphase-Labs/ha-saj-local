# Card Features

The SAJ Local cards, tile card feature and badge show a SAJ system on a Home Assistant dashboard and let you change its settings from there. The integration serves them, so nothing needs installing.

## Elements and setup

Every element is added from Home Assistant's pickers and set up by choosing one SAJ system.

Files: [index.ts](../src/index.ts), [registration.ts](../src/registration.ts), [editor.ts](../src/cards/editor.ts), [system-card.ts](../src/cards/system-card.ts), [entities.ts](../src/system/entities.ts), [title.ts](../src/system/title.ts), [empty-state.ts](../src/ui/empty-state.ts)

Requirements: [Elements and setup](requirements.md#elements-and-setup)

- Six cards appear in the card picker: power flow, status, faults, battery, controls and schedule. The weekdays feature appears in the tile card's feature picker and the status badge in the badge picker.
- The power flow, status, faults, battery, controls and schedule cards show a live preview in the card picker.
- Each element is set up in Home Assistant's visual editor by choosing one SAJ system, and the first system is chosen for a new card. A home with two systems adds a card once per system.
- A card's title is the system's device name followed by its model. The serial number is added only when two systems would otherwise have the same title.
- Elements find a system's entities through Home Assistant's entity registry, so they keep working when the system's prefix changes.
- A part whose entity does not exist or is disabled is not drawn, so each card shows only what its system has.
- A card with none of its entities enabled says which kind of entity to enable, with a link to the system's device page.
- While the system is not answering, a card says so and dims its values.
- Tapping a value opens Home Assistant's details of that entity.

## Power flow card

The power flow card draws live power between solar, battery, grid, home and the optional equipment.

Files: [power-flow-card.ts](../src/cards/power-flow-card.ts), [power.ts](../src/system/power.ts)

- Solar, battery, grid and home are drawn around the inverter, which shows the operating state.
- Each line shows the direction of the flow, and moves faster as the power grows. A power of 10 W or less is drawn as idle.
- The battery shows its state of charge and whether it is charging or discharging. The grid shows whether the system is importing or exporting.
- With Show optional equipment on, the default, the EV charger, the backup load and Meter B are drawn when the system has them. Meter B is a reading with no direction.
- With Show solar strings on, the power of each solar string is listed.
- The Scope option draws the system's own readings or the parallel system's readings. A system without parallel readings shows the empty state with the parallel scope.

## Status card

The status card sums up a system in one place.

Files: [status-card.ts](../src/cards/status-card.ts), [operating.ts](../src/system/operating.ts)

- The status card shows the operating state, coloured by how healthy the state is, and the application mode. When the mode the H2 is running in differs from the chosen mode, the mode running now is shown as well.
- The status card shows the battery state of charge, the inverter and battery temperatures and off-grid mode.
- With Show today's energy on, the default, the status card shows today's solar, load, grid import, grid export, battery charge and battery discharge energy.
- The status card counts the pieces of equipment with an active fault, or says there are no faults.
- The status card shows whether control is allowed for the system.

## Faults card

The faults card lists the active faults of each piece of equipment.

Files: [faults-card.ts](../src/cards/faults-card.ts), [faults.ts](../src/system/faults.ts)

- The faults card groups faults by inverter, battery and EV charger, and lists each active fault with how long ago the fault began.
- An unrecognised fault says to look in the diagnostics download for the register and bit.
- A Clear fault button sits under the inverter's active faults. While control is not allowed for the system, the button is disabled and a lock links to the integration's settings.
- With Show groups without faults on, the default, a group with no active fault is shown as clear. With the option off, only groups with an active fault are shown.

## Battery card

The battery card shows the battery's charge, power and readings.

Files: [battery-card.ts](../src/cards/battery-card.ts), [ring-gauge.ts](../src/ui/ring-gauge.ts)

- A ring shows the state of charge, with the backup reserve, the charge limit and the on-grid discharge limit marked on the ring.
- The battery card shows the battery power with whether the battery is charging or discharging, and the voltage, current, temperature and usable capacity.
- With Show battery packs on, the default, each pack gets a row group with its state of charge, health, voltage, current, temperature, cycles, fault and warning. A pack reading is shown only when its entity is enabled.
- A system with no battery says so.

## Controls card

The controls card gathers the settings a system offers into sections.

Files: [controls-card.ts](../src/cards/controls-card.ts), [entity-controls.ts](../src/cards/entity-controls.ts), [control-element.ts](../src/ui/control-element.ts), [number-control.ts](../src/ui/number-control.ts), [select-control.ts](../src/ui/select-control.ts), [switch.ts](../src/ui/switch.ts), [time-control.ts](../src/ui/time-control.ts), [press-control.ts](../src/ui/press-control.ts), [control.ts](../src/system/control.ts)

- The sections are Mode, Battery, Grid, Power control, EV charger and Device. The Sections option chooses which are shown, and a section with nothing to show is left out.
- Mode holds the application mode and the time-of-use settings. Battery holds the backup reserve and the charge and discharge limits. Grid holds the export limit settings and the grid power limits. EV charger holds the charger's switch, mode and charge power. Device holds the buzzer, the LED mode and clock synchronisation.
- Power control shows each power control function the system has, with the function's switch, power target and a hint on what a positive and a negative power do.
- Each setting uses the control that fits it: a slider or number field, a list, a switch, a time field or a button.
- A control changes the inverter once per decision: a slider when released, a number field on Enter or on leaving the field, and a list, switch or time field on change. The control then shows the value the inverter holds.
- A refused change is shown under the control in the integration's own words.
- While control is not allowed for the system, every control is disabled and a lock above the controls links to the integration's settings, where Allow control is switched on.
- The controls card has no restart button, so a tap on a dashboard cannot restart the inverter.

## Schedule card

The schedule card shows and edits the charge, discharge and EV charger slots.

Files: [schedule-card.ts](../src/cards/schedule-card.ts), [schedule.ts](../src/system/schedule.ts), [weekdays.ts](../src/system/weekdays.ts), [weekday-buttons.ts](../src/ui/weekday-buttons.ts)

- The schedule card lists the charge, discharge and EV charger slots, each with its times, power, days and whether the slot is on. The Slot kinds option chooses which kinds are shown.
- With Show week timeline on, the default, a week timeline draws every slot as a bar. Tapping a bar opens the slot.
- An open slot has an editor for its start, end, power, days and the slot's other settings.
- A slot is drawn only when every entity of the slot is enabled, and the schedule card counts the slots left out.
- When charge or discharge slots are shown and the application mode is not a time-of-use mode, a notice says the slots only run in time-of-use mode, with the mode list beside it.
- While control is not allowed for the system, every control on the schedule card is disabled and a lock links to the integration's settings.

## Weekdays tile card feature

The weekdays feature puts seven day buttons on a tile card for a slot's days.

Files: [weekdays-feature.ts](../src/features/weekdays-feature.ts), [weekday-buttons.ts](../src/ui/weekday-buttons.ts), [weekdays.ts](../src/system/weekdays.ts)

- The weekdays feature is offered only for a tile card whose entity is a slot's days entity.
- Seven named day buttons start on your first day of the week, taken from Home Assistant's settings or your language.
- The change is sent 1.5 seconds after the last press, so several days can be picked in one change.
- The buttons are disabled while control is not allowed for the system.

## Status badge

The status badge shows a system's state in the dashboard's badge row.

Files: [status-badge.ts](../src/badges/status-badge.ts)

- The status badge shows the operating state, coloured by how healthy the state is, and the number of pieces of equipment with an active fault.
- The status badge says when the system is not answering.
- Tapping the status badge opens the details of the operating state.

## Theme and language

The elements look and read like the rest of Home Assistant.

Files: [styles.ts](../src/ui/styles.ts), [localize.ts](../src/i18n/localize.ts), [en.json](../src/i18n/en.json)

- The elements follow the Home Assistant theme.
- Entity names, values and states use Home Assistant's own formatting and language.
- The cards' own texts exist in English only, and a dashboard in another language shows them in English.
