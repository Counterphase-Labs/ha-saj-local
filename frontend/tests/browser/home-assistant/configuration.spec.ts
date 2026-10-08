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

const callHassWebSocket = async <T>(
    page: Page,
    command: { type: string },
): Promise<T> =>
    page.evaluate(async (message) => {
        interface HassApi {
            callWS: <Result>(command: { type: string }) => Promise<Result>;
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

const expectEntrySensorsReportValues = async (
    page: Page,
    entryCount: number,
): Promise<void> => {
    await expect
        .poll(async () => {
            const registry = await callHassWebSocket<RegistryEntity[]>(page, {
                type: "config/entity_registry/list",
            });
            const states = await callHassWebSocket<EntityState[]>(page, {
                type: "get_states",
            });
            const byEntry = new Map<string, string[]>();
            for (const entity of registry) {
                if (entity.platform === "saj_local" && entity.config_entry_id) {
                    byEntry.set(entity.config_entry_id, [
                        ...(byEntry.get(entity.config_entry_id) ?? []),
                        entity.entity_id,
                    ]);
                }
            }
            return (
                byEntry.size === entryCount &&
                [...byEntry.values()].every(
                    (entityIds) =>
                        entityIds.length === 6 &&
                        entityIds.every((entityId) =>
                            states.some(
                                (state) =>
                                    state.entity_id === entityId &&
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

test("an HS3 and an H2 endpoint load and report sensor values", async ({
    page,
    browserFailures,
}) => {
    await finishOnboarding(page);

    await addIntegration(page, browserFailures, "modbus-mock");
    await expectEntrySensorsReportValues(page, 1);

    await addIntegration(page, browserFailures, "modbus-mock-h2", "h2");
    await expectEntrySensorsReportValues(page, 2);
});
