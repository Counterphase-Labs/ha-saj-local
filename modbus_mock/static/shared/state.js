import { getJson } from "./requests.js";

const TRAFFIC_LOG_LIMIT = 2000;
const MILLISECONDS = 1000;

const store = {
  description: null,
  state: null,
  answering: true,
  latestSequence: 0,
  log: [],
  counters: null,
  history: null,
  clockOffset: 0,
  fetchedAt: 0,
};
const listeners = new Set();

function notify() {
  for (const listener of listeners) listener();
}

export function onChange(listener) {
  listeners.add(listener);
}

export async function loadDescription() {
  store.description = await getJson("/api/description");
  return store.description;
}

export const description = () => store.description;
export const currentState = () => store.state;
export const isAnswering = () => store.answering;
export const traffic = () => store;

export function applyState(state) {
  store.state = state;
  store.answering = true;
  notify();
}

export async function refreshState() {
  try {
    applyState(await getJson("/api/state"));
  } catch {
    store.answering = false;
    notify();
  }
}

function takeTraffic(data) {
  if (data.latest < store.latestSequence) {
    store.log = [];
    store.latestSequence = 0;
  }
  for (const entry of data.entries) {
    store.log.push(entry);
    store.latestSequence = entry.sequence;
  }
  if (store.log.length > TRAFFIC_LOG_LIMIT) store.log.splice(0, store.log.length - TRAFFIC_LOG_LIMIT);
  store.counters = data.counters;
  store.history = data.history;
  store.clockOffset = data.now - Date.now() / MILLISECONDS;
  store.fetchedAt = Date.now() / MILLISECONDS;
}

export async function refreshTraffic() {
  try {
    takeTraffic(await getJson("/api/traffic?after=" + store.latestSequence));
  } catch {
    store.answering = false;
  }
  notify();
}

export function clearTraffic(data) {
  store.log = [];
  store.latestSequence = data.latest;
  takeTraffic({ ...data, entries: [], latest: data.latest });
  notify();
}

export function serverNow() {
  return Date.now() / MILLISECONDS + store.clockOffset;
}
