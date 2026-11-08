import React, { useState, useEffect } from 'react';
import {
  CalendarCheck,
  Search,
  Filter,
  Check,
  X,
  Clock,
  User,
  Phone,
  Mail,
  AlertTriangle,
  Download,
  Eye,
  MessageSquare,
  ShieldAlert,
  History,
  CheckCircle2,
  XCircle,
  HelpCircle,
} from 'lucide-react';
import { ReservationRequest, ReservationStatus, ReservationHistoryItem } from '../../types';
import { INITIAL_OUTLETS } from '../../utils/mockData';
import { useEnvironment } from '../../context/EnvironmentContext';
import { fetchReservationHistoryApi } from '../../api/reservations';

interface ReservationsPageProps {
  reservations: ReservationRequest[];
  onUpdateStatus: (id: number, status: ReservationStatus, notes?: string, assignedStaffName?: string) => void;
}

export const ReservationsPage: React.FC<ReservationsPageProps> = ({
  reservations,
  onUpdateStatus,
}) => {
  const { environment, isDemo } = useEnvironment();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedOutlet, setSelectedOutlet] = useState<string>('ALL');
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [activeReservation, setActiveReservation] = useState<ReservationRequest | null>(null);
  const [staffNote, setStaffNote] = useState('');
  const [assignedStaff, setAssignedStaff] = useState('');
  const [historyItems, setHistoryItems] = useState<ReservationHistoryItem[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  // Load history when active reservation opens
  useEffect(() => {
    if (!activeReservation) {
      setHistoryItems([]);
      return;
    }
    setStaffNote(activeReservation.internalNotes || '');
    setAssignedStaff(activeReservation.assignedStaffName || '');
    setLoadingHistory(true);
    fetchReservationHistoryApi(activeReservation.id)
      .then((data) => setHistoryItems(data))
      .catch((err) => {
        console.warn('Could not fetch reservation history:', err);
        setHistoryItems([]);
      })
      .finally(() => setLoadingHistory(false));
  }, [activeReservation]);

  const filteredReservations = reservations.filter((r) => {
    const q = searchQuery.toLowerCase().trim();
    const matchesSearch =
      !q ||
      r.guestName.toLowerCase().includes(q) ||
      r.guestPhone.includes(q) ||
      (r.guestEmail && r.guestEmail.toLowerCase().includes(q)) ||
      (r.referenceId && r.referenceId.toLowerCase().includes(q)) ||
      String(r.id) === q;

    const matchesOutlet = selectedOutlet === 'ALL' || r.outletId === Number(selectedOutlet);
    const matchesStatus = selectedStatus === 'ALL' || r.status === selectedStatus;
    const matchesDate = !selectedDate || r.reservationDate === selectedDate;

    return matchesSearch && matchesOutlet && matchesStatus && matchesDate;
  });

  const handleExportCSV = () => {
    const headers = 'Reference_ID,ID,Environment,Outlet,Guest_Name,Phone,Email,Covers,Date,Time,Seating_Preference,Status,Assigned_Staff,Internal_Notes\n';
    const rows = filteredReservations
      .map(
        (r) =>
          `"${r.referenceId || ''}",${r.id},${r.environment},"${r.outletName}","${r.guestName}",${r.guestPhone},${r.guestEmail || ''},${r.guestCount},${r.reservationDate},${r.reservationTime},${r.seatingPreference},${r.status},"${r.assignedStaffName || ''}","${(r.internalNotes || '').replace(/"/g, '""')}"`
      )
      .join('\n');
    const blob = new Blob([headers + rows], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `reservations_${environment.toLowerCase()}_${new Date().toISOString().substring(0, 10)}.csv`;
    a.click();
  };

  const handleApplyStatus = (newStatus: ReservationStatus) => {
    if (!activeReservation) return;
    onUpdateStatus(activeReservation.id, newStatus, staffNote, assignedStaff);
    setActiveReservation({
      ...activeReservation,
      status: newStatus,
      internalNotes: staffNote || activeReservation.internalNotes,
      assignedStaffName: assignedStaff || activeReservation.assignedStaffName,
    });
    // Add optimistic history item
    setHistoryItems((prev) => [
      {
        id: Date.now(),
        reservationId: activeReservation.id,
        previousStatus: activeReservation.status,
        newStatus,
        changedByName: 'Staff Member',
        notes: staffNote || 'Status transition applied via Admin console',
        createdAt: new Date().toISOString().replace('T', ' ').substring(0, 19),
      },
      ...prev,
    ]);
  };

  const getStatusBadge = (status: ReservationStatus) => {
    switch (status) {
      case 'ACCEPTED':
        return 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30';
      case 'UNDER_REVIEW':
        return 'bg-sky-500/15 text-sky-400 border border-sky-500/30';
      case 'PENDING':
        return 'bg-amber-500/15 text-amber-400 border border-amber-500/30';
      case 'NEW':
        return 'bg-indigo-500/15 text-indigo-400 border border-indigo-500/30';
      case 'COMPLETED':
        return 'bg-teal-500/15 text-teal-400 border border-teal-500/30';
      case 'REJECTED':
        return 'bg-rose-500/15 text-rose-400 border border-rose-500/30';
      case 'CANCELLED':
        return 'bg-slate-700/60 text-slate-400 border border-slate-600/50';
      default:
        return 'bg-charcoal-800 text-slate-300 border border-slate-700';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[11px] font-mono uppercase tracking-wider text-gold-400 font-semibold">
              Guest Services & Maître d' Console
            </span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-charcoal-800 text-slate-400 border border-slate-700">
              Scope: {environment}
            </span>
          </div>
          <h1 className="text-2xl font-serif font-bold text-white tracking-wide">
            Reservation Requests & Table Bookings
          </h1>
          <p className="text-xs text-slate-400 mt-1 max-w-xl">
            Manage table inquiries, assign staff, enforce seating capacities, and track status transition histories.
          </p>
        </div>

        <button
          onClick={handleExportCSV}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-charcoal-800 hover:bg-charcoal-700 border border-slate-700 text-xs font-semibold text-slate-200 transition self-start md:self-auto shadow-sm"
        >
          <Download className="w-3.5 h-3.5 text-gold-400" />
          <span>Export Records (CSV)</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by Reference ID (REF-RES-...), guest, or phone..."
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

          {/* Status Filter */}
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="px-3 py-2 text-xs rounded-xl bg-charcoal-900 border border-slate-700 text-slate-300 focus:outline-none focus:border-gold-400"
          >
            <option value="ALL">All Statuses</option>
            <option value="NEW">New</option>
            <option value="PENDING">Pending</option>
            <option value="UNDER_REVIEW">Under Review</option>
            <option value="ACCEPTED">Accepted</option>
            <option value="COMPLETED">Completed</option>
            <option value="REJECTED">Rejected</option>
            <option value="CANCELLED">Cancelled</option>
          </select>

          {/* Date Filter */}
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            title="Filter by reservation date"
            className="px-3 py-2 text-xs rounded-xl bg-charcoal-900 border border-slate-700 text-slate-300 focus:outline-none focus:border-gold-400"
          />
          {selectedDate && (
            <button
              onClick={() => setSelectedDate('')}
              className="px-2 py-1 text-slate-400 hover:text-white text-xs"
              title="Clear date filter"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Reservations Table */}
      <div className="rounded-2xl glass-panel border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-charcoal-900/90 text-slate-400 uppercase tracking-wider text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Tracking / Reference</th>
                <th className="py-3 px-4">Guest Details</th>
                <th className="py-3 px-4">Outlet</th>
                <th className="py-3 px-4">Date & Time</th>
                <th className="py-3 px-4">Covers</th>
                <th className="py-3 px-4">Seating</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Assigned</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {filteredReservations.length > 0 ? (
                filteredReservations.map((res) => (
                  <tr key={res.id} className="hover:bg-charcoal-800/40 transition">
                    <td className="py-3.5 px-4 font-mono">
                      <div className="text-gold-300 font-semibold text-[11px]">
                        {res.referenceId || `REF-RES-${res.id}`}
                      </div>
                      <div className="text-[10px] text-slate-500">ID #{res.id}</div>
                    </td>
                    <td className="py-3.5 px-4">
                      <div>
                        <div className="flex items-center gap-1.5 font-semibold text-white">
                          <span>{res.guestName}</span>
                          {res.environment === 'DEMO' && (
                            <span className="text-[9px] font-mono uppercase px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-400 border border-amber-500/30">
                              DEMO
                            </span>
                          )}
                        </div>
                        <p className="text-[11px] text-slate-400 font-mono mt-0.5">
                          {res.guestPhone} {res.guestEmail ? `• ${res.guestEmail}` : ''}
                        </p>
                      </div>
                    </td>
                    <td className="py-3.5 px-4 font-medium text-slate-200">{res.outletName}</td>
                    <td className="py-3.5 px-4 font-mono text-[11px]">
                      <div>{res.reservationDate}</div>
                      <div className="text-gold-400">{res.reservationTime}</div>
                    </td>
                    <td className="py-3.5 px-4 font-mono font-semibold text-slate-200">
                      {res.guestCount} Guests
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded bg-charcoal-800 text-slate-300 border border-slate-700 text-[10px] uppercase font-mono">
                        {res.seatingPreference}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-semibold uppercase tracking-wider ${getStatusBadge(
                          res.status
                        )}`}
                      >
                        {res.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-300">
                      {res.assignedStaffName ? (
                        <span className="text-[11px] text-gold-300 font-medium">
                          {res.assignedStaffName}
                        </span>
                      ) : (
                        <span className="text-[10px] text-slate-500 italic">Unassigned</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => setActiveReservation(res)}
                        className="px-3 py-1.5 rounded-lg bg-charcoal-800 hover:bg-charcoal-700 text-gold-300 border border-slate-700 text-xs font-medium transition"
                      >
                        Manage
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={9} className="text-center py-10 text-slate-500">
                    No reservations matching current filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Review & Maître D' Allocation Modal */}
      {activeReservation && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-obsidian-950/80 backdrop-blur-md overflow-y-auto">
          <div className="relative w-full max-w-2xl p-6 rounded-2xl glass-panel-elevated text-slate-100 border border-gold-400/40 shadow-luxury space-y-4 my-8">
            <div className="flex items-center justify-between border-b border-slate-700/60 pb-3">
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-lg font-serif font-bold text-white">
                    Reservation Details
                  </h3>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-gold-400/15 text-gold-300 border border-gold-400/30">
                    {activeReservation.referenceId || `REF-RES-${activeReservation.id}`}
                  </span>
                  {activeReservation.environment === 'DEMO' && (
                    <span className="text-[9px] font-mono uppercase px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-400 border border-amber-500/30">
                      DEMO DATA
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-400 mt-0.5">{activeReservation.outletName}</p>
              </div>
              <button
                onClick={() => setActiveReservation(null)}
                className="text-slate-400 hover:text-white p-1 rounded-lg"
              >
                ✕
              </button>
            </div>

            {/* Details Grid */}
            <div className="p-3.5 rounded-xl bg-charcoal-900 border border-slate-700 text-xs space-y-2">
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-slate-300">
                <div>
                  <span className="text-slate-500 block text-[10px] uppercase font-mono">Guest</span>
                  <strong className="text-white text-sm">{activeReservation.guestName}</strong>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px] uppercase font-mono">Party Size</span>
                  <strong className="text-white">{activeReservation.guestCount} Guests</strong>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px] uppercase font-mono">Phone Number</span>
                  <span className="font-mono text-slate-200">{activeReservation.guestPhone}</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px] uppercase font-mono">Reservation Schedule</span>
                  <span className="font-mono text-gold-300">
                    {activeReservation.reservationDate} at {activeReservation.reservationTime}
                  </span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px] uppercase font-mono">Seating Preference</span>
                  <span className="font-mono uppercase text-slate-200">
                    {activeReservation.seatingPreference}
                  </span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px] uppercase font-mono">Current Status</span>
                  <span
                    className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase ${getStatusBadge(
                      activeReservation.status
                    )}`}
                  >
                    {activeReservation.status.replace('_', ' ')}
                  </span>
                </div>
              </div>

              {activeReservation.guestEmail && (
                <div className="pt-2 border-t border-slate-800 text-slate-400 text-[11px]">
                  <span className="text-slate-500">Email:</span> {activeReservation.guestEmail}
                </div>
              )}

              {activeReservation.specialRequests && (
                <div className="pt-2 border-t border-slate-800 text-slate-300 text-[11px]">
                  <span className="text-gold-300 font-semibold">Special Requests / Dietary:</span>{' '}
                  <span className="italic">"{activeReservation.specialRequests}"</span>
                </div>
              )}
            </div>

            {/* Staff Assignment & Notes */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              <div>
                <label className="block text-slate-300 font-medium mb-1">Assigned Maître d' / Host</label>
                <input
                  type="text"
                  value={assignedStaff}
                  onChange={(e) => setAssignedStaff(e.target.value)}
                  placeholder="e.g. Vikramaditya (Head Host)"
                  className="w-full px-3 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400"
                />
              </div>
              <div>
                <label className="block text-slate-300 font-medium mb-1">Internal Maître d' Notes</label>
                <input
                  type="text"
                  value={staffNote}
                  onChange={(e) => setStaffNote(e.target.value)}
                  placeholder="Table 14 assigned, kitchen notified of Jain request..."
                  className="w-full px-3 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400"
                />
              </div>
            </div>

            {/* Status Transition Action Buttons */}
            <div className="pt-1 space-y-2">
              <span className="text-slate-400 text-xs font-medium block">
                Update Status Workflow:
              </span>
              <div className="flex flex-wrap gap-2 text-xs">
                <button
                  type="button"
                  onClick={() => handleApplyStatus('ACCEPTED')}
                  className="px-3 py-1.5 rounded-lg bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 hover:bg-emerald-500/30 font-semibold transition"
                >
                  ✓ Accept & Confirm Table
                </button>
                <button
                  type="button"
                  onClick={() => handleApplyStatus('UNDER_REVIEW')}
                  className="px-3 py-1.5 rounded-lg bg-sky-500/20 text-sky-300 border border-sky-500/40 hover:bg-sky-500/30 font-semibold transition"
                >
                  Mark Under Review
                </button>
                <button
                  type="button"
                  onClick={() => handleApplyStatus('PENDING')}
                  className="px-3 py-1.5 rounded-lg bg-amber-500/20 text-amber-300 border border-amber-500/40 hover:bg-amber-500/30 font-semibold transition"
                >
                  Set Pending
                </button>
                <button
                  type="button"
                  onClick={() => handleApplyStatus('COMPLETED')}
                  className="px-3 py-1.5 rounded-lg bg-teal-500/20 text-teal-300 border border-teal-500/40 hover:bg-teal-500/30 font-semibold transition"
                >
                  Mark Completed
                </button>
                <button
                  type="button"
                  onClick={() => handleApplyStatus('REJECTED')}
                  className="px-3 py-1.5 rounded-lg bg-rose-500/20 text-rose-300 border border-rose-500/40 hover:bg-rose-500/30 font-semibold transition"
                >
                  Reject Request
                </button>
                <button
                  type="button"
                  onClick={() => handleApplyStatus('CANCELLED')}
                  className="px-3 py-1.5 rounded-lg bg-slate-700/60 text-slate-300 border border-slate-600 hover:bg-slate-700 font-semibold transition"
                >
                  Cancel
                </button>
              </div>
            </div>

            {/* Status Transition History Timeline */}
            <div className="pt-3 border-t border-slate-800 text-xs">
              <div className="flex items-center gap-1.5 font-semibold text-slate-300 mb-2">
                <History className="w-3.5 h-3.5 text-gold-400" />
                <span>Status Change Audit History</span>
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
                  No previous status transitions recorded for this reservation.
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
