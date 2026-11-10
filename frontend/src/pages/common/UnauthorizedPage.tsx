import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldAlert, ArrowLeft } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export const UnauthorizedPage: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-obsidian-950 flex flex-col justify-center items-center p-6 text-center">
      <div className="max-w-md space-y-4">
        <div className="w-16 h-16 mx-auto rounded-2xl bg-rose-950/60 border border-rose-500/40 flex items-center justify-center text-rose-400 shadow-lg">
          <ShieldAlert className="w-8 h-8" />
        </div>
        <h1 className="text-3xl font-serif font-bold text-white tracking-wide">403 Forbidden</h1>
        <h2 className="text-base font-serif font-semibold text-rose-300">Access Restricted</h2>
        <p className="text-xs text-slate-400 leading-relaxed">
          Your current account role (<strong className="text-gold-400">{user?.role || 'Guest'}</strong>) does not have authorization to view this administrative resource or outlet.
        </p>
        <div className="pt-4 flex justify-center gap-3">
          <Link
            to="/admin/dashboard"
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-charcoal-800 text-slate-200 hover:text-white border border-slate-700 text-xs transition"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Return to Dashboard</span>
          </Link>
          <Link
            to="/login"
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gold-500 text-obsidian-950 font-semibold text-xs hover:bg-gold-400 shadow-gold-glow transition"
          >
            <span>Switch Account</span>
          </Link>
        </div>
      </div>
    </div>
  );
};
