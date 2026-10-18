import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
    controlElementModule,
    controlModule,
    editorModule,
    faultsModule,
    localizeModule,
    registrationModule,
    systemCardModule,
} from "../fakes/modules";

import { SajLocalFaultsCard } from "../../src/cards/faults-card";
import { relativeTimeText } from "../../src/i18n/localize";
import { pressButtonRequest } from "../../src/system/control";
import type { SystemEntity } from "../../src/system/entities";
import { faultGroups, type FaultGroup } from "../../src/system/faults";
import { entity } from "../fakes/entities";
import {
    firstIn,
    mountCard,
    requiredRowFor,
    rowsOf,
    type CardUnderTest,
    buttonIn,
    describeCardPicker,
} from "./support";
import { resultOf, trackerMocks } from "../fakes/mocks";

vi.mock("../../src/i18n/localize", () => localizeModule());
vi.mock("../../src/registration", () => registrationModule());
vi.mock("../../src/system/control", () => controlModule());
vi.mock("../../src/system/faults", () => faultsModule());
vi.mock("../../src/ui/control-element", () => controlElementModule());
vi.mock("../../src/cards/editor", () => editorModule());
vi.mock("../../src/cards/system-card", () => systemCardModule());

const TAG = "saj-local-faults-card";

describeCardPicker({ tag: TAG, card: SajLocalFaultsCard });
const FAULT_TIME = "2026-10-17T10:00:00+00:00";
const NOW = new Date("2026-10-17T10:05:00+00:00");

const binary = (key: string, state: string): SystemEntity =>
    entity(key, "binary_sensor", state, { lastChanged: FAULT_TIME });

const group = ({
    id,
    summary,
    rows = [],
}: {
    id: FaultGroup["id"];
    summary: SystemEntity;
    rows?: { entity: SystemEntity; unrecognised?: boolean }[];
}): FaultGroup => ({
    id,
    summary,
    active: summary.state.state === "on",
    rows: rows.map((row) => ({
        entity: row.entity,
        since: new Date(row.entity.state.last_changed),
        unrecognised: row.unrecognised ?? false,
    })),
});

const inverter = (state: string, rows?: Parameters<typeof group>[0]["rows"]) =>
    group({ id: "inverter", summary: binary("inverter_fault", state), rows });
const battery = (state: string, rows?: Parameters<typeof group>[0]["rows"]) =>
    group({ id: "battery", summary: binary("battery_fault", state), rows });
const ev = (state: string) =>
    group({ id: "ev", summary: binary("ev_fault", state) });

const clearButton = entity("clear_current_fault", "button", "unknown");

const mountFaults = (
    groups: FaultGroup[],
    {
        config = {},
        extra = [],
        locked = false,
    }: {
        config?: { show_clear_groups?: boolean };
        extra?: SystemEntity[];
        locked?: boolean;
    } = {},
) => {
    vi.mocked(faultGroups).mockReturnValue(groups);
    return mountCard({
        tag: TAG,
        config,
        entities: [...groups.map(({ summary }) => summary), ...extra],
        locked,
    });
};

const headings = (card: CardUnderTest): string[] =>
    [...(card.shadowRoot?.querySelectorAll("h3") ?? [])].map((heading) =>
        heading.textContent.trim(),
    );

beforeEach(() => {
    vi.useFakeTimers({ toFake: ["Date"] });
    vi.setSystemTime(NOW);
});

afterEach(() => {
    vi.useRealTimers();
    document.body.replaceChildren();
});

describe("faults card groups", () => {
    it("draws one group for each group it is given", async () => {
        const overvoltage = binary("inverter_fault_overvoltage", "on");

        const card = await mountFaults([
            inverter("on", [{ entity: overvoltage }]),
            ev("off"),
        ]);

        expect(headings(card)).toEqual(["inverter"]);
        expect(rowsOf(card).some((row) => row.label === "ev_charger")).toBe(
            true,
        );
        expect(rowsOf(card).some((row) => row.label === "battery")).toBe(false);
    });

    it("lists the rows of a group with how long ago each turned on, in the error colour", async () => {
        const overvoltage = binary("inverter_fault_overvoltage", "on");

        const card = await mountFaults([
            inverter("on", [{ entity: overvoltage }]),
        ]);
        const row = requiredRowFor({ card, entity: overvoltage });

        expect(relativeTimeText).toHaveBeenCalledWith({
            from: new Date(FAULT_TIME),
            now: NOW,
            language: "en",
        });
        expect(row.value).toBe("relative:en");
        expect(row.tone).toBe("error");
        expect(row.icon).toBe("fault");
    });

    it("lists the battery group's rows under the battery heading", async () => {
        const packFault = binary("battery_pack2_fault", "on");

        const card = await mountFaults([
            battery("on", [{ entity: packFault }]),
        ]);

        expect(headings(card)).toEqual(["battery"]);
        expect(requiredRowFor({ card, entity: packFault })).toBeDefined();
    });

    it("keeps the rows of each group under its own heading", async () => {
        const card = await mountFaults([
            inverter("on", [{ entity: binary("inverter_fault_a", "on") }]),
            battery("on", [{ entity: binary("battery_pack1_fault", "on") }]),
        ]);

        expect(headings(card)).toEqual(["inverter", "battery"]);
    });

    it("points an unrecognised fault at the diagnostics download", async () => {
        const card = await mountFaults([
            inverter("on", [
                {
                    entity: binary("inverter_fault_unrecognised", "on"),
                    unrecognised: true,
                },
            ]),
        ]);

        expect(firstIn(card, ".hint").textContent).toBe("see_diagnostics");
    });

    it("has no diagnostics hint for recognised faults", async () => {
        const card = await mountFaults([
            inverter("on", [{ entity: binary("inverter_fault_a", "on") }]),
        ]);

        expect(card.shadowRoot?.querySelector(".hint")).toBeNull();
    });

    it("lists only the heading of a group that is on without any detail row", async () => {
        const card = await mountFaults([inverter("on")]);

        expect(rowsOf(card)).toEqual([]);
        expect(headings(card)).toEqual(["inverter"]);
    });

    it("shows No active faults in the success colour for a group without faults", async () => {
        const quiet = inverter("off");

        const card = await mountFaults([quiet]);
        const row = requiredRowFor({ card, entity: quiet.summary });

        expect(row.value).toBe("no_active_faults");
        expect(row.tone).toBe("success");
        expect(row.label).toBe("inverter");
        expect(row.icon).toBe("ok");
    });

    it("hides groups without faults when asked", async () => {
        const quiet = await mountFaults([inverter("off"), battery("off")], {
            config: { show_clear_groups: false },
        });
        const mixed = await mountFaults([inverter("on"), battery("off")], {
            config: { show_clear_groups: false },
        });

        expect(rowsOf(quiet)).toEqual([]);
        expect(headings(quiet)).toEqual([]);
        expect(headings(mixed)).toEqual(["inverter"]);
        expect(rowsOf(mixed).some((row) => row.label === "battery")).toBe(
            false,
        );
    });

    it("passes the dimming of the card to the rows of groups without faults", async () => {
        vi.mocked(faultGroups).mockReturnValue([inverter("off")]);
        const card = await mountCard({
            tag: TAG,
            entities: [binary("inverter_fault", "off")],
            dimmed: true,
        });

        expect(rowsOf(card)[0]?.dimmed).toBe(true);
    });
});

describe("faults card clear fault", () => {
    const mountClearable = async (): Promise<CardUnderTest> => {
        vi.mocked(faultGroups).mockReturnValue([active()]);
        return mountCard({
            tag: TAG,
            entities: [binary("inverter_fault", "on"), clearButton],
        });
    };

    const active = () =>
        inverter("on", [
            { entity: binary("inverter_fault_overvoltage", "on") },
        ]);

    const pressButton = (card: CardUnderTest) => buttonIn(card, ".clear");

    it("presses the clear button of the system when asked", async () => {
        const card = await mountFaults([active()], { extra: [clearButton] });

        pressButton(card).click();

        expect(pressButtonRequest).toHaveBeenCalledTimes(1);
        expect(trackerMocks(card.tracker).submit).toHaveBeenCalledWith({
            entityId: clearButton.entityId,
            request: resultOf(pressButtonRequest),
        });
    });

    it.each([
        {
            name: "no clear button entity",
            groups: () => [inverter("on")],
            extra: [],
        },
        {
            name: "the inverter group without faults",
            groups: () => [inverter("off")],
            extra: [clearButton],
        },
        {
            name: "only another group with faults",
            groups: () => [
                group({ id: "ev", summary: binary("ev_fault", "on") }),
                inverter("off"),
            ],
            extra: [clearButton],
        },
    ])("offers no clear action with $name", async ({ groups, extra }) => {
        const card = await mountFaults(groups(), { extra });

        expect(card.shadowRoot?.querySelector(".clear")).toBeNull();
    });

    it("keeps the clear action enabled while changes are allowed", async () => {
        const card = await mountFaults([active()], { extra: [clearButton] });

        expect(pressButton(card).disabled).toBe(false);
        expect(card.shadowRoot?.querySelector("saj-empty-state")).toBeNull();
    });

    it("locks the clear action and shows the locked message while changes are off", async () => {
        const card = await mountFaults([active()], {
            extra: [clearButton],
            locked: true,
        });

        expect(pressButton(card).disabled).toBe(true);
        expect(firstIn(card, "saj-empty-state")).toMatchObject({
            locked: true,
        });
    });

    it("shows no locked message while changes are off when there is nothing to clear", async () => {
        const card = await mountFaults([active()], { locked: true });

        expect(card.shadowRoot?.querySelector("saj-empty-state")).toBeNull();
    });

    it("disables the clear action with a busy indicator while the call runs", async () => {
        const card = await mountClearable();
        trackerMocks(card.tracker).isBusy.mockReturnValue(true);
        card.requestUpdate();
        await card.updateComplete;

        expect(pressButton(card).disabled).toBe(true);
        expect(trackerMocks(card.tracker).isBusy).toHaveBeenCalledWith(
            clearButton.entityId,
        );
        expect(firstIn(card, ".busy").getAttribute("role")).toBe("status");
    });

    it("shows no busy indicator while idle", async () => {
        const card = await mountFaults([active()], { extra: [clearButton] });

        expect(card.shadowRoot?.querySelector(".busy")).toBeNull();
    });

    it("shows the message of a refused clear under the button", async () => {
        const card = await mountClearable();
        trackerMocks(card.tracker).errorOf.mockReturnValue(
            "Writing is not allowed",
        );
        card.requestUpdate();
        await card.updateComplete;

        expect(firstIn(card, ".error").textContent).toBe(
            "Writing is not allowed",
        );
    });

    it("shows no error when the clear was not refused", async () => {
        const card = await mountFaults([active()], { extra: [clearButton] });

        expect(card.shadowRoot?.querySelector(".error")).toBeNull();
    });
});

describe("faults card contracts", () => {
    it("offers the groups without faults option as a switch", () => {
        expect(SajLocalFaultsCard.getConfigForm()).toEqual({
            fields: [
                { kind: "boolean", name: "show_clear_groups", fallback: true },
            ],
        });
    });

    it("shows the summary of every group it has", async () => {
        const groups = [inverter("on"), ev("off")];
        const card = await mountFaults(groups);

        expect(
            card.shownEntities(new Map([["any", binary("any", "on")]])),
        ).toEqual(groups.map(({ summary }) => summary));
        expect(card.getCardSize()).toBeGreaterThan(0);
    });
});
