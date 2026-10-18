import { afterEach, describe, expect, it, vi, type Mock } from "vitest";
import { controlElementModule, weekdaysModule } from "../fakes/modules";

import "../../src/ui/weekday-buttons";
import { WEEKDAY_COMMIT_DELAY_MILLISECONDS } from "../../src/system/control";
import { weekOrder } from "../../src/system/weekdays";
import { createFakeHass } from "../fakes/hass";
import { commitsOf } from "../fakes/modules";
import { allShadowButtons, inShadow, mount } from "./mount";

const delayed = vi.hoisted(() => ({
    instances: [] as {
        options: { delayMilliseconds: number; commit: (value: number) => void };
        push: Mock<(value: number) => void>;
        flush: ReturnType<typeof vi.fn>;
        cancel: ReturnType<typeof vi.fn>;
    }[],
}));

vi.mock("../../src/system/control", () => ({
    WEEKDAY_COMMIT_DELAY_MILLISECONDS: 1500,
    DelayedCommit: class {
        readonly push = vi.fn<(value: number) => void>();
        readonly flush = vi.fn();
        readonly cancel = vi.fn();
        constructor(
            readonly options: {
                delayMilliseconds: number;
                commit: (value: number) => void;
            },
        ) {
            delayed.instances.push(this);
        }
    },
}));
vi.mock("../../src/system/weekdays", () => weekdaysModule());
vi.mock("../../src/ui/control-element", () => controlElementModule());

type WeekdayButtons = HTMLElementTagNameMap["saj-weekday-buttons"];

const MONDAY = 0;
const WEDNESDAY = 2;
const FRIDAY = 4;

const buttonsOf = (control: WeekdayButtons): HTMLButtonElement[] =>
    allShadowButtons(control);

const pressedOf = (control: WeekdayButtons): string[] =>
    buttonsOf(control).map(
        (button) => button.getAttribute("aria-pressed") ?? "",
    );

const delayedCommitOf = () => {
    const [instance] = delayed.instances.slice(-1);
    if (instance === undefined) {
        throw new Error("No delayed commit");
    }
    return instance;
};

const leaveButtons = (
    control: WeekdayButtons,
    relatedTarget: Element | null,
): void => {
    inShadow(control, ".days").dispatchEvent(
        new FocusEvent("focusout", { bubbles: true, relatedTarget }),
    );
};

afterEach(() => {
    document.body.replaceChildren();
    delayed.instances.length = 0;
});

describe("saj-weekday-buttons", () => {
    it("draws nothing without hass", async () => {
        const control = await mount<WeekdayButtons>("saj-weekday-buttons");

        expect(buttonsOf(control)).toEqual([]);
    });

    it("draws seven toggle buttons named in the user's language, pressed for the slot's days", async () => {
        const control = await mount<WeekdayButtons>("saj-weekday-buttons", {
            hass: createFakeHass({ language: "de" }),
            value: 2 ** MONDAY + 2 ** FRIDAY,
        });

        const buttons = buttonsOf(control);

        expect(buttons).toHaveLength(7);
        expect(buttons[MONDAY]?.getAttribute("aria-label")).toBe("long:0:de");
        expect(buttons[MONDAY]?.querySelector(".short")?.textContent).toBe(
            "short:0:de",
        );
        expect(buttons[MONDAY]?.querySelector(".narrow")?.textContent).toBe(
            "narrow:0:de",
        );
        expect(pressedOf(control)).toEqual([
            "true",
            "false",
            "false",
            "false",
            "true",
            "false",
            "false",
        ]);
    });

    it("draws the days in the order of the user's week", async () => {
        const hass = createFakeHass();
        vi.mocked(weekOrder).mockReturnValueOnce([6, 0, 1, 2, 3, 4, 5]);

        const control = await mount<WeekdayButtons>("saj-weekday-buttons", {
            hass,
        });

        expect(weekOrder).toHaveBeenCalledWith(hass);
        expect(buttonsOf(control)[0]?.getAttribute("aria-label")).toBe(
            "long:6:en",
        );
    });

    it("waits for the commit delay before announcing, and shows the pressed days meanwhile", async () => {
        const control = await mount<WeekdayButtons>("saj-weekday-buttons", {
            hass: createFakeHass(),
        });

        for (const day of [MONDAY, WEDNESDAY, FRIDAY]) {
            buttonsOf(control)[day]?.click();
            await control.updateComplete;
        }

        expect(delayedCommitOf().options.delayMilliseconds).toBe(
            WEEKDAY_COMMIT_DELAY_MILLISECONDS,
        );
        expect(
            delayedCommitOf().push.mock.calls.map(([value]) => value),
        ).toEqual([1, 5, 21]);
        expect(commitsOf(control)).toEqual([]);
        expect(pressedOf(control)[WEDNESDAY]).toBe("true");
    });

    it("unpresses a day that the slot has", async () => {
        const control = await mount<WeekdayButtons>("saj-weekday-buttons", {
            hass: createFakeHass(),
            value: 2 ** MONDAY + 2 ** WEDNESDAY,
        });

        buttonsOf(control)[WEDNESDAY]?.click();

        expect(delayedCommitOf().push).toHaveBeenCalledWith(1);
    });

    it("announces the decision once the delay passes and shows the entity's days again", async () => {
        const control = await mount<WeekdayButtons>("saj-weekday-buttons", {
            hass: createFakeHass(),
        });

        buttonsOf(control)[MONDAY]?.click();
        await control.updateComplete;
        delayedCommitOf().options.commit(1);
        await control.updateComplete;

        expect(commitsOf(control)).toEqual([1]);
        expect(pressedOf(control)[MONDAY]).toBe("false");
    });

    it("commits at once when focus leaves the buttons", async () => {
        const control = await mount<WeekdayButtons>("saj-weekday-buttons", {
            hass: createFakeHass(),
        });

        leaveButtons(control, null);

        expect(delayedCommitOf().flush).toHaveBeenCalledTimes(1);
    });

    it("keeps waiting when focus moves between the buttons", async () => {
        const control = await mount<WeekdayButtons>("saj-weekday-buttons", {
            hass: createFakeHass(),
        });

        leaveButtons(control, buttonsOf(control)[WEDNESDAY] ?? null);

        expect(delayedCommitOf().flush).not.toHaveBeenCalled();
    });

    it("drops a pending decision when removed", async () => {
        const control = await mount<WeekdayButtons>("saj-weekday-buttons", {
            hass: createFakeHass(),
        });

        control.remove();

        expect(delayedCommitOf().cancel).toHaveBeenCalledTimes(1);
    });

    it("disables every button while busy", async () => {
        const control = await mount<WeekdayButtons>("saj-weekday-buttons", {
            hass: createFakeHass(),
            busy: true,
        });

        expect(buttonsOf(control).every((button) => button.disabled)).toBe(
            true,
        );
    });
});
