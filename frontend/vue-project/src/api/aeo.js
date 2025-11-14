const API_BASE = import.meta.env.VITE_API_BASE_URL;

export async function analyzeWebsite(payload) {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (!res.ok) throw new Error("Failed to fetch analysis");
  return await res.json();
}
