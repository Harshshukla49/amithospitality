import React from 'react';
import { Link } from 'react-router-dom';
import { Compass, ArrowLeft, Sparkles } from 'lucide-react';

export const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-obsidian-950 flex flex-col justify-center items-center p-6 text-center">
      <div className="max-w-md space-y-4">
        <div className="w-16 h-16 mx-auto rounded-2xl bg-charcoal-900 border border-gold-400/30 flex items-center justify-center text-gold-400 shadow-gold-glow">
          <Compass className="w-8 h-8 animate-spin-slow" />
        </div>
        <h1 className="text-4xl font-serif font-bold text-white tracking-wide">404</h1>
        <h2 className="text-lg font-serif font-semibold text-gold-300">Dining Destination Not Found</h2>
        <p className="text-xs text-slate-400 leading-relaxed">
          The hospitality page or resource you requested does not exist or has been relocated within the Amit Hospitality portfolio.
        </p>
        <div className="pt-4 flex justify-center gap-3">
          <Link
            to="/concierge"
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 font-semibold text-xs hover:brightness-110 shadow-gold-glow transition"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Return to Concierge</span>
          </Link>
          <Link
            to="/admin/dashboard"
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-charcoal-800 text-slate-300 hover:text-white border border-slate-700 text-xs transition"
          >
            <span>Admin Console</span>
          </Link>
        </div>
      </div>
    </div>
  );
};
