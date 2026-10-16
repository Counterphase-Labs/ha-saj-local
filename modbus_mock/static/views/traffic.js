import { button, switchControl } from "../shared/actions.js";
import { el, svgEl } from "../shared/dom.js";
import { clockTime, elapsed, hex, humanise, parseNumber, plural, showNumber } from "../shared/format.js";
import { postJson } from "../shared/requests.js";
import { clearTraffic, currentState, refreshTraffic, serverNow, traffic } from "../shared/state.js";

const REFRESH_MILLISECONDS = 1000;
const HISTORY_SECONDS = 30 * 60;
const LOG_ROWS = 300;
const CHART_HEIGHT = 220;
const CHART_MARGIN = { left: 44, right: 8, top: 12, bottom: 28 };
const DEFAULT_CHART_WIDTH = 640;
const NICE_FACTORS = [1, 2, 5, 10];
const ALL = "";

const FUNCTION_NAMES = {
  3: "Read holding registers",
  4: "Read input registers",
  6: "Write single register",
  16: "Write multiple registers",
};

const COUNTER_ROWS = [
  ["Connections opened", "connections_opened"],
  ["Connections closed", "connections_closed"],
  ["Connections refused", "connections_refused"],
  ["Requests", "requests"],
  ["Reads", "reads"],
  ["Writes", "writes"],
  ["Registers read", "registers_read"],
  ["Registers written", "registers_written"],
  ["No answers", "no_answers"],
  ["Dropped connections", "dropped_connections"],
  ["Requests, last 10 s", "requests_last_10_seconds"],
  ["Requests, last 60 s", "requests_last_60_seconds"],
  ["Highest 60 s count", "peak_requests_per_60_seconds"],
];

const CONNECTION_TEXT = {
  opened: "Connection opened",
  closed_by_client: "Connection closed by the client",
  closed_by_module: "Connection closed by the module",
  refused: "Connection refused",
};

function functionText(code) {
  return code + " " + (FUNCTION_NAMES[code] || "Function " + code);
}

function exceptionText(code) {
  return "exception " + hex(code, 2);
}

function answerText(entry) {
  if (entry.answer === "answered") return plural(entry.detail.words.length, "register") + " answered";
  if (entry.answer === "exception") return exceptionText(entry.exception_code);
  if (entry.answer === "no_answer") return "no answer";
  if (entry.answer === "dropped") return "connection dropped";
  return "ignored (another unit)";
}

function isError(entry) {
  if (entry.kind === "connection") return entry.event === "refused" || entry.event === "closed_by_module";
  return entry.answer !== "answered";
}

function niceMaximum(value) {
  const magnitude = 10 ** Math.floor(Math.log10(Math.max(value, 1)));
  const step = NICE_FACTORS.map((factor) => factor * magnitude).find((candidate) => candidate >= value);
  return step || 10 * magnitude;
}

function statBlock(label, value, unit) {
  return el(
    "div",
    { class: "reading" },
    el("span", { class: "value", text: value }),
    el("span", { class: "name", text: label + (unit ? " (" + unit + ")" : "") }),
  );
}

function fieldTable(fields) {
  return el(
    "table",
    { class: "stat-table" },
    el("thead", {}, el("tr", {}, ...["Address", "Name", "Words", "Value"].map((text) => el("th", { text })))),
    el(
      "tbody",
      {},
      ...fields.map((field) =>
        el(
          "tr",
          {},
          el("td", {}, el("code", { text: hex(field.address) })),
          el("td", {}, el("code", { text: field.name })),
          el("td", {}, el("code", { text: field.words.map((word) => hex(word)).join(" ") })),
          el("td", { text: (field.value === null ? "" : typeof field.value === "number" ? showNumber(field.value) : field.value) + (field.label ? " " + field.label : "") }),
        ),
      ),
    ),
  );
}

function entryDetail(entry) {
  if (entry.kind === "connection") {
    return el("div", { class: "log-detail" }, el("span", { text: "Client " + entry.client + ":" + entry.port + ", connection " + entry.connection + ", " + CONNECTION_TEXT[entry.event].toLowerCase() + (entry.reason ? " (" + humanise(entry.reason).toLowerCase() + ")" : "") }));
  }
  const words = entry.detail.words;
  const heading = entry.operation === "write" ? "Words written" : "Words returned";
  return el(
    "div",
    { class: "log-detail" },
    el("span", { text: "Transaction " + entry.transaction_id + ", unit " + entry.unit_id + ", function " + functionText(entry.function) + ", " + hex(entry.start) + " for " + plural(entry.count, "register") }),
    words.length ? el("div", {}, el("strong", { text: heading + ": " }), el("code", { text: words.map((word) => hex(word)).join(" ") })) : el("span", { class: "muted", text: "No words in this entry" }),
    entry.detail.fields.length ? fieldTable(entry.detail.fields) : null,
    entry.late_duplicate ? el("span", { text: "A late duplicate of this answer was sent" }) : null,
  );
}

export function createTraffic() {
  const hero = el("div", { class: "hero" });
  const clientSelect = el("select", { "aria-label": "Graph one client" });
  const legend = el(
    "div",
    { class: "legend" },
    ...[["answered", "Answered"], ["exception", "Exception"], ["unanswered", "No answer or dropped"]].map(([key, text]) => el("span", {}, el("span", { class: "swatch " + key }), text)),
  );
  const chartBox = el("div", { class: "chart-wrap" });
  const countersBox = el("div", { class: "scroll-x" });
  const connectedBox = el("div");
  const functionSelect = el("select", { "aria-label": "Filter by function code" });
  const rangeFrom = el("input", { type: "text", class: "sized", style: "--chars: 8", placeholder: "From address", "aria-label": "From address" });
  const rangeTo = el("input", { type: "text", class: "sized", style: "--chars: 8", placeholder: "To address", "aria-label": "To address" });
  const logClient = el("select", { "aria-label": "Filter by client" });
  const errorsOnly = switchControl({ label: "Errors only", onChange: () => renderLog(true) });
  const paused = switchControl({ label: "Pause", onChange: () => renderLog(true) });
  const logBox = el("div", { class: "table" });
  const reset = button({
    label: "Reset traffic",
    iconName: "restore",
    onClick: async () => {
      const result = await postJson("/api/traffic/reset");
      if (result.ok) clearTraffic(result.data);
      renderAll();
    },
  });
  const element = el(
    "section",
    { class: "view" },
    el("div", { class: "view-heading" }, el("h2", { text: "Traffic" }), reset),
    el("div", { class: "card" }, hero),
    el("div", { class: "card" }, el("div", { class: "toolbar" }, el("h3", { text: "Requests over the last 30 minutes" }), clientSelect), chartBox, legend),
    el("div", { class: "card" }, el("h3", { text: "Counters" }), countersBox),
    el("div", { class: "card" }, el("h3", { text: "Connected clients" }), connectedBox),
    el(
      "div",
      { class: "card" },
      el("h3", { text: "Log, newest first" }),
      el("div", { class: "toolbar" }, functionSelect, rangeFrom, rangeTo, logClient, errorsOnly.element, paused.element),
      logBox,
    ),
  );
  const expanded = new Set();
  let timer = null;
  let loading = false;
  let lastLogSignature = null;

  function renderHero(counters) {
    hero.replaceChildren(
      el("div", { class: "reading" }, el("span", { class: "value", text: counters.total.requests_last_60_seconds }), el("span", { class: "name", text: "Requests per minute (last 60 s)" })),
      statBlock("Registers per minute (last 60 s)", counters.total.registers_last_60_seconds),
      statBlock("Peak requests per minute", counters.total.peak_requests_per_60_seconds),
    );
  }

  function updateClientSelects(counters) {
    const clients = Object.keys(counters.clients);
    for (const select of [clientSelect, logClient]) {
      const current = select.value;
      const known = [...select.options].slice(1).map((option) => option.value).join();
      if (known === clients.join()) continue;
      select.replaceChildren(el("option", { value: ALL, text: "All clients" }), ...clients.map((client) => el("option", { value: client, text: client })));
      select.value = clients.includes(current) ? current : ALL;
    }
  }

  function renderChart(data) {
    const width = chartBox.clientWidth || DEFAULT_CHART_WIDTH;
    const plotWidth = width - CHART_MARGIN.left - CHART_MARGIN.right;
    const plotHeight = CHART_HEIGHT - CHART_MARGIN.top - CHART_MARGIN.bottom;
    const bucketSeconds = data.history.bucket_seconds;
    const bucketCount = HISTORY_SECONDS / bucketSeconds;
    const newest = Math.floor(serverNow() / bucketSeconds) * bucketSeconds;
    const oldest = newest - (bucketCount - 1) * bucketSeconds;
    const source = clientSelect.value ? data.history.clients[clientSelect.value] || [] : data.history.total;
    const byStart = new Map(source.map((bucket) => [bucket.start, bucket]));
    const state = currentState();
    const link = state ? state.link : null;
    const threshold = link && link.lockout_requests > 0 && link.lockout_window_seconds > 0 ? (link.lockout_requests * bucketSeconds) / link.lockout_window_seconds : null;
    const buckets = Array.from({ length: bucketCount }, (_, index) => {
      const start = oldest + index * bucketSeconds;
      return { start, ...(byStart.get(start) || { answered: 0, exception: 0, unanswered: 0 }) };
    });
    const tallest = Math.max(...buckets.map((bucket) => bucket.answered + bucket.exception + bucket.unanswered), threshold || 0);
    const maximum = niceMaximum(tallest);
    const scaleY = (value) => CHART_MARGIN.top + plotHeight - (value / maximum) * plotHeight;
    const barWidth = plotWidth / bucketCount;
    const svg = svgEl("svg", { class: "chart", width, height: CHART_HEIGHT, role: "img", "aria-label": "Requests per 10 second bucket over the last 30 minutes" });
    svg.append(
      svgEl("line", { class: "axis", x1: CHART_MARGIN.left, y1: scaleY(0), x2: width - CHART_MARGIN.right, y2: scaleY(0) }),
      svgEl("text", { x: CHART_MARGIN.left - 6, y: scaleY(0), "text-anchor": "end", text: "0" }),
      svgEl("text", { x: CHART_MARGIN.left - 6, y: scaleY(maximum) + 12, "text-anchor": "end", text: showNumber(maximum) }),
      svgEl("text", { x: CHART_MARGIN.left, y: CHART_HEIGHT - 8, text: "30 min ago" }),
      svgEl("text", { x: CHART_MARGIN.left + plotWidth / 2, y: CHART_HEIGHT - 8, "text-anchor": "middle", text: "15 min ago" }),
      svgEl("text", { x: width - CHART_MARGIN.right, y: CHART_HEIGHT - 8, "text-anchor": "end", text: "now" }),
    );
    buckets.forEach((bucket, index) => {
      let base = 0;
      const x = CHART_MARGIN.left + index * barWidth;
      const group = svgEl("g", {}, svgEl("title", { text: clockTime(bucket.start) + ": " + bucket.answered + " answered, " + bucket.exception + " exception, " + bucket.unanswered + " no answer or dropped" }));
      for (const kind of ["answered", "exception", "unanswered"]) {
        if (bucket[kind] === 0) continue;
        group.append(svgEl("rect", { class: "bar " + kind, x, width: Math.max(barWidth - 1, 1), y: scaleY(base + bucket[kind]), height: (bucket[kind] / maximum) * plotHeight }));
        base += bucket[kind];
      }
      svg.append(group);
    });
    if (threshold !== null) {
      svg.append(
        svgEl("line", { class: "threshold", x1: CHART_MARGIN.left, x2: width - CHART_MARGIN.right, y1: scaleY(threshold), y2: scaleY(threshold) }),
        svgEl("text", { class: "threshold-label", x: width - CHART_MARGIN.right, y: scaleY(threshold) - 4, "text-anchor": "end", text: "Lockout at " + showNumber(Number(threshold.toFixed(2))) + " per " + bucketSeconds + " s" }),
      );
    }
    chartBox.replaceChildren(svg);
  }

  function renderCounters(counters) {
    const clients = Object.keys(counters.clients);
    const columns = [["Total", counters.total], ...clients.map((client) => [client, counters.clients[client]])];
    const exceptionsText = (stats) => Object.entries(stats.exceptions).map(([code, count]) => hex(Number(code), 2) + " × " + count).join(", ") || "none";
    countersBox.replaceChildren(
      el(
        "table",
        { class: "stat-table" },
        el("thead", {}, el("tr", {}, el("th", { text: "Counter" }), ...columns.map(([name]) => el("th", { text: name })))),
        el(
          "tbody",
          {},
          ...COUNTER_ROWS.map(([label, key]) => el("tr", {}, el("td", { text: label }), ...columns.map(([, stats]) => el("td", { text: stats[key] })))),
          el("tr", {}, el("td", { text: "Exceptions by code" }), ...columns.map(([, stats]) => el("td", { text: exceptionsText(stats) }))),
          el(
            "tr",
            {},
            el("td", { text: "Last request" }),
            ...columns.map(([, stats]) => el("td", { text: stats.last_request_at === null ? "never" : elapsed(serverNow() - stats.last_request_at) })),
          ),
        ),
      ),
    );
    connectedBox.replaceChildren(
      counters.connected.length === 0
        ? el("span", { class: "muted", text: "No client is connected" })
        : el(
            "table",
            { class: "stat-table" },
            el("thead", {}, el("tr", {}, ...["Connection", "Client", "Connected"].map((text) => el("th", { text })))),
            el("tbody", {}, ...counters.connected.map((entry) => el("tr", {}, el("td", { text: entry.connection }), el("td", { text: entry.client + ":" + entry.port }), el("td", { text: elapsed(serverNow() - entry.since) })))),
          ),
    );
  }

  function updateFunctionSelect(log) {
    const codes = [...new Set(log.filter((entry) => entry.kind === "request").map((entry) => entry.function))].sort((first, second) => first - second);
    const known = [...functionSelect.options].slice(1).map((option) => option.value).join();
    if (known === codes.join()) return;
    const current = functionSelect.value;
    functionSelect.replaceChildren(el("option", { value: ALL, text: "All function codes" }), ...codes.map((code) => el("option", { value: code, text: functionText(code) })));
    functionSelect.value = codes.map(String).includes(current) ? current : ALL;
  }

  function matches(entry) {
    if (logClient.value && entry.client !== logClient.value) return false;
    if (errorsOnly.input.checked && !isError(entry)) return false;
    const from = parseNumber(rangeFrom.value);
    const to = parseNumber(rangeTo.value);
    const filtersRequests = functionSelect.value !== ALL || Number.isFinite(from) || Number.isFinite(to);
    if (entry.kind === "connection") return !filtersRequests;
    if (functionSelect.value !== ALL && String(entry.function) !== functionSelect.value) return false;
    const last = entry.start + Math.max(entry.count, 1) - 1;
    if (Number.isFinite(from) && last < from) return false;
    if (Number.isFinite(to) && entry.start > to) return false;
    return true;
  }

  function logRow(entry) {
    const request = entry.kind === "request";
    const summary = request
      ? functionText(entry.function) + " · " + hex(entry.start) + " × " + entry.count
      : CONNECTION_TEXT[entry.event] + (entry.reason ? " (" + humanise(entry.reason).toLowerCase() + ")" : "");
    const faultText = request ? [entry.fault ? humanise(entry.fault) : null, entry.late_duplicate ? "late duplicate" : null].filter(Boolean).join(" + ") : "";
    const row = el(
      "div",
      { class: "row log-row" + (isError(entry) ? " error-row" : ""), tabindex: 0, role: "button", "aria-expanded": String(expanded.has(entry.sequence)) },
      el("span", { class: "mono", text: clockTime(entry.at) }),
      el("code", { text: entry.client + ":" + entry.port }),
      el("span", { class: "mono", text: "#" + entry.connection }),
      el("span", { text: summary }),
      el("span", { text: request ? answerText(entry) : "" }),
      el("span", { text: faultText }),
      el("span", { class: "mono", text: request ? Math.round(entry.duration_ms) + " ms" : "" }),
    );
    const toggle = () => {
      if (expanded.has(entry.sequence)) expanded.delete(entry.sequence);
      else expanded.add(entry.sequence);
      renderLog(true);
    };
    row.addEventListener("click", toggle);
    row.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        toggle();
      }
    });
    return expanded.has(entry.sequence) ? [row, entryDetail(entry)] : [row];
  }

  function renderLog(force = false) {
    if (paused.input.checked && !force) return;
    const { log, latestSequence } = traffic();
    updateFunctionSelect(log);
    const signature = [latestSequence, log.length, functionSelect.value, rangeFrom.value, rangeTo.value, logClient.value, errorsOnly.input.checked, [...expanded].join()].join("|");
    if (signature === lastLogSignature) return;
    lastLogSignature = signature;
    const shown = [];
    for (let index = log.length - 1; index >= 0 && shown.length < LOG_ROWS; index -= 1) {
      if (matches(log[index])) shown.push(log[index]);
    }
    const head = el(
      "div",
      { class: "row head log-row" },
      ...["Time", "Client", "Conn", "Request", "Answer", "Link fault", "Took"].map((text) => el("span", { text })),
    );
    logBox.replaceChildren(head, ...(shown.length ? shown.flatMap(logRow) : [el("div", { class: "empty", text: "No entries match" })]));
  }

  function renderAll() {
    const data = traffic();
    if (data.counters === null) return;
    renderHero(data.counters);
    updateClientSelects(data.counters);
    renderChart(data);
    renderCounters(data.counters);
    renderLog();
  }

  clientSelect.addEventListener("change", renderAll);
  for (const control of [functionSelect, rangeFrom, rangeTo, logClient]) control.addEventListener("input", () => renderLog(true));

  async function load() {
    if (loading) return;
    loading = true;
    try {
      await refreshTraffic();
    } finally {
      loading = false;
    }
  }

  return {
    element,
    update() {
      if (!element.hidden) renderAll();
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
