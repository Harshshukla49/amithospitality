import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Sparkles,
  MapPin,
  Clock,
  Phone,
  Mail,
  Wine,
  Coffee,
  Utensils,
  Calendar,
  ArrowRight,
  Shield,
  Search,
  CheckCircle,
  AlertTriangle,
  Music,
} from 'lucide-react';
import { ReservationModal } from '../../components/common/ReservationModal';

export const WarehouseCafePage: React.FC = () => {
  const [reservationModalOpen, setReservationModalOpen] = useState(false);
  const [activeCategory, setActiveCategory] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const warehouseCategories = [
    'ALL',
    'Sunday Brunch Buffet',
    'Artisanal Burgers & Handhelds',
    'Global Street Food & Small Plates',
    'Craft Mixology & Shakes',
  ];

  const warehouseMenuItems = [
    {
      category: 'Sunday Brunch Buffet',
      name: 'Sunday Grand Brunch Experience',
      desc: 'All-inclusive buffet spread: fluffy buttermilk pancakes, artisanal eggs made-to-order, deli sandwiches, gourmet salads, fruit platters, and decadent desserts (taxes applicable).',
      price: '₹999 + taxes',
      dietary: 'VEG',
      signature: true,
    },
    {
      category: 'Sunday Brunch Buffet',
      name: 'Brunch Craft Cocktail Add-On',
      desc: 'Free-flowing mimosas, bellinis, and warehouse craft beer flight during Sunday brunch hours (12 PM - 4 PM).',
      price: '₹499 + taxes',
      dietary: 'VEG',
      signature: false,
    },
    {
      category: 'Artisanal Burgers & Handhelds',
      name: 'The Warehouse Truffle Smash Burger',
      desc: 'Double smashed tenderloin patties, sharp cheddar, truffle mushroom compote, toasted brioche bun, house fries.',
      price: '₹625',
      dietary: 'NON_VEG',
      signature: true,
    },
    {
      category: 'Artisanal Burgers & Handhelds',
      name: 'Crispy Panko Katsu Burger',
      desc: 'Crisp panko-crusted cottage cheese steak, spicy sriracha slaw, pickled cucumber, melted gouda.',
      price: '₹545',
      dietary: 'VEG',
      signature: false,
    },
    {
      category: 'Global Street Food & Small Plates',
      name: 'Gochujang Glazed Chicken Wings',
      desc: 'Twice-fried crispy chicken wings tossed in fermented Korean chili glaze, toasted sesame, spring scallions.',
      price: '₹525',
      dietary: 'NON_VEG',
      signature: true,
    },
    {
      category: 'Global Street Food & Small Plates',
      name: 'Avocado & Edamame Crostini',
      desc: 'Smashed Hass avocado, yuzu citrus dressing, edamame beans, toasted artisan sourdough baguette.',
      price: '₹475',
      dietary: 'VEG',
      signature: false,
    },
    {
      category: 'Craft Mixology & Shakes',
      name: 'Smoked Hickory Bourbon Sour',
      desc: 'Kentucky bourbon, charred maple syrup, fresh lemon bitters, flamed citrus peel smoke.',
      price: '₹675',
      dietary: 'VEG',
      signature: true,
    },
    {
      category: 'Craft Mixology & Shakes',
      name: 'Lotus Biscoff Freakshake',
      desc: 'Thick Belgian speculoos biscoff shake, whipped cream, caramel drizzle, crushed butter cookies.',
      price: '₹395',
      dietary: 'VEG',
      signature: false,
    },
  ];

  const filteredItems = warehouseMenuItems.filter((item) => {
    const matchesCat = activeCategory === 'ALL' || item.category === activeCategory;
    const matchesQuery =
      item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.desc.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCat && matchesQuery;
  });

  return (
    <div className="min-h-screen bg-obsidian-950 text-slate-100 font-sans pb-20">
      {/* 1. HERO SECTION */}
      <section className="relative min-h-[70vh] flex items-center justify-center px-4 sm:px-6 lg:px-8 py-20 overflow-hidden">
        <div className="absolute inset-0 z-0">
          <img
            src="/images/brands/warehouse-cafe.jpg"
            alt="The Warehouse Cafe South City Mall Kolkata"
            className="w-full h-full object-cover object-center scale-105"
            onError={(e: any) => {
              e.currentTarget.src = 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?q=80&w=1600&auto=format&fit=crop';
            }}
            loading="eager"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-obsidian-950 via-obsidian-950/80 to-obsidian-950/50" />
        </div>

        <div className="relative z-10 max-w-4xl mx-auto text-center space-y-5 animate-fade-in">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-charcoal-900/90 border border-gold-400/40 text-gold-300 text-xs font-mono uppercase tracking-widest backdrop-blur-md">
            <Sparkles className="w-3.5 h-3.5 text-gold-400" />
            <span>Opened June 2022 • South City Mall</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-serif font-bold text-white tracking-tight">
            The Warehouse Cafe
          </h1>
          <p className="text-sm font-mono text-rose-400 tracking-widest uppercase">
            Urban Industrial Lounge, Live Music &amp; Sunday Brunch
          </p>

          <p className="text-sm sm:text-base text-slate-300 font-light max-w-2xl mx-auto leading-relaxed">
            Unveiled in June 2022 on the 4th Floor of South City Mall, The Warehouse Cafe pairs industrial loft design with chef-created comfort recipes, weekend acoustic sessions, and Kolkata's favorite Sunday brunch.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
            <button
              onClick={() => setReservationModalOpen(true)}
              className="px-7 py-3 rounded-xl bg-gradient-to-r from-rose-500 to-rose-600 text-white font-bold text-xs tracking-wider shadow-lg hover:brightness-110 transition flex items-center gap-2"
            >
              <Calendar className="w-4 h-4" />
              <span>Reserve a Table</span>
            </button>
            <Link
              to="/concierge?outlet=the-warehouse-cafe"
              className="px-6 py-3 rounded-xl bg-charcoal-900/90 hover:bg-charcoal-800 text-rose-300 border border-rose-400/40 text-xs font-semibold transition backdrop-blur-md flex items-center gap-2"
            >
              <Sparkles className="w-4 h-4" />
              <span>Ask Warehouse AI Concierge</span>
            </Link>
          </div>
        </div>
      </section>

      {/* 2. SUNDAY BRUNCH SPECIAL HIGHLIGHT */}
      <section className="py-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="rounded-3xl bg-gradient-to-br from-charcoal-900 via-charcoal-900/90 to-charcoal-950 border border-rose-400/40 p-8 sm:p-10 shadow-2xl relative overflow-hidden">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            <div className="lg:col-span-8 space-y-4">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-500/15 border border-rose-500/30 text-rose-400 text-xs font-mono uppercase tracking-widest">
                <Coffee className="w-3.5 h-3.5" />
                <span>Featured Experience • Every Sunday</span>
              </div>
              <h2 className="text-2xl sm:text-3xl font-serif font-bold text-white">
                The Legendary Sunday Grand Brunch (12 PM – 4 PM)
              </h2>
              <p className="text-sm text-slate-300 leading-relaxed font-light">
                Indulge in our expansive Sunday buffet spread featuring freshly flipped buttermilk pancakes, eggs prepared to your liking, deli sandwiches, seasonal fruit platters, vibrant garden salads, and gourmet desserts for <strong className="text-gold-300">₹999 + applicable taxes</strong>.
              </p>
              <div className="flex flex-wrap items-center gap-4 pt-2 text-xs text-slate-400 font-mono">
                <span className="flex items-center gap-1.5">
                  <Clock className="w-4 h-4 text-gold-400" />
                  12:00 PM to 04:00 PM
                </span>
                <span>•</span>
                <span className="flex items-center gap-1.5">
                  <Wine className="w-4 h-4 text-gold-400" />
                  Cocktail Add-on Available
                </span>
              </div>
              <p className="text-[11px] text-amber-300/80 italic pt-1">
                * Note: Sunday brunch pricing and menu items are preserved from historical website records; availability subject to current outlet confirmation.
              </p>
            </div>
            <div className="lg:col-span-4 flex flex-col items-center justify-center text-center p-6 rounded-2xl bg-charcoal-950/80 border border-slate-800">
              <p className="text-[10px] font-mono uppercase tracking-widest text-slate-400">All-Inclusive Buffet</p>
              <p className="text-4xl font-serif font-bold text-rose-400 mt-1">₹999</p>
              <p className="text-xs text-slate-500 mt-1">+ Applicable Taxes</p>
              <button
                onClick={() => setReservationModalOpen(true)}
                className="mt-4 w-full py-2.5 rounded-xl bg-gradient-to-r from-rose-500 to-rose-600 text-white font-bold text-xs hover:brightness-110 transition shadow-lg"
              >
                Book Sunday Brunch
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* 3. BRAND OVERVIEW & CONTACT DISCREPANCY TRANSPARENCY */}
      <section className="py-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
          <div className="lg:col-span-7 space-y-5">
            <span className="text-xs font-mono uppercase tracking-widest text-rose-400 font-semibold">
              The Warehouse Vibe
            </span>
            <h2 className="text-3xl font-serif font-bold text-white leading-tight">
              Industrial Loft Aesthetics Meets Live Acoustic Rhythms
            </h2>
            <p className="text-sm text-slate-300 leading-relaxed font-light">
              From open-brick exposed walls and leather chesterfields to custom iron piping and warm filament bulb illumination, <strong>The Warehouse Cafe</strong> offers a laid-back daytime cafe atmosphere that effortlessly transitions into a vibrant evening lounge with craft cocktails and live music performances.
            </p>
            <p className="text-sm text-slate-400 leading-relaxed">
              Celebrated acts including Padmashri Usha Uthup, S Factor, and Kaushik Roy Chowdhury have graced our stage, making The Warehouse Cafe Kolkata's beloved venue for live acoustics, college reunions, and social birthdays.
            </p>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-2 text-xs">
              <div className="p-3.5 rounded-xl bg-charcoal-900 border border-slate-800">
                <Clock className="w-4 h-4 text-rose-400 mb-1" />
                <p className="font-semibold text-white">12:00 PM – 12:00 AM</p>
                <p className="text-[10px] text-slate-500">Every Day</p>
              </div>
              <div className="p-3.5 rounded-xl bg-charcoal-900 border border-slate-800">
                <Utensils className="w-4 h-4 text-rose-400 mb-1" />
                <p className="font-semibold text-white">180 Seating Capacity</p>
                <p className="text-[10px] text-slate-500">Loft Lounge &amp; Bar</p>
              </div>
              <div className="p-3.5 rounded-xl bg-charcoal-900 border border-slate-800">
                <Music className="w-4 h-4 text-rose-400 mb-1" />
                <p className="font-semibold text-white">Live Music Stage</p>
                <p className="text-[10px] text-slate-500">Weekend Gigs</p>
              </div>
            </div>
          </div>

          <div className="lg:col-span-5 rounded-3xl bg-charcoal-900 border border-rose-400/30 p-6 space-y-5 shadow-2xl">
            <h3 className="text-lg font-serif font-bold text-white flex items-center gap-2">
              <MapPin className="w-4 h-4 text-rose-400" />
              <span>Location &amp; Contact Records</span>
            </h3>

            <div className="space-y-3 text-xs text-slate-300">
              <div>
                <p className="text-slate-500 font-mono">Address:</p>
                <p className="font-medium text-white">
                  4th Floor, South City Mall, 375 Prince Anwar Shah Road, Kolkata - 700068
                </p>
              </div>
              <div>
                <p className="text-slate-500 font-mono">Primary Phone Contacts:</p>
                <p className="font-medium text-rose-300 space-x-2">
                  <a href="tel:+919830434580" className="hover:underline">+91 9830434580</a>
                  <span>•</span>
                  <a href="tel:+919836196969" className="hover:underline">+91 9836196969</a>
                </p>
              </div>
              {/* Flagged Contact Notice */}
              <div className="p-3 rounded-xl bg-charcoal-950 border border-slate-800 text-[11px] text-slate-400 space-y-1">
                <div className="flex items-center gap-1.5 text-amber-400 font-semibold">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  <span>Admin Verification Notice:</span>
                </div>
                <p>
                  Historical listing also referenced alternate number <code className="text-slate-300">+91 9830434680</code>. Maintained transparently without destructive data modification.
                </p>
              </div>
              <div>
                <p className="text-slate-500 font-mono">Management Email:</p>
                <p className="font-medium text-white">
                  <a href="mailto:gm.warehouse@amithospitality.com" className="text-rose-300 hover:underline">
                    gm.warehouse@amithospitality.com
                  </a>
                </p>
              </div>
            </div>

            <button
              onClick={() => setReservationModalOpen(true)}
              className="w-full py-2.5 rounded-xl bg-gradient-to-r from-rose-500 to-rose-600 text-white font-bold text-xs hover:brightness-110 transition shadow-lg"
            >
              Request Table at The Warehouse Cafe
            </button>
          </div>
        </div>
      </section>

      {/* 4. DIGITAL MENU */}
      <section className="py-16 bg-charcoal-900/40 border-t border-slate-800 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto space-y-8">
          <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
            <div>
              <span className="text-xs font-mono uppercase tracking-widest text-rose-400 font-semibold">
                Comfort Food &amp; Mixology
              </span>
              <h2 className="text-3xl font-serif font-bold text-white mt-1">
                The Warehouse Cafe Menu
              </h2>
            </div>

            <div className="relative w-full sm:w-64">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search brunch, burgers..."
                className="w-full pl-9 pr-3 py-2 text-xs rounded-xl bg-charcoal-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-rose-400"
              />
            </div>
          </div>

          <div className="flex flex-wrap gap-2 pb-2">
            {warehouseCategories.map((cat) => (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-medium transition ${
                  activeCategory === cat
                    ? 'bg-gradient-to-r from-rose-500 to-rose-600 text-white font-bold shadow-lg'
                    : 'bg-charcoal-900 text-slate-300 border border-slate-800 hover:border-slate-700'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {filteredItems.map((item, idx) => (
              <div
                key={idx}
                className="p-5 rounded-2xl bg-charcoal-900/90 border border-slate-800 hover:border-rose-400/40 transition flex flex-col justify-between space-y-3"
              >
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <h4 className="font-serif font-bold text-base text-white">
                      {item.name}
                    </h4>
                    <span className="font-mono font-bold text-sm text-rose-400 shrink-0">
                      {item.price}
                    </span>
                  </div>
                  <div className="flex items-center gap-1.5 mt-1">
                    {item.signature && (
                      <span className="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold uppercase bg-rose-400/20 text-rose-300 border border-rose-400/30">
                        Signature
                      </span>
                    )}
                    <span
                      className={`px-1.5 py-0.5 rounded text-[9px] font-mono uppercase ${
                        item.dietary === 'VEG'
                          ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                          : 'bg-rose-950 text-rose-300 border border-rose-800'
                      }`}
                    >
                      {item.dietary}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                    {item.desc}
                  </p>
                </div>
                <p className="text-[10px] font-mono text-slate-500 uppercase tracking-wide">
                  {item.category}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Reservation Modal Trigger */}
      <ReservationModal
        isOpen={reservationModalOpen}
        onClose={() => setReservationModalOpen(false)}
        defaultOutletId={10}
        defaultOutletName="The Warehouse Cafe"
      />
    </div>
  );
};
