import { button, changedMark, confirmAction, errorSlot, send } from "../shared/actions.js";
import { el, reveal } from "../shared/dom.js";
import { humanise, parseNumber } from "../shared/format.js";
import { createSettingControl, describeValue, optionLabel } from "../shared/settingcontrol.js";
import { currentState, description } from "../shared/state.js";

function settingRow(setting) {
  const errors = errorSlot();
  const control = createSettingControl({ setting, errorSlot: errors });
  const mark = changedMark();
  const scenario = el("span", { class: "muted" });
  const reset = button({
    label: "Reset " + humanise(setting.name) + " to the scenario value",
    iconName: "restore",
    iconOnly: true,
    onClick: () =>
      send({
        path: "/api/settings",
        body: { [setting.name]: setting.scenario.raw },
        errorSlot: errors,
        success: humanise(setting.name) + " reset to " + describeValue(setting, setting.scenario),
      }),
  });
  const element = el(
    "div",
    { class: "row settings-row", id: "setting-" + setting.name },
    el("div", { class: "control-label" }, el("span", { text: humanise(setting.name) }), el("code", { class: "muted", text: setting.name + " · " + setting.address })),
    el("div", { class: "control-input" }, control.input, control.scaled, errors),
    el("div", {}, el("span", { class: "muted", text: "Scenario " }), scenario),
    el("div", { class: "control-input" }, mark, reset),
  );
  scenario.textContent = describeValue(setting, setting.scenario);
  const search = (setting.name + " " + humanise(setting.name) + " " + setting.address + " " + setting.group).toLowerCase();
  function update(state) {
    control.update(state);
    const changed = state.changes.settings.includes(setting.name);
    mark.hidden = !changed;
    reset.disabled = !changed;
    element.classList.toggle("active", changed);
  }
  return { element, update, search, name: setting.name, group: setting.group };
}

function commandRow(command) {
  const errors = errorSlot();
  let input;
  if (command.options) {
    input = el("select", { "aria-label": humanise(command.name) });
    for (const option of command.options) input.append(el("option", { value: option.value, text: optionLabel(option) }));
  } else {
    input = el("input", { type: "number", step: 1, value: 1, style: "--chars: 6", "aria-label": humanise(command.name) });
  }
  const clearAll = description().faults.clear_all;
  const run = button({
    kind: "secondary",
    label: "Run",
    iconName: "player-play",
    onClick: async () => {
      const value = parseNumber(input.value);
      const isClearAll = command.name === clearAll.command && value === clearAll.value;
      const label = command.options ? input.selectedOptions[0].textContent : humanise(command.name);
      if (!isClearAll) {
        const confirmed = await confirmAction({
          title: label,
          message: "The simulator carries out " + humanise(command.name).toLowerCase() + " (" + label + ") as if a client had written it.",
          confirmLabel: "Run " + label,
        });
        if (!confirmed) return;
      }
      send({ path: "/api/commands", body: { name: command.name, value }, errorSlot: errors, success: label + " ran" });
    },
  });
  const element = el(
    "div",
    { class: "row settings-row", id: "setting-" + command.name },
    el("div", { class: "control-label" }, el("span", { text: humanise(command.name) }), el("code", { class: "muted", text: command.name + " · " + command.address })),
    el("div", { class: "control-input" }, input, run, errors),
    el("span"),
    el("span"),
  );
  return { element, search: (command.name + " " + humanise(command.name) + " " + command.address).toLowerCase(), name: command.name };
}

export function createSettings() {
  const settings = description().settings.map(settingRow);
  const commands = description().commands.map(commandRow);
  const groups = new Map();
  for (const row of settings) {
    if (!groups.has(row.group)) groups.set(row.group, []);
    groups.get(row.group).push(row);
  }
  const groupViews = [...groups].map(([name, rows]) => {
    const summary = el("summary");
    const details = el("details", {}, summary, ...rows.map((row) => row.element));
    return { name, rows, summary, details };
  });
  const head = el(
    "div",
    { class: "row head settings-row" },
    el("span", { text: "Setting" }),
    el("span", { text: "Value" }),
    el("span", { text: "Scenario value" }),
    el("span", { text: "Changed" }),
  );
  const settingsBox = el("div", { class: "table" }, head, ...groupViews.map((group) => group.details));
  const commandsBox = el("div", { class: "table" }, ...commands.map((row) => row.element));
  const filter = el("input", { type: "search", placeholder: "Filter by name or address", "aria-label": "Filter settings" });
  const empty = el("div", { class: "empty", text: "Nothing matches the filter" });
  const element = el(
    "section",
    { class: "view" },
    el("h2", { text: "Settings" }),
    el("div", { class: "toolbar" }, filter),
    settingsBox,
    el("h2", { text: "Commands" }),
    commandsBox,
    empty,
  );
  let lastText = null;

  function applyFilter() {
    const text = filter.value.trim().toLowerCase();
    const changedText = text !== lastText;
    lastText = text;
    let shown = 0;
    for (const group of groupViews) {
      let groupShown = 0;
      for (const row of group.rows) {
        const show = !text || row.search.includes(text);
        row.element.hidden = !show;
        if (show) groupShown += 1;
      }
      group.summary.textContent = group.name + " (" + groupShown + ")";
      group.details.hidden = groupShown === 0;
      if (changedText && text) group.details.open = groupShown > 0;
      shown += groupShown;
    }
    let commandsShown = 0;
    for (const row of commands) {
      row.element.hidden = Boolean(text) && !row.search.includes(text);
      if (!row.element.hidden) commandsShown += 1;
    }
    commandsBox.hidden = commandsShown === 0;
    empty.hidden = shown + commandsShown > 0;
  }
  filter.addEventListener("input", applyFilter);

  function update() {
    const state = currentState();
    if (state === null) return;
    for (const row of settings) row.update(state);
    applyFilter();
  }

  function focusRow(name) {
    const row = [...settings, ...commands].find((candidate) => candidate.name === name);
    if (!row) return;
    filter.value = "";
    applyFilter();
    reveal(row.element);
  }

  function activate(intent) {
    update();
    if (!intent) return;
    if (intent.setting) focusRow(intent.setting);
    if (intent.changed) {
      const state = currentState();
      const first = settings.find((row) => state.changes.settings.includes(row.name));
      if (first) focusRow(first.name);
    }
  }

  return { element, update, activate, deactivate() {} };
}

