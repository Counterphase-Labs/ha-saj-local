import { afterEach, describe, expect, it, vi } from "vitest";
import { controlElementModule } from "../fakes/modules";

import "../../src/ui/press-control";
import { createFakeHass } from "../fakes/hass";
import { commitsOf } from "../fakes/modules";
import { mount, shadowButton } from "./mount";

vi.mock("../../src/ui/control-element", () => controlElementModule());

type PressControl = HTMLElementTagNameMap["saj-press-control"];

afterEach(() => {
    document.body.replaceChildren();
});

describe("saj-press-control", () => {
    it("commits once per press", async () => {
        const control = await mount<PressControl>("saj-press-control", {
            hass: createFakeHass(),
            label: "Synchronise clock",
        });
        shadowButton(control).click();

        expect(commitsOf(control)).toHaveLength(1);
        expect(shadowButton(control).getAttribute("aria-label")).toBe(
            "Synchronise clock",
        );
    });

    it.each([{ disabled: true }, { busy: true }])(
        "cannot be pressed when %o",
        async (state) => {
            const control = await mount<PressControl>("saj-press-control", {
                hass: createFakeHass(),
                ...state,
            });

            expect(shadowButton(control).disabled).toBe(true);
        },
    );
});
