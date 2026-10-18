import type { PropertyValues } from "lit";

import type { Hass } from "../hass";
import { SystemRedraw } from "../system/redraw";
import { LocalizedElement } from "./localized-element";

export abstract class SystemElement extends LocalizedElement {
    private readonly redraw = new SystemRedraw();

    protected abstract watchedDeviceId(): string | undefined;

    protected override shouldUpdate(changed: PropertyValues): boolean {
        const previous = changed.get("hass") as Hass | undefined;
        const { hass } = this;
        if (
            changed.size !== 1 ||
            previous === undefined ||
            hass === undefined
        ) {
            return true;
        }
        return this.redraw.needed({
            previous,
            next: hass,
            deviceId: this.watchedDeviceId(),
        });
    }
}
