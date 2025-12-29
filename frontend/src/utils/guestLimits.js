const KEY = "guest_usage_v1";

function load() {
  try {
    return JSON.parse(localStorage.getItem(KEY) || "{}");
  } catch {
    return {};
  }
}

function save(v) {
  localStorage.setItem(KEY, JSON.stringify(v));
}

export function remaining(featureKey, limit) {
  const used = Number(load()[featureKey] || 0);
  return Math.max(limit - used, 0);
}

export function consume(featureKey) {
  const s = load();
  s[featureKey] = Number(s[featureKey] || 0) + 1;
  save(s);
}
