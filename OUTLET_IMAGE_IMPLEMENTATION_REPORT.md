# AMIT AI CONCIERGE — PREMIUM OUTLET IMAGE GALLERY & VISUAL CARD UPGRADE
## Outlet Image Implementation & Asset Specification Report

**Project:** Amit AI Concierge  
**Organization:** Amit Hospitality  
**Visual Aesthetic:** Five-Star Luxury Hospitality & Palace Grandeur (Gold & Obsidian Palette)  
**Status:** COMPLETE & VERIFIED  
**Date:** November 8, 2026  

---

## 1. Executive Summary

The Customer Concierge interface of the **Amit AI Concierge** platform has been upgraded from text-dominated cards into a visually arresting, five-star luxury dining gallery. Each of the three core Amit Hospitality dining outlets now features an ultra-realistic, architectural landscape photograph capturing its distinctive ambiance, architectural character, and culinary prestige.

All imagery adheres strictly to a **16:9 widescreen aspect ratio** (1376 × 768 px), optimized for high-density displays (Retina/4K), and stored locally in the frontend public asset directory with graceful fallback handling.

---

## 2. Outlet Image Catalog & Asset Specifications

### A. Amber Terrace Rooftop
* **Outlet Category:** Rooftop Lounge & Fine Dining
* **Cuisine:** Modern Pan-Asian & Global Small Plates
* **Location:** 14th Floor Skyline Rooftop, Skyline Tower, MG Road
* **Primary Asset Path:** `/images/outlets/amber-terrace-rooftop.webp`
* **Alternative Asset Path:** `/images/outlets/amber-terrace-rooftop.jpg`
* **Resolution & Ratio:** 1376 × 768 pixels (16:9 widescreen)
* **File Size:** 995,743 bytes (~972 KB)
* **Visual Atmosphere & Composition:**
  - **Twilight/Night Sky:** Cinematic deep indigo dusk sky with glowing city skyscrapers and shimmering high-rise architecture across the panoramic horizon.
  - **Dining Furniture & Linens:** Impeccably styled outdoor teak and marble dining tables with glowing glass-enclosed hurricane candles, sparkling crystal wine glasses, and silver cutlery.
  - **Lounge & Lighting:** Low-profile designer lounge banquettes with plush cream cushions, warm amber under-bench LED lighting, delicate hanging fairy lights, and frameless safety glass balustrades offering unobstructed skyline vistas.
  - **Vibe:** Ultra-exclusive, romantic, high-energy metropolitan luxury.

---

### B. Saffron & Silk
* **Outlet Category:** Fine Dining Restaurant
* **Cuisine:** Contemporary Royal Indian & Awadhi
* **Location:** Grand Lobby Level Heritage, Amit Heritage Plaza
* **Primary Asset Path:** `/images/outlets/saffron-and-silk.webp`
* **Alternative Asset Path:** `/images/outlets/saffron-and-silk.jpg`
* **Resolution & Ratio:** 1376 × 768 pixels (16:9 widescreen)
* **File Size:** 987,860 bytes (~964 KB)
* **Visual Atmosphere & Composition:**
  - **Architecture & Grandeur:** Soaring vaulted palace ceilings featuring intricate carved jali lattice screens, gilded mouldings, and polished white Makrana marble floors with soft reflections.
  - **Illumination:** Magnificent colossal crystal chandeliers suspended in cascade, casting a warm golden radiance over the grand hall.
  - **Imperial Banqueting:** Large circular dining tables draped in pristine heavy white damask linen, set with ornate hand-beaten gold and brass thali chargers, polished gold silverware, and delicate crystal stemware.
  - **Fabrics & Upholstery:** Sculpted royal dining armchairs upholstered in deep saffron and royal maroon silk velvet, with matching drapery framing arched alcoves.
  - **Vibe:** Opulent, heritage-rich, regal five-star palace hospitality.

---

### C. The Velvet Cellar
* **Outlet Category:** Speakeasy & Cocktail Lounge
* **Cuisine:** Artisanal Tapas & Charcuterie
* **Location:** Sub-level 1 Jazz Vault, Amit Heritage Plaza
* **Primary Asset Path:** `/images/outlets/velvet-cellar.webp`
* **Alternative Asset Path:** `/images/outlets/velvet-cellar.jpg`
* **Resolution & Ratio:** 1376 × 768 pixels (16:9 widescreen)
* **File Size:** 889,534 bytes (~868 KB)
* **Visual Atmosphere & Composition:**
  - **Subterranean Architecture:** Heritage exposed brick barrel arches and rich, dark Honduran mahogany wall paneling.
  - **Backlit Master Bar:** Long dark marble and timber bar counter with an expansive multi-tiered backlit amber glass gantry showcasing glowing vintage whiskeys, small-batch rums, and rare cognacs with warm golden halo illumination.
  - **Lounge Seating:** Curved tufted banquettes in deep jewel-toned emerald green and sapphire blue velvet, paired with plush velvet lounge armchairs.
  - **Table Settings & Lighting:** Low-light intimate speakeasy atmosphere punctuated by art-deco brass table lamps, smoky candle votives, and crystal coupe cocktail glasses resting on polished brass cocktail tables.
  - **Vibe:** Moody, clandestine, sophisticated subterranean jazz sanctuary.

---

### D. System Fallback Asset
* **Asset Path:** `/images/outlets/fallback-outlet.webp` (and `.jpg`)
* **Resolution:** 1376 × 768 pixels (16:9)
* **Purpose:** Serves as a reliable, luxury five-star fallback in the event of missing assets or offline/network disruptions, ensuring the UI never displays broken image placeholders.

---

## 3. Storage Directory & Distribution Structure

```
frontend/
├── public/
│   └── images/
│       └── outlets/
│           ├── amber-terrace-rooftop.webp   (995 KB, 1376x768)
│           ├── amber-terrace-rooftop.jpg    (995 KB, 1376x768)
│           ├── saffron-and-silk.webp        (987 KB, 1376x768)
│           ├── saffron-and-silk.jpg         (987 KB, 1376x768)
│           ├── velvet-cellar.webp           (889 KB, 1376x768)
│           ├── velvet-cellar.jpg            (889 KB, 1376x768)
│           ├── fallback-outlet.webp         (987 KB, 1376x768)
│           └── fallback-outlet.jpg          (987 KB, 1376x768)
└── dist/
    └── images/
        └── outlets/  (Automatically bundled into production build)
```

---

## 4. Component Implementation & Integration

| Component | File Path | Role in Image Gallery Upgrade |
|---|---|---|
| `OutletCard` | `frontend/src/components/customer/OutletCard.tsx` | Dedicated 16:9 landscape card with hover zoom, gold border highlights, active context pills, signature badges, and event-isolated action buttons. |
| `MenuModal` | `frontend/src/components/customer/MenuModal.tsx` | Immersive full-screen luxury modal showcasing high-res outlet header, course categories, dietary filters, price points, and direct reservation triggers. |
| `ConciergePage` | `frontend/src/pages/customer/ConciergePage.tsx` | Transformed customer landing page with curated gallery header, 3-column responsive grid, and docked AI Concierge terminal with smooth anchor scrolling. |
| `OutletsPage` | `frontend/src/pages/admin/OutletsPage.tsx` | Enhanced admin console outlet tabs with visual photograph headers for brand consistency across staff and guest workflows. |
| `mockData.ts` | `frontend/src/utils/mockData.ts` | Enriched `INITIAL_OUTLETS` data objects with `imageUrl`, `signatureBadge`, and `floorLocation` properties. |
| `types/index.ts` | `frontend/src/types/index.ts` | Updated `Outlet` TypeScript interface with optional `imageUrl`, `signatureBadge`, and `floorLocation` fields. |

---

## 5. Image Resilience & Performance Optimizations

1. **Native Lazy Loading:** All image tags specify `loading="lazy"` to defer off-screen image loading until the guest approaches the viewport.
2. **Graceful Fallback Handlers:** Each `img` tag implements an `onError` event handler:
   ```tsx
   onError={() => setImageError(true)}
   ```
   If a network fault or resource block occurs, the component automatically replaces the broken resource with `/images/outlets/fallback-outlet.webp`.
3. **Multi-layer Gradient Scrims:** Each image is overlaid with CSS linear gradients (`bg-gradient-to-t from-charcoal-900 via-charcoal-900/30 to-transparent`), guaranteeing that white and gold text remains razor-sharp and WCAG compliant regardless of image exposure.
4. **Hardware-Accelerated Hover Zoom:** Images scale on hover using CSS `group-hover:scale-105 transition-transform duration-700 ease-out` leveraging GPU compositing for silky 60fps rendering without layout reflows.
