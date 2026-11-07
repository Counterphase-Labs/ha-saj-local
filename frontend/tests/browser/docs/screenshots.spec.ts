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
const H2_PANEL = "http://mock-h2:8080";
// The inverter temperature is one register of the HS3 realtime block, so
// refusing it leaves every other reading of the system answering.
const REFUSED_KEY = "inverter_temperature";
const REFUSED_REGISTER = 0x4010;
const ILLEGAL_ADDRESS = 2;
const REFUSED_INTERVAL_SECONDS = 10;
const REPAIR_ISSUE_AGE_SECONDS = 5;
const MILLISECONDS = 1000;
const FIXED_CLIENT_ADDRESS_PREFIX = "192.168.1.";
const FIXED_CLIENT_FIRST_HOST = 20;
const FIXED_CLIENT_PORT = 50_000;
const KEPT_ENTRIES = 60;
const HOLDING = 3;
const INPUT = 4;
const NEWEST_ENTRY_AGE_SECONDS = 2;
const ENTRY_SPACING_SECONDS = 1;
const REQUEST_DURATION_MS = 30;
const LAST_REQUEST_AGE_SECONDS = 2;
const LAST_READ_AGE_SECONDS = 20;
const CONNECTED_AGE_SECONDS = 600;
const REQUESTS_LAST_10_SECONDS = 2;
const REQUESTS_LAST_60_SECONDS = 14;
const REGISTERS_LAST_60_SECONDS = 700;
const PEAK_REQUESTS_PER_60_SECONDS = 28;
const ANSWERED_PER_PERIOD = 14;
const EXCEPTIONS_PER_PERIOD = 1;
const HISTORY_SECONDS = 30 * 60;

interface PollRequest {
    function: number;
    start: number;
    count: number;
}

const POLL_CYCLE: readonly PollRequest[] = [
    { function: INPUT, start: 0x309d, count: 18 },
    { function: HOLDING, start: 0x3644, count: 14 },
    { function: HOLDING, start: 0x4004, count: 13 },
    { function: HOLDING, start: 0x4010, count: 1 },
    { function: HOLDING, start: 0x4031, count: 15 },
    { function: HOLDING, start: 0x4059, count: 30 },
    { function: HOLDING, start: 0x4090, count: 26 },
    { function: HOLDING, start: 0x40bf, count: 24 },
    { function: HOLDING, start: 0x40df, count: 16 },
    { function: HOLDING, start: 0x4167, count: 16 },
    { function: HOLDING, start: 0x4204, count: 12 },
    { function: HOLDING, start: 0x4b12, count: 1 },
    { function: HOLDING, start: 0x8f00, count: 2 },
    { function: HOLDING, start: 0x8f03, count: 10 },
    { function: HOLDING, start: 0xa002, count: 2 },
    { function: HOLDING, start: 0xa03f, count: 30 },
    { function: HOLDING, start: 0xa062, count: 1 },
];

interface FlowResult {
    type: string;
    flow_id: string;
    step_id?: string;
    reason?: string;
    errors?: Record<string, string> | null;
}

interface StoppedReadings {
    hs3: number;
    h2: number;
}

interface SimulatorState {
    time: string;
    readings: { label: string; value: number | string }[];
}

interface TrafficEntry {
    sequence: number;
    at: number;
    client: string;
    port: number;
    kind: string;
    connection: number;
    event?: string;
    operation?: string;
    function?: number;
    start?: number;
    count?: number;
    answer?: string;
    exception_code?: number | null;
    detail?: { words: number[] };
    duration_ms?: number;
    transaction_id?: number;
    late_duplicate?: boolean;
}

interface ClientCounters {
    connections_opened: number;
    connections_closed: number;
    connections_refused: number;
    requests: number;
    reads: number;
    writes: number;
    registers_read: number;
    registers_written: number;
    exceptions: Record<string, number>;
    no_answers: number;
    dropped_connections: number;
    last_request_at: number | null;
    requests_last_10_seconds: number;
    requests_last_60_seconds: number;
    registers_last_60_seconds: number;
    peak_requests_per_60_seconds: number;
}

interface ConnectedClient {
    connection: number;
    client: string;
    port: number;
    since: number;
}

interface HistoryBucket {
    start: number;
    answered: number;
    exception: number;
    unanswered: number;
}

interface SimulatorTraffic {
    entries: TrafficEntry[];
    latest: number;
    now: number;
    counters: {
        total: ClientCounters;
        clients: Record<string, ClientCounters>;
        connected: ConnectedClient[];
    };
    history: {
        bucket_seconds: number;
        total: HistoryBucket[];
        clients: Record<string, HistoryBucket[]>;
    };
}

interface SimulatorRegisters {
    blocks: { fields: { last_read: number | null }[] }[];
}

interface RepairIssue {
    domain: string;
    translation_key: string;
    created: string;
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

const waitForHass = (page: Page): Promise<unknown> =>
    page.waitForFunction(() => {
        const home = document.querySelector("home-assistant") as unknown as {
            hass?: { language?: string; states?: object };
        } | null;
        return Boolean(home?.hass?.language && home.hass.states);
    });

const hassApi = async (
    page: Page,
    method: string,
    path: string,
    body?: Record<string, unknown>,
): Promise<unknown> => {
    await waitForHass(page);
    return page.evaluate(
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
};

const hassWebSocket = async (
    page: Page,
    message: Record<string, unknown>,
): Promise<unknown> => {
    await waitForHass(page);
    return page.evaluate(
        (wsMessage) =>
            (
                document.querySelector("home-assistant") as unknown as {
                    hass: HassConnection;
                }
            ).hass.callWS(wsMessage),
        message,
    );
};

const hassState = async (
    page: Page,
    entityId: string,
): Promise<string | undefined> => {
    await waitForHass(page);
    return page.evaluate(
        (id) =>
            (
                document.querySelector("home-assistant") as unknown as {
                    hass: HassConnection;
                }
            ).hass.states[id]?.state,
        entityId,
    );
};

const hassLanguage = async (page: Page): Promise<string> => {
    await waitForHass(page);
    return page.evaluate(
        () =>
            (
                document.querySelector("home-assistant") as unknown as {
                    hass: HassConnection;
                }
            ).hass.language,
    );
};

// The text of a Home Assistant control that has only its text, read from the
// running Home Assistant in the user's language. A renamed key is fixed here.
const localized = async (page: Page, key: string): Promise<string> => {
    await waitForHass(page);
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

const releasePointer = async (page: Page): Promise<void> => {
    await page.mouse.move(-1, -1);
    await waitForTwoFrames(page);
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
    await releasePointer(page);
    screenshots.set(name, await target.screenshot({ animations: "disabled" }));
    if (tall) {
        await page.setViewportSize(VIEWPORT);
    }
};

const waitForSettledHeight = async (target: Locator): Promise<void> => {
    let previous = -1;
    await expect
        .poll(
            async () => {
                const height = (await target.boundingBox())?.height ?? 0;
                const settled = height > 0 && height === previous;
                previous = height;
                return settled;
            },
            {
                message: "The opened section kept changing its height",
                intervals: [250],
            },
        )
        .toBe(true);
};

const SCROLL_END_READS = 4;

const scrollAncestorsToEnd = (target: Locator): Promise<boolean> =>
    target.evaluate((node) => {
        let atEnd = true;
        let current: Node | null = node;
        while (current !== null) {
            if (
                current instanceof HTMLElement &&
                current.scrollHeight > current.clientHeight &&
                ["auto", "scroll"].includes(getComputedStyle(current).overflowY)
            ) {
                current.scrollTop = current.scrollHeight;
                atEnd =
                    atEnd &&
                    current.scrollTop + current.clientHeight >=
                        current.scrollHeight - 1;
            }
            const slot: HTMLSlotElement | null =
                current instanceof Element ? current.assignedSlot : null;
            if (slot === null) {
                current =
                    current.parentNode instanceof ShadowRoot
                        ? current.parentNode.host
                        : current.parentNode;
            } else {
                current = slot;
            }
        }
        return atEnd;
    });

const scrollToEnd = async (target: Locator): Promise<void> => {
    let reads = 0;
    await expect
        .poll(
            async () => {
                reads = (await scrollAncestorsToEnd(target)) ? reads + 1 : 0;
                return reads >= SCROLL_END_READS;
            },
            {
                message: "The dialog did not stay at the end of its form",
                intervals: [250],
            },
        )
        .toBe(true);
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

const showsSolarPower = async (
    page: Page,
    entity: string,
    watts: number,
): Promise<boolean> => {
    if (!(await hasReading(page, entity))) {
        return false;
    }
    const shown = Number(await hassState(page, entity));
    return Math.abs(shown - watts) < 1;
};

const waitForSolarPower = async (
    page: Page,
    stopped: StoppedReadings,
): Promise<void> => {
    await expect
        .poll(
            async () =>
                (await showsSolarPower(
                    page,
                    entityId("sensor", "pv_power"),
                    stopped.hs3,
                )) &&
                (await showsSolarPower(
                    page,
                    entityId("sensor", "pv_power", H2_PREFIX),
                    stopped.h2,
                )),
            {
                message:
                    "Home Assistant did not show the solar power of the stopped HS3 and H2 simulators within two minutes",
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
    const equipment = flowForm(page).locator("ha-expansion-panel").first();
    await equipment.click();
    await expect(equipment.locator('[aria-expanded="true"]')).toBeVisible();
    await page.setViewportSize(TALL_VIEWPORT);
    await waitForTwoFrames(page);
    await waitForSettledHeight(equipment);
    await releasePointer(page);
    await scrollToEnd(equipment);
    await capture("optional-equipment-equipment-section", flowDialog(page));
    await page.setViewportSize(VIEWPORT);
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

const pickSystem = async (page: Page): Promise<void> => {
    const system = page
        .locator("dialog-pick-config-entry")
        .getByText(HS3_TITLE, { exact: true });
    await expect(system).toBeVisible();
    await waitForTwoFrames(page);
    await system.click();
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
    await pickSystem(page);
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
    await pickSystem(page);
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
    let created = "";
    await expect
        .poll(
            async () => {
                const { issues } = (await hassWebSocket(page, {
                    type: "repairs/list_issues",
                })) as { issues: RepairIssue[] };
                created =
                    issues.find(
                        (issue) =>
                            issue.domain === "saj_local" &&
                            issue.translation_key === "registers_refused",
                    )?.created ?? "";
                return created !== "";
            },
            {
                message: "SAJ Local repair issue registers_refused is missing",
                timeout: ISSUE_TIMEOUT_MS,
                intervals: [5000],
            },
        )
        .toBe(true);
    await page.clock.setFixedTime(
        Date.parse(created) + REPAIR_ISSUE_AGE_SECONDS * MILLISECONDS,
    );
    await page.goto("/config/repairs");
    await capture(
        "faults-and-repairs-repair-issue",
        // The title of the issue names the installation.
        page.getByRole("listitem").filter({ hasText: HS3_TITLE }),
    );
};

const SIMULATOR_PREFIX = "developer-simulator-page";
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
const NO_TRANSITIONS =
    "*, *::before, *::after { transition: none !important; }";
const FAULT_SEARCH = "section.view:visible input[type=search]";

const waitForIcons = async (page: Page): Promise<void> => {
    await page.waitForFunction(
        () =>
            document.querySelectorAll("span.icon:empty, svg.diagram g:empty")
                .length === 0,
    );
};

const captureSimulatorPart = async (
    name: string,
    target: Locator,
    { tall = false }: { tall?: boolean } = {},
): Promise<void> => {
    await waitForIcons(target.page());
    await capture(name, target, { tall });
};

const capturePageView = async (
    page: Page,
    name: string,
    { tall = false }: { tall?: boolean } = {},
): Promise<void> => {
    await waitForIcons(page);
    await page.setViewportSize(tall ? TALL_VIEWPORT : VIEWPORT);
    await waitForTwoFrames(page);
    await releasePointer(page);
    screenshots.set(
        `${SIMULATOR_PREFIX}-${name}`,
        await page.screenshot({
            animations: "disabled",
            style: NO_TRANSITIONS,
        }),
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

const simulatorGet = async <T>(
    request: APIRequestContext,
    panel: string,
    path: string,
): Promise<T> => {
    const response = await request.get(`${panel}${path}`);
    expect(
        response.ok(),
        `GET ${panel}${path} failed with ${String(response.status())}: ${await response.text()}`,
    ).toBe(true);
    return (await response.json()) as T;
};

const fixedClientCounters = (
    entries: TrafficEntry[],
    now: number,
): ClientCounters => {
    const counters: ClientCounters = {
        connections_opened: 0,
        connections_closed: 0,
        connections_refused: 0,
        requests: 0,
        reads: 0,
        writes: 0,
        registers_read: 0,
        registers_written: 0,
        exceptions: {},
        no_answers: 0,
        dropped_connections: 0,
        requests_last_10_seconds: REQUESTS_LAST_10_SECONDS,
        requests_last_60_seconds: REQUESTS_LAST_60_SECONDS,
        registers_last_60_seconds: REGISTERS_LAST_60_SECONDS,
        peak_requests_per_60_seconds: PEAK_REQUESTS_PER_60_SECONDS,
        last_request_at: now - LAST_REQUEST_AGE_SECONDS,
    };
    for (const entry of entries) {
        if (entry.kind === "connection") {
            if (entry.event === "opened") {
                counters.connections_opened += 1;
            } else if (entry.event === "refused") {
                counters.connections_refused += 1;
            } else {
                counters.connections_closed += 1;
            }
            continue;
        }
        counters.requests += 1;
        const words =
            entry.answer === "answered" ? (entry.detail?.words.length ?? 0) : 0;
        if (entry.operation === "read") {
            counters.reads += 1;
            counters.registers_read += words;
        } else if (entry.operation === "write") {
            counters.writes += 1;
            counters.registers_written += words;
        }
        if (
            entry.exception_code !== null &&
            entry.exception_code !== undefined
        ) {
            const code = String(entry.exception_code);
            counters.exceptions[code] = (counters.exceptions[code] ?? 0) + 1;
        }
        if (entry.answer === "no_answer" || entry.answer === "ignored") {
            counters.no_answers += 1;
        }
        if (entry.answer === "dropped") {
            counters.dropped_connections += 1;
        }
    }
    return counters;
};

const fixedHistory = (now: number, bucketSeconds: number): HistoryBucket[] => {
    const newestStart = Math.floor(now / bucketSeconds) * bucketSeconds;
    const periods = HISTORY_SECONDS / bucketSeconds;
    return Array.from({ length: periods }, (_, index) => ({
        start: newestStart - (periods - 1 - index) * bucketSeconds,
        answered: ANSWERED_PER_PERIOD,
        exception: EXCEPTIONS_PER_PERIOD,
        unanswered: 0,
    }));
};

const realRequestLines = (requests: TrafficEntry[]): string => {
    const occurrences = new Map<string, number>();
    for (const entry of requests) {
        const line = `function ${String(entry.function)}, start address ${String(entry.start)}, count ${String(entry.count)}`;
        occurrences.set(line, (occurrences.get(line) ?? 0) + 1);
    }
    return [...occurrences]
        .map(([line, times]) => `${line}: ${String(times)} times`)
        .join("\n");
};

const fixedPollCycle = (real: SimulatorTraffic): TrafficEntry[] => {
    const requests = real.entries
        .filter((entry) => entry.kind === "request")
        .sort((first, second) => second.sequence - first.sequence);
    return POLL_CYCLE.map((wanted) => {
        const entry = requests.find(
            (candidate) =>
                candidate.function === wanted.function &&
                candidate.start === wanted.start &&
                candidate.count === wanted.count,
        );
        if (entry === undefined) {
            throw new Error(
                `The traffic log holds no request with function ${String(wanted.function)}, start address ${String(wanted.start)} and count ${String(wanted.count)}. The traffic log holds these requests:\n${realRequestLines(requests)}`,
            );
        }
        return entry;
    });
};

const fixedTraffic = (
    real: SimulatorTraffic,
    now: number,
    withCycle: boolean,
): SimulatorTraffic => {
    const address = `${FIXED_CLIENT_ADDRESS_PREFIX}${String(FIXED_CLIENT_FIRST_HOST)}`;
    const cycle = withCycle ? fixedPollCycle(real) : [];
    const repeated: TrafficEntry[] = [];
    while (cycle.length > 0 && repeated.length < KEPT_ENTRIES) {
        repeated.push(...cycle);
    }
    const entries = repeated.slice(0, KEPT_ENTRIES).map((entry, index) => ({
        ...entry,
        sequence: index + 1,
        at:
            now -
            NEWEST_ENTRY_AGE_SECONDS -
            (KEPT_ENTRIES - 1 - index) * ENTRY_SPACING_SECONDS,
        client: address,
        port: FIXED_CLIENT_PORT,
        connection: Math.floor(index / cycle.length) + 1,
        transaction_id: (index % cycle.length) + 1,
        late_duplicate: false,
        duration_ms: REQUEST_DURATION_MS,
    }));
    const newestConnection = entries.at(-1)?.connection ?? 1;
    const counters = fixedClientCounters(entries, now);
    const history = fixedHistory(now, real.history.bucket_seconds);
    return {
        ...real,
        now,
        latest: KEPT_ENTRIES,
        entries,
        counters: {
            total: counters,
            clients: { [address]: counters },
            connected: [
                {
                    connection: newestConnection,
                    client: address,
                    port: FIXED_CLIENT_PORT,
                    since: now - CONNECTED_AGE_SECONDS,
                },
            ],
        },
        history: {
            bucket_seconds: real.history.bucket_seconds,
            total: history,
            clients: { [address]: history },
        },
    };
};

const fixedRegisters = (
    real: SimulatorRegisters,
    now: number,
): SimulatorRegisters => ({
    ...real,
    blocks: real.blocks.map((block) => ({
        ...block,
        fields: block.fields.map((field) => ({
            ...field,
            last_read:
                field.last_read === null ? null : now - LAST_READ_AGE_SECONDS,
        })),
    })),
});

const routeSimulatorData = async (
    page: Page,
    panel: string,
    path: string,
    body: (url: URL) => unknown,
): Promise<void> => {
    const origin = new URL(panel).origin;
    await page.route(
        (url) => url.origin === origin && url.pathname === path,
        (route) => {
            if (route.request().method() !== "GET") {
                return route.fallback();
            }
            return route.fulfill({
                json: body(new URL(route.request().url())),
            });
        },
    );
};

const freezeSimulatorPage = async (
    page: Page,
    request: APIRequestContext,
    panel: string,
    withCycle: boolean,
): Promise<void> => {
    const state = await simulatorGet<SimulatorState>(
        request,
        panel,
        "/api/state",
    );
    const traffic = await simulatorGet<SimulatorTraffic>(
        request,
        panel,
        "/api/traffic?after=0",
    );
    const registers = await simulatorGet<SimulatorRegisters>(
        request,
        panel,
        "/api/registers",
    );
    const now = new Date(state.time).getTime() / MILLISECONDS;
    const frozenTraffic = fixedTraffic(traffic, now, withCycle);
    const frozenRegisters = fixedRegisters(registers, now);
    await page.clock.setFixedTime(now * MILLISECONDS);
    await page.emulateMedia({ reducedMotion: "reduce" });
    await routeSimulatorData(page, panel, "/api/state", () => state);
    await routeSimulatorData(
        page,
        panel,
        "/api/registers",
        () => frozenRegisters,
    );
    await routeSimulatorData(page, panel, "/api/traffic", (url) => {
        const after = Number(url.searchParams.get("after") ?? 0);
        return {
            ...frozenTraffic,
            entries: frozenTraffic.entries.filter(
                (entry) => entry.sequence > after,
            ),
        };
    });
};

const captureSimulatorPages = async (
    page: Page,
    request: APIRequestContext,
): Promise<void> => {
    await freezeSimulatorPage(page, request, H2_PANEL, false);
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

    await freezeSimulatorPage(page, request, SIMULATOR_PANEL, true);
    await page.goto(`${SIMULATOR_PANEL}/`);
    await waitForOverview(page);
    await openSimulatorView(page, "overview");
    await expect(page.locator("article.card.faulted")).toHaveCount(1);
    await expect(
        page.locator("article.card.faulted .mark.fault"),
    ).toBeVisible();
    await expect(page.locator("header.statusbar .chip").first()).toBeVisible();
    await capturePageView(page, "overview", { tall: true });
    await captureSimulatorPart(
        `${SIMULATOR_PREFIX}-status-bar`,
        page.locator("header.statusbar"),
    );
    await captureSimulatorPart(
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
    await captureSimulatorPart(`${SIMULATOR_PREFIX}-traffic-log-detail`, log);
};

const simulatorState = async (
    request: APIRequestContext,
    panel: string,
    path: string,
    body?: Record<string, unknown>,
): Promise<SimulatorState> => {
    const response =
        body === undefined
            ? await request.post(`${panel}${path}`)
            : await request.post(`${panel}${path}`, { data: body });
    expect(
        response.ok(),
        `${panel}${path} was refused: ${await response.text()}`,
    ).toBe(true);
    return (await response.json()) as SimulatorState;
};

const stopSimulator = async (
    request: APIRequestContext,
    panel: string,
): Promise<number> => {
    const scenario = await simulatorState(request, panel, "/api/reset");
    const stopped = await simulatorState(request, panel, "/api/clock", {
        time: scenario.time,
        speed: 0,
    });
    const power = stopped.readings.find(
        (reading) => reading.label === "PV power",
    );
    expect(power, `${panel} reports no PV power`).toBeDefined();
    return Number(power?.value);
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
    const stopped: StoppedReadings = {
        hs3: await stopSimulator(request, SIMULATOR_PANEL),
        h2: await stopSimulator(request, H2_PANEL),
    };
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
    await waitForSolarPower(page, stopped);
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
    await captureSimulatorPages(page, request);

    mkdirSync(imageDirectory, { recursive: true });
    for (const [name, image] of screenshots) {
        writeFileSync(resolve(imageDirectory, `${name}.png`), image);
    }
});
