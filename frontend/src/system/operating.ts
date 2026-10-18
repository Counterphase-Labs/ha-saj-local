export type Tone =
    "primary" | "secondary" | "disabled" | "warning" | "error" | "success";

const OPERATING_TONES = new Map<string, Tone>(
    Object.entries({
        operating: "primary",
        off_grid: "warning",
        grid_connected_load_bypass: "warning",
        fault: "error",
        initialisation: "secondary",
        standby: "secondary",
        upgrade: "secondary",
        debugging: "secondary",
        self_check: "secondary",
        reset: "secondary",
    } satisfies Record<string, Tone>),
);

export const operatingTone = (state: string | undefined): Tone =>
    OPERATING_TONES.get(state ?? "") ?? "disabled";
