import React from 'react';
import KpiTable from './components/KpiTable';
import InsightsPanel from './components/InsightsPanel';
import AskBox from './components/AskBox';

export default function App() {
  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Vending Insights</h1>
      </header>
      <main className="app-main">
        <section className="card">
          <KpiTable />
        </section>
        <section className="card">
          <InsightsPanel />
        </section>
        <section className="card">
          <AskBox />
        </section>
      </main>
    </div>
  );
}
