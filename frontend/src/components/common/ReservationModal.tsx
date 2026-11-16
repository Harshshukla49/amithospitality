import React, { useState } from 'react';
import { X, Calendar, Clock, Users, CheckCircle, AlertCircle, Utensils, Sparkles, Shield } from 'lucide-react';
import { createReservationApi } from '../../api/reservations';
import { useEnvironment } from '../../context/EnvironmentContext';

interface ReservationModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultOutletId?: number;
  defaultOutletName?: string;
}

export const ReservationModal: React.FC<ReservationModalProps> = ({
  isOpen,
  onClose,
  defaultOutletId = 8,
  defaultOutletName = 'Lord of the Drinks',
}) => {
  const { environment } = useEnvironment();

  const [outletId, setOutletId] = useState<number>(defaultOutletId);
  const [guestName, setGuestName] = useState('');
  const [guestPhone, setGuestPhone] = useState('');
  const [guestEmail, setGuestEmail] = useState('');
  const [partySize, setPartySize] = useState(2);
  const [date, setDate] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() + 1);
    return d.toISOString().split('T')[0];
  });
  const [timeSlot, setTimeSlot] = useState('20:00');
  const [specialRequests, setSpecialRequests] = useState('');
  const [seatingPreference, setSeatingPreference] = useState('MAIN_DINING');

  const [submitting, setSubmitting] = useState(false);
  const [submittedReference, setSubmittedReference] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  if (!isOpen) return null;

  const outletsList = [
    { id: 8, name: 'Lord of the Drinks (South City Mall)' },
    { id: 9, name: 'Veneto Kitchen & Bar (South City Mall)' },
    { id: 10, name: 'The Warehouse Cafe (South City Mall)' },
    { id: 11, name: 'Deliite (Diamond Plaza Mall — Tasting/Tours)' },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);

    if (!guestName.trim() || !guestPhone.trim() || !guestEmail.trim()) {
      setErrorMsg('Please complete all contact information fields.');
      return;
    }

    try {
      setSubmitting(true);
      const res = await createReservationApi({
        outlet_id: outletId,
        guest_name: guestName.trim(),
        guest_phone: guestPhone.trim(),
        guest_email: guestEmail.trim(),
        guest_count: partySize,
        reservation_date: date,
        reservation_time: timeSlot,
        seating_preference: seatingPreference,
        special_requests: specialRequests.trim() || undefined,
      });

      setSubmittedReference(res.referenceId || `RES-${Date.now().toString().slice(-6)}`);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to submit reservation request. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleReset = () => {
    setSubmittedReference(null);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-obsidian-950/80 backdrop-blur-md animate-fade-in">
      <div className="relative w-full max-w-xl rounded-2xl bg-charcoal-900 border border-gold-400/40 shadow-2xl p-6 overflow-hidden">
        {/* Close Button */}
        <button
          onClick={handleReset}
          className="absolute top-4 right-4 p-2 rounded-xl text-slate-400 hover:text-white hover:bg-charcoal-800 transition"
        >
          <X className="w-5 h-5" />
        </button>

        {submittedReference ? (
          <div className="text-center py-8 space-y-4 animate-scale-up">
            <div className="w-16 h-16 rounded-full bg-emerald-500/20 border border-emerald-400/50 flex items-center justify-center mx-auto text-emerald-400">
              <CheckCircle className="w-8 h-8" />
            </div>
            <div>
              <span className="text-[11px] font-mono uppercase text-gold-400 font-semibold tracking-widest">
                Reservation Request Received
              </span>
              <h3 className="text-2xl font-serif font-bold text-white mt-1">
                Thank You, {guestName}!
              </h3>
              <p className="text-xs text-slate-400 mt-2 max-w-md mx-auto leading-relaxed">
                Your reservation request has been submitted to the front desk team. Our concierge will review table availability and send a confirmation to your phone and email.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-charcoal-950 border border-slate-800 max-w-sm mx-auto">
              <p className="text-[10px] font-mono uppercase text-slate-500">Request Reference</p>
              <p className="font-mono font-bold text-lg text-gold-300 tracking-wider">
                {submittedReference}
              </p>
              <p className="text-[11px] text-slate-400 mt-1">
                {date} at {timeSlot} • {partySize} Guests
              </p>
            </div>

            <p className="text-[11px] text-amber-300/80 italic">
              * Note: In demonstration mode, table allocations are managed virtually without real SMS fees.
            </p>

            <button
              onClick={handleReset}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 font-bold text-xs hover:brightness-110 transition shadow-gold-glow"
            >
              Done
            </button>
          </div>
        ) : (
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Sparkles className="w-4 h-4 text-gold-400" />
              <span className="text-[10px] font-mono uppercase tracking-widest text-gold-400 font-semibold">
                Table Reservation Request
              </span>
            </div>
            <h3 className="text-xl font-serif font-bold text-white">
              Reserve an Experiential Table
            </h3>
            <p className="text-xs text-slate-400 mt-1">
              Select your preferred brand destination and timing. Our hospitality team will confirm your seating.
            </p>

            {errorMsg && (
              <div className="mt-3 p-3 rounded-xl bg-rose-950/60 border border-rose-500/50 text-rose-300 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="mt-5 space-y-4">
              {/* Outlet Selection */}
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Destination Brand
                </label>
                <select
                  value={outletId}
                  onChange={(e) => setOutletId(Number(e.target.value))}
                  className="w-full px-3.5 py-2 rounded-xl bg-charcoal-950 border border-slate-700 text-white text-xs focus:outline-none focus:border-gold-400"
                >
                  {outletsList.map((o) => (
                    <option key={o.id} value={o.id}>
                      {o.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Date, Time Slot, Party Size */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Date
                  </label>
                  <input
                    type="date"
                    value={date}
                    min={new Date().toISOString().split('T')[0]}
                    onChange={(e) => setDate(e.target.value)}
                    required
                    className="w-full px-3 py-2 rounded-xl bg-charcoal-950 border border-slate-700 text-white text-xs focus:outline-none focus:border-gold-400"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Preferred Time
                  </label>
                  <select
                    value={timeSlot}
                    onChange={(e) => setTimeSlot(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-charcoal-950 border border-slate-700 text-white text-xs focus:outline-none focus:border-gold-400"
                  >
                    <option value="12:30">12:30 PM (Lunch)</option>
                    <option value="13:30">01:30 PM (Lunch)</option>
                    <option value="15:00">03:00 PM (Afternoon)</option>
                    <option value="19:00">07:00 PM (Early Dinner)</option>
                    <option value="20:00">08:00 PM (Prime Dinner)</option>
                    <option value="21:30">09:30 PM (Late Dinner)</option>
                    <option value="22:30">10:30 PM (Nightlife / Ghost Bar)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Guests Count
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="50"
                    value={partySize}
                    onChange={(e) => setPartySize(Number(e.target.value))}
                    required
                    className="w-full px-3 py-2 rounded-xl bg-charcoal-950 border border-slate-700 text-white text-xs focus:outline-none focus:border-gold-400"
                  />
                </div>
              </div>

              {/* Guest Details */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Full Name
                  </label>
                  <input
                    type="text"
                    value={guestName}
                    onChange={(e) => setGuestName(e.target.value)}
                    placeholder="Guest Name"
                    required
                    className="w-full px-3 py-2 rounded-xl bg-charcoal-950 border border-slate-700 text-white text-xs focus:outline-none focus:border-gold-400"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Phone Number
                  </label>
                  <input
                    type="tel"
                    value={guestPhone}
                    onChange={(e) => setGuestPhone(e.target.value)}
                    placeholder="+91 98315XXXXX"
                    required
                    className="w-full px-3 py-2 rounded-xl bg-charcoal-950 border border-slate-700 text-white text-xs focus:outline-none focus:border-gold-400"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={guestEmail}
                    onChange={(e) => setGuestEmail(e.target.value)}
                    placeholder="guest@example.com"
                    required
                    className="w-full px-3 py-2 rounded-xl bg-charcoal-950 border border-slate-700 text-white text-xs focus:outline-none focus:border-gold-400"
                  />
                </div>
              </div>

              {/* Seating Preference & Dietary Notes */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Seating Section
                  </label>
                  <select
                    value={seatingPreference}
                    onChange={(e) => setSeatingPreference(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-charcoal-950 border border-slate-700 text-white text-xs focus:outline-none focus:border-gold-400"
                  >
                    <option value="MAIN_DINING">Main Dining Hall</option>
                    <option value="GHOST_BAR">Ghost Bar / High-Top (LOTD)</option>
                    <option value="PRIVATE_BOOTH">Quiet Intimate Booth</option>
                    <option value="OUTDOOR_AL_FRESCO">Balcony / Al Fresco</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Special Occasion or Notes
                  </label>
                  <input
                    type="text"
                    value={specialRequests}
                    onChange={(e) => setSpecialRequests(e.target.value)}
                    placeholder="e.g., Birthday celebration, Jain food"
                    className="w-full px-3 py-2 rounded-xl bg-charcoal-950 border border-slate-700 text-white text-xs focus:outline-none focus:border-gold-400"
                  />
                </div>
              </div>

              {/* Notice */}
              <div className="p-3 rounded-xl bg-charcoal-950/60 border border-slate-800 text-[11px] text-slate-400 flex items-start gap-2">
                <Shield className="w-4 h-4 text-gold-400 shrink-0 mt-0.5" />
                <span>
                  <strong>Reservation Request Notice:</strong> Submitting this form records a formal table booking request in the restaurant system. Formal confirmation is subject to venue seating capacity.
                </span>
              </div>

              {/* Submit Buttons */}
              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-4 py-2 rounded-xl bg-charcoal-800 text-slate-300 text-xs font-medium hover:bg-charcoal-700 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-6 py-2 rounded-xl bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 font-bold text-xs hover:brightness-110 transition shadow-gold-glow disabled:opacity-50"
                >
                  {submitting ? 'Submitting Request...' : 'Submit Reservation Request'}
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};
