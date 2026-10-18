import type { Hass } from "./hass";
import { pageLocalizer } from "./i18n/localize";

export interface CardPickerEntry {
    type: string;
    name: string;
    description: string;
    preview?: boolean;
}

export interface CardFeatureContext {
    entity_id?: string;
}

export interface CardFeaturePickerEntry {
    type: string;
    name: string;
    isSupported?: (hass: Hass, context: CardFeatureContext) => boolean;
    configurable?: boolean;
}

export interface BadgePickerEntry {
    type: string;
    name: string;
    description: string;
}

declare global {
    interface Window {
        customCards?: CardPickerEntry[];
        customCardFeatures?: CardFeaturePickerEntry[];
        customBadges?: BadgePickerEntry[];
    }
}

export interface PickerTextKeys {
    nameKey: string;
    descriptionKey: string;
}

export const registerCard = ({
    type,
    nameKey,
    descriptionKey,
    preview,
}: PickerTextKeys & Pick<CardPickerEntry, "type" | "preview">): void => {
    window.customCards ??= [];
    window.customCards.push({
        type,
        preview,
        get name() {
            return pageLocalizer()(nameKey);
        },
        get description() {
            return pageLocalizer()(descriptionKey);
        },
    });
};

export const registerCardFeature = ({
    type,
    nameKey,
    isSupported,
    configurable,
}: Pick<PickerTextKeys, "nameKey"> &
    Pick<
        CardFeaturePickerEntry,
        "type" | "isSupported" | "configurable"
    >): void => {
    window.customCardFeatures ??= [];
    window.customCardFeatures.push({
        type,
        isSupported,
        configurable,
        get name() {
            return pageLocalizer()(nameKey);
        },
    });
};

export const registerBadge = ({
    type,
    nameKey,
    descriptionKey,
}: PickerTextKeys & Pick<BadgePickerEntry, "type">): void => {
    window.customBadges ??= [];
    window.customBadges.push({
        type,
        get name() {
            return pageLocalizer()(nameKey);
        },
        get description() {
            return pageLocalizer()(descriptionKey);
        },
    });
};
