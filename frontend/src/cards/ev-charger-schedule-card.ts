import { registerCard } from "../registration";
import type { SlotKind } from "../system/schedule";
import { SajScheduleCard } from "./schedule-card";

export const EV_CHARGER_SCHEDULE_CARD_TAG =
    "saj-local-ev-charger-schedule-card";

export class SajEvChargerScheduleCard extends SajScheduleCard {
    protected override readonly kind: SlotKind = "ev_charger";
}

customElements.define(EV_CHARGER_SCHEDULE_CARD_TAG, SajEvChargerScheduleCard);

registerCard({
    type: EV_CHARGER_SCHEDULE_CARD_TAG,
    nameKey: "ev_charger_schedule_card_name",
    descriptionKey: "ev_charger_schedule_card_description",
    preview: true,
});

declare global {
    interface HTMLElementTagNameMap {
        [EV_CHARGER_SCHEDULE_CARD_TAG]: SajEvChargerScheduleCard;
    }
}
