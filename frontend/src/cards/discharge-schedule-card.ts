import { registerCard } from "../registration";
import type { SlotKind } from "../system/schedule";
import { SajScheduleCard } from "./schedule-card";

export const DISCHARGE_SCHEDULE_CARD_TAG = "saj-local-discharge-schedule-card";

export class SajDischargeScheduleCard extends SajScheduleCard {
    protected override readonly kind: SlotKind = "discharge";
}

customElements.define(DISCHARGE_SCHEDULE_CARD_TAG, SajDischargeScheduleCard);

registerCard({
    type: DISCHARGE_SCHEDULE_CARD_TAG,
    nameKey: "discharge_schedule_card_name",
    descriptionKey: "discharge_schedule_card_description",
    preview: true,
});

declare global {
    interface HTMLElementTagNameMap {
        [DISCHARGE_SCHEDULE_CARD_TAG]: SajDischargeScheduleCard;
    }
}
