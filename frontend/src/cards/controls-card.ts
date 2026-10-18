import { css, html, nothing, type TemplateResult } from "lit";

import type { Hass, SajElementConfig } from "../hass";
import { registerCard } from "../registration";
import {
    systemEntities,
    type SystemEntities,
    type SystemEntity,
} from "../system/entities";
import { multiSelectField, SystemCard, type CardContext } from "./system-card";
import { baseStyles } from "../ui/styles";
import { configForm, stubConfig } from "./editor";
import { renderEntityControl } from "./entity-controls";

export const CONTROLS_CARD_TAG = "saj-local-controls-card";

export const SECTION_IDS = [
    "mode",
    "battery",
    "grid",
    "power_control",
    "ev_charger",
    "device",
] as const;

export type SectionId = (typeof SECTION_IDS)[number];

type KeyedSectionId = Exclude<SectionId, "power_control">;

const SECTION_KEYS: Record<KeyedSectionId, readonly string[]> = {
    mode: [
        "application_mode",
        "time_of_use_idle_mode",
        "time_of_use_grid_discharge",
    ],
    battery: [
        "backup_reserve_soc",
        "battery_charge_limit",
        "battery_discharge_limit_on_grid",
        "battery_discharge_limit_off_grid",
        "battery_charge_power_limit",
        "battery_discharge_power_limit",
        "battery_forced_charge_power_limit",
    ],
    grid: [
        "export_limit_mode",
        "export_limit_power",
        "export_limit_current",
        "grid_import_power_limit",
        "grid_export_power_limit",
    ],
    ev_charger: ["ev_enabled", "ev_mode", "ev_charge_power"],
    device: ["buzzer", "led_mode", "synchronise_clock"],
};

interface PowerFunction {
    id: string;
    signHintKey: string;
}

const POWER_FUNCTIONS: readonly PowerFunction[] = [
    { id: "battery", signHintKey: "sign_battery" },
    { id: "grid", signHintKey: "sign_grid" },
    { id: "inverter", signHintKey: "sign_inverter" },
];

type ControlRow =
    | { kind: "entity"; entity: SystemEntity }
    | {
          kind: "power";
          power: PowerFunction;
          control: SystemEntity | undefined;
          target: SystemEntity | undefined;
      };

interface SectionPlan {
    id: SectionId;
    rows: ControlRow[];
}

export interface ControlsCardConfig extends SajElementConfig {
    sections?: SectionId[];
}

const entityRows = ({
    entities,
    keys,
}: {
    entities: SystemEntities;
    keys: readonly string[];
}): ControlRow[] =>
    keys.flatMap((key) => {
        const entity = entities.get(key);
        return entity === undefined ? [] : [{ kind: "entity", entity }];
    });

const powerRows = (entities: SystemEntities): ControlRow[] =>
    POWER_FUNCTIONS.flatMap((power) => {
        const control = entities.get(`${power.id}_power_control`);
        const target = entities.get(`${power.id}_power_target`);
        return control === undefined && target === undefined
            ? []
            : [{ kind: "power", power, control, target }];
    });

const planOf = ({
    entities,
    sections,
}: {
    entities: SystemEntities;
    sections: readonly SectionId[];
}): SectionPlan[] =>
    SECTION_IDS.filter((id) => sections.includes(id))
        .map((id) => ({
            id,
            rows:
                id === "power_control"
                    ? powerRows(entities)
                    : entityRows({ entities, keys: SECTION_KEYS[id] }),
        }))
        .filter((section) => section.rows.length > 0);

const entitiesOfRow = (row: ControlRow): SystemEntity[] =>
    row.kind === "entity"
        ? [row.entity]
        : [row.control, row.target].filter((entity) => entity !== undefined);

export class SajControlsCard extends SystemCard<ControlsCardConfig> {
    static override styles = [
        baseStyles,
        css`
            h3 {
                margin: 12px 0 4px;
                font-size: 0.95rem;
                font-weight: 500;
            }
            .power-row {
                padding: 4px 0;
            }
            .power-name {
                font-weight: 500;
            }
            .power-controls {
                display: flex;
                flex-wrap: wrap;
                align-items: center;
                gap: 8px;
            }
            .sign-hint {
                color: var(--secondary-text-color, #727272);
                font-size: 0.85rem;
            }
        `,
    ];

    static getConfigForm(): ReturnType<typeof configForm> {
        return configForm((text) => [
            multiSelectField({
                name: "sections",
                options: SECTION_IDS.map((id) => ({
                    value: id,
                    label: text(`section_${id}`),
                })),
            }),
        ]);
    }

    static getStubConfig(
        hass: Pick<Hass, "entities" | "devices">,
    ): Omit<ControlsCardConfig, "type"> {
        return { ...stubConfig(hass), sections: [...SECTION_IDS] };
    }

    protected override readonly hasControls = true;
    protected override readonly entityKindKey = "entity_kind_configuration";

    protected get cardRows(): number {
        const { hass, config } = this;
        if (hass === undefined || config?.device === undefined) {
            return 1;
        }
        return planOf({
            entities: systemEntities({ hass, deviceId: config.device }),
            sections: this.sections,
        }).reduce((size, section) => size + 1 + section.rows.length, 1);
    }

    protected override shownEntities(entities: SystemEntities): SystemEntity[] {
        return planOf({ entities, sections: this.sections }).flatMap(
            (section) => section.rows.flatMap(entitiesOfRow),
        );
    }

    protected override renderBody(context: CardContext): TemplateResult {
        const plan = planOf({
            entities: context.entities,
            sections: this.sections,
        });
        return this.dimmedBody({
            context,
            content: html`${this.renderLockedBanner(context)}${plan.map(
                (section) => this.renderSection({ context, section }),
            )}`,
        });
    }

    private get sections(): readonly SectionId[] {
        return this.config?.sections ?? SECTION_IDS;
    }

    private renderSection({
        context,
        section,
    }: {
        context: CardContext;
        section: SectionPlan;
    }): TemplateResult {
        return html`<h3>${this.text(`section_${section.id}`)}</h3>
            ${section.rows.map((row) => this.renderRow({ context, row }))}`;
    }

    private renderRow({
        context,
        row,
    }: {
        context: CardContext;
        row: ControlRow;
    }): TemplateResult {
        if (row.kind === "entity") {
            return renderEntityControl({
                context,
                entity: row.entity,
            });
        }
        const control = (entity: SystemEntity | undefined) =>
            entity === undefined
                ? nothing
                : renderEntityControl({
                      context,
                      entity,
                      labelHidden: true,
                  });
        return html`<div class="power-row">
            <div class="power-name">${this.text(row.power.id)}</div>
            <div class="power-controls">
                ${control(row.control)}${control(row.target)}
            </div>
            ${
                row.target === undefined
                    ? nothing
                    : html`<div class="sign-hint">
                          ${this.text(row.power.signHintKey)}
                      </div>`
            }
        </div>`;
    }
}

customElements.define(CONTROLS_CARD_TAG, SajControlsCard);

registerCard({
    type: CONTROLS_CARD_TAG,
    nameKey: "controls_card_name",
    descriptionKey: "controls_card_description",
    preview: true,
});

declare global {
    interface HTMLElementTagNameMap {
        [CONTROLS_CARD_TAG]: SajControlsCard;
    }
}
