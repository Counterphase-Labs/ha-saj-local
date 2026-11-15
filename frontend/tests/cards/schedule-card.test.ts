import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { entitiesModule } from "../fakes/entities";
import {
    controlModule,
    editorModule,
    entityControlsModule,
    registrationModule,
    scheduleModule,
    stylesModule,
    systemCardModule,
    weekdaysModule,
} from "../fakes/modules";

import { SajChargeScheduleCard } from "../../src/cards/charge-schedule-card";
import { SajDischargeScheduleCard } from "../../src/cards/discharge-schedule-card";
import { SajEvChargerScheduleCard } from "../../src/cards/ev-charger-schedule-card";
import type { SajScheduleCard } from "../../src/cards/schedule-card";
import { setNumberRequest } from "../../src/system/control";
import { isUnavailable, systemEntities } from "../../src/system/entities";
import {
    scheduleOf,
    timelineBars,
    timelineOverlaps,
    timeOfUseNoticeRequired,
    type OverlapPart,
    type SlotKind,
    type TimelineBar,
} from "../../src/system/schedule";
import { weekOrder } from "../../src/system/weekdays";
import { entity, entityMap } from "../fakes/entities";
import { fakeSlot } from "../fakes/slots";
import {
    elementsIn,
    firstIn,
    mountCard,
    type CardUnderTest,
    controlStubsIn,
    type ControlStub,
    describeCardPicker,
} from "./support";
import { resultOf, trackerMocks } from "../fakes/mocks";

vi.mock("../../src/registration", () => registrationModule());
vi.mock("../../src/system/control", () => controlModule());
vi.mock("../../src/system/entities", () => entitiesModule());
vi.mock("../../src/system/schedule", () => scheduleModule());
vi.mock("../../src/system/weekdays", () => weekdaysModule());
vi.mock("../../src/cards/entity-controls", () => entityControlsModule());
vi.mock("../../src/ui/icon", () => ({}));
vi.mock("../../src/ui/weekday-buttons", () => ({}));
vi.mock("../../src/ui/styles", () => stylesModule());
vi.mock("../../src/cards/editor", () => editorModule());
vi.mock("../../src/cards/system-card", () => systemCardModule());

const TAG = "saj-local-charge-schedule-card";

const CARDS: {
    kind: SlotKind;
    tag: string;
    card: Pick<typeof SajScheduleCard, "getConfigForm" | "getStubConfig">;
}[] = [
    { kind: "charge", tag: TAG, card: SajChargeScheduleCard },
    {
        kind: "discharge",
        tag: "saj-local-discharge-schedule-card",
        card: SajDischargeScheduleCard,
    },
    {
        kind: "ev_charger",
        tag: "saj-local-ev-charger-schedule-card",
        card: SajEvChargerScheduleCard,
    },
];

for (const { tag, card } of CARDS) {
    describeCardPicker({ tag, card });
}

describe("schedule card types", () => {
    it("does not register the removed schedule card type", () => {
        expect(customElements.get("saj-local-schedule-card")).toBeUndefined();
    });

    it.each(CARDS)(
        "$tag asks for the slots of its own kind only and heads them with the kind name",
        async ({ kind, tag }) => {
            plan([fakeSlot({ kind, number: 1 })]);

            const card = await mountCard({
                tag,
                entities: [entity("buzzer", "switch", "on")],
            });

            expect(vi.mocked(scheduleOf).mock.calls.at(-1)?.[0].kinds).toEqual([
                kind,
            ]);
            expect(firstIn(card, "h3").textContent).toBe(`option_kind_${kind}`);
        },
    );

    it.each(CARDS)(
        "$tag offers the system and the timeline switch, with no slot kinds option",
        ({ card }) => {
            expect(card.getConfigForm()).toEqual({
                fields: [
                    { kind: "boolean", name: "show_timeline", fallback: true },
                ],
            });
        },
    );
});

const charge = fakeSlot({ kind: "charge", number: 1 });
const ev = fakeSlot({ kind: "ev_charger", number: 1 });

const plan = (slots = [charge], leftOut = 0): void => {
    vi.mocked(scheduleOf).mockReturnValue({ slots, leftOut });
};

const mountSchedule = (
    options: {
        config?: Record<string, unknown>;
        dimmed?: boolean;
        locked?: boolean;
    } = {},
) =>
    mountCard({
        tag: TAG,
        entities: [entity("buzzer", "switch", "on")],
        ...options,
    });

const summaries = (card: CardUnderTest): HTMLButtonElement[] => [
    ...(card.shadowRoot?.querySelectorAll<HTMLButtonElement>(".summary") ?? []),
];

const expandAll = async (card: CardUnderTest): Promise<void> => {
    for (const button of summaries(card)) {
        button.click();
    }
    await card.updateComplete;
};

const barOf = (overrides: Partial<TimelineBar> = {}): TimelineBar => ({
    day: 0,
    startMinute: 360,
    endMinute: 720,
    slot: charge,
    disabled: false,
    continuation: false,
    ...overrides,
});

const overlapOf = (overrides: Partial<OverlapPart> = {}): OverlapPart => ({
    day: 0,
    startMinute: 360,
    endMinute: 720,
    slots: [
        fakeSlot({ kind: "charge", number: 1 }),
        fakeSlot({ kind: "charge", number: 2 }),
    ],
    ...overrides,
});

beforeEach(() => {
    plan([charge]);
    vi.mocked(timelineBars).mockReturnValue([]);
    vi.mocked(timelineOverlaps).mockReturnValue([]);
    vi.mocked(timeOfUseNoticeRequired).mockReturnValue(false);
});

afterEach(() => {
    document.body.replaceChildren();
});

describe("schedule cards slots", () => {
    it("draws one row per slot with its number, times, days and power", async () => {
        plan([
            fakeSlot({ kind: "charge", number: 1, days: "5" }),
            fakeSlot({ kind: "ev_charger", number: 2 }),
        ]);

        const card = await mountSchedule();
        const [first] = summaries(card);

        expect(summaries(card)).toHaveLength(2);
        expect(first?.textContent).toContain('slot_number:{"number":1}');
        expect(first?.textContent).toContain("08:00:00");
        expect(first?.textContent).toContain("10:30:00");
        expect(first?.textContent).toContain("short:0:en short:2:en");
        expect(first?.textContent).toContain("1000");
    });

    it("lists the days in the order of the user's week", async () => {
        plan([fakeSlot({ kind: "charge", number: 1, days: "5" })]);
        vi.mocked(weekOrder).mockReturnValue([6, 5, 4, 3, 2, 1, 0]);

        const card = await mountSchedule();

        expect(summaries(card)[0]?.textContent).toContain(
            "short:2:en short:0:en",
        );
    });

    it("shows a slot with no readable days as having none", async () => {
        plan([fakeSlot({ kind: "charge", number: 1, days: "unavailable" })]);

        const card = await mountSchedule();

        expect(summaries(card)[0]?.textContent).not.toContain("short:");
    });

    it("draws an enable switch for the slots that have one and none for the others", async () => {
        plan([charge, ev]);

        const card = await mountSchedule();
        const switches = controlStubsIn(card, ".slot-header saj-control-stub");

        expect(switches.map((control) => control.entityKey)).toEqual([
            "charge_slot_1_enabled",
        ]);
        expect(switches[0]?.labelHidden).toBe(true);
    });

    it("gives a colour mark to each slot row, a different one for each slot number", async () => {
        plan([
            fakeSlot({ kind: "charge", number: 1 }),
            fakeSlot({ kind: "charge", number: 2 }),
        ]);

        const card = await mountSchedule();
        const colours = elementsIn(card, ".summary .colour-mark").map((mark) =>
            mark.style.getPropertyValue("--mark-colour"),
        );

        expect(colours).toEqual(["colour-1", "colour-2"]);
        expect(
            elementsIn(card, ".colour-mark").every(
                (mark) => mark.getAttribute("aria-hidden") === "true",
            ),
        ).toBe(true);
    });

    it("keeps the colour of a slot number whatever the other slots are", async () => {
        const colourOfSlotTwo = async (
            slots: ReturnType<typeof fakeSlot>[],
        ) => {
            plan(slots);
            const card = await mountSchedule();
            return elementsIn(card, ".colour-mark")
                .find((mark) =>
                    mark
                        .closest(".summary")
                        ?.textContent.includes('"number":2'),
                )
                ?.style.getPropertyValue("--mark-colour");
        };
        const two = fakeSlot({ kind: "charge", number: 2 });

        expect(await colourOfSlotTwo([two])).toBe(
            await colourOfSlotTwo([
                fakeSlot({ kind: "charge", number: 1 }),
                two,
                fakeSlot({ kind: "charge", number: 5 }),
            ]),
        );
    });

    it("shows the colour mark of a slot that has no bars", async () => {
        plan([fakeSlot({ kind: "charge", number: 3, start: "unavailable" })]);

        const card = await mountSchedule();

        expect(
            firstIn(card, ".colour-mark").style.getPropertyValue(
                "--mark-colour",
            ),
        ).toBe("colour-3");
        expect(elementsIn(card, ".bar")).toHaveLength(0);
    });

    it("counts the slots left out under the list", async () => {
        plan([charge], 2);

        const card = await mountSchedule();

        expect(firstIn(card, ".left-out").textContent.trim()).toBe(
            'slots_left_out:{"count":2}',
        );
    });

    it("draws no left-out count when every slot is complete", async () => {
        const card = await mountSchedule();

        expect(elementsIn(card, ".left-out")).toHaveLength(0);
    });

    it("works the schedule out once for a redraw, whatever the parts that need it", async () => {
        plan([charge], 1);

        await mountSchedule();

        expect(scheduleOf).toHaveBeenCalledTimes(1);
    });

    it("does not work the schedule out again for a redraw with the same entities", async () => {
        plan([charge]);
        const card = await mountSchedule();
        vi.mocked(scheduleOf).mockClear();

        await expandAll(card);

        expect(scheduleOf).not.toHaveBeenCalled();
    });

    it("works the schedule out again for new entities", async () => {
        plan([charge]);
        const card = await mountSchedule();
        vi.mocked(scheduleOf).mockClear();

        card.context = {
            ...(card.context as object),
            entities: entityMap([entity("buzzer", "switch", "off")]),
        };
        await card.updateComplete;

        expect(scheduleOf).toHaveBeenCalledTimes(1);
    });
});

describe("schedule cards empty and locked states", () => {
    it("says how many slots were left out when none is drawn", async () => {
        plan([], 1);

        const card = await mountSchedule();

        expect(firstIn(card, "saj-empty-state")).toMatchObject({
            message: 'slots_left_out:{"count":1}',
            kind: "entity_kind_schedule",
            locked: false,
        });
    });

    it("names the entity kind when there is no slot at all", async () => {
        plan([], 0);

        const card = await mountSchedule();

        expect(firstIn(card, "saj-empty-state").message).toBe("");
    });

    it("shows the locked message in place of the empty state while changes are off", async () => {
        plan([], 0);

        const card = await mountSchedule({ locked: true });

        expect(firstIn(card, "saj-empty-state")).toMatchObject({
            locked: true,
        });
    });

    it("shows the locked message above the slots while changes are off", async () => {
        const card = await mountSchedule({ locked: true });

        expect(card.shadowRoot?.querySelector("saj-empty-state")).toMatchObject(
            {
                locked: true,
            },
        );
    });

    it("dims the slots while the card is dimmed", async () => {
        const dimmed = await mountSchedule({ dimmed: true });
        const bright = await mountSchedule();

        expect(firstIn(dimmed, ".dimmed")).toBeDefined();
        expect(bright.shadowRoot?.querySelector(".dimmed")).toBeNull();
    });
});

describe("schedule cards timeline", () => {
    it("draws seven days in the order of the user's week with a bar for each bar it is given", async () => {
        vi.mocked(weekOrder).mockReturnValue([6, 0, 1, 2, 3, 4, 5]);
        vi.mocked(timelineBars).mockReturnValue([
            barOf({ day: 0 }),
            barOf({ day: 2 }),
        ]);

        const card = await mountSchedule();
        const days = elementsIn(card, ".day");

        expect(days).toHaveLength(7);
        expect(days[0]?.querySelector(".day-name")?.textContent).toBe(
            "short:6:en",
        );
        expect(elementsIn(card, ".bar")).toHaveLength(2);
        expect(
            elementsIn(card, ".track")[1]?.querySelectorAll(".bar"),
        ).toHaveLength(1);
    });

    it("places each bar by its minutes of the day", async () => {
        vi.mocked(timelineBars).mockReturnValue([
            barOf({ startMinute: 360, endMinute: 720 }),
        ]);

        const card = await mountSchedule();
        const style = firstIn(card, ".bar").getAttribute("style");

        expect(style).toContain("left:25%");
        expect(style).toContain("width:25%");
    });

    it("draws the timeline from the slots shown", async () => {
        await mountSchedule();

        expect(timelineBars).toHaveBeenCalledWith([charge]);
    });

    it("draws the bar of a switched-off slot as an outline in the colour of the slot", async () => {
        vi.mocked(timelineBars).mockReturnValue([
            barOf({
                disabled: true,
                slot: fakeSlot({ kind: "charge", number: 2 }),
            }),
            barOf({ day: 1 }),
        ]);

        const card = await mountSchedule();

        const outlines = elementsIn(card, ".bar.disabled");
        expect(outlines).toHaveLength(1);
        expect(outlines[0]?.style.getPropertyValue("--bar-colour")).toBe(
            "colour-2",
        );
    });

    it("draws switched-on bars after outlines so that the bars hide the outlines", async () => {
        vi.mocked(timelineBars).mockReturnValue([
            barOf({ slot: fakeSlot({ kind: "charge", number: 1 }) }),
            barOf({
                disabled: true,
                slot: fakeSlot({ kind: "charge", number: 2 }),
            }),
        ]);

        const card = await mountSchedule();

        expect(
            elementsIn(card, ".bar").map((bar) =>
                bar.classList.contains("disabled"),
            ),
        ).toEqual([true, false]);
    });

    it("names each bar for assistive technology", async () => {
        vi.mocked(timelineBars).mockReturnValue([barOf()]);

        const card = await mountSchedule();

        expect(firstIn(card, ".bar").getAttribute("aria-label")).toBe(
            'option_kind_charge slot_number:{"number":1}',
        );
    });

    it("opens a slot in the list when its bar is tapped, and keeps it open when tapped again", async () => {
        vi.mocked(timelineBars).mockReturnValue([barOf()]);
        const card = await mountSchedule();

        firstIn(card, ".bar").click();
        await card.updateComplete;
        firstIn(card, ".bar").click();
        await card.updateComplete;

        expect(summaries(card)[0]?.getAttribute("aria-expanded")).toBe("true");
        expect(elementsIn(card, ".editor")).toHaveLength(1);
    });

    it("draws each bar in the colour of its slot number", async () => {
        vi.mocked(timelineBars).mockReturnValue([
            barOf({ slot: fakeSlot({ kind: "charge", number: 1 }) }),
            barOf({
                day: 1,
                slot: fakeSlot({ kind: "charge", number: 2 }),
            }),
        ]);

        const card = await mountSchedule();

        expect(
            elementsIn(card, ".bar").map((bar) =>
                bar.style.getPropertyValue("--bar-colour"),
            ),
        ).toEqual(["colour-1", "colour-2"]);
    });

    it("draws each overlap above the bars, in its own day, hidden from assistive technology", async () => {
        const bars = [barOf()];
        vi.mocked(timelineBars).mockReturnValue(bars);
        vi.mocked(timelineOverlaps).mockReturnValue([
            overlapOf({ day: 2, startMinute: 360, endMinute: 720 }),
        ]);

        const card = await mountSchedule();
        const overlap = firstIn(card, ".overlap");

        expect(timelineOverlaps).toHaveBeenCalledWith(bars);
        expect(
            overlap.closest(".day")?.querySelector(".day-name")?.textContent,
        ).toBe("short:2:en");
        expect(overlap.getAttribute("aria-hidden")).toBe("true");
        expect(overlap.getAttribute("style")).toContain("left:25%");
        expect(overlap.getAttribute("style")).toContain("width:25%");
    });

    it("stripes an overlap with the colours of its slots in slot number order", async () => {
        vi.mocked(timelineOverlaps).mockReturnValue([overlapOf({})]);

        const card = await mountSchedule();
        const style = firstIn(card, ".overlap").getAttribute("style") ?? "";

        expect(style.indexOf("colour-1")).toBeGreaterThan(-1);
        expect(style.indexOf("colour-2")).toBeGreaterThan(
            style.indexOf("colour-1"),
        );
    });

    it("opens the overlapping slot with the lowest slot number when an overlap is tapped", async () => {
        plan([
            fakeSlot({ kind: "charge", number: 1 }),
            fakeSlot({ kind: "charge", number: 2 }),
        ]);
        vi.mocked(timelineOverlaps).mockReturnValue([overlapOf({})]);
        const card = await mountSchedule();

        firstIn(card, ".overlap").click();
        await card.updateComplete;

        expect(
            summaries(card).map((button) =>
                button.getAttribute("aria-expanded"),
            ),
        ).toEqual(["true", "false"]);
    });

    it("draws no overlap without overlap parts", async () => {
        const card = await mountSchedule();

        expect(elementsIn(card, ".overlap")).toHaveLength(0);
    });

    it("leaves the timeline out when switched off", async () => {
        const card = await mountSchedule({ config: { show_timeline: false } });

        expect(elementsIn(card, ".timeline")).toHaveLength(0);
        expect(timelineBars).not.toHaveBeenCalled();
    });
});

describe("schedule cards editor", () => {
    it("reveals the editor on expand and hides it again", async () => {
        const card = await mountSchedule();

        expect(elementsIn(card, ".editor")).toHaveLength(0);

        await expandAll(card);

        expect(elementsIn(card, ".editor")).toHaveLength(1);
        expect(summaries(card)[0]?.getAttribute("aria-expanded")).toBe("true");

        await expandAll(card);

        expect(elementsIn(card, ".editor")).toHaveLength(0);
    });

    it("holds the start, end and power controls and the weekday buttons", async () => {
        const card = await mountSchedule();
        await expandAll(card);

        expect(
            controlStubsIn(card, ".editor saj-control-stub").map(
                (control) => control.entityKey,
            ),
        ).toEqual([
            "charge_slot_1_start",
            "charge_slot_1_end",
            "charge_slot_1_power",
        ]);
        expect(elementsIn(card, ".editor saj-weekday-buttons")).toHaveLength(1);
    });

    it("adds the mode select and the two switches to an EV slot only", async () => {
        plan([charge, ev]);
        const card = await mountSchedule();
        await expandAll(card);
        const [chargeEditor, evEditor] = elementsIn(card, ".editor");
        const keysIn = (editor: Element | undefined) =>
            [...(editor?.querySelectorAll("saj-control-stub") ?? [])].map(
                (control) => control.entityKey,
            );

        expect(keysIn(chargeEditor)).toHaveLength(3);
        expect(keysIn(evEditor)).toEqual([
            "ev_slot_1_start",
            "ev_slot_1_end",
            "ev_slot_1_power",
            "ev_slot_1_mode",
            "ev_slot_1_grid_charging",
            "ev_slot_1_battery_discharge",
        ]);
    });

    it("gives the weekday buttons the slot's number and writes it once the buttons commit", async () => {
        const card = await mountSchedule();
        await expandAll(card);
        const weekdays = firstIn(card, "saj-weekday-buttons");

        weekdays.dispatchEvent(new CustomEvent("saj-commit", { detail: 21 }));

        expect(weekdays.value).toBe(5);
        expect(setNumberRequest).toHaveBeenCalledWith(21);
        expect(trackerMocks(card.tracker).submit).toHaveBeenCalledWith({
            entityId: charge.days.entityId,
            request: resultOf(setNumberRequest),
        });
    });

    it("disables the weekday buttons while changes are off", async () => {
        const locked = await mountSchedule({ locked: true });
        await expandAll(locked);

        expect(firstIn(locked, "saj-weekday-buttons").disabled).toBe(true);
    });

    it("disables the weekday buttons while the slot's weekdays are unavailable", async () => {
        plan([fakeSlot({ kind: "charge", number: 1, days: "unavailable" })]);
        vi.mocked(isUnavailable).mockImplementation(
            (item) => item.state.state === "unavailable",
        );
        const card = await mountSchedule();
        await expandAll(card);

        expect(firstIn(card, "saj-weekday-buttons").disabled).toBe(true);
    });

    it("keeps the weekday buttons enabled otherwise", async () => {
        const card = await mountSchedule();
        await expandAll(card);

        expect(firstIn(card, "saj-weekday-buttons").disabled).toBe(false);
    });

    it("shows the busy state and the refusal of the weekday write under the weekday buttons", async () => {
        const card = await mountSchedule();
        trackerMocks(card.tracker).isBusy.mockReturnValue(true);
        trackerMocks(card.tracker).errorOf.mockReturnValue("Refused");
        await expandAll(card);
        const weekdays = firstIn(card, "saj-weekday-buttons");

        expect(trackerMocks(card.tracker).isBusy).toHaveBeenCalledWith(
            charge.days.entityId,
        );
        expect(weekdays.busy).toBe(true);
        expect(weekdays.error).toBe("Refused");
    });

    it("shows no refusal when the weekday write was not refused", async () => {
        const card = await mountSchedule();
        await expandAll(card);

        expect(firstIn(card, "saj-weekday-buttons").error).toBe("");
    });
});

describe("schedule cards time-of-use notice", () => {
    const mode = entity("application_mode", "select", "backup");

    const mountWithMode = (required: boolean) => {
        vi.mocked(timeOfUseNoticeRequired).mockReturnValue(required);
        return mountCard({ tag: TAG, entities: [mode] });
    };

    it("shows the notice with the application mode control beside it when the schedule requires it", async () => {
        const card = await mountWithMode(true);
        const notice = firstIn(card, "saj-notice");

        expect(notice).toMatchObject({ message: "time_of_use_notice" });
        expect(notice.getAttribute("tone")).toBe("warning");
        expect(
            notice.querySelector<ControlStub>("saj-control-stub")?.entityKey,
        ).toBe("application_mode");
        expect(
            notice.querySelector<ControlStub>("saj-control-stub")?.labelHidden,
        ).toBe(true);
    });

    it("asks the schedule logic with the system's entities and the slots shown", async () => {
        await mountWithMode(true);

        expect(timeOfUseNoticeRequired).toHaveBeenCalledWith({
            entities: entityMap([mode]),
            slots: [charge],
        });
    });

    it("shows no notice when the schedule does not require it", async () => {
        const card = await mountWithMode(false);

        expect(elementsIn(card, "saj-notice")).toHaveLength(0);
    });

    it("shows no notice without an application mode entity, whatever the schedule says", async () => {
        vi.mocked(timeOfUseNoticeRequired).mockReturnValue(true);
        const card = await mountSchedule();

        expect(elementsIn(card, "saj-notice")).toHaveLength(0);
    });
});

describe("schedule cards contracts", () => {
    it("shows the entities of every slot", async () => {
        plan([charge, ev]);
        const card = await mountSchedule();

        expect(card.shownEntities(entityMap([]))).toEqual([
            charge.start,
            charge.end,
            charge.days,
            charge.power,
            charge.enabled,
            ev.start,
            ev.end,
            ev.days,
            ev.power,
            ev.mode,
            ev.gridCharging,
            ev.batteryDischarge,
        ]);
    });
});

describe("schedule cards size", () => {
    beforeEach(() => {
        vi.mocked(systemEntities).mockReturnValue(entityMap([]));
    });

    it("is one before it has hass or a system", async () => {
        const noDevice = await mountCard({
            tag: TAG,
            config: { device: undefined },
        });

        expect(noDevice.getCardSize()).toBe(1);
    });

    it("grows with the slots and the timeline", async () => {
        plan([charge, ev]);
        const withTimeline = await mountSchedule();
        const without = await mountSchedule({
            config: { show_timeline: false },
        });

        expect(withTimeline.getCardSize()).toBeGreaterThan(
            without.getCardSize(),
        );
        expect(systemEntities).toHaveBeenCalled();
        expect(without.getCardSize()).toBeGreaterThan(1);
    });
});
