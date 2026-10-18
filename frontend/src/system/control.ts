import type { ReactiveControllerHost } from "lit";

import type { Hass, HassServiceError } from "../hass";
import {
    INTEGRATION_PLATFORM,
    type SystemEntities,
    type SystemEntity,
} from "./entities";

export const CONTROL_ALLOWED_KEY = "control_allowed";
export const WEEKDAY_COMMIT_DELAY_MILLISECONDS = 1500;

export interface ControlLock {
    locked: boolean;
    entity: SystemEntity | null;
}

export const controlLock = (entities: SystemEntities): ControlLock => {
    const entity = entities.get(CONTROL_ALLOWED_KEY) ?? null;
    return { locked: entity?.state.state === "off", entity };
};

export interface ServiceRequest {
    domain: string;
    service: string;
    data?: Record<string, unknown>;
}

export const setNumberRequest = (value: number): ServiceRequest => ({
    domain: "number",
    service: "set_value",
    data: { value },
});

export const selectOptionRequest = (option: string): ServiceRequest => ({
    domain: "select",
    service: "select_option",
    data: { option },
});

export const setTimeRequest = (time: string): ServiceRequest => ({
    domain: "time",
    service: "set_value",
    data: { time },
});

export const setSwitchRequest = (on: boolean): ServiceRequest => ({
    domain: "switch",
    service: on ? "turn_on" : "turn_off",
});

export const pressButtonRequest = (): ServiceRequest => ({
    domain: "button",
    service: "press",
});

const exceptionMessageKey = (translationKey: string): string =>
    `component.${INTEGRATION_PLATFORM}.exceptions.${translationKey}.message`;

export const changeErrorMessage = async ({
    hass,
    error,
}: {
    hass: Hass;
    error: unknown;
}): Promise<string> => {
    const failure = (error ?? {}) as HassServiceError;
    const fallback = failure.message ?? String(error);
    if (
        failure.translation_domain !== INTEGRATION_PLATFORM ||
        failure.translation_key === undefined
    ) {
        return fallback;
    }
    const localize = await hass.loadBackendTranslation(
        "exceptions",
        INTEGRATION_PLATFORM,
    );
    const translated = localize(
        exceptionMessageKey(failure.translation_key),
        failure.translation_placeholders,
    );
    return translated === "" ? fallback : translated;
};

export class ControlTracker {
    private readonly busyEntities = new Set<string>();
    private readonly errors = new Map<string, string>();

    constructor(
        private readonly host: ReactiveControllerHost,
        private readonly hassProvider: () => Hass | undefined,
    ) {}

    isBusy(entityId: string): boolean {
        return this.busyEntities.has(entityId);
    }

    errorOf(entityId: string): string | null {
        return this.errors.get(entityId) ?? null;
    }

    async submit({
        entityId,
        request,
    }: {
        entityId: string;
        request: ServiceRequest;
    }): Promise<void> {
        const hass = this.hassProvider();
        if (hass === undefined || this.busyEntities.has(entityId)) {
            return;
        }
        this.errors.delete(entityId);
        this.busyEntities.add(entityId);
        this.host.requestUpdate();
        try {
            await hass.callService(
                request.domain,
                request.service,
                request.data,
                { entity_id: entityId },
            );
        } catch (error) {
            this.errors.set(
                entityId,
                await changeErrorMessage({ hass, error }),
            );
        } finally {
            this.busyEntities.delete(entityId);
            this.host.requestUpdate();
        }
    }
}

export class DelayedCommit<Value> {
    private pending: { value: Value } | null = null;
    private timer: ReturnType<typeof setTimeout> | null = null;

    constructor(
        private readonly options: {
            delayMilliseconds: number;
            commit: (value: Value) => void;
        },
    ) {}

    push(value: Value): void {
        this.pending = { value };
        this.stopTimer();
        this.timer = setTimeout(() => {
            this.flush();
        }, this.options.delayMilliseconds);
    }

    flush(): void {
        this.stopTimer();
        const { pending } = this;
        this.pending = null;
        if (pending !== null) {
            this.options.commit(pending.value);
        }
    }

    cancel(): void {
        this.stopTimer();
        this.pending = null;
    }

    private stopTimer(): void {
        if (this.timer !== null) {
            clearTimeout(this.timer);
            this.timer = null;
        }
    }
}
