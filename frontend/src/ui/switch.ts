import { css, html, type TemplateResult } from "lit";

import { ControlElement, controlStyles } from "./control-element";

export class SajSwitch extends ControlElement<boolean> {
    static override properties = {
        ...ControlElement.properties,
        checked: { type: Boolean },
    };

    static override styles = [
        ...controlStyles,
        css`
            button {
                position: relative;
                width: 36px;
                height: 20px;
                padding: 0;
                background: var(--disabled-text-color, #bdbdbd);
                border: none;
                border-radius: 10px;
                cursor: pointer;
            }
            button[aria-checked="true"] {
                background: var(--primary-color, #03a9f4);
            }
            button:disabled {
                opacity: 0.5;
                cursor: default;
            }
            .thumb {
                position: absolute;
                top: 2px;
                left: 2px;
                width: 16px;
                height: 16px;
                background: #fff;
                border-radius: 50%;
                transition: transform 0.15s;
            }
            button[aria-checked="true"] .thumb {
                transform: translateX(16px);
            }
        `,
    ];

    declare checked: boolean;

    constructor() {
        super();
        this.checked = false;
    }

    protected override render(): TemplateResult {
        return this.renderFrame(
            html`<button
                type="button"
                role="switch"
                aria-checked=${String(this.checked)}
                aria-label=${this.label}
                ?disabled=${this.inactive}
                @click=${() => {
                    this.commit(!this.checked);
                }}
            >
                <span class="thumb"></span>
            </button>`,
        );
    }
}

customElements.define("saj-switch", SajSwitch);

declare global {
    interface HTMLElementTagNameMap {
        "saj-switch": SajSwitch;
    }
}
