import React, { useState, useEffect } from 'react';
import {
  Activity,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  HelpCircle,
  RefreshCw,
  Cpu,
  PhoneCall,
  MessageSquare,
  Mail,
  Smartphone,
  Database,
  ShieldAlert,
  Server,
  ExternalLink,
  Lock,
} from 'lucide-react';
import { useEnvironment } from '../../context/EnvironmentContext';

interface IntegrationInfo {
  id: string;
  name: string;
  category: string;
  status: string;
  active_model?: string;
  offline_fallback?: string;
  phone_number?: string;
  phone_number_id?: string;
  provider?: string;
  sender_email?: string;
  sender_phone?: string;
  mode?: string;
  environment?: string;
  required_params: string[];
  action_required?: string | null;
}

interface DiagnosticResult {
  serviceId: string;
  connected: boolean;
  status: string;
  latency_ms?: number;
  error?: string;
  action_required?: string;
  verified_at?: string;
  raw?: any;
}

export const IntegrationsPage: React.FC = () => {
  const { environment, isDemo } = useEnvironment();
  const [loading, setLoading] = useState<boolean>(true);
  const [integrations, setIntegrations] = useState<Record<string, IntegrationInfo>>({});
  const [testResults, setTestResults] = useState<Record<string, DiagnosticResult>>({});
  const [testingId, setTestingId] = useState<string | null>(null);
  const [lastRefreshed, setLastRefreshed] = useState<string>('');

  const token = localStorage.getItem('amit_access_token') || localStorage.getItem('access_token') || '';

  const fetchStatus = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/v1/integrations/status', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      if (res.ok) {
        const data = await res.json();
        setIntegrations(data.integrations || {});
        setLastRefreshed(new Date().toLocaleTimeString());
      }
    } catch (e) {
      console.error('Failed to load integrations status:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, [token]);

  const runDiagnosticTest = async (serviceId: string) => {
    setTestingId(serviceId);
    try {
      const res = await fetch(`/api/v1/integrations/test/${serviceId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
      });
      const data = await res.json();
      setTestResults((prev) => ({
        ...prev,
        [serviceId]: {
          serviceId,
          connected: data.connected ?? false,
          status: data.status || 'UNKNOWN',
          latency_ms: data.latency_ms,
          error: data.error,
          action_required: data.action_required,
          verified_at: data.verified_at || new Date().toISOString(),
          raw: data,
        },
      }));
    } catch (e: any) {
      setTestResults((prev) => ({
        ...prev,
        [serviceId]: {
          serviceId,
          connected: false,
          status: 'TEST_ERROR',
          error: e.message || 'Diagnostic network failure',
        },
      }));
    } finally {
      setTestingId(null);
    }
  };

  const getServiceIcon = (id: string) => {
    switch (id) {
      case 'gemini':
      case 'gemini_api':
        return <Cpu className="w-6 h-6 text-amber-400" />;
      case 'whatsapp':
      case 'whatsapp_cloud_api':
        return <MessageSquare className="w-6 h-6 text-emerald-400" />;
      case 'voice':
      case 'twilio_voice':
        return <PhoneCall className="w-6 h-6 text-sky-400" />;
      case 'email':
      case 'email_service':
        return <Mail className="w-6 h-6 text-purple-400" />;
      case 'sms':
      case 'sms_service':
        return <Smartphone className="w-6 h-6 text-pink-400" />;
      case 'redis':
      case 'redis_cache':
        return <Database className="w-6 h-6 text-rose-400" />;
      case 'sentry':
      case 'sentry_monitoring':
        return <ShieldAlert className="w-6 h-6 text-orange-400" />;
      default:
        return <Server className="w-6 h-6 text-slate-400" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Title & Status Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-serif font-bold text-white tracking-wide">
              Enterprise Integrations Hub
            </h1>
            <span
              className={`px-2.5 py-0.5 rounded-full text-xs font-semibold tracking-wider ${
                isDemo
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                  : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
              }`}
            >
              {environment} MODE
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Real-time diagnostic health, connectivity verification, and live fallbacks for external hospitality services.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {lastRefreshed && (
            <span className="text-xs text-slate-500 hidden sm:inline">
              Updated at {lastRefreshed}
            </span>
          )}
          <button
            onClick={fetchStatus}
            disabled={loading}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-charcoal-800 border border-slate-700 hover:border-gold-400/50 text-slate-300 hover:text-white text-xs transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-gold-400' : ''}`} />
            Refresh Status
          </button>
        </div>
      </div>

      {/* Zero Fabrication Guarantee Notice */}
      <div className="p-4 rounded-xl bg-charcoal-900/90 border border-gold-400/20 flex items-start gap-3">
        <Lock className="w-5 h-5 text-gold-400 shrink-0 mt-0.5" />
        <div className="text-xs text-slate-300 space-y-1">
          <p className="font-semibold text-gold-300">Authentic Connectivity Guarantee</p>
          <p className="text-slate-400 leading-relaxed">
            All diagnostics query active live cloud APIs. Credentials are strictly parsed from the server runtime environment and never displayed in plain text.
            If credentials are not supplied, the platform falls back to safe local deterministic mock algorithms without degrading guest reservation or chat workflows.
          </p>
        </div>
      </div>

      {/* Integrations Grid */}
      {loading && Object.keys(integrations).length === 0 ? (
        <div className="py-20 flex flex-col items-center justify-center text-slate-500 space-y-3">
          <RefreshCw className="w-8 h-8 animate-spin text-gold-400" />
          <p className="text-sm">Inspecting enterprise cloud connectors...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {Object.entries(integrations).map(([key, info]) => {
            const result = testResults[info.id] || testResults[key];
            const isTesting = testingId === info.id || testingId === key;
            const isConfigured = info.status.startsWith('CONFIGURED');

            // Determine badge state
            let badgeBg = 'bg-slate-800 text-slate-400 border-slate-700';
            let statusText = info.status;
            let iconState = <HelpCircle className="w-4 h-4 text-slate-500" />;

            if (result) {
              if (result.connected) {
                badgeBg = 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
                statusText = 'CONNECTED';
                iconState = <CheckCircle2 className="w-4 h-4 text-emerald-400" />;
              } else if (result.status === 'NOT CONFIGURED') {
                badgeBg = 'bg-slate-800 text-slate-400 border-slate-700';
                statusText = 'NOT CONFIGURED';
                iconState = <HelpCircle className="w-4 h-4 text-slate-500" />;
              } else {
                badgeBg = 'bg-rose-500/20 text-rose-400 border-rose-500/30';
                statusText = 'DISCONNECTED';
                iconState = <XCircle className="w-4 h-4 text-rose-400" />;
              }
            } else if (isConfigured) {
              badgeBg = 'bg-amber-500/20 text-amber-300 border-amber-500/30';
              statusText = 'CONFIGURED (UNTESTED)';
              iconState = <AlertTriangle className="w-4 h-4 text-amber-400" />;
            }

            return (
              <div
                key={key}
                className="rounded-xl glass-panel border border-slate-800 p-5 flex flex-col justify-between hover:border-slate-700 transition"
              >
                <div className="space-y-4">
                  {/* Service Header */}
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <div className="p-2.5 rounded-lg bg-charcoal-900 border border-slate-800">
                        {getServiceIcon(info.id || key)}
                      </div>
                      <div>
                        <h3 className="font-semibold text-white text-base">{info.name}</h3>
                        <p className="text-xs text-slate-400">{info.category}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-xs font-medium tracking-wide">
                      {iconState}
                      <span className={badgeBg.split(' ')[1]}>{statusText}</span>
                    </div>
                  </div>

                  {/* Service Metadata */}
                  <div className="space-y-2 text-xs text-slate-300 bg-charcoal-900/60 p-3 rounded-lg border border-slate-800/80">
                    {info.active_model && (
                      <div className="flex justify-between">
                        <span className="text-slate-500">Active Model:</span>
                        <span className="font-mono text-gold-300">{info.active_model}</span>
                      </div>
                    )}
                    {info.provider && (
                      <div className="flex justify-between">
                        <span className="text-slate-500">Provider:</span>
                        <span className="font-semibold text-white">{info.provider}</span>
                      </div>
                    )}
                    {info.mode && (
                      <div className="flex justify-between">
                        <span className="text-slate-500">Operating Mode:</span>
                        <span className="font-mono text-emerald-400">{info.mode}</span>
                      </div>
                    )}
                    {info.offline_fallback && (
                      <div className="flex justify-between">
                        <span className="text-slate-500">Safety Fallback:</span>
                        <span className="text-slate-400">{info.offline_fallback}</span>
                      </div>
                    )}
                    <div className="pt-1 border-t border-slate-800">
                      <span className="text-slate-500 block mb-1">Configuration Parameters:</span>
                      <div className="flex flex-wrap gap-1">
                        {info.required_params.map((param) => (
                          <span
                            key={param}
                            className="px-1.5 py-0.5 rounded bg-charcoal-800 text-[10px] font-mono text-slate-300 border border-slate-700"
                          >
                            {param}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Diagnostic Test Result Box */}
                  {result && (
                    <div
                      className={`p-3 rounded-lg border text-xs space-y-1 ${
                        result.connected
                          ? 'bg-emerald-950/30 border-emerald-500/30 text-emerald-300'
                          : result.status === 'NOT CONFIGURED'
                          ? 'bg-slate-900 border-slate-800 text-slate-400'
                          : 'bg-rose-950/30 border-rose-500/30 text-rose-300'
                      }`}
                    >
                      <div className="flex items-center justify-between font-semibold">
                        <span>
                          {result.connected ? 'Live Ping Succeeded' : 'Diagnostic Notice'}
                        </span>
                        {result.latency_ms !== undefined && (
                          <span className="font-mono">{result.latency_ms}ms</span>
                        )}
                      </div>
                      {result.error && <p className="text-rose-400">{result.error}</p>}
                      {result.action_required && (
                        <p className="text-slate-400">{result.action_required}</p>
                      )}
                      {result.verified_at && (
                        <p className="text-[10px] text-slate-500">
                          Verified at {new Date(result.verified_at).toLocaleTimeString()}
                        </p>
                      )}
                    </div>
                  )}
                </div>

                {/* Card Actions */}
                <div className="pt-4 mt-4 border-t border-slate-800/80 flex items-center justify-between">
                  <span className="text-[11px] text-slate-500">
                    {isConfigured ? 'Credentials present in env' : 'Pending credential injection'}
                  </span>
                  <button
                    onClick={() => runDiagnosticTest(info.id || key)}
                    disabled={isTesting}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gold-500 hover:bg-gold-600 text-obsidian-950 font-semibold text-xs transition disabled:opacity-50"
                  >
                    <Activity className={`w-3.5 h-3.5 ${isTesting ? 'animate-spin' : ''}`} />
                    {isTesting ? 'Testing API...' : 'Run Diagnostics'}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
export default IntegrationsPage;
