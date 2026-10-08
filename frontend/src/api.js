const BASE = "http://localhost:5000/api";

// VULN: token kept in localStorage, readable by any injected JS (XSS -> token theft).
export function getToken() {
  return localStorage.getItem("token");
}

export async function api(path, options = {}) {
  const token = getToken();
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (token) headers.Authorization = `Bearer ${token}`;
  const res = await fetch(`${BASE}${path}`, { ...options, headers });
  return res.json();
}
