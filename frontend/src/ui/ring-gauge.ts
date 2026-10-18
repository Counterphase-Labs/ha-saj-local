import { css, html, LitElement, svg, type TemplateResult } from "lit";

import type { Tone } from "../system/operating";
import { baseStyles, toneColour } from "./styles";

export const GAUGE_RADIUS = 42;
export const GAUGE_CENTRE = 50;
export const GAUGE_STROKE = 8;
const MARKER_HALF_LENGTH = 7;
const FULL_TURN_DEGREES = 360;
const START_ANGLE_DEGREES = -90;
const PERCENT_TOTAL = 100;

export interface GaugeMarker {
    percent: number;
    label: string;
}

export interface MarkerSegment {
    x1: number;
    y1: number;
    x2: number;
    y2: number;
}

export const clampPercent = (percent: number): number =>
    Math.min(Math.max(percent, 0), PERCENT_TOTAL);

export const markerSegment = (percent: number): MarkerSegment => {
    const angle =
        ((START_ANGLE_DEGREES +
            (clampPercent(percent) / PERCENT_TOTAL) * FULL_TURN_DEGREES) *
            Math.PI) /
        (FULL_TURN_DEGREES / 2);
    const point = (distance: number): { x: number; y: number } => ({
        x: GAUGE_CENTRE + distance * Math.cos(angle),
        y: GAUGE_CENTRE + distance * Math.sin(angle),
    });
    const inner = point(GAUGE_RADIUS - MARKER_HALF_LENGTH);
    const outer = point(GAUGE_RADIUS + MARKER_HALF_LENGTH);
    return { x1: inner.x, y1: inner.y, x2: outer.x, y2: outer.y };
};

export const filledLength = (percent: number): number =>
    (2 * Math.PI * GAUGE_RADIUS * clampPercent(percent)) / PERCENT_TOTAL;

export class SajRingGauge extends LitElement {
    static override properties = {
        percent: { type: Number },
        displayValue: { type: String },
        caption: { type: String },
        label: { type: String },
        tone: { type: String },
        markers: { attribute: false },
    };

    static override styles = [
        baseStyles,
        css`
            :host {
                display: inline-block;
                width: 100%;
                max-width: 220px;
            }
            .track {
                stroke: var(--divider-color, #e0e0e0);
            }
            .centre-value {
                font-size: 18px;
                font-weight: 500;
                fill: var(--primary-text-color, #212121);
            }
            .centre-caption {
                font-size: 8px;
                fill: var(--secondary-text-color, #727272);
            }
            .marker {
                stroke: var(--primary-text-color, #212121);
                stroke-width: 2;
            }
        `,
    ];

    declare percent: number;
    declare displayValue: string;
    declare caption: string;
    declare label: string;
    declare tone: Tone;
    declare markers: readonly GaugeMarker[];

    constructor() {
        super();
        this.percent = 0;
        this.displayValue = "";
        this.caption = "";
        this.label = "";
        this.tone = "primary";
        this.markers = [];
    }

    protected override render(): TemplateResult {
        const circumference = 2 * Math.PI * GAUGE_RADIUS;
        return html`<svg
            viewBox="0 0 100 100"
            role="img"
            aria-label=${`${this.label} ${this.displayValue}`.trim()}
        >
            ${svg`<circle class="track" cx=${GAUGE_CENTRE} cy=${GAUGE_CENTRE} r=${GAUGE_RADIUS} fill="none" stroke-width=${GAUGE_STROKE}></circle>
            <circle
                cx=${GAUGE_CENTRE}
                cy=${GAUGE_CENTRE}
                r=${GAUGE_RADIUS}
                fill="none"
                stroke-width=${GAUGE_STROKE}
                stroke-linecap="round"
                stroke=${toneColour(this.tone)}
                stroke-dasharray="${filledLength(this.percent)} ${circumference}"
                transform="rotate(-90 ${GAUGE_CENTRE} ${GAUGE_CENTRE})"
            ></circle>
            ${this.markers.map((marker) => {
                const segment = markerSegment(marker.percent);
                return svg`<line class="marker" x1=${segment.x1} y1=${segment.y1} x2=${segment.x2} y2=${segment.y2}><title>${marker.label}</title></line>`;
            })}
            <text class="centre-value" x=${GAUGE_CENTRE} y=${GAUGE_CENTRE + 2} text-anchor="middle">${this.displayValue}</text>
            <text class="centre-caption" x=${GAUGE_CENTRE} y=${GAUGE_CENTRE + 14} text-anchor="middle">${this.caption}</text>`}
        </svg>`;
    }
}

customElements.define("saj-ring-gauge", SajRingGauge);

declare global {
    interface HTMLElementTagNameMap {
        "saj-ring-gauge": SajRingGauge;
    }
}
