import { css, html, nothing, type TemplateResult } from "lit";

import { fireMoreInfo } from "../actions";
import type { Hass, SajElementConfig } from "../hass";
import { registerCard } from "../registration";
import {
    isOn,
    isUnavailable,
    numericValue,
    type SystemEntities,
    type SystemEntity,
} from "../system/entities";
import { FLOW_STATE_TEXT_KEYS, powerFlow, wattsOf } from "../system/power";
import type { GaugeMarker } from "../ui/ring-gauge";
import "../ui/ring-gauge";
import type { IconName } from "../ui/icons";
import { baseStyles, toneColour } from "../ui/styles";
import { booleanField, configForm, stubConfig } from "./editor";
import { presentEntities, SystemCard, type CardContext } from "./system-card";

export const BATTERY_CARD_TYPE = "saj-local-battery-card";
const BATTERY_CARD_ROWS = 5;
const SHOW_PACKS = true;
const SOC_KEY = "battery_soc";
const POWER_KEY = "battery_power";
const POWER_SEPARATOR = " · ";

const MARKER_KEYS: readonly string[] = [
    "backup_reserve_soc",
    "battery_charge_limit",
    "battery_discharge_limit_on_grid",
];

interface ReadingKey {
    key: string;
    icon: IconName;
}

const READING_KEYS: readonly ReadingKey[] = [
    { key: "battery_voltage", icon: "battery" },
    { key: "battery_current", icon: "battery" },
    { key: "battery_temperature", icon: "temperature" },
    { key: "battery_usable_capacity", icon: "battery" },
];

const PACK_FIELDS: readonly ReadingKey[] = [
    { key: "soc", icon: "battery" },
    { key: "soh", icon: "battery" },
    { key: "voltage", icon: "battery" },
    { key: "current", icon: "battery" },
    { key: "temperature", icon: "temperature" },
    { key: "cycles", icon: "info" },
];

const PACK_FLAGS: readonly { key: string; tone: "error" | "warning" }[] = [
    { key: "fault", tone: "error" },
    { key: "warning", tone: "warning" },
];

const PACK_KEY = /^battery_pack(\d+)_/;
const DECIMAL_RADIX = 10;

const packKey = ({
    number,
    field,
}: {
    number: number;
    field: string;
}): string => `battery_pack${String(number)}_${field}`;

export interface BatteryCardConfig extends SajElementConfig {
    show_packs?: boolean;
}

export class SajLocalBatteryCard extends SystemCard<BatteryCardConfig> {
    static override styles = [
        baseStyles,
        css`
            .gauge {
                display: flex;
                justify-content: center;
                width: 100%;
                padding: 0;
                background: none;
                border: none;
                cursor: pointer;
            }
            h3 {
                display: flex;
                align-items: center;
                gap: 4px;
                margin: 8px 0 0;
                font-size: 1rem;
                font-weight: 500;
            }
        `,
    ];

    static getConfigForm(): ReturnType<typeof configForm> {
        return configForm(() => [
            booleanField({ name: "show_packs", fallback: SHOW_PACKS }),
        ]);
    }

    static getStubConfig(
        hass: Pick<Hass, "entities" | "devices">,
    ): ReturnType<typeof stubConfig> {
        return stubConfig(hass);
    }

    protected readonly cardRows = BATTERY_CARD_ROWS;

    private get showPacks(): boolean {
        return this.config?.show_packs ?? SHOW_PACKS;
    }

    private packNumbers(entities: SystemEntities): number[] {
        const numbers = new Set<number>();
        for (const key of entities.keys()) {
            const match = PACK_KEY.exec(key);
            if (match?.[1] !== undefined) {
                numbers.add(Number.parseInt(match[1], DECIMAL_RADIX));
            }
        }
        return [...numbers].sort((left, right) => left - right);
    }

    private packEntities({
        entities,
        number,
    }: {
        entities: SystemEntities;
        number: number;
    }): SystemEntity[] {
        return presentEntities({
            entities,
            keys: [...PACK_FIELDS, ...PACK_FLAGS].map(({ key }) =>
                packKey({ number, field: key }),
            ),
        });
    }

    protected override shownEntities(entities: SystemEntities): SystemEntity[] {
        if (!entities.has(SOC_KEY)) {
            return [];
        }
        const keys = [
            SOC_KEY,
            ...MARKER_KEYS,
            POWER_KEY,
            ...READING_KEYS.map(({ key }) => key),
        ];
        const plain = presentEntities({ entities, keys });
        const packs = this.showPacks
            ? this.packNumbers(entities).flatMap((number) =>
                  this.packEntities({ entities, number }),
              )
            : [];
        return [...plain, ...packs];
    }

    protected override renderEmpty(): TemplateResult {
        return html`<saj-notice
            .message=${this.text("no_battery")}
        ></saj-notice>`;
    }

    protected override renderBody(context: CardContext): TemplateResult {
        const { entities } = context;
        return html`${presentEntities({ entities, keys: [SOC_KEY] }).map(
            (soc) => this.renderGauge({ context, soc }),
        )}
        ${presentEntities({ entities, keys: [POWER_KEY] }).map((power) =>
            this.renderPower({ context, power }),
        )}
        ${READING_KEYS.map(({ key, icon }) =>
            presentEntities({ entities, keys: [key] }).map((entity) =>
                this.valueRow({ context, entity, icon }),
            ),
        )}
        ${
            this.showPacks
                ? this.packNumbers(entities).map((number) =>
                      this.renderPack({ context, number }),
                  )
                : nothing
        }`;
    }

    private renderGauge({
        context,
        soc,
    }: {
        context: CardContext;
        soc: SystemEntity;
    }): TemplateResult {
        const markers: GaugeMarker[] = MARKER_KEYS.flatMap((key) => {
            const entity = context.entities.get(key);
            const percent = entity === undefined ? null : numericValue(entity);
            return entity === undefined || percent === null
                ? []
                : [
                      {
                          percent,
                          label: `${this.nameOf({ context, entity })} ${this.valueText({ context, entity })}`,
                      },
                  ];
        });
        const label = this.nameOf({ context, entity: soc });
        const displayValue = this.valueText({ context, entity: soc });
        return html`<button
            type="button"
            class="gauge"
            aria-label=${`${label} ${displayValue}`}
            @click=${() => {
                fireMoreInfo({ host: this, entityId: soc.entityId });
            }}
        >
            <saj-ring-gauge
                .percent=${numericValue(soc) ?? 0}
                .displayValue=${displayValue}
                .label=${label}
                .tone=${isUnavailable(soc) ? "disabled" : "primary"}
                .markers=${markers}
                style=${context.dimmed ? "opacity: 0.5" : ""}
            ></saj-ring-gauge>
        </button>`;
    }

    private renderPower({
        context,
        power,
    }: {
        context: CardContext;
        power: SystemEntity;
    }): TemplateResult {
        const watts = wattsOf(power);
        const stateKey =
            watts === null
                ? undefined
                : FLOW_STATE_TEXT_KEYS[
                      powerFlow({ kind: "battery", watts }).state
                  ];
        const value = [
            this.valueText({ context, entity: power, absolute: true }),
            ...(stateKey === undefined ? [] : [this.text(stateKey)]),
        ].join(POWER_SEPARATOR);
        return this.valueRow({
            context,
            entity: power,
            icon: "battery",
            value,
        });
    }

    private renderPack({
        context,
        number,
    }: {
        context: CardContext;
        number: number;
    }): TemplateResult {
        const { entities } = context;
        return html`<h3>
                ${this.text("battery_pack", { number })}${PACK_FLAGS.map(
                    ({ key, tone }) => {
                        const entity = entities.get(
                            packKey({ number, field: key }),
                        );
                        return entity !== undefined && isOn(entity)
                            ? html`<saj-icon
                                  name="fault"
                                  role="img"
                                  aria-label=${this.nameOf({ context, entity })}
                                  style="color: ${toneColour(tone)}"
                              ></saj-icon>`
                            : nothing;
                    },
                )}
            </h3>
            ${PACK_FIELDS.map(({ key, icon }) => {
                const entity = entities.get(packKey({ number, field: key }));
                return entity === undefined
                    ? nothing
                    : this.valueRow({ context, entity, icon });
            })}`;
    }
}

customElements.define(BATTERY_CARD_TYPE, SajLocalBatteryCard);

registerCard({
    type: BATTERY_CARD_TYPE,
    nameKey: "battery_card_name",
    descriptionKey: "battery_card_description",
    preview: true,
});

declare global {
    interface HTMLElementTagNameMap {
        [BATTERY_CARD_TYPE]: SajLocalBatteryCard;
    }
}
