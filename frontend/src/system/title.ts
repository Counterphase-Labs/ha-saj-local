import type { Hass, HassDevice } from "../hass";
import { listSystemDevices } from "./entities";

const TITLE_SEPARATOR = " ";
const SERIAL_SEPARATOR = " - ";

const baseTitle = (device: HassDevice): string => {
    const name = device.name_by_user ?? device.name ?? "";
    return [name, device.model ?? ""]
        .filter((part) => part !== "")
        .join(TITLE_SEPARATOR);
};

export const systemTitles = (
    hass: Pick<Hass, "entities" | "devices">,
): ReadonlyMap<string, string> => {
    const systems = listSystemDevices(hass).map((device) => ({
        device,
        base: baseTitle(device),
    }));
    return new Map(
        systems.map(({ device, base }) => {
            const shared =
                systems.filter((other) => other.base === base).length > 1;
            const serial = device.serial_number ?? "";
            return [
                device.id,
                shared && serial !== ""
                    ? `${base}${SERIAL_SEPARATOR}${serial}`
                    : base,
            ];
        }),
    );
};

export const systemTitle = ({
    hass,
    deviceId,
}: {
    hass: Pick<Hass, "entities" | "devices">;
    deviceId: string;
}): string => systemTitles(hass).get(deviceId) ?? "";
