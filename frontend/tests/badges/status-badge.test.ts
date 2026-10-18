import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { entitiesModule } from "../fakes/entities";
import {
    actionsModule,
    editorModule,
    faultsModule,
    operatingModule,
    redrawingDevices,
    registrationModule,
    stylesModule,
    systemElementModule,
} from "../fakes/modules";

import { fireMoreInfo } from "../../src/actions";
import { SajStatusBadge } from "../../src/badges/status-badge";
import { registerBadge } from "../../src/registration";
import {
    allUnavailable,
    listSystemDevices,
    systemEntities,
    type SystemEntity,
} from "../../src/system/entities";
import { activeFaultSummaries } from "../../src/system/faults";
import { operatingTone } from "../../src/system/operating";
import { toneColour } from "../../src/ui/styles";
import { entity, entityMap } from "../fakes/entities";
import { createFakeHass, fakeDevice } from "../fakes/hass";
import { inShadow, mount, shadowButton } from "../ui/mount";

vi.mock("../../src/actions", () => actionsModule());
vi.mock("../../src/cards/editor", () => editorModule());
vi.mock("../../src/registration", () => registrationModule());
vi.mock("../../src/system/entities", () => entitiesModule());
vi.mock("../../src/system/faults", () => faultsModule());
vi.mock("../../src/ui/icon", () => ({}));
vi.mock("../../src/system/operating", () => operatingModule());
vi.mock("../../src/ui/styles", () => stylesModule());
vi.mock("../../src/ui/system-element", () => systemElementModule());

const BADGE_ELEMENT = "saj-local-status-badge";
const BADGE_TYPE = "custom:saj-local-status-badge";

type Badge = HTMLElementTagNameMap["saj-local-status-badge"];

const [registration] = vi
    .mocked(registerBadge)
    .mock.calls.map(([entry]) => entry);

const operating = (state: string): SystemEntity =>
    entity("operating_mode", "sensor", state);
const fault = (key: string, state: string): SystemEntity =>
    entity(key, "binary_sensor", state);

const badgeFor = async (
    entities: SystemEntity[],
    activeFaults: SystemEntity[] = [],
): Promise<Badge> => {
    vi.mocked(systemEntities).mockReturnValue(entityMap(entities));
    vi.mocked(activeFaultSummaries).mockReturnValue(activeFaults);
    const badge = await mount<Badge>(BADGE_ELEMENT, {
        hass: createFakeHass(),
    });
    badge.setConfig({ type: BADGE_TYPE, device: "saj_1" });
    await badge.updateComplete;
    return badge;
};

beforeEach(() => {
    vi.mocked(allUnavailable).mockReturnValue(false);
});

afterEach(() => {
    redrawingDevices.clear();
    document.body.replaceChildren();
    vi.mocked(allUnavailable).mockReset();
});

describe("saj-local-status-badge", () => {
    it("shows the operating state in the colour of the state", async () => {
        const mode = operating("operating");

        const badge = await badgeFor([mode]);

        expect(inShadow(badge, ".state").textContent).toBe("operating");
        expect(operatingTone).toHaveBeenCalledWith("operating");
        expect(toneColour).toHaveBeenCalledWith("tone(operating)");
        expect(inShadow(badge, ".state").getAttribute("style")).toContain(
            "var(--tone-tone(operating))",
        );
    });

    it("opens more-info of the operating state when tapped", async () => {
        const mode = operating("operating");
        const badge = await badgeFor([mode]);

        shadowButton(badge).click();

        expect(fireMoreInfo).toHaveBeenCalledWith({
            host: badge,
            entityId: mode.entityId,
        });
    });

    it("counts the active fault summaries in the error colour", async () => {
        const badge = await badgeFor(
            [operating("operating")],
            [fault("inverter_fault", "on"), fault("battery_fault", "on")],
        );

        const faults = inShadow(badge, ".faults");

        expect(faults.textContent).toBe('faults_count:{"count":2}');
        expect(toneColour).toHaveBeenCalledWith("error");
        expect(faults.getAttribute("style")).toContain("var(--tone-error)");
    });

    it("shows no fault count while no summary is on", async () => {
        const badge = await badgeFor([operating("operating")]);

        expect(badge.shadowRoot?.querySelector(".faults")).toBeNull();
    });

    it("says the system is not answering and dims when everything it shows is unavailable", async () => {
        vi.mocked(allUnavailable).mockReturnValue(true);

        const badge = await badgeFor(
            [operating("unavailable"), fault("inverter_fault", "unavailable")],
            [fault("inverter_fault", "on")],
        );

        expect(inShadow(badge, ".state").textContent).toBe("not_answering");
        expect(shadowButton(badge).classList).toContain("dimmed");
        expect(badge.shadowRoot?.querySelector(".faults")).toBeNull();
    });

    it("judges the answering of the operating state and the fault summaries it has", async () => {
        const mode = operating("operating");
        const summary = fault("inverter_fault", "off");

        await badgeFor([mode, summary, entity("pv_power", "sensor", "1")]);

        expect(allUnavailable).toHaveBeenCalledWith([mode, summary]);
    });

    it("shows the fault count without a tap target when the system has no operating state", async () => {
        const badge = await badgeFor(
            [fault("battery_fault", "on")],
            [fault("battery_fault", "on")],
        );

        expect(badge.shadowRoot?.querySelector("button")).toBeNull();
        expect(inShadow(badge, ".state").textContent.trim()).toBe("");
        expect(inShadow(badge, ".faults").textContent).toBe(
            'faults_count:{"count":1}',
        );
    });

    it.each([
        { name: "no device is chosen", config: { type: BADGE_TYPE } },
        {
            name: "the device has no SAJ Local entity",
            config: { type: BADGE_TYPE, device: "other" },
        },
    ])("asks to choose a system when $name", async ({ config }) => {
        const badge = await badgeFor([operating("operating")]);
        if (config.device === "other") {
            vi.mocked(systemEntities).mockReturnValue(entityMap([]));
        }
        badge.setConfig(config);
        await badge.updateComplete;

        expect(inShadow(badge, ".badge").textContent.trim()).toBe(
            "choose_system",
        );
    });

    it("asks to choose a system before the first hass arrives", async () => {
        const badge = await mount<Badge>(BADGE_ELEMENT);
        badge.setConfig({ type: BADGE_TYPE, device: "saj_1" });
        await badge.updateComplete;

        expect(inShadow(badge, ".badge").textContent.trim()).toBe(
            "choose_system",
        );
    });

    it.each([
        { name: "its own system", device: "saj_1", redraws: true },
        { name: "another system", device: "saj_2", redraws: false },
    ])(
        "redraws for a new hass only when a state of $name changed",
        async ({ device, redraws }) => {
            const badge = await badgeFor([operating("operating")]);
            vi.mocked(systemEntities).mockReturnValue(
                entityMap([operating("charging")]),
            );
            redrawingDevices.add(device);

            badge.hass = createFakeHass();
            await badge.updateComplete;

            expect(inShadow(badge, ".state").textContent).toBe(
                redraws ? "charging" : "operating",
            );
        },
    );

    it("keeps asking to choose a system when a new hass arrives before it is configured", async () => {
        const badge = await mount<Badge>(BADGE_ELEMENT, {
            hass: createFakeHass(),
        });
        redrawingDevices.add("saj_1");
        vi.mocked(systemEntities).mockReturnValue(
            entityMap([operating("charging")]),
        );
        badge.hass = createFakeHass();
        await badge.updateComplete;

        expect(inShadow(badge, ".badge").textContent.trim()).toBe(
            "choose_system",
        );
    });
});

describe("saj-local-status-badge contracts", () => {
    it("registers itself in the badge picker", () => {
        expect(registration).toMatchObject({ type: BADGE_ELEMENT });
    });

    it("asks for a device of the integration and nothing else", () => {
        expect(SajStatusBadge.getConfigForm()).toEqual({ fields: [] });
    });

    it("starts from the first SAJ Local device", () => {
        vi.mocked(listSystemDevices).mockReturnValue([fakeDevice("saj_1")]);

        expect(SajStatusBadge.getStubConfig(createFakeHass())).toEqual({
            type: BADGE_TYPE,
            device: "saj_1",
        });
    });

    it("starts without a device when the home has no SAJ Local system", () => {
        vi.mocked(listSystemDevices).mockReturnValue([]);

        expect(
            SajStatusBadge.getStubConfig(createFakeHass()).device,
        ).toBeUndefined();
    });
});
