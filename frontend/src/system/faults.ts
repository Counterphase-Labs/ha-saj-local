import type { SystemEntities, SystemEntity } from "./entities";
import { isOn } from "./entities";

export type FaultGroupId = "inverter" | "battery" | "ev";

export interface FaultGroupDefinition {
    id: FaultGroupId;
    summaryKey: string;
    prefix: string;
}

export const FAULT_GROUPS: readonly FaultGroupDefinition[] = [
    { id: "inverter", summaryKey: "inverter_fault", prefix: "inverter" },
    { id: "battery", summaryKey: "battery_fault", prefix: "battery" },
    { id: "ev", summaryKey: "ev_fault", prefix: "ev" },
];

const BATTERY_PACK_FAULT_KEY = /^battery_pack\d+_(fault|warning)$/;
const UNRECOGNISED_SUFFIX = "_fault_unrecognised";

export interface FaultRow {
    entity: SystemEntity;
    since: Date;
    unrecognised: boolean;
}

export interface FaultGroup {
    id: FaultGroupId;
    summary: SystemEntity;
    active: boolean;
    rows: FaultRow[];
}

const belongsToGroup = ({
    definition,
    key,
}: {
    definition: FaultGroupDefinition;
    key: string;
}): boolean =>
    key.startsWith(`${definition.prefix}_fault_`) ||
    (definition.id === "battery" && BATTERY_PACK_FAULT_KEY.test(key));

export const faultGroups = (entities: SystemEntities): FaultGroup[] =>
    FAULT_GROUPS.flatMap((definition) => {
        const summary = entities.get(definition.summaryKey);
        if (summary === undefined) {
            return [];
        }
        const rows = [...entities.values()]
            .filter(
                (entity) =>
                    entity.domain === "binary_sensor" &&
                    isOn(entity) &&
                    belongsToGroup({ definition, key: entity.key }),
            )
            .sort((left, right) => left.key.localeCompare(right.key))
            .map((entity) => ({
                entity,
                since: new Date(entity.state.last_changed),
                unrecognised: entity.key.endsWith(UNRECOGNISED_SUFFIX),
            }));
        return [{ id: definition.id, summary, active: isOn(summary), rows }];
    });

export const activeFaultSummaries = (
    entities: SystemEntities,
): SystemEntity[] =>
    FAULT_GROUPS.flatMap((definition) => {
        const summary = entities.get(definition.summaryKey);
        return summary !== undefined && isOn(summary) ? [summary] : [];
    });
