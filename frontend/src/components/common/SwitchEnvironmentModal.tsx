import React, { useState } from 'react';
import { AlertCircle, ShieldAlert, CheckCircle, X } from 'lucide-react';
import { useEnvironment } from '../../context/EnvironmentContext';
import { useAuth } from '../../context/AuthContext';

export const SwitchEnvironmentModal: React.FC = () => {
  const { pendingSwitch, closeSwitchModal, switchEnvironment } = useEnvironment();
  const { user, canManageEnvironment } = useAuth();
  const [reason, setReason] = useState('');
  const [confirmed, setConfirmed] = useState(false);
  const [error, setError] = useState('');

  if (!pendingSwitch?.isOpen) return null;

  const target = pendingSwitch.target;
  const isMovingToReal = target === 'REAL';

  const handleConfirm = () => {
    if (!canManageEnvironment) {
      setError('Only Super Admins and authorized Admins can change the system environment.');
      return;
    }
    if (!reason.trim()) {
      setError('Please provide a mandatory reason for the environment audit log.');
      return;
    }
    if (!confirmed) {
      setError('You must check the confirmation acknowledgment to proceed.');
      return;
    }

    switchEnvironment(target, reason, user?.fullName || 'Administrator');
    setReason('');
    setConfirmed(false);
    setError('');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-obsidian-950/80 backdrop-blur-md animate-fadeIn">
      <div className="relative w-full max-w-lg p-6 rounded-2xl glass-panel-elevated text-slate-100 border border-gold-400/40 shadow-luxury">
        <button
          onClick={closeSwitchModal}
          className="absolute top-4 right-4 p-2 text-slate-400 hover:text-gold-300 transition"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3 mb-4">
          <div className={`p-3 rounded-xl ${isMovingToReal ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40' : 'bg-gold-500/20 text-gold-400 border border-gold-500/40'}`}>
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-xl font-serif font-bold text-white">
              Confirm Environment Switch
            </h3>
            <p className="text-xs text-slate-400">
              Transitioning active knowledge state to <span className="font-semibold text-gold-400">{target} MODE</span>
            </p>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-charcoal-900/80 border border-slate-700/60 mb-4 text-xs space-y-2 text-slate-300">
          <p className="font-semibold text-slate-200 flex items-center gap-1.5">
            <AlertCircle className="w-4 h-4 text-gold-400" />
            Strict Data Isolation Protocol:
          </p>
          <ul className="list-disc list-inside space-y-1 pl-1 text-slate-400">
            {isMovingToReal ? (
              <>
                <li>AI Concierge will <strong>cease referencing fictional demo menus</strong>, prices, and policies immediately.</li>
                <li>Only <strong>verified corporate documents</strong> uploaded by authorized staff will be retrieved.</li>
                <li>If verified documentation for an item is absent, the AI will gracefully defer to human staff.</li>
              </>
            ) : (
              <>
                <li>System will reload fictional sample menus and pricing for presentation to prospective stakeholders.</li>
                <li>All AI generated responses will be prominently branded with DEMO indicators.</li>
                <li>Simulated reservations and leads will be isolated from real operations.</li>
              </>
            )}
            <li>All active AI query caches will be instantly purged.</li>
            <li>This action will be permanently recorded in the immutable compliance audit log.</li>
          </ul>
        </div>

        {error && (
          <div className="p-3 mb-4 rounded-lg bg-rose-500/20 border border-rose-500/40 text-rose-300 text-xs">
            {error}
          </div>
        )}

        <div className="space-y-4 mb-6">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              Reason for Environment Transition <span className="text-rose-400">*</span>
            </label>
            <input
              type="text"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="e.g. Stakeholder demo session completed; deploying verified wine list"
              className="w-full px-3 py-2 text-sm rounded-lg bg-charcoal-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-gold-400 transition"
            />
          </div>

          <label className="flex items-start gap-2.5 cursor-pointer text-xs text-slate-300">
            <input
              type="checkbox"
              checked={confirmed}
              onChange={(e) => setConfirmed(e.target.checked)}
              className="mt-0.5 rounded bg-charcoal-900 border-slate-600 text-gold-500 focus:ring-0"
            />
            <span>
              I understand that switching modes immediately updates live AI retrieval and all subsequent customer-facing concierge responses.
            </span>
          </label>
        </div>

        <div className="flex items-center justify-end gap-3">
          <button
            onClick={closeSwitchModal}
            className="px-4 py-2 text-sm rounded-lg text-slate-300 hover:text-white hover:bg-charcoal-800 transition"
          >
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            className="flex items-center gap-2 px-5 py-2 text-sm font-semibold rounded-lg bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 hover:brightness-110 shadow-gold-glow transition"
          >
            <CheckCircle className="w-4 h-4" />
            Switch to {target} Mode
          </button>
        </div>
      </div>
    </div>
  );
};
