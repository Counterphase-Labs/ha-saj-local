import { numericValue, type SystemEntity } from "./entities";

export const FLOW_THRESHOLD_WATTS = 10;
export const SLOWEST_FLOW_SECONDS = 6;
export const FASTEST_FLOW_SECONDS = 0.8;
export const FASTEST_FLOW_WATTS = 10000;

export type PowerNodeKind = "solar" | "battery" | "grid" | "consumer";
export type PowerState =
    | "idle"
    | "producing"
    | "consuming"
    | "charging"
    | "discharging"
    | "importing"
    | "exporting";
export type LineDirection = "none" | "to_inverter" | "from_inverter";

export interface PowerFlow {
    state: PowerState;
    line: LineDirection;
}

const IDLE_FLOW: PowerFlow = { state: "idle", line: "none" };

const ACTIVE_FLOWS: Record<
    PowerNodeKind,
    { positive: PowerFlow; negative: PowerFlow }
> = {
    solar: {
        positive: { state: "producing", line: "to_inverter" },
        negative: { state: "producing", line: "to_inverter" },
    },
    battery: {
        positive: { state: "discharging", line: "to_inverter" },
        negative: { state: "charging", line: "from_inverter" },
    },
    grid: {
        positive: { state: "exporting", line: "from_inverter" },
        negative: { state: "importing", line: "to_inverter" },
    },
    consumer: {
        positive: { state: "consuming", line: "from_inverter" },
        negative: { state: "consuming", line: "from_inverter" },
    },
};

export const powerFlow = ({
    kind,
    watts,
}: {
    kind: PowerNodeKind;
    watts: number;
}): PowerFlow => {
    if (Math.abs(watts) <= FLOW_THRESHOLD_WATTS) {
        return IDLE_FLOW;
    }
    const flows = ACTIVE_FLOWS[kind];
    return watts > 0 ? flows.positive : flows.negative;
};

export const flowDurationSeconds = (watts: number): number => {
    const floor = Math.log10(FLOW_THRESHOLD_WATTS);
    const ceiling = Math.log10(FASTEST_FLOW_WATTS);
    const position =
        (Math.log10(Math.max(Math.abs(watts), FLOW_THRESHOLD_WATTS)) - floor) /
        (ceiling - floor);
    const fraction = Math.min(position, 1);
    return Math.max(
        FASTEST_FLOW_SECONDS,
        SLOWEST_FLOW_SECONDS -
            (SLOWEST_FLOW_SECONDS - FASTEST_FLOW_SECONDS) * fraction,
    );
};

const WATTS_PER_UNIT = new Map<string, number>([
    ["W", 1],
    ["kW", 1000],
    ["MW", 1_000_000],
]);

export const wattsOf = (entity: SystemEntity): number | null => {
    const value = numericValue(entity);
    if (value === null) {
        return null;
    }
    const unit = entity.state.attributes.unit_of_measurement;
    const factor = typeof unit === "string" ? WATTS_PER_UNIT.get(unit) : 1;
    return value * (factor ?? 1);
};

export const FLOW_STATE_TEXT_KEYS: Readonly<
    Partial<Record<PowerState, string>>
> = {
    charging: "charging",
    discharging: "discharging",
    importing: "importing",
    exporting: "exporting",
    idle: "idle",
};
