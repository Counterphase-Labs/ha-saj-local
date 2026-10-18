import type { Hass, HassFirstWeekday } from "../hass";

export const WEEKDAY_COUNT = 7;
export const ALL_WEEKDAYS_MASK = 2 ** WEEKDAY_COUNT - 1;

const MONDAY_REFERENCE_DATE = Date.UTC(2024, 0, 1);
const MILLISECONDS_PER_DAY = 86_400_000;

const FIXED_FIRST_WEEKDAYS: Partial<Record<HassFirstWeekday, number>> = {
    monday: 0,
    tuesday: 1,
    wednesday: 2,
    thursday: 3,
    friday: 4,
    saturday: 5,
    sunday: 6,
};

export type WeekdayContext = Pick<Hass, "language" | "locale">;

export const weekdayIndices = (): number[] =>
    Array.from({ length: WEEKDAY_COUNT }, (_, day) => day);

export const daysOfNumber = (value: number): number[] =>
    weekdayIndices().filter((day) => (value >> day) % 2 === 1);

export const numberOfDays = (days: Iterable<number>): number => {
    let value = 0;
    for (const day of new Set(days)) {
        value += 2 ** day;
    }
    return value;
};

export const toggleDay = ({
    value,
    day,
}: {
    value: number;
    day: number;
}): number => {
    const days = new Set(daysOfNumber(value));
    if (days.has(day)) {
        days.delete(day);
    } else {
        days.add(day);
    }
    return numberOfDays(days);
};

interface WeekInfo {
    firstDay: number;
}

interface WeekInfoLocale {
    getWeekInfo?: () => WeekInfo;
    weekInfo?: WeekInfo;
}

const firstWeekdayOfLanguage = (language: string): number => {
    const locale = new Intl.Locale(language) as Intl.Locale & WeekInfoLocale;
    const weekInfo = locale.getWeekInfo?.() ?? locale.weekInfo;
    if (weekInfo === undefined) {
        return 0;
    }
    return weekInfo.firstDay - 1;
};

export const firstWeekday = ({ language, locale }: WeekdayContext): number =>
    FIXED_FIRST_WEEKDAYS[locale.first_weekday] ??
    firstWeekdayOfLanguage(language);

export const weekOrder = (context: WeekdayContext): number[] => {
    const first = firstWeekday(context);
    return weekdayIndices().map((offset) => (first + offset) % WEEKDAY_COUNT);
};

export const weekdayName = ({
    day,
    language,
    width,
}: {
    day: number;
    language: string;
    width: "narrow" | "short" | "long";
}): string =>
    new Intl.DateTimeFormat(language, {
        weekday: width,
        timeZone: "UTC",
    }).format(MONDAY_REFERENCE_DATE + day * MILLISECONDS_PER_DAY);
