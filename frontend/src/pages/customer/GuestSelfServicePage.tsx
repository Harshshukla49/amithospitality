import React, { useState, useEffect, useRef } from 'react';
import {
  Sparkles,
  Search,
  KeyRound,
  Calendar,
  Clock,
  Users,
  UtensilsCrossed,
  MapPin,
  CheckCircle2,
  AlertCircle,
  XCircle,
  Clock3,
  RefreshCw,
  Edit3,
  Trash2,
  ChevronRight,
  ShieldCheck,
  ArrowLeft,
} from 'lucide-react';
import {
  lookupReservationApi,
  verifyOtpApi,
  getGuestReservationApi,
  modifyGuestReservationApi,
  cancelGuestReservationApi,
  GuestReservationDetails,
} from '../../api/guest';
import { useEnvironment } from '../../context/EnvironmentContext';

export const GuestSelfServicePage: React.FC = () => {
  const { environment, isDemo } = useEnvironment();

  // Workflow states: 'LOOKUP' | 'VERIFY' | 'PORTAL'
  const [step, setStep] = useState<'LOOKUP' | 'VERIFY' | 'PORTAL'>('LOOKUP');

  // Lookup state
  const [referenceId, setReferenceId] = useState('');
  const [contact, setContact] = useState('');
  const [lookupLoading, setLookupLoading] = useState(false);
  const [lookupError, setLookupError] = useState<string | null>(null);

  // OTP state
  const [otp, setOtp] = useState('');
  const [targetMasked, setTargetMasked] = useState('');
  const [targetType, setTargetType] = useState<'PHONE' | 'EMAIL'>('PHONE');
  const [demoOtp, setDemoOtp] = useState<string | null>(null);
  const [verifyLoading, setVerifyLoading] = useState(false);
  const [verifyError, setVerifyError] = useState<string | null>(null);

  // Verified reservation session
  const [guestToken, setGuestToken] = useState<string | null>(null);
  const [reservation, setReservation] = useState<GuestReservationDetails | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Modification modal state
  const [isModifyOpen, setIsModifyOpen] = useState(false);
  const [modDate, setModDate] = useState('');
  const [modTime, setModTime] = useState('');
  const [modCount, setModCount] = useState(2);
  const [modRequests, setModRequests] = useState('');
  const [modLoading, setModLoading] = useState(false);
  const [modError, setModError] = useState<string | null>(null);
  const [modSuccess, setModSuccess] = useState<string | null>(null);

  // Cancellation modal state
  const [isCancelOpen, setIsCancelOpen] = useState(false);
  const [cancelReason, setCancelReason] = useState('Change of personal travel plans');
  const [cancelLoading, setCancelLoading] = useState(false);
  const [cancelError, setCancelError] = useState<string | null>(null);

  // Auto-polling ref
  const pollIntervalRef = useRef<number | null>(null);

  // Step 1: Submit Lookup
  const handleLookup = async (e: React.FormEvent) => {
    e.preventDefault();
    setLookupError(null);
    setLookupLoading(true);

    try {
      const res = await lookupReservationApi(referenceId.trim().toUpperCase(), contact.trim());
      setReferenceId(res.reference_id);
      setTargetMasked(res.target_masked);
      setTargetType(res.target_type);
      if (res.demo_otp) {
        setDemoOtp(res.demo_otp);
        setOtp(res.demo_otp); // Pre-fill for ease of testing in DEMO mode
      }
      setStep('VERIFY');
    } catch (err: any) {
      setLookupError(err.message || 'No reservation found matching this reference and contact details.');
    } finally {
      setLookupLoading(false);
    }
  };

  // Step 2: Submit OTP Verification
  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    setVerifyError(null);
    setVerifyLoading(true);

    try {
      const res = await verifyOtpApi(referenceId, otp.trim());
      setGuestToken(res.access_token);
      setReservation(res.reservation);
      setStep('PORTAL');
    } catch (err: any) {
      setVerifyError(err.message || 'Invalid or expired verification code.');
    } finally {
      setVerifyLoading(false);
    }
  };

  // Step 3: Refresh Reservation Details (REST Polling Fallback)
  const refreshDetails = async () => {
    if (!guestToken || !referenceId) return;
    setIsRefreshing(true);
    try {
      const data = await getGuestReservationApi(referenceId, guestToken);
      setReservation(data);
    } catch (err) {
      console.warn('Refresh notice:', err);
    } finally {
      setIsRefreshing(false);
    }
  };

  // Background polling every 15 seconds while active
  useEffect(() => {
    if (step === 'PORTAL' && guestToken && referenceId) {
      pollIntervalRef.current = window.setInterval(() => {
        refreshDetails();
      }, 15000);
    }
    return () => {
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    };
  }, [step, guestToken, referenceId]);

  // Open Modification Modal
  const openModifyModal = () => {
    if (!reservation) return;
    setModDate(reservation.reservation_date);
    setModTime(reservation.reservation_time);
    setModCount(reservation.guest_count);
    setModRequests(reservation.special_requests || '');
    setModError(null);
    setModSuccess(null);
    setIsModifyOpen(true);
  };

  // Submit Modification
  const handleModifySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!guestToken || !reservation) return;
    setModLoading(true);
    setModError(null);

    try {
      const res = await modifyGuestReservationApi(referenceId, guestToken, {
        reservation_date: modDate,
        reservation_time: modTime,
        guest_count: modCount,
        special_requests: modRequests,
      });
      setReservation(res.reservation);
      setModSuccess(res.message);
      setTimeout(() => {
        setIsModifyOpen(false);
        setModSuccess(null);
      }, 1200);
    } catch (err: any) {
      setModError(err.message || 'Failed to modify reservation. Please check availability.');
    } finally {
      setModLoading(false);
    }
  };

  // Submit Cancellation
  const handleCancelSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!guestToken || !reservation) return;
    setCancelLoading(true);
    setCancelError(null);

    try {
      const res = await cancelGuestReservationApi(referenceId, guestToken, cancelReason);
      setReservation(res.reservation);
      setIsCancelOpen(false);
    } catch (err: any) {
      setCancelError(err.message || 'Failed to cancel reservation.');
    } finally {
      setCancelLoading(false);
    }
  };

  // Status Badge Component
  const renderStatusBadge = (status: string) => {
    switch (status.toUpperCase()) {
      case 'ACCEPTED':
      case 'CONFIRMED':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
            <CheckCircle2 className="w-3.5 h-3.5" /> Confirmed Table
          </span>
        );
      case 'MODIFIED':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-blue-500/20 text-blue-300 border border-blue-500/40">
            <Edit3 className="w-3.5 h-3.5" /> Changes Applied
          </span>
        );
      case 'UNDER_REVIEW':
      case 'PENDING':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/40">
            <Clock3 className="w-3.5 h-3.5" /> Under Manager Review
          </span>
        );
      case 'CANCELLED':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-rose-500/20 text-rose-300 border border-rose-500/40">
            <XCircle className="w-3.5 h-3.5" /> Cancelled
          </span>
        );
      case 'COMPLETED':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-slate-500/20 text-slate-300 border border-slate-500/40">
            <CheckCircle2 className="w-3.5 h-3.5" /> Completed
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-gold-500/20 text-gold-300 border border-gold-500/40">
            <Clock className="w-3.5 h-3.5" /> Request Received
          </span>
        );
    }
  };

  return (
    <div className="min-h-[calc(100vh-8rem)] py-8 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto flex flex-col justify-center">
      {/* Header Banner */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-gold-400/10 border border-gold-400/30 text-gold-400 text-xs font-semibold tracking-wider uppercase mb-3">
          <Sparkles className="w-3.5 h-3.5" /> Guest Self-Service Portal
        </div>
        <h1 className="font-serif text-3xl sm:text-4xl font-bold text-white tracking-wide">
          Manage Your Reservation
        </h1>
        <p className="mt-2 text-sm text-slate-400 max-w-xl mx-auto">
          View live table status, modify booking time or party size, or securely cancel your dining reservation.
        </p>
      </div>

      {/* STEP 1: LOOKUP FORM */}
      {step === 'LOOKUP' && (
        <div className="glass-panel border border-gold-400/20 rounded-2xl p-6 sm:p-8 shadow-2xl backdrop-blur-xl">
          <form onSubmit={handleLookup} className="space-y-6">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                Booking Reference ID
              </label>
              <div className="relative">
                <input
                  type="text"
                  required
                  placeholder="e.g. REF-RES-20261110-XXXXXX"
                  value={referenceId}
                  onChange={(e) => setReferenceId(e.target.value)}
                  className="w-full bg-charcoal-900/90 border border-slate-700 rounded-xl px-4 py-3 pl-11 text-white placeholder-slate-500 font-mono focus:border-gold-400 focus:outline-none focus:ring-1 focus:ring-gold-400 transition"
                />
                <Search className="w-5 h-5 text-slate-400 absolute left-3.5 top-3.5" />
              </div>
              <p className="mt-1 text-[11px] text-slate-400">
                Found on your SMS or email booking confirmation.
              </p>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                Registered Phone or Email
              </label>
              <input
                type="text"
                required
                placeholder="+91 98765 00001 or guest@example.com"
                value={contact}
                onChange={(e) => setContact(e.target.value)}
                className="w-full bg-charcoal-900/90 border border-slate-700 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:border-gold-400 focus:outline-none focus:ring-1 focus:ring-gold-400 transition"
              />
            </div>

            {lookupError && (
              <div className="p-3.5 rounded-xl bg-rose-500/15 border border-rose-500/30 flex items-start gap-2.5 text-xs text-rose-300">
                <AlertCircle className="w-4 h-4 shrink-0 text-rose-400 mt-0.5" />
                <span>{lookupError}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={lookupLoading}
              className="w-full py-3.5 px-6 rounded-xl font-semibold bg-gradient-to-r from-gold-500 to-gold-600 hover:from-gold-400 hover:to-gold-500 text-obsidian-950 shadow-gold-glow flex items-center justify-center gap-2 transition disabled:opacity-50"
            >
              {lookupLoading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Locating Reservation...</span>
                </>
              ) : (
                <>
                  <span>Verify & Access Reservation</span>
                  <ChevronRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>
        </div>
      )}

      {/* STEP 2: VERIFICATION OTP CODE */}
      {step === 'VERIFY' && (
        <div className="glass-panel border border-gold-400/20 rounded-2xl p-6 sm:p-8 shadow-2xl backdrop-blur-xl">
          <button
            onClick={() => setStep('LOOKUP')}
            className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-gold-300 mb-6 transition"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> Back to Reference Lookup
          </button>

          <div className="text-center mb-6">
            <div className="w-12 h-12 rounded-2xl bg-gold-400/10 border border-gold-400/30 flex items-center justify-center mx-auto mb-3 text-gold-400">
              <KeyRound className="w-6 h-6" />
            </div>
            <h2 className="text-xl font-bold text-white">Enter 6-Digit Verification Code</h2>
            <p className="text-xs text-slate-400 mt-1">
              A single-use security code has been sent to{' '}
              <span className="font-semibold text-slate-200">{targetMasked}</span>
            </p>
            {isDemo && demoOtp && (
              <div className="mt-3 inline-block px-3 py-1 rounded-lg bg-amber-500/15 border border-amber-500/30 text-[11px] text-amber-300 font-mono">
                DEMO MODE CODE: <strong>{demoOtp}</strong>
              </div>
            )}
          </div>

          <form onSubmit={handleVerifyOtp} className="space-y-6">
            <div>
              <input
                type="text"
                required
                maxLength={6}
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                placeholder="123456"
                className="w-full text-center text-2xl tracking-[0.5em] font-mono bg-charcoal-900 border border-slate-700 rounded-xl py-3 text-gold-300 focus:border-gold-400 focus:outline-none focus:ring-1 focus:ring-gold-400 transition"
              />
            </div>

            {verifyError && (
              <div className="p-3.5 rounded-xl bg-rose-500/15 border border-rose-500/30 flex items-start gap-2.5 text-xs text-rose-300">
                <AlertCircle className="w-4 h-4 shrink-0 text-rose-400 mt-0.5" />
                <span>{verifyError}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={verifyLoading || otp.length < 4}
              className="w-full py-3.5 px-6 rounded-xl font-semibold bg-gradient-to-r from-gold-500 to-gold-600 hover:from-gold-400 hover:to-gold-500 text-obsidian-950 shadow-gold-glow flex items-center justify-center gap-2 transition disabled:opacity-50"
            >
              {verifyLoading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Validating Code...</span>
                </>
              ) : (
                <>
                  <ShieldCheck className="w-4 h-4" />
                  <span>Confirm Verification Code</span>
                </>
              )}
            </button>
          </form>
        </div>
      )}

      {/* STEP 3: RESERVATION DETAILS & SELF-SERVICE PORTAL */}
      {step === 'PORTAL' && reservation && (
        <div className="space-y-6">
          {/* Top Status Card */}
          <div className="glass-panel border border-gold-400/20 rounded-2xl p-6 sm:p-8 shadow-2xl relative overflow-hidden">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-700/80">
              <div>
                <span className="text-[11px] text-slate-400 tracking-wider font-mono">
                  BOOKING REFERENCE
                </span>
                <h2 className="text-2xl font-serif font-bold text-gold-300 tracking-wide mt-0.5">
                  {reservation.reference_id}
                </h2>
              </div>
              <div className="flex items-center gap-3">
                {renderStatusBadge(reservation.status)}
                <button
                  onClick={refreshDetails}
                  disabled={isRefreshing}
                  title="Refresh live reservation status"
                  className="p-2 rounded-lg bg-charcoal-900 border border-slate-700 text-slate-400 hover:text-white transition disabled:opacity-50"
                >
                  <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-gold-400' : ''}`} />
                </button>
              </div>
            </div>

            {/* Core Details Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6 py-6 border-b border-slate-700/80">
              <div>
                <span className="text-xs text-slate-400 flex items-center gap-1.5 mb-1">
                  <UtensilsCrossed className="w-3.5 h-3.5 text-gold-400" /> Dining Venue
                </span>
                <p className="font-semibold text-white">{reservation.outlet_name}</p>
                <p className="text-[11px] text-slate-400">{reservation.outlet_location}</p>
              </div>

              <div>
                <span className="text-xs text-slate-400 flex items-center gap-1.5 mb-1">
                  <Calendar className="w-3.5 h-3.5 text-gold-400" /> Date
                </span>
                <p className="font-semibold text-white">{reservation.reservation_date}</p>
                <p className="text-[11px] text-slate-400">Dress code: {reservation.outlet_dress_code}</p>
              </div>

              <div>
                <span className="text-xs text-slate-400 flex items-center gap-1.5 mb-1">
                  <Clock className="w-3.5 h-3.5 text-gold-400" /> Seating Time
                </span>
                <p className="font-semibold text-white">{reservation.reservation_time}</p>
                <p className="text-[11px] text-slate-400">
                  Hours: {reservation.outlet_opening_time} – {reservation.outlet_closing_time}
                </p>
              </div>

              <div>
                <span className="text-xs text-slate-400 flex items-center gap-1.5 mb-1">
                  <Users className="w-3.5 h-3.5 text-gold-400" /> Party Size
                </span>
                <p className="font-semibold text-white">{reservation.guest_count} Guests</p>
                <p className="text-[11px] text-slate-400">Section: {reservation.seating_preference}</p>
              </div>
            </div>

            {/* Special Requests */}
            {reservation.special_requests && (
              <div className="py-4 border-b border-slate-700/80 text-xs text-slate-300">
                <span className="font-semibold text-gold-400 uppercase tracking-wider block mb-1">
                  Special Requests / Dietary Notes:
                </span>
                <p className="italic bg-charcoal-900/60 p-3 rounded-xl border border-slate-800">
                  "{reservation.special_requests}"
                </p>
              </div>
            )}

            {/* Action Bar */}
            <div className="pt-6 flex flex-wrap items-center justify-between gap-4">
              <div className="text-xs text-slate-400">
                Need phone assistance? Call our Concierge hotline:{' '}
                <a href="tel:+911140509900" className="text-gold-300 font-semibold hover:underline">
                  +91 11 4050 9900
                </a>
              </div>

              <div className="flex items-center gap-3">
                {reservation.can_modify && reservation.status !== 'CANCELLED' && (
                  <button
                    onClick={openModifyModal}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-charcoal-900 border border-gold-400/40 text-gold-300 hover:bg-gold-500/10 transition"
                  >
                    <Edit3 className="w-3.5 h-3.5" />
                    <span>Modify Booking</span>
                  </button>
                )}

                {reservation.can_cancel && reservation.status !== 'CANCELLED' && (
                  <button
                    onClick={() => setIsCancelOpen(true)}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-rose-500/10 border border-rose-500/30 text-rose-300 hover:bg-rose-500/20 transition"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                    <span>Cancel Reservation</span>
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: SELF-SERVICE MODIFICATION */}
      {isModifyOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-obsidian-950/80 backdrop-blur-md">
          <div className="glass-panel border border-gold-400/30 rounded-2xl p-6 sm:p-8 max-w-lg w-full shadow-2xl relative">
            <h3 className="text-xl font-serif font-bold text-white mb-2">Modify Your Reservation</h3>
            <p className="text-xs text-slate-400 mb-6">
              Update your preferred date, time or party size. Significant party size increases may require manager review.
            </p>

            <form onSubmit={handleModifySubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Date</label>
                  <input
                    type="date"
                    required
                    value={modDate}
                    onChange={(e) => setModDate(e.target.value)}
                    className="w-full bg-charcoal-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:border-gold-400 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Time</label>
                  <input
                    type="time"
                    required
                    value={modTime}
                    onChange={(e) => setModTime(e.target.value)}
                    className="w-full bg-charcoal-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:border-gold-400 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Party Size (Guests)
                </label>
                <div className="flex items-center gap-3">
                  <button
                    type="button"
                    onClick={() => setModCount(Math.max(1, modCount - 1))}
                    className="w-9 h-9 rounded-lg bg-charcoal-900 border border-slate-700 text-slate-300 hover:bg-charcoal-800 flex items-center justify-center font-bold"
                  >
                    -
                  </button>
                  <span className="text-base font-bold text-gold-300 font-mono w-10 text-center">
                    {modCount}
                  </span>
                  <button
                    type="button"
                    onClick={() => setModCount(modCount + 1)}
                    className="w-9 h-9 rounded-lg bg-charcoal-900 border border-slate-700 text-slate-300 hover:bg-charcoal-800 flex items-center justify-center font-bold"
                  >
                    +
                  </button>
                  {modCount > 6 && (
                    <span className="text-[11px] text-amber-400">
                      * Parties &gt;6 require manager approval
                    </span>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Updated Special Requests
                </label>
                <textarea
                  rows={3}
                  value={modRequests}
                  onChange={(e) => setModRequests(e.target.value)}
                  placeholder="Seating preferences, dietary allergies, celebration notes..."
                  className="w-full bg-charcoal-900 border border-slate-700 rounded-xl p-3 text-xs text-white placeholder-slate-500 focus:border-gold-400 focus:outline-none"
                />
              </div>

              {modError && (
                <div className="p-3 rounded-xl bg-rose-500/15 border border-rose-500/30 text-xs text-rose-300">
                  {modError}
                </div>
              )}

              {modSuccess && (
                <div className="p-3 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-xs text-emerald-300">
                  {modSuccess}
                </div>
              )}

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-700">
                <button
                  type="button"
                  onClick={() => setIsModifyOpen(false)}
                  className="px-4 py-2 rounded-xl text-xs text-slate-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={modLoading}
                  className="px-5 py-2.5 rounded-xl font-semibold bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 text-xs shadow-gold-glow disabled:opacity-50"
                >
                  {modLoading ? 'Updating...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: CANCELLATION */}
      {isCancelOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-obsidian-950/80 backdrop-blur-md">
          <div className="glass-panel border border-rose-500/30 rounded-2xl p-6 sm:p-8 max-w-md w-full shadow-2xl relative">
            <h3 className="text-xl font-serif font-bold text-white mb-2">Cancel Reservation</h3>
            <p className="text-xs text-slate-400 mb-4">
              Are you sure you wish to cancel booking <strong>{referenceId}</strong>? Your table will be immediately released to other waiting guests.
            </p>

            <form onSubmit={handleCancelSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Reason for Cancellation
                </label>
                <select
                  value={cancelReason}
                  onChange={(e) => setCancelReason(e.target.value)}
                  className="w-full bg-charcoal-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:border-rose-400 focus:outline-none"
                >
                  <option value="Change of personal travel plans">Change of travel plans</option>
                  <option value="Illness or unexpected emergency">Illness or unexpected emergency</option>
                  <option value="Booked incorrect restaurant outlet">Booked incorrect restaurant outlet</option>
                  <option value="Made duplicate booking">Made duplicate booking</option>
                  <option value="Other personal reasons">Other personal reasons</option>
                </select>
              </div>

              {cancelError && (
                <div className="p-3 rounded-xl bg-rose-500/15 border border-rose-500/30 text-xs text-rose-300">
                  {cancelError}
                </div>
              )}

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-700">
                <button
                  type="button"
                  onClick={() => setIsCancelOpen(false)}
                  className="px-4 py-2 rounded-xl text-xs text-slate-400 hover:text-white"
                >
                  Keep Reservation
                </button>
                <button
                  type="submit"
                  disabled={cancelLoading}
                  className="px-5 py-2.5 rounded-xl font-semibold bg-rose-600 hover:bg-rose-500 text-white text-xs disabled:opacity-50"
                >
                  {cancelLoading ? 'Cancelling...' : 'Confirm Cancellation'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
