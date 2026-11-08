/**
 * Amit Hospitality AI Concierge — Frontend Telemetry & Privacy Monitor
 * Ensures safe error tracking without exposing PII, credentials, or session tokens.
 */

const SENSITIVE_KEYS = ['token', 'password', 'secret', 'authorization', 'key', 'access_token', 'refresh_token'];

export function scrubSensitiveData(data: Record<string, any>): Record<string, any> {
  const scrubbed: Record<string, any> = {};
  for (const [key, val] of Object.entries(data)) {
    if (SENSITIVE_KEYS.some((s) => key.toLowerCase().includes(s))) {
      scrubbed[key] = '[REDACTED]';
    } else if (typeof val === 'object' && val !== null) {
      scrubbed[key] = scrubSensitiveData(val);
    } else {
      scrubbed[key] = val;
    }
  }
  return scrubbed;
}

export function initFrontendMonitoring() {
  const dsn = (import.meta as any).env?.VITE_SENTRY_DSN;
  if (!dsn || dsn.startsWith('your_')) {
    // Sentry not configured; local error logging only
    return;
  }

  // Global window unhandled error capture
  window.addEventListener('error', (event) => {
    logFrontendError(event.error || event.message, { source: 'window.onerror' });
  });

  window.addEventListener('unhandledrejection', (event) => {
    logFrontendError(event.reason, { source: 'unhandledrejection' });
  });
}

export function logFrontendError(error: Error | string | unknown, context?: Record<string, any>) {
  const errorMsg = error instanceof Error ? error.message : String(error);
  const cleanContext = context ? scrubSensitiveData(context) : {};

  if ((import.meta as any).env?.DEV) {
    console.error('[Telemetry Audit]', errorMsg, cleanContext);
  }
}
