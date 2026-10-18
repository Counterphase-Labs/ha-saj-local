import { afterEach, describe, expect, it, vi } from "vitest";

import {
    registerBadge,
    registerCard,
    registerCardFeature,
} from "../src/registration";

vi.mock("../src/i18n/localize", () => ({
    pageLocalizer: () => (key: string) =>
        `${document.documentElement.lang}:${key}`,
}));

afterEach(() => {
    delete window.customCards;
    delete window.customCardFeatures;
    delete window.customBadges;
    document.documentElement.lang = "";
});

describe("picker registration", () => {
    it("creates each list on first use", () => {
        registerCard({
            type: "a-card",
            nameKey: "name",
            descriptionKey: "description",
        });
        registerCardFeature({ type: "a-feature", nameKey: "name" });
        registerBadge({
            type: "a-badge",
            nameKey: "name",
            descriptionKey: "description",
        });

        expect(window.customCards?.map((entry) => entry.type)).toEqual([
            "a-card",
        ]);
        expect(window.customCardFeatures?.map((entry) => entry.type)).toEqual([
            "a-feature",
        ]);
        expect(window.customBadges?.map((entry) => entry.type)).toEqual([
            "a-badge",
        ]);
    });

    it("adds to a list another card already created without removing its entries", () => {
        const foreign = { type: "foreign-card", name: "X", description: "d" };
        window.customCards = [foreign];

        registerCard({
            type: "a-card",
            nameKey: "name",
            descriptionKey: "description",
        });

        expect(window.customCards).toHaveLength(2);
        expect(window.customCards[0]).toBe(foreign);
    });

    it("words every entry in the page language at the moment the picker reads it", () => {
        registerCard({
            type: "a-card",
            nameKey: "card_name",
            descriptionKey: "card_description",
        });
        registerCardFeature({ type: "a-feature", nameKey: "feature_name" });
        registerBadge({
            type: "a-badge",
            nameKey: "badge_name",
            descriptionKey: "badge_description",
        });

        document.documentElement.lang = "de";

        expect(window.customCards?.[0]).toMatchObject({
            name: "de:card_name",
            description: "de:card_description",
        });
        expect(window.customCardFeatures?.[0]?.name).toBe("de:feature_name");
        expect(window.customBadges?.[0]).toMatchObject({
            name: "de:badge_name",
            description: "de:badge_description",
        });
    });
});
