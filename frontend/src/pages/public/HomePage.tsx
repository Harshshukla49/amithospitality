import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Sparkles,
  ArrowRight,
  Wine,
  Utensils,
  Coffee,
  ShoppingBag,
  Calendar,
  MapPin,
  Clock,
  Phone,
  Shield,
  Star,
  ChevronRight,
  Music,
  HeartHandshake,
  Award,
  Layers,
} from 'lucide-react';
import { COMPANY_PROFILE, VERIFIED_HISTORICAL_EVENTS, HOSPITALITY_GALLERY_ITEMS } from '../../utils/mockData';
import { ReservationModal } from '../../components/common/ReservationModal';

export const HomePage: React.FC = () => {
  const [reservationModalOpen, setReservationModalOpen] = useState(false);
  const [selectedOutletId, setSelectedOutletId] = useState(8);

  const handleOpenReservation = (id: number = 8) => {
    setSelectedOutletId(id);
    setReservationModalOpen(true);
  };

  return (
    <div className="flex flex-col min-h-screen bg-obsidian-950 text-slate-100 font-sans">
      {/* 1. CINEMATIC HERO SECTION */}
      <section className="relative min-h-[90vh] flex items-center justify-center px-4 sm:px-6 lg:px-8 py-20 overflow-hidden">
        {/* Cinematic Backdrop Image with Luxury Gradient Overlay */}
        <div className="absolute inset-0 z-0">
          <img
            src="https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?q=80&w=2000&auto=format&fit=crop"
            alt="Amit Hospitality Luxury Dining Ambiance"
            className="w-full h-full object-cover object-center scale-105 animate-subtle-zoom"
            loading="eager"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-obsidian-950 via-obsidian-950/80 to-obsidian-950/60" />
          <div className="absolute inset-0 bg-radial-gradient from-transparent via-obsidian-950/40 to-obsidian-950" />
        </div>

        {/* Hero Content Box */}
        <div className="relative z-10 max-w-5xl mx-auto text-center space-y-6 animate-fade-in">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-charcoal-900/90 border border-gold-400/40 text-gold-300 text-xs font-mono uppercase tracking-widest shadow-gold-glow backdrop-blur-md">
            <Sparkles className="w-3.5 h-3.5 text-gold-400" />
            <span>Amit Hospitality LLP • Estd 2018</span>
          </div>

          {/* Headline */}
          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-serif font-bold text-white tracking-tight leading-tight">
            Creating Experiences.{' '}
            <span className="block mt-2 bg-gradient-to-r from-gold-300 via-gold-400 to-amber-200 bg-clip-text text-transparent">
              Crafting Memories.
            </span>
          </h1>

          {/* Supporting Text */}
          <p className="text-base sm:text-xl text-slate-300 font-light max-w-3xl mx-auto leading-relaxed">
            Amit Hospitality brings together Kolkata's most distinctive dining destinations, experiential nightlife, and premium lifestyle retail under one vision of culinary innovation and world-class service.
          </p>

          {/* Hero CTAs */}
          <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
            <button
              onClick={() => handleOpenReservation(8)}
              className="px-8 py-3.5 rounded-xl bg-gradient-to-r from-gold-500 via-gold-600 to-amber-500 text-obsidian-950 font-bold text-sm tracking-wide shadow-gold-glow hover:scale-105 hover:brightness-110 transition-all flex items-center gap-2"
            >
              <Calendar className="w-4 h-4" />
              <span>Reserve a Table</span>
            </button>
            <Link
              to="/menus"
              className="px-7 py-3.5 rounded-xl bg-charcoal-900/90 hover:bg-charcoal-800 text-slate-200 border border-slate-700 hover:border-gold-400/50 text-sm font-semibold transition backdrop-blur-md flex items-center gap-2"
            >
              <span>Explore Menus</span>
              <ArrowRight className="w-4 h-4 text-gold-400" />
            </Link>
            <Link
              to="/concierge"
              className="px-7 py-3.5 rounded-xl bg-charcoal-900/90 hover:bg-charcoal-800 text-gold-300 border border-gold-400/30 text-sm font-semibold transition backdrop-blur-md flex items-center gap-2"
            >
              <Sparkles className="w-4 h-4 text-gold-400" />
              <span>Ask AI Concierge</span>
            </Link>
          </div>

          {/* Quick Stats / Highlights Bar */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-12 max-w-4xl mx-auto border-t border-slate-800/80">
            <div className="p-4 rounded-2xl bg-charcoal-900/60 border border-slate-800/80 backdrop-blur-sm">
              <p className="text-2xl font-serif font-bold text-gold-300">2018</p>
              <p className="text-xs text-slate-400 uppercase tracking-wider font-mono mt-1">Inception</p>
            </div>
            <div className="p-4 rounded-2xl bg-charcoal-900/60 border border-slate-800/80 backdrop-blur-sm">
              <p className="text-2xl font-serif font-bold text-gold-300">4 Brands</p>
              <p className="text-xs text-slate-400 uppercase tracking-wider font-mono mt-1">Portfolio Group</p>
            </div>
            <div className="p-4 rounded-2xl bg-charcoal-900/60 border border-slate-800/80 backdrop-blur-sm">
              <p className="text-2xl font-serif font-bold text-gold-300">South City</p>
              <p className="text-xs text-slate-400 uppercase tracking-wider font-mono mt-1">Primary Hub</p>
            </div>
            <div className="p-4 rounded-2xl bg-charcoal-900/60 border border-slate-800/80 backdrop-blur-sm">
              <p className="text-2xl font-serif font-bold text-gold-300">AI Concierge</p>
              <p className="text-xs text-slate-400 uppercase tracking-wider font-mono mt-1">24/7 Guest Care</p>
            </div>
          </div>
        </div>
      </section>

      {/* 2. THE BRAND PORTFOLIO SHOWCASE */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full space-y-12">
        <div className="text-center max-w-3xl mx-auto space-y-3">
          <span className="text-xs font-mono font-semibold uppercase tracking-widest text-gold-400">
            Destinations &amp; Experiences
          </span>
          <h2 className="text-3xl sm:text-4xl font-serif font-bold text-white tracking-wide">
            Our Celebrated Brands
          </h2>
          <p className="text-sm text-slate-400">
            From medieval nightlife and wood-fired Italian kitchens to contemporary industrial brunch cafes and boutique spirits retail.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {COMPANY_PROFILE.brands.map((brand) => (
            <div
              key={brand.id}
              className="group rounded-3xl bg-charcoal-900/80 border border-slate-800 hover:border-gold-400/50 shadow-xl overflow-hidden transition-all duration-300 hover:-translate-y-1 flex flex-col justify-between"
            >
              {/* Image Container with Badges */}
              <div className="relative h-64 overflow-hidden">
                <img
                  src={brand.heroImage}
                  alt={brand.name}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  onError={(e: any) => {
                    e.currentTarget.src = '/images/brands/amit-hospitality.jpg';
                  }}
                  loading="lazy"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-charcoal-900 via-charcoal-900/30 to-transparent" />
                <div className="absolute top-4 left-4">
                  <span className="px-3 py-1 rounded-full text-[10px] font-mono font-bold uppercase tracking-wider bg-obsidian-950/80 text-gold-300 border border-gold-400/40 backdrop-blur-md">
                    {brand.established}
                  </span>
                </div>
                <div className="absolute bottom-4 left-4 right-4">
                  <h3 className="text-2xl font-serif font-bold text-white group-hover:text-gold-200 transition-colors">
                    {brand.name}
                  </h3>
                  <p className="text-xs text-slate-300 font-mono flex items-center gap-1.5 mt-1">
                    <MapPin className="w-3.5 h-3.5 text-gold-400" />
                    <span>{brand.location}</span>
                  </p>
                </div>
              </div>

              {/* Card Body */}
              <div className="p-6 space-y-4 flex-1 flex flex-col justify-between">
                <div className="space-y-2">
                  <p className="text-xs font-semibold text-gold-400 uppercase tracking-wide">
                    {brand.cuisine}
                  </p>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    {brand.hallmark}
                  </p>
                </div>

                <div className="pt-4 border-t border-slate-800 flex items-center justify-between gap-3">
                  <Link
                    to={`/brands/${brand.slug === 'the-warehouse-cafe' ? 'warehouse' : brand.slug}`}
                    className="inline-flex items-center gap-1.5 text-xs font-bold text-gold-400 hover:text-gold-300 transition"
                  >
                    <span>Explore Brand</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                  <button
                    onClick={() => handleOpenReservation(brand.id === 'lotd' ? 8 : brand.id === 'veneto' ? 9 : brand.id === 'warehouse' ? 10 : 11)}
                    className="px-4 py-2 rounded-xl bg-charcoal-800 hover:bg-gold-500 hover:text-obsidian-950 text-slate-200 border border-slate-700 text-xs font-semibold transition"
                  >
                    Reserve Table
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 3. ABOUT THE FOUNDERS & ORIGIN STORY */}
      <section className="py-20 bg-charcoal-900/50 border-y border-slate-800/80 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-charcoal-900 border border-gold-400/30 text-gold-400 text-xs font-mono uppercase tracking-widest">
              <Award className="w-3.5 h-3.5" />
              <span>Origins &amp; Leadership</span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-serif font-bold text-white tracking-wide leading-snug">
              Pioneering Contemporary Hospitality in Eastern India
            </h2>
            <p className="text-sm text-slate-300 leading-relaxed">
              Founded in <strong>2018</strong> by visionary entrepreneurs <strong>Amit Bajoria</strong> and <strong>Vanita Bajoria</strong>, Amit Hospitality LLP was established with a singular conviction: that exceptional dining is an immersive theatrical art form combining world-class gastronomy, bespoke architecture, and authentic warmth.
            </p>
            <p className="text-sm text-slate-400 leading-relaxed">
              From the towering medieval grandeur of Kolkata's tallest bar at <strong>Lord of the Drinks</strong> to the sunlit rustic elegance of <strong>Veneto Kitchen &amp; Bar</strong>, the lively urban beats of <strong>The Warehouse Cafe</strong>, and the curated luxury spirits of <strong>Deliite</strong>, every property reflects our obsession with quality and community.
            </p>

            <div className="grid grid-cols-2 gap-4 pt-2">
              <div className="p-4 rounded-xl bg-charcoal-950 border border-slate-800">
                <p className="font-serif font-bold text-base text-white">Amit Bajoria</p>
                <p className="text-xs text-gold-400 font-mono mt-0.5">Founder &amp; Managing Partner</p>
              </div>
              <div className="p-4 rounded-xl bg-charcoal-950 border border-slate-800">
                <p className="font-serif font-bold text-base text-white">Vanita Bajoria</p>
                <p className="text-xs text-gold-400 font-mono mt-0.5">Co-Founder &amp; Director</p>
              </div>
            </div>

            <div className="pt-2">
              <Link
                to="/about"
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-charcoal-800 hover:bg-charcoal-700 text-gold-300 border border-gold-400/30 text-xs font-semibold transition"
              >
                <span>Read Full Company Story &amp; Timeline</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>

          <div className="relative rounded-3xl overflow-hidden border border-gold-400/30 shadow-2xl">
            <img
              src="https://images.unsplash.com/photo-1544025162-d76694265947?q=80&w=1200&auto=format&fit=crop"
              alt="Hospitality Culinary Artistry"
              className="w-full h-[460px] object-cover"
              loading="lazy"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-obsidian-950 via-transparent to-transparent" />
            <div className="absolute bottom-6 left-6 right-6 p-6 rounded-2xl bg-charcoal-900/90 border border-slate-700/80 backdrop-blur-md">
              <p className="text-xs font-mono uppercase tracking-widest text-gold-400">Our Credo</p>
              <p className="text-sm font-serif italic text-white mt-1">
                "We do not merely open restaurants; we build sanctuaries where friendships flourish, celebrations become memories, and every guest feels genuinely treasured."
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 4. FEATURED EVENTS & LIVE ENTERTAINMENT */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full space-y-12">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div className="space-y-2">
            <span className="text-xs font-mono font-semibold uppercase tracking-widest text-gold-400">
              Live Cultural Stage
            </span>
            <h2 className="text-3xl sm:text-4xl font-serif font-bold text-white tracking-wide">
              Celebrated Events &amp; Live Performances
            </h2>
            <p className="text-sm text-slate-400 max-w-2xl">
              Amit Hospitality properties host legendary artists, soulful Sufi recitals, and energetic live music gigs in Kolkata.
            </p>
          </div>
          <Link
            to="/events"
            className="inline-flex items-center gap-1.5 text-xs font-bold text-gold-400 hover:text-gold-300 transition shrink-0"
          >
            <span>View All Historical Events</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {VERIFIED_HISTORICAL_EVENTS.slice(0, 3).map((evt) => (
            <div
              key={evt.id}
              className="rounded-2xl bg-charcoal-900 border border-slate-800 hover:border-gold-400/40 overflow-hidden shadow-lg group transition flex flex-col justify-between"
            >
              <div className="relative h-48 overflow-hidden">
                <img
                  src={evt.imageUrl}
                  alt={evt.title}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  loading="lazy"
                />
                <div className="absolute top-3 right-3">
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-semibold uppercase tracking-wider bg-obsidian-950/80 text-gold-400 border border-gold-400/30">
                    {evt.category.replace('_', ' ')}
                  </span>
                </div>
                <div className="absolute bottom-3 left-3">
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-charcoal-900/90 text-slate-300">
                    {evt.dateStr}
                  </span>
                </div>
              </div>
              <div className="p-5 space-y-2 flex-1 flex flex-col justify-between">
                <div>
                  <h4 className="text-base font-serif font-bold text-white group-hover:text-gold-300 transition-colors">
                    {evt.title}
                  </h4>
                  <p className="text-xs text-gold-400 font-mono mt-0.5">{evt.artistOrFeature}</p>
                  <p className="text-xs text-slate-400 mt-2 line-clamp-2">{evt.description}</p>
                </div>
                <p className="text-[11px] text-slate-500 font-mono pt-3 border-t border-slate-800 flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-gold-400" />
                  <span>{evt.venueName}</span>
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 5. GUEST ENQUIRY & AI CONCIERGE CALLOUT */}
      <section className="py-20 bg-gradient-to-br from-charcoal-900 via-obsidian-950 to-charcoal-950 border-t border-slate-800 px-4 sm:px-6 lg:px-8">
        <div className="max-w-5xl mx-auto rounded-3xl p-8 sm:p-12 border border-gold-400/40 shadow-2xl relative overflow-hidden bg-charcoal-900/60 backdrop-blur-xl text-center space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-gold-400/15 border border-gold-400/30 text-gold-400 text-xs font-mono uppercase tracking-widest">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Seamless Hospitality Experience</span>
          </div>

          <h2 className="text-3xl sm:text-5xl font-serif font-bold text-white">
            Plan Your Next Memorable Gathering
          </h2>

          <p className="text-sm sm:text-base text-slate-300 max-w-2xl mx-auto font-light leading-relaxed">
            Whether booking an intimate celebration at Veneto, a high-octane corporate gala at Lord of the Drinks, a live music brunch at Warehouse Cafe, or seeking boutique event catering.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
            <Link
              to="/enquiry"
              className="px-8 py-3.5 rounded-xl bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 font-bold text-sm tracking-wide hover:brightness-110 transition shadow-gold-glow"
            >
              Submit Private Event Enquiry
            </Link>
            <Link
              to="/contact"
              className="px-7 py-3.5 rounded-xl bg-charcoal-800 hover:bg-charcoal-700 text-slate-200 border border-slate-700 text-sm font-semibold transition"
            >
              Contact Directory
            </Link>
          </div>
        </div>
      </section>

      {/* Global Reservation Modal */}
      <ReservationModal
        isOpen={reservationModalOpen}
        onClose={() => setReservationModalOpen(false)}
        defaultOutletId={selectedOutletId}
      />
    </div>
  );
};
