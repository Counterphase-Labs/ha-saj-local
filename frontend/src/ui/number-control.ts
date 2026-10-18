import { html, nothing, type TemplateResult } from "lit";
import { ifDefined } from "lit/directives/if-defined.js";

import { ControlElement } from "./control-element";

export const MAX_AUTO_SLIDER_STEPS = 256;

export type NumberMode = "auto" | "slider" | "box";
export type NumberStyle = "slider" | "box";

export interface NumberRange {
    min: number | undefined;
    max: number | undefined;
    step: number | undefined;
}

export const numberStyle = ({
    mode,
    range,
}: {
    mode: NumberMode;
    range: NumberRange;
}): NumberStyle => {
    if (mode !== "auto") {
        return mode;
    }
    const { min, max, step } = range;
    if (min === undefined || max === undefined || step === undefined) {
        return "box";
    }
    return (max - min) / step <= MAX_AUTO_SLIDER_STEPS ? "slider" : "box";
};

export class SajNumberControl extends ControlElement<number> {
    static override properties = {
        ...ControlElement.properties,
        value: { type: Number },
        min: { type: Number },
        max: { type: Number },
        step: { type: Number },
        unit: { type: String },
        displayValue: { type: String },
        mode: { type: String },
        draft: { state: true },
    };

    declare value: number;
    declare min: number | undefined;
    declare max: number | undefined;
    declare step: number | undefined;
    declare unit: string;
    declare displayValue: string;
    declare mode: NumberMode;
    declare draft: number | null;

    constructor() {
        super();
        this.value = 0;
        this.unit = "";
        this.displayValue = "";
        this.mode = "auto";
        this.draft = null;
    }

    protected override render(): TemplateResult {
        const slider =
            numberStyle({
                mode: this.mode,
                range: { min: this.min, max: this.max, step: this.step },
            }) === "slider";
        return this.renderFrame(
            html`<input
                    type=${slider ? "range" : "number"}
                    min=${ifDefined(this.min)}
                    max=${ifDefined(this.max)}
                    step=${ifDefined(this.step)}
                    aria-label=${this.label}
                    .value=${slider ? this.draftOrValue : String(this.value)}
                    ?disabled=${this.inactive}
                    @input=${this.onInput}
                    @pointerup=${slider ? this.onFinish : nothing}
                    @keydown=${this.onKeyDown}
                    @blur=${this.onFinish}
                />${
                    slider
                        ? html`<span class="value"
                              >${
                                  this.draft === null
                                      ? this.displayValue
                                      : `${String(this.draft)} ${this.unit}`
                              }</span
                          >`
                        : html`<span class="unit">${this.unit}</span>`
                }`,
        );
    }

    private get draftOrValue(): string {
        return String(this.draft ?? this.value);
    }

    private readonly onInput = (event: Event): void => {
        const parsed = Number.parseFloat(
            (event.target as HTMLInputElement).value,
        );
        this.draft = Number.isFinite(parsed) ? parsed : null;
    };

    private readonly onKeyDown = (event: KeyboardEvent): void => {
        if (event.key === "Enter") {
            this.onFinish(event);
        }
    };

    private readonly onFinish = (event: Event): void => {
        const input = event.target as HTMLInputElement;
        const decided = this.draft;
        this.draft = null;
        input.value = String(this.value);
        if (decided !== null) {
            this.commit(decided);
        }
    };
}

customElements.define("saj-number-control", SajNumberControl);

declare global {
    interface HTMLElementTagNameMap {
        "saj-number-control": SajNumberControl;
    }
}
