import type {
    Hass,
    HassDevice,
    HassEntityRegistryEntry,
    HassEntityState,
} from "../hass";

export const INTEGRATION_PLATFORM = "saj_local";

const UNAVAILABLE_STATE = "unavailable";
const UNKNOWN_STATE = "unknown";

export interface SystemEntity {
    key: string;
    entityId: string;
    domain: string;
    state: HassEntityState;
}

export type SystemEntities = ReadonlyMap<string, SystemEntity>;

export interface SystemQuery {
    hass: Pick<Hass, "entities" | "states">;
    deviceId: string;
}

type SystemRegistryEntry = HassEntityRegistryEntry & {
    device_id: string;
    translation_key: string;
};

const isSystemRegistryEntry = (
    entry: HassEntityRegistryEntry,
): entry is SystemRegistryEntry =>
    entry.platform === INTEGRATION_PLATFORM &&
    entry.device_id !== null &&
    typeof entry.translation_key === "string" &&
    entry.translation_key !== "";

export const listSystemDevices = (
    hass: Pick<Hass, "entities" | "devices">,
): HassDevice[] => {
    const deviceIds = new Set(
        Object.values(hass.entities)
            .filter(isSystemRegistryEntry)
            .map((entry) => entry.device_id),
    );
    return Object.values(hass.devices).filter((device) =>
        deviceIds.has(device.id),
    );
};

export const systemEntityIds = ({
    hass,
    deviceId,
}: Pick<SystemQuery, "deviceId"> & {
    hass: Pick<Hass, "entities">;
}): string[] =>
    Object.values(hass.entities)
        .filter(
            (entry) =>
                isSystemRegistryEntry(entry) && entry.device_id === deviceId,
        )
        .map((entry) => entry.entity_id);

export const systemEntities = ({
    hass,
    deviceId,
}: SystemQuery): SystemEntities => {
    const entities = new Map<string, SystemEntity>();
    for (const entry of Object.values(hass.entities)) {
        const state = hass.states[entry.entity_id];
        if (
            !isSystemRegistryEntry(entry) ||
            entry.device_id !== deviceId ||
            state === undefined
        ) {
            continue;
        }
        entities.set(entry.translation_key, {
            key: entry.translation_key,
            entityId: entry.entity_id,
            domain: entry.entity_id.replace(/\..*$/, ""),
            state,
        });
    }
    return entities;
};

export interface SystemEntityOwner {
    deviceId: string;
    key: string;
}

export const ownerOfEntity = ({
    hass,
    entityId,
}: {
    hass: Pick<Hass, "entities">;
    entityId: string;
}): SystemEntityOwner | null => {
    const entry = hass.entities[entityId];
    if (entry === undefined || !isSystemRegistryEntry(entry)) {
        return null;
    }
    return { deviceId: entry.device_id, key: entry.translation_key };
};

export const isUnavailable = (entity: SystemEntity): boolean =>
    entity.state.state === UNAVAILABLE_STATE;

export const allUnavailable = (entities: readonly SystemEntity[]): boolean =>
    entities.length > 0 && entities.every(isUnavailable);

export const numericValue = (entity: SystemEntity): number | null => {
    const { state } = entity.state;
    if (
        state === UNAVAILABLE_STATE ||
        state === UNKNOWN_STATE ||
        state === ""
    ) {
        return null;
    }
    const value = Number(state);
    return Number.isFinite(value) ? value : null;
};

export const isOn = (entity: SystemEntity | undefined): boolean =>
    entity?.state.state === "on";
