const SVG_NAMESPACE = "http://www.w3.org/2000/svg";
const PROPERTY_ATTRIBUTES = new Set(["value", "checked", "hidden", "disabled", "selected"]);

function applyAttributes(element, attributes) {
  for (const [name, value] of Object.entries(attributes)) {
    if (value === null || value === undefined || value === false) continue;
    if (name === "text") element.textContent = value;
    else if (name === "on") {
      for (const [type, listener] of Object.entries(value)) element.addEventListener(type, listener);
    } else if (PROPERTY_ATTRIBUTES.has(name)) element[name] = value;
    else element.setAttribute(name, value === true ? "" : value);
  }
}

export function el(tag, attributes = {}, ...children) {
  const element = document.createElement(tag);
  applyAttributes(element, attributes);
  element.append(...children.filter((child) => child !== null && child !== undefined && child !== false));
  return element;
}

export function svgEl(tag, attributes = {}, ...children) {
  const element = document.createElementNS(SVG_NAMESPACE, tag);
  applyAttributes(element, attributes);
  element.append(...children.filter((child) => child !== null && child !== undefined && child !== false));
  return element;
}

export function hasFocus(element) {
  return element === document.activeElement || element.contains(document.activeElement);
}

export function whenIdle(element, update) {
  if (!hasFocus(element)) update();
}

const FLASH_MILLISECONDS = 2000;

export function reveal(element) {
  for (let parent = element.parentElement; parent; parent = parent.parentElement) {
    if (parent.tagName === "DETAILS") parent.open = true;
  }
  element.scrollIntoView({ behavior: "smooth", block: "center" });
  element.classList.add("flash");
  setTimeout(() => element.classList.remove("flash"), FLASH_MILLISECONDS);
}
