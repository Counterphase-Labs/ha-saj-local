import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { entitiesModule } from "../fakes/entities";

import {
    changeErrorMessage,
    controlLock,
    ControlTracker,
    DelayedCommit,
    pressButtonRequest,
    selectOptionRequest,
    setNumberRequest,
    setSwitchRequest,
    setTimeRequest,
    WEEKDAY_COMMIT_DELAY_MILLISECONDS,
} from "../../src/system/control";
import { entity, entityMap } from "../fakes/entities";
import { createFakeHass, type FakeHass } from "../fakes/hass";

vi.mock("../../src/system/entities", () => entitiesModule());

const lockOf = (state: string | null) =>
    controlLock(
        entityMap(
            state === null
                ? []
                : [entity("control_allowed", "binary_sensor", state)],
        ),
    );

describe("controlLock", () => {
    it.each([
        { state: "off", locked: true },
        { state: "on", locked: false },
        { state: "unavailable", locked: false },
        { state: "unknown", locked: false },
        { state: null, locked: false },
    ])("is locked $locked for control_allowed $state", ({ state, locked }) => {
        expect(lockOf(state).locked).toBe(locked);
    });

    it("exposes the control_allowed entity when it exists", () => {
        expect(lockOf("off").entity?.key).toBe("control_allowed");
        expect(lockOf(null).entity).toBeNull();
    });
});

describe("service requests", () => {
    it("carries the value of each control to its domain", () => {
        expect(setNumberRequest(12)).toMatchObject({
            domain: "number",
            data: { value: 12 },
        });
        expect(selectOptionRequest("backup")).toMatchObject({
            domain: "select",
            data: { option: "backup" },
        });
        expect(setTimeRequest("08:30")).toMatchObject({
            domain: "time",
            data: { time: "08:30" },
        });
        expect(pressButtonRequest()).toMatchObject({ domain: "button" });
    });

    it("turns a switch on and off with different services", () => {
        expect(setSwitchRequest(true).service).not.toBe(
            setSwitchRequest(false).service,
        );
        expect(setSwitchRequest(true).domain).toBe("switch");
    });
});

describe("changeErrorMessage", () => {
    const hass = createFakeHass({
        backendTranslations: {
            "component.saj_local.exceptions.protected_setting.message":
                "{setting} is protected",
        },
    });

    it("translates an integration error with its placeholders", async () => {
        const message = await changeErrorMessage({
            hass,
            error: {
                translation_domain: "saj_local",
                translation_key: "protected_setting",
                translation_placeholders: { setting: "Grid code" },
                message: "plain",
            },
        });

        expect(message).toBe("Grid code is protected");
    });

    it("falls back to the plain message when the translation is missing", async () => {
        const message = await changeErrorMessage({
            hass,
            error: {
                translation_domain: "saj_local",
                translation_key: "unknown_key",
                message: "plain",
            },
        });

        expect(message).toBe("plain");
    });

    it.each([
        {
            description: "another integration's translated error",
            error: {
                translation_domain: "other",
                translation_key: "x",
                message: "other message",
            },
            expected: "other message",
        },
        {
            description: "an error without a translation key",
            error: { translation_domain: "saj_local", message: "no key" },
            expected: "no key",
        },
        {
            description: "a plain Error",
            error: new Error("boom"),
            expected: "boom",
        },
        {
            description: "a string",
            error: "text failure",
            expected: "text failure",
        },
        { description: "nothing", error: undefined, expected: "undefined" },
    ])("shows $description as given", async ({ error, expected }) => {
        expect(await changeErrorMessage({ hass, error })).toBe(expected);
    });
});

describe("ControlTracker", () => {
    const entityId = "number.saj_1_backup_reserve_soc";

    const setup = (hass: FakeHass | undefined) => {
        const host = { requestUpdate: vi.fn() };
        const tracker = new ControlTracker(host as never, () => hass);
        return { host, tracker };
    };

    it("calls the service on the entity and clears busy afterwards", async () => {
        const hass = createFakeHass();
        const { tracker, host } = setup(hass);

        await tracker.submit({ entityId, request: setNumberRequest(30) });

        expect(hass.serviceCalls).toEqual([
            {
                domain: "number",
                service: "set_value",
                data: { value: 30 },
                target: { entity_id: entityId },
            },
        ]);
        expect(tracker.isBusy(entityId)).toBe(false);
        expect(host.requestUpdate).toHaveBeenCalledTimes(2);
    });

    it("is busy while the call is in progress and ignores a second submit", async () => {
        const hass = createFakeHass();
        const { release } = hass.holdNextCall();
        const { tracker } = setup(hass);

        const first = tracker.submit({
            entityId,
            request: setNumberRequest(30),
        });
        await tracker.submit({ entityId, request: setNumberRequest(40) });

        expect(tracker.isBusy(entityId)).toBe(true);
        expect(hass.serviceCalls).toHaveLength(1);
        release();
        await first;
        expect(tracker.isBusy(entityId)).toBe(false);
    });

    it("keeps the error until the next change of the same control", async () => {
        const hass = createFakeHass();
        hass.rejectNextCall({ message: "refused" });
        const { tracker } = setup(hass);

        await tracker.submit({ entityId, request: setNumberRequest(30) });

        expect(tracker.errorOf(entityId)).toBe("refused");
        expect(tracker.errorOf("number.other")).toBeNull();
        expect(tracker.isBusy(entityId)).toBe(false);

        await tracker.submit({ entityId, request: setNumberRequest(31) });

        expect(tracker.errorOf(entityId)).toBeNull();
    });

    it("does nothing without hass", async () => {
        const { tracker, host } = setup(undefined);

        await tracker.submit({ entityId, request: setNumberRequest(30) });

        expect(host.requestUpdate).not.toHaveBeenCalled();
        expect(tracker.isBusy(entityId)).toBe(false);
    });
});

describe("DelayedCommit", () => {
    beforeEach(() => {
        vi.useFakeTimers();
    });

    afterEach(() => {
        vi.useRealTimers();
    });

    const setup = () => {
        const commit = vi.fn();
        return {
            commit,
            delayed: new DelayedCommit<number>({
                delayMilliseconds: WEEKDAY_COMMIT_DELAY_MILLISECONDS,
                commit,
            }),
        };
    };

    it("commits the last value once, after the delay since the last push", () => {
        const { commit, delayed } = setup();

        delayed.push(1);
        vi.advanceTimersByTime(WEEKDAY_COMMIT_DELAY_MILLISECONDS - 1);
        delayed.push(2);
        vi.advanceTimersByTime(WEEKDAY_COMMIT_DELAY_MILLISECONDS - 1);

        expect(commit).not.toHaveBeenCalled();

        vi.advanceTimersByTime(1);

        expect(commit).toHaveBeenCalledExactlyOnceWith(2);
    });

    it("commits at once on flush and not again when the delay passes", () => {
        const { commit, delayed } = setup();

        delayed.push(5);
        delayed.flush();
        vi.advanceTimersByTime(WEEKDAY_COMMIT_DELAY_MILLISECONDS * 2);

        expect(commit).toHaveBeenCalledExactlyOnceWith(5);
    });

    it("commits nothing on flush when nothing is pending", () => {
        const { commit, delayed } = setup();

        delayed.flush();

        expect(commit).not.toHaveBeenCalled();
    });

    it("commits nothing after cancel", () => {
        const { commit, delayed } = setup();

        delayed.push(5);
        delayed.cancel();
        delayed.flush();
        vi.advanceTimersByTime(WEEKDAY_COMMIT_DELAY_MILLISECONDS * 2);

        expect(commit).not.toHaveBeenCalled();
    });
});
