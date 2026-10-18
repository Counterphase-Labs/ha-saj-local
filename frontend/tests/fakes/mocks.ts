import { vi } from "vitest";

import type { ControlTracker } from "../../src/system/control";

export const resultOf = (mocked: (...args: never[]) => unknown): unknown => {
    const [first]: readonly { value: unknown }[] =
        vi.mocked(mocked).mock.results;
    return first?.value;
};

export const trackerMocks = (tracker: ControlTracker) => ({
    isBusy: vi.spyOn(tracker, "isBusy"),
    errorOf: vi.spyOn(tracker, "errorOf"),
    submit: vi.spyOn(tracker, "submit"),
});
