import { LitElement } from "lit";

import type { Hass } from "../hass";
import {
    FALLBACK_LANGUAGE,
    localizerFor,
    type Localize,
} from "../i18n/localize";

export class LocalizedElement extends LitElement {
    static override properties = {
        hass: { attribute: false },
    };

    declare hass: Hass | undefined;

    protected get text(): Localize {
        return localizerFor(this.hass?.language ?? FALLBACK_LANGUAGE);
    }
}
