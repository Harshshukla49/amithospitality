import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Sparkles,
  Calendar,
  Music,
  MapPin,
  Clock,
  ArrowRight,
  Filter,
  CheckCircle,
  Bell,
  Search,
  Shield,
  Star,
} from 'lucide-react';
import { VERIFIED_HISTORICAL_EVENTS, VerifiedEvent } from '../../utils/mockData';

export const EventsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'UPCOMING' | 'PAST'>('PAST');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [rsvpEmail, setRsvpEmail] = useState('');
  const [rsvpSubmitted, setRsvpSubmitted] = useState(false);

  const categories = ['ALL', 'LIVE_MUSIC', 'CELEBRITY_SHOW', 'SUFI_NIGHT', 'ACOUSTIC', 'BOLLYWOOD'];

  const filteredPastEvents = VERIFIED_HISTORICAL_EVENTS.filter((evt) => {
    return selectedCategory === 'ALL' || evt.category === selectedCategory;
  });

  const handleRsvpSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (rsvpEmail.trim()) {
      setRsvpSubmitted(true);
      setRsvpEmail('');
    }
  };

  return (
    <div className="min-h-screen bg-obsidian-950 text-slate-100 font-sans pb-24">
      {/* 1. HERO HEADER */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 border-b border-slate-800 bg-gradient-to-b from-charcoal-900 via-obsidian-950 to-obsidian-950">
        <div className="max-w-4xl mx-auto text-center space-y-4">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-charcoal-900 border border-gold-400/40 text-gold-300 text-xs font-mono uppercase tracking-widest">
            <Music className="w-3.5 h-3.5 text-gold-400" />
            <span>Live Entertainment &amp; Concerts</span>
          </div>
          <h1 className="text-4xl sm:text-5xl font-serif font-bold text-white tracking-tight">
            Events &amp; Stage Experiences
          </h1>
          <p className="text-sm sm:text-base text-slate-300 font-light max-w-2xl mx-auto leading-relaxed">
            From Padmashri Usha Uthup and high-energy rock bands to soulful Sufi voyages across The Warehouse Cafe and Lord of the Drinks.
          </p>

          {/* Tab Switcher: Upcoming vs Past Events */}
          <div className="pt-6 flex justify-center">
            <div className="inline-flex p-1 rounded-2xl bg-charcoal-900 border border-slate-800">
              <button
                onClick={() => setActiveTab('PAST')}
                className={`px-6 py-2.5 rounded-xl text-xs font-semibold transition ${
                  activeTab === 'PAST'
                    ? 'bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 shadow-gold-glow'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                Past Event Highlights (Verified Lineup)
              </button>
              <button
                onClick={() => setActiveTab('UPCOMING')}
                className={`px-6 py-2.5 rounded-xl text-xs font-semibold transition ${
                  activeTab === 'UPCOMING'
                    ? 'bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 shadow-gold-glow'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                Upcoming Experiences
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* 2. TAB CONTENT */}
      {activeTab === 'PAST' ? (
        <section className="py-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-8 animate-fade-in">
          {/* Category Filter */}
          <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs font-mono uppercase text-slate-400 mr-2 flex items-center gap-1">
                <Filter className="w-3.5 h-3.5 text-gold-400" />
                Category:
              </span>
              {categories.map((cat) => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-mono transition ${
                    selectedCategory === cat
                      ? 'bg-charcoal-800 text-gold-300 border border-gold-400/40 font-semibold'
                      : 'bg-charcoal-950 text-slate-400 border border-slate-800 hover:text-white'
                  }`}
                >
                  {cat.replace('_', ' ')}
                </button>
              ))}
            </div>

            <p className="text-xs font-mono text-slate-500">
              Showing {filteredPastEvents.length} archived historical performances
            </p>
          </div>

          {/* Past Events Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredPastEvents.map((evt) => (
              <div
                key={evt.id}
                className="rounded-2xl bg-charcoal-900 border border-slate-800 hover:border-gold-400/40 overflow-hidden shadow-xl group transition flex flex-col justify-between"
              >
                <div className="relative h-52 overflow-hidden">
                  <img
                    src={evt.imageUrl}
                    alt={evt.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    loading="lazy"
                  />
                  <div className="absolute top-3 right-3">
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-semibold uppercase bg-obsidian-950/80 text-gold-300 border border-gold-400/30 backdrop-blur-sm">
                      {evt.category.replace('_', ' ')}
                    </span>
                  </div>
                  <div className="absolute bottom-3 left-3">
                    <span className="px-2.5 py-1 rounded-lg text-xs font-mono font-bold bg-charcoal-900/90 text-white backdrop-blur-md">
                      {evt.dateStr}
                    </span>
                  </div>
                </div>

                <div className="p-6 space-y-3 flex-1 flex flex-col justify-between">
                  <div>
                    <h3 className="text-lg font-serif font-bold text-white group-hover:text-gold-200 transition-colors">
                      {evt.title}
                    </h3>
                    <p className="text-xs text-gold-400 font-mono mt-0.5">
                      Featuring {evt.artistOrFeature}
                    </p>
                    <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                      {evt.description}
                    </p>
                  </div>

                  <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
                    <span className="flex items-center gap-1.5 font-mono">
                      <MapPin className="w-3.5 h-3.5 text-gold-400" />
                      {evt.venueName}
                    </span>
                    <span className="text-[10px] font-mono uppercase tracking-wider text-slate-500">
                      Archived
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      ) : (
        /* UPCOMING EVENTS TAB */
        <section className="py-16 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto space-y-10 animate-fade-in text-center">
          <div className="p-10 sm:p-14 rounded-3xl bg-charcoal-900 border border-gold-400/40 shadow-2xl space-y-6">
            <div className="w-16 h-16 rounded-full bg-gold-400/10 border border-gold-400/30 flex items-center justify-center mx-auto text-gold-400">
              <Bell className="w-8 h-8" />
            </div>

            <div className="space-y-2">
              <span className="text-xs font-mono uppercase tracking-widest text-gold-400 font-semibold">
                Winter &amp; Spring 2026 Season
              </span>
              <h2 className="text-3xl sm:text-4xl font-serif font-bold text-white">
                Stay Tuned for Upcoming Experiences
              </h2>
              <p className="text-sm text-slate-300 max-w-xl mx-auto leading-relaxed">
                Our entertainment curators are finalizing the upcoming lineup of live acoustic gigs, Sufi performances, and celebrity DJ sets across Lord of the Drinks and The Warehouse Cafe.
              </p>
            </div>

            {/* Notification Registration Box */}
            <div className="max-w-md mx-auto pt-4">
              {rsvpSubmitted ? (
                <div className="p-4 rounded-xl bg-emerald-950/60 border border-emerald-500/50 text-emerald-300 text-xs flex items-center justify-center gap-2">
                  <CheckCircle className="w-4 h-4" />
                  <span>Thank you! We'll alert you the moment the next live concert is announced.</span>
                </div>
              ) : (
                <form onSubmit={handleRsvpSubmit} className="flex gap-2">
                  <input
                    type="email"
                    value={rsvpEmail}
                    onChange={(e) => setRsvpEmail(e.target.value)}
                    placeholder="Enter your email for live gig alerts..."
                    required
                    className="flex-1 px-4 py-2.5 rounded-xl bg-charcoal-950 border border-slate-700 text-white placeholder-slate-500 text-xs focus:outline-none focus:border-gold-400"
                  />
                  <button
                    type="submit"
                    className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 font-bold text-xs hover:brightness-110 transition shadow-gold-glow shrink-0"
                  >
                    Notify Me
                  </button>
                </form>
              )}
            </div>

            <div className="pt-4 text-xs text-slate-500 border-t border-slate-800 flex items-center justify-center gap-2">
              <Shield className="w-3.5 h-3.5 text-gold-400" />
              <span>We respect your privacy. No spam; only verified event announcements.</span>
            </div>
          </div>
        </section>
      )}
    </div>
  );
};
