// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows: expect(...).toBeInTheDocument()
import '@testing-library/jest-dom';

// Recharts uses ResizeObserver in the browser, but JSDOM does not provide it.
// This no-op mock keeps tests stable while still exercising component logic.
class ResizeObserverMock {
	observe() {}

	unobserve() {}

	disconnect() {}
}

global.ResizeObserver = global.ResizeObserver || ResizeObserverMock;

// React 18 + older test utilities can print this known deprecation warning.
// Filter only this message so real test errors still appear normally.
const originalConsoleError = console.error;
let consoleErrorSpy;
beforeAll(() => {
	consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation((...args) => {
		const first = String(args[0] || '');
		if (first.includes('ReactDOMTestUtils.act is deprecated in favor of React.act')) {
			return;
		}
		originalConsoleError(...args);
	});
});

afterAll(() => {
	if (consoleErrorSpy) {
		consoleErrorSpy.mockRestore();
	}
});
