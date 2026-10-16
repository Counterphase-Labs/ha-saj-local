import { dangerButton, send } from "./actions.js";
import { el, hasFocus } from "./dom.js";
import { activeFaults } from "./faultinfo.js";
import { elapsed, humanise, parseNumber, plural, showTime } from "./format.js";
import { icon } from "./icons.js";
import { go } from "./navigation.js";
import { currentState, description, isAnswering, serverNow, traffic } from "./state.js";

const SPEED_PRESETS = [1, 10, 60];
const DEFAULT_SPEED = 1;

const CHANGE_KINDS = [
  { key: "holds", label: "Holds", view: "overview" },
  { key: "faults", label: "Faults", view: "faults" },
  { key: "settings", label: "Settings", view: "settings" },
  { key: "variation", label: "Variation", view: "overview" },
  { key: "link", label: "Link", view: "link" },
];

let speedBeforePause = null;

function changeCount(changes, key) {
  const value = changes[key];
  if (Array.isArray(value)) return value.length;
  return Object.values(value).reduce((sum, count) => sum + count, 0);
}

function iconSlot() {
  const element = el("span", { class: "status-icon" });
  let current = null;
  return {
    element,
    set(name) {
      if (name === current) return;
      current = name;
      element.replaceChildren(icon(name));
    },
  };
}

function statusButton({ title, onClick }) {
  const slot = iconSlot();
  const text = el("span");
  const element = el("button", { type: "button", class: "plain", title, on: { click: onClick } }, slot.element, text);
  return { element, slot, text };
}

function clientsText() {
  const { counters } = traffic();
  if (counters === null) return "No traffic data";
  const last = counters.total.last_request_at;
  const ago = last === null ? "no requests yet" : elapsed(serverNow() - last);
  return plural(counters.connected.length, "client") + " · " + counters.total.requests_last_60_seconds + "/min · " + ago;
}

function setSpeed(speed) {
  return send({ path: "/api/clock", body: { speed }, success: speed === 0 ? "Clock paused" : "Speed set to " + speed + "×" });
}

function togglePlay() {
  const state = currentState();
  if (state.speed > 0) {
    speedBeforePause = state.speed;
    setSpeed(0);
  } else {
    setSpeed(speedBeforePause || DEFAULT_SPEED);
  }
}

export function createStatusBar() {
  const title = el("h1", { text: "SAJ simulator" });
  const identity = el("span", { class: "muted mono" });
  const simulator = statusButton({ title: "Whether the simulator's panel can be reached", onClick: () => {} });
  simulator.element.disabled = true;
  const module = statusButton({ title: "Open the Link view", onClick: () => go("link") });
  const clients = statusButton({ title: "Open the Traffic view", onClick: () => go("traffic") });
  const time = statusButton({ title: "Open the Scenario view", onClick: () => go("scenario") });
  const run = statusButton({ title: "Pause or resume the simulated clock", onClick: togglePlay });
  run.element.className = "secondary";
  const speedField = el("input", { type: "number", step: "any", "aria-label": "Speed", style: "--chars: 6" });
  speedField.addEventListener("change", () => {
    const speed = parseNumber(speedField.value);
    if (Number.isFinite(speed)) setSpeed(speed);
  });
  const presets = SPEED_PRESETS.map((speed) => ({
    speed,
    element: el("button", { type: "button", class: "secondary", text: speed + "×", on: { click: () => setSpeed(speed) } }),
  }));
  const speed = el(
    "span",
    { class: "status-group" },
    el("span", { class: "label muted", text: "Speed" }),
    ...presets.map((preset) => preset.element),
    speedField,
  );
  const faults = statusButton({ title: "Open the active faults", onClick: () => go("faults", { activeOnly: true }) });
  const chips = el("span", { class: "chips" });
  let chipSignature = null;
  const reset = dangerButton({
    label: "Reset",
    iconName: "restore",
    title: "Reset the simulator to its scenario",
    confirmTitle: "Reset to scenario",
    message: "Settings, variation, faults, holds and the link return to the scenario. The clock, the energy counters, the battery charge and the car carry on.",
    confirmLabel: "Reset to scenario",
    run: () => send({ path: "/api/reset", success: "Simulator reset to its scenario" }),
  });
  const element = el(
    "header",
    { class: "statusbar" },
    title,
    identity,
    simulator.element,
    module.element,
    clients.element,
    time.element,
    run.element,
    speed,
    faults.element,
    chips,
    el("span", { class: "status-spacer" }),
    reset,
  );

  function updateChips(state) {
    const active = CHANGE_KINDS.filter((kind) => changeCount(state.changes, kind.key) > 0);
    const signature = active.map((kind) => kind.key + changeCount(state.changes, kind.key)).join();
    if (signature === chipSignature) return;
    chipSignature = signature;
    if (active.length === 0) {
      chips.replaceChildren(el("span", { class: "muted", text: "Matches the scenario" }));
      return;
    }
    chips.replaceChildren(
      el("span", { class: "muted", text: "Changed" }),
      ...active.map((kind) =>
        el("button", {
          type: "button",
          class: "chip",
          title: "Differs from the scenario: open where it was changed",
          text: kind.label + " " + changeCount(state.changes, kind.key),
          on: { click: () => go(kind.view, { changed: kind.key }) },
        }),
      ),
    );
  }

  function update() {
    const model = description().model;
    identity.textContent = model.name.toUpperCase() + " " + model.rated_power_w + " W · " + model.serial_number;
    const answering = isAnswering();
    simulator.slot.set(answering ? "circle-check" : "alert-circle");
    simulator.text.textContent = answering ? "Simulator answering" : "Simulator not answering";
    simulator.element.className = "plain " + (answering ? "status-good" : "status-bad");
    const state = currentState();
    if (state === null) return;
    const online = state.module.status === "online";
    module.slot.set(online ? "plug-connected" : "plug-connected-x");
    module.text.textContent = "Module " + (online ? "online" : humanise(state.module.status));
    module.element.className = "plain " + (online ? "" : "status-bad");
    clients.slot.set("users");
    clients.text.textContent = clientsText();
    time.slot.set("clock");
    time.text.textContent = showTime(state.time);
    const running = state.speed > 0;
    run.slot.set(running ? "player-pause" : "player-play");
    run.text.textContent = running ? "Pause" : "Play";
    const bounds = description().model.clock.speed_bounds;
    speedField.min = bounds[0];
    speedField.max = bounds[1];
    if (!hasFocus(speedField)) speedField.value = state.speed;
    for (const preset of presets) preset.element.setAttribute("aria-pressed", String(state.speed === preset.speed));
    const faultCount = activeFaults(description(), state).length;
    faults.slot.set("alert-triangle");
    faults.text.textContent = plural(faultCount, "fault");
    faults.element.className = "plain " + (faultCount ? "status-bad" : "");
    updateChips(state);
  }

  return { element, update };
}
