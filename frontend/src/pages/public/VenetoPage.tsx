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
  Search,
  CheckCircle,
} from 'lucide-react';
import { ReservationModal } from '../../components/common/ReservationModal';

export const VenetoPage: React.FC = () => {
  const [reservationModalOpen, setReservationModalOpen] = useState(false);
  const [activeCategory, setActiveCategory] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const venetoCategories = [
    'ALL',
    'Artisanal Neapolitan Pizzas',
    'Hand-Rolled Fresh Pasta',
    'Mediterranean Antipasti',
    'Handcrafted Cocktails',
  ];

  const venetoMenuItems = [
    {
      category: 'Artisanal Neapolitan Pizzas',
      name: 'Burrata & San Marzano Margherita',
      desc: '24-hour fermented dough, San Marzano D.O.P. tomato sauce, fresh creamy burrata, basil olive oil (Demo menu item).',
      price: '₹795',
      dietary: 'VEG',
      signature: true,
    },
    {
      category: 'Artisanal Neapolitan Pizzas',
      name: 'Tartufo Funghi & Smoked Scamorza',
      desc: 'Wild porcini, cremini mushrooms, white truffle oil, smoked scamorza cheese, micro arugula.',
      price: '₹895',
      dietary: 'VEG',
      signature: true,
    },
    {
      category: 'Artisanal Neapolitan Pizzas',
      name: 'Prosciutto di Parma & Shaved Parmesan',
      desc: 'San Marzano base, aged prosciutto crudo, fresh baby rocket, 24-month Parmigiano Reggiano.',
      price: '₹995',
      dietary: 'NON_VEG',
      signature: false,
    },
    {
      category: 'Hand-Rolled Fresh Pasta',
      name: 'Handmade Spinach & Ricotta Ravioli',
      desc: 'Brown butter sauce, crispy garden sage, toasted pine nuts, aged parmesan fonduta.',
      price: '₹745',
      dietary: 'VEG',
      signature: true,
    },
    {
      category: 'Hand-Rolled Fresh Pasta',
      name: 'Slow-Braised Lamb Ragu Tagliatelle',
      desc: 'Eight-hour simmered lamb shoulder, fresh egg tagliatelle ribbons, fresh rosemary gremolata.',
      price: '₹845',
      dietary: 'NON_VEG',
      signature: true,
    },
    {
      category: 'Hand-Rolled Fresh Pasta',
      name: 'Classic Spaghetti Aglio Olio e Peperoncino',
      desc: 'Tuscan extra virgin olive oil, confit garlic cloves, peperoncino chili flakes, Italian flat-leaf parsley.',
      price: '₹625',
      dietary: 'VEG',
      signature: false,
    },
    {
      category: 'Mediterranean Antipasti',
      name: 'Truffle Arancini al Forno',
      desc: 'Crispy arborio rice croquettes, molten fontina cheese center, black truffle aioli dip.',
      price: '₹545',
      dietary: 'VEG',
      signature: false,
    },
    {
      category: 'Mediterranean Antipasti',
      name: 'Gamberi al Limone e Aglio',
      desc: 'Sautéed butterflied tiger prawns, Amalfi lemon reduction, roasted garlic, grilled sourdough ciabatta.',
      price: '₹725',
      dietary: 'NON_VEG',
      signature: true,
    },
    {
      category: 'Handcrafted Cocktails',
      name: 'Veneto Smoked Negroni',
      desc: 'Botanical gin, Campari, artisanal sweet vermouth, smoked tableside with applewood essence.',
      price: '₹695',
      dietary: 'VEG',
      signature: true,
    },
    {
      category: 'Handcrafted Cocktails',
      name: 'Amalfi Spritz Royale',
      desc: 'Limoncello di Capri, wild elderflower liqueur, prosecco, fresh garden mint spritz.',
      price: '₹645',
      dietary: 'VEG',
      signature: false,
    },
  ];

  const filteredItems = venetoMenuItems.filter((item) => {
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
            src="/images/brands/veneto.jpg"
            alt="Veneto Kitchen & Bar South City Mall"
            className="w-full h-full object-cover object-center scale-105"
            onError={(e: any) => {
              e.currentTarget.src = 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?q=80&w=1600&auto=format&fit=crop';
            }}
            loading="eager"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-obsidian-950 via-obsidian-950/80 to-obsidian-950/50" />
        </div>

        <div className="relative z-10 max-w-4xl mx-auto text-center space-y-5 animate-fade-in">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-charcoal-900/90 border border-gold-400/40 text-gold-300 text-xs font-mono uppercase tracking-widest backdrop-blur-md">
            <Sparkles className="w-3.5 h-3.5 text-gold-400" />
            <span>Amit Hospitality Group • South City Mall</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-serif font-bold text-white tracking-tight">
            Veneto Kitchen &amp; Bar
          </h1>
          <p className="text-sm font-mono text-emerald-400 tracking-widest uppercase">
            Artisanal Italian Gastronomy &amp; Cocktail Bar
          </p>

          <p className="text-sm sm:text-base text-slate-300 font-light max-w-2xl mx-auto leading-relaxed">
            Located on the 4th Floor of South City Mall, Veneto celebrates authentic Italian dining, wood-fired craftsmanship, hand-rolled pastas, and Mediterranean hospitality in an elegant contemporary setting.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
            <button
              onClick={() => setReservationModalOpen(true)}
              className="px-7 py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-emerald-600 text-obsidian-950 font-bold text-xs tracking-wider shadow-lg hover:brightness-110 transition flex items-center gap-2"
            >
              <Calendar className="w-4 h-4" />
              <span>Reserve a Table at Veneto</span>
            </button>
            <Link
              to="/concierge?outlet=veneto"
              className="px-6 py-3 rounded-xl bg-charcoal-900/90 hover:bg-charcoal-800 text-emerald-300 border border-emerald-400/40 text-xs font-semibold transition backdrop-blur-md flex items-center gap-2"
            >
              <Sparkles className="w-4 h-4" />
              <span>Ask Veneto AI Concierge</span>
            </Link>
          </div>
        </div>
      </section>

      {/* 2. BRAND PROFILE & VERIFIED DETAILS */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
          <div className="lg:col-span-7 space-y-5">
            <span className="text-xs font-mono uppercase tracking-widest text-emerald-400 font-semibold">
              The Dining Experience
            </span>
            <h2 className="text-3xl font-serif font-bold text-white leading-tight">
              Wood-Fired Flavors &amp; Mediterranean Warmth
            </h2>
            <p className="text-sm text-slate-300 leading-relaxed font-light">
              <strong>Veneto Kitchen and Bar</strong> is Amit Hospitality's tribute to Italian culinary passion. Featuring a vibrant open kitchen, custom wood-stone pizza ovens, and a curated cocktail bar, Veneto invites guests on a gastronomic voyage across Italy and the sun-drenched Mediterranean coast.
            </p>
            <p className="text-sm text-slate-400 leading-relaxed">
              Every dish is thoughtfully prepared with high-grade flours, artisanal cheeses, extra virgin olive oils, and seasonal regional produce. Paired with Italian spritzes and smoked barrel cocktails, Veneto is Kolkata's favored sanctuary for date nights, relaxed family lunches, and sophisticated social gatherings.
            </p>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-2 text-xs">
              <div className="p-3.5 rounded-xl bg-charcoal-900 border border-slate-800">
                <Clock className="w-4 h-4 text-emerald-400 mb-1" />
                <p className="font-semibold text-white">12:00 PM – 11:30 PM</p>
                <p className="text-[10px] text-slate-500">Every Day</p>
              </div>
              <div className="p-3.5 rounded-xl bg-charcoal-900 border border-slate-800">
                <Utensils className="w-4 h-4 text-emerald-400 mb-1" />
                <p className="font-semibold text-white">120 Seating Capacity</p>
                <p className="text-[10px] text-slate-500">Dining &amp; Bar</p>
              </div>
              <div className="p-3.5 rounded-xl bg-charcoal-900 border border-slate-800">
                <Wine className="w-4 h-4 text-emerald-400 mb-1" />
                <p className="font-semibold text-white">Wood-Stone Oven</p>
                <p className="text-[10px] text-slate-500">Neapolitan Artisan</p>
              </div>
            </div>
          </div>

          <div className="lg:col-span-5 rounded-3xl bg-charcoal-900 border border-emerald-400/30 p-6 space-y-5 shadow-2xl">
            <h3 className="text-lg font-serif font-bold text-white flex items-center gap-2">
              <MapPin className="w-4 h-4 text-emerald-400" />
              <span>Location &amp; Verified Contacts</span>
            </h3>

            <div className="space-y-3 text-xs text-slate-300">
              <div>
                <p className="text-slate-500 font-mono">Address:</p>
                <p className="font-medium text-white">
                  4th Floor, South City Mall, 375 Prince Anwar Shah Road, Kolkata - 700068
                </p>
              </div>
              <div>
                <p className="text-slate-500 font-mono">Phone Reservations:</p>
                <p className="font-medium text-emerald-300 space-x-2">
                  <a href="tel:+919831939515" className="hover:underline">+91 9831939515</a>
                  <span>•</span>
                  <a href="tel:+918777368681" className="hover:underline">+91 8777368681</a>
                </p>
              </div>
              <div>
                <p className="text-slate-500 font-mono">Management Email:</p>
                <p className="font-medium text-white">
                  <a href="mailto:gm.veneto@amithospitality.com" className="text-emerald-300 hover:underline">
                    gm.veneto@amithospitality.com
                  </a>
                </p>
              </div>
              <div>
                <p className="text-slate-500 font-mono">Dress Code:</p>
                <p className="text-slate-400">Smart Casual</p>
              </div>
            </div>

            <button
              onClick={() => setReservationModalOpen(true)}
              className="w-full py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-emerald-600 text-obsidian-950 font-bold text-xs hover:brightness-110 transition shadow-lg"
            >
              Request Table at Veneto
            </button>
          </div>
        </div>
      </section>

      {/* 3. DIGITAL MENU DEMONSTRATION */}
      <section className="py-16 bg-charcoal-900/40 border-t border-slate-800 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto space-y-8">
          <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
            <div>
              <span className="text-xs font-mono uppercase tracking-widest text-emerald-400 font-semibold">
                Culinary Repertoire
              </span>
              <h2 className="text-3xl font-serif font-bold text-white mt-1">
                Veneto Kitchen &amp; Bar Menu
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Demonstration culinary items. Actual seasonal offerings and prices subject to daily chef curation.
              </p>
            </div>

            <div className="relative w-full sm:w-64">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search pizzas or pastas..."
                className="w-full pl-9 pr-3 py-2 text-xs rounded-xl bg-charcoal-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-emerald-400"
              />
            </div>
          </div>

          <div className="flex flex-wrap gap-2 pb-2">
            {venetoCategories.map((cat) => (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-medium transition ${
                  activeCategory === cat
                    ? 'bg-gradient-to-r from-emerald-500 to-emerald-600 text-obsidian-950 font-bold shadow-lg'
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
                className="p-5 rounded-2xl bg-charcoal-900/90 border border-slate-800 hover:border-emerald-400/40 transition flex flex-col justify-between space-y-3"
              >
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <h4 className="font-serif font-bold text-base text-white">
                      {item.name}
                    </h4>
                    <span className="font-mono font-bold text-sm text-emerald-400 shrink-0">
                      {item.price}
                    </span>
                  </div>
                  <div className="flex items-center gap-1.5 mt-1">
                    {item.signature && (
                      <span className="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold uppercase bg-emerald-400/20 text-emerald-300 border border-emerald-400/30">
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
        defaultOutletId={9}
        defaultOutletName="Veneto Kitchen & Bar"
      />
    </div>
  );
};
