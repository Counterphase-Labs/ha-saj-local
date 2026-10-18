import { vi } from "vitest";

import type { HassEntityState } from "../../src/hass";
import type { SystemEntity } from "../../src/system/entities";

export interface EntityOptions {
    attributes?: Record<string, unknown>;
    lastChanged?: string;
    entityId?: string;
}

export const entity = (
    key: string,
    domain: string,
    state: string,
    { attributes = {}, lastChanged = "", entityId }: EntityOptions = {},
): SystemEntity => {
    const id = entityId ?? `${domain}.saj_${key}`;
    const stateObject: HassEntityState = {
        entity_id: id,
        state,
        attributes,
        last_changed: lastChanged,
    };
    return { key, entityId: id, domain, state: stateObject };
};

export const entityMap = (
    entities: readonly SystemEntity[],
): Map<string, SystemEntity> =>
    new Map(entities.map((item) => [item.key, item]));

const UNAVAILABLE = "unavailable";
const NOT_NUMERIC = new Set([UNAVAILABLE, "unknown", ""]);

export const entitiesModule = () => ({
    INTEGRATION_PLATFORM: "saj_local",
    isOn: vi.fn((item: SystemEntity | undefined) => item?.state.state === "on"),
    isUnavailable: vi.fn(
        (item: SystemEntity) => item.state.state === UNAVAILABLE,
    ),
    allUnavailable: vi.fn(
        (items: readonly SystemEntity[]) =>
            items.length > 0 &&
            items.every((item) => item.state.state === UNAVAILABLE),
    ),
    numericValue: vi.fn((item: SystemEntity) => {
        const { state } = item.state;
        const value = Number(state);
        return NOT_NUMERIC.has(state) || !Number.isFinite(value) ? null : value;
    }),
    listSystemDevices: vi.fn(() => []),
    systemEntities: vi.fn(() => new Map<string, SystemEntity>()),
    systemEntityIds: vi.fn(() => [] as string[]),
    ownerOfEntity: vi.fn(() => null),
});
