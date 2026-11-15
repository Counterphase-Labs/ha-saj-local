# Split Schedule Card By Slot Kind

## Plan Metadata

- **Revision:** 3
- **Status:** Approved
- **Last revised:** 2026-11-15
- **Requirements:** `.github/work/requirements.md` (Compatibility, Releases, Language, Testing), `frontend/docs/requirements.md` (Elements and setup)
- **Code style:** `../code-style.md`
- **Builds on:** [Add Lovelace Cards](../done/add-lovelace-cards-and-system-dashboard.md)

| Revision | Change |
| --- | --- |
| 1 | One schedule card, with a colour for each slot and a hatch on overlaps. |
| 2 | Three schedule cards, one for each slot kind, replace the schedule card. |
| 3 | A switched-off slot is an outline, and only switched-on slots make an overlap. |

## Goal

Three cards replace the schedule card: a charge schedule card, a discharge schedule card and an EV charger schedule card. Each card shows the slots of one kind, with a week timeline where each slot has its own colour. A switched-off slot shows as an outline in its colour. Where the times of two or more switched-on slots overlap on one day, the overlap shows a hatch pattern made of the colours of the overlapping slots.

## Current behaviour

- One schedule card shows the charge, discharge and EV charger slots. The Slot kinds option chooses which kinds the card shows.
- One week timeline draws the slots of all shown kinds together, above the slot list.
- Each bar has the colour of its slot kind. Thus two charge slots on one day look the same.
- Overlapping bars are drawn on top of each other. The bar drawn last hides the overlap.
- A slot that is switched off is drawn with diagonal stripes of the slot colour and transparent gaps.
- A slot row in the list shows no colour.

## Scope

In scope:

- The three new card types, and the removal of the schedule card type and its Slot kinds option.
- A colour for each slot number, a colour mark on each slot row, an outline for each switched-off slot, and a hatch on each overlap of switched-on slots.
- The card names and descriptions of the three cards in all nine languages.
- The development showcase dashboards, the cards feature list, the user pages and the developer documentation page in all nine languages, and the screenshots.

Out of scope: any change to the slot editor, to the content of a slot row or to the integration.

## Settled Decisions

### Card types

- The three card types are `saj-local-charge-schedule-card`, `saj-local-discharge-schedule-card` and `saj-local-ev-charger-schedule-card`, named Charge schedule, Discharge schedule and EV charger schedule. Reason: the names follow the slot kind names that the cards already show.
- The schedule card type `saj-local-schedule-card` is removed with no replacement alias. Reason: the removal is an approved breaking change, which adds no backwards compatibility layer (Compatibility in `.github/work/requirements.md`).
- Each new card has the System option and the Show week timeline option, with the defaults of today. The Slot kinds option does not exist on the new cards. Reason: each card shows one kind.
- The three cards share one implementation, and each card type fixes the kind. Reason: the three cards differ only in the kind.
- Each card shows a live preview in the card picker, like the schedule card today. Reason: the other cards have a preview.
- Each card title is the system title, like every other card, and a heading with the kind name is below the title. Reason: the title rule is the same for all cards, and the heading tells the three cards apart.
- A card for a kind that the system does not have, for example the EV charger schedule card on an H2, shows the empty state of today, which says which kind of entity to enable. Reason: the card shows only what its system has (Elements and setup in `frontend/docs/requirements.md`).
- The charge schedule card and the discharge schedule card show the time-of-use notice under the same condition as today. The EV charger schedule card does not show the notice. Reason: the notice concerns only charge and discharge slots, as today.
- The size that each card reports to the dashboard counts its title, its slot rows and its timeline. Reason: the dashboard must give the card enough space.

### Colours and overlaps

- The cards use one fixed palette of seven colours, one for each slot number. The same slot number has the same colour on each of the three cards. Reason: each kind has seven slots, so seven colours make each slot on a timeline different.

  | Slot | Colour | Contrast on the light track | Contrast on the dark track |
  | --- | --- | --- | --- |
  | 1 | Blue `#307ce8` | 3.07:1 | 3.07:1 |
  | 2 | Red `#f42828` | 3.07:1 | 3.07:1 |
  | 3 | Green `#1a9224` | 3.07:1 | 3.07:1 |
  | 4 | Orange `#b76c20` | 3.07:1 | 3.07:1 |
  | 5 | Purple `#b153e1` | 3.06:1 | 3.08:1 |
  | 6 | Teal `#198c8c` | 3.08:1 | 3.07:1 |
  | 7 | Pink `#f21182` | 3.07:1 | 3.07:1 |

- The track is the divider colour of the theme on the card background. In the default themes of Home Assistant 2026.9.3, the light track is `#e0e0e0` (divider `#0000001f` on card `#fff`) and the dark track is `#343434` (divider `#e1e1e11f` on card `#1c1c1c`). Each colour is at least 3:1 on both tracks, the minimum contrast for a graphic part. Reason: each bar must be easy to see in both default themes.
- Each slot always has the colour of its slot number, whatever the other slots do. Reason: a colour that does not change lets the user learn which colour is which slot.
- Each slot row shows a small round colour mark before the slot name, in the colour of the slot. Reason: the mark lets the reader match a bar to a slot without a tap.
- An overlap is a part of one day where the times of two or more bars cover the same minutes. Bars that only touch, where one ends at the minute the next starts, do not overlap. Reason: touching slots do not run at the same time.
- A switched-off slot is drawn as an outline: a 2-pixel border in the slot colour, with no fill. The switched-off stripes of today are removed. Reason: an outline cannot look like the overlap hatch, and the border stays easy to see on a short slot.
- Switched-on bars are drawn above outlines. Where a switched-off slot crosses a switched-on slot, the switched-on bar hides that part of the outline. Reason: the slot that runs is the important information.
- An overlap includes only the bars of switched-on slots. An EV charger slot has no switch and always counts as switched on. Reason: a switched-off slot does not run, so the slot does not make an overlap.
- The overlap hatch is diagonal stripes with no transparent gaps. The stripes repeat the colours of the overlapping slots, one stripe for each slot, in slot number order. Reason: the stripe colours name the slots.
- A tap on an overlap opens the overlapping slot with the lowest slot number. Assistive technology does not read the overlap hatch. Reason: one fixed rule makes the tap predictable, and the name of each bar already gives the slot.
- The overlap calculation is in the schedule module, next to the timeline bar calculation, and the card only draws the result. Reason: the schedule module holds the slot logic, and the logic gets unit tests without the card.
- A slot that crosses midnight gives two bars today. Each bar counts in overlaps on its own day. Reason: the overlap is a property of one day of the timeline.

### Documentation and showcase

- One user page, Schedule cards (`schedule-cards.md`), replaces the Schedule card user page (`schedule-card.md`) in each of the nine languages. The page has one section for each card. Reason: the three cards share their behaviour and their options.
- The table of elements in the cards user guide (`user/cards/README.md`) has one row for each new card, each linking to its section of the Schedule cards page, and the guide says that eight cards show a live preview. Reason: the guide lists every card.
- The screenshots are `cards-charge-schedule-card.png`, `cards-discharge-schedule-card.png` and `cards-ev-charger-schedule-card.png`, taken on an HS3, in each language. `cards-schedule-card.png` and `cards-schedule-card-h2.png` are deleted in each language. Reason: the HS3 has all three kinds, and the page states that the H2 has no EV charger slots.
- In each showcase dashboard, the three new cards take the place of the schedule card in every view: the Schedules section of the Dashboard view, each option combination in the Cards view, and the no-device and not-SAJ cases in the Empty states view. The H2 showcase leaves the EV charger schedule card out of the Dashboard view, and the Cards view of the H2 shows the card with its empty state. Reason: the showcase writes out every element with every option, as the cards plan this plan builds on decided.

## Work

1. **Overlap calculation.** The schedule module gives, for each day, each overlap part with its start minute, end minute and the slots that cover the part. Outcome: unit tests prove two-slot, three-slot, touching, no-overlap and midnight-crossing cases, that a switched-off slot is in no overlap part, and that an EV charger slot counts as switched on.
2. **Three card types.** The three cards replace the schedule card, with the options, title, heading, preview, empty state, notice and size above. The card names and descriptions exist in all nine languages, and the texts of the schedule card and of the Slot kinds option are removed. Outcome: unit tests prove each decision in the Card types section, and the schedule card type is no longer registered.
3. **Slot colours, outlines and colour marks.** Each card draws each switched-on bar, each switched-off outline and the colour mark of each slot in the colour of its slot number, with switched-on bars above outlines. Outcome: unit tests prove that slots 1 to 7 get seven different colours, the same colour for the same slot number on each card, no change of colour when other slots change, and an outline for a switched-off slot.
4. **Overlap hatch.** Each card draws the overlap hatch above its bars. Outcome: unit tests prove the overlap parts with their slot colours, and that a tap on an overlap opens the overlapping slot with the lowest slot number.
5. **Showcase dashboards and browser tests.** `config/dashboards/saj-hs3.yaml`, `config/dashboards/saj-h2.yaml` and the controlled browser tests use the new card types, as the Documentation and showcase decisions state. Outcome: neither dashboard names `saj-local-schedule-card`, and the browser tests pass.
6. **Feature list and documentation.** The cards feature list states eight cards in the card picker and has one Schedule cards section in place of the Schedule card section. In each of the nine languages (`en-gb`, `de`, `nl`, `fr`, `zh-hans`, `es`, `it`, `pl`, `sv`), these pages change:
   - the Schedule cards page replaces the Schedule card page;
   - the cards user guide (`user/cards/README.md`) and the weekdays feature page (`user/cards/weekdays-feature.md`) link to the Schedule cards page;
   - the page table of `developer/documentation.md` names the Schedule cards page.

   The Schedule cards page and the feature list state that a switched-off slot is an outline and that only switched-on slots make an overlap. Outcome: no page names the schedule card type, the Slot kinds option or `schedule-card.md`, no page describes switched-off stripes, and `make docs-check` passes.
7. **Screenshots.** The documentation screenshot test takes the three new screenshots, and `make docs-images` makes the screenshots in all nine languages. The two old screenshots are deleted in each language. Outcome: 27 new screenshots show the slot colours, the colour marks, a switched-off outline and an overlap hatch, and no `cards-schedule-card` screenshot is left.

## Errors and failure behaviour

- A slot with a start or end that the card cannot read has no bars today. That slot has no part in an overlap, but its colour mark keeps the colour of its slot number.
- A slot that is unavailable keeps the behaviour of today. The card dims the slot with the rest of the body.
- A dashboard that still uses `saj-local-schedule-card` shows the error card that Home Assistant shows for an unknown card type.

## Compatibility

The removal of the schedule card type and of its Slot kinds option is a breaking change, approved as an exception for this change alone (Compatibility in `.github/work/requirements.md`). No alias or conversion of the old card exists. The release notes of the next beta must name the removed card type, the removed option and the three new card types (Releases in `.github/work/requirements.md`). `make freeze-check` passes, because no stable release tag exists yet.

## Tests and verification

- Unit tests for the overlap calculation, the three card types, the slot colours and the overlap hatch, as listed in Work. The tests prove behaviour, not the palette values.
- The unit tests of the schedule card change to test the three new cards.
- The controlled browser tests pass with the new card types.
- `make ci` passes, with the 100 % coverage gate.
- A look at the new screenshots in English shows a distinct colour for each slot on a timeline, a colour mark that matches each slot, an outline for a switched-off slot, and an overlap hatch only where switched-on slots overlap.

## Dependencies and risks

- Every user dashboard with the schedule card breaks until the user adds the new cards. The beta release notes are the only notice.
- The palette is fixed and does not change with a custom theme. A custom theme with a different divider or card colour can give less contrast than the default themes.
- The schedule data in the documentation environment can have no overlapping slots. Then the screenshots do not show the overlap hatch, and the unit tests alone prove the overlap hatch.

## Open questions

None.
