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

interface RegistryEntity {
    entity_id: string;
    platform: string;
    config_entry_id: string | null;
}

interface EntityState {
    entity_id: string;
    state: string;
}

interface HassCommand {
    type: string;
    [field: string]: unknown;
}

const callHassWebSocket = async <T>(
    page: Page,
    command: HassCommand,
): Promise<T> =>
    page.evaluate(async (message) => {
        interface HassApi {
            callWS: <Result>(command: HassCommand) => Promise<Result>;
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

const addIntegration = async (
    page: Page,
    browserFailures: string[],
    host: string,
    prefix = "",
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
    await page.getByRole("textbox", { name: "Host*" }).fill(host);
    await page.getByRole("spinbutton", { name: "Port*" }).fill("502");
    await page.getByRole("spinbutton", { name: "Unit ID*" }).fill("1");
    await page
        .getByRole("spinbutton", { name: "Seconds between updates*" })
        .fill("30");
    if (prefix) {
        await page.getByRole("textbox", { name: "Prefix" }).fill(prefix);
    }
    await page.getByRole("button", { name: /submit/i }).click();
    await page.getByRole("button", { name: "Finish" }).click();
};

const smokeEntities = [
    "sensor.pv_power",
    "sensor.pv_energy_total",
    "number.battery_discharge_limit_on_grid",
] as const;

const smokeEntityId = (prefix: string, entity: string): string => {
    const [domain = "", key = ""] = entity.split(".");
    return `${domain}.saj_${prefix ? `${prefix}_` : ""}${key}`;
};

const expectCoreEntitiesReportValues = async (
    page: Page,
    prefixes: readonly string[],
): Promise<void> => {
    await expect
        .poll(async () => {
            const registry = await callHassWebSocket<RegistryEntity[]>(page, {
                type: "config/entity_registry/list",
            });
            const states = await callHassWebSocket<EntityState[]>(page, {
                type: "get_states",
            });
            const entries = new Set(
                registry
                    .filter((entity) => entity.platform === "saj_local")
                    .map((entity) => entity.config_entry_id),
            );
            return (
                entries.size === prefixes.length &&
                prefixes.every((prefix) =>
                    smokeEntities.every((entity) =>
                        states.some(
                            (state) =>
                                state.entity_id ===
                                    smokeEntityId(prefix, entity) &&
                                !["unknown", "unavailable"].includes(
                                    state.state,
                                ),
                        ),
                    ),
                )
            );
        })
        .toBe(true);
};

interface OptionsFlow {
    type: string;
    flow_id: string;
    step_id?: string;
    data_schema?: {
        name: string;
        default?: unknown;
        description?: { suggested_value?: unknown };
    }[];
}

const allowControl = async (page: Page, entityId: string): Promise<void> => {
    const registry = await callHassWebSocket<RegistryEntity[]>(page, {
        type: "config/entity_registry/list",
    });
    const entryId = registry.find(
        (entity) => entity.entity_id === entityId,
    )?.config_entry_id;
    expect(entryId).toBeTruthy();
    await page.evaluate(async (handler) => {
        interface HassApi {
            callApi: <Result>(
                method: string,
                path: string,
                body?: object,
            ) => Promise<Result>;
        }
        interface HomeAssistantElement extends HTMLElement {
            hass?: HassApi;
        }
        const hass =
            document.querySelector<HomeAssistantElement>(
                "home-assistant",
            )?.hass;
        if (!hass) {
            throw new Error("Home Assistant API is unavailable");
        }
        const path = "config/config_entries/options/flow";
        const form = await hass.callApi<OptionsFlow>("POST", path, { handler });
        const defaults: Record<string, unknown> = {};
        for (const field of form.data_schema ?? []) {
            const value = field.default ?? field.description?.suggested_value;
            if (value !== undefined) {
                defaults[field.name] = value;
            }
        }
        const confirmation = await hass.callApi<OptionsFlow>(
            "POST",
            `${path}/${form.flow_id}`,
            { ...defaults, allow_control: true },
        );
        if (confirmation.step_id !== "confirm_control") {
            throw new Error(`Unexpected step ${JSON.stringify(confirmation)}`);
        }
        await hass.callApi<OptionsFlow>(
            "POST",
            `${path}/${confirmation.flow_id}`,
            {},
        );
    }, entryId);
};

const stateOf = async (page: Page, entityId: string): Promise<string> => {
    const states = await callHassWebSocket<EntityState[]>(page, {
        type: "get_states",
    });
    return states.find((state) => state.entity_id === entityId)?.state ?? "";
};

const setNumber = async (
    page: Page,
    entityId: string,
    value: number,
): Promise<void> => {
    await callHassWebSocket(page, {
        type: "call_service",
        domain: "number",
        service: "set_value",
        service_data: { entity_id: entityId, value },
    });
};

const DASHBOARD_URL_PATH = "saj-local-power-flow";
const ELEMENT_REGISTRATION_TIMEOUT_MS = 60_000;
const POWER_FLOW_ELEMENT = "saj-local-power-flow-card";
const HS3_MODEL_PREFIX = "HS3";
const SOLAR_VALUE = /^\d.*W$/;

interface RegisteredDevice {
    id: string;
    model: string | null;
}

const expectPowerFlowCardShowsSolarPower = async (
    page: Page,
): Promise<void> => {
    const devices = await callHassWebSocket<RegisteredDevice[]>(page, {
        type: "config/device_registry/list",
    });
    const system = devices.find((device) =>
        (device.model ?? "").startsWith(HS3_MODEL_PREFIX),
    );
    if (system === undefined) {
        throw new Error("The HS3 system is not in the device registry");
    }
    await callHassWebSocket(page, {
        type: "lovelace/dashboards/create",
        url_path: DASHBOARD_URL_PATH,
        title: "SAJ Local power flow",
        mode: "storage",
        require_admin: false,
        show_in_sidebar: false,
    });
    await callHassWebSocket(page, {
        type: "lovelace/config/save",
        url_path: DASHBOARD_URL_PATH,
        config: {
            views: [
                {
                    title: "Power flow",
                    cards: [
                        {
                            type: `custom:${POWER_FLOW_ELEMENT}`,
                            device: system.id,
                        },
                    ],
                },
            ],
        },
    });
    await page.goto("/");
    await page.waitForFunction(
        (tag) => customElements.get(tag) !== undefined,
        POWER_FLOW_ELEMENT,
        { timeout: ELEMENT_REGISTRATION_TIMEOUT_MS },
    );
    await expect(page.getByRole("link", { name: "Settings" })).toBeVisible();
    await page.evaluate((path) => {
        history.pushState(null, "", path);
        window.dispatchEvent(new CustomEvent("location-changed"));
    }, `/${DASHBOARD_URL_PATH}`);
    await expect(
        page.locator(
            `${POWER_FLOW_ELEMENT} g.node[aria-label^="Solar"] text.value`,
        ),
    ).toHaveText(SOLAR_VALUE);
};

const REQUEST_BUDGET_WINDOW_MS = 60_000;
const SETTING_CHANGE_TIMEOUT_MS = REQUEST_BUDGET_WINDOW_MS + 15_000;
const TEST_TIMEOUT_MS = 2 * SETTING_CHANGE_TIMEOUT_MS + 120_000;

const expectSettingChangeToShow = async (
    page: Page,
    entityId: string,
): Promise<void> => {
    const before = await stateOf(page, entityId);
    const wanted = before === "40" ? "41" : "40";
    await expect(setNumber(page, entityId, Number(wanted))).rejects.toThrow();
    expect(await stateOf(page, entityId)).toBe(before);
    await allowControl(page, entityId);
    await expect
        .poll(
            async () => {
                try {
                    await setNumber(page, entityId, Number(wanted));
                } catch {
                    return "";
                }
                return stateOf(page, entityId);
            },
            { timeout: SETTING_CHANGE_TIMEOUT_MS },
        )
        .toBe(wanted);
};

test("an HS3 and an H2 endpoint load, report values, show a solar value on a dashboard power flow card, refuse a change until control is allowed, then change a setting", async ({
    page,
    browserFailures,
}) => {
    test.setTimeout(TEST_TIMEOUT_MS);
    await finishOnboarding(page);

    await addIntegration(page, browserFailures, "modbus-mock");
    await expectCoreEntitiesReportValues(page, [""]);
    await expectPowerFlowCardShowsSolarPower(page);

    await addIntegration(page, browserFailures, "modbus-mock-h2", "h2");
    await expectCoreEntitiesReportValues(page, ["", "h2"]);

    for (const prefix of ["", "h2"]) {
        await expectSettingChangeToShow(
            page,
            smokeEntityId(prefix, "number.battery_discharge_limit_on_grid"),
        );
    }
});
