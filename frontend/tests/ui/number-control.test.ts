import { afterEach, describe, expect, it, vi } from "vitest";
import { controlElementModule } from "../fakes/modules";

import {
    MAX_AUTO_SLIDER_STEPS,
    numberStyle,
    type NumberMode,
    type NumberRange,
} from "../../src/ui/number-control";
import { commitsOf } from "../fakes/modules";
import { inShadow, mount, shadowInput } from "./mount";

vi.mock("../../src/ui/control-element", () => controlElementModule());

type NumberControl = HTMLElementTagNameMap["saj-number-control"];

afterEach(() => {
    document.body.replaceChildren();
});

describe("numberStyle", () => {
    const stepped = (steps: number): NumberRange => ({
        min: 0,
        max: steps,
        step: 1,
    });

    it.each([
        { mode: "slider", range: stepped(10_000), expected: "slider" },
        { mode: "box", range: stepped(2), expected: "box" },
        {
            mode: "auto",
            range: stepped(MAX_AUTO_SLIDER_STEPS),
            expected: "slider",
        },
        {
            mode: "auto",
            range: stepped(MAX_AUTO_SLIDER_STEPS + 1),
            expected: "box",
        },
        {
            mode: "auto",
            range: { min: undefined, max: 10, step: 1 },
            expected: "box",
        },
        {
            mode: "auto",
            range: { min: 0, max: undefined, step: 1 },
            expected: "box",
        },
        {
            mode: "auto",
            range: { min: 0, max: 10, step: undefined },
            expected: "box",
        },
    ] satisfies { mode: NumberMode; range: NumberRange; expected: string }[])(
        "$mode with $range is a $expected",
        ({ mode, range, expected }) => {
            expect(numberStyle({ mode, range })).toBe(expected);
        },
    );
});

const typeInto = (input: HTMLInputElement, value: string): void => {
    input.value = value;
    input.dispatchEvent(new Event("input", { bubbles: true }));
};

const press = (input: HTMLInputElement, key: string): void => {
    input.dispatchEvent(new KeyboardEvent("keydown", { key, bubbles: true }));
};

const release = (input: HTMLInputElement): void => {
    input.dispatchEvent(new Event("pointerup", { bubbles: true }));
};

const leave = (input: HTMLInputElement): void => {
    input.dispatchEvent(new Event("blur"));
};

describe("saj-number-control as a slider", () => {
    const sliderProperties = {
        label: "Reserve",
        value: 20,
        min: 0,
        max: 100,
        step: 5,
        unit: "%",
        displayValue: "20 %",
        mode: "slider" as const,
    };

    it("uses the entity range and shows the formatted value beside the slider", async () => {
        const control = await mount<NumberControl>(
            "saj-number-control",
            sliderProperties,
        );
        const input = shadowInput(control);

        expect(input.type).toBe("range");
        expect([input.min, input.max, input.step]).toEqual(["0", "100", "5"]);
        expect(input.value).toBe("20");
        expect(inShadow(control, ".value").textContent).toBe("20 %");
    });

    it("shows the dragged value but commits nothing while dragging", async () => {
        const control = await mount<NumberControl>(
            "saj-number-control",
            sliderProperties,
        );
        const input = shadowInput(control);

        typeInto(input, "45");
        typeInto(input, "50");
        await control.updateComplete;

        expect(inShadow(control, ".value").textContent).toContain("50");
        expect(commitsOf(control)).toEqual([]);
    });

    it("commits the released value once and then shows the entity's value again", async () => {
        const control = await mount<NumberControl>(
            "saj-number-control",
            sliderProperties,
        );
        const input = shadowInput(control);

        typeInto(input, "45");
        release(input);
        await control.updateComplete;

        expect(commitsOf(control)).toEqual([45]);
        expect(input.value).toBe("20");
        expect(inShadow(control, ".value").textContent).toBe("20 %");
    });

    it("never commits on a change event, which arrow keys fire on every press", async () => {
        const control = await mount<NumberControl>(
            "saj-number-control",
            sliderProperties,
        );
        const input = shadowInput(control);

        typeInto(input, "25");
        input.dispatchEvent(new Event("change", { bubbles: true }));
        typeInto(input, "30");
        input.dispatchEvent(new Event("change", { bubbles: true }));

        expect(commitsOf(control)).toEqual([]);
    });

    it("commits the keyboard decision once on Enter", async () => {
        const control = await mount<NumberControl>(
            "saj-number-control",
            sliderProperties,
        );
        const input = shadowInput(control);

        typeInto(input, "25");
        typeInto(input, "30");
        press(input, "Enter");
        press(input, "Enter");

        expect(commitsOf(control)).toEqual([30]);
    });

    it("commits the keyboard decision once when the slider is left", async () => {
        const control = await mount<NumberControl>(
            "saj-number-control",
            sliderProperties,
        );
        const input = shadowInput(control);

        typeInto(input, "35");
        leave(input);
        leave(input);

        expect(commitsOf(control)).toEqual([35]);
    });

    it("ignores other keys", async () => {
        const control = await mount<NumberControl>(
            "saj-number-control",
            sliderProperties,
        );
        const input = shadowInput(control);

        typeInto(input, "35");
        press(input, "ArrowUp");

        expect(commitsOf(control)).toEqual([]);
    });

    it("commits nothing when released or left without a change", async () => {
        const control = await mount<NumberControl>(
            "saj-number-control",
            sliderProperties,
        );
        const input = shadowInput(control);

        release(input);
        leave(input);

        expect(commitsOf(control)).toEqual([]);
    });
});

describe("saj-number-control as a number field", () => {
    const boxProperties = {
        label: "Limit",
        value: 3000,
        unit: "W",
        mode: "box" as const,
    };

    it("shows the number field with the unit and no range when the entity has none", async () => {
        const control = await mount<NumberControl>(
            "saj-number-control",
            boxProperties,
        );
        const input = shadowInput(control);

        expect(input.type).toBe("number");
        expect(input.value).toBe("3000");
        expect(input.hasAttribute("min")).toBe(false);
        expect(inShadow(control, ".unit").textContent).toBe("W");
    });

    it("keeps what is typed and commits nothing for a spinner click or an arrow key", async () => {
        const control = await mount<NumberControl>(
            "saj-number-control",
            boxProperties,
        );
        const input = shadowInput(control);

        typeInto(input, "3100");
        input.dispatchEvent(new Event("change", { bubbles: true }));
        typeInto(input, "3200");
        input.dispatchEvent(new Event("change", { bubbles: true }));
        await control.updateComplete;

        expect(commitsOf(control)).toEqual([]);
        expect(input.value).toBe("3200");
    });

    it("commits the entered number once on Enter and shows the entity's value again", async () => {
        const control = await mount<NumberControl>(
            "saj-number-control",
            boxProperties,
        );
        const input = shadowInput(control);

        typeInto(input, "3500");
        press(input, "Enter");
        press(input, "Enter");

        expect(commitsOf(control)).toEqual([3500]);
        expect(input.value).toBe("3000");
    });

    it("commits the entered number once when the field is left", async () => {
        const control = await mount<NumberControl>(
            "saj-number-control",
            boxProperties,
        );
        const input = shadowInput(control);

        typeInto(input, "2800");
        leave(input);
        leave(input);

        expect(commitsOf(control)).toEqual([2800]);
    });

    it("does not commit when the pointer is released over the field", async () => {
        const control = await mount<NumberControl>(
            "saj-number-control",
            boxProperties,
        );
        const input = shadowInput(control);

        typeInto(input, "2800");
        release(input);

        expect(commitsOf(control)).toEqual([]);
    });

    it("commits nothing for an empty field and shows the entity's value again", async () => {
        const control = await mount<NumberControl>(
            "saj-number-control",
            boxProperties,
        );
        const input = shadowInput(control);

        typeInto(input, "");
        press(input, "Enter");

        expect(commitsOf(control)).toEqual([]);
        expect(input.value).toBe("3000");
    });

    it("disables the field while busy", async () => {
        const control = await mount<NumberControl>("saj-number-control", {
            ...boxProperties,
            busy: true,
        });

        expect(shadowInput(control).disabled).toBe(true);
    });
});
