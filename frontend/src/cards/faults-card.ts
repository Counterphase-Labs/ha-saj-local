import { css, html, nothing, type TemplateResult } from "lit";

import type { Hass, SajElementConfig } from "../hass";
import { relativeTimeText } from "../i18n/localize";
import { registerCard } from "../registration";
import { pressButtonRequest } from "../system/control";
import type { SystemEntities, SystemEntity } from "../system/entities";
import {
    faultGroups,
    type FaultGroup,
    type FaultGroupId,
    type FaultRow,
} from "../system/faults";
import { controlStyles } from "../ui/control-element";
import { booleanField, configForm, stubConfig } from "./editor";
import { SystemCard, type CardContext } from "./system-card";

export const FAULTS_CARD_TYPE = "saj-local-faults-card";
const FAULTS_CARD_ROWS = 4;
const SHOW_CLEAR_GROUPS = true;
const CLEAR_FAULT_KEY = "clear_current_fault";

const GROUP_LABEL_KEYS: Readonly<Record<FaultGroupId, string>> = {
    inverter: "inverter",
    battery: "battery",
    ev: "ev_charger",
};

export interface FaultsCardConfig extends SajElementConfig {
    show_clear_groups?: boolean;
}

export class SajLocalFaultsCard extends SystemCard<FaultsCardConfig> {
    static override styles = [
        ...controlStyles,
        css`
            h3 {
                margin: 8px 0 0;
                font-size: 1rem;
                font-weight: 500;
            }
            .hint {
                color: var(--secondary-text-color, #727272);
                font-size: 0.85rem;
            }
            .clear {
                padding: 6px 12px;
                background: none;
                border: 1px solid var(--divider-color, #e0e0e0);
                border-radius: 8px;
                cursor: pointer;
            }
            .clear:disabled {
                opacity: 0.5;
                cursor: default;
            }
        `,
    ];

    static getConfigForm(): ReturnType<typeof configForm> {
        return configForm(() => [
            booleanField({
                name: "show_clear_groups",
                fallback: SHOW_CLEAR_GROUPS,
            }),
        ]);
    }

    static getStubConfig(
        hass: Pick<Hass, "entities" | "devices">,
    ): ReturnType<typeof stubConfig> {
        return stubConfig(hass);
    }

    protected readonly cardRows = FAULTS_CARD_ROWS;
    protected override readonly hasControls = true;

    protected override shownEntities(entities: SystemEntities): SystemEntity[] {
        return faultGroups(entities).map(({ summary }) => summary);
    }

    protected override renderBody(context: CardContext): TemplateResult {
        const showClear = this.config?.show_clear_groups ?? SHOW_CLEAR_GROUPS;
        const groups = faultGroups(context.entities).filter(
            ({ active }) => active || showClear,
        );
        const hasClearAction = context.entities.has(CLEAR_FAULT_KEY);
        return html`${hasClearAction ? this.renderLockedBanner(context) : nothing}${groups.map(
            (group) => this.renderGroup({ context, group }),
        )}`;
    }

    private renderGroup({
        context,
        group,
    }: {
        context: CardContext;
        group: FaultGroup;
    }): TemplateResult {
        const label = this.text(GROUP_LABEL_KEYS[group.id]);
        if (!group.active) {
            return html`<saj-value-row
                .label=${label}
                .value=${this.text("no_active_faults")}
                .icon=${"ok"}
                .tone=${"success"}
                .entityId=${group.summary.entityId}
                .dimmed=${context.dimmed}
            ></saj-value-row>`;
        }
        return html`<h3>${label}</h3>
            ${group.rows.map((row) => this.renderRow({ context, row }))}
            ${group.id === "inverter" ? this.renderClear(context) : nothing}`;
    }

    private renderRow({
        context,
        row,
    }: {
        context: CardContext;
        row: FaultRow;
    }): TemplateResult {
        const since = relativeTimeText({
            from: row.since,
            now: new Date(),
            language: context.hass.language,
        });
        return html`${this.valueRow({
            context,
            entity: row.entity,
            icon: "fault",
            tone: "error",
            value: since,
        })}${
            row.unrecognised
                ? html`<div class="hint">${this.text("see_diagnostics")}</div>`
                : nothing
        }`;
    }

    private renderClear(context: CardContext): TemplateResult | typeof nothing {
        const button = context.entities.get(CLEAR_FAULT_KEY);
        if (button === undefined) {
            return nothing;
        }
        const busy = this.tracker.isBusy(button.entityId);
        const error = this.tracker.errorOf(button.entityId);
        return html`<div class="control">
                <button
                    type="button"
                    class="clear"
                    ?disabled=${context.lock.locked || busy}
                    @click=${() => {
                        void this.tracker.submit({
                            entityId: button.entityId,
                            request: pressButtonRequest(),
                        });
                    }}
                >
                    ${this.text("clear_fault")}
                </button>
                ${
                    busy
                        ? html`<saj-icon
                              class="busy"
                              name="busy"
                              role="status"
                              aria-label=${this.text("busy")}
                          ></saj-icon>`
                        : nothing
                }
            </div>
            ${
                error === null
                    ? nothing
                    : html`<div class="error" role="alert">${error}</div>`
            }`;
    }
}

customElements.define(FAULTS_CARD_TYPE, SajLocalFaultsCard);

registerCard({
    type: FAULTS_CARD_TYPE,
    nameKey: "faults_card_name",
    descriptionKey: "faults_card_description",
    preview: true,
});

declare global {
    interface HTMLElementTagNameMap {
        [FAULTS_CARD_TYPE]: SajLocalFaultsCard;
    }
}
