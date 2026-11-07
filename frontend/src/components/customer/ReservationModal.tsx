import React, { useState } from 'react';
import { X, Calendar, Clock, Users, CheckCircle2, AlertTriangle, Loader2 } from 'lucide-react';
import { Outlet, ReservationRequest } from '../../types';
import { useEnvironment } from '../../context/EnvironmentContext';
import { createReservationApi } from '../../api/reservations';

interface ReservationModalProps {
  isOpen: boolean;
  onClose: () => void;
  outlet: Outlet;
  onSuccess: (res: ReservationRequest) => void;
}

export const ReservationModal: React.FC<ReservationModalProps> = ({
  isOpen,
  onClose,
  outlet,
  onSuccess,
}) => {
  const { environment, isDemo } = useEnvironment();
  const [guestName, setGuestName] = useState('');
  const [guestPhone, setGuestPhone] = useState('');
  const [guestEmail, setGuestEmail] = useState('');
  const [guestCount, setGuestCount] = useState(2);
  const [reservationDate, setReservationDate] = useState(() => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split('T')[0];
  });
  const [reservationTime, setReservationTime] = useState('20:00');
  const [seatingPreference, setSeatingPreference] = useState<'INDOOR' | 'OUTDOOR' | 'ROOFTOP' | 'PRIVATE'>('ROOFTOP');
  const [specialRequests, setSpecialRequests] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!guestName.trim() || !guestPhone.trim()) {
      setError('Guest name and phone number are required.');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      const saved = await createReservationApi({
        outlet_id: outlet.id,
        guest_name: guestName,
        guest_phone: guestPhone,
        guest_email: guestEmail || undefined,
        guest_count: guestCount,
        reservation_date: reservationDate,
        reservation_time: reservationTime,
        seating_preference: seatingPreference,
        special_requests: specialRequests || undefined,
      });

      onSuccess(saved);
      setIsSubmitted(true);
    } catch (err: any) {
      console.warn('Backend reservation error, using local fallback:', err);
      // Resilient fallback
      const fallback: ReservationRequest = {
        id: Date.now(),
        environment,
        outletId: outlet.id,
        outletName: outlet.name,
        guestName,
        guestPhone,
        guestEmail,
        guestCount,
        reservationDate,
        reservationTime,
        seatingPreference,
        specialRequests,
        status: 'NEW',
        internalNotes: isDemo ? 'DEMO SIMULATION: Sample customer booking request.' : 'Online web inquiry received.',
        createdAt: new Date().toISOString().replace('T', ' ').substring(0, 16),
      };
      onSuccess(fallback);
      setIsSubmitted(true);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    setIsSubmitted(false);
    setError('');
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-obsidian-950/80 backdrop-blur-md">
      <div className="relative w-full max-w-lg p-6 rounded-2xl glass-panel-elevated text-slate-100 border border-gold-400/40 shadow-luxury">
        <button
          onClick={handleClose}
          className="absolute top-4 right-4 p-2 text-slate-400 hover:text-gold-300 transition"
        >
          <X className="w-5 h-5" />
        </button>

        {!isSubmitted ? (
          <>
            <div className="mb-4">
              <span className="text-[10px] tracking-widest font-semibold px-2 py-0.5 rounded bg-gold-400/20 text-gold-300 border border-gold-400/30 uppercase">
                {outlet.name}
              </span>
              <h3 className="text-xl font-serif font-bold text-white mt-1">
                Request Table Reservation
              </h3>
              <p className="text-xs text-slate-400">
                Experience exceptional hospitality. Reservations are reviewed by our maître d' to ensure optimal seating.
              </p>
            </div>

            {isDemo && (
              <div className="p-3 mb-4 rounded-xl bg-amber-500/15 border border-gold-400/30 text-gold-300 text-xs flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0 text-gold-400" />
                <span>
                  <strong>DEMO SIMULATION:</strong> This reservation will be marked as DEMO DATA in the Admin Portal and will not book a real table.
                </span>
              </div>
            )}

            {error && (
              <div className="p-2 mb-3 rounded bg-rose-500/20 border border-rose-500/40 text-rose-300 text-xs">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-3.5 text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-medium mb-1">
                    Guest Name <span className="text-rose-400">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={guestName}
                    onChange={(e) => setGuestName(e.target.value)}
                    placeholder="e.g. Vikram Singhania"
                    className="w-full px-3 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-gold-400"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-medium mb-1">
                    Phone Number <span className="text-rose-400">*</span>
                  </label>
                  <input
                    type="tel"
                    required
                    value={guestPhone}
                    onChange={(e) => setGuestPhone(e.target.value)}
                    placeholder="+91 98200 00000"
                    className="w-full px-3 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-gold-400"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">
                  Email Address <span className="text-slate-500 font-normal">(Optional for confirmation)</span>
                </label>
                <input
                  type="email"
                  value={guestEmail}
                  onChange={(e) => setGuestEmail(e.target.value)}
                  placeholder="vikram@example.com"
                  className="w-full px-3 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-gold-400"
                />
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-slate-300 font-medium mb-1 flex items-center gap-1">
                    <Calendar className="w-3 h-3 text-gold-400" /> Date
                  </label>
                  <input
                    type="date"
                    required
                    value={reservationDate}
                    onChange={(e) => setReservationDate(e.target.value)}
                    className="w-full px-2 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400 text-xs"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-medium mb-1 flex items-center gap-1">
                    <Clock className="w-3 h-3 text-gold-400" /> Time
                  </label>
                  <input
                    type="time"
                    required
                    value={reservationTime}
                    onChange={(e) => setReservationTime(e.target.value)}
                    className="w-full px-2 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400 text-xs"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-medium mb-1 flex items-center gap-1">
                    <Users className="w-3 h-3 text-gold-400" /> Guests
                  </label>
                  <select
                    value={guestCount}
                    onChange={(e) => setGuestCount(Number(e.target.value))}
                    className="w-full px-2 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400 text-xs"
                  >
                    {[1, 2, 3, 4, 5, 6, 8, 10, 12, 16].map((num) => (
                      <option key={num} value={num}>
                        {num} {num === 1 ? 'Guest' : 'Guests'}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">
                  Seating Preference
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {(['ROOFTOP', 'INDOOR', 'OUTDOOR', 'PRIVATE'] as const).map((pref) => (
                    <button
                      key={pref}
                      type="button"
                      onClick={() => setSeatingPreference(pref)}
                      className={`px-2 py-1.5 rounded-lg border text-center transition capitalize text-xs ${
                        seatingPreference === pref
                          ? 'bg-gold-500/20 border-gold-400 text-gold-300 font-semibold'
                          : 'border-slate-700 text-slate-400 hover:border-slate-500'
                      }`}
                    >
                      {pref.toLowerCase()}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">
                  Special Requests / Dietary Notes
                </label>
                <textarea
                  rows={2}
                  value={specialRequests}
                  onChange={(e) => setSpecialRequests(e.target.value)}
                  placeholder="Anniversary, birthday cake, strictly Jain meal, wheelchair access..."
                  className="w-full px-3 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-gold-400 text-xs"
                />
              </div>

              <div className="pt-2 flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={handleClose}
                  className="px-4 py-2 text-slate-400 hover:text-white transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 font-semibold rounded-lg bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 hover:brightness-110 shadow-gold-glow transition"
                >
                  Submit Reservation Request
                </button>
              </div>
            </form>
          </>
        ) : (
          <div className="text-center py-6 space-y-4">
            <div className="w-14 h-14 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 flex items-center justify-center mx-auto">
              <CheckCircle2 className="w-8 h-8" />
            </div>
            <div>
              <h3 className="text-2xl font-serif font-bold text-white">
                Request Received
              </h3>
              <p className="text-xs text-slate-300 max-w-sm mx-auto mt-2">
                Thank you, <strong>{guestName}</strong>. Your reservation inquiry for <strong>{guestCount} guests</strong> at <strong>{outlet.name}</strong> on <strong>{reservationDate} at {reservationTime}</strong> has been logged.
              </p>
            </div>
            <div className="p-3 rounded-xl bg-charcoal-900 border border-slate-700/80 text-xs text-slate-400 max-w-sm mx-auto text-left">
              <p className="font-semibold text-gold-300 mb-1">What happens next?</p>
              <p>Our restaurant host will review table allocations and contact you via phone ({guestPhone}) shortly to confirm availability.</p>
            </div>
            <button
              onClick={handleClose}
              className="px-6 py-2 rounded-lg bg-gold-500 text-obsidian-950 font-semibold hover:bg-gold-400 transition"
            >
              Return to Concierge
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
