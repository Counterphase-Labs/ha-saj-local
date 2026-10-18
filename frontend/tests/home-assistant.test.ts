import { describe, expect, it } from "vitest";

import { whenHomeAssistantIsReady } from "../src/home-assistant";

describe("waiting for Home Assistant", () => {
    it("settles only once the home-assistant element is defined", async () => {
        const events: string[] = [];
        const ready = whenHomeAssistantIsReady().then(() => {
            events.push("ready");
        });

        await Promise.resolve();
        events.push("waiting");
        customElements.define("home-assistant", class extends HTMLElement {});
        await ready;

        expect(events).toEqual(["waiting", "ready"]);
    });
});
