import { type Page } from "@playwright/test";

import { expect, removingVirtualizedList, test } from "../support/test";

const integrationName = "SAJ Local";

const account = {
    name: "Playwright User",
    username: "playwright",
    password: "playwright-test-password",
} as const;

const finishOnboarding = async (page: Page): Promise<void> => {
    await page.goto("/");
    const welcome = page.getByRole("button", { name: "Create my smart home" });
    await expect(welcome).toBeVisible();
    await welcome.click();

    await page
        .getByRole("textbox", { name: "Name*", exact: true })
        .fill(account.name);
    await page
        .getByRole("textbox", { name: "Username*", exact: true })
        .fill(account.username);
    await page
        .getByRole("textbox", { name: "Password*", exact: true })
        .fill(account.password);
    await page
        .getByRole("textbox", { name: "Confirm password*", exact: true })
        .fill(account.password);
    await page.getByRole("button", { name: /create account/i }).click();

    await expect(
        page.getByRole("heading", { name: "Home location" }),
    ).toBeVisible();
    await page.getByRole("button", { name: "Next" }).click();
    await expect(page.getByText(/country your home is in/i)).toBeVisible();
    await page.getByRole("button", { name: "Next" }).click();
    await page.getByRole("button", { name: /next|finish|skip/i }).click();
    await expect(page.getByRole("heading", { name: "All set!" })).toBeVisible();
    await page.getByRole("button", { name: "Finish" }).click();
    await expect(page).not.toHaveURL(/onboarding/);
    await expect(page.getByText("Settings", { exact: true })).toBeVisible();
};

const addIntegration = async (
    page: Page,
    browserFailures: string[],
): Promise<void> => {
    await page.getByRole("link", { name: "Settings" }).click();
    await page.getByRole("link", { name: /devices & services/i }).click();
    await page.getByRole("button", { name: /add integration/i }).click();
    await page
        .getByPlaceholder("Search for a brand name")
        .fill(integrationName);
    await expect(
        page.getByRole("button", { name: integrationName }),
    ).toBeVisible();
    browserFailures.length = 0;
    const brand = page.getByRole("button", { name: integrationName });
    await removingVirtualizedList(
        page,
        browserFailures,
        page.locator("lit-virtualizer").filter({ has: brand }),
        async () => {
            await brand.click();
        },
    );
    await page.getByRole("textbox", { name: "Host*" }).fill("modbus-observer");
    await page.getByRole("spinbutton", { name: "Port*" }).fill("502");
    const unitId = page.getByRole("spinbutton", { name: "Unit ID*" });
    await expect(unitId).toBeVisible();
    await expect(page.getByRole("slider", { name: "Unit ID*" })).toHaveCount(0);
    await unitId.fill("1");
    const interval = page.getByRole("spinbutton", {
        name: "Seconds between updates*",
    });
    await expect(interval).toBeVisible();
    await interval.fill("30");
    await page.getByRole("button", { name: /submit/i }).click();
    await page.getByRole("button", { name: "Finish" }).click();
    await expect
        .poll(async () =>
            page.evaluate(async () => {
                interface HassApi {
                    callWS: <T>(command: { type: string }) => Promise<T>;
                }
                interface HomeAssistantElement extends HTMLElement {
                    hass?: HassApi;
                }
                const root =
                    document.querySelector<HomeAssistantElement>(
                        "home-assistant",
                    );
                const hass = root?.hass;
                if (!hass) {
                    return false;
                }
                const registry = await hass.callWS<
                    { entity_id: string; platform: string }[]
                >({ type: "config/entity_registry/list" });
                const entities = registry.filter(
                    (entity) => entity.platform === "saj_local",
                );
                const states = await hass.callWS<
                    { entity_id: string; state: string }[]
                >({ type: "get_states" });
                return entities.some((entity: { entity_id: string }) =>
                    states.some(
                        (state) =>
                            state.entity_id === entity.entity_id &&
                            !["unknown", "unavailable"].includes(state.state),
                    ),
                );
            }),
        )
        .toBe(true);
};

const modbusReadCount = async (page: Page): Promise<number> => {
    const response = await page.request.get(
        "http://modbus-observer:8000/stats",
    );
    expect(response.ok()).toBeTruthy();
    const result = (await response.json()) as { read_requests: number };
    return result.read_requests;
};

const callHassWebSocket = async <T>(
    page: Page,
    command: { type: string; [key: string]: unknown },
): Promise<T> =>
    page.evaluate(async (message) => {
        interface HassApi {
            callWS: <Result>(command: {
                type: string;
                [key: string]: unknown;
            }) => Promise<Result>;
        }
        interface HomeAssistantElement extends HTMLElement {
            hass?: HassApi;
        }
        const hass =
            document.querySelector<HomeAssistantElement>(
                "home-assistant",
            )?.hass;
        if (!hass) {
            throw new Error("Home Assistant WebSocket API is unavailable");
        }
        return hass.callWS<T>(message);
    }, command);

const entityIds = async (page: Page): Promise<string[]> => {
    const registry = await callHassWebSocket<
        { entity_id: string; platform: string }[]
    >(page, { type: "config/entity_registry/list" });
    return registry
        .filter((entity) => entity.platform === "saj_local")
        .map((entity) => entity.entity_id);
};

const entityRegistryEntries = async (page: Page) => {
    const registry = await callHassWebSocket<
        {
            entity_id: string;
            unique_id: string;
            platform: string;
            disabled_by: string | null;
            name: string | null;
        }[]
    >(page, { type: "config/entity_registry/list" });
    return registry.filter((entity) => entity.platform === "saj_local");
};

const expectEntityIdentities = async (
    page: Page,
    identities: { entity_id: string; unique_id: string }[],
): Promise<void> => {
    expect(
        (await entityRegistryEntries(page))
            .map(({ entity_id, unique_id }) => ({ entity_id, unique_id }))
            .sort((left, right) =>
                left.entity_id.localeCompare(right.entity_id),
            ),
    ).toEqual(identities);
};

const expectEntityName = async (
    page: Page,
    entityId: string,
    name: string,
): Promise<void> => {
    await expect
        .poll(
            async () =>
                (await entityRegistryEntries(page)).find(
                    (entity) => entity.entity_id === entityId,
                )?.name,
        )
        .toBe(name);
};

const openNativeOptions = async (page: Page): Promise<void> => {
    await page.goto("/config/integrations");
    const integration = page
        .getByText(integrationName, { exact: true })
        .first();
    await expect(integration).toBeVisible();
    await integration.click();
    await page.getByRole("button", { name: /^configure$/i }).click();
};

const editEndpoint = async (page: Page, port: number): Promise<void> => {
    await openNativeOptions(page);
    await expect(page.getByRole("textbox", { name: "Host" })).toHaveValue(
        "modbus-observer",
    );
    await expect(
        page.getByRole("spinbutton", { name: "Seconds between updates" }),
    ).toHaveValue("30");
    await page.getByRole("spinbutton", { name: "Port" }).fill(String(port));
    await expect(page.getByRole("checkbox")).toHaveCount(0);
    await expect(page.getByRole("textbox", { name: "Host" })).toHaveCount(1);
    await expect(page.getByRole("spinbutton", { name: "Unit ID" })).toHaveCount(
        1,
    );
    await expect(
        page.getByRole("spinbutton", { name: "Seconds between updates" }),
    ).toHaveCount(1);
    await expect(page.getByRole("spinbutton")).toHaveCount(3);
    await page.getByRole("button", { name: /submit/i }).click();
};

const deviceRegistryEntries = async (page: Page) =>
    callHassWebSocket<
        {
            id: string;
            name: string | null;
            identifiers: [string, string][];
            serial_number: string | null;
            model: string | null;
        }[]
    >(page, { type: "config/device_registry/list" });

const stateFor = async (page: Page, entityId: string) => {
    const states = await callHassWebSocket<
        { entity_id: string; state: string; last_updated: string }[]
    >(page, { type: "get_states" });
    return states.find((state) => state.entity_id === entityId);
};

const expectSensorAvailable = async (
    page: Page,
    entityId: string,
): Promise<void> => {
    await expect
        .poll(async () => {
            const state = await stateFor(page, entityId);
            return Boolean(
                state && !["unknown", "unavailable"].includes(state.state),
            );
        })
        .toBe(true);
};

interface HistoryRecord {
    s: string;
    lc: number;
    lu?: number;
}

const historyFor = async (page: Page, entityIds: string[], startTime: string) =>
    callHassWebSocket<Record<string, HistoryRecord[]>>(page, {
        type: "history/history_during_period",
        start_time: startTime,
        entity_ids: entityIds,
        minimal_response: false,
        no_attributes: true,
    });

const expectHistoryRecordsRetained = (
    before: Record<string, HistoryRecord[]>,
    after: Record<string, HistoryRecord[]>,
    entityIds: string[],
): void => {
    for (const entityId of entityIds) {
        const oldRecords = before[entityId] ?? [];
        const newRecords = after[entityId] ?? [];
        expect(
            oldRecords.length,
            `recorded history for ${entityId}`,
        ).toBeGreaterThan(0);
        for (const oldRecord of oldRecords) {
            const oldTimestamp = oldRecord.lu ?? oldRecord.lc;
            expect(
                newRecords.some(
                    (record) =>
                        record.s === oldRecord.s &&
                        (record.lu ?? record.lc) === oldTimestamp,
                ),
                `original history record ${entityId} at ${String(oldTimestamp)}`,
            ).toBe(true);
        }
    }
};

const setEntityDisabled = async (
    page: Page,
    entityId: string,
    disabled: boolean,
): Promise<void> => {
    await callHassWebSocket(page, {
        type: "config/entity_registry/update",
        entity_id: entityId,
        disabled_by: disabled ? "user" : null,
    });
};

const setEntityName = async (
    page: Page,
    entityId: string,
    name: string,
): Promise<void> => {
    await callHassWebSocket(page, {
        type: "config/entity_registry/update",
        entity_id: entityId,
        name,
    });
};

test("the integration can be added through the user interface", async ({
    page,
    browserFailures,
}) => {
    await finishOnboarding(page);
    await addIntegration(page, browserFailures);
    const entities = await entityIds(page);
    expect(entities).toHaveLength(6);
    expect([...entities].sort()).toEqual(
        [
            "sensor.saj_operating_mode",
            "sensor.saj_solar_power",
            "sensor.saj_battery_power",
            "sensor.saj_battery_charge",
            "sensor.saj_grid_power",
            "sensor.saj_household_load",
        ].sort(),
    );

    const beforeRegistry = await entityRegistryEntries(page);
    const beforeIdentities = beforeRegistry
        .map(({ entity_id, unique_id }) => ({ entity_id, unique_id }))
        .sort((left, right) => left.entity_id.localeCompare(right.entity_id));
    const recordedEntity = beforeRegistry[0];
    const disabledEntity = beforeRegistry[1];
    if (!recordedEntity || !disabledEntity) {
        throw new Error(
            "The integration did not create its six sensor entities",
        );
    }
    const historyStart = new Date(Date.now() - 60_000).toISOString();
    const beforeState = await stateFor(page, recordedEntity.entity_id);
    expect(beforeState).toBeDefined();
    if (!beforeState) {
        throw new Error("The integration has no initial recorded sensor state");
    }
    const recordedEntityIds = beforeRegistry.map((entity) => entity.entity_id);
    let beforeHistory: Record<string, HistoryRecord[]> = {};
    await expect
        .poll(async () => {
            beforeHistory = await historyFor(
                page,
                recordedEntityIds,
                historyStart,
            );
            return recordedEntityIds.every(
                (entityId) => (beforeHistory[entityId]?.length ?? 0) > 0,
            );
        })
        .toBe(true);
    const beforeDevices = (await deviceRegistryEntries(page)).filter((device) =>
        device.identifiers.some(([domain]) => domain === "saj_local"),
    );
    expect(beforeDevices).toHaveLength(1);
    const originalDevice = beforeDevices[0];
    if (!originalDevice) {
        throw new Error("The integration did not create a native device");
    }
    expect(originalDevice.model).toBe("HS3 (12000 W)");
    expect(originalDevice.name).toBe("SAJ");
    const customisedEntity = beforeRegistry.find((entity) =>
        entity.entity_id.endsWith("solar_power"),
    );
    if (!customisedEntity) {
        throw new Error("The solar power entity was not registered");
    }
    const customName = "House array output";
    await setEntityName(page, customisedEntity.entity_id, customName);
    await expectEntityName(page, customisedEntity.entity_id, customName);
    await setEntityDisabled(page, disabledEntity.entity_id, true);

    const readsBeforeConnectionEdit = await modbusReadCount(page);
    await editEndpoint(page, 5022);
    await expect
        .poll(() => modbusReadCount(page))
        .toBeGreaterThan(readsBeforeConnectionEdit + 11);
    await expectSensorAvailable(page, recordedEntity.entity_id);
    await expectEntityIdentities(page, beforeIdentities);
    await expectEntityName(page, customisedEntity.entity_id, customName);
    const afterConnectionEditHistory = await historyFor(
        page,
        recordedEntityIds,
        historyStart,
    );
    expectHistoryRecordsRetained(
        beforeHistory,
        afterConnectionEditHistory,
        recordedEntityIds,
    );

    const replacementSerial = "HS3-SMOKE-REPLACE";
    const controlResponse = await page.request.post(
        "http://modbus-observer:8001/control",
        { data: { serial: replacementSerial } },
    );
    expect(controlResponse.ok()).toBeTruthy();
    await editEndpoint(page, 5022);
    await expect(page.getByText(new RegExp(replacementSerial))).toBeVisible();
    const validatedReplacementReadCount = await modbusReadCount(page);
    await page.getByRole("button", { name: /submit/i }).click();
    await expect
        .poll(() => modbusReadCount(page))
        .toBeGreaterThan(validatedReplacementReadCount + 5);

    await expectSensorAvailable(page, recordedEntity.entity_id);
    await expectEntityIdentities(page, beforeIdentities);
    await expectEntityName(page, customisedEntity.entity_id, customName);
    const afterDisabled = (await entityRegistryEntries(page)).find(
        (entity) => entity.entity_id === disabledEntity.entity_id,
    );
    expect(afterDisabled?.disabled_by).toBe("user");
    const afterDevices = (await deviceRegistryEntries(page)).filter((device) =>
        device.identifiers.some(([domain]) => domain === "saj_local"),
    );
    expect(afterDevices).toHaveLength(1);
    expect(afterDevices[0]?.id).toBe(originalDevice.id);
    expect(afterDevices[0]?.identifiers).toEqual(originalDevice.identifiers);
    expect(afterDevices[0]?.serial_number).toBe(replacementSerial);
    const afterHistory = await historyFor(
        page,
        recordedEntityIds,
        historyStart,
    );
    expectHistoryRecordsRetained(
        beforeHistory,
        afterHistory,
        recordedEntityIds,
    );

    await setEntityDisabled(page, disabledEntity.entity_id, false);

    for (const entityId of entities) {
        await setEntityDisabled(page, entityId, true);
    }
    await expect
        .poll(async () => {
            const states = await callHassWebSocket<
                { entity_id: string; state: string }[]
            >(page, { type: "get_states" });
            return entities.every(
                (entityId) =>
                    !states.some((state) => state.entity_id === entityId),
            );
        })
        .toBe(true);

    await page.waitForTimeout(32_000);
    const disabledReadCount = await modbusReadCount(page);
    await page.waitForTimeout(32_000);
    expect(await modbusReadCount(page)).toBe(disabledReadCount);

    const entityToEnable = entities[0];
    if (!entityToEnable) {
        throw new Error("The integration has no entity to re-enable");
    }
    await setEntityDisabled(page, entityToEnable, false);
    await expect
        .poll(() => modbusReadCount(page), {
            timeout: 40_000,
            intervals: [500, 1000],
        })
        .toBeGreaterThan(disabledReadCount);
});
