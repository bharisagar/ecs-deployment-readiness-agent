const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    },
    ...options
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed with ${response.status}`);
  }
  return response.json();
}

export function fetchHealth() {
  return request("/health");
}

export function fetchSampleConfig() {
  return request("/config/sample");
}

export function runReadinessCheck(payload) {
  return request("/readiness/check", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function fetchReport(reportId) {
  return request(`/readiness/report/${reportId}`);
}

export function fetchHistory() {
  return request("/readiness/history");
}
