import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Sparkles,
  MapPin,
  Clock,
  Phone,
  Mail,
  ShoppingBag,
  Search,
  CheckCircle,
  Shield,
  ArrowRight,
  Wine,
  GlassWater,
  Package,
  AlertCircle,
} from 'lucide-react';

export const DeliitePage: React.FC = () => {
  const [activeCategory, setActiveCategory] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const deliiteCategories = [
    'ALL',
    'Craft Beers & Ciders',
    'Artisanal Tonics & Mixers',
    'Gourmet Munchies & Snacks',
    'Mineral & Sparkling Water',
  ];

  const deliiteProducts = [
    {
      category: 'Craft Beers & Ciders',
      name: 'Belgian Style Wheat Ale (Demonstration Stock)',
      desc: 'Refreshing wheat ale brewed with ground coriander seeds and Curacao orange peel. 330ml bottle.',
      price: '₹280 (Demo)',
      badge: 'Boutique Selection',
      tag: 'Craft Brew',
    },
    {
      category: 'Craft Beers & Ciders',
      name: 'Hazy Tropical Session IPA (Demonstration Stock)',
      desc: 'Citrus aromatics of passion fruit and grapefruit with velvety soft hop bitterness. 330ml can.',
      price: '₹340 (Demo)',
      badge: 'Craft Can',
      tag: 'Imported Brew',
    },
    {
      category: 'Artisanal Tonics & Mixers',
      name: 'Botanical Elderflower Tonic Water',
      desc: 'Natural quinine infused with hand-picked English elderflower blossoms. Low calorie, crisp effervescence.',
      price: '₹120 (Demo)',
      badge: 'Artisanal Mixer',
      tag: 'Mixology Tonic',
    },
    {
      category: 'Artisanal Tonics & Mixers',
      name: 'Spiced Ginger Ale Reduction',
      desc: 'Real ginger root extract blended with citrus oils and spring water. Perfect pairing for single malts.',
      price: '₹115 (Demo)',
      badge: 'Artisanal Mixer',
      tag: 'Craft Soda',
    },
    {
      category: 'Mineral & Sparkling Water',
      name: 'Himalayan Sparkling Natural Spring Water',
      desc: 'Pure mountain runoff naturally filtered through mineral-rich rock strata. Light natural effervescence.',
      price: '₹110 (Demo)',
      badge: 'Spring Water',
      tag: 'Pure Mineral',
    },
    {
      category: 'Gourmet Munchies & Snacks',
      name: 'Black Truffle & Rosemary Jumbo Cashews',
      desc: 'Slow-roasted Goan cashews tossed in Tuscan black truffle sea salt and garden rosemary sprigs.',
      price: '₹350 (Demo)',
      badge: 'Gourmet Snack',
      tag: 'Artisanal Munchies',
    },
    {
      category: 'Gourmet Munchies & Snacks',
      name: 'Wasabi Roasted Green Pea Crisps',
      desc: 'Crunchy roasted peas coated with authentic Japanese wasabi seasoning. Spicy and addictive.',
      price: '₹180 (Demo)',
      badge: 'Bar Snack',
      tag: 'Crunchy Munchies',
    },
  ];

  const filteredProducts = deliiteProducts.filter((item) => {
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
            src="/images/brands/deliite.jpg"
            alt="Deliite Beverage Boutique Diamond Plaza Mall"
            className="w-full h-full object-cover object-center scale-105"
            onError={(e: any) => {
              e.currentTarget.src = 'https://images.unsplash.com/photo-1527061011665-3652c757a4d4?q=80&w=1600&auto=format&fit=crop';
            }}
            loading="eager"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-obsidian-950 via-obsidian-950/85 to-obsidian-950/50" />
        </div>

        <div className="relative z-10 max-w-4xl mx-auto text-center space-y-5 animate-fade-in">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-charcoal-900/90 border border-purple-400/40 text-purple-300 text-xs font-mono uppercase tracking-widest backdrop-blur-md">
            <ShoppingBag className="w-3.5 h-3.5 text-purple-400" />
            <span>Diamond Plaza Mall • Level 3</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-serif font-bold text-white tracking-tight">
            Deliite
          </h1>
          <p className="text-sm font-mono text-purple-400 tracking-widest uppercase">
            Curated Spirits, Craft Beers, Beverages &amp; Gourmet Munchies
          </p>

          <p className="text-sm sm:text-base text-slate-300 font-light max-w-2xl mx-auto leading-relaxed">
            Kolkata's premier lifestyle beverage boutique on the 3rd Floor of Diamond Plaza Mall, presenting top-shelf domestic and imported spirits, craft brews, boutique mixers, and artisanal bar snacks.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
            <Link
              to="/enquiry?brand=deliite"
              className="px-7 py-3 rounded-xl bg-gradient-to-r from-purple-500 to-purple-600 text-white font-bold text-xs tracking-wider shadow-lg hover:brightness-110 transition flex items-center gap-2"
            >
              <span>Retail &amp; Gifting Enquiry</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              to="/concierge?outlet=deliite"
              className="px-6 py-3 rounded-xl bg-charcoal-900/90 hover:bg-charcoal-800 text-purple-300 border border-purple-400/40 text-xs font-semibold transition backdrop-blur-md flex items-center gap-2"
            >
              <Sparkles className="w-4 h-4" />
              <span>Ask Deliite AI Concierge</span>
            </Link>
          </div>
        </div>
      </section>

      {/* 2. RETAIL INFORMATION & LOCATION */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
          <div className="lg:col-span-7 space-y-5">
            <span className="text-xs font-mono uppercase tracking-widest text-purple-400 font-semibold">
              The Boutique Concept
            </span>
            <h2 className="text-3xl font-serif font-bold text-white leading-tight">
              A Refined Beverage &amp; Lifestyle Showcase
            </h2>
            <p className="text-sm text-slate-300 leading-relaxed font-light">
              <strong>Deliite</strong> offers discerning connoisseurs an elevated retail experience. Located on the 3rd Floor of Diamond Plaza Mall (Jessore Road), our boutique curates high-grade international single malts, botanical gins, sparkling proseccos, craft ales, low-sugar artisanal tonic waters, and gourmet accompaniments.
            </p>
            <p className="text-sm text-slate-400 leading-relaxed">
              Whether curating home bars, choosing gift hampers for celebratory milestones, or picking up premium mixers for dinner parties, our team provides knowledgeable guidance and courteous service.
            </p>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 pt-2 text-xs">
              <div className="p-3.5 rounded-xl bg-charcoal-900 border border-slate-800">
                <Clock className="w-4 h-4 text-purple-400 mb-1" />
                <p className="font-semibold text-white">11:00 AM – 10:00 PM</p>
                <p className="text-[10px] text-slate-500">Every Day</p>
              </div>
              <div className="p-3.5 rounded-xl bg-charcoal-900 border border-slate-800">
                <Package className="w-4 h-4 text-purple-400 mb-1" />
                <p className="font-semibold text-white">Gifting &amp; Hampers</p>
                <p className="text-[10px] text-slate-500">Curated Packaging</p>
              </div>
              <div className="p-3.5 rounded-xl bg-charcoal-900 border border-slate-800">
                <Wine className="w-4 h-4 text-purple-400 mb-1" />
                <p className="font-semibold text-white">In-Store Showcase</p>
                <p className="text-[10px] text-slate-500">Diamond Plaza</p>
              </div>
            </div>
          </div>

          <div className="lg:col-span-5 rounded-3xl bg-charcoal-900 border border-purple-400/30 p-6 space-y-5 shadow-2xl">
            <h3 className="text-lg font-serif font-bold text-white flex items-center gap-2">
              <MapPin className="w-4 h-4 text-purple-400" />
              <span>Store Location &amp; Inquiries</span>
            </h3>

            <div className="space-y-3 text-xs text-slate-300">
              <div>
                <p className="text-slate-500 font-mono">Address:</p>
                <p className="font-medium text-white">
                  3rd Floor, Diamond Plaza Mall, 68 Jessore Road, Kolkata - 700055
                </p>
              </div>
              <div>
                <p className="text-slate-500 font-mono">Corporate Liaison Phone:</p>
                <p className="font-medium text-purple-300">
                  <a href="tel:+919432335967" className="hover:underline">+91 94323 35967</a>
                </p>
              </div>
              <div>
                <p className="text-slate-500 font-mono">Corporate Email:</p>
                <p className="font-medium text-white">
                  <a href="mailto:vanita@amithospitality.com" className="text-purple-300 hover:underline">
                    vanita@amithospitality.com
                  </a>
                </p>
              </div>

              {/* Policy Disclaimer */}
              <div className="p-3 rounded-xl bg-charcoal-950 border border-slate-800 text-[11px] text-slate-400 flex items-start gap-2">
                <AlertCircle className="w-4 h-4 text-purple-400 shrink-0 mt-0.5" />
                <span>
                  <strong>Data &amp; Purchase Policy:</strong> In compliance with excise and consumer laws, product listings represent demonstration inventory. Purchases are conducted in-store at Diamond Plaza Mall.
                </span>
              </div>
            </div>

            <Link
              to="/enquiry?brand=deliite"
              className="block text-center w-full py-2.5 rounded-xl bg-gradient-to-r from-purple-500 to-purple-600 text-white font-bold text-xs hover:brightness-110 transition shadow-lg"
            >
              Send Gifting / Product Enquiry
            </Link>
          </div>
        </div>
      </section>

      {/* 3. PRODUCT CATALOGUE SHOWCASE (DEMO CONTENT) */}
      <section className="py-16 bg-charcoal-900/40 border-t border-slate-800 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto space-y-8">
          <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
            <div>
              <span className="text-xs font-mono uppercase tracking-widest text-purple-400 font-semibold">
                Curated Showcase
              </span>
              <h2 className="text-3xl font-serif font-bold text-white mt-1">
                Boutique Catalogue Highlights
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Demonstration inventory cards. Connect with our store representatives for live availability.
              </p>
            </div>

            <div className="relative w-full sm:w-64">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search beers, mixers, munchies..."
                className="w-full pl-9 pr-3 py-2 text-xs rounded-xl bg-charcoal-950 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-purple-400"
              />
            </div>
          </div>

          <div className="flex flex-wrap gap-2 pb-2">
            {deliiteCategories.map((cat) => (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-medium transition ${
                  activeCategory === cat
                    ? 'bg-gradient-to-r from-purple-500 to-purple-600 text-white font-bold shadow-lg'
                    : 'bg-charcoal-900 text-slate-300 border border-slate-800 hover:border-slate-700'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {filteredProducts.map((item, idx) => (
              <div
                key={idx}
                className="p-5 rounded-2xl bg-charcoal-900/90 border border-slate-800 hover:border-purple-400/40 transition flex flex-col justify-between space-y-3"
              >
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <h4 className="font-serif font-bold text-base text-white">
                      {item.name}
                    </h4>
                    <span className="font-mono font-bold text-sm text-purple-400 shrink-0">
                      {item.price}
                    </span>
                  </div>
                  <div className="flex items-center gap-1.5 mt-1">
                    <span className="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold uppercase bg-purple-400/20 text-purple-300 border border-purple-400/30">
                      {item.badge}
                    </span>
                    <span className="px-1.5 py-0.5 rounded text-[9px] font-mono uppercase bg-charcoal-950 text-slate-400 border border-slate-800">
                      {item.tag}
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
    </div>
  );
};
