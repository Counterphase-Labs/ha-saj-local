import { describe, expect, it } from "vitest";

import {
    allUnavailable,
    isOn,
    isUnavailable,
    listSystemDevices,
    numericValue,
    ownerOfEntity,
    systemEntities,
    systemEntityIds,
    type SystemEntity,
} from "../../src/system/entities";
import {
    createFakeHass,
    fakeDevice,
    fakeEntity,
    fakeEntityId,
} from "../fakes/hass";

const withState = (state: string): SystemEntity => ({
    key: "pv_power",
    entityId: "sensor.pv_power",
    domain: "sensor",
    state: {
        entity_id: "sensor.pv_power",
        state,
        attributes: {},
        last_changed: "",
    },
});

describe("listSystemDevices", () => {
    it("returns only devices that own a SAJ Local entity", () => {
        const hass = createFakeHass({
            devices: [
                fakeDevice("first"),
                fakeDevice("second"),
                fakeDevice("foreign"),
            ],
            entities: [
                fakeEntity("pv_power", "sensor", "1", { deviceId: "first" }),
                fakeEntity("pv_power", "sensor", "1", { deviceId: "second" }),
                fakeEntity("temperature", "sensor", "1", {
                    deviceId: "foreign",
                    platform: "other",
                }),
            ],
        });

        expect(listSystemDevices(hass).map((device) => device.id)).toEqual([
            "first",
            "second",
        ]);
    });

    it("returns nothing when no entity belongs to the integration", () => {
        const hass = createFakeHass({ devices: [fakeDevice("foreign")] });

        expect(listSystemDevices(hass)).toEqual([]);
    });
});

describe("systemEntities", () => {
    it("keys the chosen device's entities by translation key and never mixes in another system", () => {
        const hass = createFakeHass({
            entities: [
                fakeEntity("pv_power", "sensor", "100", { deviceId: "first" }),
                fakeEntity("pv_power", "sensor", "900", { deviceId: "second" }),
                fakeEntity("control_allowed", "binary_sensor", "on", {
                    deviceId: "second",
                }),
            ],
        });

        const first = systemEntities({ hass, deviceId: "first" });
        const second = systemEntities({ hass, deviceId: "second" });

        expect([...first.keys()]).toEqual(["pv_power"]);
        expect(first.get("pv_power")?.state.state).toBe("100");
        expect([...second.keys()].sort()).toEqual([
            "control_allowed",
            "pv_power",
        ]);
        expect(second.get("pv_power")?.domain).toBe("sensor");
    });

    it("skips registry entries without a state and entries of other platforms", () => {
        const hass = createFakeHass({
            entities: [
                fakeEntity("pv_power", "sensor", "100"),
                fakeEntity("temperature", "sensor", "5", { platform: "other" }),
            ],
        });
        hass.states = {};

        expect(systemEntities({ hass, deviceId: "saj_1" }).size).toBe(0);
    });

    it("returns an empty map for a device with no SAJ Local entity", () => {
        const hass = createFakeHass({
            entities: [fakeEntity("pv_power", "sensor", "100")],
        });

        expect(systemEntities({ hass, deviceId: "other" }).size).toBe(0);
    });

    it("ignores entries without a translation key", () => {
        const hass = createFakeHass({
            entities: [fakeEntity("pv_power", "sensor", "100")],
        });
        const entry = Object.values(hass.entities)[0];
        if (entry !== undefined) {
            entry.translation_key = null;
        }

        expect(systemEntities({ hass, deviceId: "saj_1" }).size).toBe(0);
    });
});

describe("systemEntityIds", () => {
    const hass = createFakeHass({
        entities: [
            fakeEntity("pv_power", "sensor", "1", { deviceId: "first" }),
            fakeEntity("control_allowed", "binary_sensor", "on", {
                deviceId: "first",
            }),
            fakeEntity("pv_power", "sensor", "2", { deviceId: "second" }),
            fakeEntity("temperature", "sensor", "3", {
                deviceId: "first",
                platform: "other",
            }),
        ],
    });

    it("lists the entity ids of the chosen system only", () => {
        const ids = systemEntityIds({ hass, deviceId: "first" });

        expect(ids.sort()).toEqual(
            [
                fakeEntityId(
                    fakeEntity("pv_power", "sensor", "1", {
                        deviceId: "first",
                    }),
                ),
                fakeEntityId(
                    fakeEntity("control_allowed", "binary_sensor", "on", {
                        deviceId: "first",
                    }),
                ),
            ].sort(),
        );
    });

    it("lists nothing for a device with no SAJ Local entity", () => {
        expect(systemEntityIds({ hass, deviceId: "unknown" })).toEqual([]);
    });
});

describe("ownerOfEntity", () => {
    const hass = createFakeHass({
        entities: [
            fakeEntity("charge_slot_1_days", "number", "1", {
                deviceId: "first",
            }),
            fakeEntity("temperature", "sensor", "1", { platform: "other" }),
        ],
    });

    it("returns the device and key of a SAJ Local entity", () => {
        const entityId = fakeEntityId(
            fakeEntity("charge_slot_1_days", "number", "1", {
                deviceId: "first",
            }),
        );

        expect(ownerOfEntity({ hass, entityId })).toEqual({
            deviceId: "first",
            key: "charge_slot_1_days",
        });
    });

    it.each([
        { description: "an unknown entity", entityId: "number.missing" },
        {
            description: "an entity of another integration",
            entityId: fakeEntityId(
                fakeEntity("temperature", "sensor", "1", { platform: "other" }),
            ),
        },
    ])("returns null for $description", ({ entityId }) => {
        expect(ownerOfEntity({ hass, entityId })).toBeNull();
    });

    it("returns null for an entity without a device", () => {
        const entityId = fakeEntityId(
            fakeEntity("charge_slot_1_days", "number", "1", {
                deviceId: "first",
            }),
        );
        const entry = hass.entities[entityId];
        if (entry !== undefined) {
            entry.device_id = null;
        }

        expect(ownerOfEntity({ hass, entityId })).toBeNull();
    });

    it("returns null for an entity without a translation key", () => {
        const noKey = createFakeHass({
            entities: [fakeEntity("pv_power", "sensor", "1")],
        });
        const [entityId, entry] = Object.entries(noKey.entities)[0] ?? [];
        if (entry !== undefined) {
            delete entry.translation_key;
        }

        expect(
            ownerOfEntity({ hass: noKey, entityId: entityId ?? "" }),
        ).toBeNull();
    });
});

describe("state helpers", () => {
    it.each([
        { state: "unavailable", unavailable: true },
        { state: "unknown", unavailable: false },
        { state: "5", unavailable: false },
    ])("isUnavailable is $unavailable for $state", ({ state, unavailable }) => {
        expect(isUnavailable(withState(state))).toBe(unavailable);
    });

    it.each([
        { description: "no entities", states: [], expected: false },
        {
            description: "only unavailable entities",
            states: ["unavailable", "unavailable"],
            expected: true,
        },
        {
            description: "one answering entity",
            states: ["unavailable", "5"],
            expected: false,
        },
    ])(
        "allUnavailable with $description is $expected",
        ({ states, expected }) => {
            expect(allUnavailable(states.map(withState))).toBe(expected);
        },
    );

    it.each([
        { state: "12.5", expected: 12.5 },
        { state: "-3", expected: -3 },
        { state: "0", expected: 0 },
        { state: "unavailable", expected: null },
        { state: "unknown", expected: null },
        { state: "", expected: null },
        { state: "on", expected: null },
    ])("numericValue of $state is $expected", ({ state, expected }) => {
        expect(numericValue(withState(state))).toBe(expected);
    });

    it.each([
        { entity: withState("on"), expected: true },
        { entity: withState("off"), expected: false },
        { entity: undefined, expected: false },
    ])("isOn is $expected", ({ entity, expected }) => {
        expect(isOn(entity)).toBe(expected);
    });
});
