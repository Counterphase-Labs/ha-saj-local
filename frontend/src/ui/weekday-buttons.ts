import { css, html, type TemplateResult } from "lit";

import {
    DelayedCommit,
    WEEKDAY_COMMIT_DELAY_MILLISECONDS,
} from "../system/control";
import {
    toggleDay,
    weekdayName,
    weekOrder,
    daysOfNumber,
} from "../system/weekdays";
import { ControlElement, controlStyles } from "./control-element";

export class SajWeekdayButtons extends ControlElement<number> {
    static override properties = {
        ...ControlElement.properties,
        value: { type: Number },
        draft: { state: true },
    };

    static override styles = [
        ...controlStyles,
        css`
            :host {
                display: block;
            }
            .input {
                flex: 1;
                min-width: 0;
            }
            .days {
                display: flex;
                flex: 1;
                min-width: 0;
                container-type: inline-size;
                gap: var(--feature-button-spacing, 4px);
            }
            button {
                flex: 1 1 0;
                min-width: 0;
                height: var(--feature-height, 36px);
                padding: 0 2px;
                overflow: hidden;
                background: var(--secondary-background-color, #e5e5e5);
                border: none;
                border-radius: var(--feature-border-radius, 8px);
                cursor: pointer;
            }
            button[aria-pressed="true"] {
                background: var(--primary-color, #03a9f4);
                color: var(--text-primary-color, #fff);
            }
            .narrow {
                display: none;
            }
            @container (max-width: 280px) {
                .short {
                    display: none;
                }
                .narrow {
                    display: inline;
                }
            }
            button:disabled {
                opacity: 0.5;
                cursor: default;
            }
        `,
    ];

    declare value: number;
    declare draft: number | null;

    private readonly delayedCommit = new DelayedCommit<number>({
        delayMilliseconds: WEEKDAY_COMMIT_DELAY_MILLISECONDS,
        commit: (value) => {
            this.draft = null;
            this.commit(value);
        },
    });

    constructor() {
        super();
        this.value = 0;
        this.draft = null;
    }

    override disconnectedCallback(): void {
        super.disconnectedCallback();
        this.delayedCommit.cancel();
    }

    protected override render(): TemplateResult {
        const { hass } = this;
        if (hass === undefined) {
            return html``;
        }
        const { language } = hass;
        const selected = new Set(daysOfNumber(this.draft ?? this.value));
        const order = weekOrder(hass);
        return this.renderFrame(
            html`<div
                class="days"
                role="group"
                aria-label=${this.label}
                @focusout=${this.onFocusOut}
            >
                ${order.map(
                    (day) =>
                        html`<button
                            type="button"
                            aria-pressed=${String(selected.has(day))}
                            aria-label=${weekdayName({
                                day,
                                language,
                                width: "long",
                            })}
                            ?disabled=${this.inactive}
                            @click=${() => {
                                this.press(day);
                            }}
                        >
                            <span class="short"
                                >${weekdayName({
                                    day,
                                    language,
                                    width: "short",
                                })}</span
                            ><span class="narrow"
                                >${weekdayName({
                                    day,
                                    language,
                                    width: "narrow",
                                })}</span
                            >
                        </button>`,
                )}
            </div>`,
        );
    }

    private press(day: number): void {
        this.draft = toggleDay({ value: this.draft ?? this.value, day });
        this.delayedCommit.push(this.draft);
    }

    private readonly onFocusOut = (event: FocusEvent): void => {
        const group = event.currentTarget as HTMLElement;
        if (!group.contains(event.relatedTarget as Node | null)) {
            this.delayedCommit.flush();
        }
    };
}

customElements.define("saj-weekday-buttons", SajWeekdayButtons);

declare global {
    interface HTMLElementTagNameMap {
        "saj-weekday-buttons": SajWeekdayButtons;
    }
}
