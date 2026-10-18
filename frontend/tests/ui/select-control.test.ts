import { afterEach, describe, expect, it, vi } from "vitest";
import { controlElementModule } from "../fakes/modules";

import "../../src/ui/select-control";
import { commitsOf } from "../fakes/modules";
import { allInShadow, mount, shadowSelect } from "./mount";

vi.mock("../../src/ui/control-element", () => controlElementModule());

type SelectControl = HTMLElementTagNameMap["saj-select-control"];

const options = [
    { value: "a", label: "Alpha" },
    { value: "b", label: "Beta" },
];

afterEach(() => {
    document.body.replaceChildren();
});

const changeToB = async () => {
    const control = await mount<SelectControl>("saj-select-control", {
        value: "a",
        options,
    });
    const select = shadowSelect(control);

    select.value = "b";
    select.dispatchEvent(new Event("change", { bubbles: true }));
    return { control, select };
};

describe("saj-select-control", () => {
    it("lists the options with their names and selects the entity's value", async () => {
        const control = await mount<SelectControl>("saj-select-control", {
            label: "Mode",
            value: "b",
            options,
        });

        const listed = allInShadow(control, "option");

        expect(listed.map((option) => option.textContent.trim())).toEqual([
            "Alpha",
            "Beta",
        ]);
        expect(shadowSelect(control).value).toBe("b");
    });

    it("commits the chosen option on change", async () => {
        const { control } = await changeToB();

        expect(commitsOf(control)).toEqual(["b"]);
    });

    it("shows the entity's value again right after a change", async () => {
        const { select } = await changeToB();

        expect(select.value).toBe("a");
    });

    it("selects the new option when the entity's value changes", async () => {
        const control = await mount<SelectControl>("saj-select-control", {
            value: "a",
            options,
        });
        const select = shadowSelect(control);

        select.value = "b";
        control.value = "b";
        await control.updateComplete;

        expect(select.value).toBe("b");
    });

    it("is disabled while busy", async () => {
        const control = await mount<SelectControl>("saj-select-control", {
            options,
            busy: true,
        });

        expect(shadowSelect(control).disabled).toBe(true);
    });
});
