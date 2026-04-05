/**
 * MEOK AI Labs - Error Tracking Setup
 * Sentry integration for production error monitoring
 */

import * as Sentry from '@sentry/browser';
import { BrowserTracing } from '@sentry/browser';

// Initialize Sentry
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  
  // Performance monitoring
  integrations: [
    new BrowserTracing({
      tracePropagationTargets: ['meok.ai', 'localhost'],
    }),
  ],
  
  // Sampling rate for performance (10% in prod)
  tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.1 : 1.0,
  
  // Environment
  environment: process.env.NODE_ENV || 'development',
  
  // Release tracking
  release: process.env.NEXT_PUBLIC_APP_VERSION || 'unknown',
  
  // Ignore errors from these sources
  ignoreErrors: [
    // Network errors
    'Network request failed',
    'Failed to fetch',
    'NetworkError',
    
    // Browser extensions
    'chrome-extension://',
    'moz-extension://',
    'safari-extension://',
    
    // Third-party scripts
    'Refused to display',
  ],
  
  // Deny URLs containing these patterns from being sent to Sentry
  denyUrls: [
    /chrome-extension:\/\//i,
    /extensions\//i,
    /safari-extension\//i,
  ],
  
  // Before sending, sanitize the event
  beforeSend(event, hint) {
    // Don't send events from development
    if (process.env.NODE_ENV !== 'production') {
      return null;
    }
    
    // Sanitize user data
    if (event.user) {
      delete event.user.ip_address;
      delete event.user.email;
    }
    
    // Add custom tags
    event.tags = {
      ...event.tags,
      app_version: process.env.NEXT_PUBLIC_APP_VERSION,
    };
    
    return event;
  },
  
  // Set user context
  setUser: (user) => {
    if (user) {
      Sentry.setUser({
        id: user.id,
        email: user.email,
        username: user.username,
        subscription_tier: user.tier,
      });
    } else {
      Sentry.setUser(null);
    }
  },
});

// Error boundary component
export function ErrorBoundary({ children, fallback }) {
  return (
    <Sentry.ErrorBoundary fallback={fallback}>
      {children}
    </Sentry.ErrorBoundary>
  );
}

// Capture custom error with context
export function captureError(error, context = {}) {
  Sentry.withScope((scope) => {
    Object.entries(context).forEach(([key, value]) => {
      scope.setExtra(key, value);
    });
    Sentry.captureException(error);
  });
}

// Capture custom message
export function captureMessage(message, level = 'info') {
  Sentry.captureMessage(message, level);
}

// Add breadcrumb for debugging
export function addBreadcrumb(message, data = {}) {
  Sentry.addBreadcrumb({
    message,
    data,
    timestamp: Date.now(),
  });
}

// Performance monitoring
export function startTransaction(name, op) {
  return Sentry.startTransaction({ name, op });
}

// Measure function performance
export async function measurePerformance(name, fn) {
  const transaction = startTransaction(name, 'function');
  
  try {
    const result = await fn();
    transaction.setStatus('ok');
    return result;
  } catch (error) {
    transaction.setStatus('error');
    captureError(error, { transaction: name });
    throw error;
  } finally {
    transaction.finish();
  }
}

// React error boundary
export class ErrorBoundaryComponent extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    captureError(error, { componentStack: errorInfo.componentStack });
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div style={{ padding: '2rem', textAlign: 'center' }}>
          <h2>Something went wrong</h2>
          <p>We've been notified and are working on it.</p>
          <button onClick={() => window.location.reload()}>
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// Export for direct use
export default Sentry;
