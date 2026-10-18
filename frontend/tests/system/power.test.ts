import { describe, expect, it, vi } from "vitest";
import { entitiesModule } from "../fakes/entities";

import {
    FASTEST_FLOW_SECONDS,
    FLOW_THRESHOLD_WATTS,
    flowDurationSeconds,
    powerFlow,
    SLOWEST_FLOW_SECONDS,
    type PowerNodeKind,
    wattsOf,
} from "../../src/system/power";
import { numericValue } from "../../src/system/entities";
import { entity } from "../fakes/entities";

vi.mock("../../src/system/entities", () => entitiesModule());

const aboveThreshold = FLOW_THRESHOLD_WATTS + 1;

describe("powerFlow", () => {
    it.each([
        {
            kind: "solar",
            watts: aboveThreshold,
            state: "producing",
            line: "to_inverter",
        },
        {
            kind: "battery",
            watts: aboveThreshold,
            state: "discharging",
            line: "to_inverter",
        },
        {
            kind: "battery",
            watts: -aboveThreshold,
            state: "charging",
            line: "from_inverter",
        },
        {
            kind: "grid",
            watts: aboveThreshold,
            state: "exporting",
            line: "from_inverter",
        },
        {
            kind: "grid",
            watts: -aboveThreshold,
            state: "importing",
            line: "to_inverter",
        },
        {
            kind: "consumer",
            watts: aboveThreshold,
            state: "consuming",
            line: "from_inverter",
        },
        {
            kind: "solar",
            watts: -aboveThreshold,
            state: "producing",
            line: "to_inverter",
        },
        {
            kind: "consumer",
            watts: -aboveThreshold,
            state: "consuming",
            line: "from_inverter",
        },
    ] satisfies {
        kind: PowerNodeKind;
        watts: number;
        state: string;
        line: string;
    }[])(
        "$kind at $watts W is $state with the line $line",
        ({ kind, watts, state, line }) => {
            expect(powerFlow({ kind, watts })).toEqual({ state, line });
        },
    );

    it.each(["solar", "battery", "grid", "consumer"] as const)(
        "%s is idle at zero and at the threshold",
        (kind) => {
            const idle = { state: "idle", line: "none" };

            expect(powerFlow({ kind, watts: 0 })).toEqual(idle);
            expect(powerFlow({ kind, watts: FLOW_THRESHOLD_WATTS })).toEqual(
                idle,
            );
            expect(powerFlow({ kind, watts: -FLOW_THRESHOLD_WATTS })).toEqual(
                idle,
            );
        },
    );
});

describe("flowDurationSeconds", () => {
    it("is shorter for more power and stays within the slowest and fastest bounds", () => {
        const watts = [10, 50, 500, 5000, 50_000];

        const durations = watts.map(flowDurationSeconds);

        expect(durations).toEqual([...durations].sort((a, b) => b - a));
        expect(Math.max(...durations)).toBeLessThanOrEqual(
            SLOWEST_FLOW_SECONDS,
        );
        expect(Math.min(...durations)).toBeGreaterThanOrEqual(
            FASTEST_FLOW_SECONDS,
        );
    });

    it("separates 50 W from 5 kW clearly", () => {
        expect(flowDurationSeconds(50)).toBeGreaterThan(
            flowDurationSeconds(5000),
        );
    });

    it("treats a negative power like the same positive power", () => {
        expect(flowDurationSeconds(-500)).toBe(flowDurationSeconds(500));
    });
});

const powerEntity = (attributes: Record<string, unknown> = {}) =>
    entity("pv_power", "sensor", "unused", { attributes });

describe("wattsOf", () => {
    it.each([
        { unit: "W", value: 1500, expected: 1500 },
        { unit: "kW", value: 1.5, expected: 1500 },
        { unit: "MW", value: 0.002, expected: 2000 },
        { unit: "furlongs", value: 7, expected: 7 },
        { unit: undefined, value: -40, expected: -40 },
    ])(
        "reads $value in unit $unit as $expected watts",
        ({ unit, value, expected }) => {
            vi.mocked(numericValue).mockReturnValueOnce(value);
            const attributes =
                unit === undefined ? {} : { unit_of_measurement: unit };

            expect(wattsOf(powerEntity(attributes))).toBeCloseTo(expected);
        },
    );

    it("has no watts when the entity has no numeric value", () => {
        vi.mocked(numericValue).mockReturnValueOnce(null);

        expect(wattsOf(powerEntity())).toBeNull();
    });
});
