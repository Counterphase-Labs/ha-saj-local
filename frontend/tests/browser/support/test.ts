import {
    expect,
    test as base,
    type ConsoleMessage,
    type Request,
} from "@playwright/test";

const ignoredConsoleMessages = [
    "The AudioContext was not allowed to start",
] as const;

const ignoredRequestHostnames = ["basemaps.cartocdn.com"] as const;

const relevantConsoleError = (message: ConsoleMessage): string | null => {
    if (message.type() !== "error") return null;
    const text = message.text();
    const location = message.location().url;
    return ignoredConsoleMessages.some((ignored) => text.includes(ignored))
        ? null
        : `${text}${location === "" ? "" : ` (${location})`}`;
};

const failedRequest = (request: Request): string =>
    `${request.method()} ${request.url()}: ${request.failure()?.errorText ?? "failed"}`;

const ignoredFailedRequest = (request: Request): boolean =>
    ignoredRequestHostnames.some(
        (hostname) => new URL(request.url()).hostname === hostname,
    );

export const test = base.extend<{ browserFailures: string[] }>({
    browserFailures: [
        async ({ page }, use) => {
            const failures: string[] = [];
            const recordConsoleError = (message: ConsoleMessage): void => {
                const error = relevantConsoleError(message);
                if (error !== null) failures.push(`console: ${error}`);
            };
            const recordPageError = (error: Error): void => {
                failures.push(`page: ${error.message}`);
            };
            const recordFailedRequest = (request: Request): void => {
                if (ignoredFailedRequest(request)) return;
                failures.push(`request: ${failedRequest(request)}`);
            };
            page.on("console", recordConsoleError);
            page.on("pageerror", recordPageError);
            page.on("requestfailed", recordFailedRequest);
            await use(failures);
            expect(failures).toEqual([]);
        },
        { auto: true },
    ],
});

export { expect };
