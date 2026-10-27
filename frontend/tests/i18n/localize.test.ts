import { readdirSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

import { afterEach, describe, expect, it } from "vitest";

import {
    bundledTranslations,
    createLocalizer,
    FALLBACK_LANGUAGE,
    localizerFor,
    pageLocalizer,
    relativeTimeText,
    resolveLanguage,
    type Translations,
} from "../../src/i18n/localize";

const available = new Map<string, Translations>([
    [
        "en",
        {
            hello: "Hello {name}",
            only_english: "English only",
            things_one: "{count} thing",
            things_other: "{count} things",
            things: "things",
        },
    ],
    [
        "de",
        {
            hello: "Hallo {name}",
            things_one: "{count} Ding",
            things_other: "{count} Dinge",
        },
    ],
    ["pt-br", { hello: "Ola {name}" }],
]);

describe("resolveLanguage", () => {
    it.each([
        { language: "de", expected: "de" },
        { language: "de-AT", expected: "de" },
        { language: "DE_de", expected: "de" },
        { language: "pt-BR", expected: "pt-br" },
        { language: "fr", expected: FALLBACK_LANGUAGE },
    ])("$language resolves to $expected", ({ language, expected }) => {
        expect(resolveLanguage({ language, available })).toBe(expected);
    });
});

describe("createLocalizer", () => {
    it("fills placeholders in the user's language", () => {
        const text = createLocalizer({ language: "de", available });

        expect(text("hello", { name: "Anna" })).toBe("Hallo Anna");
    });

    it("falls back to English for a missing key", () => {
        const text = createLocalizer({ language: "de", available });

        expect(text("only_english")).toBe("English only");
    });

    it("falls back to English for a missing language", () => {
        const text = createLocalizer({ language: "fr", available });

        expect(text("hello", { name: "Anna" })).toBe("Hello Anna");
    });

    it("returns the key when no language has it", () => {
        const text = createLocalizer({ language: "de", available });

        expect(text("nothing_here")).toBe("nothing_here");
    });

    it("keeps a placeholder that has no value", () => {
        const text = createLocalizer({ language: "en", available });

        expect(text("hello")).toBe("Hello {name}");
    });

    it("chooses the plural form for a count", () => {
        const text = createLocalizer({ language: "en", available });

        expect(text("things", { count: 1 })).toBe("1 thing");
        expect(text("things", { count: 3 })).toBe("3 things");
    });

    it("uses the plain key for a count when no plural form exists", () => {
        const text = createLocalizer({ language: "en", available });

        expect(text("only_english", { count: 2 })).toBe("English only");
    });

    it("works with no English table at all", () => {
        const text = createLocalizer({ language: "de", available: new Map() });

        expect(text("hello")).toBe("hello");
    });
});

describe("bundled language files", () => {
    const sourceDirectory = resolve(import.meta.dirname, "../../src/i18n");
    const translationsDirectory = resolve(
        import.meta.dirname,
        "../../../custom_components/saj_local/translations",
    );
    const languagesIn = (directory: string): string[] =>
        readdirSync(directory)
            .filter((file) => file.endsWith(".json"))
            .map((file) => file.slice(0, -".json".length))
            .sort();

    it("has one file for each language the integration has", () => {
        expect(languagesIn(sourceDirectory)).toEqual(
            languagesIn(translationsDirectory),
        );
    });

    it("gives every language the keys of English, with the plural forms of the language", () => {
        const pluralSuffix = /_(zero|one|two|few|many|other)$/;
        const english = Object.keys(
            JSON.parse(
                readFileSync(resolve(sourceDirectory, "en.json"), "utf8"),
            ) as Translations,
        );
        const plainKeys = english.filter((key) => !pluralSuffix.test(key));
        const pluralBases = [
            ...new Set(
                english
                    .filter((key) => pluralSuffix.test(key))
                    .map((key) => key.replace(pluralSuffix, "")),
            ),
        ];

        for (const [language, translations] of bundledTranslations()) {
            const forms = new Intl.PluralRules(language).resolvedOptions()
                .pluralCategories;
            const expected = [
                ...plainKeys,
                ...pluralBases.flatMap((base) =>
                    forms.map((form) => `${base}_${form}`),
                ),
            ].sort();

            expect(Object.keys(translations).sort(), language).toEqual(
                expected,
            );
        }
    });

    it("loads every file and ignores nothing", () => {
        expect([...bundledTranslations().keys()].sort()).toEqual(
            languagesIn(sourceDirectory).map((language) =>
                language.toLowerCase(),
            ),
        );
    });

    it("returns the same localizer for the same language", () => {
        expect(localizerFor("en")).toBe(localizerFor("en"));
        expect(localizerFor("en")("busy")).not.toBe("busy");
    });
});

describe("pageLocalizer", () => {
    afterEach(() => {
        document.documentElement.lang = "";
    });

    it("speaks the language of the page", () => {
        document.documentElement.lang = "de";

        expect(pageLocalizer()("busy")).toBe(localizerFor("de")("busy"));
    });

    it("falls back to the fallback language when the page names none", () => {
        document.documentElement.lang = "";

        expect(pageLocalizer()("busy")).toBe(
            localizerFor(FALLBACK_LANGUAGE)("busy"),
        );
    });
});

describe("relativeTimeText", () => {
    const now = new Date("2026-10-17T12:00:00Z");
    const ago = (seconds: number) => new Date(now.getTime() - seconds * 1000);

    it.each([
        { seconds: 30, unit: "second" },
        { seconds: 5 * 60, unit: "minute" },
        { seconds: 3 * 3600, unit: "hour" },
        { seconds: 3 * 86_400, unit: "day" },
    ])("reads $seconds seconds ago in the unit $unit", ({ seconds, unit }) => {
        const expected = new Intl.RelativeTimeFormat("en", { numeric: "auto" });
        const divisor =
            { second: 1, minute: 60, hour: 3600, day: 86_400 }[unit] ?? 1;

        expect(
            relativeTimeText({ from: ago(seconds), now, language: "en" }),
        ).toBe(
            expected.format(
                -seconds / divisor,
                unit as Intl.RelativeTimeFormatUnit,
            ),
        );
    });

    it("follows the language", () => {
        expect(
            relativeTimeText({ from: ago(300), now, language: "de" }),
        ).not.toBe(relativeTimeText({ from: ago(300), now, language: "en" }));
    });
});
