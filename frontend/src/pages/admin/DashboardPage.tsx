import React from 'react';
import {
  MessageSquare,
  CalendarCheck,
  UsersRound,
  ShieldCheck,
  TrendingUp,
  AlertTriangle,
  Upload,
  ArrowRight,
  Layers,
  Sparkles,
  Clock,
} from 'lucide-react';
import { useEnvironment } from '../../context/EnvironmentContext';
import { ReservationRequest, Lead, KnowledgeDocument } from '../../types';
import { AdminTab } from '../../components/admin/Sidebar';

interface DashboardPageProps {
  reservations: ReservationRequest[];
  leads: Lead[];
  documents: KnowledgeDocument[];
  onNavigate: (tab: AdminTab) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  reservations,
  leads,
  documents,
  onNavigate,
}) => {
  const { environment, isDemo, openSwitchModal } = useEnvironment();

  const pendingReservations = reservations.filter(
    (r) => r.status === 'NEW' || r.status === 'PENDING'
  ).length;

  const totalGuests = reservations.reduce((acc, r) => acc + r.guestCount, 0);

  return (
    <div className="space-y-6">
      {/* Top Banner: Mode Indicator & Welcome */}
      <div className="p-6 rounded-2xl glass-panel-elevated border border-gold-400/30 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span
              className={`px-2 py-0.5 rounded text-[10px] font-mono uppercase font-bold tracking-wider ${
                isDemo
                  ? 'bg-amber-500/20 text-gold-300 border border-gold-400/40'
                  : 'bg-emerald-500/20 text-emerald-300 border border-emerald-400/40'
              }`}
            >
              ACTIVE SCOPE: {environment} MODE
            </span>
            <span className="text-xs text-slate-400">Amit Hospitality Executive Portal</span>
          </div>
          <h1 className="text-2xl font-serif font-bold text-white tracking-wide">
            Hospitality Intelligence & Operations
          </h1>
          <p className="text-xs text-slate-400 mt-1 max-w-xl">
            {isDemo
              ? 'Currently presenting simulated data for Amit Hospitality stakeholders. Switch to REAL mode to manage verified documents and operational menus.'
              : 'Production environment active. AI Concierge is grounded exclusively in verified corporate documentation.'}
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <button
            onClick={() => openSwitchModal(isDemo ? 'REAL' : 'DEMO')}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-charcoal-800 hover:bg-charcoal-700 border border-gold-400/40 text-gold-300 font-medium text-xs transition shadow-sm"
          >
            <Layers className="w-4 h-4 text-gold-400" />
            <span>Switch to {isDemo ? 'REAL' : 'DEMO'} Mode</span>
          </button>
          <button
            onClick={() => onNavigate('KNOWLEDGE')}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 font-semibold text-xs hover:brightness-110 shadow-gold-glow transition"
          >
            <Upload className="w-4 h-4" />
            <span>Upload Documents</span>
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Guest Conversations */}
        <div className="p-5 rounded-2xl glass-panel border border-slate-800 hover:border-gold-400/30 transition">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs uppercase tracking-wider font-medium">Guest Inquiries</span>
            <div className="w-8 h-8 rounded-lg bg-gold-400/15 text-gold-400 flex items-center justify-center">
              <MessageSquare className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold font-serif text-white">1,482</div>
          <div className="flex items-center gap-1.5 text-[11px] text-emerald-400 mt-2">
            <TrendingUp className="w-3.5 h-3.5" />
            <span>+18.4% this week</span>
          </div>
        </div>

        {/* Pending Table Reservations */}
        <div
          onClick={() => onNavigate('RESERVATIONS')}
          className="p-5 rounded-2xl glass-panel border border-slate-800 hover:border-gold-400/30 cursor-pointer transition"
        >
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs uppercase tracking-wider font-medium">Pending Bookings</span>
            <div className="w-8 h-8 rounded-lg bg-amber-400/15 text-amber-400 flex items-center justify-center">
              <CalendarCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold font-serif text-white">{pendingReservations} Requests</div>
          <div className="flex items-center gap-1.5 text-[11px] text-gold-300 mt-2">
            <span>{totalGuests} total expected covers</span>
          </div>
        </div>

        {/* Event Leads Pipeline */}
        <div
          onClick={() => onNavigate('LEADS')}
          className="p-5 rounded-2xl glass-panel border border-slate-800 hover:border-gold-400/30 cursor-pointer transition"
        >
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs uppercase tracking-wider font-medium">Event Leads</span>
            <div className="w-8 h-8 rounded-lg bg-sky-400/15 text-sky-400 flex items-center justify-center">
              <UsersRound className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold font-serif text-white">{leads.length} Proposals</div>
          <div className="flex items-center gap-1.5 text-[11px] text-slate-400 mt-2">
            <span>Private dining & banquets</span>
          </div>
        </div>

        {/* Knowledge Base Status */}
        <div
          onClick={() => onNavigate('KNOWLEDGE')}
          className="p-5 rounded-2xl glass-panel border border-slate-800 hover:border-gold-400/30 cursor-pointer transition"
        >
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs uppercase tracking-wider font-medium">Active Documents</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-400/15 text-emerald-400 flex items-center justify-center">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold font-serif text-white">{documents.length} Indexed</div>
          <div className="flex items-center gap-1.5 text-[11px] text-emerald-400 mt-2">
            <span>Scope: {environment}</span>
          </div>
        </div>
      </div>

      {/* Two Column Layout: Recent Reservations & Knowledge Health */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Recent Reservation Requests */}
        <div className="lg:col-span-2 p-5 rounded-2xl glass-panel border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-serif font-bold text-base text-white">
                Recent Guest Reservation Requests
              </h3>
              <p className="text-xs text-slate-400">
                Incoming booking requests awaiting maître d' allocation
              </p>
            </div>
            <button
              onClick={() => onNavigate('RESERVATIONS')}
              className="text-xs text-gold-400 hover:text-gold-300 font-medium flex items-center gap-1 transition"
            >
              <span>View All</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-3">
            {reservations.slice(0, 4).map((res) => (
              <div
                key={res.id}
                className="p-3.5 rounded-xl bg-charcoal-900/80 border border-slate-700/60 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-white text-sm">{res.guestName}</span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-charcoal-800 text-gold-400 border border-slate-700">
                      {res.outletName}
                    </span>
                    {res.environment === 'DEMO' && (
                      <span className="text-[9px] font-mono uppercase px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-400 border border-amber-500/30">
                        DEMO
                      </span>
                    )}
                  </div>
                  <p className="text-slate-400 mt-1">
                    {res.guestCount} Guests • {res.reservationDate} at {res.reservationTime} • Seating: {res.seatingPreference}
                  </p>
                  {res.specialRequests && (
                    <p className="text-slate-500 italic mt-0.5 truncate max-w-md">
                      "{res.specialRequests}"
                    </p>
                  )}
                </div>

                <div className="flex items-center gap-2 self-end sm:self-center">
                  <span
                    className={`px-2.5 py-1 rounded-full text-[10px] font-semibold uppercase tracking-wider ${
                      res.status === 'ACCEPTED'
                        ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                        : res.status === 'PENDING'
                        ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                        : 'bg-sky-500/15 text-sky-400 border border-sky-500/30'
                    }`}
                  >
                    {res.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right 1 Col: Quick Action & System Health */}
        <div className="space-y-4">
          <div className="p-5 rounded-2xl glass-panel border border-slate-800 space-y-4">
            <h3 className="font-serif font-bold text-base text-white">
              AI Grounding Health
            </h3>

            <div className="space-y-3 text-xs">
              <div>
                <div className="flex justify-between text-slate-300 mb-1">
                  <span>Knowledge Retrieval Precision</span>
                  <span className="text-gold-400 font-mono font-bold">99.4%</span>
                </div>
                <div className="w-full h-1.5 rounded-full bg-charcoal-800 overflow-hidden">
                  <div className="w-[99%] h-full bg-gradient-to-r from-gold-500 to-gold-400 rounded-full" />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-slate-300 mb-1">
                  <span>Zero-Hallucination Guardrail</span>
                  <span className="text-emerald-400 font-mono font-bold">100% Active</span>
                </div>
                <div className="w-full h-1.5 rounded-full bg-charcoal-800 overflow-hidden">
                  <div className="w-full h-full bg-emerald-400 rounded-full" />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-slate-300 mb-1">
                  <span>Dual-Environment Isolation</span>
                  <span className="text-emerald-400 font-mono font-bold">Enforced</span>
                </div>
                <div className="w-full h-1.5 rounded-full bg-charcoal-800 overflow-hidden">
                  <div className="w-full h-full bg-emerald-400 rounded-full" />
                </div>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-charcoal-900 border border-slate-700/60 text-[11px] text-slate-400 space-y-1">
              <p className="font-semibold text-slate-200">Current Scope Protection</p>
              <p>
                The AI is restricted to retrieving data tagged as <strong>{environment}</strong>. Cross-environment contamination is prevented at database and vector levels.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
