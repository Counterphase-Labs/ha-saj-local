export const ACTION_EVENT = "hass-action";
export const SETTINGS_PATH = "/config/integrations/integration/saj_local";
export const deviceDetailPath = (deviceId: string): string =>
    `/config/devices/device/${deviceId}`;

export const fireMoreInfo = ({
    host,
    entityId,
}: {
    host: EventTarget;
    entityId: string;
}): void => {
    host.dispatchEvent(
        new CustomEvent(ACTION_EVENT, {
            bubbles: true,
            composed: true,
            detail: {
                action: "tap",
                config: {
                    entity: entityId,
                    tap_action: { action: "more-info" },
                },
            },
        }),
    );
};

export const fireNavigate = ({
    host,
    path,
}: {
    host: EventTarget;
    path: string;
}): void => {
    host.dispatchEvent(
        new CustomEvent(ACTION_EVENT, {
            bubbles: true,
            composed: true,
            detail: {
                action: "tap",
                config: {
                    tap_action: { action: "navigate", navigation_path: path },
                },
            },
        }),
    );
};
