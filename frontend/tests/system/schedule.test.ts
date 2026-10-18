import { describe, expect, it, vi } from "vitest";
import { entitiesModule } from "../fakes/entities";

import type { SystemEntity } from "../../src/system/entities";
import {
    minuteOfDay,
    MINUTES_PER_DAY,
    scheduleOf,
    SLOT_COUNT,
    slotEnabled,
    timelineBars,
    timeOfUseNoticeRequired,
    type Slot,
    type SlotKind,
} from "../../src/system/schedule";
import { entity, entityMap } from "../fakes/entities";
import { slotEntities } from "../fakes/slots";

vi.mock("../../src/system/entities", () => entitiesModule());
vi.mock("../../src/system/weekdays", () => ({ WEEKDAY_COUNT: 7 }));

const entitiesOf = (entities: SystemEntity[]) => entityMap(entities);

const firstSlot = (fakes: SystemEntity[], kind: SlotKind = "charge"): Slot => {
    const slot = scheduleOf({ entities: entitiesOf(fakes), kinds: [kind] })
        .slots[0];
    if (slot === undefined) {
        throw new Error("no slot built");
    }
    return slot;
};

describe("scheduleOf", () => {
    it("builds a slot only when every key exists", () => {
        const schedule = scheduleOf({
            entities: entitiesOf([
                ...slotEntities({ kind: "charge", number: 1 }),
                ...slotEntities({
                    kind: "charge",
                    number: 2,
                    skip: ["charge_slot_2_power"],
                }),
            ]),
            kinds: ["charge"],
        });

        expect(schedule.slots.map((slot) => slot.number)).toEqual([1]);
        expect(schedule.leftOut).toBe(1);
    });

    it.each(["start", "end", "days", "power", "enabled"])(
        "leaves out a slot whose %s entity is missing",
        (suffix) => {
            const schedule = scheduleOf({
                entities: entitiesOf(
                    slotEntities({
                        kind: "discharge",
                        number: 3,
                        skip: [`discharge_slot_3_${suffix}`],
                    }),
                ),
                kinds: ["discharge"],
            });

            expect(schedule.slots).toEqual([]);
            expect(schedule.leftOut).toBe(1);
        },
    );

    it("builds EV slots with their extra entities and no enable switch", () => {
        const slot = firstSlot(slotEntities({ kind: "ev", number: 1 }), "ev");

        expect(slot.enabled).toBeNull();
        expect(slot.mode?.key).toBe("ev_slot_1_mode");
        expect(slot.gridCharging?.key).toBe("ev_slot_1_grid_charging");
        expect(slot.batteryDischarge?.key).toBe("ev_slot_1_battery_discharge");
        expect(slotEnabled(slot)).toBe(true);
    });

    it("leaves out an EV slot without its mode", () => {
        const schedule = scheduleOf({
            entities: entitiesOf(
                slotEntities({
                    kind: "ev",
                    number: 1,
                    skip: ["ev_slot_1_mode"],
                }),
            ),
            kinds: ["ev"],
        });

        expect(schedule.leftOut).toBe(1);
    });

    it("builds only the requested kinds, in kind order, up to the slot count", () => {
        const fakes = (["ev", "discharge", "charge"] as const).flatMap((kind) =>
            Array.from({ length: SLOT_COUNT }, (_, index) =>
                slotEntities({ kind, number: index + 1 }),
            ).flat(),
        );

        const all = scheduleOf({
            entities: entitiesOf(fakes),
            kinds: ["ev", "discharge", "charge"],
        });
        const onlyEv = scheduleOf({
            entities: entitiesOf(fakes),
            kinds: ["ev"],
        });

        expect(all.slots).toHaveLength(3 * SLOT_COUNT);
        expect(all.slots[0]?.kind).toBe("charge");
        expect(all.slots.at(-1)?.kind).toBe("ev");
        expect(onlyEv.slots.every((slot) => slot.kind === "ev")).toBe(true);
        expect(all.leftOut).toBe(0);
    });

    it("counts nothing for a system without slots", () => {
        expect(
            scheduleOf({ entities: entitiesOf([]), kinds: ["charge"] }),
        ).toEqual({
            slots: [],
            leftOut: 0,
        });
    });
});

describe("slotEnabled", () => {
    it.each([
        { state: "on", expected: true },
        { state: "off", expected: false },
    ])("a charge slot switched $state is $expected", ({ state, expected }) => {
        expect(
            slotEnabled(
                firstSlot(
                    slotEntities({ kind: "charge", number: 1, enabled: state }),
                ),
            ),
        ).toBe(expected);
    });
});

describe("minuteOfDay", () => {
    it.each([
        { state: "00:00:00", expected: 0 },
        { state: "08:30:00", expected: 510 },
        { state: "23:59:00", expected: MINUTES_PER_DAY - 1 },
        { state: "unavailable", expected: null },
        { state: "", expected: null },
    ])("$state is $expected", ({ state, expected }) => {
        const slot = firstSlot(
            slotEntities({ kind: "charge", number: 1, start: state }),
        );

        expect(minuteOfDay(slot.start)).toBe(expected);
    });

    it("is null when the state has no minutes part", () => {
        const slot = firstSlot(
            slotEntities({ kind: "charge", number: 1, start: "08" }),
        );

        expect(minuteOfDay(slot.start)).toBeNull();
    });
});

describe("timelineBars", () => {
    it("draws one bar on each day of the slot", () => {
        const slot = firstSlot(
            slotEntities({ kind: "charge", number: 1, days: "21" }),
        );

        const bars = timelineBars([slot]);

        expect(bars.map((bar) => bar.day)).toEqual([0, 2, 4]);
        expect(bars.every((bar) => !bar.continuation && !bar.disabled)).toBe(
            true,
        );
        expect(bars[0]?.startMinute).toBe(minuteOfDay(slot.start));
        expect(bars[0]?.endMinute).toBe(minuteOfDay(slot.end));
    });

    it("runs a slot past midnight to the end of the day and on into the next day", () => {
        const slot = firstSlot(
            slotEntities({
                kind: "charge",
                number: 1,
                start: "22:00:00",
                end: "02:00:00",
                days: "1",
            }),
        );

        const [evening, morning] = timelineBars([slot]);

        expect(evening).toMatchObject({
            day: 0,
            endMinute: MINUTES_PER_DAY,
            continuation: false,
        });
        expect(morning).toMatchObject({
            day: 1,
            startMinute: 0,
            continuation: true,
        });
        expect(morning?.endMinute).toBe(minuteOfDay(slot.end));
    });

    it("wraps a Sunday slot past midnight onto Monday", () => {
        const slot = firstSlot(
            slotEntities({
                kind: "charge",
                number: 1,
                start: "23:00:00",
                end: "01:00:00",
                days: "64",
            }),
        );

        expect(timelineBars([slot]).map((bar) => bar.day)).toEqual([6, 0]);
    });

    it.each([
        {
            description: "no days",
            days: "0",
            start: "08:00:00",
            end: "10:00:00",
        },
        {
            description: "equal start and end",
            days: "1",
            start: "08:00:00",
            end: "08:00:00",
        },
        {
            description: "an unreadable start",
            days: "1",
            start: "unavailable",
            end: "10:00:00",
        },
        {
            description: "an unreadable end",
            days: "1",
            start: "08:00:00",
            end: "unavailable",
        },
        {
            description: "an unreadable weekday number",
            days: "unavailable",
            start: "08:00:00",
            end: "10:00:00",
        },
    ])("draws nothing for a slot with $description", ({ days, start, end }) => {
        const slot = firstSlot(
            slotEntities({ kind: "charge", number: 1, days, start, end }),
        );

        expect(timelineBars([slot])).toEqual([]);
    });

    it("marks the bars of a switched-off slot as disabled", () => {
        const slot = firstSlot(
            slotEntities({ kind: "charge", number: 1, enabled: "off" }),
        );

        expect(timelineBars([slot]).every((bar) => bar.disabled)).toBe(true);
    });
});

describe("timeOfUseNoticeRequired", () => {
    const modeEntity = (state: string) =>
        entity("application_mode", "select", state);
    const chargeSlot = slotEntities({ kind: "charge", number: 1 });
    const evSlot = slotEntities({ kind: "ev", number: 1 });
    const slotsOf = (fakes: SystemEntity[], kinds: SlotKind[]) =>
        scheduleOf({ entities: entitiesOf(fakes), kinds }).slots;

    it.each([
        { mode: "time_of_use", expected: false },
        { mode: "time_of_use_bms", expected: false },
        { mode: "self_consumption", expected: true },
        { mode: "backup", expected: true },
        { mode: "unavailable", expected: true },
        { mode: "unknown", expected: true },
    ])("for application mode $mode is $expected", ({ mode, expected }) => {
        const fakes = [...chargeSlot, modeEntity(mode)];

        expect(
            timeOfUseNoticeRequired({
                entities: entitiesOf(fakes),
                slots: slotsOf(fakes, ["charge"]),
            }),
        ).toBe(expected);
    });

    it("is not required without an application mode entity", () => {
        expect(
            timeOfUseNoticeRequired({
                entities: entitiesOf(chargeSlot),
                slots: slotsOf(chargeSlot, ["charge"]),
            }),
        ).toBe(false);
    });

    it("is not required when only EV slots are shown", () => {
        const fakes = [...evSlot, modeEntity("backup")];

        expect(
            timeOfUseNoticeRequired({
                entities: entitiesOf(fakes),
                slots: slotsOf(fakes, ["ev"]),
            }),
        ).toBe(false);
    });
});
