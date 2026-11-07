import React, { useState } from 'react';
import {
  Sliders,
  Shield,
  Layers,
  History,
  Save,
  CheckCircle,
  AlertTriangle,
  Cpu,
  Download,
} from 'lucide-react';
import { useEnvironment } from '../../context/EnvironmentContext';
import { exportAuditLogsCsv } from '../../api/audit';

export const SettingsPage: React.FC = () => {
  const { environment, isDemo, openSwitchModal, auditLogs } = useEnvironment();

  // AI Configuration State
  const [model, setModel] = useState('gemini-1.5-flash');
  const [temperature, setTemperature] = useState(0.2);
  const [topK, setTopK] = useState(4);
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [exportingAudit, setExportingAudit] = useState(false);

  const handleExportAuditTrail = async () => {
    try {
      setExportingAudit(true);
      const blob = await exportAuditLogsCsv(environment);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `amit_hospitality_audit_trail_${environment.toLowerCase()}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to export audit trail', err);
    } finally {
      setExportingAudit(false);
    }
  };

  const handleSaveAIConfig = (e: React.FormEvent) => {
    e.preventDefault();
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 2500);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <span className="text-[11px] font-mono uppercase tracking-wider text-gold-400 font-semibold">
            System & Governance
          </span>
        </div>
        <h1 className="text-2xl font-serif font-bold text-white tracking-wide">
          Settings, Audit Logs & AI Configuration
        </h1>
        <p className="text-xs text-slate-400 mt-1 max-w-xl">
          Control active knowledge environments, configure grounded LLM hyperparameters, and inspect the immutable compliance audit trail.
        </p>
      </div>

      {/* Environment Management Card */}
      <div className="p-6 rounded-2xl glass-panel-elevated border border-gold-400/30 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div
              className={`p-3 rounded-xl ${
                isDemo
                  ? 'bg-amber-500/20 text-gold-400 border border-gold-400/40'
                  : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
              }`}
            >
              <Layers className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-serif font-bold text-lg text-white">Active Knowledge Scope</h3>
                <span
                  className={`px-2 py-0.5 rounded text-[10px] font-mono uppercase font-bold tracking-wider ${
                    isDemo
                      ? 'bg-amber-500/20 text-gold-300 border border-gold-400/40'
                      : 'bg-emerald-500/20 text-emerald-300 border border-emerald-400/40'
                  }`}
                >
                  {environment} MODE
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                {isDemo
                  ? 'Fictional sample menus and prices are currently active for demonstration.'
                  : 'Verified company knowledge is currently active. The AI will never output fictional data.'}
              </p>
            </div>
          </div>

          <button
            onClick={() => openSwitchModal(isDemo ? 'REAL' : 'DEMO')}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 font-semibold text-xs hover:brightness-110 shadow-gold-glow transition"
          >
            <span>Switch to {isDemo ? 'REAL' : 'DEMO'} Mode</span>
          </button>
        </div>
      </div>

      {/* AI RAG Configuration */}
      <div className="p-6 rounded-2xl glass-panel border border-slate-800 space-y-4">
        <div className="flex items-center gap-2 text-gold-400">
          <Cpu className="w-5 h-5" />
          <h3 className="font-serif font-bold text-base text-white">
            AI Engine & Grounding Parameters
          </h3>
        </div>

        <form onSubmit={handleSaveAIConfig} className="space-y-4 text-xs">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-slate-300 font-medium mb-1">LLM Foundation Model</label>
              <select
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400"
              >
                <option value="gemini-1.5-flash">Google Gemini 1.5 Flash (Sub-second)</option>
                <option value="gemini-1.5-pro">Google Gemini 1.5 Pro (Deep Reasoning)</option>
                <option value="gpt-4o-mini">OpenAI GPT-4o Mini (Fallback)</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-300 font-medium mb-1">
                Temperature ({temperature}) — Strict Factuality
              </label>
              <input
                type="range"
                min="0.0"
                max="0.7"
                step="0.05"
                value={temperature}
                onChange={(e) => setTemperature(Number(e.target.value))}
                className="w-full accent-gold-400"
              />
              <p className="text-[10px] text-slate-500 mt-1">
                0.2 is recommended to prevent hallucinations.
              </p>
            </div>

            <div>
              <label className="block text-slate-300 font-medium mb-1">
                Top-K Vector Chunks Retrieved ({topK})
              </label>
              <input
                type="range"
                min="2"
                max="8"
                step="1"
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                className="w-full accent-gold-400"
              />
              <p className="text-[10px] text-slate-500 mt-1">
                Number of grounded semantic chunks injected per turn.
              </p>
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-charcoal-900 border border-slate-700/80 space-y-1.5">
            <p className="font-semibold text-slate-200">Active System Prompt Grounding Rule:</p>
            <p className="font-mono text-[11px] text-slate-400 leading-relaxed">
              "You are Amit Hospitality's luxury AI Concierge. Answer questions strictly using retrieved knowledge chunks from the currently active environment. Never invent menu prices, timings, or policies. In REAL mode, if verified info is missing, gracefully inform the guest that verified records are not yet indexed."
            </p>
          </div>

          <div className="flex items-center justify-between pt-2">
            {savedSuccess ? (
              <span className="text-emerald-400 flex items-center gap-1 font-semibold text-xs">
                <CheckCircle className="w-4 h-4" /> Parameters updated successfully
              </span>
            ) : (
              <span />
            )}
            <button
              type="submit"
              className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-charcoal-800 hover:bg-charcoal-700 text-gold-300 border border-slate-700 font-semibold transition"
            >
              <Save className="w-3.5 h-3.5" />
              <span>Save AI Configuration</span>
            </button>
          </div>
        </form>
      </div>

      {/* Immutable Audit Trail Table */}
      <div className="p-6 rounded-2xl glass-panel border border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-gold-400">
            <History className="w-5 h-5" />
            <div>
              <h3 className="font-serif font-bold text-base text-white">
                Compliance & Environment Audit Trail
              </h3>
              <p className="text-[11px] text-slate-400">
                {auditLogs.length} immutable records logged for security & compliance
              </p>
            </div>
          </div>
          <button
            onClick={handleExportAuditTrail}
            disabled={exportingAudit || auditLogs.length === 0}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-charcoal-800 hover:bg-charcoal-700 text-gold-300 border border-slate-700 text-xs font-medium transition disabled:opacity-50 self-start sm:self-auto"
            title="Export full compliance audit log to CSV"
          >
            <Download className="w-3.5 h-3.5" />
            <span>{exportingAudit ? 'Exporting...' : 'Export Audit Trail (.CSV)'}</span>
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-charcoal-900/90 text-slate-400 uppercase tracking-wider text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-3">Timestamp</th>
                <th className="py-2.5 px-3">Administrator</th>
                <th className="py-2.5 px-3">Action</th>
                <th className="py-2.5 px-3">Scope</th>
                <th className="py-2.5 px-3">Details / Reason</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80 font-mono text-[11px]">
              {auditLogs.map((log) => (
                <tr key={log.id} className="hover:bg-charcoal-800/40 transition">
                  <td className="py-3 px-3 text-slate-400">{log.timestamp}</td>
                  <td className="py-3 px-3 text-white font-sans font-medium">{log.userName}</td>
                  <td className="py-3 px-3 text-gold-400 font-semibold">{log.action}</td>
                  <td className="py-3 px-3">
                    <span
                      className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                        log.environment === 'DEMO'
                          ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                          : 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                      }`}
                    >
                      {log.environment}
                    </span>
                  </td>
                  <td className="py-3 px-3 font-sans text-slate-300">{log.details}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
