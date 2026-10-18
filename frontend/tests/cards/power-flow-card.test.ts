import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
    actionsModule,
    editorModule,
    iconsModule,
    operatingModule,
    powerModule,
    registrationModule,
    stylesModule,
    systemCardModule,
} from "../fakes/modules";

import { fireMoreInfo } from "../../src/actions";
import {
    POWER_FLOW_SCOPES,
    SajLocalPowerFlowCard,
} from "../../src/cards/power-flow-card";
import type { SystemEntity } from "../../src/system/entities";
import { operatingTone } from "../../src/system/operating";
import {
    flowDurationSeconds,
    powerFlow,
    wattsOf,
    type PowerFlow,
} from "../../src/system/power";
import { toneColour } from "../../src/ui/styles";
import { entity, entityMap } from "../fakes/entities";
import {
    elementsIn,
    firstIn,
    mountCard,
    type CardUnderTest,
    describeCardPicker,
} from "./support";

vi.mock("../../src/actions", () => actionsModule());
vi.mock("../../src/registration", () => registrationModule());
vi.mock("../../src/system/operating", () => operatingModule());
vi.mock("../../src/system/power", () => powerModule());
vi.mock("../../src/ui/icons", () => iconsModule());
vi.mock("../../src/ui/styles", () => stylesModule());
vi.mock("../../src/cards/editor", () => editorModule());
vi.mock("../../src/cards/system-card", () => systemCardModule());

const TAG = "saj-local-power-flow-card";

describeCardPicker({
    tag: TAG,
    card: SajLocalPowerFlowCard,
    startingOptions: { scope: "system" },
});

const reading = (key: string, state: string): SystemEntity =>
    entity(key, "sensor", state);

const mountFlow = (
    entities: SystemEntity[],
    config: Record<string, unknown> = {},
    dimmed = false,
) => mountCard({ tag: TAG, config, entities, dimmed });

const labelsOf = (card: CardUnderTest): string[] =>
    elementsIn(card, ".label").map((label) => label.textContent);

const secondariesOf = (card: CardUnderTest): string[] =>
    elementsIn(card, ".secondary").map((label) => label.textContent);

const valuesOf = (card: CardUnderTest): string[] =>
    elementsIn(card, ".value").map((label) => label.textContent);

const lineOf = ({
    card,
    label,
}: {
    card: CardUnderTest;
    label: string;
}): Element => {
    const line = elementsIn(card, ".line")[labelsOf(card).indexOf(label)];
    if (line === undefined) {
        throw new Error(`No line for ${label}`);
    }
    return line;
};

const press = (target: Element, key: string): KeyboardEvent => {
    const event = new KeyboardEvent("keydown", {
        key,
        bubbles: true,
        cancelable: true,
    });
    target.dispatchEvent(event);
    return event;
};

const flowsOf = (flows: Partial<Record<string, PowerFlow>>): void => {
    vi.mocked(powerFlow).mockImplementation(
        ({ kind }) => flows[kind] ?? { state: "idle", line: "none" },
    );
};

beforeEach(() => {
    vi.mocked(wattsOf).mockImplementation((item) => {
        const value = Number(item.state.state);
        return Number.isFinite(value) ? value : null;
    });
    flowsOf({});
});

afterEach(() => {
    document.body.replaceChildren();
});

describe("power flow card nodes", () => {
    it("draws a node for each key present and none for absent keys, with the inverter last", async () => {
        const card = await mountFlow([
            reading("pv_power", "1000"),
            reading("load_power", "400"),
            entity("operating_mode", "sensor", "operating"),
        ]);

        expect(labelsOf(card)).toEqual(["solar", "home", "inverter"]);
        expect(elementsIn(card, ".line")).toHaveLength(2);
    });

    it("draws every node of a fully equipped system", async () => {
        const card = await mountFlow([
            reading("pv_power", "1"),
            reading("battery_power", "1"),
            reading("grid_power", "1"),
            reading("load_power", "1"),
            reading("ev_power", "1"),
            reading("backup_load_power", "1"),
            reading("meter_b_power", "1"),
            entity("operating_mode", "sensor", "operating"),
        ]);

        expect(labelsOf(card)).toEqual([
            "solar",
            "battery",
            "grid",
            "home",
            "ev_charger",
            "backup_load",
            "meter_b",
            "inverter",
        ]);
    });

    it.each([
        { config: {}, expected: ["ev_charger", "backup_load", "meter_b"] },
        {
            config: { show_optional: true },
            expected: ["ev_charger", "backup_load", "meter_b"],
        },
        { config: { show_optional: false }, expected: [] },
    ])(
        "draws the optional equipment with $config",
        async ({ config, expected }) => {
            const card = await mountFlow(
                [
                    reading("pv_power", "1"),
                    reading("ev_power", "1"),
                    reading("backup_load_power", "1"),
                    reading("meter_b_power", "1"),
                ],
                config,
            );

            expect(labelsOf(card)).toEqual(["solar", ...expected]);
        },
    );

    it("puts the optional nodes in one row below the battery", async () => {
        const card = await mountFlow([
            reading("battery_power", "1"),
            reading("ev_power", "1"),
            reading("meter_b_power", "1"),
        ]);
        const boxes = elementsIn(card, ".box");
        const tops = boxes.map((box) => Number(box.getAttribute("y")));
        const lefts = boxes.map((box) => Number(box.getAttribute("x")));

        expect(tops[1]).toBe(tops[2]);
        expect(tops[1]).toBeGreaterThan(tops[0] ?? Infinity);
        expect(lefts[1]).not.toBe(lefts[2]);
    });

    it("reads the system keys by default and the parallel keys with the parallel scope", async () => {
        const entities = [
            reading("pv_power", "100"),
            reading("parallel_pv_power", "900"),
            reading("battery_soc", "10"),
            reading("parallel_battery_soc", "90"),
            reading("battery_power", "1"),
            reading("parallel_battery_power", "1"),
        ];

        const system = await mountFlow(entities);
        const parallel = await mountFlow(entities, { scope: "parallel" });

        expect(valuesOf(system)[0]).toBe("value(pv_power)");
        expect(secondariesOf(system)[1]).toContain("value(battery_soc)");
        expect(valuesOf(parallel)[0]).toBe("value(parallel_pv_power)");
        expect(secondariesOf(parallel)[1]).toContain(
            "value(parallel_battery_soc)",
        );
    });

    it("shows the value of battery and grid as an absolute number and of the others as it is", async () => {
        const card = await mountFlow([
            reading("pv_power", "1"),
            reading("battery_power", "1"),
            reading("grid_power", "1"),
            reading("load_power", "1"),
        ]);

        expect(valuesOf(card)).toEqual([
            "value(pv_power)",
            "value(battery_power,absolute)",
            "value(grid_power,absolute)",
            "value(load_power)",
        ]);
    });

    it("shows the inverter state in the colour of its operating state", async () => {
        const card = await mountFlow([
            entity("operating_mode", "sensor", "fault"),
        ]);

        expect(valuesOf(card)).toEqual(["value(operating_mode)"]);
        expect(operatingTone).toHaveBeenCalledWith("fault");
        expect(toneColour).toHaveBeenCalledWith("tone(fault)");
        expect(firstIn(card, ".value").getAttribute("style")).toContain(
            "var(--tone-tone(fault))",
        );
    });

    it("shows the charger status beneath the EV charger", async () => {
        const card = await mountFlow([
            reading("ev_power", "7000"),
            entity("ev_status", "sensor", "charging"),
        ]);

        expect(secondariesOf(card)).toEqual(["value(ev_status)"]);
    });
});

describe("power flow card parallel scope", () => {
    it("shows the empty state on a system without parallel readings", async () => {
        const card = await mountFlow(
            [
                reading("pv_power", "100"),
                entity("operating_mode", "sensor", "x"),
            ],
            { scope: "parallel" },
        );

        expect(firstIn(card, "saj-empty-state")).toMatchObject({
            kind: "entity_kind_reading",
        });
        expect(card.shadowRoot?.querySelector("svg")).toBeNull();
    });

    it("shows what a parallel system has, and the inverter", async () => {
        const hub = entity("operating_mode", "sensor", "operating");
        const parallelSolar = reading("parallel_pv_power", "100");
        const card = await mountFlow([parallelSolar, hub], {
            scope: "parallel",
        });

        expect(card.shownEntities(entityMap([parallelSolar, hub]))).toEqual([
            hub,
            parallelSolar,
        ]);
    });

    it("keeps the readings that are the same in both scopes out of the test for parallel readings", async () => {
        const card = await mountFlow([reading("ev_power", "1")], {
            scope: "parallel",
        });

        expect(
            card.shadowRoot?.querySelector("saj-empty-state"),
        ).not.toBeNull();
    });
});

describe("power flow card lines", () => {
    it.each([
        { line: "to_inverter", reverse: false },
        { line: "from_inverter", reverse: true },
    ] as const)(
        "animates a line the flow says runs $line, reversed: $reverse",
        async ({ line, reverse }) => {
            flowsOf({ solar: { state: "producing", line } });

            const card = await mountFlow([reading("pv_power", "500")]);
            const drawn = lineOf({ card, label: "solar" });

            expect(drawn.classList.contains("active")).toBe(true);
            expect(drawn.classList.contains("idle")).toBe(false);
            expect(drawn.classList.contains("reverse")).toBe(reverse);
        },
    );

    it("asks the flow of each node with its kind and watts", async () => {
        await mountFlow([
            reading("pv_power", "500"),
            reading("battery_power", "-20"),
            reading("grid_power", "-30"),
            reading("load_power", "40"),
        ]);

        expect(powerFlow).toHaveBeenCalledWith({ kind: "solar", watts: 500 });
        expect(powerFlow).toHaveBeenCalledWith({ kind: "battery", watts: -20 });
        expect(powerFlow).toHaveBeenCalledWith({ kind: "grid", watts: -30 });
        expect(powerFlow).toHaveBeenCalledWith({ kind: "consumer", watts: 40 });
    });

    it("keeps a line still when the flow has no direction", async () => {
        const card = await mountFlow([reading("pv_power", "5")]);
        const drawn = lineOf({ card, label: "solar" });

        expect(drawn.classList.contains("idle")).toBe(true);
        expect(drawn.classList.contains("active")).toBe(false);
        expect(drawn.getAttribute("style")).toBe("");
    });

    it("keeps a line still, and asks for no flow, when the power cannot be read", async () => {
        flowsOf({ battery: { state: "charging", line: "from_inverter" } });
        vi.mocked(wattsOf).mockReturnValue(null);

        const card = await mountFlow([reading("battery_power", "unavailable")]);

        expect(
            lineOf({ card, label: "battery" }).classList.contains("idle"),
        ).toBe(true);
        expect(powerFlow).not.toHaveBeenCalled();
    });

    it("never gives the second meter a flow direction", async () => {
        flowsOf({ consumer: { state: "consuming", line: "from_inverter" } });

        const card = await mountFlow([reading("meter_b_power", "5000")]);

        expect(
            lineOf({ card, label: "meter_b" }).classList.contains("idle"),
        ).toBe(true);
        expect(powerFlow).not.toHaveBeenCalled();
    });

    it("runs the animation at the duration for the node's power and in the colour of its flow", async () => {
        flowsOf({ solar: { state: "producing", line: "to_inverter" } });
        vi.mocked(flowDurationSeconds).mockReturnValue(1.5);

        const card = await mountFlow([reading("pv_power", "5000")]);
        const style = lineOf({ card, label: "solar" }).getAttribute("style");

        expect(flowDurationSeconds).toHaveBeenCalledWith(5000);
        expect(style).toContain("--flow-duration: 1.5s");
        expect(style).toContain("--energy-solar-color");
    });

    it("colours the battery line differently when charging and discharging", async () => {
        flowsOf({ battery: { state: "charging", line: "from_inverter" } });
        const charging = await mountFlow([reading("battery_power", "-500")]);
        flowsOf({ battery: { state: "discharging", line: "to_inverter" } });
        const discharging = await mountFlow([reading("battery_power", "500")]);

        expect(
            lineOf({ card: charging, label: "battery" }).getAttribute("style"),
        ).not.toBe(
            lineOf({ card: discharging, label: "battery" }).getAttribute(
                "style",
            ),
        );
    });
});

describe("power flow card words", () => {
    it.each([
        "importing",
        "exporting",
        "idle",
        "charging",
        "discharging",
    ] as const)(
        "shows the word for $state beside the grid and battery power",
        async (state) => {
            flowsOf({
                grid: { state, line: "none" },
                battery: { state, line: "none" },
            });

            const card = await mountFlow([
                reading("grid_power", "5"),
                reading("battery_power", "5"),
            ]);

            expect(secondariesOf(card)).toEqual([state, state]);
        },
    );

    it("shows the state of charge with the battery direction", async () => {
        flowsOf({ battery: { state: "charging", line: "from_inverter" } });

        const card = await mountFlow([
            reading("battery_power", "-100"),
            reading("battery_soc", "64"),
        ]);

        expect(secondariesOf(card)).toEqual(["value(battery_soc) · charging"]);
    });

    it("shows the state of charge alone when the battery power cannot be read", async () => {
        flowsOf({ battery: { state: "charging", line: "from_inverter" } });
        vi.mocked(wattsOf).mockReturnValue(null);

        const card = await mountFlow([
            reading("battery_power", "unavailable"),
            reading("battery_soc", "64"),
        ]);

        expect(secondariesOf(card)).toEqual(["value(battery_soc)"]);
    });

    it("shows no word for a flow that has none", async () => {
        flowsOf({ battery: { state: "producing", line: "none" } });

        const card = await mountFlow([reading("battery_power", "5")]);

        expect(secondariesOf(card)).toEqual([""]);
    });

    it("shows no word for nodes that need no direction words", async () => {
        flowsOf({ consumer: { state: "importing", line: "none" } });

        const card = await mountFlow([
            reading("pv_power", "1200"),
            reading("load_power", "-5"),
        ]);

        expect(secondariesOf(card)).toEqual(["", ""]);
    });
});

describe("power flow card solar strings", () => {
    const strings = [
        reading("pv_power", "1000"),
        reading("pv10_power", "100"),
        reading("pv2_power", "400"),
        reading("pv1_power", "500"),
        reading("pv0_power", "7"),
    ];

    it("lists each string from 1 in order beneath the solar node when asked", async () => {
        const card = await mountFlow(strings, { show_strings: true });

        expect(
            elementsIn(card, ".string").map((line) => line.textContent),
        ).toEqual([
            "name(pv1_power): value(pv1_power)",
            "name(pv2_power): value(pv2_power)",
            "name(pv10_power): value(pv10_power)",
        ]);
    });

    it("leaves the strings out by default", async () => {
        const card = await mountFlow(strings);

        expect(elementsIn(card, ".string")).toEqual([]);
    });

    it("opens more-info of a string when tapped", async () => {
        const card = await mountFlow(strings, { show_strings: true });

        firstIn(card, ".string").parentElement?.dispatchEvent(
            new MouseEvent("click", { bubbles: true }),
        );

        expect(fireMoreInfo).toHaveBeenCalledWith({
            host: card,
            entityId: "sensor.saj_pv1_power",
        });
    });

    it("shows the strings as entities of the card", async () => {
        const card = await mountFlow(strings, { show_strings: true });
        const pv1 = reading("pv1_power", "500");

        expect(card.shownEntities(entityMap([pv1]))).toContainEqual(pv1);
    });
});

describe("power flow card interaction", () => {
    it("opens more-info of a node when tapped", async () => {
        const card = await mountFlow([reading("grid_power", "-100")]);

        firstIn(card, ".node").dispatchEvent(
            new MouseEvent("click", { bubbles: true }),
        );

        expect(fireMoreInfo).toHaveBeenCalledWith({
            host: card,
            entityId: "sensor.saj_grid_power",
        });
    });

    it.each(["Enter", " "])(
        "opens more-info when %j is pressed on a node",
        async (key) => {
            const card = await mountFlow([reading("grid_power", "-100")]);

            const event = press(firstIn(card, ".node"), key);

            expect(event.defaultPrevented).toBe(true);
            expect(fireMoreInfo).toHaveBeenCalledTimes(1);
        },
    );

    it("ignores other keys", async () => {
        const card = await mountFlow([reading("grid_power", "-100")]);

        const event = press(firstIn(card, ".node"), "a");

        expect(event.defaultPrevented).toBe(false);
        expect(fireMoreInfo).not.toHaveBeenCalled();
    });

    it("makes every node reachable by keyboard with an accessible name", async () => {
        flowsOf({ grid: { state: "importing", line: "to_inverter" } });

        const card = await mountFlow([
            reading("grid_power", "-100"),
            entity("operating_mode", "sensor", "operating"),
        ]);

        for (const node of elementsIn(card, ".node")) {
            expect(node.getAttribute("tabindex")).toBe("0");
            expect(node.getAttribute("role")).toBe("button");
            expect(node.getAttribute("aria-label")).not.toBe("");
        }
        expect(
            elementsIn(card, ".node")[0]?.getAttribute("aria-label"),
        ).toContain("importing");
    });

    it("dims the drawing while the card is dimmed", async () => {
        const dimmed = await mountFlow([reading("grid_power", "1")], {}, true);
        const live = await mountFlow([reading("grid_power", "1")]);

        expect(firstIn(dimmed, "svg").classList.contains("dimmed")).toBe(true);
        expect(firstIn(live, "svg").classList.contains("dimmed")).toBe(false);
    });
});

describe("power flow card contracts", () => {
    it("offers the switches and the scope", () => {
        expect(SajLocalPowerFlowCard.getConfigForm()).toEqual({
            fields: [
                { kind: "boolean", name: "show_strings", fallback: false },
                { kind: "boolean", name: "show_optional", fallback: true },
                {
                    kind: "select",
                    name: "scope",
                    options: POWER_FLOW_SCOPES.map((value) => ({
                        value,
                        label: `option_scope_${value}`,
                    })),
                    fallback: "system",
                },
            ],
        });
    });

    it("has a size", async () => {
        const card = await mountFlow([reading("pv_power", "1")]);

        expect(card.getCardSize()).toBeGreaterThan(0);
    });
});
