import { resolve } from "node:path";

import { defineConfig } from "vitest/config";

export default defineConfig({
    build: {
        emptyOutDir: true,
        lib: {
            entry: resolve(import.meta.dirname, "src/index.ts"),
            formats: ["es"],
        },
        manifest: "asset-manifest.json",
        outDir: resolve(
            import.meta.dirname,
            "../custom_components/saj_local/frontend",
        ),
        rollupOptions: {
            output: {
                entryFileNames: "saj-local-[hash].js",
                inlineDynamicImports: true,
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
