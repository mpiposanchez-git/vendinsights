export async function request(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error('Network response was not ok');
  return res.json();
}

// thin wrappers for domain API calls
export async function getKpis() {
  try {
    return await request('/api/kpis');
  } catch {
    // fall back to a static sample (useful during development)
    return await request('/kpis.json');
  }
}
