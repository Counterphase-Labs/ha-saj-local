export type Translations = Readonly<Record<string, string>>;
export type TextValues = Readonly<Record<string, string | number>>;
export type Localize = (key: string, values?: TextValues) => string;

export const FALLBACK_LANGUAGE = "en";

const LANGUAGE_FILES = import.meta.glob<Translations>("./*.json", {
    eager: true,
    import: "default",
});

const LANGUAGE_FILE_AFFIXES = /^\.\/|\.json$/g;

export const bundledTranslations = (): ReadonlyMap<string, Translations> =>
    new Map(
        Object.entries(LANGUAGE_FILES).map(([path, translations]) => [
            path.replace(LANGUAGE_FILE_AFFIXES, "").toLowerCase(),
            translations,
        ]),
    );

export const resolveLanguage = ({
    language,
    available,
}: {
    language: string;
    available: ReadonlyMap<string, Translations>;
}): string => {
    const normalised = language.toLowerCase().replaceAll("_", "-");
    const base = normalised.replace(/-.*$/, "");
    return (
        [normalised, base].find((candidate) => available.has(candidate)) ??
        FALLBACK_LANGUAGE
    );
};

const fillPlaceholders = ({
    template,
    values,
}: {
    template: string;
    values: TextValues;
}): string =>
    template.replace(/\{(\w+)\}/g, (placeholder, name: string) =>
        name in values ? String(values[name]) : placeholder,
    );

export const createLocalizer = ({
    language,
    available,
}: {
    language: string;
    available: ReadonlyMap<string, Translations>;
}): Localize => {
    const chosen = available.get(resolveLanguage({ language, available }));
    const fallback = available.get(FALLBACK_LANGUAGE);
    const plurals = new Intl.PluralRules(language);
    const lookup = (key: string): string | undefined =>
        chosen?.[key] ?? fallback?.[key];
    return (key, values = {}) => {
        const count = values.count;
        const pluralKey =
            typeof count === "number"
                ? `${key}_${plurals.select(count)}`
                : undefined;
        const template =
            (pluralKey === undefined ? undefined : lookup(pluralKey)) ??
            lookup(key) ??
            key;
        return fillPlaceholders({ template, values });
    };
};

const localizers = new Map<string, Localize>();

export const localizerFor = (language: string): Localize => {
    const cached = localizers.get(language);
    if (cached !== undefined) {
        return cached;
    }
    const created = createLocalizer({
        language,
        available: bundledTranslations(),
    });
    localizers.set(language, created);
    return created;
};

export const pageLocalizer = (): Localize =>
    localizerFor(document.documentElement.lang || FALLBACK_LANGUAGE);

const RELATIVE_UNITS: readonly {
    name: Intl.RelativeTimeFormatUnit;
    seconds: number;
}[] = [
    { name: "day", seconds: 86_400 },
    { name: "hour", seconds: 3_600 },
    { name: "minute", seconds: 60 },
];

export const relativeTimeText = ({
    from,
    now,
    language,
}: {
    from: Date;
    now: Date;
    language: string;
}): string => {
    const seconds = Math.round((from.getTime() - now.getTime()) / 1000);
    const formatter = new Intl.RelativeTimeFormat(language, {
        numeric: "auto",
    });
    const unit = RELATIVE_UNITS.find(
        (candidate) => Math.abs(seconds) >= candidate.seconds,
    );
    return unit === undefined
        ? formatter.format(seconds, "second")
        : formatter.format(Math.round(seconds / unit.seconds), unit.name);
};
