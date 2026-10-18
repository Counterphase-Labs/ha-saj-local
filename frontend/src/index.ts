import { whenHomeAssistantIsReady } from "./home-assistant";

void whenHomeAssistantIsReady().then(() =>
    Promise.all([
        import("./badges/status-badge"),
        import("./cards/battery-card"),
        import("./cards/faults-card"),
        import("./cards/power-flow-card"),
        import("./cards/status-card"),
        import("./cards/controls-card"),
        import("./cards/schedule-card"),
        import("./features/weekdays-feature"),
    ]),
);
