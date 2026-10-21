import { button, changedMark, errorSlot, send, switchControl } from "../shared/actions.js";
import { el, hasFocus, whenIdle } from "../shared/dom.js";
import { hex, humanise, humaniseWithoutUnit, inputChars, parseNumber, showNumber } from "../shared/format.js";
import { currentState, description } from "../shared/state.js";

const PERCENT_STEP = "any";
const WHOLE_STEP = 1;
const PERCENT_CHARS = 6;

function unitText(setting) {
  return setting.unit ? " " + setting.unit : "";
}

function scenarioText(setting) {
  if (setting.kind === "flag") return setting.scenario ? "on" : "off";
  if (setting.kind === "blocks") return setting.scenario.length ? blocksText(setting.scenario) : "none";
  return showNumber(setting.scenario) + unitText(setting);
}

function blocksText(blocks) {
  return blocks.map((block) => hex(block.start) + "–" + hex(block.end) + " → " + block.code).join(", ");
}

function rowShell({ setting, input, errors, mark, reset }) {
  return el(
    "div",
    { class: "control-row" },
    el("div", { class: "control-label" }, el("span", { text: humaniseWithoutUnit(setting.name, setting.unit) }), el("code", { class: "muted", text: setting.name })),
    el("div", { class: "control-input" }, ...input),
    el("div", { class: "control-note" }, el("span", { text: "Scenario " + scenarioText(setting) }), mark, reset, errors),
  );
}

function resetButton(setting, errors) {
  return button({
    label: "Reset " + humanise(setting.name) + " to the scenario value",
    iconName: "restore",
    iconOnly: true,
    onClick: () =>
      send({ path: "/api/link", body: { [setting.name]: setting.scenario }, errorSlot: errors, success: humanise(setting.name) + " reset to " + scenarioText(setting) }),
  });
}

function numberRow(setting) {
  const errors = errorSlot();
  const percent = setting.kind === "percent";
  const field = el("input", {
    type: "number",
    min: setting.minimum,
    max: setting.maximum,
    step: percent ? PERCENT_STEP : WHOLE_STEP,
    style: "--chars: " + (percent ? PERCENT_CHARS : inputChars({ maximum: setting.maximum, step: WHOLE_STEP })),
    "aria-label": humanise(setting.name),
  });
  field.addEventListener("change", () =>
    send({ path: "/api/link", body: { [setting.name]: parseNumber(field.value) }, errorSlot: errors, success: humanise(setting.name) + " set to " + field.value + unitText(setting) }),
  );
  const mark = changedMark();
  const reset = resetButton(setting, errors);
  const element = rowShell({ setting, input: [field, setting.unit ? el("span", { class: "muted", text: setting.unit }) : null], errors, mark, reset });
  return {
    element,
    update(state) {
      const changed = state.changes.link.includes(setting.name);
      mark.hidden = !changed;
      reset.disabled = !changed;
      whenIdle(field, () => {
        field.value = state.link[setting.name];
      });
    },
  };
}

function flagRow(setting) {
  const errors = errorSlot();
  const toggle = switchControl({
    label: null,
    onChange: (checked) => send({ path: "/api/link", body: { [setting.name]: checked }, errorSlot: errors, success: humanise(setting.name) + (checked ? " on" : " off") }),
  });
  toggle.input.setAttribute("aria-label", humanise(setting.name));
  const mark = changedMark();
  const reset = resetButton(setting, errors);
  const stateText = el("span", { class: "muted" });
  const element = rowShell({ setting, input: [toggle.element, stateText], errors, mark, reset });
  return {
    element,
    update(state) {
      const changed = state.changes.link.includes(setting.name);
      mark.hidden = !changed;
      reset.disabled = !changed;
      toggle.input.checked = Boolean(state.link[setting.name]);
      stateText.textContent = toggle.input.checked ? "On" : "Off";
    },
  };
}

function blocksRow(setting) {
  const errors = errorSlot();
  const lines = el("div", { class: "block-editor" });
  let dirty = false;
  let renderedKey = null;

  function lineInput(label, value, chars) {
    const input = el("input", { type: "text", class: "sized", style: "--chars: " + chars, value, "aria-label": label });
    input.addEventListener("input", () => {
      dirty = true;
    });
    return input;
  }

  function addLine(block) {
    const start = lineInput("Block start address", hex(block.start), 6);
    const end = lineInput("Block end address", hex(block.end), 6);
    const code = lineInput("Exception code 0 to 255", String(block.code), 3);
    const line = el(
      "div",
      { class: "block-line" },
      "From",
      start,
      "to",
      end,
      "answer exception",
      code,
      button({
        label: "Remove block",
        iconName: "x",
        iconOnly: true,
        onClick: () => {
          dirty = true;
          line.remove();
        },
      }),
    );
    line.read = () => ({ start: parseNumber(start.value), end: parseNumber(end.value), code: parseNumber(code.value) });
    lines.append(line);
  }

  function readLines() {
    return [...lines.children].map((line) => line.read());
  }

  const add = button({
    label: "Add block",
    iconName: "plus",
    onClick: () => {
      dirty = true;
      addLine({ start: 0, end: 0, code: 0 });
    },
  });
  const apply = button({
    kind: "primary",
    label: "Apply blocks",
    iconName: "check",
    onClick: async () => {
      const done = await send({ path: "/api/link", body: { [setting.name]: readLines() }, errorSlot: errors, success: "Refused blocks applied" });
      if (done) {
        dirty = false;
        renderedKey = null;
        update(currentState());
      }
    },
  });
  const mark = changedMark();
  const reset = resetButton(setting, errors);
  const element = el(
    "div",
    { class: "control-row" },
    el("div", { class: "control-label" }, el("span", { text: humanise(setting.name) }), el("code", { class: "muted", text: setting.name })),
    el("div", { class: "control-input" }, add, apply),
    el("div", { class: "control-note" }, el("span", { text: "Scenario " + scenarioText(setting) }), mark, reset, errors),
    lines,
  );
  function update(state) {
    const changed = state.changes.link.includes(setting.name);
    mark.hidden = !changed;
    reset.disabled = !changed;
    const key = JSON.stringify(state.link[setting.name]);
    if (dirty || hasFocus(lines) || key === renderedKey) return;
    renderedKey = key;
    lines.replaceChildren();
    for (const block of state.link[setting.name]) addLine(block);
  }
  return { element, update };
}

export function createLink() {
  const rows = description().link.settings.map((setting) => {
    if (setting.kind === "flag") return flagRow(setting);
    if (setting.kind === "blocks") return blocksRow(setting);
    return numberRow(setting);
  });
  const status = el("strong");
  const detail = el("span", { class: "muted" });
  const drop = button({
    label: "Drop connections now",
    iconName: "plug-x",
    onClick: () => send({ path: "/api/link/drop", success: "Every client connection was closed" }),
  });
  const resetModule = button({
    label: "Reset module",
    iconName: "restore",
    onClick: () => send({ path: "/api/link/reset", success: "Module reset: lockout cleared" }),
  });
  const element = el(
    "section",
    { class: "view" },
    el("h2", { text: "Link" }),
    el("div", { class: "card" }, el("h3", { text: "Module" }), el("div", { class: "toolbar" }, status, detail), el("div", { class: "toolbar" }, drop, resetModule)),
    el("div", { class: "link-grid" }, ...rows.map((row) => el("div", { class: "card" }, row.element))),
  );

  function update() {
    const state = currentState();
    if (state === null) return;
    const module = state.module;
    status.textContent = "Module " + (module.status === "online" ? "online" : humanise(module.status).toLowerCase());
    const locked = module.locked_out
      ? module.whole_port
        ? "Every client is locked out"
        : "Locked out: " + module.locked_addresses.join(", ")
      : "";
    detail.textContent = locked;
    for (const row of rows) row.update(state);
  }

  return { element, update, activate: update, deactivate() {} };
}
