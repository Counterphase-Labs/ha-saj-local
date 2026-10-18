export interface HassEntityState {
    entity_id: string;
    state: string;
    attributes: Record<string, unknown>;
    last_changed: string;
}

export interface HassEntityRegistryEntry {
    entity_id: string;
    device_id: string | null;
    platform: string;
    translation_key?: string | null;
}

export interface HassDevice {
    id: string;
    name: string | null;
    name_by_user?: string | null;
    model?: string | null;
    serial_number?: string | null;
}

export type HassFirstWeekday =
    | "language"
    | "monday"
    | "tuesday"
    | "wednesday"
    | "thursday"
    | "friday"
    | "saturday"
    | "sunday";

export interface HassLocale {
    language: string;
    first_weekday: HassFirstWeekday;
}

export interface HassServiceTarget {
    entity_id: string;
}

export interface HassServiceError {
    message?: string;
    translation_key?: string;
    translation_domain?: string;
    translation_placeholders?: Record<string, string>;
}

export type HassLocalize = (
    key: string,
    values?: Record<string, string | number>,
) => string;

export interface HassEntityNameItem {
    type: "entity" | "device" | "area" | "floor";
}

export interface Hass {
    states: Record<string, HassEntityState>;
    entities: Record<string, HassEntityRegistryEntry>;
    devices: Record<string, HassDevice>;
    locale: HassLocale;
    language: string;
    callService: (
        domain: string,
        service: string,
        serviceData?: Record<string, unknown>,
        target?: HassServiceTarget,
    ) => Promise<unknown>;
    localize: HassLocalize;
    loadBackendTranslation: (
        category: string,
        integration?: string,
    ) => Promise<HassLocalize>;
    formatEntityState: (stateObj: HassEntityState, state?: string) => string;
    formatEntityName: (
        stateObj: HassEntityState,
        content: readonly HassEntityNameItem[],
    ) => string;
}

export interface SajElementConfig {
    type: string;
    device?: string;
}
