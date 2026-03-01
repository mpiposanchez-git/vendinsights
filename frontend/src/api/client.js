const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || '';

function toApiUrl(path) {
  if (path.startsWith('http')) {
    return path;
  }
  return `${API_BASE_URL}${path}`;
}

export async function request(url, options) {
  const res = await fetch(toApiUrl(url), options);
  if (!res.ok) throw new Error('Network response was not ok');
  return res.json();
}

// thin wrappers for domain API calls
export async function getKpis(token) {
  try {
    return await request('/api/kpis', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  } catch (error) {
    if (process.env.REACT_APP_ALLOW_SAMPLE_FALLBACK !== 'true') {
      throw error;
    }
    return await request('/kpis.json');
  }
}

export async function login(username, password) {
  return request('/api/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });
}
