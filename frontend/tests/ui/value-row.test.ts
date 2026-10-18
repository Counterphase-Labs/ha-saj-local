import { afterEach, describe, expect, it, vi } from "vitest";
import { actionsModule, stylesModule } from "../fakes/modules";

import { fireMoreInfo } from "../../src/actions";
import { toneColour } from "../../src/ui/styles";
import "../../src/ui/value-row";
import { inShadow, mount, shadowButton } from "./mount";

vi.mock("../../src/actions", () => actionsModule());
vi.mock("../../src/ui/icon", () => ({}));
vi.mock("../../src/ui/styles", () => stylesModule());

type Row = HTMLElementTagNameMap["saj-value-row"];

afterEach(() => {
    document.body.replaceChildren();
    vi.mocked(fireMoreInfo).mockClear();
});

describe("saj-value-row", () => {
    it("shows the label and value as plain text without an entity", async () => {
        const row = await mount<Row>("saj-value-row", {
            label: "Solar",
            value: "5 kW",
        });

        expect(inShadow(row, ".label").textContent).toBe("Solar");
        expect(inShadow(row, ".value").textContent).toBe("5 kW");
        expect(row.shadowRoot?.querySelector("button")).toBeNull();
        expect(row.shadowRoot?.querySelector("saj-icon")).toBeNull();
    });

    it("draws the icon when given one", async () => {
        const row = await mount<Row>("saj-value-row", { icon: "solar" });

        expect(inShadow(row, "saj-icon")).toBeTruthy();
    });

    it("opens more-info of its entity when tapped", async () => {
        const row = await mount<Row>("saj-value-row", {
            entityId: "sensor.pv_power",
        });

        shadowButton(row).click();

        expect(fireMoreInfo).toHaveBeenCalledWith({
            host: row,
            entityId: "sensor.pv_power",
        });
    });

    it("colours the value by tone and dims it on request", async () => {
        const row = await mount<Row>("saj-value-row", {
            tone: "error",
            dimmed: true,
        });

        expect(toneColour).toHaveBeenCalledWith("error");
        expect(inShadow(row, ".value").style.color).toBe("var(--tone-error)");
        expect(inShadow(row, ".row").classList.contains("dimmed")).toBe(true);
    });
});
