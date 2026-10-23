# Dashboard cards

The Dashboard cards page explains how to add the SAJ Local cards to a dashboard and choose a system, and lists what each element shows. The full lists are in the [Elements and setup](../../../../frontend/docs/features.md#elements-and-setup) and [Theme and language](../../../../frontend/docs/features.md#theme-and-language) sections of the cards feature list, and in the [Cards](../../../../custom_components/saj_local/docs/features.md#cards) section of the integration feature list.

SAJ Local serves the cards and registers the cards with Home Assistant when Home Assistant starts. The cards appear in the card picker, so there is no resource to add and no cache to clear.

## Elements

| Element | What the element shows |
| --- | --- |
| [Power flow card](power-flow-card.md) | Live power between solar, battery, grid, home and the optional equipment. |
| [Status card](status-card.md) | The operating state, the application mode, key readings, today's energy, a fault summary and whether control is allowed. |
| [Faults card](faults-card.md) | The active faults of each piece of equipment, and a Clear fault button. |
| [Battery card](battery-card.md) | The state of charge with the limits marked, the battery readings and one row group for each pack. |
| [Controls card](controls-card.md) | The settings of the system in sections. |
| [Schedule card](schedule-card.md) | The charge, discharge and EV charger slots, a week timeline and a slot editor. |
| [Weekdays tile card feature](weekdays-feature.md) | Seven day buttons on a tile card, for the days of a slot. |
| [Status badge](status-badge.md) | A badge with the operating state and the number of pieces of equipment with an active fault. |

## Add an element

1. Edit a dashboard and choose Add card. For the weekdays feature, add a tile card and open the features of the tile card. For the badge, edit the badges of the dashboard.
2. Pick the SAJ Local element in the picker. The six cards show a live preview.
3. Choose the system in the System field of the visual editor. A new card or badge starts with the first system. The weekdays feature has no editor, because the feature uses the entity of the tile card.

A home with two systems adds a card once per system. A card's title is the device name of the system followed by the model, for example SAJ HS3 (12000 W). SAJ Local adds the serial number only when two systems would otherwise have an identical title. Rename each device in Home Assistant if you want other titles.

The elements find the entities of a system through the entity registry, and not by entity ID, so the elements keep working when you change a [prefix](../entities-and-prefix.md#the-prefix).

## What every element does

- **Only what the system has.** A part whose entity does not exist or is disabled is not drawn, so each card shows only what the system has. A part for one model appears only on that model, and each element page names the parts.
- **An empty card says why.** A card with none of the entities of the card enabled says which kind of entity to enable, with a link to the device page of the system.
- **A system that does not answer.** A card says so and dims the values.
- **Tap a value.** Tapping a value opens the details of the entity in Home Assistant.
- **Locked controls.** While [Allow control](../changing-settings.md#allow-control) is off for the system, every control is disabled and a lock links to the settings of the integration. Switching Allow control on also enables the entities that the cards need, see [the control set](../changing-settings.md#the-control-set).
- **One change per decision.** A slider changes the inverter when you release the slider. A number field changes the inverter on Enter or when you leave the field. A list, a switch or a time field changes the inverter on change. The control then shows the value that the inverter holds, and a refusal appears under the control in the words of the integration.

## Theme and language

The elements follow the Home Assistant theme. Entity names, values and states use the formatting and the language of Home Assistant. The texts of the cards exist in English only, so a dashboard in another language shows the texts of the cards in English.

## Not supported yet

- Card texts in languages other than English.
