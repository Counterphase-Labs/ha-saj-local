import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { entitiesModule } from "../fakes/entities";
import {
    editorModule,
    faultsModule,
    operatingModule,
    registrationModule,
    stylesModule,
    systemCardModule,
} from "../fakes/modules";

import { SajLocalStatusCard } from "../../src/cards/status-card";
import { isOn, isUnavailable } from "../../src/system/entities";
import { activeFaultSummaries } from "../../src/system/faults";
import { operatingTone } from "../../src/system/operating";
import { entity, entityMap } from "../fakes/entities";
import {
    mountCard,
    requiredRowFor,
    rowFor,
    rowLabelled,
    rowsOf,
    describeCardPicker,
} from "./support";

vi.mock("../../src/registration", () => registrationModule());
vi.mock("../../src/system/entities", () => entitiesModule());
vi.mock("../../src/system/faults", () => faultsModule());
vi.mock("../../src/system/operating", () => operatingModule());
vi.mock("../../src/ui/styles", () => stylesModule());
vi.mock("../../src/cards/editor", () => editorModule());
vi.mock("../../src/cards/system-card", () => systemCardModule());

const TAG = "saj-local-status-card";

describeCardPicker({ tag: TAG, card: SajLocalStatusCard });

const mode = entity("operating_mode", "sensor", "operating");
const applicationMode = entity("application_mode", "select", "time_of_use");
const applicationModeActive = entity(
    "application_mode_active",
    "sensor",
    "self_consumption",
);
const soc = entity("battery_soc", "sensor", "80");
const temperature = entity("inverter_temperature", "sensor", "41");
const pvToday = entity("pv_energy_today", "sensor", "12");
const inverterFault = entity("inverter_fault", "binary_sensor", "off");
const batteryFault = entity("battery_fault", "binary_sensor", "off");
const allowed = entity("control_allowed", "binary_sensor", "on");

const mountStatus = (
    entities: ReturnType<typeof entity>[],
    config: { show_energy?: boolean } = {},
    dimmed = false,
) => mountCard({ tag: TAG, config, entities, dimmed });

beforeEach(() => {
    vi.mocked(activeFaultSummaries).mockReturnValue([]);
});

afterEach(() => {
    document.body.replaceChildren();
});

describe("status card parts", () => {
    it("draws a row for each key present and none for absent keys", async () => {
        const card = await mountStatus([mode, soc, pvToday]);

        expect(rowsOf(card)).toHaveLength(3);
        expect(rowFor({ card, entity: temperature })).toBeUndefined();
        expect(rowFor({ card, entity: soc })).toBeDefined();
    });

    it("colours the operating state with the tone of the state", async () => {
        const card = await mountStatus([mode]);

        expect(operatingTone).toHaveBeenCalledWith("operating");
        expect(requiredRowFor({ card, entity: mode }).tone).toBe(
            "tone(operating)",
        );
    });

    it("shows the application mode and the mode running now only when they differ", async () => {
        const different = await mountStatus([
            applicationMode,
            applicationModeActive,
        ]);
        const same = await mountStatus([
            applicationMode,
            { ...applicationModeActive, state: applicationMode.state },
        ]);

        expect(
            requiredRowFor({ card: different, entity: applicationModeActive })
                .label,
        ).toBe("mode_running_now");
        expect(rowFor({ card: same, entity: applicationModeActive })).toBe(
            undefined,
        );
        expect(rowFor({ card: same, entity: applicationMode })).toBeDefined();
    });

    it("leaves out the mode running now without an application mode", async () => {
        const card = await mountStatus([mode, applicationModeActive]);

        expect(rowFor({ card, entity: applicationModeActive })).toBeUndefined();
    });

    it.each([
        { config: {}, drawn: true },
        { config: { show_energy: true }, drawn: true },
        { config: { show_energy: false }, drawn: false },
    ])(
        "draws today's energy with $config: $drawn",
        async ({ config, drawn }) => {
            const card = await mountStatus([mode, pvToday], config);

            expect(rowFor({ card, entity: pvToday }) !== undefined).toBe(drawn);
        },
    );

    it("passes the dimming of the card to every row", async () => {
        const card = await mountStatus([mode, soc], {}, true);

        expect(rowsOf(card).every((row) => row.dimmed)).toBe(true);
    });
});

describe("status card faults and changes", () => {
    it("says there are no faults without a tap target", async () => {
        const card = await mountStatus([mode, inverterFault, batteryFault]);
        const row = rowLabelled({ card, label: "faults" });

        expect(row.value).toBe("no_faults");
        expect(row.entityId).toBeUndefined();
        expect(row.tone).toBeUndefined();
        expect(row.icon).toBe("ok");
    });

    it("counts the faults that are on, in the error colour, and opens the first one that is on", async () => {
        const active = [
            {
                ...inverterFault,
                state: { ...inverterFault.state, state: "on" },
            },
            { ...batteryFault, state: { ...batteryFault.state, state: "on" } },
        ];
        vi.mocked(activeFaultSummaries).mockReturnValue(active);

        const card = await mountStatus([mode, inverterFault, batteryFault]);
        const row = rowLabelled({ card, label: "faults" });

        expect(row.value).toBe('faults_count:{"count":2}');
        expect(row.tone).toBe("error");
        expect(row.icon).toBe("fault");
        expect(row.entityId).toBe(inverterFault.entityId);
    });

    it("asks for the active summaries of the system's entities", async () => {
        await mountStatus([mode, inverterFault]);

        expect(activeFaultSummaries).toHaveBeenCalledWith(
            entityMap([mode, inverterFault]),
        );
    });

    it("leaves out the fault row for a system without fault summaries", async () => {
        const card = await mountStatus([mode]);

        expect(rowsOf(card).some((row) => row.label === "faults")).toBe(false);
    });

    it.each([
        {
            on: true,
            unavailable: false,
            value: "changes_allowed",
            tone: "success",
        },
        {
            on: false,
            unavailable: false,
            value: "changes_off",
            tone: "warning",
        },
        { on: false, unavailable: true, value: "unavailable", tone: "warning" },
    ])(
        "shows changes as $value when control_allowed is on: $on and unavailable: $unavailable",
        async ({ on, unavailable, value, tone }) => {
            vi.mocked(isOn).mockReturnValue(on);
            vi.mocked(isUnavailable).mockReturnValue(unavailable);

            const card = await mountStatus([mode, allowed]);
            const row = requiredRowFor({ card, entity: allowed });

            expect(row.value).toBe(value);
            expect(row.tone).toBe(tone);
            expect(row.label).toBe("changes");
            expect(row.icon).toBe("lock");
        },
    );

    it("leaves out the changes row without a control_allowed entity", async () => {
        const card = await mountStatus([mode]);

        expect(rowsOf(card).some((row) => row.label === "changes")).toBe(false);
    });
});

describe("status card contracts", () => {
    it("offers the energy option as a switch", () => {
        expect(SajLocalStatusCard.getConfigForm()).toEqual({
            fields: [{ kind: "boolean", name: "show_energy", fallback: true }],
        });
    });

    it("has a size", async () => {
        const card = await mountStatus([mode]);

        expect(card.getCardSize()).toBeGreaterThan(0);
    });

    it("shows the entities of the keys it draws, leaving today's energy out when asked", async () => {
        const entities = entityMap([
            mode,
            soc,
            pvToday,
            inverterFault,
            allowed,
        ]);
        const withEnergy = await mountStatus([mode]);
        const withoutEnergy = await mountStatus([mode], { show_energy: false });

        expect(withEnergy.shownEntities(entities)).toEqual([
            mode,
            soc,
            pvToday,
            inverterFault,
            allowed,
        ]);
        expect(withoutEnergy.shownEntities(entities)).toEqual([
            mode,
            soc,
            inverterFault,
            allowed,
        ]);
    });
});
