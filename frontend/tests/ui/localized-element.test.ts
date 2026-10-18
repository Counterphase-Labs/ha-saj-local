import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { localizeModule } from "../fakes/modules";

import { localizerFor } from "../../src/i18n/localize";
import { LocalizedElement } from "../../src/ui/localized-element";
import { createFakeHass } from "../fakes/hass";

vi.mock("../../src/i18n/localize", () => localizeModule());

class ProbeElement extends LocalizedElement {
    say(key: string): string {
        return this.text(key);
    }
}
customElements.define("probe-localized", ProbeElement);

beforeEach(() => {
    vi.mocked(localizerFor).mockClear();
});

afterEach(() => {
    document.body.replaceChildren();
});

describe("LocalizedElement", () => {
    it("translates with the localizer of the language of hass", () => {
        const probe = new ProbeElement();
        probe.hass = createFakeHass({ language: "de" });

        expect(probe.say("busy")).toBe("busy");
        expect(localizerFor).toHaveBeenCalledWith("de");
    });

    it("falls back to the default language without hass", () => {
        const probe = new ProbeElement();

        probe.say("busy");

        expect(localizerFor).toHaveBeenCalledWith("en");
    });
});
