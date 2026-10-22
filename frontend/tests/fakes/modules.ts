import { vi, type MockInstance } from "vitest";

import type { Hass } from "../../src/hass";

export const fakeText = (
    key: string,
    values?: Readonly<Record<string, string | number>>,
): string => (values === undefined ? key : `${key}:${JSON.stringify(values)}`);

export const stylesModule = async () => {
    const { css } = await import("lit");
    return {
        baseStyles: css``,
        TONE_COLOURS: {},
        toneColour: vi.fn((tone: string | undefined) =>
            tone === undefined ? "inherit" : `var(--tone-${tone})`,
        ),
    };
};

export const iconsModule = () => ({
    ICONS: new Proxy<Record<string, string>>(
        {},
        {
            get: (_target, name) => `path:${String(name)}`,
        },
    ),
});

export const localizedElementModule = async () => {
    const { LitElement } = await import("lit");
    class LocalizedElement extends LitElement {
        static properties = { hass: { attribute: false } };
        declare hass: Hass | undefined;

        protected get text(): typeof fakeText {
            return fakeText;
        }
    }
    return { LocalizedElement };
};

export const localizeModule = () => ({
    FALLBACK_LANGUAGE: "en",
    localizerFor: vi.fn(() => fakeText),
    pageLocalizer: vi.fn(() => fakeText),
    relativeTimeText: vi.fn(
        ({ language }: { language: string }) => `relative:${language}`,
    ),
});

export const actionsModule = () => ({
    ACTION_EVENT: "hass-action",
    SETTINGS_PATH: "/settings",
    deviceDetailPath: vi.fn((deviceId: string) => `/device/${deviceId}`),
    fireMoreInfo: vi.fn(),
    fireNavigate: vi.fn(),
});

export const registrationModule = () => ({
    registerCard: vi.fn(),
    registerCardFeature: vi.fn(),
    registerBadge: vi.fn(),
});

export const controlElementModule = async () => {
    const { LitElement, html } = await import("lit");
    class ControlElement extends LitElement {
        static properties = {
            hass: { attribute: false },
            label: { type: String },
            labelHidden: { type: Boolean },
            disabled: { type: Boolean },
            busy: { type: Boolean },
            error: { type: String },
        };

        declare hass: Hass | undefined;
        declare label: string;
        declare labelHidden: boolean;
        declare disabled: boolean;
        declare busy: boolean;
        declare error: string;
        readonly commit = vi.fn();

        constructor() {
            super();
            this.label = "";
            this.labelHidden = false;
            this.disabled = false;
            this.busy = false;
            this.error = "";
        }

        protected get text(): typeof fakeText {
            return fakeText;
        }

        protected get inactive(): boolean {
            return this.disabled || this.busy;
        }

        protected renderFrame(input: unknown) {
            return html`<div class="frame">${input}</div>`;
        }
    }
    return {
        ControlElement,
        controlStyles: [],
        COMMIT_EVENT: "saj-commit",
    };
};

const commitSpyOf = (control: Element): MockInstance => {
    const spy: unknown = Reflect.get(control, "commit");
    if (!vi.isMockFunction(spy)) {
        throw new Error("The element does not record commits");
    }
    return spy;
};

export const commitsOf = (control: Element): unknown[] =>
    commitSpyOf(control).mock.calls.map(([value]: unknown[]) => value);

export const editorModule = () => ({
    booleanField: vi.fn(
        ({ name, fallback }: { name: string; fallback: boolean }) => ({
            kind: "boolean",
            name,
            fallback,
        }),
    ),
    selectField: vi.fn(
        ({
            name,
            options,
            fallback,
        }: {
            name: string;
            options: unknown[];
            fallback: string;
        }) => ({
            kind: "select",
            name,
            options,
            fallback,
        }),
    ),
    configForm: vi.fn(
        (fields: (text: typeof fakeText) => readonly unknown[]) => ({
            fields: fields(fakeText),
        }),
    ),
    stubConfig: vi.fn(() => ({ stub: true })),
});

export const entityControlsModule = async () => {
    const { html } = await import("lit");
    return {
        entityLabel: vi.fn(
            ({ entity }: { entity: { key: string } }) => `label(${entity.key})`,
        ),
        renderEntityControl: vi.fn(
            ({
                entity,
                labelHidden = false,
            }: {
                entity: { key: string };
                labelHidden?: boolean;
            }) =>
                html`<saj-control-stub
                    .entityKey=${entity.key}
                    .labelHidden=${labelHidden}
                ></saj-control-stub>`,
        ),
    };
};

export const faultsModule = () => ({
    FAULT_GROUPS: [
        { id: "inverter", summaryKey: "inverter_fault", prefix: "inverter" },
        { id: "battery", summaryKey: "battery_fault", prefix: "battery" },
        { id: "ev", summaryKey: "ev_fault", prefix: "ev" },
    ],
    faultGroups: vi.fn(() => []),
    activeFaultSummaries: vi.fn(() => []),
});

export const powerModule = () => ({
    FLOW_STATE_TEXT_KEYS: {
        charging: "charging",
        discharging: "discharging",
        importing: "importing",
        exporting: "exporting",
        idle: "idle",
    },
    powerFlow: vi.fn(() => ({ state: "idle", line: "none" })),
    flowDurationSeconds: vi.fn((watts: number) => 100 / Math.max(watts, 1)),
    wattsOf: vi.fn(() => null),
});

export const operatingModule = () => ({
    operatingTone: vi.fn(
        (state: string | undefined) => `tone(${String(state)})`,
    ),
});

export const controlModule = () => ({
    pressButtonRequest: vi.fn(() => ({ domain: "button", service: "press" })),
    setNumberRequest: vi.fn((value: number) => ({
        domain: "number",
        service: "set_value",
        data: { value },
    })),
    selectOptionRequest: vi.fn((option: string) => ({
        domain: "select",
        service: "select_option",
        data: { option },
    })),
    setTimeRequest: vi.fn((time: string) => ({
        domain: "time",
        service: "set_value",
        data: { time },
    })),
    setSwitchRequest: vi.fn((on: boolean) => ({
        domain: "switch",
        service: on ? "turn_on" : "turn_off",
    })),
    controlLock: vi.fn(() => ({ locked: false, entity: null })),
    ControlTracker: class {
        constructor(
            readonly host?: unknown,
            readonly hassProvider?: () => unknown,
        ) {}

        readonly isBusy = vi.fn(() => false);
        readonly errorOf = vi.fn((): string | null => null);
        readonly submit = vi.fn(() => Promise.resolve());
    },
    CONTROL_ALLOWED_KEY: "control_allowed",
});

export const systemCardModule = async () => {
    const { LitElement, html, nothing } = await import("lit");
    const { ControlTracker } = controlModule();
    abstract class SystemCard extends LitElement {
        static properties = {
            hass: { attribute: false },
            config: { attribute: false, state: true },
            context: { attribute: false },
        };

        declare hass: Hass | undefined;
        declare config: Record<string, unknown> | undefined;
        declare context: unknown;
        protected abstract readonly cardRows: number;
        protected abstract shownEntities(entities: unknown): unknown[];
        protected abstract renderBody(context: unknown): unknown;
        protected emptyMessage?(context: unknown): string;
        readonly tracker = new ControlTracker(this, () => this.hass);
        protected readonly hasControls: boolean = false;
        protected readonly entityKindKey: string = "entity_kind_reading";

        setConfig(config: Record<string, unknown>): void {
            this.config = config;
        }

        getCardSize(): number {
            return this.cardRows;
        }

        getGridOptions(): { columns: number; min_columns: number } {
            return { columns: 12, min_columns: 6 };
        }

        protected get text(): typeof fakeText {
            return fakeText;
        }

        protected nameOf({ entity }: { entity: { key: string } }): string {
            return `name(${entity.key})`;
        }

        protected valueText({
            entity,
            absolute = false,
        }: {
            entity: { key: string };
            absolute?: boolean;
        }): string {
            return `value(${entity.key}${absolute ? ",absolute" : ""})`;
        }

        protected valueRow(options: {
            context: { dimmed: boolean };
            entity: { key: string; entityId: string };
            icon?: string;
            tone?: string;
            absolute?: boolean;
            label?: string;
            value?: string;
        }) {
            const { entity } = options;
            return html`<saj-value-row
                .label=${options.label ?? this.nameOf({ entity })}
                .value=${
                    options.value ??
                    this.valueText({ entity, absolute: options.absolute })
                }
                .icon=${options.icon}
                .tone=${options.tone}
                .entityId=${entity.entityId}
                .dimmed=${options.context.dimmed}
            ></saj-value-row>`;
        }

        protected renderEmpty(context: { lock: { locked: boolean } }) {
            const message = this.emptyMessage?.(context);
            return html`<saj-empty-state
                .locked=${this.hasControls && context.lock.locked}
                .kind=${this.entityKindKey}
                .message=${message ?? ""}
            ></saj-empty-state>`;
        }

        protected renderLockedBanner(context: { lock: { locked: boolean } }) {
            return context.lock.locked
                ? html`<saj-empty-state .locked=${true}></saj-empty-state>`
                : nothing;
        }

        protected dimmedBody({
            context,
            content,
        }: {
            context: { dimmed: boolean };
            content: unknown;
        }) {
            return html`<div class=${context.dimmed ? "dimmed" : "bright"}>
                ${content}
            </div>`;
        }

        protected render() {
            const { context } = this;
            if (context === undefined) {
                return nothing;
            }
            const { entities } = context as { entities: unknown };
            return this.shownEntities(entities).length === 0
                ? this.renderEmpty(context as { lock: { locked: boolean } })
                : this.renderBody(context);
        }
    }
    return {
        SystemCard,
        GRID_COLUMNS: 12,
        MINIMUM_GRID_COLUMNS: 6,
        presentEntities: ({
            entities,
            keys,
        }: {
            entities: ReadonlyMap<string, unknown>;
            keys: readonly string[];
        }) => keys.flatMap((key) => entities.get(key) ?? []),
        multiSelectField: vi.fn(
            ({ name, options }: { name: string; options: unknown[] }) => ({
                kind: "multi",
                name,
                options,
            }),
        ),
    };
};

export const redrawingDevices = new Set<string>();

export const systemElementModule = async () => {
    const { LitElement } = await import("lit");
    abstract class SystemElement extends LitElement {
        static properties = { hass: { attribute: false } };
        declare hass: Hass | undefined;
        protected abstract watchedDeviceId(): string | undefined;

        protected override shouldUpdate(
            changed: Map<string, unknown>,
        ): boolean {
            const watched = this.watchedDeviceId();
            const onlyHassChanged =
                changed.size === 1 && changed.get("hass") !== undefined;
            return (
                !onlyHassChanged ||
                (watched !== undefined && redrawingDevices.has(watched))
            );
        }

        protected get text(): typeof fakeText {
            return fakeText;
        }
    }
    return { SystemElement };
};

export const scheduleModule = () => ({
    APPLICATION_MODE_KEY: "application_mode",
    MINUTES_PER_DAY: 1440,
    SLOT_KINDS: ["charge", "discharge", "ev_charger"],
    scheduleOf: vi.fn(() => ({ slots: [], leftOut: 0 })),
    timelineBars: vi.fn(() => []),
    timeOfUseNoticeRequired: vi.fn(() => false),
});

export const weekdaysModule = () => ({
    toggleDay: ({ value, day }: { value: number; day: number }) =>
        value ^ (1 << day),
    daysOfNumber: (value: number) =>
        [0, 1, 2, 3, 4, 5, 6].filter((day) => (value >> day) % 2 === 1),
    weekdayName: ({
        day,
        language,
        width,
    }: {
        day: number;
        language: string;
        width: string;
    }) => `${width}:${String(day)}:${language}`,
    weekOrder: vi.fn(() => [0, 1, 2, 3, 4, 5, 6]),
});
