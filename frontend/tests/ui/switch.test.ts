import { afterEach, describe, expect, it, vi } from "vitest";
import { controlElementModule } from "../fakes/modules";

import "../../src/ui/switch";
import { commitsOf } from "../fakes/modules";
import { mount, shadowButton } from "./mount";

vi.mock("../../src/ui/control-element", () => controlElementModule());

type Switch = HTMLElementTagNameMap["saj-switch"];

afterEach(() => {
    document.body.replaceChildren();
});

describe("saj-switch", () => {
    it.each([
        { checked: false, committed: true },
        { checked: true, committed: false },
    ])(
        "commits $committed when clicked while checked is $checked",
        async ({ checked, committed }) => {
            const control = await mount<Switch>("saj-switch", {
                label: "Buzzer",
                checked,
            });

            shadowButton(control).click();

            expect(commitsOf(control)).toEqual([committed]);
        },
    );

    it("is a switch with an accessible name that reflects the entity state only", async () => {
        const control = await mount<Switch>("saj-switch", {
            label: "Buzzer",
            checked: true,
        });
        const button = shadowButton(control);

        expect(button.getAttribute("role")).toBe("switch");
        expect(button.getAttribute("aria-label")).toBe("Buzzer");
        expect(button.getAttribute("aria-checked")).toBe("true");

        button.click();
        await control.updateComplete;

        expect(button.getAttribute("aria-checked")).toBe("true");
    });

    it.each([{ disabled: true }, { busy: true }])(
        "cannot be switched when %o",
        async (state) => {
            const control = await mount<Switch>("saj-switch", state);

            expect(shadowButton(control).disabled).toBe(true);
        },
    );
});
