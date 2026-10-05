import { resolve } from "node:path";

import { defineConfig } from "vitest/config";

export default defineConfig({
    build: {
        emptyOutDir: true,
        lib: {
            entry: resolve(import.meta.dirname, "src/card.ts"),
            formats: ["es"],
        },
        manifest: "asset-manifest.json",
        outDir: resolve(
            import.meta.dirname,
            "../custom_components/saj_modbus/frontend",
        ),
        rollupOptions: {
            output: {
                entryFileNames: "saj-modbus-card-[hash].js",
            },
        },
    },
    test: {
        environment: "jsdom",
        include: ["tests/**/*.test.ts"],
        coverage: {
            enabled: true,
            provider: "v8",
            include: ["src/**/*.ts"],
            reporter: ["text"],
            thresholds: {
                lines: 100,
                functions: 100,
                statements: 100,
                branches: 100,
            },
        },
    },
});
