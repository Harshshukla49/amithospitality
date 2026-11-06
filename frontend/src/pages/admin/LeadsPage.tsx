import React, { useState } from 'react';
import {
  UsersRound,
  Search,
  Filter,
  Download,
  Calendar,
  Briefcase,
  CheckCircle,
  Clock,
  ArrowRight,
} from 'lucide-react';
import { Lead, LeadStatus } from '../../types';
import { INITIAL_OUTLETS } from '../../utils/mockData';
import { useEnvironment } from '../../context/EnvironmentContext';

interface LeadsPageProps {
  leads: Lead[];
  onUpdateStatus: (id: number, status: LeadStatus, notes?: string) => void;
}

export const LeadsPage: React.FC<LeadsPageProps> = ({ leads, onUpdateStatus }) => {
  const { environment } = useEnvironment();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState<string>('ALL');
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');
  const [activeLead, setActiveLead] = useState<Lead | null>(null);
  const [leadNote, setLeadNote] = useState('');

  const filteredLeads = leads.filter((l) => {
    const matchesSearch =
      l.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      l.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      l.phone.includes(searchQuery);
    const matchesType = selectedType === 'ALL' || l.enquiryType === selectedType;
    const matchesStatus = selectedStatus === 'ALL' || l.status === selectedStatus;
    return matchesSearch && matchesType && matchesStatus;
  });

  const handleExportCSV = () => {
    const headers = 'ID,Environment,Outlet,Name,Phone,Email,Type,Guests,Date,Budget,Status\n';
    const rows = filteredLeads
      .map(
        (l) =>
          `${l.id},${l.environment},"${l.outletName}","${l.name}",${l.phone},${l.email},${l.enquiryType},${l.guestCount},${l.targetDate},"${l.budgetRange}",${l.status}`
      )
      .join('\n');
    const blob = new Blob([headers + rows], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `event_leads_${environment.toLowerCase()}_${new Date().toISOString().substring(0, 10)}.csv`;
    a.click();
  };

  const handleApplyStatus = (status: LeadStatus) => {
    if (!activeLead) return;
    onUpdateStatus(activeLead.id, status, leadNote);
    setActiveLead({ ...activeLead, status, notes: leadNote || activeLead.notes });
    setLeadNote('');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[11px] font-mono uppercase tracking-wider text-gold-400 font-semibold">
              Banquets & Private Dining
            </span>
          </div>
          <h1 className="text-2xl font-serif font-bold text-white tracking-wide">
            Event & High-Value Inquiries Pipeline
          </h1>
          <p className="text-xs text-slate-400 mt-1 max-w-xl">
            Track inquiries for wedding buyouts, corporate executive dinners, and milestone celebrations.
          </p>
        </div>

        <button
          onClick={handleExportCSV}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-charcoal-800 hover:bg-charcoal-700 border border-slate-700 text-xs font-semibold text-slate-200 transition self-start md:self-auto"
        >
          <Download className="w-3.5 h-3.5 text-gold-400" />
          <span>Export to CSV</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search leads by name, email, or phone..."
            className="w-full pl-9 pr-3 py-2 text-xs rounded-xl bg-charcoal-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-gold-400"
          />
        </div>

        <div className="flex items-center gap-2">
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="px-3 py-2 text-xs rounded-xl bg-charcoal-900 border border-slate-700 text-slate-300 focus:outline-none focus:border-gold-400"
          >
            <option value="ALL">All Event Types</option>
            <option value="PRIVATE_DINING">Private Dining</option>
            <option value="CORPORATE_EVENT">Corporate Dinner</option>
            <option value="WEDDING">Wedding / Sangeet</option>
            <option value="BIRTHDAY">Anniversary / Birthday</option>
          </select>

          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="px-3 py-2 text-xs rounded-xl bg-charcoal-900 border border-slate-700 text-slate-300 focus:outline-none focus:border-gold-400"
          >
            <option value="ALL">All Stages</option>
            <option value="NEW">New</option>
            <option value="CONTACTED">Contacted</option>
            <option value="QUALIFIED">Qualified</option>
            <option value="PROPOSAL_SENT">Proposal Sent</option>
            <option value="WON">Won</option>
            <option value="LOST">Lost</option>
          </select>
        </div>
      </div>

      {/* Leads Table */}
      <div className="rounded-2xl glass-panel border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-charcoal-900/90 text-slate-400 uppercase tracking-wider text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Client Contact</th>
                <th className="py-3 px-4">Event Type</th>
                <th className="py-3 px-4">Target Date</th>
                <th className="py-3 px-4">Guests</th>
                <th className="py-3 px-4">Budget Range</th>
                <th className="py-3 px-4">Pipeline Stage</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {filteredLeads.map((lead) => (
                <tr key={lead.id} className="hover:bg-charcoal-800/40 transition">
                  <td className="py-3.5 px-4">
                    <div>
                      <div className="flex items-center gap-1.5 font-semibold text-white">
                        <span>{lead.name}</span>
                        {lead.environment === 'DEMO' && (
                          <span className="text-[9px] font-mono uppercase px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-400 border border-amber-500/30">
                            DEMO
                          </span>
                        )}
                      </div>
                      <p className="text-[11px] text-slate-400 font-mono mt-0.5">
                        {lead.phone} • {lead.email}
                      </p>
                    </div>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className="px-2 py-0.5 rounded bg-charcoal-800 text-gold-400 border border-slate-700 text-[10px] uppercase font-mono">
                      {lead.enquiryType.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 font-mono text-[11px] text-slate-300">
                    {lead.targetDate}
                  </td>
                  <td className="py-3.5 px-4 font-mono font-semibold text-slate-200">
                    {lead.guestCount} Guests
                  </td>
                  <td className="py-3.5 px-4 font-mono text-gold-400">
                    {lead.budgetRange}
                  </td>
                  <td className="py-3.5 px-4">
                    <span
                      className={`inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-semibold uppercase tracking-wider ${
                        lead.status === 'WON'
                          ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                          : lead.status === 'QUALIFIED'
                          ? 'bg-gold-500/15 text-gold-400 border border-gold-500/30'
                          : lead.status === 'PROPOSAL_SENT'
                          ? 'bg-sky-500/15 text-sky-400 border border-sky-500/30'
                          : 'bg-charcoal-700 text-slate-300'
                      }`}
                    >
                      {lead.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <button
                      onClick={() => {
                        setActiveLead(lead);
                        setLeadNote(lead.notes || '');
                      }}
                      className="px-3 py-1.5 rounded-lg bg-charcoal-800 hover:bg-charcoal-700 text-gold-300 border border-slate-700 text-xs font-medium transition"
                    >
                      Manage
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Lead Management Modal */}
      {activeLead && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-obsidian-950/80 backdrop-blur-md">
          <div className="relative w-full max-w-lg p-6 rounded-2xl glass-panel-elevated text-slate-100 border border-gold-400/40 shadow-luxury space-y-4">
            <div className="flex items-center justify-between border-b border-slate-700/60 pb-3">
              <div>
                <h3 className="text-lg font-serif font-bold text-white">{activeLead.name}</h3>
                <p className="text-xs text-slate-400">
                  {activeLead.enquiryType.replace('_', ' ')} • {activeLead.outletName}
                </p>
              </div>
              <button onClick={() => setActiveLead(null)} className="text-slate-400 hover:text-white">
                ✕
              </button>
            </div>

            <div className="p-3.5 rounded-xl bg-charcoal-900 border border-slate-700 text-xs space-y-2">
              <div className="grid grid-cols-2 gap-2 text-slate-300">
                <div>
                  <span className="text-slate-500">Phone:</span> {activeLead.phone}
                </div>
                <div>
                  <span className="text-slate-500">Email:</span> {activeLead.email}
                </div>
                <div>
                  <span className="text-slate-500">Guests:</span> {activeLead.guestCount}
                </div>
                <div>
                  <span className="text-slate-500">Target Date:</span> {activeLead.targetDate}
                </div>
                <div>
                  <span className="text-slate-500">Budget:</span> <strong className="text-gold-400">{activeLead.budgetRange}</strong>
                </div>
                <div>
                  <span className="text-slate-500">Current Stage:</span> <strong className="text-white">{activeLead.status}</strong>
                </div>
              </div>

              {activeLead.notes && (
                <div className="pt-2 border-t border-slate-800 text-slate-400">
                  <span className="text-gold-300 font-semibold">Client Vision:</span> "{activeLead.notes}"
                </div>
              )}
            </div>

            <div className="space-y-1.5 text-xs">
              <label className="block text-slate-300 font-medium">Add Sales / Banquets Update</label>
              <textarea
                rows={2}
                value={leadNote}
                onChange={(e) => setLeadNote(e.target.value)}
                placeholder="Spoke with client, shared 4-course banquet menu, site walkthrough scheduled..."
                className="w-full px-3 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400"
              />
            </div>

            <div className="pt-2 flex flex-wrap items-center justify-between gap-2 text-xs">
              <span className="text-slate-500">Advance Stage:</span>
              <div className="flex flex-wrap gap-1.5">
                {(['CONTACTED', 'QUALIFIED', 'PROPOSAL_SENT', 'WON', 'LOST'] as const).map(
                  (stage) => (
                    <button
                      key={stage}
                      onClick={() => handleApplyStatus(stage)}
                      className={`px-2.5 py-1 rounded-lg border text-xs font-medium transition ${
                        stage === 'WON'
                          ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 hover:bg-emerald-500/30'
                          : stage === 'LOST'
                          ? 'bg-rose-500/20 text-rose-300 border-rose-500/40 hover:bg-rose-500/30'
                          : 'bg-charcoal-800 text-slate-300 border-slate-700 hover:border-gold-400'
                      }`}
                    >
                      {stage.replace('_', ' ')}
                    </button>
                  )
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
