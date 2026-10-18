import { afterEach, describe, expect, it, vi } from "vitest";
import { stylesModule } from "../fakes/modules";

import {
    clampPercent,
    filledLength,
    GAUGE_CENTRE,
    GAUGE_RADIUS,
    markerSegment,
} from "../../src/ui/ring-gauge";
import "../../src/ui/ring-gauge";
import { allInShadow, inShadow, mount } from "./mount";

vi.mock("../../src/ui/styles", () => stylesModule());

type Gauge = HTMLElementTagNameMap["saj-ring-gauge"];

afterEach(() => {
    document.body.replaceChildren();
});

describe("gauge geometry", () => {
    it.each([
        { percent: -5, expected: 0 },
        { percent: 40, expected: 40 },
        { percent: 130, expected: 100 },
    ])("clamps $percent to $expected", ({ percent, expected }) => {
        expect(clampPercent(percent)).toBe(expected);
    });

    it("fills the whole circumference at 100 percent and nothing at 0", () => {
        expect(filledLength(0)).toBe(0);
        expect(filledLength(100)).toBeCloseTo(2 * Math.PI * GAUGE_RADIUS);
        expect(filledLength(50)).toBeCloseTo(filledLength(100) / 2);
    });

    it("puts the 0 percent marker at the top and the 50 percent marker at the bottom", () => {
        const top = markerSegment(0);
        const bottom = markerSegment(50);

        expect(top.x1).toBeCloseTo(GAUGE_CENTRE);
        expect(top.y1).toBeLessThan(GAUGE_CENTRE);
        expect(bottom.x1).toBeCloseTo(GAUGE_CENTRE);
        expect(bottom.y1).toBeGreaterThan(GAUGE_CENTRE);
    });

    it("crosses the ring: the marker starts inside and ends outside it", () => {
        const segment = markerSegment(25);
        const distance = (x: number, y: number): number =>
            Math.hypot(x - GAUGE_CENTRE, y - GAUGE_CENTRE);

        expect(distance(segment.x1, segment.y1)).toBeLessThan(GAUGE_RADIUS);
        expect(distance(segment.x2, segment.y2)).toBeGreaterThan(GAUGE_RADIUS);
    });
});

describe("saj-ring-gauge", () => {
    it("shows the value and caption and names itself for assistive technology", async () => {
        const gauge = await mount<Gauge>("saj-ring-gauge", {
            percent: 60,
            displayValue: "60 %",
            caption: "Charge",
            label: "Battery",
        });

        expect(inShadow(gauge, ".centre-value").textContent).toBe("60 %");
        expect(inShadow(gauge, ".centre-caption").textContent).toBe("Charge");
        expect(inShadow(gauge, "svg").getAttribute("aria-label")).toBe(
            "Battery 60 %",
        );
    });

    it("draws one titled marker for each marker given", async () => {
        const gauge = await mount<Gauge>("saj-ring-gauge", {
            markers: [
                { percent: 20, label: "Reserve" },
                { percent: 90, label: "Limit" },
            ],
        });

        expect(
            allInShadow(gauge, ".marker title").map(
                (title) => title.textContent,
            ),
        ).toEqual(["Reserve", "Limit"]);
    });

    it("draws the track and the filled ring and no markers by default", async () => {
        const gauge = await mount<Gauge>("saj-ring-gauge");

        expect(allInShadow(gauge, "circle")).toHaveLength(2);
        expect(allInShadow(gauge, ".marker")).toEqual([]);
    });
});
