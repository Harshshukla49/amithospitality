import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { logFrontendError } from '../../utils/monitoring';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  errorMessage: string;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    errorMessage: '',
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, errorMessage: error.message };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    logFrontendError(error, { componentStack: errorInfo.componentStack });
  }

  private handleReload = () => {
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-obsidian-950 text-slate-100 flex flex-col items-center justify-center p-6 text-center">
          <div className="p-8 rounded-2xl glass-panel border border-gold-400/30 max-w-md w-full space-y-5 shadow-2xl">
            <div className="w-14 h-14 mx-auto rounded-full bg-amber-500/10 border border-gold-400/40 flex items-center justify-center text-amber-400">
              <AlertTriangle className="w-7 h-7" />
            </div>

            <div className="space-y-2">
              <h1 className="text-xl font-serif font-bold text-white tracking-wide">
                Concierge Service Reconnecting
              </h1>
              <p className="text-sm text-slate-400 leading-relaxed">
                An unexpected interface anomaly occurred. Our luxury concierge service is momentarily recalibrating.
              </p>
            </div>

            <button
              onClick={this.handleReload}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-gold-500 hover:bg-gold-600 text-obsidian-950 font-semibold text-xs tracking-wider uppercase transition shadow-gold-glow"
            >
              <RefreshCw className="w-4 h-4" />
              Reload Experience
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
