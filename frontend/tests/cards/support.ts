import type { LitElement } from "lit";
import { describe, expect, it, vi } from "vitest";

import { registerCard } from "../../src/registration";
import type { Hass } from "../../src/hass";
import type { CardContext } from "../../src/cards/system-card";
import type { SystemEntity } from "../../src/system/entities";
import { entityMap } from "../fakes/entities";
import { createFakeHass, DEFAULT_DEVICE_ID } from "../fakes/hass";

type Row = HTMLElementTagNameMap["saj-value-row"];

export type CardUnderTest = LitElement & {
    hass: unknown;
    context: unknown;
    config: unknown;
    tracker: CardContext["tracker"];
    setConfig: (config: never) => void;
    getCardSize: () => number;
    shownEntities: (
        entities: ReadonlyMap<string, SystemEntity>,
    ) => SystemEntity[];
};

export interface MountOptions {
    tag: string;
    config?: Record<string, unknown>;
    entities?: readonly SystemEntity[];
    dimmed?: boolean;
    locked?: boolean;
    hass?: ReturnType<typeof createFakeHass>;
}

export const createCard = (tag: string): CardUnderTest =>
    document.createElement(tag) as CardUnderTest;

export const mountCard = async ({
    tag,
    config = {},
    entities = [],
    dimmed = false,
    locked = false,
    hass = createFakeHass(),
}: MountOptions): Promise<CardUnderTest> => {
    const card = createCard(tag);
    card.hass = hass;
    card.setConfig({
        type: tag,
        device: DEFAULT_DEVICE_ID,
        ...config,
    } as never);
    card.context = {
        hass,
        deviceId: DEFAULT_DEVICE_ID,
        entities: entityMap(entities),
        lock: { locked, entity: null },
        tracker: card.tracker,
        dimmed,
    } satisfies CardContext;
    document.body.append(card);
    await card.updateComplete;
    return card;
};

export const rowsOf = (card: LitElement): Row[] => [
    ...(card.shadowRoot?.querySelectorAll("saj-value-row") ?? []),
];

export const rowFor = ({
    card,
    entity,
}: {
    card: LitElement;
    entity: SystemEntity;
}): Row | undefined =>
    rowsOf(card).find((row) => row.entityId === entity.entityId);

export const requiredRowFor = (options: {
    card: LitElement;
    entity: SystemEntity;
}): Row => {
    const row = rowFor(options);
    if (row === undefined) {
        throw new Error(`No row for ${options.entity.key}`);
    }
    return row;
};

export const rowLabelled = ({
    card,
    label,
}: {
    card: LitElement;
    label: string;
}): Row => {
    const found = rowsOf(card).find((row) => row.label === label);
    if (found === undefined) {
        throw new Error(`No row labelled ${label}`);
    }
    return found;
};

export interface ControlStub extends HTMLElement {
    entityKey: string;
    labelHidden: boolean;
}

declare global {
    interface HTMLElementTagNameMap {
        "saj-control-stub": ControlStub;
    }
}

export const elementsIn = (
    card: LitElement,
    selector: string,
): HTMLElement[] => [
    ...(card.shadowRoot?.querySelectorAll<HTMLElement>(selector) ?? []),
];

export const controlStubsIn = (
    card: LitElement,
    selector: string,
): ControlStub[] => [
    ...(card.shadowRoot?.querySelectorAll<ControlStub>(selector) ?? []),
];

type ElementFor<Selector extends string> =
    Selector extends keyof HTMLElementTagNameMap
        ? HTMLElementTagNameMap[Selector]
        : HTMLElement;

export const firstIn = <Selector extends string>(
    card: LitElement,
    selector: Selector,
): ElementFor<Selector> => {
    const found = card.shadowRoot?.querySelector(selector);
    if (found === null || found === undefined) {
        throw new Error(`Nothing matches ${selector}`);
    }
    return found as ElementFor<Selector>;
};

export const buttonIn = (
    card: LitElement,
    selector: string,
): HTMLButtonElement => {
    const found = card.shadowRoot?.querySelector<HTMLButtonElement>(selector);
    if (found === null || found === undefined) {
        throw new Error(`Nothing matches ${selector}`);
    }
    return found;
};

export const describeCardPicker = ({
    tag,
    card,
    startingOptions = {},
}: {
    tag: string;
    card: { getStubConfig: (hass: Hass) => object };
    startingOptions?: Record<string, unknown>;
}): void => {
    const registrations = vi
        .mocked(registerCard)
        .mock.calls.map(([entry]) => entry);

    describe(`${tag} picker contract`, () => {
        it("starts from the common starting configuration", () => {
            expect(card.getStubConfig(createFakeHass())).toEqual({
                stub: true,
                ...startingOptions,
            });
        });

        it("registers itself in the card picker with a preview", () => {
            expect(registrations).toEqual([
                expect.objectContaining({ type: tag, preview: true }),
            ]);
        });
    });
};
