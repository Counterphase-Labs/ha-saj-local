import { html, type TemplateResult } from "lit";
import { afterEach, describe, expect, it, vi } from "vitest";
import { localizedElementModule, stylesModule } from "../fakes/modules";

import { COMMIT_EVENT, ControlElement } from "../../src/ui/control-element";
import { createFakeHass } from "../fakes/hass";
import { captureEvents, inShadow, mount } from "./mount";

vi.mock("../../src/ui/icon", () => ({}));
vi.mock("../../src/ui/styles", () => stylesModule());
vi.mock("../../src/ui/localized-element", () => localizedElementModule());

class ProbeControl extends ControlElement<number> {
    protected override render(): TemplateResult {
        return this.renderFrame(
            html`<button ?disabled=${this.inactive}>probe</button>`,
        );
    }

    choose(value: number): void {
        this.commit(value);
    }
}
customElements.define("probe-control", ProbeControl);

afterEach(() => {
    document.body.replaceChildren();
});

describe("control frame", () => {
    it("shows the label only when there is one", async () => {
        const labelled = await mount<ProbeControl>("probe-control", {
            label: "Buzzer",
        });
        const bare = await mount<ProbeControl>("probe-control");

        expect(inShadow(labelled, ".label").textContent).toBe("Buzzer");
        expect(bare.shadowRoot?.querySelector(".label")).toBeNull();
    });

    it("hides a label that is kept as the accessible name", async () => {
        const control = await mount<ProbeControl>("probe-control", {
            label: "Buzzer",
            labelHidden: true,
        });

        expect(control.shadowRoot?.querySelector(".label")).toBeNull();
    });

    it("shows a busy indicator and disables the control while busy", async () => {
        const control = await mount<ProbeControl>("probe-control", {
            hass: createFakeHass(),
            busy: true,
        });

        expect(inShadow(control, ".busy").getAttribute("role")).toBe("status");
        expect(inShadow(control, "button").hasAttribute("disabled")).toBe(true);
    });

    it("draws no busy indicator when idle", async () => {
        const control = await mount<ProbeControl>("probe-control");

        expect(control.shadowRoot?.querySelector(".busy")).toBeNull();
        expect(inShadow(control, "button").hasAttribute("disabled")).toBe(
            false,
        );
    });

    it("disables the control when disabled", async () => {
        const control = await mount<ProbeControl>("probe-control", {
            disabled: true,
        });

        expect(inShadow(control, "button").hasAttribute("disabled")).toBe(true);
    });

    it("shows the error as an alert under the control", async () => {
        const control = await mount<ProbeControl>("probe-control", {
            error: "Refused",
        });

        expect(inShadow(control, ".error[role=alert]").textContent).toBe(
            "Refused",
        );
    });

    it("shows no error when there is none", async () => {
        const control = await mount<ProbeControl>("probe-control");

        expect(control.shadowRoot?.querySelector(".error")).toBeNull();
    });
});

describe("committing", () => {
    it("announces the decision with an event that crosses shadow boundaries", async () => {
        const control = await mount<ProbeControl>("probe-control");
        const events = captureEvents(document.body, COMMIT_EVENT);

        control.choose(7);

        expect(events.map((event) => event.detail)).toEqual([7]);
        expect(events[0]?.composed).toBe(true);
    });
});
