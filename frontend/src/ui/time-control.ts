import { html, type PropertyValues, type TemplateResult } from "lit";

import { ControlElement } from "./control-element";

const CLOCK_TEXT_LENGTH = "HH:MM".length;

export class SajTimeControl extends ControlElement<string> {
    static override properties = {
        ...ControlElement.properties,
        value: { type: String },
        draft: { state: true },
    };

    declare value: string;
    declare draft: string | null;

    constructor() {
        super();
        this.value = "";
        this.draft = null;
    }

    override disconnectedCallback(): void {
        super.disconnectedCallback();
        this.finish();
    }

    private get shownText(): string {
        return this.value.slice(0, CLOCK_TEXT_LENGTH);
    }

    protected override willUpdate(changed: PropertyValues): void {
        if (this.disabled && this.draft !== null) {
            this.draft = null;
        }
        super.willUpdate(changed);
    }

    protected override render(): TemplateResult {
        return this.renderFrame(
            html`<input
                type="time"
                aria-label=${this.label}
                .value=${this.draft ?? this.shownText}
                ?disabled=${this.inactive}
                @change=${this.onChange}
                @keydown=${this.onKeyDown}
                @blur=${this.onBlur}
            />`,
        );
    }

    private readonly onChange = (event: Event): void => {
        this.draft = (event.target as HTMLInputElement).value;
    };

    private readonly onKeyDown = (event: KeyboardEvent): void => {
        if (event.key === "Enter") {
            this.finish();
        }
    };

    private readonly onBlur = (): void => {
        this.finish();
    };

    private finish(): void {
        const decided = this.draft;
        this.draft = null;
        if (decided !== null && decided !== "" && decided !== this.shownText) {
            this.commit(decided);
        }
    }
}

customElements.define("saj-time-control", SajTimeControl);

declare global {
    interface HTMLElementTagNameMap {
        "saj-time-control": SajTimeControl;
    }
}
