import { beforeEach, describe, expect, it, vi } from "vitest";
import { entitiesModule } from "../fakes/entities";

import type { HassEntityState } from "../../src/hass";
import { systemEntityIds } from "../../src/system/entities";
import { SystemRedraw, type RedrawHass } from "../../src/system/redraw";

vi.mock("../../src/system/entities", () => entitiesModule());

const OWN_ENTITY = "sensor.saj_pv_power";
const OTHER_ENTITY = "sensor.kitchen_temperature";

const stateOf = (state: string): HassEntityState => ({
    entity_id: OWN_ENTITY,
    state,
    attributes: {},
    last_changed: "",
});

const snapshot = (overrides: Partial<RedrawHass> = {}): RedrawHass => ({
    entities: {},
    devices: {},
    language: "en",
    locale: { language: "en", first_weekday: "monday" },
    states: { [OWN_ENTITY]: stateOf("1"), [OTHER_ENTITY]: stateOf("20") },
    ...overrides,
});

const next = (
    previous: RedrawHass,
    overrides: Partial<RedrawHass>,
): RedrawHass => ({ ...previous, ...overrides });

const ownStateChange = (previous: RedrawHass): Partial<RedrawHass> => ({
    states: { ...previous.states, [OWN_ENTITY]: stateOf("2") },
});

const neededAfter = ({
    previous,
    overrides,
    deviceId,
}: {
    previous: RedrawHass;
    overrides: Partial<RedrawHass>;
    deviceId: string | undefined;
}): boolean =>
    new SystemRedraw().needed({
        previous,
        next: next(previous, overrides),
        deviceId,
    });

beforeEach(() => {
    vi.mocked(systemEntityIds).mockReset();
    vi.mocked(systemEntityIds).mockReturnValue([OWN_ENTITY]);
});

describe("SystemRedraw", () => {
    it("is not needed when nothing the element shows changed, whatever else changed", () => {
        const previous = snapshot();

        expect(
            neededAfter({
                previous,
                overrides: {
                    states: {
                        ...previous.states,
                        [OTHER_ENTITY]: stateOf("21"),
                    },
                },
                deviceId: "saj_1",
            }),
        ).toBe(false);
    });

    it("is needed when the state object of an entity of the system changed", () => {
        const previous = snapshot();

        expect(
            neededAfter({
                previous,
                overrides: ownStateChange(previous),
                deviceId: "saj_1",
            }),
        ).toBe(true);
    });

    it("is needed when an entity of the system appears or disappears", () => {
        const previous = snapshot();
        const { [OWN_ENTITY]: removed, ...rest } = previous.states;

        expect(removed).toBeDefined();
        expect(
            neededAfter({
                previous,
                overrides: { states: rest },
                deviceId: "saj_1",
            }),
        ).toBe(true);
    });

    it.each([
        { name: "the entity registry", overrides: { entities: {} } },
        { name: "the device registry", overrides: { devices: {} } },
        { name: "the language", overrides: { language: "de" } },
        {
            name: "the locale",
            overrides: {
                locale: { language: "en", first_weekday: "sunday" as const },
            },
        },
    ])("is needed when $name changed", ({ overrides }) => {
        expect(
            neededAfter({ previous: snapshot(), overrides, deviceId: "saj_1" }),
        ).toBe(true);
    });

    it("never looks at an entity when there is no system chosen", () => {
        const previous = snapshot();

        expect(
            neededAfter({
                previous,
                overrides: ownStateChange(previous),
                deviceId: undefined,
            }),
        ).toBe(false);
        expect(systemEntityIds).not.toHaveBeenCalled();
    });

    it("scans the registry once while the registry and the system stay the same", () => {
        const redraw = new SystemRedraw();
        const previous = snapshot();
        const current = next(previous, {});

        redraw.needed({ previous, next: current, deviceId: "saj_1" });
        redraw.needed({ previous: current, next: current, deviceId: "saj_1" });

        expect(systemEntityIds).toHaveBeenCalledTimes(1);
    });

    it("scans again when the system chosen changes", () => {
        const redraw = new SystemRedraw();
        const previous = snapshot();

        redraw.needed({ previous, next: previous, deviceId: "saj_1" });
        redraw.needed({ previous, next: previous, deviceId: "saj_2" });

        expect(systemEntityIds).toHaveBeenCalledTimes(2);
    });
});
