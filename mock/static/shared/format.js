const HEX_RADIX = 16;
const SECONDS_PER_MINUTE = 60;
const SECONDS_PER_HOUR = 3600;

export function humanise(name) {
  const words = name.replace(/_/g, " ").trim();
  return words.charAt(0).toUpperCase() + words.slice(1);
}

const UNIT_WORDS = { "%": ["percent"], s: ["s", "seconds"] };

export function humaniseWithoutUnit(name, unit) {
  const words = name.split("_");
  const unitWords = unit ? [unit.toLowerCase(), ...(UNIT_WORDS[unit] || [])] : [];
  if (words.length > 1 && unitWords.includes(words[words.length - 1])) words.pop();
  return humanise(words.join("_"));
}

export function hex(value, digits = 4) {
  return "0x" + value.toString(HEX_RADIX).toUpperCase().padStart(digits, "0");
}

export function parseNumber(text) {
  const trimmed = String(text).trim();
  return trimmed === "" ? Number.NaN : Number(trimmed);
}

export function decimalsOf(step) {
  const text = String(step);
  const point = text.indexOf(".");
  return point === -1 ? 0 : text.length - point - 1;
}

export function inputChars({ maximum, step }) {
  const decimals = decimalsOf(step);
  return String(Math.trunc(Math.abs(maximum))).length + (decimals ? decimals + 1 : 0) + 1;
}

export function showNumber(value) {
  if (typeof value !== "number") return String(value);
  return Number.isInteger(value) ? String(value) : String(Number(value.toFixed(4)));
}

export function showTime(isoText) {
  return isoText.replace("T", " ");
}

export function clockTime(epochSeconds) {
  return new Date(epochSeconds * 1000).toLocaleTimeString([], { hour12: false });
}

export function elapsed(seconds) {
  if (seconds < 0) return "0 s ago";
  if (seconds < SECONDS_PER_MINUTE) return Math.floor(seconds) + " s ago";
  if (seconds < SECONDS_PER_HOUR) return Math.floor(seconds / SECONDS_PER_MINUTE) + " min ago";
  return Math.floor(seconds / SECONDS_PER_HOUR) + " h ago";
}

export function plural(count, singular, pluralForm = singular + "s") {
  return count + " " + (count === 1 ? singular : pluralForm);
}
