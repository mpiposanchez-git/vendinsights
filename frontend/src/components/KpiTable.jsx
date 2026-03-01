import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { getKpis } from '../api/client';

export default function KpiTable({ token }) {
  const [kpis, setKpis] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!token) {
      return;
    }
    getKpis(token)
      .then(setKpis)
      .catch((err) => setError(err.toString()));
  }, [token]);

  if (error) return <div className="error">Error loading KPIs: {error}</div>;
  if (!kpis) return <div>Loading KPIs…</div>;

  return (
    <div className="kpi-table-container">
      <table className="kpi-table">
        <thead>
          <tr>
            <th>KPI</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(kpis).map(([key, val]) => (
            <tr key={key}>
              <td>{key.replace(/_/g, ' ')}</td>
              <td>{typeof val === 'object' ? JSON.stringify(val) : val}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

KpiTable.propTypes = {
  token: PropTypes.string.isRequired,
};
