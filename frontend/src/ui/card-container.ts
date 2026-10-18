import { css, html, LitElement, nothing, type TemplateResult } from "lit";

import { baseStyles } from "./styles";

export class SajCard extends LitElement {
    static override properties = {
        heading: { type: String },
    };

    static override styles = [
        baseStyles,
        css`
            .card {
                box-sizing: border-box;
                height: 100%;
                padding: 16px;
                background: var(
                    --ha-card-background,
                    var(--card-background-color, #fff)
                );
                border-radius: var(--ha-card-border-radius, 12px);
                border-width: var(--ha-card-border-width, 1px);
                border-style: solid;
                border-color: var(
                    --ha-card-border-color,
                    var(--divider-color, #e0e0e0)
                );
                box-shadow: var(--ha-card-box-shadow, none);
            }
            h2 {
                margin: 0 0 12px;
                font-size: 1.1rem;
                font-weight: 500;
            }
        `,
    ];

    declare heading: string;

    constructor() {
        super();
        this.heading = "";
    }

    protected override render(): TemplateResult {
        return html`<div class="card">
            ${this.heading === "" ? nothing : html`<h2>${this.heading}</h2>`}
            <slot></slot>
        </div>`;
    }
}

customElements.define("saj-card", SajCard);

declare global {
    interface HTMLElementTagNameMap {
        "saj-card": SajCard;
    }
}
