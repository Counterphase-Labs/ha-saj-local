import type { Hass } from "../hass";
import { pageLocalizer, type Localize } from "../i18n/localize";
import { INTEGRATION_PLATFORM, listSystemDevices } from "../system/entities";

export interface EditorOption {
    value: string;
    label: string;
}

export interface EditorField {
    name: string;
    required?: boolean;
    default?: unknown;
    selector: Record<string, unknown>;
}

export interface EditorSchemaItem {
    name: string;
}

export interface ConfigForm {
    schema: EditorField[];
    computeLabel: (item: EditorSchemaItem) => string;
}

export const booleanField = ({
    name,
    fallback,
}: {
    name: string;
    fallback: boolean;
}): EditorField => ({
    name,
    default: fallback,
    selector: { boolean: {} },
});

export const selectField = ({
    name,
    options,
    fallback,
}: {
    name: string;
    options: readonly EditorOption[];
    fallback: string;
}): EditorField => ({
    name,
    default: fallback,
    selector: { select: { options, mode: "dropdown" } },
});

const DEVICE_FIELD: EditorField = {
    name: "device",
    required: true,
    selector: { device: { filter: { integration: INTEGRATION_PLATFORM } } },
};

export const configForm = (
    fields: (text: Localize) => readonly EditorField[],
): ConfigForm => {
    const text = pageLocalizer();
    return {
        schema: [DEVICE_FIELD, ...fields(text)],
        computeLabel: (item) => text(`option_${item.name}`),
    };
};

export const stubConfig = (
    hass: Pick<Hass, "entities" | "devices">,
): { device?: string } => {
    const [first] = listSystemDevices(hass);
    return first === undefined ? {} : { device: first.id };
};
