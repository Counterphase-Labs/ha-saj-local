import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { entitiesModule } from "../fakes/entities";
import {
    controlModule,
    entityControlsModule,
    registrationModule,
    systemElementModule,
} from "../fakes/modules";

import {
    SajWeekdaysFeature,
    supportsWeekdays,
    WEEKDAYS_FEATURE_TAG,
} from "../../src/features/weekdays-feature";
import { registerCardFeature } from "../../src/registration";
import {
    controlLock,
    setNumberRequest,
    type ControlTracker,
} from "../../src/system/control";
import {
    isUnavailable,
    ownerOfEntity,
    systemEntities,
} from "../../src/system/entities";
import { entity, entityMap } from "../fakes/entities";
import { createFakeHass } from "../fakes/hass";
import { elementsIn, firstIn } from "../cards/support";
import { mount } from "../ui/mount";
import { resultOf, trackerMocks } from "../fakes/mocks";

vi.mock("../../src/ui/system-element", () => systemElementModule());
vi.mock("../../src/cards/entity-controls", () => entityControlsModule());
vi.mock("../../src/system/entities", () => entitiesModule());
vi.mock("../../src/system/control", () => controlModule());
vi.mock("../../src/registration", () => registrationModule());
vi.mock("../../src/ui/weekday-buttons", () => ({}));

const DAYS_ENTITY_ID = "number.saj_charge_slot_1_days";
const PROBE_TAG = "probe-weekdays-feature";

class ProbeFeature extends SajWeekdaysFeature {
    watched(): string | undefined {
        return this.watchedDeviceId();
    }

    get controlTracker(): ControlTracker {
        return this.tracker;
    }
}
customElements.define(PROBE_TAG, ProbeFeature);

const [registration] = vi
    .mocked(registerCardFeature)
    .mock.calls.map(([entry]) => entry);

const daysEntity = entity("charge_slot_1_days", "number", "5", {
    entityId: DAYS_ENTITY_ID,
});

const mountFeature = async ({
    entityId = DAYS_ENTITY_ID,
    hass = createFakeHass(),
}: {
    entityId?: string | null;
    hass?: ReturnType<typeof createFakeHass> | null;
} = {}) => {
    const feature = await mount<ProbeFeature>(PROBE_TAG, {
        hass: hass ?? undefined,
        context: { entity_id: entityId ?? undefined },
    });
    return feature;
};

const trackerOf = (feature: ProbeFeature) =>
    trackerMocks(feature.controlTracker);

beforeEach(() => {
    vi.mocked(ownerOfEntity).mockReturnValue({
        deviceId: "saj_1",
        key: "charge_slot_1_days",
    });
    vi.mocked(systemEntities).mockReturnValue(entityMap([daysEntity]));
    vi.mocked(controlLock).mockReturnValue({ locked: false, entity: null });
});

afterEach(() => {
    document.body.replaceChildren();
});

describe("saj-local-weekdays support", () => {
    const supported = (
        entityId: string | undefined,
        owner: { deviceId: string; key: string } | null,
    ): boolean => {
        vi.mocked(ownerOfEntity).mockReturnValue(owner);
        return supportsWeekdays({
            hass: createFakeHass(),
            context: { entity_id: entityId },
        });
    };

    it("is offered for a SAJ Local number entity whose key ends in _days", () => {
        expect(
            supported(DAYS_ENTITY_ID, { deviceId: "saj_1", key: "slot_days" }),
        ).toBe(true);
    });

    it.each([
        {
            name: "a number entity with another key",
            entityId: "number.saj_charge_slot_1_power",
            owner: { deviceId: "saj_1", key: "charge_slot_1_power" },
        },
        {
            name: "an entity of another domain",
            entityId: "sensor.saj_charge_slot_1_days",
            owner: { deviceId: "saj_1", key: "charge_slot_1_days" },
        },
        {
            name: "an entity that is not SAJ Local",
            entityId: DAYS_ENTITY_ID,
            owner: null,
        },
        {
            name: "a tile without an entity",
            entityId: undefined,
            owner: { deviceId: "saj_1", key: "charge_slot_1_days" },
        },
    ])("is not offered for $name", ({ entityId, owner }) => {
        expect(supported(entityId, owner)).toBe(false);
    });

    it("lets the card feature picker ask about a tile's entity", () => {
        const hass = createFakeHass();

        expect(
            registration?.isSupported?.(hass, { entity_id: DAYS_ENTITY_ID }),
        ).toBe(true);
        expect(ownerOfEntity).toHaveBeenCalledWith({
            hass,
            entityId: DAYS_ENTITY_ID,
        });
    });
});

describe("saj-local-weekdays", () => {
    it("draws the weekday buttons with the entity name as the hidden label and the entity's weekdays", async () => {
        const feature = await mountFeature();
        const buttons = firstIn(feature, "saj-weekday-buttons");

        expect(buttons.labelHidden).toBe(true);
        expect(buttons.label).toBe("label(charge_slot_1_days)");
        expect(buttons.value).toBe(5);
    });

    it("shows no weekdays when the entity's state is not a number", async () => {
        vi.mocked(systemEntities).mockReturnValue(
            entityMap([
                entity("charge_slot_1_days", "number", "unknown", {
                    entityId: DAYS_ENTITY_ID,
                }),
            ]),
        );

        const feature = await mountFeature();

        expect(firstIn(feature, "saj-weekday-buttons").value).toBe(0);
    });

    it("looks the system's entities up through the entity's owner", async () => {
        const hass = createFakeHass();

        await mountFeature({ hass });

        expect(systemEntities).toHaveBeenCalledWith({
            hass,
            deviceId: "saj_1",
        });
    });

    it("writes the weekday number the buttons commit to the entity", async () => {
        const feature = await mountFeature();

        firstIn(feature, "saj-weekday-buttons").dispatchEvent(
            new CustomEvent("saj-commit", { detail: 21 }),
        );

        expect(setNumberRequest).toHaveBeenCalledWith(21);
        expect(trackerOf(feature).submit).toHaveBeenCalledWith({
            entityId: DAYS_ENTITY_ID,
            request: resultOf(setNumberRequest),
        });
    });

    it("keeps a press from opening the tile's more-info dialog", async () => {
        const feature = await mountFeature();
        const tileClicks: Event[] = [];
        document.body.addEventListener("click", (event) =>
            tileClicks.push(event),
        );

        firstIn(feature, "div").dispatchEvent(
            new MouseEvent("click", { bubbles: true, composed: true }),
        );

        expect(tileClicks).toEqual([]);
    });

    it("shows busy during the write and the refusal after it", async () => {
        const feature = await mountFeature();
        trackerOf(feature).isBusy.mockReturnValue(true);
        trackerOf(feature).errorOf.mockReturnValue("Refused");
        feature.requestUpdate();
        await feature.updateComplete;
        const buttons = firstIn(feature, "saj-weekday-buttons");

        expect(trackerOf(feature).isBusy).toHaveBeenCalledWith(DAYS_ENTITY_ID);
        expect(buttons.busy).toBe(true);
        expect(buttons.error).toBe("Refused");
    });

    it("shows no refusal when the write was not refused", async () => {
        const feature = await mountFeature();

        expect(firstIn(feature, "saj-weekday-buttons").error).toBe("");
    });

    it.each([
        {
            name: "changes are off",
            locked: true,
            unavailable: false,
            disabled: true,
        },
        {
            name: "changes are on",
            locked: false,
            unavailable: false,
            disabled: false,
        },
        {
            name: "the weekdays are unavailable",
            locked: false,
            unavailable: true,
            disabled: true,
        },
    ])(
        "disables the buttons: $disabled when $name",
        async ({ locked, unavailable, disabled }) => {
            vi.mocked(controlLock).mockReturnValue({ locked, entity: null });
            vi.mocked(isUnavailable).mockReturnValue(unavailable);

            const feature = await mountFeature();

            expect(controlLock).toHaveBeenCalledWith(entityMap([daysEntity]));
            expect(firstIn(feature, "saj-weekday-buttons").disabled).toBe(
                disabled,
            );
        },
    );

    it.each([
        {
            name: "hass",
            hass: null,
            entityId: DAYS_ENTITY_ID,
            owner: true,
            found: true,
        },
        {
            name: "an entity",
            hass: createFakeHass(),
            entityId: null,
            owner: true,
            found: true,
        },
        {
            name: "a SAJ Local owner",
            hass: createFakeHass(),
            entityId: DAYS_ENTITY_ID,
            owner: false,
            found: true,
        },
        {
            name: "a state",
            hass: createFakeHass(),
            entityId: DAYS_ENTITY_ID,
            owner: true,
            found: false,
        },
    ])(
        "draws nothing without $name",
        async ({ hass, entityId, owner, found }) => {
            if (!owner) {
                vi.mocked(ownerOfEntity).mockReturnValue(null);
            }
            if (!found) {
                vi.mocked(systemEntities).mockReturnValue(entityMap([]));
            }

            const feature = await mountFeature({ hass, entityId });

            expect(
                feature.shadowRoot?.querySelector("saj-weekday-buttons"),
            ).toBeNull();
        },
    );

    it("draws nothing without a tile context", async () => {
        const feature = await mount<ProbeFeature>(PROBE_TAG, {
            hass: createFakeHass(),
        });

        expect(elementsIn(feature, "saj-weekday-buttons")).toEqual([]);
    });
});

describe("saj-local-weekdays contracts", () => {
    it("keeps its configuration and offers a stub for the feature picker", async () => {
        const feature = await mountFeature();
        const stub = SajWeekdaysFeature.getStubConfig();

        feature.setConfig(stub);

        expect(feature.config).toBe(stub);
        expect(stub.type).toBe(`custom:${WEEKDAYS_FEATURE_TAG}`);
    });

    it("lets its tracker call services with the feature's current hass and refresh the feature", async () => {
        const hass = createFakeHass();
        const feature = await mountFeature({ hass });
        const provider: unknown = Reflect.get(
            feature.controlTracker,
            "hassProvider",
        );

        expect(feature.controlTracker).toMatchObject({ host: feature });
        if (typeof provider !== "function") {
            throw new Error("The tracker has no hass provider");
        }
        expect(Reflect.apply(provider, undefined, [])).toBe(hass);
    });

    it("watches the system of the tile's entity", async () => {
        const feature = await mountFeature();

        expect(feature.watched()).toBe("saj_1");
    });

    it.each([
        { name: "hass", hass: null, entityId: DAYS_ENTITY_ID },
        { name: "a tile entity", hass: createFakeHass(), entityId: null },
    ])("watches no system without $name", async ({ hass, entityId }) => {
        const feature = await mountFeature({ hass, entityId });

        expect(feature.watched()).toBeUndefined();
    });

    it("watches no system for an entity that is not SAJ Local", async () => {
        const feature = await mountFeature();
        vi.mocked(ownerOfEntity).mockReturnValue(null);

        expect(feature.watched()).toBeUndefined();
    });

    it("registers itself in the card feature picker as not configurable", () => {
        expect(registration).toMatchObject({
            type: WEEKDAYS_FEATURE_TAG,
            configurable: false,
        });
    });
});
