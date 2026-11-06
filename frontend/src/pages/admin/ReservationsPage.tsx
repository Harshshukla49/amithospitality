import React, { useState } from 'react';
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
} from 'lucide-react';
import { ReservationRequest, ReservationStatus } from '../../types';
import { INITIAL_OUTLETS } from '../../utils/mockData';
import { useEnvironment } from '../../context/EnvironmentContext';

interface ReservationsPageProps {
  reservations: ReservationRequest[];
  onUpdateStatus: (id: number, status: ReservationStatus, notes?: string) => void;
}

export const ReservationsPage: React.FC<ReservationsPageProps> = ({
  reservations,
  onUpdateStatus,
}) => {
  const { environment, isDemo } = useEnvironment();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedOutlet, setSelectedOutlet] = useState<string>('ALL');
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');
  const [activeReservation, setActiveReservation] = useState<ReservationRequest | null>(null);
  const [staffNote, setStaffNote] = useState('');

  const filteredReservations = reservations.filter((r) => {
    const matchesSearch =
      r.guestName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.guestPhone.includes(searchQuery);
    const matchesOutlet = selectedOutlet === 'ALL' || r.outletId === Number(selectedOutlet);
    const matchesStatus = selectedStatus === 'ALL' || r.status === selectedStatus;
    return matchesSearch && matchesOutlet && matchesStatus;
  });

  const handleExportCSV = () => {
    const headers = 'ID,Environment,Outlet,Guest,Phone,Email,Guests,Date,Time,Seating,Status\n';
    const rows = filteredReservations
      .map(
        (r) =>
          `${r.id},${r.environment},"${r.outletName}","${r.guestName}",${r.guestPhone},${r.guestEmail || ''},${r.guestCount},${r.reservationDate},${r.reservationTime},${r.seatingPreference},${r.status}`
      )
      .join('\n');
    const blob = new Blob([headers + rows], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `reservations_${environment.toLowerCase()}_${new Date().toISOString().substring(0, 10)}.csv`;
    a.click();
  };

  const handleApplyStatus = (status: ReservationStatus) => {
    if (!activeReservation) return;
    onUpdateStatus(activeReservation.id, status, staffNote);
    setActiveReservation({ ...activeReservation, status, internalNotes: staffNote || activeReservation.internalNotes });
    setStaffNote('');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[11px] font-mono uppercase tracking-wider text-gold-400 font-semibold">
              Guest Services
            </span>
          </div>
          <h1 className="text-2xl font-serif font-bold text-white tracking-wide">
            Reservation Requests & Table Bookings
          </h1>
          <p className="text-xs text-slate-400 mt-1 max-w-xl">
            Review incoming dining requests, manage maître d' table allocations, and update booking statuses.
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
            placeholder="Search by guest name or phone..."
            className="w-full pl-9 pr-3 py-2 text-xs rounded-xl bg-charcoal-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-gold-400"
          />
        </div>

        <div className="flex items-center gap-2">
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

          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="px-3 py-2 text-xs rounded-xl bg-charcoal-900 border border-slate-700 text-slate-300 focus:outline-none focus:border-gold-400"
          >
            <option value="ALL">All Statuses</option>
            <option value="NEW">New</option>
            <option value="PENDING">Pending</option>
            <option value="ACCEPTED">Accepted</option>
            <option value="REJECTED">Rejected</option>
            <option value="CANCELLED">Cancelled</option>
          </select>
        </div>
      </div>

      {/* Reservations Table */}
      <div className="rounded-2xl glass-panel border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-charcoal-900/90 text-slate-400 uppercase tracking-wider text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Guest Details</th>
                <th className="py-3 px-4">Outlet</th>
                <th className="py-3 px-4">Date & Time</th>
                <th className="py-3 px-4">Covers</th>
                <th className="py-3 px-4">Seating</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {filteredReservations.length > 0 ? (
                filteredReservations.map((res) => (
                  <tr key={res.id} className="hover:bg-charcoal-800/40 transition">
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
                        className={`inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-semibold uppercase tracking-wider ${
                          res.status === 'ACCEPTED'
                            ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                            : res.status === 'PENDING'
                            ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                            : res.status === 'NEW'
                            ? 'bg-sky-500/15 text-sky-400 border border-sky-500/30'
                            : 'bg-rose-500/15 text-rose-400 border border-rose-500/30'
                        }`}
                      >
                        {res.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => {
                          setActiveReservation(res);
                          setStaffNote(res.internalNotes || '');
                        }}
                        className="px-3 py-1.5 rounded-lg bg-charcoal-800 hover:bg-charcoal-700 text-gold-300 border border-slate-700 text-xs font-medium transition"
                      >
                        Review
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="text-center py-10 text-slate-500">
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
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-obsidian-950/80 backdrop-blur-md">
          <div className="relative w-full max-w-lg p-6 rounded-2xl glass-panel-elevated text-slate-100 border border-gold-400/40 shadow-luxury space-y-4">
            <div className="flex items-center justify-between border-b border-slate-700/60 pb-3">
              <div>
                <h3 className="text-lg font-serif font-bold text-white">
                  Reservation #{activeReservation.id}
                </h3>
                <p className="text-xs text-slate-400">{activeReservation.outletName}</p>
              </div>
              <button
                onClick={() => setActiveReservation(null)}
                className="text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <div className="p-3.5 rounded-xl bg-charcoal-900 border border-slate-700 text-xs space-y-2">
              <div className="grid grid-cols-2 gap-2 text-slate-300">
                <div>
                  <span className="text-slate-500">Guest:</span> <strong>{activeReservation.guestName}</strong>
                </div>
                <div>
                  <span className="text-slate-500">Party Size:</span> <strong>{activeReservation.guestCount} Guests</strong>
                </div>
                <div>
                  <span className="text-slate-500">Phone:</span> {activeReservation.guestPhone}
                </div>
                <div>
                  <span className="text-slate-500">Time:</span> {activeReservation.reservationDate} at {activeReservation.reservationTime}
                </div>
                <div>
                  <span className="text-slate-500">Seating:</span> {activeReservation.seatingPreference}
                </div>
                <div>
                  <span className="text-slate-500">Current Status:</span> <strong className="text-gold-400">{activeReservation.status}</strong>
                </div>
              </div>

              {activeReservation.specialRequests && (
                <div className="pt-2 border-t border-slate-800 text-slate-400">
                  <span className="text-gold-300 font-semibold">Special Request:</span> "{activeReservation.specialRequests}"
                </div>
              )}
            </div>

            <div className="space-y-1.5 text-xs">
              <label className="block text-slate-300 font-medium">Internal Maître D' Notes</label>
              <textarea
                rows={2}
                value={staffNote}
                onChange={(e) => setStaffNote(e.target.value)}
                placeholder="Table allocation, dietary confirmation from kitchen, VIP escort..."
                className="w-full px-3 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400"
              />
            </div>

            <div className="pt-2 flex flex-wrap items-center justify-between gap-2 text-xs">
              <span className="text-slate-500">Update Status:</span>
              <div className="flex gap-2">
                <button
                  onClick={() => handleApplyStatus('ACCEPTED')}
                  className="px-3 py-1.5 rounded-lg bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 hover:bg-emerald-500/30 font-semibold transition"
                >
                  Accept & Allocate
                </button>
                <button
                  onClick={() => handleApplyStatus('PENDING')}
                  className="px-3 py-1.5 rounded-lg bg-amber-500/20 text-amber-300 border border-amber-500/40 hover:bg-amber-500/30 font-semibold transition"
                >
                  Mark Under Review
                </button>
                <button
                  onClick={() => handleApplyStatus('REJECTED')}
                  className="px-3 py-1.5 rounded-lg bg-rose-500/20 text-rose-300 border border-rose-500/40 hover:bg-rose-500/30 font-semibold transition"
                >
                  Decline
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
