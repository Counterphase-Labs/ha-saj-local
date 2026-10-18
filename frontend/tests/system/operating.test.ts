import { describe, expect, it } from "vitest";

import { operatingTone } from "../../src/system/operating";

describe("operatingTone", () => {
    it.each([
        { state: "operating", tone: "primary" },
        { state: "off_grid", tone: "warning" },
        { state: "grid_connected_load_bypass", tone: "warning" },
        { state: "fault", tone: "error" },
        { state: "initialisation", tone: "secondary" },
        { state: "standby", tone: "secondary" },
        { state: "upgrade", tone: "secondary" },
        { state: "debugging", tone: "secondary" },
        { state: "self_check", tone: "secondary" },
        { state: "reset", tone: "secondary" },
        { state: "unknown", tone: "disabled" },
        { state: "unavailable", tone: "disabled" },
        { state: "constructor", tone: "disabled" },
        { state: undefined, tone: "disabled" },
    ])("$state is $tone", ({ state, tone }) => {
        expect(operatingTone(state)).toBe(tone);
    });
});
