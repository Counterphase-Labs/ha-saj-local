import { css } from "lit";

import type { Tone } from "../system/operating";

export const TONE_COLOURS: Record<Tone, string> = {
    primary: "var(--primary-color, #03a9f4)",
    secondary: "var(--secondary-text-color, #727272)",
    disabled: "var(--disabled-text-color, #bdbdbd)",
    warning: "var(--warning-color, #ff9800)",
    error: "var(--error-color, #db4437)",
    success: "var(--success-color, #43a047)",
};

export const toneColour = (tone: Tone | undefined): string =>
    tone === undefined ? "inherit" : TONE_COLOURS[tone];

export const baseStyles = css`
    :host {
        display: block;
        color: var(--primary-text-color, #212121);
        font-family: var(--primary-font-family, sans-serif);
    }
    button {
        font: inherit;
        color: inherit;
    }
    button:focus-visible,
    input:focus-visible,
    select:focus-visible {
        outline: 2px solid var(--primary-color, #03a9f4);
        outline-offset: 2px;
    }
    @media (prefers-reduced-motion: reduce) {
        * {
            animation: none !important;
            transition: none !important;
        }
    }
`;
