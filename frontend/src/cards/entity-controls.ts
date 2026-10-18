import { html, type TemplateResult } from "lit";

import type { Hass, HassEntityNameItem } from "../hass";
import {
    selectOptionRequest,
    setNumberRequest,
    setSwitchRequest,
    setTimeRequest,
    pressButtonRequest,
    type ControlLock,
    type ControlTracker,
    type ServiceRequest,
} from "../system/control";
import {
    isUnavailable,
    numericValue,
    type SystemEntity,
} from "../system/entities";
import "../ui/number-control";
import "../ui/press-control";
import "../ui/select-control";
import "../ui/switch";
import "../ui/time-control";
import "../ui/value-row";

const ENTITY_NAME: readonly HassEntityNameItem[] = [{ type: "entity" }];

export interface ControlContext {
    hass: Hass;
    lock: ControlLock;
    tracker: ControlTracker;
}

export const entityLabel = ({
    hass,
    entity,
}: {
    hass: Hass;
    entity: SystemEntity;
}): string => hass.formatEntityName(entity.state, ENTITY_NAME);

export const renderEntityControl = ({
    context,
    entity,
    labelHidden = false,
}: {
    context: ControlContext;
    entity: SystemEntity;
    labelHidden?: boolean;
}): TemplateResult => {
    const { hass, lock, tracker } = context;
    const { attributes } = entity.state;
    const label = entityLabel({ hass, entity });
    const disabled = lock.locked || isUnavailable(entity);
    const busy = tracker.isBusy(entity.entityId);
    const error = tracker.errorOf(entity.entityId) ?? "";
    const submit = (request: ServiceRequest): void => {
        void tracker.submit({ entityId: entity.entityId, request });
    };

    switch (entity.domain) {
        case "number":
            return html`<saj-number-control
                .hass=${hass}
                .label=${label}
                .labelHidden=${labelHidden}
                .disabled=${disabled}
                .busy=${busy}
                .error=${error}
                .value=${numericValue(entity) ?? 0}
                .min=${attributes.min}
                .max=${attributes.max}
                .step=${attributes.step}
                .unit=${attributes.unit_of_measurement ?? ""}
                .mode=${attributes.mode ?? "auto"}
                .displayValue=${hass.formatEntityState(entity.state)}
                @saj-commit=${(event: CustomEvent<number>) => {
                    submit(setNumberRequest(event.detail));
                }}
            ></saj-number-control>`;
        case "select":
            return html`<saj-select-control
                .hass=${hass}
                .label=${label}
                .labelHidden=${labelHidden}
                .disabled=${disabled}
                .busy=${busy}
                .error=${error}
                .value=${entity.state.state}
                .options=${(
                    (attributes.options as string[] | undefined) ?? []
                ).map((option) => ({
                    value: option,
                    label: hass.formatEntityState(entity.state, option),
                }))}
                @saj-commit=${(event: CustomEvent<string>) => {
                    submit(selectOptionRequest(event.detail));
                }}
            ></saj-select-control>`;
        case "switch":
            return html`<saj-switch
                .hass=${hass}
                .label=${label}
                .labelHidden=${labelHidden}
                .disabled=${disabled}
                .busy=${busy}
                .error=${error}
                .checked=${entity.state.state === "on"}
                @saj-commit=${(event: CustomEvent<boolean>) => {
                    submit(setSwitchRequest(event.detail));
                }}
            ></saj-switch>`;
        case "time":
            return html`<saj-time-control
                .hass=${hass}
                .label=${label}
                .labelHidden=${labelHidden}
                .disabled=${disabled}
                .busy=${busy}
                .error=${error}
                .value=${entity.state.state}
                @saj-commit=${(event: CustomEvent<string>) => {
                    submit(setTimeRequest(event.detail));
                }}
            ></saj-time-control>`;
        case "button":
            return html`<saj-press-control
                .hass=${hass}
                .label=${label}
                .labelHidden=${labelHidden}
                .disabled=${disabled}
                .busy=${busy}
                .error=${error}
                @saj-commit=${() => {
                    submit(pressButtonRequest());
                }}
            ></saj-press-control>`;
        default:
            return html`<saj-value-row
                .label=${label}
                .value=${hass.formatEntityState(entity.state)}
                .entityId=${entity.entityId}
            ></saj-value-row>`;
    }
};
