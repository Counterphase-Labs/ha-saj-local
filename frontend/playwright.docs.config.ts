import { defineConfig } from "@playwright/test";

const locale = process.env.DOCS_LOCALE ?? "en-GB";

export default defineConfig({
    testDir: "tests/browser/docs",
    fullyParallel: false,
    forbidOnly: true,
    outputDir: `test-results/docs/${locale.toLowerCase()}`,
    reporter: [
        ["dot"],
        [
            "html",
            {
                open: "never",
                outputFolder: `playwright-report/docs/${locale.toLowerCase()}`,
            },
        ],
    ],
    timeout: 900_000,
    expect: { timeout: 15_000 },
    use: {
        baseURL: process.env.HOME_ASSISTANT_URL ?? "http://homeassistant:8123",
        browserName: "chromium",
        colorScheme: "light",
        headless: true,
        actionTimeout: 15_000,
        navigationTimeout: 30_000,
        screenshot: "only-on-failure",
        trace: "retain-on-failure",
        viewport: { width: 1280, height: 800 },
    },
});
