import { el, whenIdle } from "./dom.js";
import { errorSlot, send } from "./actions.js";
import { parseNumber } from "./format.js";

const PACK_CODE_MAXIMUM = 65535;

export function createPackCodes(pack) {
  const errors = errorSlot();
  const codeField = (kind) =>
    el("input", { type: "number", min: 0, max: PACK_CODE_MAXIMUM, step: 1, style: "--chars: 5", "aria-label": "Pack " + pack + " " + kind + " code" });
  const fault = codeField("fault");
  const warning = codeField("warning");
  const apply = () =>
    send({
      path: "/api/faults",
      body: { packs: { [pack]: { fault: parseNumber(fault.value), warning: parseNumber(warning.value) } } },
      errorSlot: errors,
      success: "Pack " + pack + " codes set to " + fault.value + " and " + warning.value,
    });
  fault.addEventListener("change", apply);
  warning.addEventListener("change", apply);
  const inputs = el("div", { class: "control-input" }, "Fault code", fault, "Warning code", warning);
  function update(state, container) {
    const codes = (state.faults.packs || {})[pack] || { fault: 0, warning: 0 };
    whenIdle(container, () => {
      fault.value = codes.fault;
      warning.value = codes.warning;
    });
    return codes.fault !== 0 || codes.warning !== 0;
  }
  return { inputs, errors, update };
}
