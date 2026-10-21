export async function getJson(path) {
  const response = await fetch(path);
  if (!response.ok) throw new Error(path + " answered " + response.status);
  return response.json();
}

export async function postJson(path, body) {
  const options = { method: "POST" };
  if (body !== undefined) {
    options.headers = { "Content-Type": "application/json" };
    options.body = JSON.stringify(body);
  }
  const response = await fetch(path, options);
  return { ok: response.ok, data: await response.json() };
}
