import { html, LitElement, type TemplateResult } from "lit";

export interface SajLocalCardConfig {
    type: string;
    title: string;
}

export class SajLocalCard extends LitElement {
    static override properties = {
        title: { state: true },
    };

    declare title: string;

    constructor() {
        super();
        this.title = "";
    }

    setConfig(config: Partial<SajLocalCardConfig>): void {
        if (config.title === undefined || config.title === "") {
            throw new Error("The card configuration requires a title");
        }
        this.title = config.title;
    }

    protected override render(): TemplateResult {
        return html`<ha-card><h2>${this.title}</h2></ha-card>`;
    }
}

customElements.define("saj-local-card", SajLocalCard);

declare global {
    interface HTMLElementTagNameMap {
        "saj-local-card": SajLocalCard;
    }
}
