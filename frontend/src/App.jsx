import React, { useState } from 'react';
import KpiTable from './components/KpiTable';
import InsightsPanel from './components/InsightsPanel';
import AskBox from './components/AskBox';
import { login } from './api/client';

export default function App() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [token, setToken] = useState(localStorage.getItem('authToken'));

  async function handleLogin(event) {
    event.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const response = await login(username, password);
      localStorage.setItem('authToken', response.access_token);
      setToken(response.access_token);
      setPassword('');
    } catch {
      setError('Invalid username or password.');
    } finally {
      setLoading(false);
    }
  }

  function handleLogout() {
    localStorage.removeItem('authToken');
    setToken(null);
  }

  if (!token) {
    return (
      <div className="app-container">
        <header className="app-header">
          <h1>Vending Insights</h1>
        </header>
        <main className="app-main">
          <section className="card login-card">
            <h2>Sign In</h2>
            <form onSubmit={handleLogin} className="login-form">
              <label>
                Username
                <input
                  type="text"
                  value={username}
                  onChange={(event) => setUsername(event.target.value)}
                  required
                />
              </label>
              <label>
                Password
                <input
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  required
                />
              </label>
              <button type="submit" disabled={loading}>
                {loading ? 'Signing in…' : 'Sign In'}
              </button>
              {error && <div className="error">{error}</div>}
            </form>
          </section>
        </main>
      </div>
    );
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Vending Insights</h1>
        <button type="button" className="logout-button" onClick={handleLogout}>
          Logout
        </button>
      </header>
      <main className="app-main">
        <section className="card">
          <KpiTable token={token} />
        </section>
        <section className="card">
          <InsightsPanel token={token} />
        </section>
        <section className="card">
          <AskBox />
        </section>
      </main>
    </div>
  );
}
