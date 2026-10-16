import { button, changedMark, errorSlot, send, switchControl } from "../shared/actions.js";
import { el, reveal, svgEl, whenIdle } from "../shared/dom.js";
import { activeFaults } from "../shared/faultinfo.js";
import { humanise, inputChars, parseNumber, showNumber } from "../shared/format.js";
import { icon, iconNode } from "../shared/icons.js";
import { go } from "../shared/navigation.js";
import { createPackCodes } from "../shared/packcodes.js";
import { createSettingControl } from "../shared/settingcontrol.js";
import { currentState, description } from "../shared/state.js";

const DIAGRAM_WIDTH = 640;
const DIAGRAM_HEIGHT = 360;
const NODE_WIDTH = 160;
const NODE_HEIGHT = 92;
const INVERTER_WIDTH = 120;
const INVERTER_HEIGHT = 72;
const INVERTER_CENTRE = { x: 320, y: 180 };
const ICON_SIZE = 28;
const NODE_PADDING = 12;

const NODE_LAYOUT = {
  solar: {
    centre: { x: 320, y: 52 },
    icon: "sun",
    nodeEnd: { x: 320, y: 98 },
    inverterEnd: { x: 320, y: 144 },
  },
  external_pv: {
    centre: { x: 544, y: 52 },
    icon: "sun",
    nodeEnd: { x: 500, y: 98 },
    inverterEnd: { x: 360, y: 144 },
  },
  grid: {
    centre: { x: 96, y: 180 },
    icon: "plug-connected",
    nodeEnd: { x: 176, y: 180 },
    inverterEnd: { x: 260, y: 180 },
  },
  house: {
    centre: { x: 544, y: 180 },
    icon: "home",
    nodeEnd: { x: 464, y: 180 },
    inverterEnd: { x: 380, y: 180 },
  },
  battery: {
    centre: { x: 176, y: 308 },
    icon: "battery-3",
    nodeEnd: { x: 176, y: 262 },
    inverterEnd: { x: 290, y: 216 },
  },
  ev_charger: {
    centre: { x: 464, y: 308 },
    icon: "car",
    nodeEnd: { x: 464, y: 262 },
    inverterEnd: { x: 350, y: 216 },
  },
};

const EV_ENERGY_STEP = 100;

function flowFor(kind, power) {
  if (Math.round(power) === 0) return { colour: "idle", towardsInverter: true, moving: false };
  if (kind === "solar" || kind === "external_pv") return { colour: "solar", towardsInverter: true, moving: true };
  if (kind === "grid") return { colour: "grid", towardsInverter: power > 0, moving: true };
  if (kind === "battery") {
    return power < 0
      ? { colour: "charge", towardsInverter: false, moving: true }
      : { colour: "discharge", towardsInverter: true, moving: true };
  }
  if (kind === "ev_charger") return { colour: "ev", towardsInverter: false, moving: true };
  return { colour: "house", towardsInverter: false, moving: true };
}

function pathBetween(layout, towardsInverter) {
  const [from, to] = towardsInverter ? [layout.nodeEnd, layout.inverterEnd] : [layout.inverterEnd, layout.nodeEnd];
  return "M" + from.x + " " + from.y + " L" + to.x + " " + to.y;
}

function reading(state, name) {
  return state.node_readings[name];
}

function formatReading(value, unit) {
  return showNumber(value) + (unit ? " " + unit : "");
}

function nodeGroup({ node, layout, onOpen }) {
  const x = layout.centre.x - NODE_WIDTH / 2;
  const y = layout.centre.y - NODE_HEIGHT / 2;
  const group = svgEl("g", { class: "node node-" + node.kind, tabindex: 0, role: "button", "aria-label": node.label + ": open its card" });
  const lines = node.readings.map((_, index) =>
    svgEl("text", {
      class: index === 0 ? "node-value" : "node-label",
      x: x + NODE_PADDING,
      y: y + 62 + index * 20,
    }),
  );
  group.append(
    svgEl("rect", { x, y, width: NODE_WIDTH, height: NODE_HEIGHT, rx: 10 }),
    iconNode(layout.icon, { x: x + NODE_PADDING, y: y + NODE_PADDING, width: ICON_SIZE, height: ICON_SIZE }),
    svgEl("text", { class: "node-label", x: x + NODE_PADDING + ICON_SIZE + 8, y: y + 32, text: node.label }),
    ...lines,
  );
  group.addEventListener("click", onOpen);
  group.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      onOpen();
    }
  });
  return { group, lines };
}

function createDiagram({ openCard }) {
  const nodes = description().nodes.filter((node) => NODE_LAYOUT[node.kind]);
  const svg = svgEl("svg", {
    class: "diagram",
    viewBox: "0 0 " + DIAGRAM_WIDTH + " " + DIAGRAM_HEIGHT,
    role: "group",
    "aria-label": "Power flow",
  });
  const flows = svgEl("g");
  const hubCard = description().cards.find((card) => card.hub);
  const inverterX = INVERTER_CENTRE.x - INVERTER_WIDTH / 2;
  const inverterY = INVERTER_CENTRE.y - INVERTER_HEIGHT / 2;
  const inverterGroup = svgEl("g", { class: "node node-inverter" });
  inverterGroup.append(
    svgEl("rect", { x: inverterX, y: inverterY, width: INVERTER_WIDTH, height: INVERTER_HEIGHT, rx: 10 }),
    iconNode("bolt", { x: inverterX + 16, y: inverterY + 22, width: ICON_SIZE, height: ICON_SIZE }),
    svgEl("text", { class: "node-label", x: inverterX + 52, y: inverterY + 42, text: hubCard ? hubCard.label : "Hub" }),
  );
  if (hubCard) {
    inverterGroup.setAttribute("tabindex", "0");
    inverterGroup.setAttribute("role", "button");
    inverterGroup.setAttribute("aria-label", hubCard.label + ": open its card");
    inverterGroup.addEventListener("click", () => openCard(hubCard.key));
    inverterGroup.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        openCard(hubCard.key);
      }
    });
  }
  const parts = nodes.map((node) => ({
    node,
    layout: NODE_LAYOUT[node.kind],
    flow: svgEl("path", { class: "flow idle" }),
    ...nodeGroup({ node, layout: NODE_LAYOUT[node.kind], onOpen: () => openCard(node.card) }),
  }));
  flows.append(...parts.map((part) => part.flow));
  svg.append(flows, inverterGroup, ...parts.map((part) => part.group));

  function update(state, faultedCards) {
    for (const part of parts) {
      const values = part.node.readings.map((spec) => reading(state, spec.name));
      part.lines.forEach((line, index) => {
        const spec = part.node.readings[index];
        line.textContent = formatReading(values[index], spec.unit);
        line.replaceChildren(line.textContent, svgEl("title", { text: spec.label }));
      });
      const flow = flowFor(part.node.kind, values[0]);
      part.flow.setAttribute("d", pathBetween(part.layout, flow.towardsInverter));
      part.flow.setAttribute("class", "flow " + flow.colour + (flow.moving ? " active" : ""));
      part.group.classList.toggle("fault", faultedCards.has(part.node.card));
    }
  }

  const legend = el(
    "div",
    { class: "legend" },
    ...[
      ["solar", "Solar"],
      ["grid", "Grid"],
      ["charge", "Battery charging"],
      ["discharge", "Battery discharging"],
      ["ev", "EV charging"],
      ["house", "House"],
      ["idle", "No flow"],
    ].map(([key, text]) => el("span", {}, el("span", { class: "swatch " + key }), text)),
  );
  return { element: el("div", { class: "diagram-wrap" }, svg, legend), update };
}

function variationRow(parameter) {
  const errors = errorSlot();
  const stepAttributes = { min: parameter.minimum, max: parameter.maximum, step: parameter.step };
  const field = el("input", {
    ...stepAttributes,
    type: "number",
    style: "--chars: " + inputChars({ maximum: parameter.maximum, step: parameter.step }),
    "aria-label": parameter.label,
  });
  const slider = parameter.slider ? el("input", { ...stepAttributes, type: "range", "aria-label": parameter.label + " slider" }) : null;
  const sendValue = (input) =>
    send({
      path: "/api/variation",
      body: { [parameter.name]: parseNumber(input.value) },
      errorSlot: errors,
      success: parameter.label + " set to " + input.value + (parameter.unit ? " " + parameter.unit : ""),
    });
  field.addEventListener("change", () => sendValue(field));
  if (slider) {
    slider.addEventListener("input", () => {
      field.value = slider.value;
    });
    slider.addEventListener("change", () => sendValue(slider));
    field.addEventListener("input", () => {
      slider.value = field.value;
    });
  }
  const mark = changedMark();
  const reset = button({
    label: "Reset " + parameter.label + " to the scenario value",
    iconName: "restore",
    iconOnly: true,
    onClick: () =>
      send({
        path: "/api/variation",
        body: { [parameter.name]: parameter.scenario },
        errorSlot: errors,
        success: parameter.label + " reset to " + parameter.scenario,
      }),
  });
  const unit = parameter.unit ? el("span", { class: "muted", text: parameter.unit }) : null;
  const element = el(
    "div",
    { class: "control-row" },
    el("div", { class: "control-label" }, el("span", { text: parameter.label }), el("span", { class: "mono", text: parameter.name })),
    el("div", { class: "control-input" }, slider, field, unit, reset),
    el(
      "div",
      { class: "control-note" },
      el("span", { text: "Scenario value " + showNumber(parameter.scenario) + (parameter.unit ? " " + parameter.unit : "") }),
      mark,
      errors,
    ),
  );
  function update(state) {
    const changed = state.changes.variation.includes(parameter.name);
    mark.hidden = !changed;
    reset.disabled = !changed;
    whenIdle(element, () => {
      field.value = state.variation[parameter.name];
      if (slider) slider.value = field.value;
    });
  }
  return { element, update };
}

function holdRow(hold) {
  const errors = errorSlot();
  const field = el("input", {
    type: "number",
    min: hold.minimum,
    max: hold.maximum,
    step: hold.step,
    style: "--chars: " + inputChars({ maximum: hold.maximum, step: hold.step }),
    "aria-label": "Hold " + hold.label + " at",
  });
  let toggle;
  const apply = (enabled) =>
    send({
      path: "/api/holds",
      body: { [hold.name]: enabled ? parseNumber(field.value) : null },
      errorSlot: errors,
      success: enabled ? hold.label + " held at " + field.value + " " + hold.unit : hold.label + " released",
    });
  toggle = switchControl({ label: "Hold " + hold.label, onChange: apply });
  field.addEventListener("change", () => {
    if (toggle.input.checked) apply(true);
  });
  const mark = changedMark("Held");
  const element = el(
    "div",
    { class: "control-row" },
    el("div", { class: "control-label" }, toggle.element, el("span", { class: "mono", text: hold.name })),
    el("div", { class: "control-input" }, field, el("span", { class: "muted", text: hold.unit })),
    el("div", { class: "control-note" }, mark, errors),
  );
  function update(state) {
    const held = state.holds[hold.name];
    mark.hidden = held === null;
    toggle.input.checked = held !== null;
    whenIdle(field, () => {
      field.value = held !== null ? held : state.hold_readings[hold.name];
    });
  }
  return { element, update };
}

function packRow(pack) {
  const codes = createPackCodes(pack);
  const element = el(
    "div",
    { class: "control-row" },
    el("div", { class: "control-label", text: "Pack " + pack + " codes" }),
    codes.inputs,
    el("div", { class: "control-note" }, codes.errors),
  );
  return { element, update: (state) => codes.update(state, element) };
}

function stateOfChargeRow() {
  const bounds = description().model.equipment.battery.soc_bounds;
  const errors = errorSlot();
  const slider = el("input", { type: "range", min: bounds[0], max: bounds[1], step: 1, "aria-label": "State of charge" });
  const output = el("output", { class: "mono" });
  const show = () => {
    output.textContent = slider.value + " %";
  };
  slider.addEventListener("input", show);
  slider.addEventListener("change", () =>
    send({ path: "/api/battery", body: { soc_percent: parseNumber(slider.value) }, errorSlot: errors, success: "State of charge set to " + slider.value + " %" }),
  );
  const element = el(
    "div",
    { class: "control-row" },
    el("div", { class: "control-label", text: "State of charge" }),
    el("div", { class: "control-input" }, slider, output),
    el("div", { class: "control-note" }, errors),
  );
  function update(state) {
    whenIdle(slider, () => {
      slider.value = Math.round(state.battery.soc_percent);
      show();
    });
  }
  return { element, update };
}

function carRow() {
  const charger = description().model.equipment.ev_charger;
  const errors = errorSlot();
  const energy = el("input", {
    type: "number",
    min: charger.energy_bounds_wh[0],
    max: charger.energy_bounds_wh[1],
    step: EV_ENERGY_STEP,
    value: charger.default_energy_wh,
    style: "--chars: " + inputChars({ maximum: charger.energy_bounds_wh[1], step: EV_ENERGY_STEP }),
    "aria-label": "Energy the car needs",
  });
  const plugIn = button({
    kind: "primary",
    label: "Plug in",
    iconName: "plug-connected",
    onClick: () => send({ path: "/api/ev", body: { plugged: true, energy_needed_wh: parseNumber(energy.value) }, errorSlot: errors, success: "Car plugged in needing " + energy.value + " Wh" }),
  });
  const unplug = button({
    label: "Unplug",
    iconName: "plug-x",
    onClick: () => send({ path: "/api/ev", body: { plugged: false }, errorSlot: errors, success: "Car unplugged" }),
  });
  const element = el(
    "div",
    { class: "control-row" },
    el("div", { class: "control-label", text: "Car" }),
    el("div", { class: "control-input" }, "Needs", energy, el("span", { class: "muted", text: "Wh" }), plugIn, unplug),
    el("div", { class: "control-note" }, errors),
  );
  return { element, update: () => {} };
}

function cardChangeKinds(card, state) {
  const faultEquipment = Object.entries(description().faults.cards).filter(([, key]) => key === card.key).map(([equipment]) => equipment);
  return {
    holds: description().holds.some((hold) => hold.card === card.key && state.changes.holds.includes(hold.name)),
    variation: description().variation.some((parameter) => parameter.card === card.key && state.changes.variation.includes(parameter.name)),
    faults: faultEquipment.some((equipment) => (state.changes.faults[equipment] || 0) > 0),
  };
}

function createReadings(card) {
  const element = el("div", { class: "readings-block" });
  const cells = new Map(
    card.readings.map((spec) => {
      const value = el("span", { class: "value" });
      element.append(el("div", { class: "reading" }, value, el("span", { class: "name", text: spec.label })));
      return [spec.name, value];
    }),
  );
  function update(state) {
    for (const spec of card.readings) cells.get(spec.name).textContent = formatReading(state.card_readings[spec.name], spec.unit);
  }
  return { element, update };
}

const SPECIAL_CONTROLS = { state_of_charge: stateOfChargeRow, car: carRow };

function createCard(card, onChangeMarks) {
  const parameters = description().variation.filter((parameter) => parameter.card === card.key);
  const rows = [];
  const primaryRows = parameters.filter((candidate) => candidate.primary).map(variationRow);
  const moreRows = [];
  for (const hold of description().holds.filter((candidate) => candidate.card === card.key)) primaryRows.push(holdRow(hold));
  for (const kind of card.controls) primaryRows.push(SPECIAL_CONTROLS[kind]());
  for (const setting of description().settings.filter((candidate) => candidate.card === card.key)) {
    (setting.primary ? primaryRows : moreRows).push(settingRow(setting));
  }
  for (const parameter of parameters.filter((candidate) => !candidate.primary)) moreRows.push(variationRow(parameter));
  if (description().faults.cards.packs === card.key) {
    for (const pack of description().faults.packs) moreRows.push(packRow(pack));
  }
  rows.push(...primaryRows, ...moreRows);
  const readings = createReadings(card);
  const mark = changedMark("Differs from the scenario");
  const faultMark = el("span", { class: "mark fault", hidden: true }, icon("alert-triangle"), "Fault active");
  const reset = button({
    label: "Reset",
    iconName: "restore",
    title: "Reset this card's variation, holds and faults to the scenario",
    onClick: () => send({ path: "/api/reset/" + encodeURIComponent(card.key), success: card.label + " reset to the scenario" }),
  });
  const faultList = el("ul");
  const faultBox = el(
    "div",
    { class: "faults-link", hidden: true },
    el("strong", { text: "Active faults" }),
    faultList,
    button({ label: "Open in Faults", iconName: "alert-triangle", onClick: () => go("faults", { activeOnly: true }) }),
  );
  const disclosure = moreRows.length
    ? el("details", {}, el("summary", {}, "More " + card.label.toLowerCase() + " settings"), el("div", { class: "disclosure" }, ...moreRows.map((row) => row.element)))
    : null;
  const element = el(
    "article",
    { class: "card", id: "card-" + card.key },
    el("div", { class: "card-heading" }, el("h3", { text: card.label }), faultMark, mark, reset),
    readings.element,
    primaryRows.length ? el("span", { class: "group-label", text: "Settings" }) : null,
    primaryRows.length ? el("div", { class: "controls" }, ...primaryRows.map((row) => row.element)) : null,
    disclosure,
    faultBox,
  );
  let faultSignature = null;
  function update(state) {
    readings.update(state);
    for (const row of rows) row.update(state);
    const kinds = cardChangeKinds(card, state);
    const changed = kinds.holds || kinds.variation || kinds.faults;
    element.classList.toggle("changed", changed);
    mark.hidden = !changed;
    reset.disabled = !changed;
    const active = activeFaults(description(), state).filter((item) => item.card === card.key);
    element.classList.toggle("faulted", active.length > 0);
    faultMark.hidden = active.length === 0;
    faultBox.hidden = active.length === 0;
    const signature = active.map((item) => item.name).join("|");
    if (signature !== faultSignature) {
      faultSignature = signature;
      faultList.replaceChildren(...active.map((item) => el("li", { text: item.name })));
    }
    onChangeMarks(card.key, kinds);
  }
  return { element, update, details: disclosure };

  function settingRow(setting) {
    const errors = errorSlot();
    const control = createSettingControl({ setting, errorSlot: errors });
    const row = {
      element: el(
        "div",
        { class: "control-row" },
        el("div", { class: "control-label" }, el("span", { text: humanise(setting.name) }), el("span", { class: "mono", text: setting.name + " · " + setting.address })),
        el("div", { class: "control-input" }, control.input, control.scaled),
        el("div", { class: "control-note" }, errors),
      ),
      update: control.update,
    };
    return row;
  }
}

export function createOverview() {
  const changeKinds = new Map();
  const cards = new Map();
  const diagram = createDiagram({ openCard });
  const grid = el("div", { class: "cards" });
  for (const cardSpec of description().cards) {
    const card = createCard(cardSpec, (key, kinds) => changeKinds.set(key, kinds));
    cards.set(cardSpec.key, card);
    grid.append(card.element);
  }
  const element = el("section", { class: "view" }, el("h2", { text: "Overview" }), diagram.element, grid);

  function openCard(key) {
    const card = cards.get(key);
    if (!card) return;
    if (card.details) card.details.open = true;
    reveal(card.element);
  }

  function update() {
    const state = currentState();
    if (state === null) return;
    const faulted = new Set(activeFaults(description(), state).map((item) => item.card));
    diagram.update(state, faulted);
    for (const card of cards.values()) card.update(state);
  }

  function activate(intent) {
    update();
    if (!intent) return;
    if (intent.card) openCard(intent.card);
    if (intent.changed) {
      const first = [...changeKinds].find(([, kinds]) => kinds[intent.changed]);
      if (first) openCard(first[0]);
    }
  }

  return { element, update, activate, deactivate() {} };
}

