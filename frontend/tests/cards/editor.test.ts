import { beforeEach, describe, expect, it, vi } from "vitest";
import { entitiesModule } from "../fakes/entities";
import { localizeModule } from "../fakes/modules";

import {
    booleanField,
    configForm,
    selectField,
    stubConfig,
} from "../../src/cards/editor";
import { pageLocalizer } from "../../src/i18n/localize";
import { listSystemDevices } from "../../src/system/entities";
import { createFakeHass, fakeDevice } from "../fakes/hass";
import { fakeText } from "../fakes/modules";

vi.mock("../../src/i18n/localize", () => localizeModule());
vi.mock("../../src/system/entities", () => entitiesModule());

beforeEach(() => {
    vi.mocked(listSystemDevices).mockReset();
});

describe("editor fields", () => {
    it.each([true, false])(
        "offers a boolean selector showing the card's default of %s",
        (fallback) => {
            expect(booleanField({ name: "show_packs", fallback })).toEqual({
                name: "show_packs",
                default: fallback,
                selector: { boolean: {} },
            });
        },
    );

    it("offers a dropdown of the given options showing the card's default", () => {
        const options = [{ value: "a", label: "A" }];

        expect(selectField({ name: "scope", options, fallback: "a" })).toEqual({
            name: "scope",
            default: "a",
            selector: { select: { options, mode: "dropdown" } },
        });
    });
});

describe("configForm", () => {
    it("starts with the required device choice limited to the integration's devices", () => {
        const form = configForm(() => []);

        expect(form.schema).toEqual([
            {
                name: "device",
                required: true,
                selector: {
                    device: { filter: { integration: "saj_local" } },
                },
            },
        ]);
    });

    it("adds the element's own fields after the device choice, worded by the page language", () => {
        const fields = vi.fn(() => [
            booleanField({ name: "show_packs", fallback: true }),
        ]);

        const form = configForm(fields);

        expect(fields).toHaveBeenCalledWith(fakeText);
        expect(pageLocalizer).toHaveBeenCalled();
        expect(form.schema.map((field) => field.name)).toEqual([
            "device",
            "show_packs",
        ]);
    });

    it("labels every field from the page language's option text", () => {
        const form = configForm(() => []);

        expect(form.computeLabel({ name: "show_packs" })).toBe(
            "option_show_packs",
        );
    });
});

describe("stubConfig", () => {
    it("chooses the first SAJ Local system", () => {
        vi.mocked(listSystemDevices).mockReturnValue([
            fakeDevice("first"),
            fakeDevice("second"),
        ]);

        expect(stubConfig(createFakeHass())).toEqual({ device: "first" });
    });

    it("chooses nothing when there is no SAJ Local system", () => {
        vi.mocked(listSystemDevices).mockReturnValue([]);

        expect(stubConfig(createFakeHass())).toEqual({});
    });
});
