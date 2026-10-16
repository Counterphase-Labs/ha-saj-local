import { el } from "./shared/dom.js";
import { icon } from "./shared/icons.js";
import { setViewShower, takeIntent } from "./shared/navigation.js";
import { loadDescription, onChange, refreshState, refreshTraffic } from "./shared/state.js";
import { createStatusBar } from "./shared/statusbar.js";
import { mountToasts } from "./shared/toasts.js";
import { createFaults } from "./views/faults.js";
import { createLink } from "./views/link.js";
import { createOverview } from "./views/overview.js";
import { createRegisters } from "./views/registers.js";
import { createScenario } from "./views/scenario.js";
import { createSettings } from "./views/settings.js";
import { createTraffic } from "./views/traffic.js";

const POLL_MILLISECONDS = 3000;
const DEFAULT_VIEW = "overview";

const VIEWS = [
  { key: "overview", label: "Overview", iconName: "layout-dashboard", create: createOverview },
  { key: "faults", label: "Faults", iconName: "alert-triangle", create: createFaults },
  { key: "settings", label: "Settings", iconName: "settings", create: createSettings },
  { key: "registers", label: "Registers", iconName: "table", create: createRegisters },
  { key: "traffic", label: "Traffic", iconName: "activity", create: createTraffic },
  { key: "link", label: "Link", iconName: "network", create: createLink },
  { key: "scenario", label: "Scenario", iconName: "adjustments", create: createScenario },
];

async function start() {
  mountToasts(document.getElementById("toasts"));
  await loadDescription();
  const statusBar = createStatusBar();
  const tabs = el("nav", { class: "tabs", "aria-label": "Views" });
  const main = document.getElementById("view");
  const views = new Map();
  let active = null;

  for (const spec of VIEWS) {
    const view = spec.create();
    view.element.hidden = true;
    views.set(spec.key, { ...view, tab: el("a", { class: "tab", href: "#" + spec.key }, icon(spec.iconName), spec.label) });
    main.append(view.element);
    tabs.append(views.get(spec.key).tab);
  }
  document.getElementById("status").replaceWith(statusBar.element);
  statusBar.element.after(tabs);

  function show(key) {
    const next = views.has(key) ? key : DEFAULT_VIEW;
    const intent = takeIntent();
    if (active !== null && active !== next) {
      views.get(active).element.hidden = true;
      views.get(active).tab.removeAttribute("aria-current");
      views.get(active).deactivate();
    }
    const view = views.get(next);
    view.element.hidden = false;
    view.tab.setAttribute("aria-current", "page");
    if (active !== next) window.scrollTo(0, 0);
    active = next;
    view.activate(intent);
  }

  setViewShower(show);
  window.addEventListener("hashchange", () => show(location.hash.slice(1)));

  onChange(() => {
    statusBar.update();
    if (active !== null) views.get(active).update();
  });

  await Promise.all([refreshState(), refreshTraffic()]);
  show(location.hash.slice(1));
  setInterval(() => {
    refreshState();
    refreshTraffic();
  }, POLL_MILLISECONDS);
}

start().catch((error) => {
  document.getElementById("view").textContent = "Could not load the page: " + error.message;
});

