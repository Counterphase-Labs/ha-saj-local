import { html, type TemplateResult } from "lit";

import type { Hass, SajElementConfig } from "../hass";
import { registerCardFeature, type CardFeatureContext } from "../registration";
import {
    ControlTracker,
    controlLock,
    setNumberRequest,
} from "../system/control";
import {
    isUnavailable,
    numericValue,
    ownerOfEntity,
    systemEntities,
} from "../system/entities";
import { SystemElement } from "../ui/system-element";
import "../ui/weekday-buttons";
import { entityLabel } from "../cards/entity-controls";

export const WEEKDAYS_FEATURE_TAG = "saj-local-weekdays";

const NUMBER_DOMAIN_PREFIX = "number.";
const WEEKDAYS_KEY_SUFFIX = "_days";

export const supportsWeekdays = ({
    hass,
    context,
}: {
    hass: Hass;
    context: CardFeatureContext;
}): boolean => {
    const entityId = context.entity_id ?? "";
    return (
        entityId.startsWith(NUMBER_DOMAIN_PREFIX) &&
        (ownerOfEntity({ hass, entityId })?.key.endsWith(WEEKDAYS_KEY_SUFFIX) ??
            false)
    );
};

export class SajWeekdaysFeature extends SystemElement {
    static override properties = {
        ...SystemElement.properties,
        context: { attribute: false },
        config: { attribute: false },
    };

    static getStubConfig(): SajElementConfig {
        return { type: `custom:${WEEKDAYS_FEATURE_TAG}` };
    }

    declare context: CardFeatureContext | undefined;
    declare config: SajElementConfig | undefined;

    protected readonly tracker = new ControlTracker(this, () => this.hass);

    setConfig(config: SajElementConfig): void {
        this.config = config;
    }

    protected override watchedDeviceId(): string | undefined {
        const { hass, context } = this;
        const entityId = context?.entity_id;
        return hass === undefined || entityId === undefined
            ? undefined
            : ownerOfEntity({ hass, entityId })?.deviceId;
    }

    protected override render(): TemplateResult {
        const { hass, context } = this;
        const entityId = context?.entity_id;
        if (hass === undefined || entityId === undefined) {
            return html``;
        }
        const owner = ownerOfEntity({ hass, entityId });
        if (owner === null) {
            return html``;
        }
        const entities = systemEntities({ hass, deviceId: owner.deviceId });
        const entity = entities.get(owner.key);
        if (entity === undefined) {
            return html``;
        }
        return html`<div
            @click=${(event: Event) => {
                event.stopPropagation();
            }}
        >
            <saj-weekday-buttons
                .hass=${hass}
                .label=${entityLabel({ hass, entity })}
                .labelHidden=${true}
                .value=${numericValue(entity) ?? 0}
                .disabled=${
                    controlLock(entities).locked || isUnavailable(entity)
                }
                .busy=${this.tracker.isBusy(entityId)}
                .error=${this.tracker.errorOf(entityId) ?? ""}
                @saj-commit=${(event: CustomEvent<number>) => {
                    void this.tracker.submit({
                        entityId,
                        request: setNumberRequest(event.detail),
                    });
                }}
            ></saj-weekday-buttons>
        </div>`;
    }
}

customElements.define(WEEKDAYS_FEATURE_TAG, SajWeekdaysFeature);

registerCardFeature({
    type: WEEKDAYS_FEATURE_TAG,
    nameKey: "weekdays_feature_name",
    isSupported: (hass, context) => supportsWeekdays({ hass, context }),
    configurable: false,
});

declare global {
    interface HTMLElementTagNameMap {
        [WEEKDAYS_FEATURE_TAG]: SajWeekdaysFeature;
    }
}
