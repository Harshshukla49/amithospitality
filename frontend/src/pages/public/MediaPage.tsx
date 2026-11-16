import React, { useState } from 'react';
import {
  Sparkles,
  Filter,
  Maximize2,
  X,
  ChevronLeft,
  ChevronRight,
  MapPin,
  Camera,
  Image as ImageIcon,
} from 'lucide-react';
import { HOSPITALITY_GALLERY_ITEMS, GalleryItem } from '../../utils/mockData';

export const MediaPage: React.FC = () => {
  const [selectedBrand, setSelectedBrand] = useState<string>('all');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [lightboxIndex, setLightboxIndex] = useState<number | null>(null);

  const brandFilters = [
    { label: 'All Brands', slug: 'all' },
    { label: 'Lord of the Drinks', slug: 'lord-of-the-drinks' },
    { label: 'Veneto Kitchen & Bar', slug: 'veneto' },
    { label: 'The Warehouse Cafe', slug: 'the-warehouse-cafe' },
    { label: 'Deliite Lifestyle', slug: 'deliite' },
  ];

  const categoryFilters = ['ALL', 'Interiors', 'Cocktails', 'Cuisine', 'Celebrations', 'Nightlife'];

  const filteredItems = HOSPITALITY_GALLERY_ITEMS.filter((item) => {
    const matchesBrand = selectedBrand === 'all' || item.brandSlug === selectedBrand;
    const matchesCat = selectedCategory === 'ALL' || item.category === selectedCategory;
    return matchesBrand && matchesCat;
  });

  const openLightbox = (index: number) => {
    setLightboxIndex(index);
  };

  const closeLightbox = () => {
    setLightboxIndex(null);
  };

  const nextImage = () => {
    if (lightboxIndex !== null) {
      setLightboxIndex((lightboxIndex + 1) % filteredItems.length);
    }
  };

  const prevImage = () => {
    if (lightboxIndex !== null) {
      setLightboxIndex((lightboxIndex - 1 + filteredItems.length) % filteredItems.length);
    }
  };

  const currentItem: GalleryItem | undefined =
    lightboxIndex !== null ? filteredItems[lightboxIndex] : undefined;

  return (
    <div className="min-h-screen bg-obsidian-950 text-slate-100 font-sans pb-24">
      {/* 1. HERO HEADER */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 border-b border-slate-800 bg-gradient-to-b from-charcoal-900 via-obsidian-950 to-obsidian-950">
        <div className="max-w-4xl mx-auto text-center space-y-4">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-charcoal-900 border border-gold-400/40 text-gold-300 text-xs font-mono uppercase tracking-widest">
            <Camera className="w-3.5 h-3.5 text-gold-400" />
            <span>Visual Chronicle • Media &amp; Gallery</span>
          </div>
          <h1 className="text-4xl sm:text-5xl font-serif font-bold text-white tracking-tight">
            Sensory Moments &amp; Ambiance
          </h1>
          <p className="text-sm sm:text-base text-slate-300 font-light max-w-2xl mx-auto leading-relaxed">
            Explore the architectural elegance, handcrafted cocktails, wood-fired gastronomy, and celebratory memories across Amit Hospitality destinations.
          </p>
        </div>
      </section>

      {/* 2. GALLERY CONTROLS & FILTERS */}
      <section className="py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-4">
        {/* Brand Filters */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-mono uppercase text-slate-400 mr-2 flex items-center gap-1">
            <Filter className="w-3.5 h-3.5 text-gold-400" />
            Brand:
          </span>
          {brandFilters.map((brand) => (
            <button
              key={brand.slug}
              onClick={() => setSelectedBrand(brand.slug)}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-medium transition ${
                selectedBrand === brand.slug
                  ? 'bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 font-bold shadow-gold-glow'
                  : 'bg-charcoal-900 text-slate-300 border border-slate-800 hover:border-slate-700'
              }`}
            >
              {brand.label}
            </button>
          ))}
        </div>

        {/* Category Filters */}
        <div className="flex flex-wrap items-center gap-2 pt-1 border-t border-slate-800/80">
          <span className="text-xs font-mono uppercase text-slate-400 mr-2">Category:</span>
          {categoryFilters.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1 rounded-lg text-[11px] font-mono transition ${
                selectedCategory === cat
                  ? 'bg-charcoal-800 text-gold-300 border border-gold-400/40 font-semibold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </section>

      {/* 3. RESPONSIVE MASONRY PHOTO GRID */}
      <section className="px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        {filteredItems.length === 0 ? (
          <div className="p-16 text-center rounded-3xl bg-charcoal-900/50 border border-slate-800 space-y-3">
            <ImageIcon className="w-10 h-10 text-slate-600 mx-auto" />
            <h3 className="text-lg font-serif font-bold text-white">No Photographs Found</h3>
            <p className="text-xs text-slate-400">
              Try switching your brand or category filter to browse more images.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredItems.map((item, idx) => (
              <div
                key={item.id}
                onClick={() => openLightbox(idx)}
                className="group relative rounded-2xl overflow-hidden bg-charcoal-900 border border-slate-800 hover:border-gold-400/50 transition-all duration-300 cursor-pointer shadow-lg hover:shadow-gold-glow/20"
              >
                {/* Photo Element with Fallback Handler */}
                <div className="relative h-72 w-full overflow-hidden">
                  <img
                    src={item.imageUrl}
                    alt={item.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    onError={(e: any) => {
                      e.currentTarget.src = item.fallbackUrl;
                    }}
                    loading="lazy"
                  />
                  {/* Subtle Gradient Veil */}
                  <div className="absolute inset-0 bg-gradient-to-t from-obsidian-950 via-obsidian-950/20 to-transparent opacity-80 group-hover:opacity-60 transition-opacity" />

                  {/* Top Badges */}
                  <div className="absolute top-3 left-3">
                    <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono uppercase bg-obsidian-950/80 text-gold-300 border border-gold-400/30 backdrop-blur-sm">
                      {item.brandName}
                    </span>
                  </div>

                  <div className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity p-1.5 rounded-lg bg-obsidian-950/80 text-white">
                    <Maximize2 className="w-4 h-4" />
                  </div>

                  {/* Bottom Caption Overlay */}
                  <div className="absolute bottom-3 left-3 right-3 space-y-1">
                    <span className="text-[10px] font-mono text-gold-400 uppercase tracking-widest">
                      {item.category}
                    </span>
                    <h4 className="text-sm font-serif font-bold text-white leading-tight">
                      {item.title}
                    </h4>
                    <p className="text-[11px] text-slate-300 line-clamp-1">
                      {item.caption}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* 4. FULL-SCREEN LIGHTBOX MODAL */}
      {currentItem && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-obsidian-950/95 backdrop-blur-xl p-4 sm:p-8 animate-fade-in">
          {/* Close Lightbox */}
          <button
            onClick={closeLightbox}
            className="absolute top-6 right-6 p-2 rounded-full bg-charcoal-900 border border-slate-700 text-slate-300 hover:text-white transition z-10"
            aria-label="Close image lightbox"
          >
            <X className="w-6 h-6" />
          </button>

          {/* Previous Button */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              prevImage();
            }}
            className="absolute left-4 sm:left-8 top-1/2 -translate-y-1/2 p-3 rounded-full bg-charcoal-900/80 border border-slate-700 text-white hover:border-gold-400 transition z-10"
            aria-label="Previous image"
          >
            <ChevronLeft className="w-6 h-6" />
          </button>

          {/* Next Button */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              nextImage();
            }}
            className="absolute right-4 sm:right-8 top-1/2 -translate-y-1/2 p-3 rounded-full bg-charcoal-900/80 border border-slate-700 text-white hover:border-gold-400 transition z-10"
            aria-label="Next image"
          >
            <ChevronRight className="w-6 h-6" />
          </button>

          {/* Lightbox Center Content */}
          <div className="max-w-5xl w-full max-h-[85vh] flex flex-col items-center">
            <div className="relative w-full max-h-[70vh] flex items-center justify-center overflow-hidden rounded-2xl border border-slate-800 shadow-2xl">
              <img
                src={currentItem.imageUrl}
                alt={currentItem.title}
                className="max-h-[70vh] w-auto max-w-full object-contain rounded-2xl"
                onError={(e: any) => {
                  e.currentTarget.src = currentItem.fallbackUrl;
                }}
              />
            </div>

            {/* Info Footer */}
            <div className="w-full text-center mt-4 space-y-1">
              <p className="text-xs font-mono text-gold-400 uppercase tracking-widest">
                {currentItem.brandName} • {currentItem.category}
              </p>
              <h3 className="text-xl font-serif font-bold text-white">
                {currentItem.title}
              </h3>
              <p className="text-xs text-slate-300 max-w-xl mx-auto">
                {currentItem.caption}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
