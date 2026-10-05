import { readdirSync } from "node:fs";
import { resolve } from "node:path";

import { expect, test } from "../support/test";

const assetDirectory = resolve(
    import.meta.dirname,
    "../../../../custom_components/saj_local/frontend",
);

const cardAsset = (): string => {
    const filename = readdirSync(assetDirectory).find(
        (candidate) =>
            candidate.startsWith("saj-local-card-") &&
            candidate.endsWith(".js"),
    );
    if (filename === undefined) {
        throw new Error("Built card asset was not found");
    }
    return resolve(assetDirectory, filename);
};

test("the built card renders its configured title", async ({ page }) => {
    await page.goto("about:blank");
    await page.addScriptTag({ path: cardAsset(), type: "module" });

    await page.evaluate(async () => {
        await customElements.whenDefined("saj-local-card");
        const card = document.createElement("saj-local-card") as HTMLElement & {
            setConfig(config: { type: string; title: string }): void;
        };
        card.setConfig({ type: "custom:saj-local-card", title: "Inverter" });
        document.body.append(card);
    });

    await expect(page.getByText("Inverter")).toBeVisible();
});
