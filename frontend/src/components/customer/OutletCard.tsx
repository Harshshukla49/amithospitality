import React, { useState } from 'react';
import {
  Sparkles,
  Clock,
  MapPin,
  Utensils,
  Calendar,
  Check,
  ChevronRight,
  Shield,
} from 'lucide-react';
import { Outlet } from '../../types';

interface OutletCardProps {
  outlet: Outlet;
  isSelected: boolean;
  onSelect: (outlet: Outlet) => void;
  onViewMenu: (outlet: Outlet) => void;
  onBookTable: (outlet: Outlet) => void;
}

export const OutletCard: React.FC<OutletCardProps> = ({
  outlet,
  isSelected,
  onSelect,
  onViewMenu,
  onBookTable,
}) => {
  const [imageError, setImageError] = useState(false);

  const imageSrc = imageError
    ? '/images/outlets/fallback-outlet.webp'
    : outlet.imageUrl || '/images/outlets/fallback-outlet.webp';

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={() => onSelect(outlet)}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onSelect(outlet);
        }
      }}
      className={`group relative flex flex-col rounded-2xl overflow-hidden transition-all duration-300 cursor-pointer text-left focus:outline-none focus:ring-2 focus:ring-gold-400 ${
        isSelected
          ? 'bg-charcoal-900 border-2 border-gold-400 shadow-gold-glow ring-1 ring-gold-400/50'
          : 'bg-charcoal-900/80 border border-slate-800 hover:border-gold-400/60 hover:shadow-luxury'
      }`}
    >
      {/* 16:9 Landscape Image Header with Hover Zoom & Subtle Dark Gradient Overlays */}
      <div className="relative w-full aspect-[16/9] overflow-hidden bg-obsidian-950 shrink-0">
        <img
          src={imageSrc}
          alt={`${outlet.name} - ${outlet.cuisineType}`}
          className="w-full h-full object-cover transition-transform duration-700 ease-out group-hover:scale-105"
          onError={() => setImageError(true)}
          loading="lazy"
        />

        {/* Ambient Dark Gradient Overlays for Readability */}
        <div className="absolute inset-0 bg-gradient-to-t from-charcoal-900 via-charcoal-900/30 to-transparent pointer-events-none" />
        <div className="absolute inset-0 bg-gradient-to-b from-obsidian-950/60 via-transparent to-transparent pointer-events-none" />

        {/* Signature Outlet Badge (Top Left) */}
        <div className="absolute top-3 left-3 flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-obsidian-950/85 backdrop-blur-md border border-gold-400/40 text-gold-300 text-[10px] sm:text-[11px] font-semibold tracking-wider uppercase shadow-md">
          <Sparkles className="w-3 h-3 text-gold-400 shrink-0" />
          <span>{outlet.signatureBadge || (outlet.isPopular ? 'Signature Destination' : 'Exclusive Dining')}</span>
        </div>

        {/* Active Concierge Context Indicator (Top Right) */}
        {isSelected && (
          <div className="absolute top-3 right-3 flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 text-[10px] sm:text-[11px] font-bold tracking-wider uppercase shadow-gold-glow animate-pulse">
            <Check className="w-3 h-3 stroke-[3]" />
            <span>Active Concierge</span>
          </div>
        )}

        {/* Floating Quick Location Chip on Image Bottom */}
        <div className="absolute bottom-2.5 left-3 right-3 flex items-center justify-between text-[11px] text-slate-300">
          <span className="flex items-center gap-1 bg-obsidian-950/80 backdrop-blur-sm px-2 py-0.5 rounded-md border border-slate-700/60">
            <MapPin className="w-3 h-3 text-gold-400 shrink-0" />
            <span className="truncate max-w-[170px] sm:max-w-[200px]">
              {outlet.floorLocation || outlet.location.split(',')[0]}
            </span>
          </span>
          <span className="flex items-center gap-1 bg-obsidian-950/80 backdrop-blur-sm px-2 py-0.5 rounded-md border border-slate-700/60">
            <Clock className="w-3 h-3 text-gold-400 shrink-0" />
            <span>{outlet.openingTime} - {outlet.closingTime}</span>
          </span>
        </div>
      </div>

      {/* Card Content Body */}
      <div className="p-4 sm:p-5 flex-1 flex flex-col justify-between space-y-3.5">
        <div>
          {/* Cuisine Sub-heading */}
          <div className="flex items-center justify-between gap-2 mb-1">
            <span className="text-[11px] font-mono tracking-wider uppercase text-gold-400 font-semibold truncate">
              {outlet.cuisineType}
            </span>
            <span className="text-[10px] text-slate-400 shrink-0">
              {outlet.outletType.split('&')[0]}
            </span>
          </div>

          {/* Luxury Outlet Title */}
          <h3
            className={`font-serif text-lg sm:text-xl font-bold tracking-wide transition-colors ${
              isSelected ? 'text-gold-300' : 'text-white group-hover:text-gold-200'
            }`}
          >
            {outlet.name}
          </h3>

          {/* Description */}
          <p className="text-xs text-slate-300 mt-1.5 leading-relaxed line-clamp-2">
            {outlet.description}
          </p>
        </div>

        {/* Action Button Row with Strict Event Isolation */}
        <div className="pt-2 border-t border-slate-800 flex items-center gap-2">
          {/* View Menu Button */}
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              onViewMenu(outlet);
            }}
            className="flex-1 px-3 py-2 rounded-xl bg-obsidian-900 hover:bg-charcoal-800 text-slate-200 hover:text-gold-300 border border-slate-700/80 hover:border-gold-400/50 text-xs font-semibold flex items-center justify-center gap-1.5 transition shadow-sm"
          >
            <Utensils className="w-3.5 h-3.5 text-gold-400" />
            <span>View Menu</span>
          </button>

          {/* Book a Table Button */}
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              onBookTable(outlet);
            }}
            className="flex-1 px-3 py-2 rounded-xl bg-gradient-to-r from-gold-500 to-gold-600 hover:brightness-110 text-obsidian-950 text-xs font-bold flex items-center justify-center gap-1.5 shadow-gold-glow transition"
          >
            <Calendar className="w-3.5 h-3.5" />
            <span>Book a Table</span>
          </button>
        </div>

        {/* Selection Status Prompt */}
        <div className="text-[10px] text-center pt-0.5">
          {isSelected ? (
            <span className="text-gold-400/90 font-medium flex items-center justify-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-gold-400 animate-ping" />
              <span>Converse with {outlet.name.split(' ')[0]} concierge below</span>
            </span>
          ) : (
            <span className="text-slate-400 group-hover:text-slate-200 transition flex items-center justify-center gap-1">
              <span>Click card to switch AI Concierge</span>
              <ChevronRight className="w-3 h-3 text-gold-400/60" />
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
