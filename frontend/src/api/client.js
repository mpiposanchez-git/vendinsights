// Optional base URL, useful when frontend and backend are hosted separately.
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || '';

function toApiUrl(path) {
  // Allow absolute URLs for flexibility while still supporting relative API paths.
  if (path.startsWith('http')) {
    return path;
  }
  return `${API_BASE_URL}${path}`;
}

export async function request(url, options) {
  // Centralized request helper: all API calls share the same error handling.
  const res = await fetch(toApiUrl(url), options);
  if (!res.ok) throw new Error('Network response was not ok');
  return res.json();
}

// Domain-specific wrapper for KPI retrieval.
export async function getKpis(token) {
  try {
    return await request('/api/kpis', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  } catch (error) {
    // Optional demo mode: fallback to static sample data when backend is unavailable.
    if (process.env.REACT_APP_ALLOW_SAMPLE_FALLBACK !== 'true') {
      throw error;
    }
    return await request('/kpis.json');
  }
}

export async function login(username, password) {
  // Sends credentials and expects a JWT token response from the backend.
  return request('/api/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });
}
