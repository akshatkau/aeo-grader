const API_BASE = "http://127.0.0.1:8000/api";   // Use 127.0.0.1 not localhost

export async function analyzeWebsite(payload) {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (!res.ok) throw new Error("Failed to fetch analysis");
  return await res.json();
}
