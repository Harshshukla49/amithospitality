import React, { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { Sparkles, Shield, Lock, Mail, ArrowRight, AlertTriangle, RefreshCw, KeyRound, Check } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useEnvironment } from '../../context/EnvironmentContext';
import { UserRole } from '../../types';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { loginWithCredentials, login } = useAuth();
  const { environment, isDemo } = useEnvironment();

  const [email, setEmail] = useState('admin@amithospitality.com');
  const [password, setPassword] = useState('AmitConcierge2026!Secure');
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const from = (location.state as any)?.from?.pathname || '/admin/dashboard';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setLoading(true);

    try {
      const res = await loginWithCredentials(email, password);
      if (res.success) {
        navigate(from, { replace: true });
      } else {
        setErrorMessage(res.error || 'Authentication failed. Please verify credentials.');
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Connection to authentication service failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickFill = (role: UserRole, userEmail: string, pass: string) => {
    setEmail(userEmail);
    setPassword(pass);
    setErrorMessage(null);
  };

  return (
    <div className="min-h-screen bg-obsidian-950 flex flex-col justify-center items-center p-4 relative overflow-hidden">
      {/* Background Glow */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-96 h-96 bg-gold-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-md space-y-6 relative z-10">
        {/* Brand Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-gradient-to-br from-gold-400 to-gold-600 shadow-gold-glow mb-2">
            <Sparkles className="w-6 h-6 text-obsidian-950" />
          </div>
          <h1 className="text-2xl sm:text-3xl font-serif font-bold text-white tracking-wide">
            AMIT HOSPITALITY
          </h1>
          <p className="text-xs text-gold-400 font-mono tracking-widest uppercase">
            Enterprise Admin Portal
          </p>
        </div>

        {/* Login Card */}
        <div className="rounded-2xl glass-panel-elevated border border-gold-400/30 p-6 sm:p-8 space-y-5 shadow-luxury">
          {errorMessage && (
            <div className="flex items-center gap-2.5 p-3 rounded-xl bg-rose-950/80 border border-rose-500/50 text-rose-300 text-xs animate-fade-in">
              <AlertTriangle className="w-4 h-4 shrink-0 text-rose-400" />
              <span>{errorMessage}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Work Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@amithospitality.com"
                  className="w-full pl-9 pr-3 py-2.5 rounded-xl bg-charcoal-900 border border-slate-700 text-white text-xs focus:outline-none focus:border-gold-400"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full pl-9 pr-3 py-2.5 rounded-xl bg-charcoal-900 border border-slate-700 text-white text-xs focus:outline-none focus:border-gold-400 font-mono"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-xl bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 font-bold text-xs uppercase tracking-wider hover:brightness-110 shadow-gold-glow transition flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Verifying Credentials...</span>
                </>
              ) : (
                <>
                  <span>Sign In to Admin Portal</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Quick-Fill Demonstration Selector */}
          <div className="pt-4 border-t border-slate-800 space-y-2.5">
            <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono">
              <span className="flex items-center gap-1.5">
                <KeyRound className="w-3.5 h-3.5 text-gold-400" />
                <span>Quick-Fill Demo Roles</span>
              </span>
              <span className="text-[10px] text-gold-400/80 font-bold">1-Click Autofill</span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-[11px]">
              <button
                type="button"
                onClick={() => handleQuickFill('SUPER_ADMIN', 'admin@amithospitality.com', 'AmitConcierge2026!Secure')}
                className="p-2 rounded-lg bg-charcoal-900 hover:bg-charcoal-800 border border-slate-800 hover:border-gold-400/50 text-left text-slate-300 transition"
              >
                <div className="font-semibold text-white">Super Admin</div>
                <div className="text-[10px] text-slate-500">Full System Access</div>
              </button>
              <button
                type="button"
                onClick={() => handleQuickFill('MANAGER', 'manager@amithospitality.com', 'Manager2026!')}
                className="p-2 rounded-lg bg-charcoal-900 hover:bg-charcoal-800 border border-slate-800 hover:border-gold-400/50 text-left text-slate-300 transition"
              >
                <div className="font-semibold text-white">F&B Manager</div>
                <div className="text-[10px] text-slate-500">Amber Terrace (ID: 1)</div>
              </button>
            </div>
          </div>

          <div className="pt-2 text-center">
            <Link
              to="/concierge"
              className="text-xs text-slate-400 hover:text-gold-400 transition"
            >
              ← Return to Guest Concierge Experience
            </Link>
          </div>
        </div>

        {/* Environment Gating Footer */}
        <div className="text-center text-[11px] text-slate-500 font-mono flex items-center justify-center gap-2">
          <Shield className="w-3.5 h-3.5 text-gold-400" />
          <span>Active Environment: <strong className="text-gold-400">{environment}</strong></span>
        </div>
      </div>
    </div>
  );
};
