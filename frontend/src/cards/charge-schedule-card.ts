import { registerCard } from "../registration";
import type { SlotKind } from "../system/schedule";
import { SajScheduleCard } from "./schedule-card";

export const CHARGE_SCHEDULE_CARD_TAG = "saj-local-charge-schedule-card";

export class SajChargeScheduleCard extends SajScheduleCard {
    protected override readonly kind: SlotKind = "charge";
}

customElements.define(CHARGE_SCHEDULE_CARD_TAG, SajChargeScheduleCard);

registerCard({
    type: CHARGE_SCHEDULE_CARD_TAG,
    nameKey: "charge_schedule_card_name",
    descriptionKey: "charge_schedule_card_description",
    preview: true,
});

declare global {
    interface HTMLElementTagNameMap {
        [CHARGE_SCHEDULE_CARD_TAG]: SajChargeScheduleCard;
    }
}
