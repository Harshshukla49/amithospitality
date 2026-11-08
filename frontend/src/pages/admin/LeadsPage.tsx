import React, { useState, useEffect } from 'react';
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
  Plus,
  History,
  Phone,
  Mail,
  User,
  X,
  AlertTriangle,
} from 'lucide-react';
import { Lead, LeadStatus, LeadType, LeadHistoryItem } from '../../types';
import { INITIAL_OUTLETS } from '../../utils/mockData';
import { useEnvironment } from '../../context/EnvironmentContext';
import { fetchLeadHistoryApi, createLeadApi } from '../../api/leads';

interface LeadsPageProps {
  leads: Lead[];
  onUpdateStatus: (id: number, status: LeadStatus, notes?: string, assignedStaffName?: string) => void;
  onAddLead?: (lead: Lead) => void;
}

export const LeadsPage: React.FC<LeadsPageProps> = ({
  leads,
  onUpdateStatus,
  onAddLead,
}) => {
  const { environment, isDemo } = useEnvironment();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedOutlet, setSelectedOutlet] = useState<string>('ALL');
  const [selectedType, setSelectedType] = useState<string>('ALL');
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');
  const [activeLead, setActiveLead] = useState<Lead | null>(null);
  const [leadNote, setLeadNote] = useState('');
  const [assignedStaff, setAssignedStaff] = useState('');
  const [historyItems, setHistoryItems] = useState<LeadHistoryItem[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  // Manual Lead Creation Modal State
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [createName, setCreateName] = useState('');
  const [createPhone, setCreatePhone] = useState('');
  const [createEmail, setCreateEmail] = useState('');
  const [createOutletId, setCreateOutletId] = useState<number>(INITIAL_OUTLETS[0]?.id || 1);
  const [createType, setCreateType] = useState<LeadType>('CORPORATE_EVENT');
  const [createGuests, setCreateGuests] = useState(25);
  const [createDate, setCreateDate] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() + 14);
    return d.toISOString().split('T')[0];
  });
  const [createBudget, setCreateBudget] = useState('₹2,00,000 - ₹5,00,000');
  const [createNotes, setCreateNotes] = useState('');
  const [createStaff, setCreateStaff] = useState('');
  const [createError, setCreateError] = useState('');
  const [isSubmittingManual, setIsSubmittingManual] = useState(false);

  // Load history when active lead opens
  useEffect(() => {
    if (!activeLead) {
      setHistoryItems([]);
      return;
    }
    setLeadNote(activeLead.internalNotes || activeLead.notes || '');
    setAssignedStaff(activeLead.assignedStaffName || '');
    setLoadingHistory(true);
    fetchLeadHistoryApi(activeLead.id)
      .then((data) => setHistoryItems(data))
      .catch((err) => {
        console.warn('Could not fetch lead history:', err);
        setHistoryItems([]);
      })
      .finally(() => setLoadingHistory(false));
  }, [activeLead]);

  const filteredLeads = leads.filter((l) => {
    const q = searchQuery.toLowerCase().trim();
    const matchesSearch =
      !q ||
      l.name.toLowerCase().includes(q) ||
      l.email.toLowerCase().includes(q) ||
      l.phone.includes(q) ||
      (l.referenceId && l.referenceId.toLowerCase().includes(q)) ||
      String(l.id) === q;

    const matchesOutlet = selectedOutlet === 'ALL' || l.outletId === Number(selectedOutlet);
    const matchesType = selectedType === 'ALL' || l.enquiryType === selectedType;
    const matchesStatus = selectedStatus === 'ALL' || l.status === selectedStatus;

    return matchesSearch && matchesOutlet && matchesType && matchesStatus;
  });

  const handleExportCSV = () => {
    const headers =
      'Reference_ID,ID,Environment,Outlet,Name,Phone,Email,Enquiry_Type,Guests,Date,Budget_Range,Status,Assigned_Staff,Internal_Notes,Source\n';
    const rows = filteredLeads
      .map(
        (l) =>
          `"${l.referenceId || ''}",${l.id},${l.environment},"${l.outletName}","${l.name}",${l.phone},${l.email},${l.enquiryType},${l.guestCount},${l.targetDate},"${l.budgetRange}",${l.status},"${l.assignedStaffName || ''}","${(l.internalNotes || l.notes || '').replace(/"/g, '""')}","${l.source || ''}"`
      )
      .join('\n');
    const blob = new Blob([headers + rows], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `event_leads_${environment.toLowerCase()}_${new Date().toISOString().substring(0, 10)}.csv`;
    a.click();
  };

  const handleApplyStatus = (newStatus: LeadStatus) => {
    if (!activeLead) return;
    onUpdateStatus(activeLead.id, newStatus, leadNote, assignedStaff);
    setActiveLead({
      ...activeLead,
      status: newStatus,
      internalNotes: leadNote || activeLead.internalNotes,
      assignedStaffName: assignedStaff || activeLead.assignedStaffName,
    });
    // Optimistic history item
    setHistoryItems((prev) => [
      {
        id: Date.now(),
        leadId: activeLead.id,
        previousStatus: activeLead.status,
        newStatus,
        changedByName: 'Staff Member',
        notes: leadNote || 'Status transition applied via Admin console',
        createdAt: new Date().toISOString().replace('T', ' ').substring(0, 19),
      },
      ...prev,
    ]);
  };

  const handleCreateManualLead = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanPhone = createPhone.replace(/\D/g, '');
    if (!createName.trim()) {
      setCreateError('Please provide the client name.');
      return;
    }
    if (cleanPhone.length < 7 || cleanPhone.length > 15) {
      setCreateError('Please enter a valid phone number (7 to 15 digits).');
      return;
    }

    setIsSubmittingManual(true);
    setCreateError('');

    try {
      const selectedOut = INITIAL_OUTLETS.find((o) => o.id === createOutletId) || INITIAL_OUTLETS[0];
      const newLead = await createLeadApi({
        outlet_id: createOutletId,
        name: createName.trim(),
        phone: createPhone.trim(),
        email: createEmail.trim(),
        enquiry_type: createType,
        guest_count: createGuests,
        target_date: createDate,
        budget_range: createBudget,
        notes: createNotes.trim() || undefined,
        assigned_staff_name: createStaff.trim() || undefined,
        source: 'STAFF_MANUAL_ENTRY',
      });

      if (onAddLead) {
        onAddLead(newLead);
      }
      setIsCreateModalOpen(false);
      // Reset form
      setCreateName('');
      setCreatePhone('');
      setCreateEmail('');
      setCreateNotes('');
      setCreateStaff('');
    } catch (err: any) {
      console.warn('Backend manual lead creation error, using fallback:', err);
      const selectedOut = INITIAL_OUTLETS.find((o) => o.id === createOutletId) || INITIAL_OUTLETS[0];
      const generatedRef = `REF-LEAD-${createDate.replace(/-/g, '')}-${Math.floor(1000 + Math.random() * 9000)}`;
      const fallbackLead: Lead = {
        id: Date.now(),
        referenceId: generatedRef,
        environment,
        outletId: createOutletId,
        outletName: selectedOut.name,
        name: createName.trim(),
        phone: createPhone.trim(),
        email: createEmail.trim(),
        enquiryType: createType,
        guestCount: createGuests,
        targetDate: createDate,
        budgetRange: createBudget,
        status: 'NEW',
        notes: createNotes.trim(),
        assignedStaffName: createStaff.trim(),
        source: 'STAFF_MANUAL_ENTRY',
        createdAt: new Date().toISOString().replace('T', ' ').substring(0, 16),
      };
      if (onAddLead) {
        onAddLead(fallbackLead);
      }
      setIsCreateModalOpen(false);
    } finally {
      setIsSubmittingManual(false);
    }
  };

  const getStatusBadge = (status: LeadStatus) => {
    switch (status) {
      case 'CONVERTED':
      case 'WON':
        return 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30';
      case 'QUALIFIED':
        return 'bg-gold-500/15 text-gold-400 border border-gold-500/30';
      case 'FOLLOW_UP_REQUIRED':
        return 'bg-orange-500/15 text-orange-400 border border-orange-500/30';
      case 'CONTACTED':
        return 'bg-sky-500/15 text-sky-400 border border-sky-500/30';
      case 'PROPOSAL_SENT':
        return 'bg-indigo-500/15 text-indigo-400 border border-indigo-500/30';
      case 'CLOSED':
      case 'LOST':
        return 'bg-rose-500/15 text-rose-400 border border-rose-500/30';
      case 'NEW':
      default:
        return 'bg-charcoal-700 text-slate-300 border border-slate-600';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[11px] font-mono uppercase tracking-wider text-gold-400 font-semibold">
              Banquets & Private Dining Pipeline
            </span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-charcoal-800 text-slate-400 border border-slate-700">
              Scope: {environment}
            </span>
          </div>
          <h1 className="text-2xl font-serif font-bold text-white tracking-wide">
            Lead Management & Event Inquiries
          </h1>
          <p className="text-xs text-slate-400 mt-1 max-w-xl">
            Track inquiries for wedding buyouts, corporate executive dinners, private parties, and callbacks with audit timelines.
          </p>
        </div>

        <div className="flex items-center gap-2 self-start md:self-auto">
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 font-semibold text-xs hover:brightness-110 shadow-gold-glow transition"
          >
            <Plus className="w-4 h-4" />
            <span>Create Lead</span>
          </button>
          <button
            onClick={handleExportCSV}
            className="flex items-center gap-2 px-3.5 py-2.5 rounded-xl bg-charcoal-800 hover:bg-charcoal-700 border border-slate-700 text-xs font-semibold text-slate-200 transition shadow-sm"
          >
            <Download className="w-3.5 h-3.5 text-gold-400" />
            <span>Export (CSV)</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search leads by Reference ID (REF-LEAD-...), name, email, or phone..."
            className="w-full pl-9 pr-3 py-2 text-xs rounded-xl bg-charcoal-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-gold-400"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {/* Outlet Filter */}
          <select
            value={selectedOutlet}
            onChange={(e) => setSelectedOutlet(e.target.value)}
            className="px-3 py-2 text-xs rounded-xl bg-charcoal-900 border border-slate-700 text-slate-300 focus:outline-none focus:border-gold-400"
          >
            <option value="ALL">All Outlets</option>
            {INITIAL_OUTLETS.map((o) => (
              <option key={o.id} value={o.id}>
                {o.name}
              </option>
            ))}
          </select>

          {/* Type Filter */}
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="px-3 py-2 text-xs rounded-xl bg-charcoal-900 border border-slate-700 text-slate-300 focus:outline-none focus:border-gold-400"
          >
            <option value="ALL">All Event Types</option>
            <option value="CORPORATE_EVENT">Corporate Event</option>
            <option value="PRIVATE_PARTY">Private Party</option>
            <option value="BIRTHDAY_PARTY">Birthday Party</option>
            <option value="GROUP_BOOKING">Group Booking</option>
            <option value="WEDDING_EVENT">Wedding / Reception</option>
            <option value="CUSTOMER_CALLBACK">Customer Callback</option>
            <option value="GENERAL_ENQUIRY">General Enquiry</option>
            <option value="PRIVATE_DINING">Private Dining</option>
            <option value="CATERING">Outdoor Catering</option>
          </select>

          {/* Status Filter */}
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="px-3 py-2 text-xs rounded-xl bg-charcoal-900 border border-slate-700 text-slate-300 focus:outline-none focus:border-gold-400"
          >
            <option value="ALL">All Stages</option>
            <option value="NEW">New</option>
            <option value="CONTACTED">Contacted</option>
            <option value="QUALIFIED">Qualified</option>
            <option value="FOLLOW_UP_REQUIRED">Follow-up Required</option>
            <option value="CONVERTED">Converted</option>
            <option value="CLOSED">Closed</option>
            <option value="PROPOSAL_SENT">Proposal Sent</option>
          </select>
        </div>
      </div>

      {/* Leads Table */}
      <div className="rounded-2xl glass-panel border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-charcoal-900/90 text-slate-400 uppercase tracking-wider text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Tracking / Reference</th>
                <th className="py-3 px-4">Client Contact</th>
                <th className="py-3 px-4">Outlet</th>
                <th className="py-3 px-4">Enquiry Type</th>
                <th className="py-3 px-4">Target Date</th>
                <th className="py-3 px-4">Guests</th>
                <th className="py-3 px-4">Budget Range</th>
                <th className="py-3 px-4">Pipeline Stage</th>
                <th className="py-3 px-4">Assigned Staff</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {filteredLeads.length > 0 ? (
                filteredLeads.map((lead) => (
                  <tr key={lead.id} className="hover:bg-charcoal-800/40 transition">
                    <td className="py-3.5 px-4 font-mono">
                      <div className="text-gold-300 font-semibold text-[11px]">
                        {lead.referenceId || `REF-LEAD-${lead.id}`}
                      </div>
                      <div className="text-[10px] text-slate-500">
                        {lead.source || 'LEAD'}
                      </div>
                    </td>
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
                    <td className="py-3.5 px-4 font-medium text-slate-200">
                      {lead.outletName}
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
                        className={`inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-semibold uppercase tracking-wider ${getStatusBadge(
                          lead.status
                        )}`}
                      >
                        {lead.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      {lead.assignedStaffName ? (
                        <span className="text-[11px] text-gold-300 font-medium">
                          {lead.assignedStaffName}
                        </span>
                      ) : (
                        <span className="text-[10px] text-slate-500 italic">Unassigned</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => setActiveLead(lead)}
                        className="px-3 py-1.5 rounded-lg bg-charcoal-800 hover:bg-charcoal-700 text-gold-300 border border-slate-700 text-xs font-medium transition"
                      >
                        Manage
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={10} className="text-center py-10 text-slate-500">
                    No leads matching current filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Lead Management & Status History Modal */}
      {activeLead && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-obsidian-950/80 backdrop-blur-md overflow-y-auto">
          <div className="relative w-full max-w-2xl p-6 rounded-2xl glass-panel-elevated text-slate-100 border border-gold-400/40 shadow-luxury space-y-4 my-8">
            <div className="flex items-center justify-between border-b border-slate-700/60 pb-3">
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-lg font-serif font-bold text-white">{activeLead.name}</h3>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-gold-400/15 text-gold-300 border border-gold-400/30">
                    {activeLead.referenceId || `REF-LEAD-${activeLead.id}`}
                  </span>
                  {activeLead.environment === 'DEMO' && (
                    <span className="text-[9px] font-mono uppercase px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-400 border border-amber-500/30">
                      DEMO DATA
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-400">
                  {activeLead.enquiryType.replace('_', ' ')} • {activeLead.outletName}
                </p>
              </div>
              <button onClick={() => setActiveLead(null)} className="text-slate-400 hover:text-white p-1 rounded-lg">
                ✕
              </button>
            </div>

            <div className="p-3.5 rounded-xl bg-charcoal-900 border border-slate-700 text-xs space-y-2">
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-slate-300">
                <div>
                  <span className="text-slate-500 block text-[10px] uppercase font-mono">Phone</span>
                  <span className="font-mono text-slate-200">{activeLead.phone}</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px] uppercase font-mono">Email</span>
                  <span className="text-slate-200">{activeLead.email}</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px] uppercase font-mono">Guest Count</span>
                  <strong className="text-white">{activeLead.guestCount} Guests</strong>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px] uppercase font-mono">Target Date</span>
                  <span className="font-mono text-gold-300">{activeLead.targetDate}</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px] uppercase font-mono">Budget</span>
                  <strong className="text-gold-400">{activeLead.budgetRange}</strong>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px] uppercase font-mono">Current Stage</span>
                  <span
                    className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase ${getStatusBadge(
                      activeLead.status
                    )}`}
                  >
                    {activeLead.status.replace('_', ' ')}
                  </span>
                </div>
              </div>

              {activeLead.notes && (
                <div className="pt-2 border-t border-slate-800 text-slate-300 text-[11px]">
                  <span className="text-gold-300 font-semibold">Client Vision / Notes:</span> "{activeLead.notes}"
                </div>
              )}
            </div>

            {/* Staff Assignment & Follow-up Note */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              <div>
                <label className="block text-slate-300 font-medium mb-1">Assigned Sales / Banquets Staff</label>
                <input
                  type="text"
                  value={assignedStaff}
                  onChange={(e) => setAssignedStaff(e.target.value)}
                  placeholder="e.g. Shalini Roy (Events Director)"
                  className="w-full px-3 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400"
                />
              </div>
              <div>
                <label className="block text-slate-300 font-medium mb-1">Follow-up / Internal Update Note</label>
                <input
                  type="text"
                  value={leadNote}
                  onChange={(e) => setLeadNote(e.target.value)}
                  placeholder="Spoke with host, shared 4-course menu, walkthrough scheduled..."
                  className="w-full px-3 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400"
                />
              </div>
            </div>

            {/* Advance Status Stage */}
            <div className="pt-1 space-y-2">
              <span className="text-slate-400 text-xs font-medium block">Advance Pipeline Stage:</span>
              <div className="flex flex-wrap gap-2 text-xs">
                {(['NEW', 'CONTACTED', 'QUALIFIED', 'FOLLOW_UP_REQUIRED', 'CONVERTED', 'CLOSED'] as const).map(
                  (stage) => (
                    <button
                      key={stage}
                      type="button"
                      onClick={() => handleApplyStatus(stage)}
                      className={`px-3 py-1.5 rounded-lg border text-xs font-medium transition ${
                        stage === 'CONVERTED'
                          ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 hover:bg-emerald-500/30'
                          : stage === 'CLOSED'
                          ? 'bg-rose-500/20 text-rose-300 border-rose-500/40 hover:bg-rose-500/30'
                          : stage === 'FOLLOW_UP_REQUIRED'
                          ? 'bg-orange-500/20 text-orange-300 border-orange-500/40 hover:bg-orange-500/30'
                          : 'bg-charcoal-800 text-slate-300 border-slate-700 hover:border-gold-400'
                      }`}
                    >
                      {stage.replace('_', ' ')}
                    </button>
                  )
                )}
              </div>
            </div>

            {/* Status Change Audit Timeline */}
            <div className="pt-3 border-t border-slate-800 text-xs">
              <div className="flex items-center gap-1.5 font-semibold text-slate-300 mb-2">
                <History className="w-3.5 h-3.5 text-gold-400" />
                <span>Lead Status Audit History</span>
              </div>

              {loadingHistory ? (
                <p className="text-slate-500 text-xs italic">Loading status history timeline...</p>
              ) : historyItems.length > 0 ? (
                <div className="max-h-40 overflow-y-auto space-y-2 pr-1">
                  {historyItems.map((h) => (
                    <div
                      key={h.id}
                      className="p-2 rounded-lg bg-charcoal-900/90 border border-slate-800 text-[11px] flex items-start justify-between gap-2"
                    >
                      <div>
                        <div className="font-medium text-slate-200">
                          {h.previousStatus ? `${h.previousStatus} → ` : 'Initial: '}
                          <span className="text-gold-300 font-semibold">{h.newStatus}</span>
                        </div>
                        {h.notes && <div className="text-slate-400 mt-0.5 italic">"{h.notes}"</div>}
                      </div>
                      <div className="text-right text-[10px] text-slate-500 shrink-0 font-mono">
                        <div>{h.changedByName}</div>
                        <div>{h.createdAt.substring(0, 16)}</div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-slate-500 text-xs italic">
                  No previous status transitions recorded for this lead.
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Manual Staff Create Lead Modal */}
      {isCreateModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-obsidian-950/80 backdrop-blur-md overflow-y-auto">
          <div className="relative w-full max-w-lg p-6 rounded-2xl glass-panel-elevated text-slate-100 border border-gold-400/40 shadow-luxury space-y-4 my-8">
            <div className="flex items-center justify-between border-b border-slate-700/60 pb-3">
              <div>
                <h3 className="text-lg font-serif font-bold text-white">Log Event / Private Lead</h3>
                <p className="text-xs text-slate-400">Manual staff entry for walk-in or phone inquiries</p>
              </div>
              <button
                onClick={() => setIsCreateModalOpen(false)}
                className="text-slate-400 hover:text-white p-1 rounded-lg"
              >
                ✕
              </button>
            </div>

            {createError && (
              <div className="p-2 rounded bg-rose-500/20 border border-rose-500/40 text-rose-300 text-xs">
                {createError}
              </div>
            )}

            <form onSubmit={handleCreateManualLead} className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-medium mb-1">
                    Client Name <span className="text-rose-400">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={createName}
                    onChange={(e) => setCreateName(e.target.value)}
                    placeholder="e.g. Vikram Seth"
                    className="w-full px-3 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-medium mb-1">
                    Phone Number <span className="text-rose-400">*</span>
                  </label>
                  <input
                    type="tel"
                    required
                    value={createPhone}
                    onChange={(e) => setCreatePhone(e.target.value)}
                    placeholder="+91 98110 00000"
                    className="w-full px-3 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Email Address</label>
                  <input
                    type="email"
                    value={createEmail}
                    onChange={(e) => setCreateEmail(e.target.value)}
                    placeholder="vikram@corp.com"
                    className="w-full px-3 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Outlet</label>
                  <select
                    value={createOutletId}
                    onChange={(e) => setCreateOutletId(Number(e.target.value))}
                    className="w-full px-2 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400"
                  >
                    {INITIAL_OUTLETS.map((o) => (
                      <option key={o.id} value={o.id}>
                        {o.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Enquiry Type</label>
                  <select
                    value={createType}
                    onChange={(e) => setCreateType(e.target.value as LeadType)}
                    className="w-full px-2 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400"
                  >
                    <option value="CORPORATE_EVENT">Corporate Event</option>
                    <option value="PRIVATE_PARTY">Private Party</option>
                    <option value="BIRTHDAY_PARTY">Birthday Party</option>
                    <option value="GROUP_BOOKING">Group Booking</option>
                    <option value="WEDDING_EVENT">Wedding / Reception</option>
                    <option value="CUSTOMER_CALLBACK">Callback Request</option>
                    <option value="GENERAL_ENQUIRY">General Enquiry</option>
                  </select>
                </div>
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Target Date</label>
                  <input
                    type="date"
                    required
                    value={createDate}
                    onChange={(e) => setCreateDate(e.target.value)}
                    className="w-full px-2 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Guests</label>
                  <input
                    type="number"
                    min={1}
                    value={createGuests}
                    onChange={(e) => setCreateGuests(Number(e.target.value))}
                    className="w-full px-2 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Budget Range</label>
                  <input
                    type="text"
                    value={createBudget}
                    onChange={(e) => setCreateBudget(e.target.value)}
                    placeholder="₹2,00,000 - ₹5,00,000"
                    className="w-full px-3 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Assigned Staff</label>
                  <input
                    type="text"
                    value={createStaff}
                    onChange={(e) => setCreateStaff(e.target.value)}
                    placeholder="Staff owner name"
                    className="w-full px-3 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">Requirements & Vision</label>
                <textarea
                  rows={2}
                  value={createNotes}
                  onChange={(e) => setCreateNotes(e.target.value)}
                  placeholder="AV projector needed, cocktail tasting menu, rooftop seating preference..."
                  className="w-full px-3 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400"
                />
              </div>

              <div className="pt-2 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setIsCreateModalOpen(false)}
                  className="px-4 py-2 text-slate-400 hover:text-white transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmittingManual}
                  className="px-5 py-2 font-semibold rounded-lg bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 hover:brightness-110 shadow-gold-glow transition disabled:opacity-50"
                >
                  {isSubmittingManual ? 'Saving...' : 'Save Lead'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
