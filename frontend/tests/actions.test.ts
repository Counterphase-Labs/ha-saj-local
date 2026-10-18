import { describe, expect, it } from "vitest";

import {
    ACTION_EVENT,
    deviceDetailPath,
    fireMoreInfo,
    fireNavigate,
} from "../src/actions";

const capture = (
    fire: (host: EventTarget) => void,
): CustomEvent<unknown> | undefined => {
    const host = new EventTarget();
    let received: CustomEvent<unknown> | undefined;
    host.addEventListener(ACTION_EVENT, (event) => {
        received = event as CustomEvent<unknown>;
    });
    fire(host);
    return received;
};

describe("actions", () => {
    it("fires a more-info action for the entity", () => {
        const event = capture((host) => {
            fireMoreInfo({ host, entityId: "sensor.pv_power" });
        });

        expect(event?.detail).toEqual({
            action: "tap",
            config: {
                entity: "sensor.pv_power",
                tap_action: { action: "more-info" },
            },
        });
        expect(event?.bubbles).toBe(true);
        expect(event?.composed).toBe(true);
    });

    it("fires a navigate action to the path", () => {
        const event = capture((host) => {
            fireNavigate({ host, path: "/config" });
        });

        expect(event?.detail).toEqual({
            action: "tap",
            config: {
                tap_action: { action: "navigate", navigation_path: "/config" },
            },
        });
    });

    it("builds the device page path from the device id", () => {
        expect(deviceDetailPath("abc")).toContain("abc");
    });
});
