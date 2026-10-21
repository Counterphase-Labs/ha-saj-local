let showView = () => {};
let pendingIntent = null;

export function setViewShower(shower) {
  showView = shower;
}

export function takeIntent() {
  const intent = pendingIntent;
  pendingIntent = null;
  return intent;
}

export function go(key, intent = null) {
  pendingIntent = intent;
  if (location.hash === "#" + key) showView(key);
  else location.hash = key;
}
