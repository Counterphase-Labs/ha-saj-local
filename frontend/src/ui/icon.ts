import { css, LitElement, svg, type TemplateResult } from "lit";

import { ICONS, type IconName } from "./icons";

export class SajIcon extends LitElement {
    static override properties = {
        name: { type: String },
    };

    static override styles = css`
        :host {
            display: inline-flex;
            width: var(--saj-icon-size, 24px);
            height: var(--saj-icon-size, 24px);
            fill: currentcolor;
        }
        svg {
            width: 100%;
            height: 100%;
        }
    `;

    declare name: IconName;

    constructor() {
        super();
        this.name = "info";
    }

    protected override render(): TemplateResult {
        return svg`<svg viewBox="0 0 24 24" aria-hidden="true"><path d=${ICONS[this.name]}></path></svg>`;
    }
}

customElements.define("saj-icon", SajIcon);

declare global {
    interface HTMLElementTagNameMap {
        "saj-icon": SajIcon;
    }
}
