import { describe, expect, it, vi } from "vitest";
import { entitiesModule } from "../fakes/entities";

import { activeFaultSummaries, faultGroups } from "../../src/system/faults";
import { entity, entityMap } from "../fakes/entities";
import type { SystemEntity } from "../../src/system/entities";

vi.mock("../../src/system/entities", () => entitiesModule());

const binary = (key: string, state: string, lastChanged?: string) =>
    entity(key, "binary_sensor", state, { lastChanged });

const entitiesOf = (entities: SystemEntity[]) => entityMap(entities);

describe("faultGroups", () => {
    it("makes a group for each summary present and none for absent ones", () => {
        const groups = faultGroups(
            entitiesOf([
                binary("inverter_fault", "off"),
                binary("battery_fault", "on"),
            ]),
        );

        expect(groups.map((group) => group.id)).toEqual([
            "inverter",
            "battery",
        ]);
        expect(groups.map((group) => group.active)).toEqual([false, true]);
    });

    it("lists only active rows of the group's prefix with their start time", () => {
        const since = "2026-10-17T08:00:00+00:00";
        const [group] = faultGroups(
            entitiesOf([
                binary("inverter_fault", "on"),
                binary("inverter_fault_overvoltage", "on", since),
                binary("inverter_fault_overcurrent", "off"),
                binary("battery_fault_cell", "on"),
                entity("inverter_fault_code", "sensor", "on"),
            ]),
        );

        expect(group?.rows.map((row) => row.entity.key)).toEqual([
            "inverter_fault_overvoltage",
        ]);
        expect(group?.rows[0]?.since.toISOString()).toBe(
            new Date(since).toISOString(),
        );
    });

    it("sorts rows by key", () => {
        const [group] = faultGroups(
            entitiesOf([
                binary("inverter_fault", "on"),
                binary("inverter_fault_b", "on"),
                binary("inverter_fault_a", "on"),
            ]),
        );

        expect(group?.rows.map((row) => row.entity.key)).toEqual([
            "inverter_fault_a",
            "inverter_fault_b",
        ]);
    });

    it("adds pack faults and warnings to the battery group only", () => {
        const groups = faultGroups(
            entitiesOf([
                binary("battery_fault", "on"),
                binary("inverter_fault", "on"),
                binary("battery_pack1_fault", "on"),
                binary("battery_pack2_warning", "on"),
                binary("battery_pack3_warning", "off"),
            ]),
        );

        const battery = groups.find((group) => group.id === "battery");
        const inverter = groups.find((group) => group.id === "inverter");
        expect(battery?.rows.map((row) => row.entity.key)).toEqual([
            "battery_pack1_fault",
            "battery_pack2_warning",
        ]);
        expect(inverter?.rows).toEqual([]);
    });

    it("flags the unrecognised row", () => {
        const [group] = faultGroups(
            entitiesOf([
                binary("ev_fault", "on"),
                binary("ev_fault_unrecognised", "on"),
                binary("ev_fault_known", "on"),
            ]),
        );

        const flags = Object.fromEntries(
            (group?.rows ?? []).map((row) => [
                row.entity.key,
                row.unrecognised,
            ]),
        );
        expect(flags).toEqual({
            ev_fault_known: false,
            ev_fault_unrecognised: true,
        });
    });
});

describe("activeFaultSummaries", () => {
    it("returns the summaries that are on, in group order", () => {
        const summaries = activeFaultSummaries(
            entitiesOf([
                binary("ev_fault", "on"),
                binary("battery_fault", "off"),
                binary("inverter_fault", "on"),
            ]),
        );

        expect(summaries.map((summary) => summary.key)).toEqual([
            "inverter_fault",
            "ev_fault",
        ]);
    });

    it("returns nothing when no summary exists", () => {
        expect(activeFaultSummaries(entitiesOf([]))).toEqual([]);
    });
});
