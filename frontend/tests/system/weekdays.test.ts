import { afterEach, describe, expect, it, vi } from "vitest";

import type { HassFirstWeekday } from "../../src/hass";
import {
    ALL_WEEKDAYS_MASK,
    daysOfNumber,
    firstWeekday,
    numberOfDays,
    toggleDay,
    weekdayIndices,
    weekdayName,
    weekOrder,
    WEEKDAY_COUNT,
} from "../../src/system/weekdays";

const context = (first_weekday: HassFirstWeekday, language = "en-US") => ({
    language,
    locale: { language, first_weekday },
});

describe("weekday numbers", () => {
    it.each(weekdayIndices())("day %i is bit %i and nothing else", (day) => {
        expect(numberOfDays([day])).toBe(2 ** day);
        expect(daysOfNumber(2 ** day)).toEqual([day]);
    });

    it("converts every number from 0 to 127 back to the same number", () => {
        for (let value = 0; value <= ALL_WEEKDAYS_MASK; value += 1) {
            expect(numberOfDays(daysOfNumber(value))).toBe(value);
        }
    });

    it("counts a repeated day once", () => {
        expect(numberOfDays([2, 2])).toBe(numberOfDays([2]));
    });

    it("turns Monday, Wednesday and Friday into 21", () => {
        expect(numberOfDays([0, 2, 4])).toBe(21);
    });

    it("toggles a day on and off", () => {
        const on = toggleDay({ value: 0, day: 3 });

        expect(daysOfNumber(on)).toEqual([3]);
        expect(toggleDay({ value: on, day: 3 })).toBe(0);
    });
});

describe("week order", () => {
    afterEach(() => {
        vi.restoreAllMocks();
        vi.unstubAllGlobals();
    });

    it.each([
        { setting: "monday", first: 0 },
        { setting: "tuesday", first: 1 },
        { setting: "wednesday", first: 2 },
        { setting: "thursday", first: 3 },
        { setting: "friday", first: 4 },
        { setting: "saturday", first: 5 },
        { setting: "sunday", first: 6 },
    ] as const)("starts on $setting", ({ setting, first }) => {
        const order = weekOrder(context(setting));

        expect(order[0]).toBe(first);
        expect([...order].sort()).toEqual(weekdayIndices());
        expect(order).toHaveLength(WEEKDAY_COUNT);
    });

    const stubLocale = (members: Record<string, unknown>) => {
        const constructed = vi.fn();
        class FakeLocale {
            constructor() {
                constructed();
                Object.assign(this, members);
            }

            toString(): string {
                return "fake";
            }
        }
        vi.stubGlobal(
            "Intl",
            Object.create(Intl, { Locale: { value: FakeLocale } }),
        );
        return constructed;
    };

    it.each([
        { firstDay: 1, first: 0 },
        { firstDay: 6, first: 5 },
        { firstDay: 7, first: 6 },
    ])(
        "follows the week information method when the week starts on day $firstDay",
        ({ firstDay, first }) => {
            stubLocale({ getWeekInfo: () => ({ firstDay }) });

            expect(firstWeekday(context("language"))).toBe(first);
        },
    );

    it.each([
        { firstDay: 1, first: 0 },
        { firstDay: 7, first: 6 },
    ])(
        "follows the week information property when the browser has no method and the week starts on day $firstDay",
        ({ firstDay, first }) => {
            stubLocale({ weekInfo: { firstDay } });

            expect(firstWeekday(context("language"))).toBe(first);
        },
    );

    it("prefers the method over the property", () => {
        stubLocale({
            getWeekInfo: () => ({ firstDay: 7 }),
            weekInfo: { firstDay: 1 },
        });

        expect(firstWeekday(context("language"))).toBe(6);
    });

    it("starts on Monday when the browser has neither the method nor the property", () => {
        stubLocale({});

        expect(firstWeekday(context("language"))).toBe(0);
    });

    it("does not ask the browser when the user chose a first weekday", () => {
        const constructed = stubLocale({});

        firstWeekday(context("sunday"));

        expect(constructed).not.toHaveBeenCalled();
    });
});

describe("weekdayName", () => {
    it("follows the language", () => {
        const english = weekdayName({ day: 0, language: "en", width: "long" });
        const german = weekdayName({ day: 0, language: "de", width: "long" });

        expect(english).not.toBe(german);
    });

    it("is shorter in the short width and distinct per day", () => {
        const short = weekdayIndices().map((day) =>
            weekdayName({ day, language: "en", width: "short" }),
        );
        const long = weekdayName({ day: 2, language: "en", width: "long" });

        expect(new Set(short).size).toBe(WEEKDAY_COUNT);
        expect(short[2]?.length).toBeLessThan(long.length);
    });
});
