import { readdirSync } from "node:fs";
import { resolve } from "node:path";

import { expect, test } from "../support/test";

const assetDirectory = resolve(
    import.meta.dirname,
    "../../../../custom_components/saj_local/frontend",
);

const DEVICE_ID = "saj_system";
const WEEKDAYS_ENTITY_ID = "number.saj_charge_slot_1_days";

interface EntitySpec {
    key: string;
    domain: string;
    state: string;
    attributes?: Record<string, unknown>;
}

const entity = (
    key: string,
    domain: string,
    state: string,
    attributes: Record<string, unknown> = {},
): EntitySpec => ({ key, domain, state, attributes });

const SYSTEM_ENTITIES: readonly EntitySpec[] = [
    entity("pv_power", "sensor", "3500", { unit_of_measurement: "W" }),
    entity("battery_power", "sensor", "-800", { unit_of_measurement: "W" }),
    entity("battery_soc", "sensor", "64", { unit_of_measurement: "%" }),
    entity("battery_voltage", "sensor", "51.2", { unit_of_measurement: "V" }),
    entity("grid_power", "sensor", "-2000", { unit_of_measurement: "W" }),
    entity("load_power", "sensor", "1500", { unit_of_measurement: "W" }),
    entity("operating_mode", "sensor", "operating"),
    entity("pv_energy_today", "sensor", "12.4", {
        unit_of_measurement: "kWh",
    }),
    entity("control_allowed", "binary_sensor", "on"),
    entity("inverter_fault", "binary_sensor", "on"),
    entity("inverter_fault_dc_overvoltage", "binary_sensor", "on"),
    entity("backup_reserve_soc", "number", "20", {
        min: 0,
        max: 100,
        step: 1,
        mode: "box",
        unit_of_measurement: "%",
    }),
    entity("charge_slot_1_start", "time", "08:00:00"),
    entity("charge_slot_1_end", "time", "10:30:00"),
    entity("charge_slot_1_days", "number", "21", {
        min: 0,
        max: 127,
        step: 1,
    }),
    entity("charge_slot_1_power", "number", "1000", {
        unit_of_measurement: "W",
    }),
    entity("charge_slot_1_enabled", "switch", "on"),
];

const bundleAsset = (): string => {
    const filename = readdirSync(assetDirectory).find(
        (candidate) =>
            candidate.startsWith("saj-local-") && candidate.endsWith(".js"),
    );
    if (filename === undefined) {
        throw new Error("Built bundle was not found");
    }
    return resolve(assetDirectory, filename);
};

test.beforeEach(async ({ page }) => {
    await page.goto("about:blank");
    await page.evaluate(() => {
        customElements.define("home-assistant", class extends HTMLElement {});
    });
    await page.addScriptTag({ path: bundleAsset(), type: "module" });
    await page.waitForFunction(() =>
        customElements.get("saj-local-power-flow-card"),
    );
    await page.evaluate(
        ({ entities, deviceId, weekdaysEntityId }) => {
            const states: Record<string, unknown> = {};
            const registry: Record<string, unknown> = {};
            for (const spec of entities) {
                const entityId = `${spec.domain}.saj_${spec.key}`;
                states[entityId] = {
                    entity_id: entityId,
                    state: spec.state,
                    attributes: spec.attributes ?? {},
                    last_changed: "2026-10-17T10:00:00+00:00",
                };
                registry[entityId] = {
                    entity_id: entityId,
                    device_id: deviceId,
                    platform: "saj_local",
                    translation_key: spec.key,
                };
            }
            interface FakeState {
                entity_id: string;
                state: string;
                attributes: { unit_of_measurement?: string };
            }
            const hass = {
                states,
                entities: registry,
                devices: {
                    [deviceId]: {
                        id: deviceId,
                        name: "SAJ",
                        model: "HS3 (12000 W)",
                    },
                },
                language: "en",
                locale: { language: "en", first_weekday: "monday" },
                callService: () => Promise.resolve(),
                localize: (key: string) => key,
                loadBackendTranslation: () =>
                    Promise.resolve((key: string) => key),
                formatEntityState: (stateObject: FakeState, state?: string) =>
                    `${state ?? stateObject.state}${
                        stateObject.attributes.unit_of_measurement === undefined
                            ? ""
                            : ` ${stateObject.attributes.unit_of_measurement}`
                    }`,
                formatEntityName: (stateObject: FakeState) =>
                    stateObject.entity_id.split(".saj_")[1] ?? "",
            };
            const mountElement = (
                tag: string,
                setup: (element: HTMLElement) => void,
            ): void => {
                const element = document.createElement(tag);
                setup(element);
                document.body.append(element);
            };
            const configured = (tag: string): void => {
                mountElement(tag, (element) => {
                    Object.assign(element, { hass });
                    (
                        element as HTMLElement & {
                            setConfig: (config: object) => void;
                        }
                    ).setConfig({ type: `custom:${tag}`, device: deviceId });
                });
            };
            for (const tag of [
                "saj-local-power-flow-card",
                "saj-local-status-card",
                "saj-local-faults-card",
                "saj-local-battery-card",
                "saj-local-controls-card",
                "saj-local-schedule-card",
                "saj-local-status-badge",
            ]) {
                configured(tag);
            }
            mountElement("saj-local-weekdays", (element) => {
                Object.assign(element, {
                    hass,
                    context: { entity_id: weekdaysEntityId },
                });
            });
        },
        {
            entities: SYSTEM_ENTITIES,
            deviceId: DEVICE_ID,
            weekdaysEntityId: WEEKDAYS_ENTITY_ID,
        },
    );
});

test("the power flow card shows the solar power", async ({ page }) => {
    await expect(
        page.locator("saj-local-power-flow-card text.value", {
            hasText: "3500 W",
        }),
    ).toBeVisible();
});

test("the status card shows the operating state", async ({ page }) => {
    await expect(
        page
            .locator("saj-local-status-card saj-value-row")
            .getByText("operating", { exact: true }),
    ).toBeVisible();
});

test("the faults card shows the active fault", async ({ page }) => {
    await expect(
        page
            .locator("saj-local-faults-card saj-value-row")
            .getByText("inverter_fault_dc_overvoltage"),
    ).toBeVisible();
});

test("the battery card shows the state of charge", async ({ page }) => {
    await expect(
        page.locator("saj-local-battery-card saj-ring-gauge").getByText("64 %"),
    ).toBeVisible();
});

test("the controls card shows the backup reserve", async ({ page }) => {
    await expect(
        page.locator("saj-local-controls-card input[type=number]"),
    ).toHaveValue("20");
});

test("the schedule card shows the charge slot times", async ({ page }) => {
    await expect(
        page
            .locator("saj-local-schedule-card .slot-detail")
            .getByText("08:00:00 - 10:30:00"),
    ).toBeVisible();
});

test("the weekdays feature presses the days of the slot", async ({ page }) => {
    const feature = page.locator("saj-local-weekdays");

    await expect(
        feature.getByRole("button", { name: "Wednesday", pressed: true }),
    ).toBeVisible();
    await expect(
        feature.getByRole("button", { name: "Tuesday", pressed: false }),
    ).toBeVisible();
});

test("the status badge shows the operating state", async ({ page }) => {
    await expect(page.locator("saj-local-status-badge .state")).toHaveText(
        "operating",
    );
});
