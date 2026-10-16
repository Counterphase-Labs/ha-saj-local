import { button, dangerButton, errorSlot, send } from "../shared/actions.js";
import { el, whenIdle } from "../shared/dom.js";
import { currentState, description } from "../shared/state.js";

export function createScenario() {
  const presetError = errorSlot();
  const presetCards = description().presets.map((preset) =>
    el(
      "div",
      { class: "card" },
      el("div", {}, el("h3", { text: preset.name }), el("p", { class: "muted", text: preset.description })),
      button({
        label: "Apply",
        iconName: "check",
        title: "Apply " + preset.name,
        onClick: () => send({ path: "/api/presets/" + encodeURIComponent(preset.key), errorSlot: presetError, success: preset.name + " applied" }),
      }),
    ),
  );
  const timeError = errorSlot();
  const time = el("input", { type: "datetime-local", step: 1, "aria-label": "Simulated time" });
  const setTime = button({
    kind: "primary",
    label: "Set time",
    iconName: "clock",
    onClick: () => send({ path: "/api/clock", body: { time: time.value }, errorSlot: timeError, success: "Simulated time set to " + time.value.replace("T", " ") }),
  });
  const resetCounters = dangerButton({
    label: "Reset energy counters",
    iconName: "restore",
    confirmTitle: "Reset energy counters",
    message: "The simulator's energy counters start again from zero.",
    confirmLabel: "Reset counters",
    run: () => send({ path: "/api/ledger/reset", success: "Energy counters reset" }),
  });
  const resetScenario = dangerButton({
    label: "Reset to scenario",
    iconName: "restore",
    confirmTitle: "Reset to scenario",
    message: "Settings, variation, faults, holds and the link return to the scenario. The clock, the energy counters, the battery charge and the car carry on.",
    confirmLabel: "Reset to scenario",
    run: () => send({ path: "/api/reset", success: "Simulator reset to its scenario" }),
  });
  const exportLink = el("a", { class: "button secondary", href: "/api/scenario", download: "scenario.yaml" }, "Export scenario");
  const element = el(
    "section",
    { class: "view" },
    el("h2", { text: "Scenario" }),
    el("div", { class: "card" }, el("h3", { text: "Presets" }), el("p", { class: "muted", text: "A preset returns settings, variation, faults, holds and the link to the scenario, then applies its own changes. Time, energy counters and battery charge carry on." }), presetError),
    el("div", { class: "preset-grid" }, ...presetCards),
    el(
      "div",
      { class: "card" },
      el("h3", { text: "Simulated time (UTC)" }),
      el("div", { class: "toolbar" }, time, setTime),
      timeError,
    ),
    el(
      "div",
      { class: "card" },
      el("h3", { text: "Reset and export" }),
      el("div", { class: "toolbar" }, resetCounters, resetScenario, exportLink),
    ),
  );

  function update() {
    const state = currentState();
    if (state === null) return;
    whenIdle(time, () => {
      time.value = state.time;
    });
  }

  return { element, update, activate: update, deactivate() {} };
}
