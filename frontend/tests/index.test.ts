import { describe, expect, it, vi } from "vitest";

const MODULES = [
    "../src/badges/status-badge",
    "../src/cards/battery-card",
    "../src/cards/faults-card",
    "../src/cards/power-flow-card",
    "../src/cards/status-card",
    "../src/cards/controls-card",
    "../src/cards/schedule-card",
    "../src/features/weekdays-feature",
];

const fakes = vi.hoisted(() => {
    const loaded: string[] = [];
    let release = (): void => undefined;
    const homeAssistantReady = new Promise<void>((resolve) => {
        release = resolve;
    });
    return {
        loaded,
        release: () => {
            release();
        },
        homeAssistantReady,
    };
});

vi.mock("../src/home-assistant", () => ({
    whenHomeAssistantIsReady: () => fakes.homeAssistantReady,
}));

for (const path of MODULES) {
    vi.doMock(path, () => {
        fakes.loaded.push(path);
        return {};
    });
}

describe("bundle entry", () => {
    it("loads every element only after Home Assistant has defined its own root element", async () => {
        await import("../src/index");
        const loadedBeforeReady = [...fakes.loaded];

        fakes.release();
        await vi.waitFor(() => {
            expect(fakes.loaded).toHaveLength(MODULES.length);
        });

        expect(loadedBeforeReady).toEqual([]);
        expect([...fakes.loaded].sort()).toEqual([...MODULES].sort());
    });
});
