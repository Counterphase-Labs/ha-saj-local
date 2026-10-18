import { css, html, nothing, type TemplateResult } from "lit";

import "./icon";
import { LocalizedElement } from "./localized-element";
import { baseStyles } from "./styles";

export const COMMIT_EVENT = "saj-commit";

export const controlStyles = [
    baseStyles,
    css`
        .control {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 4px 0;
        }
        .label {
            flex: 1;
            color: var(--secondary-text-color, #727272);
        }
        .input {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .busy {
            --saj-icon-size: 18px;
            animation: spin 1s linear infinite;
        }
        .error {
            color: var(--error-color, #db4437);
            font-size: 0.85rem;
        }
        @keyframes spin {
            to {
                transform: rotate(360deg);
            }
        }
    `,
];

export abstract class ControlElement<Value> extends LocalizedElement {
    static override properties = {
        ...LocalizedElement.properties,
        label: { type: String },
        labelHidden: { type: Boolean },
        disabled: { type: Boolean },
        busy: { type: Boolean },
        error: { type: String },
    };

    static override styles = controlStyles;

    declare label: string;
    declare labelHidden: boolean;
    declare disabled: boolean;
    declare busy: boolean;
    declare error: string;

    constructor() {
        super();
        this.label = "";
        this.labelHidden = false;
        this.disabled = false;
        this.busy = false;
        this.error = "";
    }

    protected get inactive(): boolean {
        return this.disabled || this.busy;
    }

    protected commit(value: Value): void {
        this.dispatchEvent(
            new CustomEvent<Value>(COMMIT_EVENT, {
                detail: value,
                bubbles: true,
                composed: true,
            }),
        );
    }

    protected renderFrame(input: TemplateResult): TemplateResult {
        return html`<div class="control">
                ${
                    this.label === "" || this.labelHidden
                        ? nothing
                        : html`<span class="label">${this.label}</span>`
                }
                <span class="input"
                    >${input}${
                        this.busy
                            ? html`<saj-icon
                                  class="busy"
                                  name="busy"
                                  role="status"
                                  aria-label=${this.text("busy")}
                              ></saj-icon>`
                            : nothing
                    }</span
                >
            </div>
            ${
                this.error === ""
                    ? nothing
                    : html`<div class="error" role="alert">${this.error}</div>`
            }`;
    }
}
