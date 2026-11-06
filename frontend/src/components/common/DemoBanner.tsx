import React from 'react';
import { AlertTriangle, ArrowRight } from 'lucide-react';
import { useEnvironment } from '../../context/EnvironmentContext';

export const DemoBanner: React.FC = () => {
  const { isDemo, openSwitchModal } = useEnvironment();

  if (!isDemo) return null;

  return (
    <div className="bg-gradient-to-r from-amber-950/90 via-charcoal-900 to-amber-950/90 border-b border-gold-400/30 px-4 py-2 text-xs md:text-sm text-gold-200 flex flex-wrap items-center justify-between gap-2 shadow-sm">
      <div className="flex items-center gap-2">
        <span className="flex h-2 w-2 rounded-full bg-gold-400 animate-pulse" />
        <AlertTriangle className="w-4 h-4 text-gold-400 shrink-0" />
        <span>
          <strong className="font-semibold text-gold-300">DEMO MODE ACTIVE:</strong> All menus, prices, restaurant timings, and policies displayed are fictional sample data for demonstration.
        </span>
      </div>
      <button
        onClick={() => openSwitchModal('REAL')}
        className="flex items-center gap-1.5 px-3 py-1 rounded bg-gold-500/20 hover:bg-gold-500/30 text-gold-300 border border-gold-400/40 font-medium transition text-xs whitespace-nowrap"
      >
        <span>Switch to REAL Mode</span>
        <ArrowRight className="w-3.5 h-3.5" />
      </button>
    </div>
  );
};
