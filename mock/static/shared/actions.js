import { el } from "./dom.js";
import { icon } from "./icons.js";
import { postJson } from "./requests.js";
import { applyState } from "./state.js";
import { toast } from "./toasts.js";

let dialog = null;

function confirmDialog() {
  if (dialog === null) {
    dialog = el("dialog", { "aria-labelledby": "confirm-title" });
    document.body.append(dialog);
  }
  return dialog;
}

export function confirmAction({ title, message, confirmLabel }) {
  const shown = confirmDialog();
  return new Promise((resolve) => {
    const cancel = el("button", { type: "button", class: "secondary", text: "Cancel", autofocus: true });
    const confirm = el("button", { type: "submit", class: "danger", value: "confirm", text: confirmLabel });
    const form = el(
      "form",
      { method: "dialog" },
      el("h3", { id: "confirm-title", text: title }),
      el("p", { text: message }),
      el("div", { class: "dialog-actions" }, cancel, confirm),
    );
    cancel.addEventListener("click", () => shown.close("cancel"));
    shown.addEventListener("close", () => resolve(shown.returnValue === "confirm"), { once: true });
    shown.returnValue = "cancel";
    shown.replaceChildren(form);
    shown.showModal();
  });
}

export async function send({ path, body, errorSlot, success }) {
  try {
    const result = await postJson(path, body);
    if (!result.ok) {
      if (errorSlot) errorSlot.textContent = result.data.error;
      toast({ kind: "refusal", message: result.data.error });
      return false;
    }
    if (errorSlot) errorSlot.textContent = "";
    applyState(result.data);
    toast({ kind: "success", message: success });
    return true;
  } catch (error) {
    const message = "Request failed: " + error.message;
    if (errorSlot) errorSlot.textContent = message;
    toast({ kind: "refusal", message });
    return false;
  }
}

export function button({ kind = "secondary", label, iconName, title, onClick, iconOnly = false }) {
  const element = el("button", {
    type: "button",
    class: kind + (iconOnly ? " icon-only" : ""),
    title: title || label,
    "aria-label": iconOnly ? label : null,
    on: { click: onClick },
  });
  if (iconName) element.append(icon(iconName));
  if (!iconOnly) element.append(label);
  return element;
}

export function dangerButton({ label, iconName, title, confirmTitle, message, confirmLabel, run }) {
  return button({
    kind: "danger",
    label,
    iconName,
    title,
    onClick: async () => {
      if (await confirmAction({ title: confirmTitle || label, message, confirmLabel: confirmLabel || label })) run();
    },
  });
}

export function switchControl({ label, checked = false, onChange }) {
  const input = el("input", { type: "checkbox", role: "switch", checked });
  input.addEventListener("change", () => onChange(input.checked));
  return { input, element: el("label", { class: "switch" }, input, el("span", { class: "track" }), label ? el("span", { text: label }) : null) };
}

export function changedMark(text = "Changed") {
  return el("span", { class: "mark", hidden: true }, icon("pencil"), text);
}

export function errorSlot() {
  return el("span", { class: "error", role: "alert" });
}
