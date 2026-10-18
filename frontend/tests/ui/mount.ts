import type { LitElement } from "lit";

export const mount = async <Element extends LitElement>(
    tag: string,
    properties: Partial<Element> = {},
): Promise<Element> => {
    const element = document.createElement(tag) as Element;
    Object.assign(element, properties);
    document.body.append(element);
    await element.updateComplete;
    return element;
};

export const settle = async (element: LitElement): Promise<void> => {
    element.requestUpdate();
    await element.updateComplete;
};

export const inShadow = (
    element: LitElement,
    selector: string,
): HTMLElement => {
    const found = element.shadowRoot?.querySelector<HTMLElement>(selector);
    if (found === null || found === undefined) {
        throw new Error(`Nothing matches ${selector}`);
    }
    return found;
};

export const allInShadow = (
    element: LitElement,
    selector: string,
): HTMLElement[] => [
    ...(element.shadowRoot?.querySelectorAll<HTMLElement>(selector) ?? []),
];

const asKind = <Kind extends HTMLElement>(
    found: HTMLElement,
    kind: abstract new () => Kind,
): Kind => {
    if (!(found instanceof kind)) {
        throw new Error("Unexpected element kind");
    }
    return found;
};

export const shadowInput = (
    element: LitElement,
    selector = "input",
): HTMLInputElement => asKind(inShadow(element, selector), HTMLInputElement);

export const shadowSelect = (element: LitElement): HTMLSelectElement =>
    asKind(inShadow(element, "select"), HTMLSelectElement);

export const shadowButton = (
    element: LitElement,
    selector = "button",
): HTMLButtonElement => asKind(inShadow(element, selector), HTMLButtonElement);

export const allShadowButtons = (element: LitElement): HTMLButtonElement[] =>
    allInShadow(element, "button").map((found) =>
        asKind(found, HTMLButtonElement),
    );

export const captureEvents = (
    target: EventTarget,
    type: string,
): CustomEvent<unknown>[] => {
    const events: CustomEvent<unknown>[] = [];
    target.addEventListener(type, (event) => {
        events.push(event as CustomEvent<unknown>);
    });
    return events;
};

export const changeField = (
    field: HTMLInputElement | HTMLSelectElement,
    text: string,
): void => {
    field.value = text;
    field.dispatchEvent(new Event("change", { bubbles: true }));
};
