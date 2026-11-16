import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Sparkles,
  MapPin,
  Clock,
  Phone,
  Mail,
  Wine,
  Utensils,
  Calendar,
  ArrowRight,
  Shield,
  Star,
  CheckCircle,
  Search,
} from 'lucide-react';
import { ReservationModal } from '../../components/common/ReservationModal';

export const LordOfDrinksPage: React.FC = () => {
  const [reservationModalOpen, setReservationModalOpen] = useState(false);
  const [activeCategory, setActiveCategory] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const lotdCategories = [
    'ALL',
    'Signature Cocktails & Spirits',
    'Artisanal Dimsums & Tapas',
    'Tandoori & Kebabs',
    'Continental & Pan-Asian Mains',
    'Decadent Desserts',
  ];

  const lotdMenuItems = [
    {
      category: 'Signature Cocktails & Spirits',
      name: 'My 18th Birthday',
      desc: 'Signature LOTD concoction with premium vodka, rich butterscotch liqueur, salted caramel, popcorn syrup, and fresh pineapple juice.',
      price: '₹675',
      dietary: 'VEG',
      signature: true,
    },
    {
      category: 'Signature Cocktails & Spirits',
      name: 'Lavender Sour',
      desc: 'Botanical dry gin, organic lavender blossom tincture, butterfly pea flower tea, fresh lime, and vegan aquafaba foam.',
      price: '₹695',
      dietary: 'VEG',
      signature: true,
    },
    {
      category: 'Signature Cocktails & Spirits',
      name: 'Ghost Bar Smoked Old Fashioned',
      desc: 'Single barrel bourbon, Angostura & orange bitters, charred orange zest, smoked inside an applewood cloche.',
      price: '₹745',
      dietary: 'VEG',
      signature: true,
    },
    {
      category: 'Artisanal Dimsums & Tapas',
      name: 'Truffle Edamame & Cream Cheese Dumpling',
      desc: 'Steamed crystal translucent dumplings with black truffle essence, served with scallion-chili crisp dip.',
      price: '₹575',
      dietary: 'VEG',
      signature: true,
    },
    {
      category: 'Artisanal Dimsums & Tapas',
      name: 'Crispy LOTD Lotus Stem',
      desc: 'Wok-tossed lotus stem crisps with sweet chili honey glaze, toasted sesame, and Sichuan scallions.',
      price: '₹525',
      dietary: 'VEG',
      signature: false,
    },
    {
      category: 'Artisanal Dimsums & Tapas',
      name: 'Chili Mountain Chicken',
      desc: 'Diced chicken tossed with dry red Kashmiri chilies, Sichuan peppercorns, roasted peanuts, and spring onion.',
      price: '₹625',
      dietary: 'NON_VEG',
      signature: true,
    },
    {
      category: 'Tandoori & Kebabs',
      name: 'Bhatthi Ka Murgh Tikka',
      desc: 'Charcoal-grilled tender chicken morsels steeped in mustard oil, roasted cumin, and black cardamom marinade.',
      price: '₹645',
      dietary: 'NON_VEG',
      signature: true,
    },
    {
      category: 'Tandoori & Kebabs',
      name: 'Paneer Angara Tikka',
      desc: 'Fresh cottage cheese stuffed with dry fruit compote, smoked over live charcoal with degi mirch.',
      price: '₹545',
      dietary: 'VEG',
      signature: false,
    },
    {
      category: 'Continental & Pan-Asian Mains',
      name: 'Slow Braised Butter Chicken Kulcha Platter',
      desc: 'Old Delhi recipe butter chicken served with mini zaatar garlic kulchas and pickled onions.',
      price: '₹695',
      dietary: 'NON_VEG',
      signature: true,
    },
    {
      category: 'Continental & Pan-Asian Mains',
      name: 'Wood Fired Wild Mushroom Risotto',
      desc: 'Arborio rice slowly simmered with porcini stock, shaved parmesan, and white truffle glaze.',
      price: '₹675',
      dietary: 'VEG',
      signature: false,
    },
    {
      category: 'Decadent Desserts',
      name: 'LOTD Flaming Sizzling Brownie',
      desc: 'Warm walnut brownie served with vanilla bean ice cream and flamed Dark Rum chocolate sauce tableside.',
      price: '₹425',
      dietary: 'VEG',
      signature: true,
    },
  ];

  const filteredItems = lotdMenuItems.filter((item) => {
    const matchesCat = activeCategory === 'ALL' || item.category === activeCategory;
    const matchesQuery =
      item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.desc.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCat && matchesQuery;
  });

  return (
    <div className="min-h-screen bg-obsidian-950 text-slate-100 font-sans pb-20">
      {/* 1. CINEMATIC HERO */}
      <section className="relative min-h-[75vh] flex items-center justify-center px-4 sm:px-6 lg:px-8 py-20 overflow-hidden">
        <div className="absolute inset-0 z-0">
          <img
            src="/images/brands/lord-of-the-drinks.jpg"
            alt="Lord of the Drinks Kolkata Ghost Bar"
            className="w-full h-full object-cover object-center scale-105"
            onError={(e: any) => {
              e.currentTarget.src = 'https://images.unsplash.com/photo-1572116469696-31de0f17cc34?q=80&w=1600&auto=format&fit=crop';
            }}
            loading="eager"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-obsidian-950 via-obsidian-950/80 to-obsidian-950/50" />
        </div>

        <div className="relative z-10 max-w-4xl mx-auto text-center space-y-5 animate-fade-in">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-charcoal-900/90 border border-gold-400/40 text-gold-300 text-xs font-mono uppercase tracking-widest backdrop-blur-md">
            <Sparkles className="w-3.5 h-3.5 text-gold-400" />
            <span>Introduced December 2019 • Amit Hospitality Group</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-serif font-bold text-white tracking-tight">
            Lord of the Drinks
          </h1>
          <p className="text-sm font-mono text-gold-400 tracking-widest uppercase">
            Kolkata's Tallest Bar &amp; Experiential Nightlife Destination
          </p>

          <p className="text-sm sm:text-base text-slate-300 font-light max-w-2xl mx-auto leading-relaxed">
            Towering across the 4th Floor of South City Mall, LOTD Kolkata transports guests into an opulent medieval European castle world with its iconic Ghost Bar, neon-lit lounges, and progressive global gastronomy.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
            <button
              onClick={() => setReservationModalOpen(true)}
              className="px-7 py-3 rounded-xl bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 font-bold text-xs tracking-wider shadow-gold-glow hover:brightness-110 transition flex items-center gap-2"
            >
              <Calendar className="w-4 h-4" />
              <span>Reserve a Table at LOTD</span>
            </button>
            <Link
              to="/concierge?outlet=lord-of-the-drinks"
              className="px-6 py-3 rounded-xl bg-charcoal-900/90 hover:bg-charcoal-800 text-gold-300 border border-gold-400/40 text-xs font-semibold transition backdrop-blur-md flex items-center gap-2"
            >
              <Sparkles className="w-4 h-4" />
              <span>Ask LOTD AI Concierge</span>
            </Link>
          </div>
        </div>
      </section>

      {/* 2. BRAND PROFILE & GHOST BAR HIGHLIGHT */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
          <div className="lg:col-span-7 space-y-5">
            <span className="text-xs font-mono uppercase tracking-widest text-gold-400 font-semibold">
              The Legend
            </span>
            <h2 className="text-3xl font-serif font-bold text-white leading-tight">
              An Architectural Marvel Overlooking South City
            </h2>
            <p className="text-sm text-slate-300 leading-relaxed font-light">
              Introduced to southern Kolkata in <strong>December 2019</strong> by Amit Hospitality LLP, <strong>Lord of the Drinks (LOTD Kolkata)</strong> redefined the city's nightlife landscape. Built across an expansive 220-seat layout on the 4th Floor of South City Mall, it features dramatic 24-foot vaulted ceilings, stone arches, medieval heraldry, and gothic wrought-iron chandeliers.
            </p>
            <p className="text-sm text-slate-400 leading-relaxed">
              At its center lies the celebrated <strong>Ghost Bar</strong>—an illuminated, backlit alabaster counter where master mixologists craft botanical infusions, smoke-infused single malts, and theatrical cocktails. Whether gathering for daytime corporate luncheons, family celebrations, or weekend nightlife, LOTD promises an unforgettable escapade.
            </p>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-2 text-xs">
              <div className="p-3.5 rounded-xl bg-charcoal-900 border border-slate-800">
                <Clock className="w-4 h-4 text-gold-400 mb-1" />
                <p className="font-semibold text-white">12:00 PM – 12:00 AM</p>
                <p className="text-[10px] text-slate-500">Every Day</p>
              </div>
              <div className="p-3.5 rounded-xl bg-charcoal-900 border border-slate-800">
                <Utensils className="w-4 h-4 text-gold-400 mb-1" />
                <p className="font-semibold text-white">220 Seating Capacity</p>
                <p className="text-[10px] text-slate-500">Main, Lounge &amp; Ghost Bar</p>
              </div>
              <div className="p-3.5 rounded-xl bg-charcoal-900 border border-slate-800">
                <Wine className="w-4 h-4 text-gold-400 mb-1" />
                <p className="font-semibold text-white">Ghost Bar</p>
                <p className="text-[10px] text-slate-500">Progressive Mixology</p>
              </div>
            </div>
          </div>

          <div className="lg:col-span-5 rounded-3xl bg-charcoal-900 border border-gold-400/30 p-6 space-y-5 shadow-2xl">
            <h3 className="text-lg font-serif font-bold text-white flex items-center gap-2">
              <MapPin className="w-4 h-4 text-gold-400" />
              <span>Location &amp; Verified Contacts</span>
            </h3>

            <div className="space-y-3 text-xs text-slate-300">
              <div>
                <p className="text-slate-500 font-mono">Address:</p>
                <p className="font-medium text-white">
                  4th Floor, South City Mall, 375 Prince Anwar Shah Road, Jadavpur, Kolkata - 700068
                </p>
              </div>
              <div>
                <p className="text-slate-500 font-mono">Phone Reservations:</p>
                <p className="font-medium text-gold-300 space-x-2">
                  <a href="tel:+919831568080" className="hover:underline">+91 9831568080</a>
                  <span>•</span>
                  <a href="tel:+919831638080" className="hover:underline">+91 9831638080</a>
                </p>
              </div>
              <div>
                <p className="text-slate-500 font-mono">General Manager Email:</p>
                <p className="font-medium text-white">
                  <a href="mailto:gm@lodkolkata.com" className="text-gold-300 hover:underline">
                    gm@lodkolkata.com
                  </a>
                </p>
              </div>
              <div>
                <p className="text-slate-500 font-mono">Dress Code:</p>
                <p className="text-slate-400">
                  Smart Casual (Collared shirts, tailored attire; no flip-flops or athletic shorts after 7 PM)
                </p>
              </div>
            </div>

            <button
              onClick={() => setReservationModalOpen(true)}
              className="w-full py-2.5 rounded-xl bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 font-bold text-xs hover:brightness-110 transition shadow-gold-glow"
            >
              Request Table at LOTD
            </button>
          </div>
        </div>
      </section>

      {/* 3. DIGITAL CULINARY & COCKTAIL MENU */}
      <section className="py-16 bg-charcoal-900/40 border-t border-slate-800 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto space-y-8">
          <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
            <div>
              <span className="text-xs font-mono uppercase tracking-widest text-gold-400 font-semibold">
                Curated Gastronomy
              </span>
              <h2 className="text-3xl font-serif font-bold text-white mt-1">
                Lord of the Drinks Digital Menu
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Prices and dishes shown represent our demonstration culinary repertoire. Subject to seasonal availability.
              </p>
            </div>

            {/* Search Input */}
            <div className="relative w-full sm:w-64">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search dishes or cocktails..."
                className="w-full pl-9 pr-3 py-2 text-xs rounded-xl bg-charcoal-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-gold-400"
              />
            </div>
          </div>

          {/* Category Filter Pills */}
          <div className="flex flex-wrap gap-2 pb-2">
            {lotdCategories.map((cat) => (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-medium transition ${
                  activeCategory === cat
                    ? 'bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 font-bold shadow-gold-glow'
                    : 'bg-charcoal-900 text-slate-300 border border-slate-800 hover:border-slate-700'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Menu Items Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {filteredItems.map((item, idx) => (
              <div
                key={idx}
                className="p-5 rounded-2xl bg-charcoal-900/90 border border-slate-800 hover:border-gold-400/40 transition flex flex-col justify-between space-y-3"
              >
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <h4 className="font-serif font-bold text-base text-white">
                      {item.name}
                    </h4>
                    <span className="font-mono font-bold text-sm text-gold-400 shrink-0">
                      {item.price}
                    </span>
                  </div>
                  <div className="flex items-center gap-1.5 mt-1">
                    {item.signature && (
                      <span className="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold uppercase bg-gold-400/20 text-gold-300 border border-gold-400/30">
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
        defaultOutletId={8}
        defaultOutletName="Lord of the Drinks"
      />
    </div>
  );
};
