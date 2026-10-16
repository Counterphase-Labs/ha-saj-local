import { button, errorSlot, send, switchControl } from "../shared/actions.js";
import { el } from "../shared/dom.js";
import { createPackCodes } from "../shared/packcodes.js";
import { faultEquipment } from "../shared/faultinfo.js";
import { currentState, description } from "../shared/state.js";

function cardLabel(equipment) {
  const key = description().faults.cards[equipment];
  const card = description().cards.find((candidate) => candidate.key === key);
  return card ? card.label : equipment;
}

function bitRow({ equipment, bit }) {
  const errors = errorSlot();
  const toggle = switchControl({
    label: null,
    onChange: (checked) =>
      send({
        path: "/api/faults",
        body: { [equipment]: { [bit.key]: checked } },
        errorSlot: errors,
        success: bit.name + (checked ? " set" : " cleared"),
      }),
  });
  toggle.input.setAttribute("aria-label", bit.name);
  const element = el(
    "div",
    { class: "row faults-row" + (bit.reserved ? " reserved" : "") },
    el("div", {}, el("div", { text: bit.name }), errors),
    el("div", { text: cardLabel(equipment) }),
    el("code", { text: bit.register + " bit " + bit.bit }),
    el("div", { text: bit.effect }),
    toggle.element,
  );
  const search = (bit.name + " " + bit.register + " " + bit.bit + " " + bit.key).toLowerCase();
  function update(state) {
    const active = Boolean((state.faults[equipment] || {})[bit.key]);
    toggle.input.checked = active;
    element.classList.toggle("active", active);
    return active;
  }
  return { element, equipment, search, update, reserved: bit.reserved, register: bit.register };
}

function packRow(pack) {
  const codes = createPackCodes(pack);
  const element = el(
    "div",
    { class: "row pack-row" },
    el("div", {}, el("div", { text: "Pack " + pack + " fault and warning codes" }), el("span", { class: "muted", text: "No bit table names them, so they are number codes" })),
    el("div", {}, codes.inputs, codes.errors),
  );
  function update(state) {
    const active = codes.update(state, element);
    element.classList.toggle("active", active);
    return active;
  }
  return { element, update, search: ("pack " + pack + " fault warning code").toLowerCase() };
}

export function createFaults() {
  const faults = description().faults;
  const equipmentKeys = faultEquipment(description());
  const named = [];
  const reservedByRegister = new Map();
  for (const equipment of equipmentKeys) {
    for (const bit of faults[equipment]) {
      const row = bitRow({ equipment, bit });
      if (!bit.reserved) named.push(row);
      else {
        const key = equipment + " " + bit.register;
        if (!reservedByRegister.has(key)) reservedByRegister.set(key, { equipment, register: bit.register, rows: [] });
        reservedByRegister.get(key).rows.push(row);
      }
    }
  }
  const packRows = faults.packs.map(packRow);
  const search = el("input", { type: "search", placeholder: "Search name, register or bit", "aria-label": "Search faults" });
  const equipment = el(
    "select",
    { "aria-label": "Filter by equipment" },
    el("option", { value: "", text: "All equipment" }),
    ...equipmentKeys.map((key) => el("option", { value: key, text: cardLabel(key) })),
  );
  const activeOnly = switchControl({ label: "Active only", onChange: applyFilters });
  const clear = button({
    kind: "primary",
    label: "Clear all faults",
    iconName: "restore",
    onClick: () =>
      send({ path: "/api/commands", body: { name: faults.clear_all.command, value: faults.clear_all.value }, success: "All faults cleared" }),
  });
  const head = el(
    "div",
    { class: "row head faults-row" },
    el("span", { text: "Fault" }),
    el("span", { text: "Equipment" }),
    el("span", { text: "Register and bit" }),
    el("span", { text: "Effect" }),
    el("span", { text: "State" }),
  );
  const namedBox = el("div", { class: "table" }, head, ...named.map((row) => row.element));
  const reservedGroups = [...reservedByRegister.values()].map((group) => {
    const summary = el("summary", {});
    const details = el("details", {}, summary, ...group.rows.map((row) => row.element));
    return { ...group, summary, details };
  });
  const reservedBox = el("div", { class: "table" }, ...reservedGroups.map((group) => group.details));
  const reservedHeading = el("h3", { text: "Reserved bits" });
  const packBox = el("div", { class: "table" }, ...packRows.map((row) => row.element));
  const empty = el("div", { class: "empty", text: "No fault matches the filter" });
  const element = el(
    "section",
    { class: "view" },
    el("div", { class: "view-heading" }, el("h2", { text: "Faults" }), clear),
    el("div", { class: "toolbar" }, search, equipment, activeOnly.element),
    namedBox,
    packBox,
    reservedHeading,
    reservedBox,
    empty,
  );
  let lastSignature = null;
  search.addEventListener("input", applyFilters);
  equipment.addEventListener("change", applyFilters);

  function applyFilters() {
    const text = search.value.trim().toLowerCase();
    const wanted = equipment.value;
    const onlyActive = activeOnly.input.checked;
    const state = currentState();
    const visible = (row, rowEquipment, active) =>
      (!wanted || rowEquipment === wanted) && (!text || row.search.includes(text)) && (!onlyActive || active);
    const signature = [text, wanted, onlyActive].join("|");
    const filterChanged = signature !== lastSignature;
    lastSignature = signature;
    let shown = 0;
    for (const row of named) {
      const show = visible(row, row.equipment, row.element.classList.contains("active"));
      row.element.hidden = !show;
      if (show) shown += 1;
    }
    for (const group of reservedGroups) {
      let groupShown = 0;
      for (const row of group.rows) {
        const show = visible(row, row.equipment, row.element.classList.contains("active"));
        row.element.hidden = !show;
        if (show) groupShown += 1;
      }
      group.summary.textContent = "Reserved bits in " + group.register + " (" + groupShown + ")";
      group.details.hidden = groupShown === 0;
      if (filterChanged && (text || onlyActive)) group.details.open = groupShown > 0;
      shown += groupShown;
    }
    const packsMatchEquipment = !wanted || faults.cards[wanted] === faults.cards.packs;
    let packsShown = 0;
    packRows.forEach((row) => {
      const show = packsMatchEquipment && (!text || row.search.includes(text)) && (!onlyActive || row.element.classList.contains("active"));
      row.element.hidden = !show;
      if (show) packsShown += 1;
    });
    packBox.hidden = packsShown === 0;
    reservedHeading.hidden = reservedBox.children.length === 0 || [...reservedGroups].every((group) => group.details.hidden);
    reservedBox.hidden = reservedHeading.hidden;
    namedBox.hidden = named.every((row) => row.element.hidden);
    empty.hidden = shown + packsShown > 0 || state === null;
  }

  function update() {
    const state = currentState();
    if (state === null) return;
    for (const row of [...named, ...packRows, ...reservedGroups.flatMap((group) => group.rows)]) row.update(state);
    applyFilters();
  }

  function activate(intent) {
    if (intent && intent.activeOnly) {
      activeOnly.input.checked = true;
      search.value = "";
      equipment.value = "";
    }
    update();
  }

  return { element, update, activate, deactivate() {} };
}
