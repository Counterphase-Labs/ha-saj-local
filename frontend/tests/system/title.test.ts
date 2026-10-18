import { beforeEach, describe, expect, it, vi } from "vitest";
import { entitiesModule } from "../fakes/entities";

import { listSystemDevices } from "../../src/system/entities";
import { systemTitle, systemTitles } from "../../src/system/title";
import { createFakeHass, fakeDevice } from "../fakes/hass";

vi.mock("../../src/system/entities", () => entitiesModule());

const systemsOf = (...devices: ReturnType<typeof fakeDevice>[]) => {
    vi.mocked(listSystemDevices).mockReturnValue(devices);
    return createFakeHass({ devices });
};

beforeEach(() => {
    vi.mocked(listSystemDevices).mockReset();
});

describe("systemTitle", () => {
    it("joins the device name and the model", () => {
        const hass = systemsOf(fakeDevice("a", { name: "Roof", model: "H2" }));

        expect(systemTitle({ hass, deviceId: "a" })).toBe("Roof H2");
    });

    it("puts the name chosen by the user first", () => {
        const hass = systemsOf(
            fakeDevice("a", {
                name: "SAJ",
                name_by_user: "Garage",
                model: "H2",
            }),
        );

        expect(systemTitle({ hass, deviceId: "a" })).toBe("Garage H2");
    });

    it("leaves out a missing name or model", () => {
        const hass = systemsOf(
            fakeDevice("a", { name: null, model: "H2" }),
            fakeDevice("b", { name: "Roof", model: null }),
        );

        expect(systemTitle({ hass, deviceId: "a" })).toBe("H2");
        expect(systemTitle({ hass, deviceId: "b" })).toBe("Roof");
    });

    it("adds the serial number only when two systems share a title", () => {
        const hass = systemsOf(
            fakeDevice("a", { serial_number: "S1" }),
            fakeDevice("b", { serial_number: "S2" }),
            fakeDevice("c", { name: "Other", serial_number: "SN-300" }),
        );

        const titles = systemTitles(hass);

        expect(titles.get("a")).toContain("S1");
        expect(titles.get("b")).toContain("S2");
        expect(titles.get("a")).not.toBe(titles.get("b"));
        expect(titles.get("c")).not.toContain("SN-300");
    });

    it("keeps the shared title when a device has no serial number", () => {
        const hass = systemsOf(fakeDevice("a"), fakeDevice("b"));

        expect(systemTitle({ hass, deviceId: "a" })).toBe(
            systemTitle({ hass, deviceId: "b" }),
        );
    });

    it("returns an empty title for a device that is not a SAJ Local system", () => {
        const hass = systemsOf();

        expect(systemTitle({ hass, deviceId: "a" })).toBe("");
    });
});
