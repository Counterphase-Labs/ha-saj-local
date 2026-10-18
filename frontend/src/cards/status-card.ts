import { css, html, nothing, type TemplateResult } from "lit";

import type { Hass, SajElementConfig } from "../hass";
import { registerCard } from "../registration";
import {
    isOn,
    isUnavailable,
    type SystemEntities,
    type SystemEntity,
} from "../system/entities";
import { activeFaultSummaries, FAULT_GROUPS } from "../system/faults";
import { operatingTone } from "../system/operating";
import type { IconName } from "../ui/icons";
import { baseStyles } from "../ui/styles";
import { booleanField, configForm, stubConfig } from "./editor";
import { presentEntities, SystemCard, type CardContext } from "./system-card";

export const STATUS_CARD_TYPE = "saj-local-status-card";
const STATUS_CARD_ROWS = 5;
const SHOW_ENERGY = true;

export interface StatusCardConfig extends SajElementConfig {
    show_energy?: boolean;
}

interface ReadingKey {
    key: string;
    icon: IconName;
}

const READING_KEYS: readonly ReadingKey[] = [
    { key: "battery_soc", icon: "battery" },
    { key: "inverter_temperature", icon: "temperature" },
    { key: "battery_temperature", icon: "temperature" },
    { key: "off_grid_mode", icon: "grid" },
];

const TODAY_KEYS: readonly string[] = [
    "pv_energy_today",
    "load_energy_today",
    "grid_import_energy_today",
    "grid_export_energy_today",
    "battery_charge_energy_today",
    "battery_discharge_energy_today",
];

const OPERATING_MODE_KEY = "operating_mode";
const APPLICATION_MODE_KEY = "application_mode";
const APPLICATION_MODE_ACTIVE_KEY = "application_mode_active";
const CONTROL_ALLOWED_KEY = "control_allowed";

export class SajLocalStatusCard extends SystemCard<StatusCardConfig> {
    static override styles = [
        baseStyles,
        css`
            .section {
                padding: 4px 0;
            }
            .section + .section {
                border-top: 1px solid var(--divider-color, #e0e0e0);
            }
        `,
    ];

    static getConfigForm(): ReturnType<typeof configForm> {
        return configForm(() => [
            booleanField({ name: "show_energy", fallback: SHOW_ENERGY }),
        ]);
    }

    static getStubConfig(
        hass: Pick<Hass, "entities" | "devices">,
    ): ReturnType<typeof stubConfig> {
        return stubConfig(hass);
    }

    protected readonly cardRows = STATUS_CARD_ROWS;

    private get showEnergy(): boolean {
        return this.config?.show_energy ?? SHOW_ENERGY;
    }

    protected override shownEntities(entities: SystemEntities): SystemEntity[] {
        return presentEntities({
            entities,
            keys: [
                OPERATING_MODE_KEY,
                APPLICATION_MODE_KEY,
                APPLICATION_MODE_ACTIVE_KEY,
                ...READING_KEYS.map(({ key }) => key),
                ...(this.showEnergy ? TODAY_KEYS : []),
                ...FAULT_GROUPS.map(({ summaryKey }) => summaryKey),
                CONTROL_ALLOWED_KEY,
            ],
        });
    }

    protected override renderBody(context: CardContext): TemplateResult {
        return html`${this.section(this.renderState(context))}${this.section(
            this.renderMode(context),
        )}${this.section(this.renderReadings(context))}${this.section(
            this.showEnergy ? this.renderToday(context) : [],
        )}${this.section([
            ...this.renderFaults(context),
            ...this.renderChanges(context),
        ])}`;
    }

    private section(
        rows: readonly TemplateResult[],
    ): TemplateResult | typeof nothing {
        return rows.length === 0
            ? nothing
            : html`<div class="section">${rows}</div>`;
    }

    private renderState(context: CardContext): TemplateResult[] {
        const entity = context.entities.get(OPERATING_MODE_KEY);
        return entity === undefined
            ? []
            : [
                  this.valueRow({
                      context,
                      entity,
                      icon: "inverter",
                      tone: operatingTone(entity.state.state),
                  }),
              ];
    }

    private renderMode(context: CardContext): TemplateResult[] {
        const mode = context.entities.get(APPLICATION_MODE_KEY);
        if (mode === undefined) {
            return [];
        }
        const active = context.entities.get(APPLICATION_MODE_ACTIVE_KEY);
        return [
            this.valueRow({ context, entity: mode, icon: "settings" }),
            ...(active === undefined || active.state.state === mode.state.state
                ? []
                : [
                      this.valueRow({
                          context,
                          entity: active,
                          icon: "settings",
                          label: this.text("mode_running_now"),
                      }),
                  ]),
        ];
    }

    private renderReadings(context: CardContext): TemplateResult[] {
        return READING_KEYS.flatMap(({ key, icon }) => {
            const entity = context.entities.get(key);
            return entity === undefined
                ? []
                : [this.valueRow({ context, entity, icon })];
        });
    }

    private renderToday(context: CardContext): TemplateResult[] {
        return presentEntities({
            entities: context.entities,
            keys: TODAY_KEYS,
        }).map((entity) => this.valueRow({ context, entity, icon: "info" }));
    }

    private renderFaults(context: CardContext): TemplateResult[] {
        const summaries = presentEntities({
            entities: context.entities,
            keys: FAULT_GROUPS.map(({ summaryKey }) => summaryKey),
        });
        if (summaries.length === 0) {
            return [];
        }
        const active = activeFaultSummaries(context.entities);
        const [first] = active;
        const count = active.length;
        return [
            html`<saj-value-row
                .label=${this.text("faults")}
                .value=${
                    count === 0
                        ? this.text("no_faults")
                        : this.text("faults_count", { count })
                }
                .icon=${count === 0 ? "ok" : "fault"}
                .tone=${count === 0 ? undefined : "error"}
                .entityId=${first?.entityId}
                .dimmed=${context.dimmed}
            ></saj-value-row>`,
        ];
    }

    private renderChanges(context: CardContext): TemplateResult[] {
        const entity = context.entities.get(CONTROL_ALLOWED_KEY);
        if (entity === undefined) {
            return [];
        }
        const allowed = isOn(entity);
        return [
            this.valueRow({
                context,
                entity,
                icon: "lock",
                label: this.text("changes"),
                tone: allowed ? "success" : "warning",
                value: isUnavailable(entity)
                    ? this.text("unavailable")
                    : this.text(allowed ? "changes_allowed" : "changes_off"),
            }),
        ];
    }
}

customElements.define(STATUS_CARD_TYPE, SajLocalStatusCard);

registerCard({
    type: STATUS_CARD_TYPE,
    nameKey: "status_card_name",
    descriptionKey: "status_card_description",
    preview: true,
});

declare global {
    interface HTMLElementTagNameMap {
        [STATUS_CARD_TYPE]: SajLocalStatusCard;
    }
}
