const ICON_FOLDER = "/static/vendor/tabler/";
const cache = new Map();

function load(name) {
  if (!cache.has(name)) {
    cache.set(
      name,
      fetch(ICON_FOLDER + name + ".svg")
        .then((response) => response.text())
        .then((text) => new DOMParser().parseFromString(text, "image/svg+xml").documentElement),
    );
  }
  return cache.get(name);
}

export function icon(name) {
  const holder = document.createElement("span");
  holder.className = "icon";
  holder.setAttribute("aria-hidden", "true");
  load(name)
    .then((svg) => holder.replaceChildren(document.importNode(svg, true)))
    .catch(() => holder.replaceChildren());
  return holder;
}

export function iconNode(name, attributes) {
  const placeholder = document.createElementNS("http://www.w3.org/2000/svg", "g");
  load(name)
    .then((svg) => {
      const copy = document.importNode(svg, true);
      for (const [key, value] of Object.entries(attributes)) copy.setAttribute(key, value);
      placeholder.replaceChildren(copy);
    })
    .catch(() => placeholder.replaceChildren());
  return placeholder;
}
