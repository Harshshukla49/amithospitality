import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Sparkles, X, MessageSquare, ArrowRight, Shield } from 'lucide-react';

export const FloatingConciergeLauncher: React.FC = () => {
  const location = useLocation();
  const [minimized, setMinimized] = useState(false);

  // Don't display floating bubble on the dedicated full-screen concierge page or admin pages
  if (
    location.pathname.startsWith('/concierge') ||
    location.pathname.startsWith('/admin') ||
    location.pathname.startsWith('/login')
  ) {
    return null;
  }

  return (
    <div className="fixed bottom-6 right-6 z-40 flex flex-col items-end">
      {/* Pop-up bubble helper banner (collapsible) */}
      {!minimized && (
        <div className="mb-3 max-w-xs rounded-2xl bg-charcoal-900/95 border border-gold-400/40 p-4 shadow-2xl backdrop-blur-md animate-fade-in relative hidden sm:block">
          <button
            onClick={() => setMinimized(true)}
            className="absolute top-2 right-2 text-slate-400 hover:text-white"
            title="Dismiss bubble"
          >
            <X className="w-3.5 h-3.5" />
          </button>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-[10px] font-mono uppercase font-bold text-gold-400 tracking-wider">
              Amit AI Concierge Live
            </span>
          </div>
          <p className="text-xs text-slate-200 font-medium">
            Looking for menu prices, event line-ups, or private dining at LOTD, Veneto &amp; Warehouse Cafe?
          </p>
          <Link
            to="/concierge"
            className="mt-2.5 inline-flex items-center gap-1.5 text-xs font-bold text-gold-300 hover:text-gold-200 transition"
          >
            <span>Ask Concierge Assistant</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      )}

      {/* Main Trigger Button */}
      <Link
        to="/concierge"
        aria-label="Open AI Concierge Chatbot"
        className="flex items-center gap-2.5 px-4 py-3 rounded-full bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 font-bold text-xs shadow-gold-glow hover:scale-105 hover:brightness-110 transition-all border border-gold-300/60 group"
      >
        <Sparkles className="w-4 h-4 animate-spin-slow group-hover:rotate-12 transition-transform" />
        <span className="tracking-wide">Chat with AI Concierge</span>
      </Link>
    </div>
  );
};
