import '@testing-library/jest-dom';

// Intercept relative fetch calls in jsdom test environment so tests do not hang on unmocked endpoints
const originalFetch = globalThis.fetch;
if (originalFetch) {
  globalThis.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
    const url =
      typeof input === 'string'
        ? input
        : input instanceof URL
        ? input.toString()
        : (input as Request)?.url || '';

    if (url.startsWith('/api/audit') || url.includes('/api/audit')) {
      return new Response(JSON.stringify([]), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    if (typeof input === 'string' && input.startsWith('/')) {
      input = `http://localhost:8000${input}`;
    }
    return originalFetch(input, init);
  };
}
