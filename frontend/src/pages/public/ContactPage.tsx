import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Sparkles,
  MapPin,
  Phone,
  Mail,
  Clock,
  Send,
  Building,
  CheckCircle,
  AlertCircle,
  Shield,
  ArrowRight,
  ExternalLink,
} from 'lucide-react';
import { COMPANY_PROFILE } from '../../utils/mockData';
import { createLeadApi } from '../../api/leads';

export const ContactPage: React.FC = () => {
  const [activeVenue, setActiveVenue] = useState('corporate');
  const [senderName, setSenderName] = useState('');
  const [senderPhone, setSenderPhone] = useState('');
  const [senderEmail, setSenderEmail] = useState('');
  const [senderMessage, setSenderMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const venues = [
    {
      id: 'corporate',
      name: 'Corporate Headquarters',
      sub: 'Amit Hospitality LLP Executive Offices',
      address: '401 Kamalalaya Centre, 156A Lenin Sarani, Kolkata - 700013',
      phone: '+91 94323 35967',
      email: 'vanita@amithospitality.com',
      hours: 'Mon - Sat: 10:00 AM – 06:30 PM',
      outletId: 8,
      mapUrl: 'https://maps.google.com/maps?q=Kamalalaya+Centre+156A+Lenin+Sarani+Kolkata&t=&z=15&ie=UTF8&iwloc=&output=embed',
    },
    {
      id: 'lotd',
      name: 'Lord of the Drinks',
      sub: "Kolkata's Tallest Bar & Experiential Nightlife",
      address: '4th Floor, South City Mall, 375 Prince Anwar Shah Road, Kolkata - 700068',
      phones: ['+91 9831568080', '+91 9831638080'],
      email: 'gm@lodkolkata.com',
      hours: 'Every Day: 12:00 PM – 12:00 AM',
      outletId: 8,
      mapUrl: 'https://maps.google.com/maps?q=South+City+Mall+Kolkata&t=&z=15&ie=UTF8&iwloc=&output=embed',
    },
    {
      id: 'veneto',
      name: 'Veneto Kitchen and Bar',
      sub: 'Artisanal Italian & Mediterranean Dining',
      address: '4th Floor, South City Mall, 375 Prince Anwar Shah Road, Kolkata - 700068',
      phones: ['+91 9831939515', '+91 8777368681'],
      email: 'gm.veneto@amithospitality.com',
      hours: 'Every Day: 12:00 PM – 11:30 PM',
      outletId: 9,
      mapUrl: 'https://maps.google.com/maps?q=South+City+Mall+Kolkata&t=&z=15&ie=UTF8&iwloc=&output=embed',
    },
    {
      id: 'warehouse',
      name: 'The Warehouse Cafe',
      sub: 'Contemporary Industrial Cafe & Sunday Brunch',
      address: '4th Floor, South City Mall, 375 Prince Anwar Shah Road, Kolkata - 700068',
      phones: ['+91 9830434580', '+91 9836196969'],
      email: 'gm.warehouse@amithospitality.com',
      hours: 'Every Day: 12:00 PM – 12:00 AM',
      outletId: 10,
      discrepancy: 'Historical listing also recorded +91 9830434680; flagged for verification.',
      mapUrl: 'https://maps.google.com/maps?q=South+City+Mall+Kolkata&t=&z=15&ie=UTF8&iwloc=&output=embed',
    },
    {
      id: 'deliite',
      name: 'Deliite Lifestyle Retail',
      sub: 'Premium Beverage Boutique & Gourmet Refreshments',
      address: '3rd Floor, Diamond Plaza Mall, 68 Jessore Road, Kolkata - 700055',
      phone: '+91 94323 35967 (Corporate Desk)',
      email: 'vanita@amithospitality.com',
      hours: 'Every Day: 11:00 AM – 10:00 PM',
      outletId: 11,
      mapUrl: 'https://maps.google.com/maps?q=Diamond+Plaza+Mall+Kolkata&t=&z=15&ie=UTF8&iwloc=&output=embed',
    },
  ];

  const currentVenue = venues.find((v) => v.id === activeVenue) || venues[0];

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setSuccessMsg(null);

    if (!senderName.trim() || !senderPhone.trim() || !senderEmail.trim() || !senderMessage.trim()) {
      setErrorMsg('Please complete all contact and message fields.');
      return;
    }

    try {
      setSubmitting(true);
      const res = await createLeadApi({
        outlet_id: currentVenue.outletId,
        name: senderName.trim(),
        phone: senderPhone.trim(),
        email: senderEmail.trim(),
        enquiry_type: 'CUSTOMER_CALLBACK',
        guest_count: 2,
        target_date: new Date().toISOString().split('T')[0],
        budget_range: 'Standard',
        notes: `[Contact Form to ${currentVenue.name}]: ${senderMessage.trim()}`,
        source: 'WEBSITE',
      });

      setSuccessMsg(`Your inquiry has been received (Ref: ${res.referenceId || 'LOGGED'}). Our team will reply shortly.`);
      setSenderName('');
      setSenderPhone('');
      setSenderEmail('');
      setSenderMessage('');
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to submit contact message. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-obsidian-950 text-slate-100 font-sans pb-24">
      {/* 1. HERO HEADER */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 border-b border-slate-800 bg-gradient-to-b from-charcoal-900 via-obsidian-950 to-obsidian-950">
        <div className="max-w-4xl mx-auto text-center space-y-4">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-charcoal-900 border border-gold-400/40 text-gold-300 text-xs font-mono uppercase tracking-widest">
            <MapPin className="w-3.5 h-3.5 text-gold-400" />
            <span>Locations &amp; Direct Contact Directory</span>
          </div>
          <h1 className="text-4xl sm:text-5xl font-serif font-bold text-white tracking-tight">
            Connect With Amit Hospitality
          </h1>
          <p className="text-sm sm:text-base text-slate-300 font-light max-w-2xl mx-auto leading-relaxed">
            Reach our executive headquarters or connect directly with our restaurant outlet general managers across South City Mall and Diamond Plaza Mall.
          </p>
        </div>
      </section>

      {/* 2. VENUE TABS & CONTACT CARDS */}
      <section className="py-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-10">
        <div className="flex flex-wrap items-center justify-center gap-2">
          {venues.map((v) => (
            <button
              key={v.id}
              onClick={() => setActiveVenue(v.id)}
              className={`px-4 py-2 rounded-xl text-xs font-medium transition ${
                activeVenue === v.id
                  ? 'bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 font-bold shadow-gold-glow'
                  : 'bg-charcoal-900 text-slate-300 border border-slate-800 hover:border-slate-700'
              }`}
            >
              {v.name}
            </button>
          ))}
        </div>

        {/* Selected Venue Details + Interactive Map */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Contact Details Card (5 cols) */}
          <div className="lg:col-span-5 rounded-3xl bg-charcoal-900 border border-gold-400/30 p-8 space-y-6 shadow-2xl">
            <div>
              <span className="text-[10px] font-mono uppercase tracking-widest text-gold-400 font-semibold">
                Destination Profile
              </span>
              <h2 className="text-2xl font-serif font-bold text-white mt-1">
                {currentVenue.name}
              </h2>
              <p className="text-xs text-slate-400 mt-1">{currentVenue.sub}</p>
            </div>

            <div className="space-y-4 pt-4 border-t border-slate-800 text-xs text-slate-300">
              <div className="flex items-start gap-3">
                <MapPin className="w-4 h-4 text-gold-400 shrink-0 mt-0.5" />
                <div>
                  <p className="text-slate-500 font-mono">Location / Address:</p>
                  <p className="text-white font-medium mt-0.5">{currentVenue.address}</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Phone className="w-4 h-4 text-gold-400 shrink-0 mt-0.5" />
                <div>
                  <p className="text-slate-500 font-mono">Phone (Click-to-Call):</p>
                  {currentVenue.phones ? (
                    <div className="flex flex-wrap gap-2 mt-0.5">
                      {currentVenue.phones.map((p, idx) => (
                        <a
                          key={idx}
                          href={`tel:${p.replace(/\s+/g, '')}`}
                          className="px-2.5 py-1 rounded-lg bg-charcoal-950 border border-slate-800 text-gold-300 hover:text-white hover:border-gold-400 transition"
                        >
                          {p}
                        </a>
                      ))}
                    </div>
                  ) : (
                    <a
                      href={`tel:${currentVenue.phone?.replace(/\s+/g, '')}`}
                      className="text-gold-300 hover:underline block mt-0.5"
                    >
                      {currentVenue.phone}
                    </a>
                  )}
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Mail className="w-4 h-4 text-gold-400 shrink-0 mt-0.5" />
                <div>
                  <p className="text-slate-500 font-mono">Official Email (Click-to-Email):</p>
                  <a
                    href={`mailto:${currentVenue.email}`}
                    className="text-gold-300 hover:underline block mt-0.5"
                  >
                    {currentVenue.email}
                  </a>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Clock className="w-4 h-4 text-gold-400 shrink-0 mt-0.5" />
                <div>
                  <p className="text-slate-500 font-mono">Operational Timings:</p>
                  <p className="text-slate-300 mt-0.5">{currentVenue.hours}</p>
                </div>
              </div>

              {currentVenue.discrepancy && (
                <div className="p-3 rounded-xl bg-charcoal-950 border border-amber-500/30 text-[11px] text-amber-300/90 space-y-1">
                  <p className="font-semibold">Verification Notice:</p>
                  <p className="text-slate-400">{currentVenue.discrepancy}</p>
                </div>
              )}
            </div>

            <div className="pt-2">
              <Link
                to="/enquiry"
                className="w-full text-center block py-2.5 rounded-xl bg-charcoal-800 hover:bg-charcoal-700 text-slate-200 border border-slate-700 text-xs font-semibold transition"
              >
                Plan Private Banquet / Corporate Gathering &rarr;
              </Link>
            </div>
          </div>

          {/* Map & Direct Message Form (7 cols) */}
          <div className="lg:col-span-7 space-y-6">
            {/* Embedded Google Map Frame */}
            <div className="rounded-3xl overflow-hidden border border-slate-800 bg-charcoal-900 shadow-2xl h-64 sm:h-80 relative">
              <iframe
                title={`${currentVenue.name} Google Map Location`}
                src={currentVenue.mapUrl}
                width="100%"
                height="100%"
                style={{ border: 0 }}
                allowFullScreen={false}
                loading="lazy"
                referrerPolicy="no-referrer-when-downgrade"
                className="opacity-80 hover:opacity-100 transition-opacity"
              />
            </div>

            {/* Quick Contact Form */}
            <div className="rounded-3xl bg-charcoal-900 border border-slate-800 p-6 sm:p-8 space-y-4 shadow-xl">
              <h3 className="font-serif font-bold text-lg text-white">
                Send Direct Message to {currentVenue.name}
              </h3>

              {successMsg && (
                <div className="p-3 rounded-xl bg-emerald-950/60 border border-emerald-500/50 text-emerald-300 text-xs flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 shrink-0" />
                  <span>{successMsg}</span>
                </div>
              )}

              {errorMsg && (
                <div className="p-3 rounded-xl bg-rose-950/60 border border-rose-500/50 text-rose-300 text-xs flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{errorMsg}</span>
                </div>
              )}

              <form onSubmit={handleSendMessage} className="space-y-3">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <input
                    type="text"
                    value={senderName}
                    onChange={(e) => setSenderName(e.target.value)}
                    placeholder="Your Name *"
                    required
                    className="px-3.5 py-2 text-xs rounded-xl bg-charcoal-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-gold-400"
                  />
                  <input
                    type="tel"
                    value={senderPhone}
                    onChange={(e) => setSenderPhone(e.target.value)}
                    placeholder="Phone Number *"
                    required
                    className="px-3.5 py-2 text-xs rounded-xl bg-charcoal-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-gold-400"
                  />
                  <input
                    type="email"
                    value={senderEmail}
                    onChange={(e) => setSenderEmail(e.target.value)}
                    placeholder="Email Address *"
                    required
                    className="px-3.5 py-2 text-xs rounded-xl bg-charcoal-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-gold-400"
                  />
                </div>

                <textarea
                  rows={3}
                  value={senderMessage}
                  onChange={(e) => setSenderMessage(e.target.value)}
                  placeholder="How can our management team assist you today? *"
                  required
                  className="w-full px-3.5 py-2 text-xs rounded-xl bg-charcoal-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-gold-400"
                />

                <div className="flex items-center justify-between pt-1">
                  <span className="text-[10px] text-slate-500 font-mono">
                    Protected by Amit Hospitality Secure CRM
                  </span>
                  <button
                    type="submit"
                    disabled={submitting}
                    className="px-6 py-2 rounded-xl bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 font-bold text-xs hover:brightness-110 transition shadow-gold-glow disabled:opacity-50"
                  >
                    {submitting ? 'Sending...' : 'Send Message'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
