import { html, type TemplateResult } from "lit";

import { ControlElement } from "./control-element";

const CLOCK_TEXT_LENGTH = "HH:MM".length;

export class SajTimeControl extends ControlElement<string> {
    static override properties = {
        ...ControlElement.properties,
        value: { type: String },
    };

    declare value: string;

    constructor() {
        super();
        this.value = "";
    }

    private get shownText(): string {
        return this.value.slice(0, CLOCK_TEXT_LENGTH);
    }

    protected override render(): TemplateResult {
        return this.renderFrame(
            html`<input
                type="time"
                aria-label=${this.label}
                .value=${this.shownText}
                ?disabled=${this.inactive}
                @change=${(event: Event) => {
                    const input = event.target as HTMLInputElement;
                    const chosen = input.value;
                    input.value = this.shownText;
                    if (chosen !== "") {
                        this.commit(chosen);
                    }
                }}
            />`,
        );
    }
}

customElements.define("saj-time-control", SajTimeControl);

declare global {
    interface HTMLElementTagNameMap {
        "saj-time-control": SajTimeControl;
    }
}
