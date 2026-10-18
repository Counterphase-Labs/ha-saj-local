import { html, type TemplateResult } from "lit";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { entitiesModule } from "../fakes/entities";
import { controlModule, systemElementModule } from "../fakes/modules";

import {
    multiSelectField,
    presentEntities,
    SystemCard,
    type CardContext,
} from "../../src/cards/system-card";
import type { SajElementConfig } from "../../src/hass";
import { controlLock } from "../../src/system/control";
import {
    allUnavailable,
    isUnavailable,
    numericValue,
    systemEntities,
    type SystemEntities,
    type SystemEntity,
} from "../../src/system/entities";
import { systemTitle } from "../../src/system/title";
import { entity, entityMap } from "../fakes/entities";
import { createFakeHass } from "../fakes/hass";
import { mount } from "../ui/mount";

vi.mock("../../src/system/control", () => controlModule());
vi.mock("../../src/system/entities", () => entitiesModule());
vi.mock("../../src/system/title", () => ({
    systemTitle: vi.fn(() => "System title"),
}));
vi.mock("../../src/ui/system-element", () => systemElementModule());
vi.mock("../../src/ui/card-container", () => ({}));
vi.mock("../../src/ui/empty-state", () => ({}));
vi.mock("../../src/ui/notice", () => ({}));
vi.mock("../../src/ui/value-row", () => ({}));

const shown = vi.hoisted((): { entities: unknown[] } => ({ entities: [] }));
const calls = vi.hoisted((): { context: unknown } => ({
    context: undefined,
}));

class ProbeCard extends SystemCard<SajElementConfig> {
    protected readonly cardRows = 3;
    protected override readonly hasControls = true;
    protected override readonly entityKindKey = "entity_kind_probe";
    withMessage = false;

    protected override shownEntities(): SystemEntity[] {
        return shown.entities as SystemEntity[];
    }

    protected override emptyMessage(): string {
        return this.withMessage ? "custom message" : "";
    }

    protected override renderBody(context: CardContext): TemplateResult {
        calls.context = context;
        return html`<div id="body">
            ${this.valueRow({
                context,
                entity: entity("pv_power", "sensor", "100"),
                icon: "solar",
                tone: "primary",
            })}
            ${this.renderLockedBanner(context)}
            ${this.dimmedBody({ context, content: html`<b>inside</b>` })}
        </div>`;
    }

    callNameOf(context: CardContext, target: SystemEntity): string {
        return this.nameOf({ context, entity: target });
    }

    callValueText(
        context: CardContext,
        target: SystemEntity,
        absolute?: boolean,
    ): string {
        return this.valueText({ context, entity: target, absolute });
    }

    watched(): string | undefined {
        return this.watchedDeviceId();
    }

    get controlTracker(): CardContext["tracker"] {
        return this.tracker;
    }
}
customElements.define("probe-card", ProbeCard);

class PlainCard extends SystemCard<SajElementConfig> {
    protected readonly cardRows = 1;

    protected override shownEntities(): SystemEntity[] {
        return [];
    }

    protected override renderBody(): TemplateResult {
        return html``;
    }
}
customElements.define("plain-card", PlainCard);

const hass = Object.assign(createFakeHass(), {
    formatEntityName: vi.fn(() => "Name"),
    formatEntityState: vi.fn(
        (_state: unknown, override?: string) =>
            `formatted(${override ?? "state"})`,
    ),
});

const pvPower = entity("pv_power", "sensor", "100");

const mountProbe = async (
    config: Partial<SajElementConfig> | null = {
        type: "probe",
        device: "saj_1",
    },
): Promise<ProbeCard> => {
    const card = await mount<ProbeCard>("probe-card");
    card.hass = hass;
    if (config !== null) {
        card.setConfig(config as SajElementConfig);
    }
    await card.updateComplete;
    return card;
};

function inCard<Tag extends keyof HTMLElementTagNameMap>(
    card: ProbeCard,
    selector: Tag,
): HTMLElementTagNameMap[Tag] | null;
function inCard(card: ProbeCard, selector: string): Element | null;
function inCard(card: ProbeCard, selector: string): Element | null {
    return card.shadowRoot?.querySelector(selector) ?? null;
}

const contextOf = (overrides: Partial<CardContext> = {}): CardContext => ({
    hass,
    deviceId: "saj_1",
    entities: entityMap([]),
    lock: { locked: false, entity: null },
    tracker: {} as never,
    dimmed: false,
    ...overrides,
});

beforeEach(() => {
    shown.entities = [pvPower];
    calls.context = undefined;
    vi.mocked(systemEntities).mockReturnValue(entityMap([pvPower]));
    vi.mocked(allUnavailable).mockReturnValue(false);
    vi.mocked(controlLock).mockReturnValue({ locked: false, entity: null });
});

afterEach(() => {
    document.body.replaceChildren();
    vi.mocked(allUnavailable).mockReset();
    vi.mocked(systemEntities).mockReset();
});

describe("presentEntities", () => {
    it("returns the entities that exist, in the order of the keys", () => {
        const first = entity("a", "sensor", "1");
        const second = entity("b", "sensor", "2");

        expect(
            presentEntities({
                entities: entityMap([second, first]),
                keys: ["b", "missing", "a"],
            }),
        ).toEqual([second, first]);
    });
});

describe("multiSelectField", () => {
    it("offers a list of options that can be chosen several at a time, all chosen by default", () => {
        const options = [
            { value: "a", label: "A" },
            { value: "b", label: "B" },
        ];

        expect(multiSelectField({ name: "kinds", options })).toEqual({
            name: "kinds",
            default: ["a", "b"],
            selector: { select: { options, multiple: true, mode: "list" } },
        });
    });
});

describe("SystemCard contract", () => {
    it("reports its size and a grid that can shrink", async () => {
        const card = await mountProbe();
        const options = card.getGridOptions();

        expect(card.getCardSize()).toBe(3);
        expect(options.min_columns).toBeLessThan(options.columns);
    });

    it("lets its tracker call services with the card's current hass and refresh the card", async () => {
        const card = await mountProbe();
        const provider: unknown = Reflect.get(
            card.controlTracker,
            "hassProvider",
        );

        expect(card.controlTracker).toMatchObject({ host: card });
        if (typeof provider !== "function") {
            throw new Error("The tracker has no hass provider");
        }
        expect(Reflect.apply(provider, undefined, [])).toBe(hass);
    });

    it("watches the device it is configured for", async () => {
        const card = await mountProbe();

        expect(card.watched()).toBe("saj_1");
    });

    it("watches nothing before it is configured", async () => {
        const card = await mountProbe(null);

        expect(card.watched()).toBeUndefined();
    });
});

describe("SystemCard drawing", () => {
    it("draws nothing before it has hass and a configuration", async () => {
        const withoutConfig = await mountProbe(null);
        const withoutHass = await mount<ProbeCard>("probe-card");
        withoutHass.setConfig({ type: "probe", device: "saj_1" });
        await withoutHass.updateComplete;

        expect(inCard(withoutConfig, "saj-card")).toBeNull();
        expect(inCard(withoutHass, "saj-card")).toBeNull();
    });

    it("asks for a system when no device is chosen", async () => {
        const card = await mountProbe({ type: "probe" });

        expect(inCard(card, "saj-notice")?.message).toBe("choose_system");
        expect(systemEntities).not.toHaveBeenCalled();
    });

    it("asks for a system when the device has no SAJ Local entity", async () => {
        vi.mocked(systemEntities).mockReturnValue(entityMap([]));

        const card = await mountProbe();

        expect(inCard(card, "saj-notice")?.message).toBe("choose_system");
        expect(inCard(card, "#body")).toBeNull();
    });

    it("titles the card with the system title", async () => {
        const card = await mountProbe();

        expect(systemTitle).toHaveBeenCalledWith({ hass, deviceId: "saj_1" });
        expect(inCard(card, "saj-card")?.heading).toBe("System title");
    });

    it("gives the body the entities, the lock, the tracker and the device", async () => {
        const lock = { locked: true, entity: null };
        vi.mocked(controlLock).mockReturnValue(lock);

        const card = await mountProbe();

        expect(calls.context).toMatchObject({
            hass,
            deviceId: "saj_1",
            lock,
            tracker: card.controlTracker,
            dimmed: false,
        });
        expect(
            (calls.context as { entities: SystemEntities }).entities.get(
                "pv_power",
            ),
        ).toBe(pvPower);
    });

    it("says it is not answering and dims the body while everything it shows is unavailable", async () => {
        vi.mocked(allUnavailable).mockReturnValue(true);

        const card = await mountProbe();

        expect(allUnavailable).toHaveBeenCalledWith(shown.entities);
        expect(inCard(card, "saj-notice")?.message).toBe("not_answering");
        expect((calls.context as CardContext).dimmed).toBe(true);
    });

    it("says nothing about answering while something it shows answers", async () => {
        const card = await mountProbe();

        expect(inCard(card, "saj-notice")).toBeNull();
    });
});

describe("SystemCard empty state", () => {
    beforeEach(() => {
        shown.entities = [];
    });

    it("names the kind of entity to enable and links to the device", async () => {
        const card = await mountProbe();
        const empty = inCard(card, "saj-empty-state");

        expect(empty).toMatchObject({
            kind: "entity_kind_probe",
            deviceId: "saj_1",
            locked: false,
            message: "",
        });
        expect(inCard(card, "#body")).toBeNull();
    });

    it("passes the card's own message to the empty state", async () => {
        const card = await mount<ProbeCard>("probe-card");
        card.withMessage = true;
        card.hass = hass;
        card.setConfig({ type: "probe", device: "saj_1" });
        await card.updateComplete;

        expect(inCard(card, "saj-empty-state")?.message).toBe("custom message");
    });

    it("shows the locked message instead while changes are off and the card has controls", async () => {
        vi.mocked(controlLock).mockReturnValue({ locked: true, entity: null });

        const card = await mountProbe();

        expect(inCard(card, "saj-empty-state")?.locked).toBe(true);
    });
});

describe("SystemCard without controls or a message of its own", () => {
    it("shows the empty state with no message and never the locked message", async () => {
        vi.mocked(controlLock).mockReturnValue({ locked: true, entity: null });
        const card = await mount<PlainCard>("plain-card");
        card.hass = hass;
        card.setConfig({ type: "plain", device: "saj_1" });
        await card.updateComplete;

        expect(card.shadowRoot?.querySelector("saj-empty-state")).toMatchObject(
            { locked: false, message: "" },
        );
    });
});

describe("SystemCard helpers", () => {
    it("names an entity the way Home Assistant does", async () => {
        const card = await mountProbe();

        expect(card.callNameOf(contextOf(), pvPower)).toBe("Name");
        expect(hass.formatEntityName).toHaveBeenCalledWith(pvPower.state, [
            { type: "entity" },
        ]);
    });

    it("formats a value the way Home Assistant does", async () => {
        const card = await mountProbe();

        expect(card.callValueText(contextOf(), pvPower)).toBe(
            "formatted(state)",
        );
    });

    it("formats the absolute value of a number when asked", async () => {
        vi.mocked(numericValue).mockReturnValueOnce(-250);
        const card = await mountProbe();

        expect(card.callValueText(contextOf(), pvPower, true)).toBe(
            "formatted(250)",
        );
    });

    it("formats the state as it is when the absolute value is asked for but there is no number", async () => {
        vi.mocked(numericValue).mockReturnValueOnce(null);
        const card = await mountProbe();

        expect(card.callValueText(contextOf(), pvPower, true)).toBe(
            "formatted(state)",
        );
    });

    it("shows an unavailable entity as unavailable", async () => {
        const card = await mountProbe();
        vi.mocked(isUnavailable).mockReturnValueOnce(true);

        expect(card.callValueText(contextOf(), pvPower)).toBe("unavailable");
    });

    it("draws a value row with the name, value, icon, tone and entity, dimmed with the card", async () => {
        const card = await mountProbe();
        const row = inCard(card, "saj-value-row");

        expect(row).toMatchObject({
            label: "Name",
            value: "formatted(state)",
            icon: "solar",
            tone: "primary",
            entityId: pvPower.entityId,
            dimmed: false,
        });
    });

    it("draws the locked message only while changes are off", async () => {
        vi.mocked(controlLock).mockReturnValue({ locked: true, entity: null });
        const locked = await mountProbe();
        vi.mocked(controlLock).mockReturnValue({ locked: false, entity: null });
        const open = await mountProbe();

        expect(inCard(locked, "#body saj-empty-state")).not.toBeNull();
        expect(inCard(open, "#body saj-empty-state")).toBeNull();
    });

    it("dims the content of a dimmed body", async () => {
        vi.mocked(allUnavailable).mockReturnValue(true);
        const dimmed = await mountProbe();
        vi.mocked(allUnavailable).mockReturnValue(false);
        const bright = await mountProbe();

        expect(inCard(dimmed, "#body > div")?.getAttribute("style")).toContain(
            "opacity",
        );
        expect(inCard(bright, "#body > div")?.getAttribute("style")).toBe("");
    });
});
