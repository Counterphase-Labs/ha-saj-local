import { afterEach, describe, expect, it, vi } from "vitest";
import { stylesModule } from "../fakes/modules";

import "../../src/ui/notice";
import { toneColour } from "../../src/ui/styles";
import { inShadow, mount } from "./mount";

vi.mock("../../src/ui/icon", () => ({}));
vi.mock("../../src/ui/styles", () => stylesModule());

type Notice = HTMLElementTagNameMap["saj-notice"];

afterEach(() => {
    document.body.replaceChildren();
});

describe("saj-notice", () => {
    it("shows the message with a status role and a slot for an action", async () => {
        const notice = await mount<Notice>("saj-notice", {
            message: "Heads up",
        });

        expect(inShadow(notice, ".message").textContent).toBe("Heads up");
        expect(inShadow(notice, ".notice").getAttribute("role")).toBe("status");
        expect(inShadow(notice, "slot")).toBeTruthy();
    });

    it("announces an error as an alert", async () => {
        const notice = await mount<Notice>("saj-notice", { tone: "error" });

        expect(inShadow(notice, ".notice").getAttribute("role")).toBe("alert");
    });

    it.each(["primary", "warning", "error"] as const)(
        "colours the icon with the colour of the tone %s",
        async (tone) => {
            const notice = await mount<Notice>("saj-notice", { tone });

            expect(toneColour).toHaveBeenCalledWith(tone);
            expect(
                inShadow(notice, "saj-icon").getAttribute("style"),
            ).toContain(`var(--tone-${tone})`);
        },
    );
});
