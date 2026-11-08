import React, { useState } from 'react';
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
  CheckCircle2,
  Clock3,
  PhoneCall,
  Search,
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
  const [recentFilter, setRecentFilter] = useState('');

  // 1. Total reservation requests
  const totalReservations = reservations.length;

  // 2. Pending requests (NEW, PENDING, UNDER_REVIEW)
  const pendingRequests = reservations.filter(
    (r) => r.status === 'NEW' || r.status === 'PENDING' || r.status === 'UNDER_REVIEW'
  ).length;

  // 3. Accepted requests
  const acceptedRequests = reservations.filter((r) => r.status === 'ACCEPTED').length;

  // 4. New leads
  const newLeads = leads.filter((l) => l.status === 'NEW').length;

  // 5. Follow-up required
  const followUpRequired = leads.filter(
    (l) => l.status === 'FOLLOW_UP_REQUIRED' || l.status === 'CONTACTED'
  ).length;

  // Total covers expected
  const totalCovers = reservations.reduce((acc, r) => acc + r.guestCount, 0);

  // Filter recent reservations
  const filteredRecentReservations = reservations.filter((r) => {
    if (!recentFilter) return true;
    const q = recentFilter.toLowerCase();
    return (
      r.guestName.toLowerCase().includes(q) ||
      (r.referenceId && r.referenceId.toLowerCase().includes(q)) ||
      r.outletName.toLowerCase().includes(q)
    );
  });

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
              ? 'Currently presenting simulated business data for Amit Hospitality stakeholders. Switch to REAL mode to manage verified documents and operational menus.'
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

      {/* 6 Core Functional Dashboard Metric Sections */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3.5">
        {/* 1. Total Reservation Requests */}
        <div
          onClick={() => onNavigate('RESERVATIONS')}
          className="p-4 rounded-xl glass-panel border border-slate-800 hover:border-gold-400/40 cursor-pointer transition"
        >
          <div className="flex items-center justify-between text-slate-400 mb-1.5">
            <span className="text-[10px] uppercase tracking-wider font-semibold">Total Requests</span>
            <div className="w-7 h-7 rounded-lg bg-gold-400/15 text-gold-400 flex items-center justify-center">
              <CalendarCheck className="w-3.5 h-3.5" />
            </div>
          </div>
          <div className="text-2xl font-bold font-serif text-white">{totalReservations}</div>
          <div className="text-[11px] text-slate-400 mt-1">{totalCovers} total covers</div>
        </div>

        {/* 2. Pending Requests */}
        <div
          onClick={() => onNavigate('RESERVATIONS')}
          className="p-4 rounded-xl glass-panel border border-slate-800 hover:border-gold-400/40 cursor-pointer transition"
        >
          <div className="flex items-center justify-between text-slate-400 mb-1.5">
            <span className="text-[10px] uppercase tracking-wider font-semibold">Pending Review</span>
            <div className="w-7 h-7 rounded-lg bg-amber-400/15 text-amber-400 flex items-center justify-center">
              <Clock3 className="w-3.5 h-3.5" />
            </div>
          </div>
          <div className="text-2xl font-bold font-serif text-amber-300">{pendingRequests}</div>
          <div className="text-[11px] text-slate-400 mt-1">Awaiting maître d'</div>
        </div>

        {/* 3. Accepted Requests */}
        <div
          onClick={() => onNavigate('RESERVATIONS')}
          className="p-4 rounded-xl glass-panel border border-slate-800 hover:border-gold-400/40 cursor-pointer transition"
        >
          <div className="flex items-center justify-between text-slate-400 mb-1.5">
            <span className="text-[10px] uppercase tracking-wider font-semibold">Accepted Tables</span>
            <div className="w-7 h-7 rounded-lg bg-emerald-400/15 text-emerald-400 flex items-center justify-center">
              <CheckCircle2 className="w-3.5 h-3.5" />
            </div>
          </div>
          <div className="text-2xl font-bold font-serif text-emerald-300">{acceptedRequests}</div>
          <div className="text-[11px] text-emerald-400/80 mt-1">Tables confirmed</div>
        </div>

        {/* 4. New Leads */}
        <div
          onClick={() => onNavigate('LEADS')}
          className="p-4 rounded-xl glass-panel border border-slate-800 hover:border-gold-400/40 cursor-pointer transition"
        >
          <div className="flex items-center justify-between text-slate-400 mb-1.5">
            <span className="text-[10px] uppercase tracking-wider font-semibold">New Leads</span>
            <div className="w-7 h-7 rounded-lg bg-sky-400/15 text-sky-400 flex items-center justify-center">
              <UsersRound className="w-3.5 h-3.5" />
            </div>
          </div>
          <div className="text-2xl font-bold font-serif text-sky-300">{newLeads}</div>
          <div className="text-[11px] text-slate-400 mt-1">Direct inquiries</div>
        </div>

        {/* 5. Follow-up Required */}
        <div
          onClick={() => onNavigate('LEADS')}
          className="p-4 rounded-xl glass-panel border border-slate-800 hover:border-gold-400/40 cursor-pointer transition"
        >
          <div className="flex items-center justify-between text-slate-400 mb-1.5">
            <span className="text-[10px] uppercase tracking-wider font-semibold">Follow-Up Required</span>
            <div className="w-7 h-7 rounded-lg bg-orange-400/15 text-orange-400 flex items-center justify-center">
              <PhoneCall className="w-3.5 h-3.5" />
            </div>
          </div>
          <div className="text-2xl font-bold font-serif text-orange-300">{followUpRequired}</div>
          <div className="text-[11px] text-slate-400 mt-1">Callbacks & quotes</div>
        </div>

        {/* 6. Active Knowledge Documents */}
        <div
          onClick={() => onNavigate('KNOWLEDGE')}
          className="p-4 rounded-xl glass-panel border border-slate-800 hover:border-gold-400/40 cursor-pointer transition"
        >
          <div className="flex items-center justify-between text-slate-400 mb-1.5">
            <span className="text-[10px] uppercase tracking-wider font-semibold">Active Docs</span>
            <div className="w-7 h-7 rounded-lg bg-emerald-400/15 text-emerald-400 flex items-center justify-center">
              <ShieldCheck className="w-3.5 h-3.5" />
            </div>
          </div>
          <div className="text-2xl font-bold font-serif text-white">{documents.length}</div>
          <div className="text-[11px] text-emerald-400 mt-1">Scope: {environment}</div>
        </div>
      </div>

      {/* Two Column Layout: Recent Reservation Requests & Recent Event Leads */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column: Recent Reservation Requests */}
        <div className="p-5 rounded-2xl glass-panel border border-slate-800 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
            <div>
              <h3 className="font-serif font-bold text-base text-white">
                Recent Reservation Requests
              </h3>
              <p className="text-xs text-slate-400">
                Incoming table booking requests awaiting maître d' review
              </p>
            </div>
            <button
              onClick={() => onNavigate('RESERVATIONS')}
              className="text-xs text-gold-400 hover:text-gold-300 font-medium flex items-center gap-1 transition self-start sm:self-auto"
            >
              <span>View All ({reservations.length})</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-2.5">
            {reservations.slice(0, 5).map((res) => (
              <div
                key={res.id}
                className="p-3 rounded-xl bg-charcoal-900/80 border border-slate-700/60 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2.5 text-xs"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-white">{res.guestName}</span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-charcoal-800 text-gold-400 border border-slate-700">
                      {res.outletName}
                    </span>
                    <span className="text-[10px] font-mono text-slate-400">
                      {res.referenceId || `REF-RES-${res.id}`}
                    </span>
                    {res.environment === 'DEMO' && (
                      <span className="text-[9px] font-mono uppercase px-1.5 py-0.2 rounded bg-amber-500/15 text-amber-400 border border-amber-500/30">
                        DEMO
                      </span>
                    )}
                  </div>
                  <p className="text-slate-400 mt-1">
                    {res.guestCount} Guests • {res.reservationDate} at {res.reservationTime} • Seating: {res.seatingPreference}
                  </p>
                  {res.specialRequests && (
                    <p className="text-slate-400 italic mt-0.5 truncate max-w-sm">
                      "{res.specialRequests}"
                    </p>
                  )}
                </div>

                <span
                  className={`px-2.5 py-1 rounded-full text-[10px] font-semibold uppercase tracking-wider shrink-0 ${
                    res.status === 'ACCEPTED'
                      ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                      : res.status === 'UNDER_REVIEW'
                      ? 'bg-sky-500/15 text-sky-400 border border-sky-500/30'
                      : res.status === 'PENDING'
                      ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                      : 'bg-indigo-500/15 text-indigo-400 border border-indigo-500/30'
                  }`}
                >
                  {res.status.replace('_', ' ')}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column: Recent Event & Callback Enquiries */}
        <div className="p-5 rounded-2xl glass-panel border border-slate-800 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
            <div>
              <h3 className="font-serif font-bold text-base text-white">
                Recent Event & Lead Enquiries
              </h3>
              <p className="text-xs text-slate-400">
                Private banquets, corporate dinners, parties and callbacks
              </p>
            </div>
            <button
              onClick={() => onNavigate('LEADS')}
              className="text-xs text-gold-400 hover:text-gold-300 font-medium flex items-center gap-1 transition self-start sm:self-auto"
            >
              <span>View All ({leads.length})</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-2.5">
            {leads.slice(0, 5).map((lead) => (
              <div
                key={lead.id}
                className="p-3 rounded-xl bg-charcoal-900/80 border border-slate-700/60 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2.5 text-xs"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-white">{lead.name}</span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-charcoal-800 text-gold-400 border border-slate-700">
                      {lead.enquiryType.replace('_', ' ')}
                    </span>
                    <span className="text-[10px] font-mono text-slate-400">
                      {lead.referenceId || `REF-LEAD-${lead.id}`}
                    </span>
                    {lead.environment === 'DEMO' && (
                      <span className="text-[9px] font-mono uppercase px-1.5 py-0.2 rounded bg-amber-500/15 text-amber-400 border border-amber-500/30">
                        DEMO
                      </span>
                    )}
                  </div>
                  <p className="text-slate-400 mt-1">
                    {lead.outletName} • {lead.guestCount} Guests • Target: {lead.targetDate}
                  </p>
                  <p className="text-gold-400/80 font-mono text-[11px] mt-0.5">
                    Budget: {lead.budgetRange}
                  </p>
                </div>

                <span
                  className={`px-2.5 py-1 rounded-full text-[10px] font-semibold uppercase tracking-wider shrink-0 ${
                    lead.status === 'CONVERTED' || lead.status === 'WON'
                      ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                      : lead.status === 'QUALIFIED'
                      ? 'bg-gold-500/15 text-gold-400 border border-gold-500/30'
                      : lead.status === 'FOLLOW_UP_REQUIRED'
                      ? 'bg-orange-500/15 text-orange-400 border border-orange-500/30'
                      : 'bg-charcoal-700 text-slate-300'
                  }`}
                >
                  {lead.status.replace('_', ' ')}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
