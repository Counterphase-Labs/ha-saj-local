import { html, type TemplateResult } from "lit";

import { ControlElement } from "./control-element";

export interface SelectOption {
    value: string;
    label: string;
}

export class SajSelectControl extends ControlElement<string> {
    static override properties = {
        ...ControlElement.properties,
        value: { type: String },
        options: { attribute: false },
    };

    declare value: string;
    declare options: readonly SelectOption[];

    constructor() {
        super();
        this.value = "";
        this.options = [];
    }

    protected override render(): TemplateResult {
        return this.renderFrame(
            html`<select
                aria-label=${this.label}
                ?disabled=${this.inactive}
                @change=${(event: Event) => {
                    const select = event.target as HTMLSelectElement;
                    const chosen = select.value;
                    select.value = this.value;
                    this.commit(chosen);
                }}
            >
                ${this.options.map(
                    (option) =>
                        html`<option
                            value=${option.value}
                            .selected=${option.value === this.value}
                        >
                            ${option.label}
                        </option>`,
                )}
            </select>`,
        );
    }
}

customElements.define("saj-select-control", SajSelectControl);

declare global {
    interface HTMLElementTagNameMap {
        "saj-select-control": SajSelectControl;
    }
}
