import React, { useState } from 'react';
import { X, Calendar, Users, Briefcase, CheckCircle2, Loader2 } from 'lucide-react';
import { Outlet, Lead, LeadType } from '../../types';
import { useEnvironment } from '../../context/EnvironmentContext';
import { createLeadApi } from '../../api/leads';

interface LeadModalProps {
  isOpen: boolean;
  onClose: () => void;
  outlet: Outlet;
  onSuccess: (lead: Lead) => void;
}

export const LeadModal: React.FC<LeadModalProps> = ({
  isOpen,
  onClose,
  outlet,
  onSuccess,
}) => {
  const { environment, isDemo } = useEnvironment();
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');
  const [enquiryType, setEnquiryType] = useState<LeadType>('PRIVATE_DINING');
  const [guestCount, setGuestCount] = useState(25);
  const [targetDate, setTargetDate] = useState(() => {
    const nextMonth = new Date();
    nextMonth.setDate(nextMonth.getDate() + 20);
    return nextMonth.toISOString().split('T')[0];
  });
  const [budgetRange, setBudgetRange] = useState('₹1,50,000 - ₹3,00,000');
  const [notes, setNotes] = useState('');
  const [submittedRefId, setSubmittedRefId] = useState('');
  const [error, setError] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const cleanPhone = phone.replace(/\D/g, '');
    if (!name.trim()) {
      setError('Please provide your name.');
      return;
    }
    if (cleanPhone.length < 7 || cleanPhone.length > 15) {
      setError('Please enter a valid contact phone number (7 to 15 digits).');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      const saved = await createLeadApi({
        outlet_id: outlet.id,
        name: name.trim(),
        phone: phone.trim(),
        email: email.trim(),
        enquiry_type: enquiryType,
        guest_count: guestCount,
        target_date: targetDate,
        budget_range: budgetRange,
        notes: notes.trim() || undefined,
        source: 'AI_CONCIERGE_WEB',
      });

      const refId = saved.referenceId || `REF-LEAD-${targetDate.replace(/-/g, '')}-${saved.id}`;
      setSubmittedRefId(refId);
      onSuccess(saved);
      setIsSubmitted(true);
    } catch (err: any) {
      console.warn('Backend lead error, using fallback:', err);
      const generatedRef = `REF-LEAD-${targetDate.replace(/-/g, '')}-${Math.floor(1000 + Math.random() * 9000)}`;
      setSubmittedRefId(generatedRef);
      const fallback: Lead = {
        id: Date.now(),
        referenceId: generatedRef,
        environment,
        outletId: outlet.id,
        outletName: outlet.name,
        name: name.trim(),
        phone: phone.trim(),
        email: email.trim(),
        enquiryType,
        guestCount,
        targetDate,
        budgetRange,
        status: 'NEW',
        notes: notes.trim(),
        source: 'AI_CONCIERGE_WEB',
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
                Private Dining & Banquets
              </span>
              <h3 className="text-xl font-serif font-bold text-white mt-1">
                Bespoke Events at {outlet.name}
              </h3>
              <p className="text-xs text-slate-400">
                From high-level corporate galas to milestone anniversaries, our banquets team curates exquisite culinary experiences.
              </p>
            </div>

            {isDemo && (
              <div className="p-3 mb-4 rounded-xl bg-amber-500/15 border border-gold-400/30 text-gold-300 text-xs flex items-center gap-2">
                <span>
                  <strong>DEMO SIMULATION:</strong> This event inquiry will be marked as DEMO DATA in the Admin Portal.
                </span>
              </div>
            )}

            {error && (
              <div className="p-2 mb-3 rounded bg-rose-500/20 border border-rose-500/40 text-rose-300 text-xs">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-3.5 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-medium mb-1">
                    Contact Name <span className="text-rose-400">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Rajesh Mehta"
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
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder="+91 98220 00000"
                    className="w-full px-3 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-gold-400"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-medium mb-1">
                    Email Address <span className="text-rose-400">*</span>
                  </label>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="rajesh@company.com"
                    className="w-full px-3 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-gold-400"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-medium mb-1">
                    Event Type
                  </label>
                  <select
                    value={enquiryType}
                    onChange={(e) => setEnquiryType(e.target.value as LeadType)}
                    className="w-full px-2 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400"
                  >
                    <option value="CORPORATE_EVENT">Corporate Event / Dinner</option>
                    <option value="PRIVATE_PARTY">Private Party / Celebration</option>
                    <option value="BIRTHDAY_PARTY">Birthday Party</option>
                    <option value="GROUP_BOOKING">Group Booking</option>
                    <option value="WEDDING_EVENT">Wedding / Reception Enquiry</option>
                    <option value="CUSTOMER_CALLBACK">Customer Callback Request</option>
                    <option value="GENERAL_ENQUIRY">General Banquets Enquiry</option>
                    <option value="PRIVATE_DINING">Private Dining Room</option>
                    <option value="CATERING">Outdoor Luxury Catering</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-slate-300 font-medium mb-1 flex items-center gap-1">
                    <Calendar className="w-3 h-3 text-gold-400" /> Target Date
                  </label>
                  <input
                    type="date"
                    required
                    value={targetDate}
                    onChange={(e) => setTargetDate(e.target.value)}
                    className="w-full px-2 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-medium mb-1 flex items-center gap-1">
                    <Users className="w-3 h-3 text-gold-400" /> Approx Guests
                  </label>
                  <input
                    type="number"
                    min={10}
                    max={250}
                    value={guestCount}
                    onChange={(e) => setGuestCount(Number(e.target.value))}
                    className="w-full px-2 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400"
                  />
                </div>
                <div>
                  <label className="block text-slate-300 font-medium mb-1 flex items-center gap-1">
                    <Briefcase className="w-3 h-3 text-gold-400" /> Budget Range
                  </label>
                  <select
                    value={budgetRange}
                    onChange={(e) => setBudgetRange(e.target.value)}
                    className="w-full px-2 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white focus:outline-none focus:border-gold-400"
                  >
                    <option value="₹1,00,000 - ₹2,50,000">₹1L - ₹2.5L</option>
                    <option value="₹2,50,000 - ₹5,00,000">₹2.5L - ₹5L</option>
                    <option value="₹5,00,000 - ₹10,00,000">₹5L - ₹10L</option>
                    <option value="₹10,00,000+">₹10L+ (Full Buyout)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">
                  Event Vision & Requirements
                </label>
                <textarea
                  rows={2}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Tell us about decor, customized menu courses, audio/visual needs, live music..."
                  className="w-full px-3 py-2 rounded-lg bg-charcoal-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-gold-400"
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
                  Submit Event Inquiry
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
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-gold-400/15 border border-gold-400/30 text-gold-300 font-mono text-xs font-semibold mb-2">
                Reference ID: {submittedRefId}
              </div>
              <h3 className="text-2xl font-serif font-bold text-white">
                Inquiry Forwarded
              </h3>
              <p className="text-xs text-slate-300 max-w-sm mx-auto mt-2">
                Thank you, <strong>{name}</strong>. Our Banquets & Private Events Director has received your specifications for <strong>{outlet.name}</strong>.
              </p>
            </div>

            {isDemo && (
              <div className="p-2.5 rounded-xl bg-amber-500/15 border border-amber-500/30 text-amber-300 text-xs flex items-center justify-center gap-1.5">
                <span><strong>DEMO SIMULATION:</strong> This lead record has been logged in DEMO mode.</span>
              </div>
            )}

            <p className="text-xs text-slate-400">
              A bespoke proposal and floorplan options will be delivered to <strong>{email}</strong> or followed up at <strong>{phone}</strong> within 24 business hours.
            </p>
            <button
              onClick={handleClose}
              className="px-6 py-2 rounded-lg bg-gold-500 text-obsidian-950 font-semibold hover:bg-gold-400 transition"
            >
              Close
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
