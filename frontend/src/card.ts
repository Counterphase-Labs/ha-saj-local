import { html, LitElement, type TemplateResult } from "lit";

export interface SajModbusCardConfig {
    type: string;
    title: string;
}

export class SajModbusCard extends LitElement {
    static override properties = {
        title: { state: true },
    };

    declare title: string;

    constructor() {
        super();
        this.title = "";
    }

    setConfig(config: Partial<SajModbusCardConfig>): void {
        if (config.title === undefined || config.title === "") {
            throw new Error("The card configuration requires a title");
        }
        this.title = config.title;
    }

    protected override render(): TemplateResult {
        return html`<ha-card><h2>${this.title}</h2></ha-card>`;
    }
}

customElements.define("saj-modbus-card", SajModbusCard);

declare global {
    interface HTMLElementTagNameMap {
        "saj-modbus-card": SajModbusCard;
    }
}
