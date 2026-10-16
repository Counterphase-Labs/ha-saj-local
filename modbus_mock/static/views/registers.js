import { button, switchControl } from "../shared/actions.js";
import { el } from "../shared/dom.js";
import { elapsed, hex, humanise, showNumber } from "../shared/format.js";
import { go } from "../shared/navigation.js";
import { getJson } from "../shared/requests.js";
import { description, serverNow } from "../shared/state.js";
import { toast } from "../shared/toasts.js";

const REFRESH_MILLISECONDS = 1000;
const HIGHLIGHT_MILLISECONDS = 2000;
const RESERVED_ACCESS = "reserved";

async function copyText(text, what) {
  try {
    await navigator.clipboard.writeText(text);
    toast({ kind: "success", message: "Copied " + what + ": " + text });
  } catch {
    toast({ kind: "refusal", message: "The browser did not allow copying" });
  }
}

function highlight(cell) {
  cell.classList.remove("cell-changed");
  void cell.offsetWidth;
  cell.classList.add("cell-changed");
  setTimeout(() => cell.classList.remove("cell-changed"), HIGHLIGHT_MILLISECONDS);
}

function valueText(field) {
  if (field.value === null || field.value === undefined) return "";
  const shown = typeof field.value === "number" ? showNumber(field.value) : String(field.value);
  return field.label ? shown + " " + field.label : shown;
}

function wordsText(words) {
  if (words === null) return "";
  return words.map((word) => hex(word)).join(" ");
}

function addressText(field) {
  return field.last_address === field.address ? field.address : field.address + "–" + field.last_address;
}

function fieldRow({ field, block, linkable }) {
  const raw = el("code");
  const value = el("span", { class: "mono" });
  const read = el("span", { class: "muted" });
  const actions = el("div", { class: "copy-cell" });
  const reserved = field.access === RESERVED_ACCESS;
  actions.append(
    button({ label: "Raw", iconName: "copy", title: "Copy raw", onClick: () => copyText(raw.textContent, "raw words") }),
    button({ label: "Value", iconName: "copy", title: "Copy value", onClick: () => copyText(value.textContent, "value") }),
  );
  if (linkable) {
    actions.append(
      button({ label: "Open its control in Settings", iconName: "settings", iconOnly: true, title: "Open its control in Settings", onClick: () => go("settings", { setting: field.name }) }),
    );
  }
  const element = el(
    "div",
    { class: "row registers-row" + (reserved ? " reserved gap" : "") },
    el("code", { text: addressText(field) }),
    el("div", {}, el("div", { text: reserved ? "reserved" : humanise(field.name) }), reserved ? null : el("code", { class: "muted", text: field.name })),
    raw,
    value,
    el("span", { class: "mono", text: reserved ? "reserved" : field.encoding + " · " + field.access }),
    read,
    actions,
  );
  return {
    element,
    raw,
    value,
    read,
    address: field.address,
    block,
    access: field.access,
    search: (field.name + " " + humanise(field.name) + " " + field.address).toLowerCase(),
    previousWords: null,
    changed: false,
  };
}

function gaps(block) {
  const covered = new Set();
  for (const field of block.fields) {
    for (let address = parseInt(field.address, 16); address <= parseInt(field.last_address, 16); address += 1) covered.add(address);
  }
  const missing = [];
  for (let address = parseInt(block.start, 16); address <= parseInt(block.end, 16); address += 1) {
    if (!covered.has(address)) {
      missing.push({ address: hex(address), last_address: hex(address), name: RESERVED_ACCESS, encoding: "", scale: 1, access: RESERVED_ACCESS, words: [0], value: 0, label: null, last_read: null });
    }
  }
  return missing;
}

export function createRegisters() {
  const names = new Set([...description().settings, ...description().commands].map((setting) => setting.name));
  const filter = el("input", { type: "search", placeholder: "Filter by name or address", "aria-label": "Filter registers" });
  const blockSelect = el("select", { "aria-label": "Filter by block" });
  const accessSelect = el("select", { "aria-label": "Filter by access" });
  const changedOnly = switchControl({ label: "Changed only", onChange: applyFilters });
  const reservedSwitch = switchControl({ label: "Show reserved words", onChange: applyFilters });
  const head = el(
    "div",
    { class: "row head registers-row" },
    ...["Address", "Name", "Raw", "Value", "Type", "Read", ""].map((text) => el("span", { text })),
  );
  const tableBox = el("div", { class: "table" }, head);
  const empty = el("div", { class: "empty", text: "No register matches the filter" });
  const element = el(
    "section",
    { class: "view" },
    el("h2", { text: "Registers" }),
    el("div", { class: "toolbar" }, filter, blockSelect, accessSelect, changedOnly.element, reservedSwitch.element),
    tableBox,
    empty,
  );
  let rows = [];
  let blocks = [];
  let signature = null;
  let timer = null;
  let loading = false;
  let loaded = false;

  function structureOf(data) {
    return data.blocks.map((block) => block.start + block.end + block.fields.length).join(",");
  }

  function build(data) {
    rows = [];
    blocks = [];
    tableBox.replaceChildren(head);
    blockSelect.replaceChildren(el("option", { value: "", text: "All blocks" }));
    const accesses = new Set([RESERVED_ACCESS]);
    for (const block of data.blocks) {
      const refusedByModel = block.refusal !== null && block.refusal.model;
      const fields = [...block.fields, ...(refusedByModel ? [] : gaps(block))].sort((first, second) => parseInt(first.address, 16) - parseInt(second.address, 16));
      const blockRows = fields.map((field) => {
        accesses.add(field.access);
        return fieldRow({ field, block: block.start, linkable: names.has(field.name) && field.access !== "read-only" });
      });
      const refusal = block.refusal
        ? el("span", { class: "badge bad", text: "Refused with exception " + block.refusal.code + " by " + [block.refusal.model ? "the model" : null, block.refusal.link ? "a link fault" : null].filter(Boolean).join(" and ") })
        : null;
      const summary = el("summary", {}, el("span", { class: "block-title" }, el("strong", { text: block.name }), el("code", { text: block.start + "–" + block.end }), refusal));
      const details = el("details", { open: true }, summary, ...blockRows.map((row) => row.element));
      blocks.push({ start: block.start, details, rows: blockRows });
      rows.push(...blockRows);
      tableBox.append(details);
      blockSelect.append(el("option", { value: block.start, text: block.name + " " + block.start }));
    }
    accessSelect.replaceChildren(el("option", { value: "", text: "Any access" }), ...[...accesses].map((access) => el("option", { value: access, text: access })));
    signature = structureOf(data);
  }

  function applyFilters() {
    const text = filter.value.trim().toLowerCase();
    const showReserved = reservedSwitch.input.checked;
    let shown = 0;
    for (const block of blocks) {
      let blockShown = 0;
      for (const row of block.rows) {
        const show =
          (showReserved || row.access !== RESERVED_ACCESS) &&
          (!text || row.search.includes(text)) &&
          (!blockSelect.value || blockSelect.value === row.block) &&
          (!accessSelect.value || accessSelect.value === row.access) &&
          (!changedOnly.input.checked || row.changed);
        row.element.hidden = !show;
        if (show) blockShown += 1;
      }
      block.details.hidden = block.rows.length > 0 && blockShown === 0;
      shown += blockShown;
    }
    empty.hidden = shown > 0;
  }

  function refreshReads() {
    const now = serverNow();
    for (const row of rows) row.read.textContent = row.lastRead === null || row.lastRead === undefined ? "never" : elapsed(now - row.lastRead);
  }

  function apply(data) {
    if (structureOf(data) !== signature) {
      build(data);
      loaded = false;
    }
    const byAddress = new Map();
    for (const block of data.blocks) for (const field of block.fields) byAddress.set(field.address, field);
    for (const row of rows) {
      const field = byAddress.get(row.address) || { words: [0], value: 0, label: null, last_read: null };
      const words = wordsText(field.words);
      if (row.previousWords !== null && row.previousWords !== words) {
        highlight(row.value);
        highlight(row.raw);
        row.changed = true;
      }
      row.previousWords = words;
      row.raw.textContent = words;
      row.value.textContent = valueText(field);
      row.lastRead = field.last_read;
    }
    loaded = true;
    refreshReads();
    applyFilters();
  }

  async function load() {
    if (loading) return;
    loading = true;
    try {
      apply(await getJson("/api/registers"));
    } catch {
      loaded = false;
    } finally {
      loading = false;
    }
  }

  filter.addEventListener("input", applyFilters);
  blockSelect.addEventListener("change", applyFilters);
  accessSelect.addEventListener("change", applyFilters);

  return {
    element,
    update() {
      if (loaded) refreshReads();
    },
    activate() {
      load();
      timer = setInterval(load, REFRESH_MILLISECONDS);
    },
    deactivate() {
      clearInterval(timer);
      timer = null;
    },
  };
}
