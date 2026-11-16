import React, { useState } from 'react';
import {
  Sparkles,
  Mail,
  Phone,
  Calendar,
  Users,
  CheckCircle,
  AlertCircle,
  Shield,
  Send,
  Building,
} from 'lucide-react';
import { createLeadApi } from '../../api/leads';
import { LeadType } from '../../types';

export const EnquiryPage: React.FC = () => {
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');
  const [selectedOutletId, setSelectedOutletId] = useState<number>(8);
  const [enquiryCategory, setEnquiryCategory] = useState<LeadType>('GENERAL_ENQUIRY');
  const [guestCount, setGuestCount] = useState<number>(10);
  const [targetDate, setTargetDate] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() + 7);
    return d.toISOString().split('T')[0];
  });
  const [budgetRange, setBudgetRange] = useState('₹1,00,000 - ₹2,50,000');
  const [message, setMessage] = useState('');

  const [submitting, setSubmitting] = useState(false);
  const [submittedLeadRef, setSubmittedLeadRef] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const brandOptions = [
    { id: 8, name: 'Lord of the Drinks (South City Mall)' },
    { id: 9, name: 'Veneto Kitchen & Bar (South City Mall)' },
    { id: 10, name: 'The Warehouse Cafe (South City Mall)' },
    { id: 11, name: 'Deliite Lifestyle Retail (Diamond Plaza)' },
  ];

  const categoryOptions: { label: string; value: LeadType }[] = [
    { label: 'General Group Enquiry', value: 'GENERAL_ENQUIRY' },
    { label: 'Private Party / Celebration', value: 'PRIVATE_PARTY' },
    { label: 'Corporate Gala / Banquet', value: 'CORPORATE_EVENT' },
    { label: 'Birthday Celebration', value: 'BIRTHDAY_PARTY' },
    { label: 'Large Group Booking (20+ Guests)', value: 'GROUP_BOOKING' },
    { label: 'Brand Partnership / Collaboration', value: 'CUSTOMER_CALLBACK' },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!name.trim() || !phone.trim() || !email.trim()) {
      setErrorMessage('Please fill in your name, contact phone, and email address.');
      return;
    }

    try {
      setSubmitting(true);
      const res = await createLeadApi({
        outlet_id: selectedOutletId,
        name: name.trim(),
        phone: phone.trim(),
        email: email.trim(),
        enquiry_type: enquiryCategory,
        guest_count: guestCount,
        target_date: targetDate,
        budget_range: budgetRange,
        notes: message.trim() || undefined,
        source: 'WEBSITE',
      });

      setSubmittedLeadRef(res.referenceId || `REF-${Date.now().toString().slice(-6)}`);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to submit enquiry to backend. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleReset = () => {
    setSubmittedLeadRef(null);
    setName('');
    setPhone('');
    setEmail('');
    setMessage('');
  };

  return (
    <div className="min-h-screen bg-obsidian-950 text-slate-100 font-sans pb-24">
      {/* 1. HERO HEADER */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 border-b border-slate-800 bg-gradient-to-b from-charcoal-900 via-obsidian-950 to-obsidian-950">
        <div className="max-w-4xl mx-auto text-center space-y-4">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-charcoal-900 border border-gold-400/40 text-gold-300 text-xs font-mono uppercase tracking-widest">
            <Mail className="w-3.5 h-3.5 text-gold-400" />
            <span>Private Dining &amp; Corporate Enquiries</span>
          </div>
          <h1 className="text-4xl sm:text-5xl font-serif font-bold text-white tracking-tight">
            Connect With Our Events Team
          </h1>
          <p className="text-sm sm:text-base text-slate-300 font-light max-w-2xl mx-auto leading-relaxed">
            Planning a private celebration, corporate banquet, wedding reception, or group gathering? Our event curators will assist you every step of the way.
          </p>
        </div>
      </section>

      {/* 2. FORM CONTAINER */}
      <section className="py-12 px-4 sm:px-6 lg:px-8 max-w-3xl mx-auto">
        <div className="p-8 sm:p-12 rounded-3xl bg-charcoal-900 border border-gold-400/30 shadow-2xl space-y-6">
          {errorMessage && (
            <div className="p-4 rounded-xl bg-rose-950/60 border border-rose-500/50 text-rose-300 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          {submittedLeadRef ? (
            <div className="text-center py-8 space-y-4 animate-scale-up">
              <div className="w-16 h-16 rounded-full bg-emerald-500/20 border border-emerald-400/50 flex items-center justify-center mx-auto text-emerald-400">
                <CheckCircle className="w-8 h-8" />
              </div>
              <h3 className="text-2xl font-serif font-bold text-white">
                Enquiry Successfully Logged!
              </h3>
              <p className="text-xs text-slate-300 max-w-md mx-auto leading-relaxed">
                Thank you, <strong>{name}</strong>. Your enquiry has been persisted to the central banquet management system with reference:
              </p>
              <div className="p-4 rounded-xl bg-charcoal-950 border border-slate-800 max-w-sm mx-auto">
                <p className="text-[10px] font-mono uppercase text-slate-500">Tracking Reference</p>
                <p className="font-mono font-bold text-lg text-gold-300 tracking-wider">
                  {submittedLeadRef}
                </p>
              </div>
              <p className="text-xs text-slate-400">
                Our sales director will reach out within 24 business hours to finalize bespoke menus and table configurations.
              </p>
              <button
                onClick={handleReset}
                className="px-6 py-2 rounded-xl bg-charcoal-800 text-slate-200 text-xs font-semibold hover:bg-charcoal-700 transition"
              >
                Submit Another Enquiry
              </button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <span className="text-[10px] font-mono uppercase text-gold-400 font-semibold tracking-wider">
                  Enquiry Specification
                </span>
                <h3 className="text-xl font-serif font-bold text-white mt-1">
                  Tell Us About Your Gathering
                </h3>
              </div>

              {/* Brand & Category Selectors */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Select Brand / Outlet *
                  </label>
                  <select
                    value={selectedOutletId}
                    onChange={(e) => setSelectedOutletId(Number(e.target.value))}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-charcoal-950 border border-slate-700 text-white text-xs focus:outline-none focus:border-gold-400"
                  >
                    {brandOptions.map((b) => (
                      <option key={b.id} value={b.id}>
                        {b.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Enquiry Category *
                  </label>
                  <select
                    value={enquiryCategory}
                    onChange={(e) => setEnquiryCategory(e.target.value as LeadType)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-charcoal-950 border border-slate-700 text-white text-xs focus:outline-none focus:border-gold-400"
                  >
                    {categoryOptions.map((c) => (
                      <option key={c.value} value={c.value}>
                        {c.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Contact Information */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Your Full Name *
                  </label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Organizer Name"
                    required
                    className="w-full px-3.5 py-2.5 rounded-xl bg-charcoal-950 border border-slate-700 text-white text-xs focus:outline-none focus:border-gold-400"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Phone Number *
                  </label>
                  <input
                    type="tel"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder="+91 9831XXXXXX"
                    required
                    className="w-full px-3.5 py-2.5 rounded-xl bg-charcoal-950 border border-slate-700 text-white text-xs focus:outline-none focus:border-gold-400"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Email Address *
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="email@company.com"
                    required
                    className="w-full px-3.5 py-2.5 rounded-xl bg-charcoal-950 border border-slate-700 text-white text-xs focus:outline-none focus:border-gold-400"
                  />
                </div>
              </div>

              {/* Event Details: Date, Guests, Budget */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Target Date *
                  </label>
                  <input
                    type="date"
                    value={targetDate}
                    min={new Date().toISOString().split('T')[0]}
                    onChange={(e) => setTargetDate(e.target.value)}
                    required
                    className="w-full px-3.5 py-2.5 rounded-xl bg-charcoal-950 border border-slate-700 text-white text-xs focus:outline-none focus:border-gold-400"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Estimated Guests
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="500"
                    value={guestCount}
                    onChange={(e) => setGuestCount(Number(e.target.value))}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-charcoal-950 border border-slate-700 text-white text-xs focus:outline-none focus:border-gold-400"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Estimated Budget Range
                  </label>
                  <select
                    value={budgetRange}
                    onChange={(e) => setBudgetRange(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-charcoal-950 border border-slate-700 text-white text-xs focus:outline-none focus:border-gold-400"
                  >
                    <option value="₹25,000 - ₹50,000">₹25,000 - ₹50,000</option>
                    <option value="₹50,000 - ₹1,00,000">₹50,000 - ₹1,00,000</option>
                    <option value="₹1,00,000 - ₹2,50,000">₹1,00,000 - ₹2,50,000</option>
                    <option value="₹2,50,000 - ₹5,00,000">₹2,50,000 - ₹5,00,000</option>
                    <option value="₹5,00,000+">₹5,00,000+ (Grand Gala)</option>
                  </select>
                </div>
              </div>

              {/* Requirements & Notes */}
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Event Specifics / Menu Preferences
                </label>
                <textarea
                  rows={4}
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Tell us about specific culinary preferences (e.g. Jain food, live sushi station), AV/microphone setups, cake, or celebratory decor requirements..."
                  className="w-full px-3.5 py-2.5 rounded-xl bg-charcoal-950 border border-slate-700 text-white text-xs focus:outline-none focus:border-gold-400"
                />
              </div>

              {/* Security & Persistence Notice */}
              <div className="p-3.5 rounded-xl bg-charcoal-950 border border-slate-800 text-[11px] text-slate-400 flex items-start gap-2">
                <Shield className="w-4 h-4 text-gold-400 shrink-0 mt-0.5" />
                <span>
                  <strong>Data Integrity Guarantee:</strong> Your submission generates an official tracked reference in our PostgreSQL CRM pipeline. No data is lost or discarded.
                </span>
              </div>

              <button
                type="submit"
                disabled={submitting}
                className="w-full py-3.5 rounded-xl bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 font-bold text-xs tracking-wider uppercase hover:brightness-110 transition shadow-gold-glow disabled:opacity-50 flex items-center justify-center gap-2"
              >
                <Send className="w-4 h-4" />
                <span>{submitting ? 'Persisting Enquiry to Database...' : 'Submit Event Enquiry'}</span>
              </button>
            </form>
          )}
        </div>
      </section>
    </div>
  );
};
