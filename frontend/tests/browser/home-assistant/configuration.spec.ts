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
    await page.getByRole("button", { name: /submit/i }).click();
    await page.getByRole("button", { name: "Finish" }).click();
};

test("the integration can be added through the user interface", async ({
    page,
    browserFailures,
}) => {
    await finishOnboarding(page);
    await addIntegration(page, browserFailures);

    await expect(
        page.locator("ha-md-list-item").getByText(integrationName),
    ).toBeVisible();
});
