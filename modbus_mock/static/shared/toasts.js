const MAXIMUM_TOASTS = 3;
const TOAST_MILLISECONDS = 4000;

let container = null;

export function mountToasts(element) {
  container = element;
}

export function toast({ kind, message }) {
  const entry = document.createElement("div");
  entry.className = "toast " + kind;
  entry.setAttribute("role", kind === "refusal" ? "alert" : "status");
  entry.textContent = message;
  container.append(entry);
  while (container.children.length > MAXIMUM_TOASTS) container.firstElementChild.remove();
  setTimeout(() => entry.remove(), TOAST_MILLISECONDS);
}
