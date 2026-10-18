import {
    numericValue,
    type SystemEntities,
    type SystemEntity,
} from "./entities";
import { WEEKDAY_COUNT } from "./weekdays";

export const SLOT_COUNT = 7;
export const MINUTES_PER_DAY = 24 * 60;
export const TIME_OF_USE_MODES: readonly string[] = [
    "time_of_use",
    "time_of_use_bms",
];
export const APPLICATION_MODE_KEY = "application_mode";

const MINUTES_PER_HOUR = 60;

export type SlotKind = "charge" | "discharge" | "ev";
export const SLOT_KINDS: readonly SlotKind[] = ["charge", "discharge", "ev"];

const BASE_SUFFIXES = ["start", "end", "days", "power"] as const;
const SWITCHED_SUFFIXES = [...BASE_SUFFIXES, "enabled"] as const;
const EV_SUFFIXES = [
    ...BASE_SUFFIXES,
    "mode",
    "grid_charging",
    "battery_discharge",
] as const;

export interface Slot {
    kind: SlotKind;
    number: number;
    stem: string;
    start: SystemEntity;
    end: SystemEntity;
    days: SystemEntity;
    power: SystemEntity;
    enabled: SystemEntity | null;
    mode: SystemEntity | null;
    gridCharging: SystemEntity | null;
    batteryDischarge: SystemEntity | null;
}

export interface Schedule {
    slots: Slot[];
    leftOut: number;
}

export interface TimelineBar {
    day: number;
    startMinute: number;
    endMinute: number;
    slot: Slot;
    disabled: boolean;
    continuation: boolean;
}

const suffixesOf = (kind: SlotKind): readonly string[] =>
    kind === "ev" ? EV_SUFFIXES : SWITCHED_SUFFIXES;

const slotNumbers = (): number[] =>
    Array.from({ length: SLOT_COUNT }, (_, index) => index + 1);

export const slotStem = ({
    kind,
    number,
}: {
    kind: SlotKind;
    number: number;
}): string => `${kind}_slot_${String(number)}`;

const buildSlot = ({
    entities,
    kind,
    number,
}: {
    entities: SystemEntities;
    kind: SlotKind;
    number: number;
}): { slot: Slot | null; partial: boolean } => {
    const stem = slotStem({ kind, number });
    const found = suffixesOf(kind).map((suffix) =>
        entities.get(`${stem}_${suffix}`),
    );
    const present = found.filter((entity) => entity !== undefined);
    if (present.length === 0) {
        return { slot: null, partial: false };
    }
    const byKey = (suffix: string): SystemEntity | null =>
        entities.get(`${stem}_${suffix}`) ?? null;
    const start = byKey("start");
    const end = byKey("end");
    const days = byKey("days");
    const power = byKey("power");
    const complete = present.length === found.length;
    if (!complete || !start || !end || !days || !power) {
        return { slot: null, partial: true };
    }
    return {
        slot: {
            kind,
            number,
            stem,
            start,
            end,
            days,
            power,
            enabled: byKey("enabled"),
            mode: byKey("mode"),
            gridCharging: byKey("grid_charging"),
            batteryDischarge: byKey("battery_discharge"),
        },
        partial: false,
    };
};

export const scheduleOf = ({
    entities,
    kinds,
}: {
    entities: SystemEntities;
    kinds: readonly SlotKind[];
}): Schedule => {
    const slots: Slot[] = [];
    let leftOut = 0;
    for (const kind of SLOT_KINDS.filter((candidate) =>
        kinds.includes(candidate),
    )) {
        for (const number of slotNumbers()) {
            const built = buildSlot({ entities, kind, number });
            if (built.slot !== null) {
                slots.push(built.slot);
            }
            if (built.partial) {
                leftOut += 1;
            }
        }
    }
    return { slots, leftOut };
};

export const slotEnabled = (slot: Slot): boolean =>
    slot.enabled === null || slot.enabled.state.state === "on";

export const minuteOfDay = (entity: SystemEntity): number | null => {
    const [hours, minutes] = entity.state.state.split(":").map(Number);
    if (
        hours === undefined ||
        minutes === undefined ||
        !Number.isFinite(hours) ||
        !Number.isFinite(minutes)
    ) {
        return null;
    }
    return hours * MINUTES_PER_HOUR + minutes;
};

export const timelineBars = (slots: readonly Slot[]): TimelineBar[] => {
    const bars: TimelineBar[] = [];
    for (const slot of slots) {
        const start = minuteOfDay(slot.start);
        const end = minuteOfDay(slot.end);
        const daysValue = numericValue(slot.days);
        if (start === null || end === null || daysValue === null) {
            continue;
        }
        const disabled = !slotEnabled(slot);
        const addBar = (bar: Omit<TimelineBar, "slot" | "disabled">): void => {
            bars.push({ ...bar, slot, disabled });
        };
        for (let day = 0; day < WEEKDAY_COUNT; day += 1) {
            if ((daysValue >> day) % 2 !== 1 || start === end) {
                continue;
            }
            if (end > start) {
                addBar({
                    day,
                    startMinute: start,
                    endMinute: end,
                    continuation: false,
                });
                continue;
            }
            addBar({
                day,
                startMinute: start,
                endMinute: MINUTES_PER_DAY,
                continuation: false,
            });
            addBar({
                day: (day + 1) % WEEKDAY_COUNT,
                startMinute: 0,
                endMinute: end,
                continuation: true,
            });
        }
    }
    return bars;
};

export const timeOfUseNoticeRequired = ({
    entities,
    slots,
}: {
    entities: SystemEntities;
    slots: readonly Slot[];
}): boolean => {
    const mode = entities.get(APPLICATION_MODE_KEY);
    const showsTimeOfUseSlots = slots.some((slot) => slot.kind !== "ev");
    return (
        showsTimeOfUseSlots &&
        mode !== undefined &&
        !TIME_OF_USE_MODES.includes(mode.state.state)
    );
};
