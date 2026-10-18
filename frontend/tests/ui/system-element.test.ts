import { html, type TemplateResult } from "lit";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { localizedElementModule } from "../fakes/modules";

import { SystemElement } from "../../src/ui/system-element";
import { createFakeHass } from "../fakes/hass";
import { mount } from "./mount";

const redraw = vi.hoisted(() => ({
    needed: vi.fn<(arguments_: unknown) => boolean>(),
}));

vi.mock("../../src/system/redraw", () => ({
    SystemRedraw: class {
        needed = redraw.needed;
    },
}));
vi.mock("../../src/ui/localized-element", () => localizedElementModule());

let drawn = 0;

class ProbeSystem extends SystemElement {
    static override properties = {
        ...SystemElement.properties,
        note: { type: String },
    };

    declare note: string;
    device: string | undefined = "saj_1";

    protected override watchedDeviceId(): string | undefined {
        return this.device;
    }

    protected override render(): TemplateResult {
        drawn += 1;
        return html`${this.note}`;
    }
}
customElements.define("probe-system", ProbeSystem);

beforeEach(() => {
    drawn = 0;
    redraw.needed.mockReset();
});

afterEach(() => {
    document.body.replaceChildren();
});

describe("SystemElement", () => {
    it("draws for the first hass it gets", async () => {
        await mount<ProbeSystem>("probe-system", { hass: createFakeHass() });

        expect(drawn).toBe(1);
        expect(redraw.needed).not.toHaveBeenCalled();
    });

    it("draws again when a new hass changes what the element shows, and asks about its own system", async () => {
        const first = createFakeHass();
        const second = createFakeHass();
        const element = await mount<ProbeSystem>("probe-system", {
            hass: first,
        });
        redraw.needed.mockReturnValue(true);

        element.hass = second;
        await element.updateComplete;

        expect(drawn).toBe(2);
        expect(redraw.needed).toHaveBeenCalledWith({
            previous: first,
            next: second,
            deviceId: "saj_1",
        });
    });

    it("does not draw again when a new hass changes nothing the element shows", async () => {
        const element = await mount<ProbeSystem>("probe-system", {
            hass: createFakeHass(),
        });
        redraw.needed.mockReturnValue(false);

        element.hass = createFakeHass();
        await element.updateComplete;

        expect(drawn).toBe(1);
    });

    it("judges several hass updates before a draw by the first and the last", async () => {
        const first = createFakeHass();
        const last = createFakeHass();
        const element = await mount<ProbeSystem>("probe-system", {
            hass: first,
        });
        redraw.needed.mockReturnValue(false);

        element.hass = createFakeHass();
        element.hass = last;
        await element.updateComplete;

        expect(redraw.needed).toHaveBeenCalledTimes(1);
        expect(redraw.needed).toHaveBeenCalledWith(
            expect.objectContaining({ previous: first, next: last }),
        );
    });

    it("always draws when something other than hass changed", async () => {
        const element = await mount<ProbeSystem>("probe-system", {
            hass: createFakeHass(),
        });
        redraw.needed.mockReturnValue(false);

        element.note = "changed";
        await element.updateComplete;
        element.hass = createFakeHass();
        element.note = "again";
        await element.updateComplete;

        expect(drawn).toBe(3);
        expect(redraw.needed).not.toHaveBeenCalled();
    });

    it("draws when hass is taken away", async () => {
        const element = await mount<ProbeSystem>("probe-system", {
            hass: createFakeHass(),
        });

        element.hass = undefined;
        await element.updateComplete;

        expect(drawn).toBe(2);
        expect(redraw.needed).not.toHaveBeenCalled();
    });
});
