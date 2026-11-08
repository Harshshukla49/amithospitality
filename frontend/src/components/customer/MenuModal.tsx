import React, { useState } from 'react';
import {
  X,
  Sparkles,
  Utensils,
  Calendar,
  Clock,
  MapPin,
  Shield,
  Leaf,
  Flame,
  MessageSquare,
} from 'lucide-react';
import { Outlet, MenuItem, DietaryFlag } from '../../types';
import { DEMO_MENU_ITEMS } from '../../utils/mockData';

interface MenuModalProps {
  isOpen: boolean;
  onClose: () => void;
  outlet: Outlet;
  onBookTable: (outlet: Outlet) => void;
  onAskConcierge: (query: string) => void;
}

export const MenuModal: React.FC<MenuModalProps> = ({
  isOpen,
  onClose,
  outlet,
  onBookTable,
  onAskConcierge,
}) => {
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [dietaryFilter, setDietaryFilter] = useState<string>('ALL');

  if (!isOpen) return null;

  // Filter items for this outlet
  const outletItems: MenuItem[] = DEMO_MENU_ITEMS.filter(
    (item) => item.outletId === outlet.id
  );

  // Extract unique categories
  const categories = ['ALL', ...Array.from(new Set(outletItems.map((i) => i.categoryName)))];

  // Apply filters
  const filteredItems = outletItems.filter((item) => {
    const matchesCategory =
      selectedCategory === 'ALL' || item.categoryName === selectedCategory;
    const matchesDiet =
      dietaryFilter === 'ALL' ||
      item.dietaryFlags.includes(dietaryFilter as DietaryFlag);
    return matchesCategory && matchesDiet;
  });

  const getDietaryBadge = (flag: DietaryFlag) => {
    switch (flag) {
      case 'VEG':
        return (
          <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            VEG
          </span>
        );
      case 'VEGAN':
        return (
          <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold bg-teal-500/15 text-teal-300 border border-teal-500/30">
            <Leaf className="w-2.5 h-2.5 text-teal-400" />
            VEGAN
          </span>
        );
      case 'NON_VEG':
        return (
          <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold bg-rose-500/15 text-rose-400 border border-rose-500/30">
            <span className="w-1.5 h-1.5 rounded-full bg-rose-400" />
            NON-VEG
          </span>
        );
      case 'JAIN':
        return (
          <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold bg-amber-500/15 text-amber-300 border border-amber-500/30">
            JAIN
          </span>
        );
      case 'GLUTEN_FREE':
        return (
          <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold bg-purple-500/15 text-purple-300 border border-purple-500/30">
            GF
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-obsidian-950/80 backdrop-blur-md overflow-y-auto animate-fade-in">
      <div className="relative w-full max-w-3xl bg-charcoal-900 border border-gold-400/40 rounded-2xl shadow-luxury overflow-hidden my-6 max-h-[90vh] flex flex-col">
        {/* Landscape Hero Header with Ambient Gradient */}
        <div className="relative h-48 sm:h-56 w-full overflow-hidden shrink-0">
          <img
            src={outlet.imageUrl || '/images/outlets/fallback-outlet.webp'}
            alt={`${outlet.name} Ambience`}
            className="w-full h-full object-cover"
            onError={(e) => {
              (e.target as HTMLImageElement).src = '/images/outlets/fallback-outlet.webp';
            }}
          />
          {/* Subtle multi-layer gradient overlay */}
          <div className="absolute inset-0 bg-gradient-to-t from-charcoal-900 via-charcoal-900/60 to-transparent" />
          <div className="absolute inset-0 bg-gradient-to-r from-obsidian-950/80 via-transparent to-obsidian-950/60" />

          {/* Close Button */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-2 rounded-full bg-obsidian-950/70 hover:bg-obsidian-950 text-slate-300 hover:text-white border border-slate-700 hover:border-gold-400/50 transition backdrop-blur-sm shadow-md"
            aria-label="Close Menu"
          >
            <X className="w-5 h-5" />
          </button>

          {/* Header Title & Badges */}
          <div className="absolute bottom-4 left-4 right-4 sm:left-6 sm:right-6 flex flex-col sm:flex-row sm:items-end justify-between gap-2">
            <div>
              <div className="flex items-center gap-2 mb-1.5">
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider bg-gold-500/20 text-gold-300 border border-gold-400/40">
                  {outlet.signatureBadge || 'Signature Dining'}
                </span>
                <span className="text-xs text-gold-400 font-medium tracking-wide">
                  {outlet.cuisineType}
                </span>
              </div>
              <h2 className="text-2xl sm:text-3xl font-serif font-bold text-white tracking-wide">
                {outlet.name}
              </h2>
            </div>

            <div className="flex items-center gap-3 text-xs text-slate-300 bg-obsidian-950/70 backdrop-blur-md px-3 py-1.5 rounded-xl border border-slate-700/60 w-fit">
              <span className="flex items-center gap-1">
                <Clock className="w-3.5 h-3.5 text-gold-400" />
                <span>{outlet.openingTime} - {outlet.closingTime}</span>
              </span>
              <span className="text-slate-600">•</span>
              <span className="flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5 text-gold-400" />
                <span>{outlet.floorLocation || outlet.location.split(',')[0]}</span>
              </span>
            </div>
          </div>
        </div>

        {/* Filter Navigation Bar */}
        <div className="p-4 sm:px-6 border-b border-slate-800 bg-charcoal-900/90 backdrop-blur-sm shrink-0 space-y-2.5">
          {/* Categories */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-thin">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 mr-1 shrink-0">
              Courses:
            </span>
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3 py-1 rounded-lg text-xs font-medium whitespace-nowrap transition ${
                  selectedCategory === cat
                    ? 'bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 font-semibold shadow-gold-glow'
                    : 'bg-obsidian-900 text-slate-300 hover:text-white border border-slate-700 hover:border-slate-600'
                }`}
              >
                {cat === 'ALL' ? 'All Courses' : cat}
              </button>
            ))}
          </div>

          {/* Dietary Flags */}
          <div className="flex items-center gap-1.5 overflow-x-auto text-[11px]">
            <span className="text-slate-400 font-semibold uppercase tracking-wider mr-1 shrink-0">
              Dietary:
            </span>
            {['ALL', 'VEG', 'NON_VEG', 'VEGAN', 'JAIN', 'GLUTEN_FREE'].map((diet) => (
              <button
                key={diet}
                onClick={() => setDietaryFilter(diet)}
                className={`px-2.5 py-0.5 rounded-full transition font-mono ${
                  dietaryFilter === diet
                    ? 'bg-gold-400/20 text-gold-300 border border-gold-400/60 font-bold'
                    : 'bg-obsidian-900/60 text-slate-400 hover:text-slate-200 border border-slate-800'
                }`}
              >
                {diet === 'ALL' ? 'All Diets' : diet.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>

        {/* Menu Items List Viewport */}
        <div className="p-4 sm:p-6 overflow-y-auto flex-1 space-y-3.5">
          {filteredItems.length === 0 ? (
            <div className="text-center py-12 text-slate-400 space-y-2">
              <Utensils className="w-8 h-8 text-gold-400/60 mx-auto" />
              <p className="text-sm font-medium">No dishes match the selected dietary filters.</p>
              <button
                onClick={() => {
                  setSelectedCategory('ALL');
                  setDietaryFilter('ALL');
                }}
                className="text-xs text-gold-400 hover:underline"
              >
                Reset menu filters
              </button>
            </div>
          ) : (
            filteredItems.map((item) => (
              <div
                key={item.id}
                className="p-3.5 sm:p-4 rounded-xl bg-obsidian-900/70 border border-slate-800/80 hover:border-gold-400/40 transition group flex flex-col sm:flex-row sm:items-start justify-between gap-3"
              >
                <div className="space-y-1.5 flex-1">
                  <div className="flex items-center flex-wrap gap-2">
                    <h4 className="font-serif font-bold text-sm sm:text-base text-white group-hover:text-gold-300 transition">
                      {item.name}
                    </h4>
                    {item.isSignature && (
                      <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider bg-gold-500/15 text-gold-400 border border-gold-400/30">
                        <Sparkles className="w-2.5 h-2.5" />
                        Chef's Signature
                      </span>
                    )}
                    {item.dietaryFlags.map((flag) => (
                      <React.Fragment key={flag}>{getDietaryBadge(flag)}</React.Fragment>
                    ))}
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed pr-2">
                    {item.description}
                  </p>
                </div>

                <div className="text-left sm:text-right shrink-0 pt-1 sm:pt-0">
                  <span className="text-sm sm:text-base font-serif font-bold text-gold-300">
                    ₹{item.price.toLocaleString('en-IN')}
                  </span>
                  <p className="text-[10px] text-slate-500">Taxes as applicable</p>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Modal Footer with Direct Actions */}
        <div className="p-4 sm:px-6 border-t border-slate-800 bg-charcoal-950 flex flex-col sm:flex-row items-center justify-between gap-3 shrink-0">
          <div className="text-xs text-slate-400 flex items-center gap-1.5">
            <Shield className="w-3.5 h-3.5 text-gold-400" />
            <span>Dress Code: <strong className="text-slate-200">{outlet.dressCode}</strong></span>
          </div>

          <div className="flex items-center gap-2.5 w-full sm:w-auto justify-end">
            <button
              onClick={() => {
                onClose();
                onAskConcierge(`Tell me more about signature specialties, wine pairings, and guest favorites at ${outlet.name}.`);
              }}
              className="flex-1 sm:flex-initial px-3.5 py-2 rounded-xl border border-slate-700 hover:border-gold-400/50 bg-charcoal-900 text-slate-200 hover:text-gold-300 text-xs font-semibold flex items-center justify-center gap-1.5 transition"
            >
              <MessageSquare className="w-3.5 h-3.5 text-gold-400" />
              <span>Ask Concierge</span>
            </button>

            <button
              onClick={() => {
                onClose();
                onBookTable(outlet);
              }}
              className="flex-1 sm:flex-initial px-4 py-2 rounded-xl bg-gradient-to-r from-gold-500 to-gold-600 hover:brightness-110 text-obsidian-950 text-xs font-bold flex items-center justify-center gap-1.5 shadow-gold-glow transition"
            >
              <Calendar className="w-3.5 h-3.5" />
              <span>Book a Table</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
