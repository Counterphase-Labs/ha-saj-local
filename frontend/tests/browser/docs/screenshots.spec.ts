import { mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

import {
    expect,
    test,
    type APIRequestContext,
    type Locator,
    type Page,
} from "@playwright/test";

const locale = process.env.DOCS_LOCALE ?? "en-GB";
const imageDirectory = resolve(
    import.meta.dirname,
    "../../../../docs/images",
    locale.toLowerCase(),
);
// A step that validates the endpoint reads the inverter first.
const FLOW_STEP_TIMEOUT_MS = 60_000;
const READING_TIMEOUT_MS = 120_000;
const ISSUE_TIMEOUT_MS = 120_000;
const CONTROL_ENTITIES_TIMEOUT_MS = 120_000;
const account = {
    name: "Docs User",
    username: "docs",
    password: "docs-password-1",
} as const;

const HS3_HOST = "mock-docs";
const HS3_TITLE = "SAJ HS3MOCK0000000000003";
const H2_HOST = "mock-h2";
const H2_PREFIX = "h2";
const SIMULATOR_PANEL = "http://mock-docs:8080";
// The inverter temperature is one register of the HS3 realtime block, so
// refusing it leaves every other reading of the system answering.
const REFUSED_KEY = "inverter_temperature";
const REFUSED_REGISTER = 0x4010;
const ILLEGAL_ADDRESS = 2;
const REFUSED_INTERVAL_SECONDS = 10;

interface FlowResult {
    type: string;
    flow_id: string;
    step_id?: string;
    reason?: string;
    errors?: Record<string, string> | null;
}

interface HassConnection {
    callApi(
        method: string,
        path: string,
        body?: Record<string, unknown>,
    ): Promise<unknown>;
    callWS(message: Record<string, unknown>): Promise<unknown>;
    language: string;
    localize(key: string): string;
    states: Record<
        string,
        { state: string; attributes: Record<string, unknown> } | undefined
    >;
}

interface RegistryEntity {
    entity_id: string;
    platform: string;
    config_entry_id: string | null;
}

interface RegisteredDevice {
    id: string;
    model: string | null;
    config_entries: string[];
}

interface DashboardElement {
    tag: string;
    config: Record<string, unknown>;
}

test.use({ locale: "en-US" });

const screenshots = new Map<string, Buffer>();

const hassApi = (
    page: Page,
    method: string,
    path: string,
    body?: Record<string, unknown>,
): Promise<unknown> =>
    page.evaluate(
        async ([apiMethod, apiPath, apiBody]) => {
            try {
                return await (
                    document.querySelector("home-assistant") as unknown as {
                        hass: HassConnection;
                    }
                ).hass.callApi(apiMethod, apiPath, apiBody);
            } catch (error) {
                // Home Assistant rejects with a plain object, not an Error.
                throw new Error(`${apiPath}: ${JSON.stringify(error)}`, {
                    cause: error,
                });
            }
        },
        [method, path, body] as const,
    );

const hassWebSocket = (
    page: Page,
    message: Record<string, unknown>,
): Promise<unknown> =>
    page.evaluate(
        (wsMessage) =>
            (
                document.querySelector("home-assistant") as unknown as {
                    hass: HassConnection;
                }
            ).hass.callWS(wsMessage),
        message,
    );

const hassState = (page: Page, entityId: string): Promise<string | undefined> =>
    page.evaluate(
        (id) =>
            (
                document.querySelector("home-assistant") as unknown as {
                    hass: HassConnection;
                }
            ).hass.states[id]?.state,
        entityId,
    );

const hassLanguage = (page: Page): Promise<string> =>
    page.evaluate(
        () =>
            (
                document.querySelector("home-assistant") as unknown as {
                    hass: HassConnection;
                }
            ).hass.language,
    );

// The text of a Home Assistant control that has only its text, read from the
// running Home Assistant in the user's language. A renamed key is fixed here.
const localized = async (page: Page, key: string): Promise<string> => {
    const read = (): Promise<string> =>
        page.evaluate(
            (textKey) =>
                (
                    document.querySelector("home-assistant") as unknown as {
                        hass: HassConnection;
                    }
                ).hass.localize(textKey),
            key,
        );
    // A page loads the texts of its panel after it has started.
    await expect
        .poll(read, { message: `Home Assistant has no text for ${key}` })
        .toBeTruthy();
    return read();
};

// SAJ Local's own text, read from the integration's translations that Home
// Assistant serves. The third part of the key is the translation category.
const integrationText = async (page: Page, key: string): Promise<string> => {
    const { resources } = (await hassWebSocket(page, {
        type: "frontend/get_translations",
        language: await hassLanguage(page),
        category: key.split(".")[2],
        integration: ["saj_local"],
    })) as { resources: Record<string, string | undefined> };
    const text = resources[key];
    expect(text, `SAJ Local has no text for ${key}`).toBeTruthy();
    return text ?? "";
};

// Home Assistant names an entity in its server language when the entity is
// created, so a name in another language means the server language was set
// too late or not at all.
const expectEntityNamesInLanguage = async (page: Page): Promise<void> => {
    const expected = await integrationText(
        page,
        "component.saj_local.entity.sensor.battery_power.name",
    );
    const id = entityId("sensor", "battery_power");
    const name = await page.evaluate(
        (stateId) =>
            (
                document.querySelector("home-assistant") as unknown as {
                    hass: HassConnection;
                }
            ).hass.states[stateId]?.attributes.friendly_name,
        id,
    );
    expect(
        typeof name === "string" && name.endsWith(expected),
        `${id} is named "${String(name)}", not in ${locale} ("${expected}"): the server language was not applied before SAJ Local was set up`,
    ).toBe(true);
};

const VIEWPORT = { width: 1280, height: 800 } as const;
// A tall dialog or card is taller than the viewport, and Home Assistant's fixed
// header would cover its top, so such an element is taken in a taller window.
const TALL_VIEWPORT = { width: VIEWPORT.width, height: 1600 } as const;

const waitForTwoFrames = async (page: Page): Promise<void> => {
    await page.evaluate(
        () =>
            new Promise<void>((done) => {
                requestAnimationFrame(() => {
                    requestAnimationFrame(() => {
                        done();
                    });
                });
            }),
    );
};

const capture = async (
    name: string,
    target: Locator,
    { tall = false }: { tall?: boolean } = {},
): Promise<void> => {
    const page = target.page();
    if (tall) {
        await page.setViewportSize(TALL_VIEWPORT);
        await waitForTwoFrames(page);
    }
    await expect(target).toBeVisible();
    screenshots.set(name, await target.screenshot({ animations: "disabled" }));
    if (tall) {
        await page.setViewportSize(VIEWPORT);
    }
};

const hasReading = async (page: Page, entityId: string): Promise<boolean> => {
    const state = await hassState(page, entityId);
    return state !== undefined && !["unknown", "unavailable"].includes(state);
};

const entityId = (domain: string, key: string, prefix = ""): string =>
    `${domain}.saj_${prefix === "" ? "" : `${prefix}_`}${key}`;

const completeOnboarding = async (
    request: APIRequestContext,
    baseUrl: string,
): Promise<void> => {
    const clientId = `${baseUrl}/`;
    const created = await request.post("/api/onboarding/users", {
        data: { client_id: clientId, language: locale, ...account },
    });
    expect(created.ok()).toBe(true);
    const { auth_code: code } = (await created.json()) as { auth_code: string };
    const token = await request.post("/auth/token", {
        form: {
            grant_type: "authorization_code",
            code,
            client_id: clientId,
        },
    });
    const { access_token: accessToken } = (await token.json()) as {
        access_token: string;
    };
    const headers = { authorization: `Bearer ${accessToken}` };
    for (const step of ["core_config", "analytics"]) {
        const done = await request.post(`/api/onboarding/${step}`, {
            headers,
            data: {},
        });
        expect(done.ok()).toBe(true);
    }
    const integration = await request.post("/api/onboarding/integration", {
        headers,
        data: { client_id: clientId, redirect_uri: clientId },
    });
    expect(integration.ok()).toBe(true);
};

const logIn = async (page: Page): Promise<void> => {
    await page.goto("/");
    // The sign-in form is Home Assistant's own, found by input name and element.
    await page
        .locator('ha-auth-flow input[name="username"]')
        .fill(account.username);
    // Enter in the password field submits the form, whatever the button text.
    const password = page.locator('ha-auth-flow input[name="password"]');
    await password.fill(account.password);
    await password.press("Enter");
    await expect(page.locator("ha-sidebar")).toBeVisible();
};

// The language is stored the way the profile page stores it, in the user's
// frontend data and in the browser, so the code is set without the picker.
const selectUserLanguage = async (page: Page): Promise<void> => {
    await hassWebSocket(page, {
        type: "frontend/set_user_data",
        key: "language",
        value: {
            language: locale,
            number_format: "language",
            time_format: "language",
            date_format: "language",
            time_zone: "local",
            first_weekday: "language",
        },
    });
    await page.evaluate((code) => {
        window.localStorage.setItem("selectedLanguage", JSON.stringify(code));
    }, locale);
    await page.reload();
    await expect.poll(() => hassLanguage(page)).toBe(locale);
    await expect(page.locator("ha-sidebar")).toBeVisible();
};

const flowDialog = (page: Page): Locator => page.getByRole("dialog").last();

// The form is slotted into the dialog, so queries search the flow dialog host.
const flowForm = (page: Page): Locator =>
    page.locator("dialog-data-entry-flow");

// Home Assistant gives each field of a form the name of its schema key.
const flowField = (page: Page, key: string): Locator =>
    flowForm(page).locator(`input[name="${key}"]`);

// The button of the flow dialog that goes on: Submit, Finish and the like.
const flowPrimaryButton = (page: Page): Locator =>
    flowForm(page).locator('ha-button[slot="primaryAction"]:not([href])');

const closeFlowDialog = async (page: Page): Promise<void> => {
    // Closing the dialog aborts the flow, so nothing is saved.
    await flowForm(page).locator('[data-dialog="close"]').first().click();
    await expect(page.getByRole("dialog")).toHaveCount(0);
};

const addHs3 = async (page: Page): Promise<void> => {
    // Home Assistant's own route that starts the flow of one integration.
    await page.goto("/config/integrations/dashboard/add?domain=saj_local");
    // Home Assistant first asks to confirm the setup; OK is the primary action.
    await page.locator('[slot="primaryAction"]').click();
    // The port and the unit ID keep their defaults, 502 and 1.
    await flowField(page, "host").fill(HS3_HOST);
    await capture("getting-started-add-system", flowDialog(page), {
        tall: true,
    });
    // The model picker is the only list item of the form.
    await flowForm(page).getByRole("listitem").click();
    // Automatic is the first model on offer.
    const automatic = page.getByRole("menuitem").first();
    await expect(automatic).toBeVisible();
    await capture("getting-started-manual-model", page.locator("body"));
    await automatic.click();
    await flowPrimaryButton(page).click();
    await expect(flowField(page, "host")).toHaveCount(0, {
        timeout: FLOW_STEP_TIMEOUT_MS,
    });
    // The last step of the flow ends it with its primary button.
    await flowPrimaryButton(page).click();
    await expect(page.getByRole("dialog")).toHaveCount(0);
};

const addH2 = async (page: Page): Promise<void> => {
    const flow = "config/config_entries/flow";
    const form = (await hassApi(page, "POST", flow, {
        handler: "saj_local",
    })) as FlowResult;
    const created = (await hassApi(page, "POST", `${flow}/${form.flow_id}`, {
        host: H2_HOST,
        port: 502,
        unit_id: 1,
        scan_interval: 60,
        model: "automatic",
        prefix: H2_PREFIX,
        allow_control: false,
    })) as FlowResult;
    expect(created.type, JSON.stringify(created.errors)).toBe("create_entry");
};

const entryIdOf = async (page: Page, prefix: string): Promise<string> => {
    const registry = (await hassWebSocket(page, {
        type: "config/entity_registry/list",
    })) as RegistryEntity[];
    const wanted = entityId("sensor", "pv_power", prefix);
    const entry = registry.find((entity) => entity.entity_id === wanted);
    expect(entry?.config_entry_id).toBeTruthy();
    return entry?.config_entry_id ?? "";
};

const waitForSolarPower = async (page: Page): Promise<void> => {
    await expect
        .poll(
            async () =>
                (await hasReading(page, entityId("sensor", "pv_power"))) &&
                (await hasReading(
                    page,
                    entityId("sensor", "pv_power", H2_PREFIX),
                )),
            {
                message:
                    "Neither the HS3 nor the H2 reported solar power within two minutes",
                timeout: READING_TIMEOUT_MS,
                intervals: [2000],
            },
        )
        .toBe(true);
};

const deviceOf = async (page: Page, model: string): Promise<string> => {
    const devices = (await hassWebSocket(page, {
        type: "config/device_registry/list",
    })) as RegisteredDevice[];
    const device = devices.find((candidate) =>
        (candidate.model ?? "").startsWith(model),
    );
    expect(device, `no ${model} device`).toBeDefined();
    return device?.id ?? "";
};

const dashboardPath = (name: string): string => `saj-docs-${name}`;

const addDashboard = async (
    page: Page,
    name: string,
    device: string,
    extra: Record<string, unknown>[],
): Promise<void> => {
    const urlPath = dashboardPath(name);
    await hassWebSocket(page, {
        type: "lovelace/dashboards/create",
        url_path: urlPath,
        title: `SAJ Local ${name}`,
        mode: "storage",
        require_admin: false,
        show_in_sidebar: false,
    });
    await hassWebSocket(page, {
        type: "lovelace/config/save",
        url_path: urlPath,
        config: {
            views: [
                {
                    title: name,
                    path: "overview",
                    badges: [{ type: "custom:saj-local-status-badge", device }],
                    cards: [
                        ...[
                            "power-flow",
                            "status",
                            "faults",
                            "battery",
                            "controls",
                            "schedule",
                        ].map((card) => ({
                            type: `custom:saj-local-${card}-card`,
                            device,
                        })),
                        ...extra,
                    ],
                },
            ],
        },
    });
};

const openDashboard = async (page: Page, name: string): Promise<void> => {
    await page.goto(`/${dashboardPath(name)}/overview`);
    await page.waitForFunction(
        () => customElements.get("saj-local-power-flow-card") !== undefined,
        undefined,
        { timeout: 60_000 },
    );
};

const element = (page: Page, tag: string): Locator => page.locator(tag).first();

const captureCards = async (
    page: Page,
    name: string,
    cards: Record<string, string>,
): Promise<void> => {
    await openDashboard(page, name);
    for (const [image, tag] of Object.entries(cards)) {
        const target = element(page, tag);
        await target.scrollIntoViewIfNeeded();
        await capture(image, target, { tall: true });
    }
};

const optionsEntryPage = async (page: Page): Promise<void> => {
    await page.goto("/config/integrations/integration/saj_local");
};

const openConfigure = async (page: Page): Promise<void> => {
    await page.goto("/config/integrations/integration/saj_local");
    await page
        .locator("ha-config-entry-row")
        .filter({ hasText: HS3_TITLE })
        .getByRole("button", {
            name: await localized(
                page,
                "ui.panel.config.integrations.config_entry.configure",
            ),
        })
        .click();
    await expect(flowField(page, "host")).toBeVisible();
};

const toggleAllowControl = async (page: Page): Promise<void> => {
    // The thumb of the switch covers the input, so the input is checked directly.
    const allowControl = flowForm(page).getByRole("switch");
    await flowForm(page).locator("ha-switch").click();
    await expect(allowControl).toBeChecked();
};

const submitFlow = async (page: Page): Promise<void> => {
    await flowPrimaryButton(page).click();
};

const captureConfigureForms = async (page: Page): Promise<void> => {
    await openConfigure(page);
    // The equipment section is the only collapsible section of the form.
    await flowForm(page).locator("ha-expansion-panel").first().click();
    await capture("optional-equipment-equipment-section", flowDialog(page), {
        tall: true,
    });
    await flowField(page, "prefix").fill("house");
    await submitFlow(page);
    await expect(
        flowForm(page).getByText(
            await integrationText(
                page,
                "component.saj_local.options.step.confirm_prefix.title",
            ),
        ),
    ).toBeVisible();
    await capture(
        "entities-and-prefix-prefix-change-warning",
        flowDialog(page),
        { tall: true },
    );
    await closeFlowDialog(page);
};

const capturePollingGroup = async (page: Page): Promise<void> => {
    await optionsEntryPage(page);
    await page
        .getByRole("button", {
            name: await integrationText(
                page,
                "component.saj_local.config_subentries.polling_group.initiate_flow.user",
            ),
        })
        .click();
    // The picker is the last element on the page, after the hub row of the same title.
    await page.getByText(HS3_TITLE, { exact: true }).last().click();
    await flowField(page, "name").fill("Fast");
    await capture("polling-polling-group", flowDialog(page), { tall: true });
    await closeFlowDialog(page);
};

const allowControlThroughForm = async (page: Page): Promise<void> => {
    await openConfigure(page);
    await toggleAllowControl(page);
    await submitFlow(page);
    await expect(
        flowForm(page).getByText(
            await integrationText(
                page,
                "component.saj_local.options.step.confirm_control.title",
            ),
        ),
    ).toBeVisible({ timeout: FLOW_STEP_TIMEOUT_MS });
    await capture("changing-settings-allow-control-warning", flowDialog(page), {
        tall: true,
    });
    await submitFlow(page);
    await closeFlowDialog(page);
};

const changeOptionsThroughApi = async (
    page: Page,
    entryId: string,
    changes: Record<string, unknown>,
    confirmations: string[],
): Promise<void> => {
    const path = "config/config_entries/options/flow";
    let result = (await hassApi(page, "POST", path, {
        handler: entryId,
    })) as FlowResult & {
        data_schema?: {
            name: string;
            default?: unknown;
            description?: { suggested_value?: unknown };
        }[];
    };
    const defaults: Record<string, unknown> = {};
    for (const field of result.data_schema ?? []) {
        const value = field.default ?? field.description?.suggested_value;
        if (value !== undefined) {
            defaults[field.name] = value;
        }
    }
    result = (await hassApi(page, "POST", `${path}/${result.flow_id}`, {
        ...defaults,
        ...changes,
    })) as FlowResult;
    for (const step of confirmations) {
        expect(result.step_id).toBe(step);
        result = (await hassApi(
            page,
            "POST",
            `${path}/${result.flow_id}`,
            {},
        )) as FlowResult;
    }
    // The options flow ends with an abort that says the settings were saved.
    expect(result.reason, JSON.stringify(result.errors)).toBe("changes_saved");
};

const allowControlThroughApi = (page: Page, entryId: string): Promise<void> =>
    changeOptionsThroughApi(page, entryId, { allow_control: true }, [
        "confirm_control",
    ]);

const setNumber = async (
    page: Page,
    entity: string,
    value: number,
): Promise<void> => {
    await hassWebSocket(page, {
        type: "call_service",
        domain: "number",
        service: "set_value",
        service_data: { entity_id: entity, value },
    });
    await expect.poll(() => hassState(page, entity)).toBe(String(value));
};

const waitForControlEntities = async (page: Page): Promise<void> => {
    await expect
        .poll(
            async () =>
                (await hasReading(
                    page,
                    entityId("number", "charge_slot_1_days"),
                )) &&
                (await hasReading(
                    page,
                    entityId("number", "charge_slot_1_days", H2_PREFIX),
                )),
            {
                message:
                    "The control entities did not appear after Allow control was switched on",
                timeout: CONTROL_ENTITIES_TIMEOUT_MS,
                intervals: [2000],
            },
        )
        .toBe(true);
};

const capturePowerSchedule = async (page: Page): Promise<void> => {
    await hassWebSocket(page, {
        type: "schedule/create",
        name: "Night charging",
        icon: "mdi:battery-clock",
        monday: [{ from: "01:00:00", to: "05:00:00" }],
        tuesday: [{ from: "01:00:00", to: "05:00:00" }],
        wednesday: [{ from: "01:00:00", to: "05:00:00" }],
        thursday: [{ from: "01:00:00", to: "05:00:00" }],
        friday: [{ from: "01:00:00", to: "05:00:00" }],
    });
    await optionsEntryPage(page);
    await page
        .getByRole("button", {
            name: await integrationText(
                page,
                "component.saj_local.config_subentries.power_schedule.initiate_flow.user",
            ),
        })
        .click();
    // The picker is the last element on the page, after the hub row of the same title.
    await page.getByText(HS3_TITLE, { exact: true }).last().click();
    const dialog = flowDialog(page);
    const form = flowForm(page);
    // Battery is the first function, so it is already chosen.
    await form.locator("ha-entity-picker").click();
    await page.getByText("Night charging", { exact: true }).last().click();
    // The entity picker is a second dialog until it has closed.
    await expect(page.getByRole("dialog")).toHaveCount(1);
    await capture("power-control-schedule-helper", dialog, { tall: true });
    await closeFlowDialog(page);
};

const captureDiagnostics = async (page: Page): Promise<void> => {
    await optionsEntryPage(page);
    // The first dropdown of a hub row is the menu of the installation itself.
    await page
        .locator("ha-config-entry-row")
        .filter({ hasText: HS3_TITLE })
        .locator("ha-dropdown")
        .first()
        .locator("ha-icon-button")
        .click();
    const item = page.getByRole("menuitem", {
        name: await localized(
            page,
            "ui.panel.config.integrations.config_entry.download_diagnostics",
        ),
    });
    await expect(item.first()).toBeVisible();
    await capture("troubleshooting-diagnostics-download", page.locator("body"));
    await page.keyboard.press("Escape");
};

const simulatorPost = async (
    request: APIRequestContext,
    path: string,
    body: Record<string, unknown>,
): Promise<void> => {
    const response = await request.post(`${SIMULATOR_PANEL}${path}`, {
        data: body,
    });
    expect(response.ok(), await response.text()).toBe(true);
};

// A polling group of the one reading the simulator refuses is read every
// REFUSED_INTERVAL_SECONDS on its own, so the refusals that suspend the reading
// come fast and do not wait for the slower default interval.
const addRepairPollingGroup = async (
    page: Page,
    entryId: string,
): Promise<void> => {
    const path = "config/config_entries/subentries/flow";
    const form = (await hassApi(page, "POST", path, {
        handler: [entryId, "polling_group"],
    })) as FlowResult & {
        data_schema?: {
            name: string;
            selector?: { select?: { options?: { value: string }[] } };
        }[];
    };
    const options =
        form.data_schema?.find((field) => field.name === "keys")?.selector
            ?.select?.options ?? [];
    expect(
        options.some((option) => option.value === REFUSED_KEY),
        `${REFUSED_KEY} is not offered to a polling group`,
    ).toBe(true);
    const review = (await hassApi(page, "POST", `${path}/${form.flow_id}`, {
        name: "Inverter temperature",
        scan_interval: REFUSED_INTERVAL_SECONDS,
        keys: [REFUSED_KEY],
    })) as FlowResult;
    const saved = (await hassApi(page, "POST", `${path}/${review.flow_id}`, {
        next_step_id: "save_group",
    })) as FlowResult;
    expect(saved.type, JSON.stringify(saved.errors)).toBe("create_entry");
};

const captureRepair = async (
    page: Page,
    request: APIRequestContext,
    entryId: string,
): Promise<void> => {
    await addRepairPollingGroup(page, entryId);
    await simulatorPost(request, "/api/link", {
        refused_blocks: [
            {
                start: REFUSED_REGISTER,
                end: REFUSED_REGISTER,
                code: ILLEGAL_ADDRESS,
            },
        ],
    });
    await expect
        .poll(
            async () => {
                const { issues } = (await hassWebSocket(page, {
                    type: "repairs/list_issues",
                })) as {
                    issues: { domain: string; translation_key: string }[];
                };
                return issues.some(
                    (issue) =>
                        issue.domain === "saj_local" &&
                        issue.translation_key === "registers_refused",
                );
            },
            {
                message: "SAJ Local repair issue registers_refused is missing",
                timeout: ISSUE_TIMEOUT_MS,
                intervals: [5000],
            },
        )
        .toBe(true);
    await page.goto("/config/repairs");
    await capture(
        "faults-and-repairs-repair-issue",
        // The title of the issue names the installation.
        page.getByRole("listitem").filter({ hasText: HS3_TITLE }),
    );
};

const SIMULATOR_PREFIX = "developer-simulator-page";
const H2_PANEL = "http://mock-h2:8080";
const SIMULATOR_FAULT = "Fan 1 fault";
// The simulator page names each view by the key of its tab link.
const SIMULATOR_VIEWS = [
    "faults",
    "settings",
    "registers",
    "traffic",
    "link",
    "scenario",
] as const;
const FAULT_SEARCH = "section.view:visible input[type=search]";

const capturePageView = async (
    page: Page,
    name: string,
    { tall = false }: { tall?: boolean } = {},
): Promise<void> => {
    await page.setViewportSize(tall ? TALL_VIEWPORT : VIEWPORT);
    await waitForTwoFrames(page);
    screenshots.set(
        `${SIMULATOR_PREFIX}-${name}`,
        await page.screenshot({ animations: "disabled" }),
    );
    await page.setViewportSize(VIEWPORT);
};

const openSimulatorView = async (page: Page, view: string): Promise<void> => {
    await page.locator(`nav.tabs a[href="#${view}"]`).click();
    await expect(
        page.locator(`nav.tabs a[href="#${view}"][aria-current="page"]`),
    ).toBeVisible();
    await expect(page.locator("section.view:visible h2").first()).toBeVisible();
};

const waitForOverview = async (page: Page): Promise<void> => {
    await expect(page.locator("svg.diagram")).toBeVisible();
    await expect(page.locator("article.card").first()).toBeVisible();
};

const captureSimulatorPages = async (page: Page): Promise<void> => {
    await page.goto(H2_PANEL);
    await waitForOverview(page);
    await capturePageView(page, "overview-h2", { tall: true });

    await page.goto(`${SIMULATOR_PANEL}/`);
    await waitForOverview(page);
    await openSimulatorView(page, "faults");
    await page.locator(FAULT_SEARCH).fill("Fan 1");
    const fault = page.getByRole("switch", { name: SIMULATOR_FAULT });
    await fault.check({ force: true });
    await expect(fault).toBeChecked();
    await page.locator(FAULT_SEARCH).fill("");
    await expect(page.locator(".toast")).toHaveCount(0, { timeout: 15_000 });

    await openSimulatorView(page, "overview");
    await expect(page.locator("article.card.faulted")).toHaveCount(1);
    await expect(
        page.locator("article.card.faulted .mark.fault"),
    ).toBeVisible();
    await expect(page.locator("header.statusbar .chip").first()).toBeVisible();
    await capturePageView(page, "overview", { tall: true });
    await capture(
        `${SIMULATOR_PREFIX}-status-bar`,
        page.locator("header.statusbar"),
    );
    await capture(
        `${SIMULATOR_PREFIX}-equipment-card`,
        page.locator("article.card.faulted"),
        { tall: true },
    );

    for (const view of SIMULATOR_VIEWS) {
        await openSimulatorView(page, view);
        if (view === "faults") {
            await page.locator(FAULT_SEARCH).fill("Fan");
            await expect(
                page.getByRole("switch", { name: SIMULATOR_FAULT }),
            ).toBeChecked();
        }
        if (view === "registers") {
            await expect(
                page.locator("section.view:visible .registers-row").nth(1),
            ).toBeVisible();
        }
        if (view === "traffic") {
            await expect(
                page
                    .locator("section.view:visible .row.log-row.error-row")
                    .first(),
            ).toBeVisible();
        }
        await capturePageView(page, view);
    }

    await openSimulatorView(page, "traffic");
    // The log is the last card of the traffic view, and Errors only is the
    // first switch of the log's toolbar.
    const log = page.locator("section.view:visible .card").last();
    await log.getByRole("switch").first().check({ force: true });
    await log.locator(".row.log-row.error-row").first().click();
    await expect(log.locator(".log-detail")).toBeVisible();
    await capture(`${SIMULATOR_PREFIX}-traffic-log-detail`, log);
};

const weekdaysTile = (entity: string): DashboardElement => ({
    tag: "hui-tile-card",
    config: {
        type: "tile",
        entity,
        features: [{ type: "custom:saj-local-weekdays-feature" }],
    },
});

test("takes every documentation screenshot", async ({
    page,
    request,
    baseURL,
}) => {
    test.setTimeout(1_500_000);
    expect(baseURL).toBeDefined();
    await completeOnboarding(request, baseURL ?? "");
    await logIn(page);
    await selectUserLanguage(page);

    // Without a country Home Assistant raises a repair of its own. The server
    // language names the entities, so it is set before SAJ Local is set up.
    await hassWebSocket(page, {
        type: "config/core/update",
        country: "GB",
        language: locale,
    });
    await addHs3(page);
    await addH2(page);
    await waitForSolarPower(page);
    await expectEntityNamesInLanguage(page);

    const hs3Entry = await entryIdOf(page, "");
    const h2Entry = await entryIdOf(page, H2_PREFIX);
    const tile = weekdaysTile(entityId("number", "charge_slot_1_days"));
    await addDashboard(page, "hs3", await deviceOf(page, "HS3"), [tile.config]);
    await addDashboard(page, "h2", await deviceOf(page, "H2"), []);

    await captureCards(page, "hs3", {
        "cards-controls-card-locked": "saj-local-controls-card",
    });
    await capturePollingGroup(page);
    await captureConfigureForms(page);
    await allowControlThroughForm(page);
    await allowControlThroughApi(page, h2Entry);
    await waitForControlEntities(page);

    await setNumber(page, entityId("number", "charge_slot_1_days"), 31);
    await captureCards(page, "hs3", {
        "cards-power-flow-card": "saj-local-power-flow-card",
        "cards-status-card": "saj-local-status-card",
        "cards-faults-card": "saj-local-faults-card",
        "cards-battery-card": "saj-local-battery-card",
        "cards-controls-card": "saj-local-controls-card",
        "cards-schedule-card": "saj-local-schedule-card",
        "cards-status-badge": "saj-local-status-badge",
        "cards-weekdays-feature": tile.tag,
    });
    await captureCards(page, "h2", {
        "cards-power-flow-card-h2": "saj-local-power-flow-card",
        "cards-battery-card-h2": "saj-local-battery-card",
        "cards-controls-card-h2": "saj-local-controls-card",
        "cards-schedule-card-h2": "saj-local-schedule-card",
    });
    await capturePowerSchedule(page);
    await captureDiagnostics(page);
    await captureRepair(page, request, hs3Entry);
    await captureSimulatorPages(page);

    mkdirSync(imageDirectory, { recursive: true });
    for (const [name, image] of screenshots) {
        writeFileSync(resolve(imageDirectory, `${name}.png`), image);
    }
});
