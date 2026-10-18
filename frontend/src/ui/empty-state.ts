import { css, html, nothing, type TemplateResult } from "lit";

import { deviceDetailPath, fireNavigate, SETTINGS_PATH } from "../actions";
import "./icon";
import { LocalizedElement } from "./localized-element";
import { baseStyles } from "./styles";

export class SajEmptyState extends LocalizedElement {
    static override properties = {
        ...LocalizedElement.properties,
        locked: { type: Boolean },
        kind: { type: String },
        deviceId: { type: String },
        message: { type: String },
    };

    static override styles = [
        baseStyles,
        css`
            .empty {
                display: flex;
                flex-direction: column;
                align-items: flex-start;
                gap: 8px;
                padding: 8px 0;
            }
            .title {
                display: flex;
                align-items: center;
                gap: 8px;
                font-weight: 500;
            }
            .body {
                color: var(--secondary-text-color, #727272);
            }
            button {
                padding: 0;
                background: none;
                border: none;
                color: var(--primary-color, #03a9f4);
                cursor: pointer;
            }
        `,
    ];

    declare locked: boolean;
    declare kind: string;
    declare deviceId: string | undefined;
    declare message: string;

    constructor() {
        super();
        this.locked = false;
        this.kind = "";
        this.message = "";
    }

    protected override render(): TemplateResult {
        const { text } = this;
        return this.locked
            ? html`<div class="empty">
                  <span class="title"
                      ><saj-icon name="lock"></saj-icon>${text(
                          "locked_message",
                      )}</span
                  >
                  ${this.renderLink({
                      label: text("open_settings"),
                      path: SETTINGS_PATH,
                  })}
              </div>`
            : html`<div class="empty">
                  <span class="title">${text("empty_title")}</span>
                  <span class="body"
                      >${
                          this.message === ""
                              ? text("empty_enable", { kind: this.kind })
                              : this.message
                      }</span
                  >
                  ${
                      this.deviceId === undefined
                          ? nothing
                          : this.renderLink({
                                label: text("open_device_page"),
                                path: deviceDetailPath(this.deviceId),
                            })
                  }
              </div>`;
    }

    private renderLink({
        label,
        path,
    }: {
        label: string;
        path: string;
    }): TemplateResult {
        return html`<button
            type="button"
            @click=${() => {
                fireNavigate({ host: this, path });
            }}
        >
            ${label}
        </button>`;
    }
}

customElements.define("saj-empty-state", SajEmptyState);

declare global {
    interface HTMLElementTagNameMap {
        "saj-empty-state": SajEmptyState;
    }
}
