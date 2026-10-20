export default function formatCompact(results) {
    return results
        .flatMap((result) =>
            result.messages.map(
                (message) =>
                    `${result.filePath}:${String(message.line ?? 1)}:${String(message.column ?? 1)} ${message.ruleId ?? "error"} ${message.message}`,
            ),
        )
        .join("\n");
}
