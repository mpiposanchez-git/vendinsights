import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { askLumo, getLumoMode } from '../api/client';

// Lumo+ panel for natural-language questions over KPI + telemetry data.
export default function AskBox({ token }) {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState('local');

  useEffect(() => {
    let mounted = true;
    async function loadMode() {
      try {
        const response = await getLumoMode(token);
        if (mounted && response?.active_mode) {
          setMode(response.active_mode);
        }
      } catch {
        if (mounted) {
          setMode('local');
        }
      }
    }
    loadMode();
    return () => {
      mounted = false;
    };
  }, [token]);

  async function handleAsk(event) {
    event.preventDefault();
    if (!question.trim()) {
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await askLumo(token, question.trim());
      setAnswer(response.answer || 'No response received.');
    } catch (requestError) {
      setError(requestError.toString());
    } finally {
      setLoading(false);
    }
  }

  const lines = answer ? answer.split('\n') : [];
  const actionPlanHeader = 'Action plan (next 7 days):';
  const actionPlanIndex = lines.findIndex((line) => line.trim() === actionPlanHeader);
  const summaryText = actionPlanIndex >= 0 ? lines.slice(0, actionPlanIndex).join('\n') : answer;
  const actionPlanItems =
    actionPlanIndex >= 0
      ? lines
          .slice(actionPlanIndex + 1)
          .map((line) => line.trim())
          .filter(Boolean)
          .map((line) => line.replace(/^\d+\.\s*/, ''))
      : [];

  return (
    <div className="ask-box">
      <div className="ask-header">
        <h2>Lumo+</h2>
        <span className={`mode-badge mode-${mode}`}>Mode: {mode === 'openai' ? 'OpenAI' : 'Local AI'}</span>
      </div>
      <p className="ask-help">Ask about KPI trends, payment issues, stockouts, or machine performance.</p>
      <form onSubmit={handleAsk} className="ask-form">
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Example: Which machines look at risk of stockouts and why?"
          rows={4}
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Thinking…' : 'Ask Lumo+'}
        </button>
      </form>

      {error && <div className="error">Error: {error}</div>}

      {answer && (
        <div className="ask-answer">
          <h3>Answer</h3>
          <pre className="ask-answer-text">{summaryText}</pre>
          {actionPlanItems.length > 0 && (
            <div className="ask-action-plan">
              <h4>Action Plan (Next 7 Days)</h4>
              <ol>
                {actionPlanItems.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ol>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

AskBox.propTypes = {
  token: PropTypes.string.isRequired,
};
