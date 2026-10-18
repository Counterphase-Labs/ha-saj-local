import { afterEach, describe, expect, it } from "vitest";

import "../../src/ui/icon";
import { ICONS, type IconName } from "../../src/ui/icons";
import { inShadow, mount } from "./mount";

afterEach(() => {
    document.body.replaceChildren();
});

describe("saj-icon", () => {
    it.each(["solar", "battery", "busy"] satisfies IconName[])(
        "draws the path of the %s icon as inline svg",
        async (name) => {
            const icon = await mount<HTMLElementTagNameMap["saj-icon"]>(
                "saj-icon",
                { name },
            );

            expect(inShadow(icon, "path").getAttribute("d")).toBe(ICONS[name]);
            expect(inShadow(icon, "svg").getAttribute("aria-hidden")).toBe(
                "true",
            );
        },
    );

    it("draws the information icon until it is given another", async () => {
        const icon = await mount<HTMLElementTagNameMap["saj-icon"]>("saj-icon");

        expect(inShadow(icon, "path").getAttribute("d")).toBe(ICONS.info);
    });
});
