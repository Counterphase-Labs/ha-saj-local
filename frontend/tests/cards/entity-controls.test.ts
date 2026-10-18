import { render } from "lit";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { entitiesModule } from "../fakes/entities";
import { controlModule } from "../fakes/modules";

import {
    entityLabel,
    renderEntityControl,
    type ControlContext,
} from "../../src/cards/entity-controls";
import {
    ControlTracker,
    pressButtonRequest,
    selectOptionRequest,
    setNumberRequest,
    setSwitchRequest,
    setTimeRequest,
} from "../../src/system/control";
import { isUnavailable, numericValue } from "../../src/system/entities";
import { entity } from "../fakes/entities";
import { createFakeHass } from "../fakes/hass";
import { resultOf, trackerMocks } from "../fakes/mocks";

vi.mock("../../src/system/control", () => controlModule());
vi.mock("../../src/system/entities", () => entitiesModule());
vi.mock("../../src/ui/number-control", () => ({}));
vi.mock("../../src/ui/press-control", () => ({}));
vi.mock("../../src/ui/select-control", () => ({}));
vi.mock("../../src/ui/switch", () => ({}));
vi.mock("../../src/ui/time-control", () => ({}));
vi.mock("../../src/ui/value-row", () => ({}));

type Properties = Record<string, unknown>;

const hass = Object.assign(createFakeHass(), {
    formatEntityName: () => "Name",
    formatEntityState: (_state: unknown, override?: string) =>
        `formatted(${override ?? "state"})`,
});

const container = document.createElement("div");

const contextOf = (
    overrides: Partial<ControlContext> = {},
): ControlContext => ({
    hass,
    lock: { locked: false, entity: null },
    tracker: new ControlTracker({} as never, () => undefined),
    ...overrides,
});

const drawn = (
    options: Parameters<typeof renderEntityControl>[0],
): Element & Properties => {
    render(renderEntityControl(options), container);
    const [element] = container.children;
    if (element === undefined) {
        throw new Error("Nothing drawn");
    }
    return element as Element & Properties;
};

const commit = (element: Element, detail: unknown): void => {
    element.dispatchEvent(new CustomEvent("saj-commit", { detail }));
};

beforeEach(() => {
    vi.mocked(numericValue).mockClear();
    vi.mocked(isUnavailable).mockClear();
});

afterEach(() => {
    render(undefined, container);
});

describe("entityLabel", () => {
    it("names the entity the way Home Assistant does", () => {
        expect(entityLabel({ hass, entity: entity("a", "number", "1") })).toBe(
            "Name",
        );
    });
});

describe("renderEntityControl number", () => {
    const attributes = {
        min: 0,
        max: 100,
        step: 5,
        unit_of_measurement: "%",
        mode: "slider",
    };

    it("follows the entity's range, unit, mode and formatted value", () => {
        const element = drawn({
            context: contextOf(),
            entity: entity("backup_reserve_soc", "number", "20", {
                attributes,
            }),
        });

        expect(element.localName).toBe("saj-number-control");
        expect(element).toMatchObject({
            label: "Name",
            value: 20,
            min: 0,
            max: 100,
            step: 5,
            unit: "%",
            mode: "slider",
            displayValue: "formatted(state)",
        });
    });

    it("falls back to an empty unit, automatic mode and zero without a number", () => {
        vi.mocked(numericValue).mockReturnValueOnce(null);

        const element = drawn({
            context: contextOf(),
            entity: entity("backup_reserve_soc", "number", "unknown"),
        });

        expect(element).toMatchObject({ unit: "", mode: "auto", value: 0 });
    });

    it("submits the committed number to the entity", () => {
        const context = contextOf();
        const target = entity("backup_reserve_soc", "number", "20");
        const element = drawn({ context, entity: target });

        commit(element, 55);

        expect(setNumberRequest).toHaveBeenCalledWith(55);
        expect(trackerMocks(context.tracker).submit).toHaveBeenCalledWith({
            entityId: target.entityId,
            request: resultOf(setNumberRequest),
        });
    });
});

describe("renderEntityControl select", () => {
    it("lists the entity's options with the names Home Assistant gives them", () => {
        const element = drawn({
            context: contextOf(),
            entity: entity("application_mode", "select", "backup", {
                attributes: { options: ["backup", "time_of_use"] },
            }),
        });

        expect(element.localName).toBe("saj-select-control");
        expect(element.value).toBe("backup");
        expect(element.options).toEqual([
            { value: "backup", label: "formatted(backup)" },
            { value: "time_of_use", label: "formatted(time_of_use)" },
        ]);
    });

    it("lists no options for an entity without any", () => {
        const element = drawn({
            context: contextOf(),
            entity: entity("application_mode", "select", "backup"),
        });

        expect(element.options).toEqual([]);
    });

    it("submits the chosen option", () => {
        const context = contextOf();
        const target = entity("application_mode", "select", "backup");
        const element = drawn({ context, entity: target });

        commit(element, "time_of_use");

        expect(selectOptionRequest).toHaveBeenCalledWith("time_of_use");
        expect(trackerMocks(context.tracker).submit).toHaveBeenCalledWith({
            entityId: target.entityId,
            request: resultOf(selectOptionRequest),
        });
    });
});

describe("renderEntityControl switch, time and button", () => {
    it.each([
        { state: "on", checked: true },
        { state: "off", checked: false },
    ])(
        "shows a switch that is $state as checked $checked",
        ({ state, checked }) => {
            const element = drawn({
                context: contextOf(),
                entity: entity("buzzer", "switch", state),
            });

            expect(element.localName).toBe("saj-switch");
            expect(element.checked).toBe(checked);
        },
    );

    it("submits the switch decision", () => {
        const context = contextOf();
        const element = drawn({
            context,
            entity: entity("buzzer", "switch", "off"),
        });

        commit(element, true);

        expect(setSwitchRequest).toHaveBeenCalledWith(true);
        expect(trackerMocks(context.tracker).submit).toHaveBeenCalledTimes(1);
    });

    it("shows a time field with the entity's time and submits the chosen time", () => {
        const context = contextOf();
        const element = drawn({
            context,
            entity: entity("charge_slot_1_start", "time", "08:00:00"),
        });

        commit(element, "09:30");

        expect(element.localName).toBe("saj-time-control");
        expect(element.value).toBe("08:00:00");
        expect(setTimeRequest).toHaveBeenCalledWith("09:30");
        expect(trackerMocks(context.tracker).submit).toHaveBeenCalledTimes(1);
    });

    it("shows a button that submits a press", () => {
        const context = contextOf();
        const element = drawn({
            context,
            entity: entity("synchronise_clock", "button", "unknown"),
        });

        commit(element, null);

        expect(element.localName).toBe("saj-press-control");
        expect(pressButtonRequest).toHaveBeenCalledTimes(1);
        expect(trackerMocks(context.tracker).submit).toHaveBeenCalledTimes(1);
    });

    it("shows any other entity as a value row", () => {
        const target = entity("led_mode", "sensor", "bright");

        const element = drawn({ context: contextOf(), entity: target });

        expect(element.localName).toBe("saj-value-row");
        expect(element).toMatchObject({
            label: "Name",
            value: "formatted(state)",
            entityId: target.entityId,
        });
    });
});

describe("renderEntityControl state of every control", () => {
    it.each([
        { name: "number", domain: "number" },
        { name: "select", domain: "select" },
        { name: "switch", domain: "switch" },
        { name: "time", domain: "time" },
        { name: "button", domain: "button" },
    ])(
        "passes the label, error and hidden label to the $name control",
        ({ domain }) => {
            const context = contextOf();
            trackerMocks(context.tracker).errorOf.mockReturnValue("Refused");

            const element = drawn({
                context,
                entity: entity("a", domain, "on"),
                labelHidden: true,
            });

            expect(element).toMatchObject({
                label: "Name",
                labelHidden: true,
                error: "Refused",
                busy: false,
                disabled: false,
            });
        },
    );

    it("shows no error when the tracker has none", () => {
        const element = drawn({
            context: contextOf(),
            entity: entity("buzzer", "switch", "on"),
        });

        expect(element.error).toBe("");
    });

    it("disables the control while changes are off for the system", () => {
        const element = drawn({
            context: contextOf({ lock: { locked: true, entity: null } }),
            entity: entity("buzzer", "switch", "on"),
        });

        expect(element.disabled).toBe(true);
    });

    it("disables the control of an unavailable entity", () => {
        vi.mocked(isUnavailable).mockReturnValueOnce(true);

        const element = drawn({
            context: contextOf(),
            entity: entity("buzzer", "switch", "unavailable"),
        });

        expect(element.disabled).toBe(true);
    });

    it("shows the control busy while the entity is being changed", () => {
        const context = contextOf();
        trackerMocks(context.tracker).isBusy.mockReturnValue(true);

        const element = drawn({
            context,
            entity: entity("buzzer", "switch", "on"),
        });

        expect(element.busy).toBe(true);
    });
});
