import { html, nothing, type TemplateResult } from "lit";

import type { Hass, HassEntityNameItem, SajElementConfig } from "../hass";
import "../ui/card-container";
import "../ui/empty-state";
import "../ui/notice";
import "../ui/value-row";
import type { IconName } from "../ui/icons";
import type { EditorField, EditorOption } from "./editor";
import type { ControlContext } from "./entity-controls";
import { SystemElement } from "../ui/system-element";
import {
    allUnavailable,
    isUnavailable,
    numericValue,
    systemEntities,
    type SystemEntities,
    type SystemEntity,
} from "../system/entities";
import {
    ControlTracker,
    controlLock,
    type ControlLock,
} from "../system/control";
import type { Tone } from "../system/operating";
import { systemTitle } from "../system/title";

export const GRID_COLUMNS = 12;
export const MINIMUM_GRID_COLUMNS = 6;
const DIMMED_STYLE = "opacity: 0.5";

const ENTITY_NAME: readonly HassEntityNameItem[] = [{ type: "entity" }];

export const presentEntities = ({
    entities,
    keys,
}: {
    entities: SystemEntities;
    keys: readonly string[];
}): SystemEntity[] =>
    keys.flatMap((key) => {
        const entity = entities.get(key);
        return entity === undefined ? [] : [entity];
    });

export const multiSelectField = ({
    name,
    options,
}: {
    name: string;
    options: readonly EditorOption[];
}): EditorField => ({
    name,
    default: options.map((option) => option.value),
    selector: { select: { options, multiple: true, mode: "list" } },
});

export interface SystemGridOptions {
    columns: number;
    min_columns: number;
}

export interface CardContext extends ControlContext {
    deviceId: string;
    entities: SystemEntities;
    lock: ControlLock;
    dimmed: boolean;
}

export interface RowOptions {
    context: CardContext;
    entity: SystemEntity;
    icon?: IconName;
    tone?: Tone;
    absolute?: boolean;
    label?: string;
    value?: string;
}

export abstract class SystemCard<
    Config extends SajElementConfig,
> extends SystemElement {
    static override properties = {
        ...SystemElement.properties,
        config: { attribute: false, state: true },
    };

    declare config: Config | undefined;

    protected abstract readonly cardRows: number;
    protected readonly hasControls: boolean = false;
    protected readonly entityKindKey: string = "entity_kind_reading";

    protected readonly tracker = new ControlTracker(this, () => this.hass);

    setConfig(config: Config): void {
        this.config = config;
    }

    protected override watchedDeviceId(): string | undefined {
        return this.config?.device;
    }

    getCardSize(): number {
        return this.cardRows;
    }

    getGridOptions(): SystemGridOptions {
        return {
            columns: GRID_COLUMNS,
            min_columns: MINIMUM_GRID_COLUMNS,
        };
    }

    protected abstract shownEntities(entities: SystemEntities): SystemEntity[];

    protected abstract renderBody(context: CardContext): TemplateResult;

    protected nameOf({
        context,
        entity,
    }: {
        context: CardContext;
        entity: SystemEntity;
    }): string {
        return context.hass.formatEntityName(entity.state, ENTITY_NAME);
    }

    protected valueText({
        context,
        entity,
        absolute = false,
    }: {
        context: CardContext;
        entity: SystemEntity;
        absolute?: boolean;
    }): string {
        if (isUnavailable(entity)) {
            return this.text("unavailable");
        }
        const number = absolute ? numericValue(entity) : null;
        return context.hass.formatEntityState(
            entity.state,
            number === null ? undefined : String(Math.abs(number)),
        );
    }

    protected valueRow({
        context,
        entity,
        icon,
        tone,
        absolute,
        label,
        value,
    }: RowOptions): TemplateResult {
        return html`<saj-value-row
            .label=${label ?? this.nameOf({ context, entity })}
            .value=${value ?? this.valueText({ context, entity, absolute })}
            .icon=${icon}
            .tone=${tone}
            .entityId=${entity.entityId}
            .dimmed=${context.dimmed}
        ></saj-value-row>`;
    }

    protected emptyMessage?(context: CardContext): string;

    protected renderEmpty(context: CardContext): TemplateResult {
        return html`<saj-empty-state
            .hass=${this.hass}
            .locked=${this.hasControls && context.lock.locked}
            .kind=${this.text(this.entityKindKey)}
            .message=${this.emptyMessage?.(context) ?? ""}
            .deviceId=${context.deviceId}
        ></saj-empty-state>`;
    }

    protected renderLockedBanner(
        context: CardContext,
    ): TemplateResult | typeof nothing {
        return context.lock.locked
            ? html`<saj-empty-state
                  .hass=${this.hass}
                  .locked=${true}
              ></saj-empty-state>`
            : nothing;
    }

    protected dimmedBody({
        context,
        content,
    }: {
        context: CardContext;
        content: TemplateResult;
    }): TemplateResult {
        return html`<div style=${context.dimmed ? DIMMED_STYLE : ""}>
            ${content}
        </div>`;
    }

    protected override render(): TemplateResult | typeof nothing {
        const { hass, config } = this;
        if (hass === undefined || config === undefined) {
            return nothing;
        }
        const { device } = config;
        const entities =
            device === undefined
                ? new Map<string, SystemEntity>()
                : systemEntities({ hass, deviceId: device });
        const heading =
            device === undefined ? "" : systemTitle({ hass, deviceId: device });
        return html`<saj-card .heading=${heading}
            >${
                device === undefined || entities.size === 0
                    ? html`<saj-notice
                          .message=${this.text("choose_system")}
                      ></saj-notice>`
                    : this.renderSystem({ hass, deviceId: device, entities })
            }</saj-card
        >`;
    }

    private renderSystem({
        hass,
        deviceId,
        entities,
    }: {
        hass: Hass;
        deviceId: string;
        entities: SystemEntities;
    }): TemplateResult {
        const shown = this.shownEntities(entities);
        const context: CardContext = {
            hass,
            deviceId,
            entities,
            lock: controlLock(entities),
            tracker: this.tracker,
            dimmed: allUnavailable(shown),
        };
        if (shown.length === 0) {
            return this.renderEmpty(context);
        }
        return html`${
            context.dimmed
                ? html`<saj-notice
                      tone="warning"
                      .message=${this.text("not_answering")}
                  ></saj-notice>`
                : nothing
        }${this.renderBody(context)}`;
    }
}
