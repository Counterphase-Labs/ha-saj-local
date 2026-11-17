import { afterEach, describe, expect, it, vi } from "vitest";
import { controlElementModule } from "../fakes/modules";

import "../../src/ui/time-control";
import { commitsOf } from "../fakes/modules";
import { mount, settle, shadowInput, changeField } from "./mount";

vi.mock("../../src/ui/control-element", () => controlElementModule());

type TimeControl = HTMLElementTagNameMap["saj-time-control"];

const ENTITY_TIME = "08:30:00";

const mountField = async (
    properties: Partial<TimeControl> = {},
): Promise<{ control: TimeControl; input: HTMLInputElement }> => {
    const control = await mount<TimeControl>("saj-time-control", {
        value: ENTITY_TIME,
        ...properties,
    });
    return { control, input: shadowInput(control) };
};

const leave = (input: HTMLInputElement): void => {
    input.dispatchEvent(new Event("blur"));
};

const pressKey = (input: HTMLInputElement, key: string): void => {
    input.dispatchEvent(new KeyboardEvent("keydown", { key }));
};

afterEach(() => {
    document.body.replaceChildren();
});

describe("saj-time-control", () => {
    it("shows the hours and minutes of the entity's time", async () => {
        const { input } = await mountField({ label: "Start" });

        expect(input.type).toBe("time");
        expect(input.value).toBe("08:30");
    });

    it("commits nothing on change, and keeps the chosen time in the input", async () => {
        const { control, input } = await mountField();

        changeField(input, "11:00");
        await settle(control);

        expect(commitsOf(control)).toEqual([]);
        expect(input.value).toBe("11:00");
    });

    it("commits the draft on Enter", async () => {
        const { control, input } = await mountField();

        changeField(input, "09:15");
        pressKey(input, "Enter");

        expect(commitsOf(control)).toEqual(["09:15"]);
    });

    it("ignores other keys", async () => {
        const { control, input } = await mountField();

        changeField(input, "09:15");
        pressKey(input, "a");

        expect(commitsOf(control)).toEqual([]);
    });

    it("commits the draft when the field loses focus", async () => {
        const { control, input } = await mountField();

        changeField(input, "09:15");
        leave(input);

        expect(commitsOf(control)).toEqual(["09:15"]);
    });

    it("commits the last time of a series of changes once", async () => {
        const { control, input } = await mountField();

        changeField(input, "09:00");
        changeField(input, "09:15");
        changeField(input, "10:45");
        leave(input);
        leave(input);

        expect(commitsOf(control)).toEqual(["10:45"]);
    });

    it("commits the draft when the field is removed", async () => {
        const { control, input } = await mountField();

        changeField(input, "09:15");
        control.remove();

        expect(commitsOf(control)).toEqual(["09:15"]);
    });

    it("commits nothing when the field is removed with no draft", async () => {
        const { control } = await mountField();

        control.remove();

        expect(commitsOf(control)).toEqual([]);
    });

    it("commits nothing when the draft is the entity's time", async () => {
        const { control, input } = await mountField();

        changeField(input, "08:30");
        leave(input);

        expect(commitsOf(control)).toEqual([]);
    });

    it("commits nothing when the field is cleared, and keeps the entity's time", async () => {
        const { control, input } = await mountField();

        changeField(input, "");
        await settle(control);
        leave(input);
        await settle(control);

        expect(commitsOf(control)).toEqual([]);
        expect(input.value).toBe("08:30");
    });

    it("shows the entity's time again after the save starts", async () => {
        const { control, input } = await mountField();

        changeField(input, "11:00");
        await settle(control);
        leave(input);
        await settle(control);

        expect(input.value).toBe("08:30");
    });

    it("is disabled while the save of its entity runs", async () => {
        const { control, input } = await mountField();

        control.busy = true;
        await settle(control);

        expect(input.disabled).toBe(true);
    });

    it("sends the draft when the entity's time changes from another source", async () => {
        const { control, input } = await mountField();

        changeField(input, "09:15");
        control.value = "10:00:00";
        await settle(control);
        expect(input.value).toBe("09:15");
        leave(input);

        expect(commitsOf(control)).toEqual(["09:15"]);
    });

    it("holds no draft while disabled", async () => {
        const { control, input } = await mountField();

        changeField(input, "09:15");
        await settle(control);
        control.disabled = true;
        await settle(control);
        control.disabled = false;
        await settle(control);
        leave(input);

        expect(commitsOf(control)).toEqual([]);
        expect(input.value).toBe("08:30");
    });
});
