import type { Slot } from "../../src/system/schedule";
import type { SystemEntity } from "../../src/system/entities";
import { entity } from "./entities";

export type SlotKind = "charge" | "discharge" | "ev";

export interface SlotOptions {
    kind: SlotKind;
    number: number;
    start?: string;
    end?: string;
    days?: string;
    power?: string;
    enabled?: string;
    skip?: string[];
}

export const slotEntities = ({
    kind,
    number,
    start = "08:00:00",
    end = "10:30:00",
    days = "5",
    power = "1000",
    enabled = "on",
    skip = [],
}: SlotOptions): SystemEntity[] => {
    const stem = `${kind}_slot_${String(number)}`;
    const all: SystemEntity[] = [
        entity(`${stem}_start`, "time", start),
        entity(`${stem}_end`, "time", end),
        entity(`${stem}_days`, "number", days),
        entity(`${stem}_power`, "number", power),
        ...(kind === "ev"
            ? [
                  entity(`${stem}_mode`, "select", "charge"),
                  entity(`${stem}_grid_charging`, "switch", "off"),
                  entity(`${stem}_battery_discharge`, "switch", "off"),
              ]
            : [entity(`${stem}_enabled`, "switch", enabled)]),
    ];
    return all.filter((item) => !skip.includes(item.key));
};

export const fakeSlot = (options: SlotOptions): Slot => {
    const entities = slotEntities(options);
    const stem = `${options.kind}_slot_${String(options.number)}`;
    const named = (suffix: string): SystemEntity | null =>
        entities.find((item) => item.key === `${stem}_${suffix}`) ?? null;
    const required = (suffix: string): SystemEntity => {
        const found = named(suffix);
        if (found === null) {
            throw new Error(`No ${suffix} entity`);
        }
        return found;
    };
    return {
        kind: options.kind,
        number: options.number,
        stem,
        start: required("start"),
        end: required("end"),
        days: required("days"),
        power: required("power"),
        enabled: named("enabled"),
        mode: named("mode"),
        gridCharging: named("grid_charging"),
        batteryDischarge: named("battery_discharge"),
    };
};
