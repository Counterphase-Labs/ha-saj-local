import { css, html, nothing, svg, type TemplateResult } from "lit";

import { fireMoreInfo } from "../actions";
import type { Hass, SajElementConfig } from "../hass";
import { registerCard } from "../registration";
import type { SystemEntities, SystemEntity } from "../system/entities";
import { operatingTone } from "../system/operating";
import {
    FLOW_STATE_TEXT_KEYS,
    flowDurationSeconds,
    powerFlow,
    wattsOf,
    type PowerFlow,
    type PowerNodeKind,
    type PowerState,
} from "../system/power";
import { ICONS, type IconName } from "../ui/icons";
import { baseStyles, toneColour } from "../ui/styles";
import { booleanField, configForm, selectField, stubConfig } from "./editor";
import { SystemCard, type CardContext } from "./system-card";

export const POWER_FLOW_CARD_TYPE = "saj-local-power-flow-card";
const POWER_FLOW_CARD_ROWS = 6;
const SHOW_STRINGS = false;
const SHOW_OPTIONAL = true;
const DEFAULT_SCOPE: PowerFlowScope = "system";

export type PowerFlowScope = "system" | "parallel";
export const POWER_FLOW_SCOPES: readonly PowerFlowScope[] = [
    "system",
    "parallel",
];

export interface PowerFlowCardConfig extends SajElementConfig {
    show_strings?: boolean;
    show_optional_equipment?: boolean;
    scope?: PowerFlowScope;
}

export const VIEW_WIDTH = 400;
export const VIEW_HEIGHT = 520;
const NODE_WIDTH = 104;
const NODE_HEIGHT = 84;
const NODE_RADIUS = 12;
const ICON_SIZE = 24;
const ICON_OFFSET_Y = -38;
const VALUE_OFFSET_Y = 8;
const LABEL_OFFSET_Y = 22;
const SECONDARY_OFFSET_Y = 35;
const STRING_LINE_HEIGHT = 16;
const STRING_FIRST_OFFSET_Y = 16;
const SECONDARY_SEPARATOR = " · ";
const OPTIONAL_ROW_Y = 460;

interface Point {
    x: number;
    y: number;
}

const HUB_POSITION: Point = { x: 200, y: 225 };
const SOLAR_POSITION: Point = { x: 200, y: 50 };

type NodeId = "solar" | "battery" | "grid" | "home" | "ev" | "backup" | "meter";

interface NodeSpec {
    id: NodeId;
    labelKey: string;
    icon: IconName;
    kind: PowerNodeKind | null;
    keys: Readonly<Record<PowerFlowScope, string>>;
    secondaryKeys?: Readonly<Record<PowerFlowScope, string>>;
    flowWords: boolean;
    absolute: boolean;
    optional: boolean;
    position?: Point;
}

const NODE_SPECS: readonly NodeSpec[] = [
    {
        id: "solar",
        labelKey: "solar",
        icon: "solar",
        kind: "solar",
        keys: { system: "pv_power", parallel: "parallel_pv_power" },
        flowWords: false,
        absolute: false,
        optional: false,
        position: SOLAR_POSITION,
    },
    {
        id: "battery",
        labelKey: "battery",
        icon: "battery",
        kind: "battery",
        keys: { system: "battery_power", parallel: "parallel_battery_power" },
        secondaryKeys: {
            system: "battery_soc",
            parallel: "parallel_battery_soc",
        },
        flowWords: true,
        absolute: true,
        optional: false,
        position: { x: 200, y: 360 },
    },
    {
        id: "grid",
        labelKey: "grid",
        icon: "grid",
        kind: "grid",
        keys: { system: "grid_power", parallel: "parallel_grid_power" },
        flowWords: true,
        absolute: true,
        optional: false,
        position: { x: 60, y: 225 },
    },
    {
        id: "home",
        labelKey: "home",
        icon: "home",
        kind: "consumer",
        keys: { system: "load_power", parallel: "parallel_load_power" },
        flowWords: false,
        absolute: false,
        optional: false,
        position: { x: 340, y: 225 },
    },
    {
        id: "ev",
        labelKey: "ev_charger",
        icon: "ev",
        kind: "consumer",
        keys: { system: "ev_power", parallel: "ev_power" },
        secondaryKeys: { system: "ev_status", parallel: "ev_status" },
        flowWords: false,
        absolute: false,
        optional: true,
    },
    {
        id: "backup",
        labelKey: "backup_load",
        icon: "backup",
        kind: "consumer",
        keys: {
            system: "backup_load_power",
            parallel: "parallel_backup_load_power",
        },
        flowWords: false,
        absolute: false,
        optional: true,
    },
    {
        id: "meter",
        labelKey: "meter_b",
        icon: "meter",
        kind: null,
        keys: { system: "meter_b_power", parallel: "parallel_meter_b_power" },
        flowWords: false,
        absolute: false,
        optional: true,
    },
];

const OPERATING_MODE_KEY = "operating_mode";
const PV_STRING_KEY = /^pv([1-9]\d*)_power$/;
const NON_DIGITS = /\D/g;

const FLOW_COLOURS: Readonly<Record<PowerState, string>> = {
    idle: "var(--divider-color, #e0e0e0)",
    producing: "var(--energy-solar-color, #ff9800)",
    consuming: "var(--primary-color, #03a9f4)",
    charging: "var(--energy-battery-in-color, #f06292)",
    discharging: "var(--energy-battery-out-color, #4db6ac)",
    importing: "var(--energy-grid-consumption-color, #488fc2)",
    exporting: "var(--energy-grid-return-color, #8353d1)",
};

const NO_FLOW: PowerFlow = { state: "idle", line: "none" };

interface DrawnNode {
    spec: NodeSpec;
    entity: SystemEntity;
    secondaryEntity: SystemEntity | undefined;
    flow: PowerFlow;
    watts: number | null;
    position: Point;
}

const isActivationKey = (event: KeyboardEvent): boolean =>
    event.key === "Enter" || event.key === " ";

export class SajLocalPowerFlowCard extends SystemCard<PowerFlowCardConfig> {
    static override styles = [
        baseStyles,
        css`
            svg {
                display: block;
                width: 100%;
                height: auto;
            }
            .node {
                cursor: pointer;
            }
            .node:focus-visible {
                outline: 2px solid var(--primary-color, #03a9f4);
            }
            .box {
                fill: var(
                    --ha-card-background,
                    var(--card-background-color, #fff)
                );
                stroke: var(--divider-color, #e0e0e0);
            }
            .icon {
                fill: var(--primary-text-color, #212121);
            }
            .value {
                font-size: 15px;
                font-weight: 500;
                fill: var(--primary-text-color, #212121);
            }
            .label,
            .secondary,
            .string {
                font-size: 11px;
                fill: var(--secondary-text-color, #727272);
            }
            .string {
                paint-order: stroke;
                stroke: var(
                    --ha-card-background,
                    var(--card-background-color, #fff)
                );
                stroke-width: 4px;
            }
            .dimmed .value,
            .dimmed .secondary,
            .dimmed .string {
                opacity: 0.5;
            }
            .line {
                fill: none;
                stroke-width: 3;
                stroke-linecap: round;
            }
            .line.idle {
                stroke: var(--divider-color, #e0e0e0);
            }
            .line.active {
                stroke-dasharray: 6 10;
                animation: flow var(--flow-duration, 2s) linear infinite;
            }
            .line.reverse {
                animation-direction: reverse;
            }
            @keyframes flow {
                to {
                    stroke-dashoffset: -16;
                }
            }
        `,
    ];

    static getConfigForm(): ReturnType<typeof configForm> {
        return configForm((text) => [
            booleanField({ name: "show_strings", fallback: SHOW_STRINGS }),
            booleanField({
                name: "show_optional_equipment",
                fallback: SHOW_OPTIONAL,
            }),
            selectField({
                name: "scope",
                options: POWER_FLOW_SCOPES.map((scope) => ({
                    value: scope,
                    label: text(`option_scope_${scope}`),
                })),
                fallback: DEFAULT_SCOPE,
            }),
        ]);
    }

    static getStubConfig(
        hass: Pick<Hass, "entities" | "devices">,
    ): Omit<PowerFlowCardConfig, "type"> {
        return { ...stubConfig(hass), scope: DEFAULT_SCOPE };
    }

    protected readonly cardRows = POWER_FLOW_CARD_ROWS;

    private get scope(): PowerFlowScope {
        return this.config?.scope ?? DEFAULT_SCOPE;
    }

    private drawnNodes(entities: SystemEntities): DrawnNode[] {
        const { scope } = this;
        const showOptional =
            this.config?.show_optional_equipment ?? SHOW_OPTIONAL;
        const present = NODE_SPECS.flatMap((spec) => {
            const entity = entities.get(spec.keys[scope]);
            return entity === undefined || (spec.optional && !showOptional)
                ? []
                : [{ spec, entity }];
        });
        const optionalCount = present.filter(
            ({ spec }) => spec.optional,
        ).length;
        let optionalIndex = 0;
        return present.map(({ spec, entity }) => {
            const watts = wattsOf(entity);
            const secondaryKey = spec.secondaryKeys?.[scope];
            const position =
                spec.position ??
                this.optionalPosition({
                    index: optionalIndex++,
                    count: optionalCount,
                });
            return {
                spec,
                entity,
                secondaryEntity:
                    secondaryKey === undefined
                        ? undefined
                        : entities.get(secondaryKey),
                watts,
                position,
                flow:
                    spec.kind === null || watts === null
                        ? NO_FLOW
                        : powerFlow({ kind: spec.kind, watts }),
            };
        });
    }

    private optionalPosition({
        index,
        count,
    }: {
        index: number;
        count: number;
    }): Point {
        return {
            x: (VIEW_WIDTH * (index + 1)) / (count + 1),
            y: OPTIONAL_ROW_Y,
        };
    }

    private stringEntities(entities: SystemEntities): SystemEntity[] {
        return (this.config?.show_strings ?? SHOW_STRINGS)
            ? [...entities.values()]
                  .filter((entity) => PV_STRING_KEY.test(entity.key))
                  .sort(
                      (left, right) =>
                          this.stringNumber(left) - this.stringNumber(right),
                  )
            : [];
    }

    private stringNumber(entity: SystemEntity): number {
        return Number(entity.key.replace(NON_DIGITS, ""));
    }

    private hasScopedReadings(entities: SystemEntities): boolean {
        const { scope } = this;
        return NODE_SPECS.some(
            ({ keys }) =>
                keys.system !== keys.parallel && entities.has(keys[scope]),
        );
    }

    protected override shownEntities(entities: SystemEntities): SystemEntity[] {
        if (this.scope === "parallel" && !this.hasScopedReadings(entities)) {
            return [];
        }
        const hub = entities.get(OPERATING_MODE_KEY);
        return [
            ...(hub === undefined ? [] : [hub]),
            ...this.drawnNodes(entities).map(({ entity }) => entity),
            ...this.stringEntities(entities),
        ];
    }

    protected override renderBody(context: CardContext): TemplateResult {
        const nodes = this.drawnNodes(context.entities);
        const hub = context.entities.get(OPERATING_MODE_KEY);
        const strings = this.stringEntities(context.entities);
        return html`<svg
            class=${context.dimmed ? "dimmed" : ""}
            viewBox="0 0 ${VIEW_WIDTH} ${VIEW_HEIGHT}"
            role="group"
        >
            ${nodes.map((node) => this.renderLine(node))}
            ${nodes.map((node) => this.renderNode({ node, context }))}
            ${hub === undefined ? nothing : this.renderHub({ entity: hub, context })}
            ${strings.map((entity, index) =>
                this.renderString({ entity, index, context }),
            )}
        </svg>`;
    }

    private renderLine(node: DrawnNode): TemplateResult {
        const { flow, position, watts } = node;
        const active = flow.line !== "none" && watts !== null;
        const classes = [
            "line",
            active ? "active" : "idle",
            flow.line === "from_inverter" ? "reverse" : "",
        ].join(" ");
        return svg`<line
            class=${classes}
            x1=${position.x}
            y1=${position.y}
            x2=${HUB_POSITION.x}
            y2=${HUB_POSITION.y}
            style=${
                active
                    ? `--flow-duration: ${String(flowDurationSeconds(watts))}s; stroke: ${FLOW_COLOURS[flow.state]}`
                    : ""
            }
        ></line>`;
    }

    private renderNode({
        node,
        context,
    }: {
        node: DrawnNode;
        context: CardContext;
    }): TemplateResult {
        const { spec, entity, flow, position } = node;
        const flowKey = spec.flowWords
            ? FLOW_STATE_TEXT_KEYS[flow.state]
            : undefined;
        const secondary = [
            ...(node.secondaryEntity === undefined
                ? []
                : [this.valueText({ context, entity: node.secondaryEntity })]),
            ...(flowKey === undefined || node.watts === null
                ? []
                : [this.text(flowKey)]),
        ].join(SECONDARY_SEPARATOR);
        return this.renderTarget({
            entity,
            position,
            icon: spec.icon,
            label: this.text(spec.labelKey),
            value: this.valueText({ context, entity, absolute: spec.absolute }),
            secondary,
        });
    }

    private renderHub({
        entity,
        context,
    }: {
        entity: SystemEntity;
        context: CardContext;
    }): TemplateResult {
        return this.renderTarget({
            entity,
            position: HUB_POSITION,
            icon: "inverter",
            label: this.text("inverter"),
            value: this.valueText({ context, entity }),
            secondary: "",
            colour: toneColour(operatingTone(entity.state.state)),
        });
    }

    private renderTarget({
        entity,
        position,
        icon,
        label,
        value,
        secondary,
        colour,
    }: {
        entity: SystemEntity;
        position: Point;
        icon: IconName;
        label: string;
        value: string;
        secondary: string;
        colour?: string;
    }): TemplateResult {
        const { x, y } = position;
        return this.renderTap({
            entity,
            label: `${label} ${value} ${secondary}`.trim(),
            content: svg`<rect
                class="box"
                x=${x - NODE_WIDTH / 2}
                y=${y - NODE_HEIGHT / 2}
                width=${NODE_WIDTH}
                height=${NODE_HEIGHT}
                rx=${NODE_RADIUS}
            ></rect>
            <path
                class="icon"
                d=${ICONS[icon]}
                transform="translate(${x - ICON_SIZE / 2} ${y + ICON_OFFSET_Y})"
            ></path>
            <text
                class="value"
                x=${x}
                y=${y + VALUE_OFFSET_Y}
                text-anchor="middle"
                style=${colour === undefined ? "" : `fill: ${colour}`}
            >${value}</text>
            <text class="label" x=${x} y=${y + LABEL_OFFSET_Y} text-anchor="middle">${label}</text>
            <text class="secondary" x=${x} y=${y + SECONDARY_OFFSET_Y} text-anchor="middle">${secondary}</text>`,
        });
    }

    private renderString({
        entity,
        index,
        context,
    }: {
        entity: SystemEntity;
        index: number;
        context: CardContext;
    }): TemplateResult {
        const text = `${this.nameOf({ context, entity })}: ${this.valueText({ context, entity })}`;
        return this.renderTap({
            entity,
            label: text,
            content: svg`<text
                class="string"
                x=${SOLAR_POSITION.x}
                y=${SOLAR_POSITION.y + NODE_HEIGHT / 2 + STRING_FIRST_OFFSET_Y + index * STRING_LINE_HEIGHT}
                text-anchor="middle"
            >${text}</text>`,
        });
    }

    private renderTap({
        entity,
        label,
        content,
    }: {
        entity: SystemEntity;
        label: string;
        content: TemplateResult;
    }): TemplateResult {
        const open = (): void => {
            fireMoreInfo({ host: this, entityId: entity.entityId });
        };
        return svg`<g
            class="node"
            role="button"
            tabindex="0"
            aria-label=${label}
            @click=${open}
            @keydown=${(event: KeyboardEvent) => {
                if (isActivationKey(event)) {
                    event.preventDefault();
                    open();
                }
            }}
        >${content}</g>`;
    }
}

customElements.define(POWER_FLOW_CARD_TYPE, SajLocalPowerFlowCard);

registerCard({
    type: POWER_FLOW_CARD_TYPE,
    nameKey: "power_flow_card_name",
    descriptionKey: "power_flow_card_description",
    preview: true,
});

declare global {
    interface HTMLElementTagNameMap {
        [POWER_FLOW_CARD_TYPE]: SajLocalPowerFlowCard;
    }
}
