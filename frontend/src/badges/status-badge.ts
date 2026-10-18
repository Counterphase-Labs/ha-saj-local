import { css, html, nothing, type TemplateResult } from "lit";
import { styleMap } from "lit/directives/style-map.js";

import { fireMoreInfo } from "../actions";
import type { Hass, SajElementConfig } from "../hass";
import { configForm } from "../cards/editor";
import { registerBadge } from "../registration";
import {
    allUnavailable,
    listSystemDevices,
    systemEntities,
} from "../system/entities";
import { activeFaultSummaries, FAULT_GROUPS } from "../system/faults";
import { operatingTone } from "../system/operating";
import "../ui/icon";
import { SystemElement } from "../ui/system-element";
import { baseStyles, toneColour } from "../ui/styles";

const BADGE_ELEMENT = "saj-local-status-badge";
const BADGE_TYPE = `custom:${BADGE_ELEMENT}`;

const OPERATING_MODE_KEY = "operating_mode";

export class SajStatusBadge extends SystemElement {
    static override properties = {
        ...SystemElement.properties,
        config: { attribute: false },
    };

    static override styles = [
        baseStyles,
        css`
            :host {
                display: inline-block;
            }
            .badge {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                box-sizing: border-box;
                height: var(--ha-badge-size, 36px);
                padding: 0 12px;
                background: var(
                    --ha-card-background,
                    var(--card-background-color, #fff)
                );
                border-width: var(--ha-card-border-width, 1px);
                border-style: solid;
                border-color: var(
                    --ha-card-border-color,
                    var(--divider-color, #e0e0e0)
                );
                border-radius: var(--ha-badge-border-radius, 18px);
                box-shadow: var(--ha-card-box-shadow, none);
                font-size: 0.9rem;
            }
            button.badge {
                cursor: pointer;
            }
            .dimmed {
                opacity: 0.5;
            }
        `,
    ];

    static getConfigForm(): ReturnType<typeof configForm> {
        return configForm(() => []);
    }

    static getStubConfig(
        hass: Pick<Hass, "entities" | "devices">,
    ): SajElementConfig {
        return { type: BADGE_TYPE, device: listSystemDevices(hass)[0]?.id };
    }

    declare config: SajElementConfig | undefined;

    setConfig(config: SajElementConfig): void {
        this.config = config;
    }

    protected override watchedDeviceId(): string | undefined {
        return this.config?.device;
    }

    protected override render(): TemplateResult {
        const { hass, config, text } = this;
        const entities =
            hass === undefined || config?.device === undefined
                ? undefined
                : systemEntities({ hass, deviceId: config.device });
        if (
            hass === undefined ||
            entities === undefined ||
            entities.size === 0
        ) {
            return html`<div class="badge dimmed">
                ${text("choose_system")}
            </div>`;
        }
        const mode = entities.get(OPERATING_MODE_KEY);
        const shown = [
            mode,
            ...FAULT_GROUPS.map((group) => entities.get(group.summaryKey)),
        ].filter((entity) => entity !== undefined);
        const answering = !allUnavailable(shown);
        const faultCount = activeFaultSummaries(entities).length;
        const stateText = answering
            ? mode === undefined
                ? ""
                : hass.formatEntityState(mode.state)
            : text("not_answering");
        const content = html`<saj-icon name="inverter"></saj-icon>
            <span
                class="state"
                style=${styleMap({
                    color: toneColour(operatingTone(mode?.state.state)),
                })}
                >${stateText}</span
            >
            ${
                answering && faultCount > 0
                    ? html`<span
                          class="faults"
                          style=${styleMap({ color: toneColour("error") })}
                          >${text("faults_count", { count: faultCount })}</span
                      >`
                    : nothing
            }`;
        return mode === undefined
            ? html`<div class="badge">${content}</div>`
            : html`<button
                  type="button"
                  class=${answering ? "badge" : "badge dimmed"}
                  @click=${() => {
                      fireMoreInfo({ host: this, entityId: mode.entityId });
                  }}
              >
                  ${content}
              </button>`;
    }
}

customElements.define(BADGE_ELEMENT, SajStatusBadge);

registerBadge({
    type: BADGE_ELEMENT,
    nameKey: "badge_name",
    descriptionKey: "badge_description",
});

declare global {
    interface HTMLElementTagNameMap {
        "saj-local-status-badge": SajStatusBadge;
    }
}
