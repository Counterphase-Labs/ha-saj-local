import { afterEach, describe, expect, it } from "vitest";

import "../src/card";

const mountCard = (): HTMLElementTagNameMap["saj-modbus-card"] => {
    const card = document.createElement("saj-modbus-card");
    document.body.append(card);
    return card;
};

describe("saj-modbus-card", () => {
    afterEach(() => {
        document.body.replaceChildren();
    });

    it("renders the configured title inside ha-card", async () => {
        const card = mountCard();

        card.setConfig({ type: "custom:saj-modbus-card", title: "Inverter" });
        await card.updateComplete;

        const haCard = card.shadowRoot?.querySelector("ha-card");
        expect(haCard?.textContent).toContain("Inverter");
    });

    it.each([
        { description: "no title", config: { type: "custom:saj-modbus-card" } },
        {
            description: "an empty title",
            config: { type: "custom:saj-modbus-card", title: "" },
        },
    ])("rejects a configuration with $description", ({ config }) => {
        const card = mountCard();

        expect(() => {
            card.setConfig(config);
        }).toThrow(/title/);
    });
});
