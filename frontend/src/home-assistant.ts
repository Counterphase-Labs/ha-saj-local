const HOME_ASSISTANT_ELEMENT = "home-assistant";

export const whenHomeAssistantIsReady = (): Promise<CustomElementConstructor> =>
    customElements.whenDefined(HOME_ASSISTANT_ELEMENT);
