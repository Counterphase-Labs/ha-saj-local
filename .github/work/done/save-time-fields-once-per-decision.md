# Save Time Fields Once Per Decision

## Plan Metadata

- **Revision:** 1
- **Status:** Approved
- **Last revised:** 2026-11-17
- **Requirements:** `.github/work/requirements.md` (Compatibility, Releases, Language, Testing), `frontend/docs/requirements.md` (Elements and setup)
- **Code style:** `../code-style.md`
- **Builds on:** [Add Lovelace Cards](../done/add-lovelace-cards-and-system-dashboard.md), [Split Schedule Card By Slot Kind](../done/split-schedule-card-by-slot-kind.md)

| Revision | Change |
| --- | --- |
| 1 | A time field saves when the user leaves the field, and a pending change of the weekday buttons is saved when the buttons are removed. |

## Goal

A user changes the hours and the minutes of a time field in one open of the time picker, and the card saves the time once. The picker stays open while the user turns the hour wheel and the minute wheel. The desktop and the phone save at the same moment.

## Current behaviour

- The time field sends the time to the inverter on each `change` event of the native time input. On a phone, the picker sends a change each time a wheel stops. On the desktop, the browser sends a change for each hour or minute field.
- Each save disables the time field until Home Assistant answers. On a phone, the disabled field closes the picker. Thus a change of the start and the end of one slot needs four opens and four saves.
- After each change, the time field puts the old time back into the input until the new state arrives. On a phone, the wheel can move back to the old time while the picker is open.
- The weekday buttons drop a pending change when the buttons are removed, for example when the user closes the slot less than 1.5 seconds after the last press.
- The number field, the slider, the list, the switch and the button already save once for each decision. A list saves one choice for each open, which is one decision.

## Scope

In scope:

- The time field, everywhere the cards show it. Today only the slot editor of the three schedule cards shows time fields.
- The weekday buttons, in the slot editor and in the weekdays tile card feature.
- The cards feature list and the cards user guide in all nine languages.

Out of scope: the integration, the number field, the slider, the list, the switch, the button, and the time that a save takes in the integration.

## Settled Decisions

- A time field keeps the chosen time as a draft and shows the draft in the input until the save. Reason: the picker must keep the time that the user turns to.
- A time field saves the draft once: on Enter, when the field loses focus, or when the field is removed from the page. Reason: the same rule as the number field, and the picker closes before the save starts.
- A time field does not save when the draft is the same as the time of the entity. Reason: an open and close of the picker with no change must not write to the inverter.
- A time field ignores an empty draft and keeps the time of the entity, as today. Reason: an empty time is not a valid value.
- A time field stays disabled while the save of its own entity runs, and then shows the time of the entity. Reason: the save starts after the picker closed, and the original cards plan shows the value that the inverter holds, not an optimistic value.
- The time field of another entity stays usable while one save runs, as today. Reason: busy state is kept for each entity.
- The weekday buttons save a pending change at once when the buttons are removed from the page, in place of dropping the change. Reason: the user made the decision, and a slot that closes must not lose the decision.
- No new helper for the time field. The time field uses the same draft and save rules as the number field. Reason: no new abstraction is necessary.

## Work

1. **Time field draft and save.** The time field keeps a draft, shows the draft, and saves once on Enter, on loss of focus or on removal, with no save for an empty draft or a draft equal to the entity time. Outcome: unit tests prove each rule in Settled Decisions for the time field, and that a series of change events before the loss of focus gives one save with the last time.
2. **Weekday buttons on removal.** The weekday buttons save a pending change when the buttons are removed. Outcome: a unit test proves that removal with a pending change gives one save, and that removal with no pending change gives no save.
3. **Feature list and user guide.** The Controls card section of `frontend/docs/features.md` says that a time field changes the inverter on Enter or on leaving the field. The Weekdays tile card feature section says that a pending change is also sent when the buttons close. The "One change per decision" bullet of `user/cards/README.md` gives the same time field rule in each of the nine languages (`en-gb`, `de`, `nl`, `fr`, `zh-hans`, `es`, `it`, `pl`, `sv`). Outcome: no page says that a time field changes the inverter on change, and `make docs-check` passes.

## Errors and failure behaviour

- A refused save shows the message of the integration under the time field, as today, and the field shows the time of the entity again.
- When the entity time changes from a different source while a draft exists, the draft stays until the user leaves the field. The save then sends the draft.
- When a phone puts the app in the background with the focus still in a time field, the draft stays unsaved until the field loses focus or the page removes the field. A page that the phone closes without a removal loses the draft.
- While Allow control is off, the time field is disabled and holds no draft, as today.

## Compatibility

The cards are at the first beta (`1.0.0b1`). The change alters only when a time field and the weekday buttons send a change. No card type, card setting, entity or stored setting changes, so no installation, dashboard or automation breaks (Compatibility in `.github/work/requirements.md`). The release notes of the next beta name the changed save rule of the time field (Releases in `.github/work/requirements.md`).

## Tests and verification

- Unit tests for the time field and the weekday buttons, as listed in Work. The tests of the time field that expect a save on each change event change to the new rules.
- The existing tests of the schedule cards and of the weekdays tile card feature pass with no change of their expectations.
- `make ci` passes, with the 100 % coverage gate.
- A check on a phone in the Home Assistant app, on iOS and on Android: in an open slot, a change of the start hour and the start minute in one open of the picker gives one save, and the picker stays open until the user closes the picker. The same check is done for a list in the slot editor.
- A check in a desktop browser: a change of the hours and the minutes of a time field gives one save when the user leaves the field.

## Dependencies and risks

- The unit tests and the browser tests run in a desktop browser and cannot open a native phone picker. Only the phone check proves the behaviour on a phone.
- The moment when a phone browser takes the focus away from a time input after the picker closes is not proven. If a phone keeps the focus after the picker closes, the save occurs when the user taps a different part of the page.
- The behaviour of a list on a phone is not proven. If the phone check shows that a list closes or saves before the user is done, the fix of the list is added to this plan as an amendment.

## Open questions

None.
