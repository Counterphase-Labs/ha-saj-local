import { el, whenIdle } from "./dom.js";
import { send } from "./actions.js";
import { humanise, inputChars, parseNumber, showNumber } from "./format.js";

const TEXT_SETTING_STEP = 1;

export function optionLabel(option) {
  return option.label === null ? String(option.value) : option.value + " " + option.label;
}

export function describeValue(setting, entry) {
  if (setting.options) {
    const match = setting.options.find((option) => option.value === entry.raw);
    return match ? optionLabel(match) : String(entry.raw);
  }
  if (setting.text) return String(entry.raw);
  return setting.scale === 1 ? String(entry.raw) : showNumber(entry.value) + " (raw " + entry.raw + ")";
}

export function createSettingControl({ setting, errorSlot, applyTo = "/api/settings" }) {
  let input;
  if (setting.options) {
    input = el("select", { "aria-label": humanise(setting.name) });
    for (const option of setting.options) input.append(el("option", { value: option.value, text: optionLabel(option) }));
  } else if (setting.text) {
    input = el("input", {
      type: "text",
      class: "sized",
      maxlength: setting.max_length,
      style: "--chars: " + setting.max_length,
      "aria-label": humanise(setting.name),
    });
  } else {
    input = el("input", {
      type: "number",
      step: 1,
      min: setting.minimum,
      max: setting.maximum,
      style: "--chars: " + inputChars({ maximum: Math.max(Math.abs(setting.minimum), Math.abs(setting.maximum)), step: TEXT_SETTING_STEP }),
      "aria-label": humanise(setting.name),
    });
  }
  const scaled = el("span", { class: "muted mono" });
  input.addEventListener("change", () => {
    const value = setting.text ? input.value : parseNumber(input.value);
    send({
      path: applyTo,
      body: { [setting.name]: value },
      errorSlot,
      success: humanise(setting.name) + " set to " + (setting.options ? input.selectedOptions[0].textContent : input.value),
    });
  });
  function update(state) {
    const entry = state.settings[setting.name];
    if (!entry) return;
    whenIdle(input, () => {
      input.value = entry.raw;
    });
    scaled.textContent = setting.scale === 1 || setting.text || setting.options ? "" : "= " + showNumber(entry.value);
  }
  return { input, scaled, update };
}
