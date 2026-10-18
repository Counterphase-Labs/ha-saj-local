import { afterEach, describe, expect, it, vi } from "vitest";
import { stylesModule } from "../fakes/modules";

import "../../src/ui/card-container";
import { inShadow, mount } from "./mount";

vi.mock("../../src/ui/styles", () => stylesModule());

afterEach(() => {
    document.body.replaceChildren();
});

describe("saj-card", () => {
    it("shows the heading when there is one", async () => {
        const card = await mount<HTMLElementTagNameMap["saj-card"]>(
            "saj-card",
            { heading: "Battery" },
        );

        expect(inShadow(card, "h2").textContent).toBe("Battery");
    });

    it("draws no heading without one and offers a slot for content", async () => {
        const card = await mount<HTMLElementTagNameMap["saj-card"]>("saj-card");

        expect(card.shadowRoot?.querySelector("h2")).toBeNull();
        expect(inShadow(card, "slot")).toBeTruthy();
    });
});
