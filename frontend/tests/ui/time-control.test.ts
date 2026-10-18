import { afterEach, describe, expect, it, vi } from "vitest";
import { controlElementModule } from "../fakes/modules";

import "../../src/ui/time-control";
import { commitsOf } from "../fakes/modules";
import { mount, settle, shadowInput, changeField } from "./mount";

vi.mock("../../src/ui/control-element", () => controlElementModule());

type TimeControl = HTMLElementTagNameMap["saj-time-control"];

afterEach(() => {
    document.body.replaceChildren();
});

describe("saj-time-control", () => {
    it("shows the hours and minutes of the entity's time", async () => {
        const control = await mount<TimeControl>("saj-time-control", {
            label: "Start",
            value: "08:30:00",
        });

        const input = shadowInput(control);

        expect(input.type).toBe("time");
        expect(input.value).toBe("08:30");
    });

    it("commits the chosen time on change", async () => {
        const control = await mount<TimeControl>("saj-time-control", {
            value: "08:30:00",
        });
        const input = shadowInput(control);

        input.value = "09:15";
        input.dispatchEvent(new Event("change", { bubbles: true }));

        expect(commitsOf(control)).toEqual(["09:15"]);
    });

    it("commits nothing when the field is cleared", async () => {
        const control = await mount<TimeControl>("saj-time-control", {
            value: "08:30:00",
        });
        const input = shadowInput(control);

        changeField(input, "");
        await settle(control);

        expect(commitsOf(control)).toEqual([]);
    });

    it("shows the entity's time again right after a change", async () => {
        const control = await mount<TimeControl>("saj-time-control", {
            value: "08:30:00",
        });
        const input = shadowInput(control);

        input.value = "11:00";
        input.dispatchEvent(new Event("change", { bubbles: true }));

        expect(input.value).toBe("08:30");
    });
});
