import '@testing-library/jest-dom';

// Intercept relative fetch calls in jsdom test environment
const originalFetch = globalThis.fetch;
if (originalFetch) {
  globalThis.fetch = (input: RequestInfo | URL, init?: RequestInit) => {
    if (typeof input === 'string' && input.startsWith('/')) {
      input = `http://localhost:8000${input}`;
    }
    return originalFetch(input, init);
  };
}
