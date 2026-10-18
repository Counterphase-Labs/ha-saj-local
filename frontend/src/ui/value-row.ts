import { css, html, LitElement, nothing, type TemplateResult } from "lit";
import { styleMap } from "lit/directives/style-map.js";

import { fireMoreInfo } from "../actions";
import type { Tone } from "../system/operating";
import "./icon";
import type { IconName } from "./icons";
import { baseStyles, toneColour } from "./styles";

export class SajValueRow extends LitElement {
    static override properties = {
        label: { type: String },
        value: { type: String },
        icon: { type: String },
        entityId: { type: String },
        tone: { type: String },
        dimmed: { type: Boolean },
    };

    static override styles = [
        baseStyles,
        css`
            .row {
                display: flex;
                align-items: center;
                gap: 8px;
                width: 100%;
                padding: 4px 0;
                background: none;
                border: none;
                text-align: start;
            }
            button.row {
                cursor: pointer;
            }
            .label {
                flex: 1;
                color: var(--secondary-text-color, #727272);
            }
            .dimmed .value {
                opacity: 0.5;
            }
        `,
    ];

    declare label: string;
    declare value: string;
    declare icon: IconName | undefined;
    declare entityId: string | undefined;
    declare tone: Tone | undefined;
    declare dimmed: boolean;

    constructor() {
        super();
        this.label = "";
        this.value = "";
        this.dimmed = false;
    }

    protected override render(): TemplateResult {
        const content = html`${
                this.icon === undefined
                    ? nothing
                    : html`<saj-icon .name=${this.icon}></saj-icon>`
            }
            <span class="label">${this.label}</span>
            <span
                class="value"
                style=${styleMap({ color: toneColour(this.tone) })}
                >${this.value}</span
            >`;
        const classes = this.dimmed ? "row dimmed" : "row";
        const { entityId } = this;
        return entityId === undefined
            ? html`<div class=${classes}>${content}</div>`
            : html`<button
                  type="button"
                  class=${classes}
                  @click=${() => {
                      fireMoreInfo({ host: this, entityId });
                  }}
              >
                  ${content}
              </button>`;
    }
}

customElements.define("saj-value-row", SajValueRow);

declare global {
    interface HTMLElementTagNameMap {
        "saj-value-row": SajValueRow;
    }
}
