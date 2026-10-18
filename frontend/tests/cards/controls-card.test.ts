import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { entitiesModule } from "../fakes/entities";
import {
    editorModule,
    entityControlsModule,
    registrationModule,
    stylesModule,
    systemCardModule,
} from "../fakes/modules";

import { SajControlsCard, SECTION_IDS } from "../../src/cards/controls-card";
import { renderEntityControl } from "../../src/cards/entity-controls";
import { systemEntities, type SystemEntity } from "../../src/system/entities";
import { entity, entityMap } from "../fakes/entities";
import {
    createCard,
    elementsIn,
    firstIn,
    mountCard,
    type CardUnderTest,
    controlStubsIn,
    describeCardPicker,
} from "./support";

vi.mock("../../src/registration", () => registrationModule());
vi.mock("../../src/system/entities", () => entitiesModule());
vi.mock("../../src/cards/entity-controls", () => entityControlsModule());
vi.mock("../../src/ui/styles", () => stylesModule());
vi.mock("../../src/cards/editor", () => editorModule());
vi.mock("../../src/cards/system-card", () => systemCardModule());

const TAG = "saj-local-controls-card";

describeCardPicker({
    tag: TAG,
    card: SajControlsCard,
    startingOptions: { sections: SECTION_IDS },
});

const number = (key: string): SystemEntity => entity(key, "number", "20");
const switchOf = (key: string): SystemEntity => entity(key, "switch", "on");
const select = (key: string): SystemEntity => entity(key, "select", "backup");

const mountControls = (
    entities: SystemEntity[],
    config: Record<string, unknown> = {},
    options: { dimmed?: boolean; locked?: boolean } = {},
) => mountCard({ tag: TAG, config, entities, ...options });

const headings = (card: CardUnderTest): string[] =>
    elementsIn(card, "h3").map((heading) => heading.textContent.trim());

const controlKeys = (card: CardUnderTest): string[] =>
    controlStubsIn(card, "saj-control-stub").map(
        (control) => control.entityKey,
    );

afterEach(() => {
    document.body.replaceChildren();
});

describe("controls card sections", () => {
    it("draws sections for present keys and omits the others", async () => {
        const card = await mountControls([
            number("backup_reserve_soc"),
            select("application_mode"),
            switchOf("buzzer"),
        ]);

        expect(headings(card)).toEqual([
            "section_mode",
            "section_battery",
            "section_device",
        ]);
        expect(controlKeys(card)).toEqual([
            "application_mode",
            "backup_reserve_soc",
            "buzzer",
        ]);
    });

    it("draws only the chosen sections", async () => {
        const card = await mountControls(
            [number("backup_reserve_soc"), switchOf("buzzer")],
            { sections: ["device"] },
        );

        expect(headings(card)).toEqual(["section_device"]);
        expect(controlKeys(card)).toEqual(["buzzer"]);
    });

    it("gives every control the card's context with its label shown", async () => {
        const card = await mountControls([switchOf("buzzer")]);

        const options = vi.mocked(renderEntityControl).mock.calls[0]?.[0];
        expect(options?.context).toBe(card.context);
        expect(options?.entity.key).toBe("buzzer");
        expect(firstIn(card, "saj-control-stub").labelHidden).toBe(false);
    });

    it("draws a power control row with its name and the sign hint under the target", async () => {
        const card = await mountControls([
            switchOf("battery_power_control"),
            number("battery_power_target"),
            number("inverter_power_target"),
            switchOf("grid_power_control"),
        ]);
        const rows = elementsIn(card, ".power-row");

        expect(rows).toHaveLength(3);
        expect(
            elementsIn(card, ".power-name").map((name) => name.textContent),
        ).toEqual(["battery", "grid", "inverter"]);
        expect(
            [...(rows[0]?.querySelectorAll("saj-control-stub") ?? [])].map(
                (control) => control.entityKey,
            ),
        ).toEqual(["battery_power_control", "battery_power_target"]);
        expect(
            elementsIn(card, ".sign-hint").map((hint) =>
                hint.textContent.trim(),
            ),
        ).toEqual(["sign_battery", "sign_inverter"]);
    });

    it("hides the labels of the controls in a power row, which the row names", async () => {
        const card = await mountControls([
            switchOf("battery_power_control"),
            number("battery_power_target"),
        ]);

        expect(
            controlStubsIn(card, "saj-control-stub").map(
                (control) => control.labelHidden,
            ),
        ).toEqual([true, true]);
    });

    it("leaves Restart inverter and Clear fault off the card", async () => {
        const card = await mountControls([
            entity("restart_inverter", "button", "unknown"),
            entity("clear_current_fault", "button", "unknown"),
            entity("synchronise_clock", "button", "unknown"),
        ]);

        expect(controlKeys(card)).toEqual(["synchronise_clock"]);
    });

    it("shows the locked message above the sections while changes are off", async () => {
        const locked = await mountControls(
            [switchOf("buzzer")],
            {},
            { locked: true },
        );
        const open = await mountControls([switchOf("buzzer")]);

        expect(
            locked.shadowRoot?.querySelector("saj-empty-state"),
        ).toMatchObject({
            locked: true,
        });
        expect(open.shadowRoot?.querySelector("saj-empty-state")).toBeNull();
    });

    it("dims the sections while the card is dimmed", async () => {
        const dimmed = await mountControls(
            [switchOf("buzzer")],
            {},
            { dimmed: true },
        );
        const bright = await mountControls([switchOf("buzzer")]);

        expect(firstIn(dimmed, ".dimmed")).toBeDefined();
        expect(bright.shadowRoot?.querySelector(".dimmed")).toBeNull();
    });
});

describe("controls card states", () => {
    it("shows the empty state naming configuration entities when no section is drawn", async () => {
        const card = await mountControls([entity("pv_power", "sensor", "100")]);

        expect(firstIn(card, "saj-empty-state")).toMatchObject({
            locked: false,
            kind: "entity_kind_configuration",
        });
    });

    it("shows the locked message in place of the empty state while changes are off", async () => {
        const card = await mountControls([], {}, { locked: true });

        expect(firstIn(card, "saj-empty-state")).toMatchObject({
            locked: true,
        });
    });

    it("shows every control entity of the card as what the card shows", async () => {
        const card = await mountControls([]);
        const control = switchOf("battery_power_control");
        const target = number("battery_power_target");
        const buzzer = switchOf("buzzer");

        expect(
            card.shownEntities(entityMap([control, target, buzzer])),
        ).toEqual([control, target, buzzer]);
    });
});

describe("controls card contracts", () => {
    it("offers a choice of sections", () => {
        expect(SajControlsCard.getConfigForm()).toEqual({
            fields: [
                {
                    kind: "multi",
                    name: "sections",
                    options: SECTION_IDS.map((id) => ({
                        value: id,
                        label: `section_${id}`,
                    })),
                },
            ],
        });
    });
});

describe("controls card size", () => {
    beforeEach(() => {
        vi.mocked(systemEntities).mockReset();
    });

    it("is one before it has hass or a system", async () => {
        const card = createCard(TAG);
        const noDevice = await mountCard({
            tag: TAG,
            config: { device: undefined },
        });

        expect(card.getCardSize()).toBe(1);
        expect(noDevice.getCardSize()).toBe(1);
    });

    it("grows with the sections and rows drawn", async () => {
        const entities = entityMap([
            number("backup_reserve_soc"),
            switchOf("buzzer"),
        ]);
        vi.mocked(systemEntities).mockReturnValue(entities);
        const card = await mountCard({
            tag: TAG,
            entities: [...entities.values()],
        });
        const smaller = await mountCard({
            tag: TAG,
            config: { sections: ["device"] },
            entities: [...entities.values()],
        });

        expect(card.getCardSize()).toBeGreaterThan(smaller.getCardSize());
        expect(systemEntities).toHaveBeenCalled();
    });
});
