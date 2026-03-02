import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import InsightsPanel from '../InsightsPanel';
import * as client from '../../api/client';

// Mock API response so the test is deterministic and does not call a real backend.
beforeEach(() => {
  jest.spyOn(client, 'getKpis').mockResolvedValue({
    units_sold_per_slot: { A: 10, B: 5 },
    revenue_by_hour: [
      { timestamp: '2026-02-28T00:00:00Z', revenue: 100 },
      { timestamp: '2026-02-28T01:00:00Z', revenue: 50 },
    ],
  });
});

afterEach(() => {
  jest.restoreAllMocks();
});

describe('InsightsPanel', () => {
  test('renders chart and allows switching metrics', async () => {
    // Any non-empty token is fine because API calls are mocked.
    render(<InsightsPanel token="test-token" />);
    expect(screen.getByText(/loading insights/i)).toBeInTheDocument();
    await waitFor(() => screen.getByText(/visualization/i));

    // default should show units chart
    expect(screen.getByText(/units sold per slot/i)).toBeInTheDocument();

    // switch to revenue
    fireEvent.change(screen.getByLabelText(/select metric/i), {
      target: { value: 'revenue' },
    });
    expect(screen.getByText(/revenue over time/i)).toBeInTheDocument();
  });
});
