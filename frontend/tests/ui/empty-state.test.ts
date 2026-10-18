import { afterEach, describe, expect, it, vi } from "vitest";
import {
    actionsModule,
    localizedElementModule,
    stylesModule,
} from "../fakes/modules";

import { fireNavigate } from "../../src/actions";
import "../../src/ui/empty-state";
import { createFakeHass } from "../fakes/hass";
import { inShadow, mount, shadowButton } from "./mount";

vi.mock("../../src/ui/styles", () => stylesModule());
vi.mock("../../src/actions", () => actionsModule());
vi.mock("../../src/ui/icon", () => ({}));
vi.mock("../../src/ui/localized-element", () => localizedElementModule());

type EmptyState = HTMLElementTagNameMap["saj-empty-state"];

afterEach(() => {
    document.body.replaceChildren();
    vi.mocked(fireNavigate).mockClear();
});

describe("saj-empty-state", () => {
    it("names the kind of entity to enable and links to the device page", async () => {
        const state = await mount<EmptyState>("saj-empty-state", {
            hass: createFakeHass(),
            kind: "schedule",
            deviceId: "abc",
        });

        expect(inShadow(state, ".body").textContent).toContain("schedule");
        shadowButton(state).click();

        expect(fireNavigate).toHaveBeenCalledWith({
            host: state,
            path: "/device/abc",
        });
    });

    it("shows a given message instead of the enable hint", async () => {
        const state = await mount<EmptyState>("saj-empty-state", {
            hass: createFakeHass(),
            message: "3 slots have disabled entities",
        });

        expect(inShadow(state, ".body").textContent).toBe(
            "3 slots have disabled entities",
        );
    });

    it("has no device link without a device", async () => {
        const state = await mount<EmptyState>("saj-empty-state", {
            hass: createFakeHass(),
        });

        expect(state.shadowRoot?.querySelector("button")).toBeNull();
    });

    it("shows the locked message and a settings link in the locked variant", async () => {
        const state = await mount<EmptyState>("saj-empty-state", {
            hass: createFakeHass(),
            locked: true,
            kind: "schedule",
            deviceId: "abc",
        });

        expect(inShadow(state, ".title").textContent).toContain(
            "locked_message",
        );
        expect(state.shadowRoot?.querySelector(".body")).toBeNull();
        shadowButton(state).click();

        expect(fireNavigate).toHaveBeenCalledWith({
            host: state,
            path: "/settings",
        });
    });
});
