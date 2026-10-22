import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { entitiesModule } from "../fakes/entities";
import {
    actionsModule,
    editorModule,
    powerModule,
    registrationModule,
    stylesModule,
    systemCardModule,
} from "../fakes/modules";

import { fireMoreInfo } from "../../src/actions";
import { SajLocalBatteryCard } from "../../src/cards/battery-card";
import type { SystemEntity } from "../../src/system/entities";
import { powerFlow, wattsOf } from "../../src/system/power";
import { entity, entityMap } from "../fakes/entities";
import {
    elementsIn,
    firstIn,
    mountCard,
    requiredRowFor,
    rowFor,
    rowsOf,
    buttonIn,
    describeCardPicker,
} from "./support";

vi.mock("../../src/actions", () => actionsModule());
vi.mock("../../src/registration", () => registrationModule());
vi.mock("../../src/system/entities", () => entitiesModule());
vi.mock("../../src/system/power", () => powerModule());
vi.mock("../../src/ui/ring-gauge", () => ({}));
vi.mock("../../src/ui/icon", () => ({}));
vi.mock("../../src/cards/system-card", () => systemCardModule());
vi.mock("../../src/cards/editor", () => editorModule());
vi.mock("../../src/ui/styles", () => stylesModule());

const TAG = "saj-local-battery-card";

describeCardPicker({ tag: TAG, card: SajLocalBatteryCard });

const reading = (key: string, state: string): SystemEntity =>
    entity(key, "sensor", state);

const soc = reading("battery_soc", "64");
const power = reading("battery_power", "-1500");

const mountBattery = (
    entities: SystemEntity[],
    config: { show_packs?: boolean } = {},
    dimmed = false,
) => mountCard({ tag: TAG, config, entities, dimmed });

beforeEach(() => {
    vi.mocked(wattsOf).mockReturnValue(null);
});

afterEach(() => {
    document.body.replaceChildren();
});

describe("battery card gauge", () => {
    it("shows the state of charge on the ring and names it", async () => {
        const card = await mountBattery([soc]);
        const gauge = firstIn(card, "saj-ring-gauge");

        expect(gauge.percent).toBe(64);
        expect(gauge.displayValue).toBe("value(battery_soc)");
        expect(gauge.label).toBe("name(battery_soc)");
        expect(gauge.tone).toBe("primary");
        expect(gauge.markers).toEqual([]);
    });

    it("marks the reserve and the limits that are present and numeric", async () => {
        const card = await mountBattery([
            soc,
            reading("backup_reserve_soc", "20"),
            reading("battery_charge_soc_limit", "90"),
            reading("battery_discharge_soc_limit_on_grid", "unknown"),
        ]);

        expect(firstIn(card, "saj-ring-gauge").markers).toEqual([
            {
                percent: 20,
                label: "name(backup_reserve_soc) value(backup_reserve_soc)",
            },
            {
                percent: 90,
                label: "name(battery_charge_soc_limit) value(battery_charge_soc_limit)",
            },
        ]);
    });

    it("greys the ring when the state of charge is unavailable", async () => {
        const card = await mountBattery([
            reading("battery_soc", "unavailable"),
        ]);
        const gauge = firstIn(card, "saj-ring-gauge");

        expect(gauge.tone).toBe("disabled");
        expect(gauge.percent).toBe(0);
    });

    it("opens more-info of the state of charge when the ring is tapped", async () => {
        const card = await mountBattery([soc]);

        buttonIn(card, ".gauge").click();

        expect(fireMoreInfo).toHaveBeenCalledWith({
            host: card,
            entityId: soc.entityId,
        });
    });

    it("names the ring for assistive technology with the name and value", async () => {
        const card = await mountBattery([soc]);

        expect(firstIn(card, ".gauge").getAttribute("aria-label")).toBe(
            "name(battery_soc) value(battery_soc)",
        );
    });

    it("dims the ring while the card is dimmed and not otherwise", async () => {
        const dimmed = await mountBattery([soc], {}, true);
        const bright = await mountBattery([soc]);

        expect(firstIn(dimmed, "saj-ring-gauge").style.opacity).toBe("0.5");
        expect(firstIn(bright, "saj-ring-gauge").style.opacity).toBe("");
    });

    it("says the system has no battery without a state of charge", async () => {
        const card = await mountBattery([reading("battery_voltage", "50")]);

        expect(firstIn(card, "saj-notice")).toMatchObject({
            message: "no_battery",
        });
        expect(rowsOf(card)).toEqual([]);
        expect(card.shadowRoot?.querySelector("saj-ring-gauge")).toBeNull();
    });
});

describe("battery card power and readings", () => {
    it.each([
        { state: "charging", word: "charging" },
        { state: "discharging", word: "discharging" },
        { state: "idle", word: "idle" },
    ])(
        "shows the absolute power with the word for $state",
        async ({ state, word }) => {
            vi.mocked(wattsOf).mockReturnValue(-1500);
            vi.mocked(powerFlow).mockReturnValue({
                state: state as "idle",
                line: "none",
            });

            const card = await mountBattery([soc, power]);

            expect(powerFlow).toHaveBeenCalledWith({
                kind: "battery",
                watts: -1500,
            });
            expect(requiredRowFor({ card, entity: power }).value).toBe(
                `value(battery_power,absolute) · ${word}`,
            );
            expect(requiredRowFor({ card, entity: power }).icon).toBe(
                "battery",
            );
        },
    );

    it("shows battery power without a direction word when the state has no word or no watts", async () => {
        vi.mocked(wattsOf).mockReturnValue(20);
        vi.mocked(powerFlow).mockReturnValue({
            state: "producing",
            line: "none",
        });
        const noWord = await mountBattery([soc, power]);
        vi.mocked(wattsOf).mockReturnValue(null);
        const noWatts = await mountBattery([soc, power]);

        expect(requiredRowFor({ card: noWord, entity: power }).value).toBe(
            "value(battery_power,absolute)",
        );
        expect(requiredRowFor({ card: noWatts, entity: power }).value).toBe(
            "value(battery_power,absolute)",
        );
    });

    it("draws the readings that are present and none that are absent", async () => {
        const voltage = reading("battery_voltage", "52");
        const temperature = reading("battery_temperature", "24");

        const card = await mountBattery([soc, voltage, temperature]);

        expect(requiredRowFor({ card, entity: voltage }).icon).toBe("battery");
        expect(requiredRowFor({ card, entity: temperature }).icon).toBe(
            "temperature",
        );
        expect(rowsOf(card)).toHaveLength(2);
        expect(
            rowFor({ card, entity: reading("battery_current", "1") }),
        ).toBeUndefined();
    });
});

describe("battery card packs", () => {
    const packs = [
        reading("battery_pack10_soc", "70"),
        reading("battery_pack2_soc", "60"),
        reading("battery_pack2_cycles", "300"),
        reading("battery_pack2_serial_number", "ABC"),
        reading("battery_pack3_serial_number", "DEF"),
    ];

    it("draws one section for each pack with any pack key, in pack order, and a row for each present field", async () => {
        const card = await mountBattery([soc, ...packs]);
        const titles = elementsIn(card, "h3").map((heading) =>
            heading.textContent.trim(),
        );

        expect(titles).toEqual([
            'battery_pack:{"number":2}',
            'battery_pack:{"number":3}',
            'battery_pack:{"number":10}',
        ]);
        expect(
            rowFor({ card, entity: reading("battery_pack2_cycles", "") }),
        ).toBeDefined();
        expect(
            rowFor({
                card,
                entity: reading("battery_pack2_serial_number", ""),
            }),
        ).toBeUndefined();
    });

    it("leaves the packs out when asked", async () => {
        const card = await mountBattery([soc, ...packs], { show_packs: false });

        expect(card.shadowRoot?.querySelector("h3")).toBeNull();
        expect(rowsOf(card)).toEqual([]);
    });

    it.each([
        { key: "battery_pack1_fault", tone: "error" },
        { key: "battery_pack1_warning", tone: "warning" },
    ])(
        "marks a pack with $key on in the colour of $tone",
        async ({ key, tone }) => {
            const card = await mountBattery([
                soc,
                reading("battery_pack1_soc", "50"),
                entity(key, "binary_sensor", "on"),
            ]);
            const marks = elementsIn(card, "h3 saj-icon");

            expect(marks).toHaveLength(1);
            expect(marks[0]?.getAttribute("aria-label")).toBe(`name(${key})`);
            expect(marks[0]?.getAttribute("style")).toContain(`--tone-${tone}`);
        },
    );

    it("marks nothing for a pack whose fault and warning are off", async () => {
        const card = await mountBattery([
            soc,
            reading("battery_pack1_soc", "50"),
            entity("battery_pack1_fault", "binary_sensor", "off"),
            entity("battery_pack1_warning", "binary_sensor", "off"),
        ]);

        expect(elementsIn(card, "h3 saj-icon")).toEqual([]);
    });

    it("marks nothing for a pack without a fault or warning entity", async () => {
        const card = await mountBattery([
            soc,
            reading("battery_pack1_soc", "50"),
        ]);

        expect(elementsIn(card, "h3 saj-icon")).toEqual([]);
    });
});

describe("battery card contracts", () => {
    it("offers the packs option as a switch", () => {
        expect(SajLocalBatteryCard.getConfigForm()).toEqual({
            fields: [{ kind: "boolean", name: "show_packs", fallback: true }],
        });
    });

    it("shows nothing without a state of charge, and the readings and pack entities with one", async () => {
        const card = await mountBattery([soc]);
        const voltage = reading("battery_voltage", "52");
        const packSoc = reading("battery_pack1_soc", "50");
        const withPacks = entityMap([soc, voltage, packSoc]);

        expect(card.shownEntities(entityMap([voltage]))).toEqual([]);
        expect(card.shownEntities(withPacks)).toEqual([soc, voltage, packSoc]);
        expect(card.getCardSize()).toBeGreaterThan(0);
    });

    it("leaves the pack entities out of what it shows when the packs are left out", async () => {
        const card = await mountBattery([soc], { show_packs: false });
        const packSoc = reading("battery_pack1_soc", "50");

        expect(card.shownEntities(entityMap([soc, packSoc]))).toEqual([soc]);
    });
});
