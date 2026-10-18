import { css, html, LitElement, type TemplateResult } from "lit";

import type { Tone } from "../system/operating";
import "./icon";
import type { IconName } from "./icons";
import { baseStyles, toneColour } from "./styles";

export type NoticeTone = Extract<Tone, "primary" | "warning" | "error">;

const NOTICE_ICONS: Record<NoticeTone, IconName> = {
    primary: "info",
    warning: "info",
    error: "fault",
};

export class SajNotice extends LitElement {
    static override properties = {
        message: { type: String },
        tone: { type: String },
    };

    static override styles = [
        baseStyles,
        css`
            .notice {
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 8px 0;
            }
            .message {
                flex: 1;
            }
        `,
    ];

    declare message: string;
    declare tone: NoticeTone;

    constructor() {
        super();
        this.message = "";
        this.tone = "primary";
    }

    protected override render(): TemplateResult {
        return html`<div
            class="notice"
            role=${this.tone === "error" ? "alert" : "status"}
        >
            <saj-icon
                .name=${NOTICE_ICONS[this.tone]}
                style="color: ${toneColour(this.tone)}"
            ></saj-icon>
            <span class="message">${this.message}</span>
            <slot></slot>
        </div>`;
    }
}

customElements.define("saj-notice", SajNotice);

declare global {
    interface HTMLElementTagNameMap {
        "saj-notice": SajNotice;
    }
}
