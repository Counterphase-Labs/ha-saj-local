import type {
    Hass,
    HassDevice,
    HassEntityRegistryEntry,
    HassEntityState,
    HassFirstWeekday,
    HassServiceError,
    HassServiceTarget,
} from "../../src/hass";
export const SAJ_PLATFORM = "saj_local";
export const DEFAULT_DEVICE_ID = "saj_1";
export const DEFAULT_LAST_CHANGED = "2026-10-17T10:00:00+00:00";

export interface FakeEntity {
    key: string;
    domain: string;
    state: string;
    attributes?: Record<string, unknown>;
    deviceId?: string;
    platform?: string;
    lastChanged?: string;
}

export interface RecordedServiceCall {
    domain: string;
    service: string;
    data: Record<string, unknown> | undefined;
    target: HassServiceTarget | undefined;
}

export interface FakeHassOptions {
    entities?: readonly FakeEntity[];
    devices?: readonly HassDevice[];
    language?: string;
    firstWeekday?: HassFirstWeekday;
    backendTranslations?: Readonly<Record<string, string>>;
}

export interface FakeHass extends Hass {
    serviceCalls: RecordedServiceCall[];
    rejectNextCall: (failure: HassServiceError) => void;
    holdNextCall: () => { release: () => void };
}

export const fakeEntityId = (entity: FakeEntity): string =>
    `${entity.domain}.${entity.deviceId ?? DEFAULT_DEVICE_ID}_${entity.key}`;

const fillPlaceholders = (
    template: string,
    values: Record<string, string | number> | undefined,
): string =>
    template.replace(/\{(\w+)\}/g, (placeholder, name: string) =>
        values !== undefined && name in values
            ? String(values[name])
            : placeholder,
    );

export const createFakeHass = ({
    entities = [],
    devices = [],
    language = "en",
    firstWeekday = "monday",
    backendTranslations = {},
}: FakeHassOptions = {}): FakeHass => {
    const states: Record<string, HassEntityState> = {};
    const registry: Record<string, HassEntityRegistryEntry> = {};
    for (const entity of entities) {
        const entityId = fakeEntityId(entity);
        states[entityId] = {
            entity_id: entityId,
            state: entity.state,
            attributes: entity.attributes ?? {},
            last_changed: entity.lastChanged ?? DEFAULT_LAST_CHANGED,
        };
        registry[entityId] = {
            entity_id: entityId,
            device_id: entity.deviceId ?? DEFAULT_DEVICE_ID,
            platform: entity.platform ?? SAJ_PLATFORM,
            translation_key: entity.key,
        };
    }

    const serviceCalls: RecordedServiceCall[] = [];
    let nextFailure: HassServiceError | null = null;
    let held: { gate: Promise<void> } | null = null;

    return {
        states,
        entities: registry,
        devices: Object.fromEntries(
            devices.map((device) => [device.id, device]),
        ),
        language,
        locale: { language, first_weekday: firstWeekday },
        serviceCalls,
        callService: (domain, service, data, target) => {
            serviceCalls.push({ domain, service, data, target });
            const gate = held?.gate ?? Promise.resolve();
            held = null;
            const failure = nextFailure;
            nextFailure = null;
            return gate.then(() =>
                failure === null
                    ? undefined
                    : Promise.reject(
                          Object.assign(
                              new Error(failure.message ?? ""),
                              failure,
                          ),
                      ),
            );
        },
        rejectNextCall: (failure) => {
            nextFailure = failure;
        },
        holdNextCall: () => {
            let release = (): void => undefined;
            held = {
                gate: new Promise<void>((resolve) => {
                    release = resolve;
                }),
            };
            return { release };
        },
        localize: (key) => key,
        loadBackendTranslation: () =>
            Promise.resolve((key, values) =>
                fillPlaceholders(backendTranslations[key] ?? "", values),
            ),
        formatEntityState: (stateObj, state) =>
            `${state ?? stateObj.state}${
                typeof stateObj.attributes.unit_of_measurement === "string"
                    ? ` ${stateObj.attributes.unit_of_measurement}`
                    : ""
            }`,
        formatEntityName: (stateObj) =>
            registry[stateObj.entity_id]?.translation_key ?? "",
    };
};

export const fakeEntity = (
    key: string,
    domain: string,
    state: string,
    extra: Partial<FakeEntity> = {},
): FakeEntity => ({ key, domain, state, ...extra });

export const fakeDevice = (
    id: string,
    extra: Partial<HassDevice> = {},
): HassDevice => ({ id, name: "SAJ", model: "HS3 (12000 W)", ...extra });
