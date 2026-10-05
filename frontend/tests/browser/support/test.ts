import {
    expect,
    test as base,
    type ConsoleMessage,
    type Locator,
    type Page,
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

// Home Assistant's virtualised lists await `layoutComplete` without handling a
// rejection, and reading it on an idle list creates a promise that only a later
// layout resolves. Removing such a list rejects that promise with the string
// "disconnected", which the page reports as an uncaught error. It is expected
// exactly when a list is removed on purpose, so it is accepted only while
// `action` removes `list`; the same error anywhere else still fails the test.
const listTeardownFailure = "page: disconnected";

export const removingVirtualizedList = async (
    page: Page,
    failures: string[],
    list: Locator,
    action: () => Promise<void>,
): Promise<void> => {
    const element = await list.elementHandle();
    const first = failures.length;
    await action();
    await page.waitForFunction((candidate) => !candidate.isConnected, element);
    // Events reach the test in order, so this round trip flushes the rejection.
    await page.evaluate(() => undefined);
    const teardown = failures
        .slice(first)
        .filter((failure) => failure === listTeardownFailure);
    expect(teardown.length).toBeLessThanOrEqual(1);
    for (const failure of teardown) {
        failures.splice(failures.indexOf(failure, first), 1);
    }
};

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
