import { defineConfig } from "@playwright/test";

export default defineConfig({
    testDir: "tests/browser/home-assistant",
    fullyParallel: false,
    forbidOnly: true,
    outputDir: "test-results/home-assistant",
    reporter: [
        ["list"],
        [
            "html",
            { open: "never", outputFolder: "playwright-report/home-assistant" },
        ],
    ],
    timeout: 120_000,
    expect: { timeout: 15_000 },
    use: {
        baseURL: process.env.HOME_ASSISTANT_URL ?? "http://homeassistant:8123",
        browserName: "chromium",
        headless: true,
        actionTimeout: 15_000,
        navigationTimeout: 30_000,
        screenshot: "only-on-failure",
        trace: "retain-on-failure",
    },
});
