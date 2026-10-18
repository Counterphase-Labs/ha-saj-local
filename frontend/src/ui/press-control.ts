import { html, type TemplateResult } from "lit";

import { ControlElement } from "./control-element";

export class SajPressControl extends ControlElement<null> {
    protected override render(): TemplateResult {
        return this.renderFrame(
            html`<button
                type="button"
                aria-label=${this.label}
                ?disabled=${this.inactive}
                @click=${() => {
                    this.commit(null);
                }}
            >
                ${this.text("press")}
            </button>`,
        );
    }
}

customElements.define("saj-press-control", SajPressControl);

declare global {
    interface HTMLElementTagNameMap {
        "saj-press-control": SajPressControl;
    }
}
