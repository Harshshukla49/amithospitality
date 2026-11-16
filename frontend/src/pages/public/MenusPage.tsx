import React, { useState } from 'react';
import {
  Sparkles,
  Search,
  Filter,
  Wine,
  Utensils,
  Coffee,
  ShoppingBag,
  Calendar,
  CheckCircle,
} from 'lucide-react';
import { ReservationModal } from '../../components/common/ReservationModal';

export const MenusPage: React.FC = () => {
  const [selectedBrandSlug, setSelectedBrandSlug] = useState('lord-of-the-drinks');
  const [activeCategory, setActiveCategory] = useState('ALL');
  const [dietaryFilter, setDietaryFilter] = useState<'ALL' | 'VEG' | 'NON_VEG'>('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [reservationModalOpen, setReservationModalOpen] = useState(false);

  const brandOptions = [
    {
      id: 8,
      slug: 'lord-of-the-drinks',
      name: 'Lord of the Drinks',
      sub: 'Kolkata’s Tallest Bar & Progressive Dining',
      icon: Wine,
      color: 'text-amber-400',
    },
    {
      id: 9,
      slug: 'veneto',
      name: 'Veneto Kitchen & Bar',
      sub: 'Wood-Fired Neapolitan Pizzas & Artisanal Pasta',
      icon: Utensils,
      color: 'text-emerald-400',
    },
    {
      id: 10,
      slug: 'the-warehouse-cafe',
      name: 'The Warehouse Cafe',
      sub: 'Industrial Comfort Food & Legendary Sunday Brunch',
      icon: Coffee,
      color: 'text-rose-400',
    },
    {
      id: 11,
      slug: 'deliite',
      name: 'Deliite Lifestyle Retail',
      sub: 'Curated Craft Beers, Spirits & Bar Munchies',
      icon: ShoppingBag,
      color: 'text-purple-400',
    },
  ];

  // Curated Multi-Brand Culinary Catalog
  const allMenuItems = [
    // Lord of the Drinks
    {
      brandSlug: 'lord-of-the-drinks',
      category: 'Signature Cocktails',
      name: 'My 18th Birthday',
      desc: 'Signature LOTD concoction with premium vodka, rich butterscotch liqueur, salted caramel, popcorn syrup, and fresh pineapple juice.',
      price: '₹675',
      dietary: 'VEG',
      signature: true,
    },
    {
      brandSlug: 'lord-of-the-drinks',
      category: 'Signature Cocktails',
      name: 'Lavender Sour',
      desc: 'Botanical dry gin, organic lavender blossom tincture, butterfly pea flower tea, fresh lime, and vegan aquafaba foam.',
      price: '₹695',
      dietary: 'VEG',
      signature: true,
    },
    {
      brandSlug: 'lord-of-the-drinks',
      category: 'Signature Cocktails',
      name: 'Ghost Bar Smoked Old Fashioned',
      desc: 'Single barrel bourbon, Angostura & orange bitters, charred orange zest, smoked inside an applewood cloche.',
      price: '₹745',
      dietary: 'VEG',
      signature: true,
    },
    {
      brandSlug: 'lord-of-the-drinks',
      category: 'Small Plates & Dimsums',
      name: 'Truffle Edamame & Cream Cheese Dumpling',
      desc: 'Steamed crystal translucent dumplings with black truffle essence, served with scallion-chili crisp dip.',
      price: '₹575',
      dietary: 'VEG',
      signature: true,
    },
    {
      brandSlug: 'lord-of-the-drinks',
      category: 'Small Plates & Dimsums',
      name: 'Chili Mountain Chicken',
      desc: 'Diced chicken tossed with dry red Kashmiri chilies, Sichuan peppercorns, roasted peanuts, and spring onion.',
      price: '₹625',
      dietary: 'NON_VEG',
      signature: true,
    },
    {
      brandSlug: 'lord-of-the-drinks',
      category: 'Tandoor & Grills',
      name: 'Bhatthi Ka Murgh Tikka',
      desc: 'Charcoal-grilled tender chicken morsels steeped in mustard oil, roasted cumin, and black cardamom marinade.',
      price: '₹645',
      dietary: 'NON_VEG',
      signature: true,
    },
    {
      brandSlug: 'lord-of-the-drinks',
      category: 'Mains & Curries',
      name: 'Slow Braised Butter Chicken Kulcha Platter',
      desc: 'Old Delhi recipe butter chicken served with mini zaatar garlic kulchas and pickled onions.',
      price: '₹695',
      dietary: 'NON_VEG',
      signature: true,
    },

    // Veneto Kitchen & Bar
    {
      brandSlug: 'veneto',
      category: 'Artisanal Pizzas',
      name: 'Burrata & San Marzano Margherita',
      desc: '24-hour fermented dough, San Marzano D.O.P. tomato sauce, fresh creamy burrata, basil olive oil.',
      price: '₹795',
      dietary: 'VEG',
      signature: true,
    },
    {
      brandSlug: 'veneto',
      category: 'Artisanal Pizzas',
      name: 'Tartufo Funghi & Smoked Scamorza',
      desc: 'Wild porcini, cremini mushrooms, white truffle oil, smoked scamorza cheese, micro arugula.',
      price: '₹895',
      dietary: 'VEG',
      signature: true,
    },
    {
      brandSlug: 'veneto',
      category: 'Fresh Pastas',
      name: 'Handmade Spinach & Ricotta Ravioli',
      desc: 'Brown butter sauce, crispy garden sage, toasted pine nuts, aged parmesan fonduta.',
      price: '₹745',
      dietary: 'VEG',
      signature: true,
    },
    {
      brandSlug: 'veneto',
      category: 'Fresh Pastas',
      name: 'Slow-Braised Lamb Ragu Tagliatelle',
      desc: 'Eight-hour simmered lamb shoulder, fresh egg tagliatelle ribbons, fresh rosemary gremolata.',
      price: '₹845',
      dietary: 'NON_VEG',
      signature: true,
    },
    {
      brandSlug: 'veneto',
      category: 'Italian Cocktails',
      name: 'Veneto Smoked Negroni',
      desc: 'Botanical gin, Campari, artisanal sweet vermouth, smoked tableside with applewood essence.',
      price: '₹695',
      dietary: 'VEG',
      signature: true,
    },

    // The Warehouse Cafe
    {
      brandSlug: 'the-warehouse-cafe',
      category: 'Sunday Brunch Buffet',
      name: 'Sunday Grand Brunch Experience',
      desc: 'All-inclusive buffet: buttermilk pancakes, made-to-order eggs, deli sandwiches, salads, fruit platters, and desserts.',
      price: '₹999 + taxes',
      dietary: 'VEG',
      signature: true,
    },
    {
      brandSlug: 'the-warehouse-cafe',
      category: 'Burgers & Handhelds',
      name: 'The Warehouse Truffle Smash Burger',
      desc: 'Double smashed tenderloin patties, sharp cheddar, truffle mushroom compote, toasted brioche bun, house fries.',
      price: '₹625',
      dietary: 'NON_VEG',
      signature: true,
    },
    {
      brandSlug: 'the-warehouse-cafe',
      category: 'Global Street Food',
      name: 'Gochujang Glazed Chicken Wings',
      desc: 'Twice-fried crispy chicken wings tossed in fermented Korean chili glaze, toasted sesame, spring scallions.',
      price: '₹525',
      dietary: 'NON_VEG',
      signature: true,
    },
    {
      brandSlug: 'the-warehouse-cafe',
      category: 'Craft Mixology',
      name: 'Smoked Hickory Bourbon Sour',
      desc: 'Kentucky bourbon, charred maple syrup, fresh lemon bitters, flamed citrus peel smoke.',
      price: '₹675',
      dietary: 'VEG',
      signature: true,
    },

    // Deliite
    {
      brandSlug: 'deliite',
      category: 'Craft Beers',
      name: 'Belgian Style Wheat Ale',
      desc: 'Refreshing wheat ale brewed with coriander seeds and Curacao orange peel (Retail demo).',
      price: '₹280 (Demo)',
      dietary: 'VEG',
      signature: true,
    },
    {
      brandSlug: 'deliite',
      category: 'Mixers & Tonics',
      name: 'Botanical Elderflower Tonic Water',
      desc: 'Natural quinine infused with hand-picked English elderflower blossoms. Low calorie.',
      price: '₹120 (Demo)',
      dietary: 'VEG',
      signature: true,
    },
    {
      brandSlug: 'deliite',
      category: 'Gourmet Munchies',
      name: 'Black Truffle & Rosemary Cashews',
      desc: 'Slow-roasted jumbo Goan cashews tossed in Tuscan black truffle sea salt and rosemary.',
      price: '₹350 (Demo)',
      dietary: 'VEG',
      signature: true,
    },
  ];

  // Derive categories for selected brand
  const currentBrandItems = allMenuItems.filter((item) => item.brandSlug === selectedBrandSlug);
  const categoriesList = ['ALL', ...Array.from(new Set(currentBrandItems.map((i) => i.category)))];

  const filteredItems = currentBrandItems.filter((item) => {
    const matchesCat = activeCategory === 'ALL' || item.category === activeCategory;
    const matchesDiet =
      dietaryFilter === 'ALL' || item.dietary === dietaryFilter;
    const matchesQuery =
      item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.desc.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCat && matchesDiet && matchesQuery;
  });

  const activeBrand = brandOptions.find((b) => b.slug === selectedBrandSlug) || brandOptions[0];

  return (
    <div className="min-h-screen bg-obsidian-950 text-slate-100 font-sans pb-24">
      {/* 1. HERO HEADER */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 border-b border-slate-800 bg-gradient-to-b from-charcoal-900 via-obsidian-950 to-obsidian-950">
        <div className="max-w-4xl mx-auto text-center space-y-4">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-charcoal-900 border border-gold-400/40 text-gold-300 text-xs font-mono uppercase tracking-widest">
            <Utensils className="w-3.5 h-3.5 text-gold-400" />
            <span>Digital Menus • Culinary &amp; Mixology Catalog</span>
          </div>
          <h1 className="text-4xl sm:text-5xl font-serif font-bold text-white tracking-tight">
            Curated Culinary Creations
          </h1>
          <p className="text-sm sm:text-base text-slate-300 font-light max-w-2xl mx-auto leading-relaxed">
            Browse live digital menus, signature cocktails, and seasonal dishes across all Amit Hospitality brands.
          </p>
        </div>
      </section>

      {/* 2. BRAND SELECTOR STRIP */}
      <section className="py-6 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {brandOptions.map((brand) => {
            const Icon = brand.icon;
            const isSelected = selectedBrandSlug === brand.slug;
            return (
              <button
                key={brand.slug}
                onClick={() => {
                  setSelectedBrandSlug(brand.slug);
                  setActiveCategory('ALL');
                }}
                className={`p-4 rounded-2xl border text-left transition flex items-start gap-3 ${
                  isSelected
                    ? 'bg-charcoal-800 border-gold-400 shadow-gold-glow/20'
                    : 'bg-charcoal-900/60 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className={`p-2 rounded-xl bg-charcoal-950 border border-slate-800 ${brand.color} shrink-0`}>
                  <Icon className="w-4 h-4" />
                </div>
                <div className="overflow-hidden">
                  <p className={`font-serif font-bold text-xs truncate ${isSelected ? 'text-gold-300' : 'text-white'}`}>
                    {brand.name}
                  </p>
                  <p className="text-[11px] text-slate-400 truncate mt-0.5">{brand.sub}</p>
                </div>
              </button>
            );
          })}
        </div>
      </section>

      {/* 3. CONTROLS: CATEGORIES & SEARCH */}
      <section className="py-4 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-4 rounded-2xl bg-charcoal-900 border border-slate-800">
          {/* Dietary Filter */}
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono uppercase text-slate-400">Dietary:</span>
            <button
              onClick={() => setDietaryFilter('ALL')}
              className={`px-3 py-1 rounded-lg text-xs font-mono ${
                dietaryFilter === 'ALL'
                  ? 'bg-charcoal-800 text-white border border-slate-700'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setDietaryFilter('VEG')}
              className={`px-3 py-1 rounded-lg text-xs font-mono ${
                dietaryFilter === 'VEG'
                  ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                  : 'text-slate-400 hover:text-emerald-400'
              }`}
            >
              Vegetarian
            </button>
            <button
              onClick={() => setDietaryFilter('NON_VEG')}
              className={`px-3 py-1 rounded-lg text-xs font-mono ${
                dietaryFilter === 'NON_VEG'
                  ? 'bg-rose-950 text-rose-300 border border-rose-800'
                  : 'text-slate-400 hover:text-rose-400'
              }`}
            >
              Non-Veg
            </button>
          </div>

          {/* Search Field */}
          <div className="relative w-full md:w-72">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search dishes or drinks..."
              className="w-full pl-9 pr-3 py-2 text-xs rounded-xl bg-charcoal-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-gold-400"
            />
          </div>
        </div>

        {/* Categories Strip */}
        <div className="flex flex-wrap gap-2 pb-2">
          {categoriesList.map((cat) => (
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
      </section>

      {/* 4. DISHES & COCKTAILS GRID */}
      <section className="px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto pt-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredItems.map((item, idx) => (
            <div
              key={idx}
              className="p-6 rounded-2xl bg-charcoal-900 border border-slate-800 hover:border-gold-400/40 transition flex flex-col justify-between space-y-4 shadow-lg group"
            >
              <div>
                <div className="flex items-start justify-between gap-2">
                  <h3 className="font-serif font-bold text-lg text-white group-hover:text-gold-200 transition-colors">
                    {item.name}
                  </h3>
                  <span className="font-mono font-bold text-sm text-gold-400 shrink-0">
                    {item.price}
                  </span>
                </div>
                <div className="flex items-center gap-1.5 mt-1.5">
                  {item.signature && (
                    <span className="px-2 py-0.5 rounded text-[9px] font-mono font-bold uppercase bg-gold-400/20 text-gold-300 border border-gold-400/30">
                      Signature
                    </span>
                  )}
                  <span
                    className={`px-2 py-0.5 rounded text-[9px] font-mono uppercase ${
                      item.dietary === 'VEG'
                        ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                        : 'bg-rose-950 text-rose-300 border border-rose-800'
                    }`}
                  >
                    {item.dietary}
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-2.5 leading-relaxed">
                  {item.desc}
                </p>
              </div>

              <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
                <span className="text-[10px] font-mono uppercase text-slate-500">
                  {item.category}
                </span>
                <button
                  onClick={() => setReservationModalOpen(true)}
                  className="text-xs font-semibold text-gold-400 hover:text-gold-300 transition"
                >
                  Book Table &rarr;
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Reservation Modal Trigger */}
      <ReservationModal
        isOpen={reservationModalOpen}
        onClose={() => setReservationModalOpen(false)}
        defaultOutletId={activeBrand.id}
        defaultOutletName={activeBrand.name}
      />
    </div>
  );
};
