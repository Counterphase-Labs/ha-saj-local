import type { Hass } from "../hass";
import { systemEntityIds } from "./entities";

export type RedrawHass = Pick<
    Hass,
    "entities" | "devices" | "language" | "locale" | "states"
>;

export class SystemRedraw {
    private registry: RedrawHass["entities"] | undefined;
    private cachedDeviceId: string | undefined;
    private entityIds: readonly string[] = [];

    needed({
        previous,
        next,
        deviceId,
    }: {
        previous: RedrawHass;
        next: RedrawHass;
        deviceId: string | undefined;
    }): boolean {
        if (
            previous.entities !== next.entities ||
            previous.devices !== next.devices ||
            previous.language !== next.language ||
            previous.locale !== next.locale
        ) {
            return true;
        }
        return this.idsOf({ hass: next, deviceId }).some(
            (entityId) => previous.states[entityId] !== next.states[entityId],
        );
    }

    private idsOf({
        hass,
        deviceId,
    }: {
        hass: RedrawHass;
        deviceId: string | undefined;
    }): readonly string[] {
        if (
            this.registry !== hass.entities ||
            this.cachedDeviceId !== deviceId
        ) {
            this.registry = hass.entities;
            this.cachedDeviceId = deviceId;
            this.entityIds =
                deviceId === undefined
                    ? []
                    : systemEntityIds({ hass, deviceId });
        }
        return this.entityIds;
    }
}
