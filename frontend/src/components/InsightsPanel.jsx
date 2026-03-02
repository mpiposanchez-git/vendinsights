import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { getKpis } from '../api/client';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
} from 'recharts';

// Shows chart-based KPI views (units sold and revenue over time).
export default function InsightsPanel({ token }) {
  const [kpis, setKpis] = useState(null);
  const [error, setError] = useState(null);
  const [metric, setMetric] = useState('units');

  useEffect(() => {
    // Only fetch data when the user has a valid auth token.
    if (!token) {
      return;
    }
    getKpis(token)
      .then(setKpis)
      .catch((err) => setError(err.toString()));
  }, [token]);

  if (error) return <div className="error">Error loading insights: {error}</div>;
  if (!kpis) return <div>Loading insights…</div>;

  // Convert slot dictionary into chart-friendly objects.
  const slotData = kpis.units_sold_per_slot
    ? Object.entries(kpis.units_sold_per_slot).map(([slot, qty]) => ({ slot, qty }))
    : [];

  // Revenue time-series already arrives in chart-ready format.
  const revenueData = kpis.revenue_by_hour || [];

  return (
    <div className="insights-panel">
      <h2>Visualization</h2>
      <div className="form-group">
        <label>
          Select metric:&nbsp;
          <select value={metric} onChange={(e) => setMetric(e.target.value)}>
            <option value="units">Units sold per slot</option>
            <option value="revenue">Revenue over time</option>
          </select>
        </label>
      </div>

      {metric === 'units' && slotData.length > 0 && (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={slotData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="slot" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="qty" fill="#8884d8" name="Units sold" />
          </BarChart>
        </ResponsiveContainer>
      )}

      {metric === 'revenue' && revenueData.length > 0 && (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={revenueData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="timestamp" tickFormatter={(t) => t.slice(11, 16)} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="revenue" fill="#82ca9d" name="Revenue" />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}

InsightsPanel.propTypes = {
  token: PropTypes.string.isRequired,
};
