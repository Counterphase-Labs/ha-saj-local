import { css, html, nothing, type TemplateResult } from "lit";
import { styleMap } from "lit/directives/style-map.js";

import type { Hass, SajElementConfig } from "../hass";
import { registerCard } from "../registration";
import { setNumberRequest } from "../system/control";
import {
    isUnavailable,
    numericValue,
    systemEntities,
    type SystemEntities,
    type SystemEntity,
} from "../system/entities";
import {
    APPLICATION_MODE_KEY,
    MINUTES_PER_DAY,
    scheduleOf,
    SLOT_KINDS,
    timelineBars,
    timeOfUseNoticeRequired,
    type Schedule,
    type Slot,
    type SlotKind,
    type TimelineBar,
} from "../system/schedule";
import { baseStyles } from "../ui/styles";
import { daysOfNumber, weekdayName, weekOrder } from "../system/weekdays";
import "../ui/icon";
import "../ui/weekday-buttons";
import { renderEntityControl } from "./entity-controls";
import { multiSelectField, SystemCard, type CardContext } from "./system-card";
import { booleanField, configForm, stubConfig } from "./editor";

export const SCHEDULE_CARD_TAG = "saj-local-schedule-card";

const TIMELINE_ROWS_IN_CARD_SIZE = 4;
const SHOW_TIMELINE = true;

const KIND_COLOURS: Record<SlotKind, string> = {
    charge: "var(--energy-battery-in-color, #4db6ac)",
    discharge: "var(--energy-battery-out-color, #a280db)",
    ev_charger: "var(--energy-grid-consumption-color, #488fc2)",
};

export interface ScheduleCardConfig extends SajElementConfig {
    slot_kinds?: SlotKind[];
    show_timeline?: boolean;
}

const percentOfDay = (minutes: number): number =>
    (minutes / MINUTES_PER_DAY) * 100;

export class SajScheduleCard extends SystemCard<ScheduleCardConfig> {
    static override properties = {
        ...SystemCard.properties,
        expanded: { state: true },
    };

    static override styles = [
        baseStyles,
        css`
            .timeline {
                display: flex;
                flex-direction: column;
                gap: 4px;
                margin-bottom: 12px;
            }
            .day {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .day-name {
                width: 36px;
                color: var(--secondary-text-color, #727272);
                font-size: 0.8rem;
            }
            .track {
                position: relative;
                flex: 1;
                height: 16px;
                background: var(--divider-color, #e0e0e0);
                border-radius: 4px;
            }
            .bar {
                position: absolute;
                top: 0;
                height: 100%;
                min-width: 4px;
                padding: 0;
                background: var(--bar-colour);
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            .bar.disabled {
                background: repeating-linear-gradient(
                    45deg,
                    var(--bar-colour) 0 4px,
                    transparent 4px 8px
                );
            }
            h3 {
                margin: 12px 0 4px;
                font-size: 0.95rem;
                font-weight: 500;
            }
            .slot-header {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .summary {
                display: flex;
                flex: 1;
                align-items: center;
                gap: 8px;
                padding: 6px 0;
                background: none;
                border: none;
                cursor: pointer;
                text-align: start;
            }
            .summary .slot-name {
                font-weight: 500;
            }
            .summary .slot-detail {
                color: var(--secondary-text-color, #727272);
            }
            .summary[aria-expanded="true"] saj-icon {
                transform: rotate(180deg);
            }
            .editor {
                padding: 4px 0 8px 32px;
            }
            .left-out {
                margin-top: 8px;
                color: var(--secondary-text-color, #727272);
                font-size: 0.85rem;
            }
        `,
    ];

    static getConfigForm(): ReturnType<typeof configForm> {
        return configForm((text) => [
            multiSelectField({
                name: "slot_kinds",
                options: SLOT_KINDS.map((kind) => ({
                    value: kind,
                    label: text(`option_kind_${kind}`),
                })),
            }),
            booleanField({
                name: "show_timeline",
                fallback: SHOW_TIMELINE,
            }),
        ]);
    }

    static getStubConfig(
        hass: Pick<Hass, "entities" | "devices">,
    ): Omit<ScheduleCardConfig, "type"> {
        return { ...stubConfig(hass), slot_kinds: [...SLOT_KINDS] };
    }

    declare expanded: ReadonlySet<string>;

    private scheduled:
        | {
              entities: SystemEntities;
              kinds: readonly SlotKind[];
              schedule: Schedule;
          }
        | undefined;

    constructor() {
        super();
        this.expanded = new Set();
    }

    protected override readonly hasControls = true;
    protected override readonly entityKindKey = "entity_kind_schedule";

    protected get cardRows(): number {
        const { hass, config } = this;
        if (hass === undefined || config?.device === undefined) {
            return 1;
        }
        const { slots } = this.scheduleFor(
            systemEntities({ hass, deviceId: config.device }),
        );
        return (
            1 +
            slots.length +
            (this.showTimeline ? TIMELINE_ROWS_IN_CARD_SIZE : 0)
        );
    }

    protected override shownEntities(entities: SystemEntities): SystemEntity[] {
        return this.scheduleFor(entities).slots.flatMap((slot) =>
            this.slotEntities(slot),
        );
    }

    protected override emptyMessage(context: CardContext): string {
        const { leftOut } = this.scheduleFor(context.entities);
        return leftOut === 0
            ? ""
            : this.text("slots_left_out", { count: leftOut });
    }

    protected override renderBody(context: CardContext): TemplateResult {
        const { slots, leftOut } = this.scheduleFor(context.entities);
        return this.dimmedBody({
            context,
            content: html`${this.renderLockedBanner(context)}${this.renderNotice(
                context,
                slots,
            )}${
                this.showTimeline
                    ? this.renderTimeline(context, slots)
                    : nothing
            }${SLOT_KINDS.filter((kind) =>
                slots.some((slot) => slot.kind === kind),
            ).map((kind) =>
                this.renderKind({
                    context,
                    kind,
                    slots: slots.filter((slot) => slot.kind === kind),
                }),
            )}${
                leftOut === 0
                    ? nothing
                    : html`<div class="left-out">
                          ${this.text("slots_left_out", { count: leftOut })}
                      </div>`
            }`,
        });
    }

    private scheduleFor(entities: SystemEntities): Schedule {
        const { kinds } = this;
        if (
            this.scheduled?.entities !== entities ||
            this.scheduled.kinds !== kinds
        ) {
            this.scheduled = {
                entities,
                kinds,
                schedule: scheduleOf({ entities, kinds }),
            };
        }
        return this.scheduled.schedule;
    }

    private get kinds(): readonly SlotKind[] {
        return this.config?.slot_kinds ?? SLOT_KINDS;
    }

    private get showTimeline(): boolean {
        return this.config?.show_timeline ?? SHOW_TIMELINE;
    }

    private slotEntities(slot: Slot): SystemEntity[] {
        return [
            slot.start,
            slot.end,
            slot.days,
            slot.power,
            slot.enabled,
            slot.mode,
            slot.gridCharging,
            slot.batteryDischarge,
        ].filter((entity) => entity !== null);
    }

    private renderNotice(
        context: CardContext,
        slots: readonly Slot[],
    ): TemplateResult | typeof nothing {
        const mode = context.entities.get(APPLICATION_MODE_KEY);
        if (
            mode === undefined ||
            !timeOfUseNoticeRequired({ entities: context.entities, slots })
        ) {
            return nothing;
        }
        return html`<saj-notice
            tone="warning"
            .message=${this.text("time_of_use_notice")}
            >${renderEntityControl({
                context,
                entity: mode,
                labelHidden: true,
            })}</saj-notice
        >`;
    }

    private renderTimeline(
        context: CardContext,
        slots: readonly Slot[],
    ): TemplateResult {
        const bars = timelineBars(slots);
        const { language } = context.hass;
        return html`<div
            class="timeline"
            role="group"
            aria-label=${this.text("week_timeline")}
        >
            ${weekOrder(context.hass).map(
                (day) =>
                    html`<div class="day">
                        <span class="day-name"
                            >${weekdayName({
                                day,
                                language,
                                width: "short",
                            })}</span
                        >
                        <div class="track">
                            ${bars
                                .filter((bar) => bar.day === day)
                                .map((bar) => this.renderBar(bar))}
                        </div>
                    </div>`,
            )}
        </div>`;
    }

    private renderBar(bar: TimelineBar): TemplateResult {
        const { slot } = bar;
        return html`<button
            type="button"
            class=${bar.disabled ? "bar disabled" : "bar"}
            style=${styleMap({
                left: `${String(percentOfDay(bar.startMinute))}%`,
                width: `${String(percentOfDay(bar.endMinute - bar.startMinute))}%`,
                "--bar-colour": KIND_COLOURS[slot.kind],
            })}
            aria-label=${this.slotName(slot)}
            @click=${() => {
                this.expand(slot.stem);
            }}
        ></button>`;
    }

    private slotName(slot: Slot): string {
        return `${this.text(`option_kind_${slot.kind}`)} ${this.text(
            "slot_number",
            { number: slot.number },
        )}`;
    }

    private renderKind({
        context,
        kind,
        slots,
    }: {
        context: CardContext;
        kind: SlotKind;
        slots: readonly Slot[];
    }): TemplateResult {
        return html`<h3>${this.text(`option_kind_${kind}`)}</h3>
            ${slots.map((slot) => this.renderSlot({ context, slot }))}`;
    }

    private renderSlot({
        context,
        slot,
    }: {
        context: CardContext;
        slot: Slot;
    }): TemplateResult {
        const { hass } = context;
        const open = this.expanded.has(slot.stem);
        const daysValue = numericValue(slot.days) ?? 0;
        const selectedDays = new Set(daysOfNumber(daysValue));
        const dayNames = weekOrder(hass)
            .filter((day) => selectedDays.has(day))
            .map((day) =>
                weekdayName({ day, language: hass.language, width: "short" }),
            )
            .join(" ");
        return html`<div class="slot">
            <div class="slot-header">
                <button
                    type="button"
                    class="summary"
                    aria-expanded=${String(open)}
                    @click=${() => {
                        this.toggle(slot.stem);
                    }}
                >
                    <saj-icon name="expand"></saj-icon>
                    <span class="slot-name"
                        >${this.text("slot_number", {
                            number: slot.number,
                        })}</span
                    >
                    <span class="slot-detail"
                        >${hass.formatEntityState(slot.start.state)} -
                        ${hass.formatEntityState(slot.end.state)}</span
                    >
                    <span class="slot-detail">${dayNames}</span>
                    <span class="slot-detail"
                        >${hass.formatEntityState(slot.power.state)}</span
                    >
                </button>
                ${
                    slot.enabled === null
                        ? nothing
                        : renderEntityControl({
                              context,
                              entity: slot.enabled,
                              labelHidden: true,
                          })
                }
            </div>
            ${open ? this.renderEditor({ context, slot }) : nothing}
        </div>`;
    }

    private renderEditor({
        context,
        slot,
    }: {
        context: CardContext;
        slot: Slot;
    }): TemplateResult {
        const { hass, lock } = context;
        const control = (entity: SystemEntity | null) =>
            entity === null
                ? nothing
                : renderEntityControl({ context, entity });
        const { days } = slot;
        return html`<div class="editor">
            ${control(slot.start)}${control(slot.end)}${control(slot.power)}
            <saj-weekday-buttons
                .hass=${hass}
                .label=${this.text("weekdays")}
                .value=${numericValue(days) ?? 0}
                .disabled=${lock.locked || isUnavailable(days)}
                .busy=${this.tracker.isBusy(days.entityId)}
                .error=${this.tracker.errorOf(days.entityId) ?? ""}
                @saj-commit=${(event: CustomEvent<number>) => {
                    void this.tracker.submit({
                        entityId: days.entityId,
                        request: setNumberRequest(event.detail),
                    });
                }}
            ></saj-weekday-buttons>
            ${control(slot.mode)}${control(slot.gridCharging)}${control(
                slot.batteryDischarge,
            )}
        </div>`;
    }

    private toggle(stem: string): void {
        const next = new Set(this.expanded);
        if (!next.delete(stem)) {
            next.add(stem);
        }
        this.expanded = next;
    }

    private expand(stem: string): void {
        this.expanded = new Set([...this.expanded, stem]);
    }
}

customElements.define(SCHEDULE_CARD_TAG, SajScheduleCard);

registerCard({
    type: SCHEDULE_CARD_TAG,
    nameKey: "schedule_card_name",
    descriptionKey: "schedule_card_description",
    preview: true,
});

declare global {
    interface HTMLElementTagNameMap {
        [SCHEDULE_CARD_TAG]: SajScheduleCard;
    }
}
