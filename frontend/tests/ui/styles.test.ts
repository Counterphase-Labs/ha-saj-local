import { describe, expect, it } from "vitest";

import type { Tone } from "../../src/system/operating";
import { TONE_COLOURS, toneColour } from "../../src/ui/styles";

describe("toneColour", () => {
    it.each(Object.keys(TONE_COLOURS) as Tone[])(
        "uses a theme variable with a fallback for %s",
        (tone) => {
            expect(toneColour(tone)).toMatch(/^var\(--[a-z-]+, .+\)$/);
        },
    );

    it("inherits the colour without a tone", () => {
        expect(toneColour(undefined)).toBe("inherit");
    });
});
