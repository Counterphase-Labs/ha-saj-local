import { defineConfig } from "@playwright/test";

export default defineConfig({
    testDir: "tests/browser/controlled",
    fullyParallel: true,
    outputDir: "test-results/controlled",
    reporter: [
        ["list"],
        [
            "html",
            { open: "never", outputFolder: "playwright-report/controlled" },
        ],
    ],
    use: {
        browserName: "chromium",
        headless: true,
        screenshot: "only-on-failure",
        trace: "retain-on-failure",
    },
});
