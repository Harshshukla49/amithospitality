import React, { useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  Sparkles,
  Calendar,
  User,
  X,
  ArrowRight,
  Home,
  BookOpen,
  UtensilsCrossed,
  Image as ImageIcon,
  PartyPopper,
  Briefcase,
  HelpCircle,
  MapPin,
  Shield,
  LogOut,
} from 'lucide-react';
import { useEnvironment } from '../../context/EnvironmentContext';
import { useAuth } from '../../context/AuthContext';

interface MegaMenuOverlayProps {
  isOpen: boolean;
  onClose: () => void;
}

export const MegaMenuOverlay: React.FC<MegaMenuOverlayProps> = ({ isOpen, onClose }) => {
  const { environment, isDemo, openSwitchModal } = useEnvironment();
  const { user, isAuthenticated, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const overlayRef = useRef<HTMLDivElement>(null);
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const prevPathRef = useRef(location.pathname);
  const triggerElementRef = useRef<HTMLElement | null>(null);

  // Prevent background scrolling and manage focus restoration
  useEffect(() => {
    if (isOpen) {
      triggerElementRef.current = document.activeElement as HTMLElement;
      const originalOverflow = document.body.style.overflow;
      document.body.style.overflow = 'hidden';

      // Focus close button on open
      const timer = setTimeout(() => closeButtonRef.current?.focus(), 50);

      return () => {
        document.body.style.overflow = originalOverflow;
        clearTimeout(timer);
        // Restore focus to trigger element on close
        if (triggerElementRef.current && typeof triggerElementRef.current.focus === 'function') {
          triggerElementRef.current.focus();
        }
      };
    }
  }, [isOpen]);

  // Close on ESC key and trap focus within modal dialog (Tab / Shift+Tab)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;

      if (e.key === 'Escape') {
        onClose();
        return;
      }

      if (e.key === 'Tab' && overlayRef.current) {
        const focusableElements = overlayRef.current.querySelectorAll<HTMLElement>(
          'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
        );
        if (focusableElements.length === 0) return;

        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        if (e.shiftKey) {
          if (document.activeElement === firstElement || !overlayRef.current.contains(document.activeElement)) {
            e.preventDefault();
            lastElement.focus();
          }
        } else {
          if (document.activeElement === lastElement || !overlayRef.current.contains(document.activeElement)) {
            e.preventDefault();
            firstElement.focus();
          }
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // Close only on subsequent route changes, not on initial mount
  useEffect(() => {
    if (prevPathRef.current !== location.pathname) {
      prevPathRef.current = location.pathname;
      onClose();
    }
  }, [location.pathname, onClose]);

  if (!isOpen) return null;
  if (typeof document === 'undefined') return null;

  const isCurrentActive = (path: string) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  const handleLogout = () => {
    logout();
    onClose();
    navigate('/login');
  };

  // 4 Genuine Amit Hospitality Portfolio Brands (Verified Content, No Unsupported Claims)
  const brands = [
    {
      id: 'lotd',
      name: 'LORD OF THE DRINKS',
      descriptor: 'Experiential Dining, Medieval European Architecture & Bar Sanctuary',
      location: '4th Floor, South City Mall',
      path: '/brands/lord-of-drinks',
      image: '/images/brands/lord-of-the-drinks.jpg',
      badge: 'Lounge & Bar',
    },
    {
      id: 'veneto',
      name: 'VENETO KITCHEN & BAR',
      descriptor: 'Artisanal Italian Kitchen, Neapolitan Pizzeria & Handcrafted Cocktails',
      location: '4th Floor, South City Mall',
      path: '/brands/veneto',
      image: '/images/brands/veneto.jpg',
      badge: 'Artisanal Italian',
    },
    {
      id: 'warehouse',
      name: 'THE WAREHOUSE CAFE',
      descriptor: 'Urban Industrial Restobar, Global Cuisines & Vibrant Ambience',
      location: '4th Floor, South City Mall',
      path: '/brands/warehouse',
      image: '/images/brands/warehouse-cafe.jpg',
      badge: 'Urban Cafe',
    },
    {
      id: 'deliite',
      name: 'DELIITE',
      descriptor: 'Boutique Liquor & Premium Beverage Retail Destination',
      location: '3rd Floor, Diamond Plaza Mall',
      path: '/brands/deliite',
      image: '/images/brands/deliite.jpg',
      badge: 'Boutique Retail',
    },
  ];

  // Group A: Explore
  const exploreLinks = [
    { label: 'Home', path: '/', icon: Home, desc: 'Corporate portal & portfolio overview' },
    { label: 'Know Us', path: '/about', icon: BookOpen, desc: 'Heritage, leadership & corporate story' },
    { label: 'Digital Menus', path: '/menus', icon: UtensilsCrossed, desc: 'Curated menus across all destinations' },
    { label: 'Gallery', path: '/media', icon: ImageIcon, desc: 'Photographic moments & press coverage' },
  ];

  // Group B: Experience & Connect
  const connectLinks = [
    { label: 'Events', path: '/events', icon: PartyPopper, desc: 'Celebrations, nightlife & private dining' },
    { label: 'Careers', path: '/career', icon: Briefcase, desc: 'Join our dedicated culinary and guest experience team' },
    { label: 'Enquiry', path: '/enquiry', icon: HelpCircle, desc: 'Banquets, corporate events & reservations' },
    { label: 'Contact', path: '/contact', icon: MapPin, desc: 'Kolkata headquarters & mall destinations' },
  ];

  const content = (
    <div
      ref={overlayRef}
      className="fixed inset-0 z-[100] bg-[#08090B] text-[#F5F3EE] w-full max-w-full overflow-x-hidden overflow-y-auto animate-fade-in flex flex-col justify-between motion-reduce:transition-none"
      role="dialog"
      aria-modal="true"
      aria-label="Amit Hospitality Luxury Navigation Menu"
    >
      {/* ========================================================================= */}
      {/* PHASE 3: PREMIUM HEADER                                                    */}
      {/* ========================================================================= */}
      <header className="sticky top-0 z-30 w-full border-b border-[#232730] bg-[#08090B]/95 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 h-16 sm:h-20 flex items-center justify-between gap-2 sm:gap-4">
          {/* Left Brand Lockup */}
          <Link to="/" onClick={onClose} className="flex items-center gap-2 sm:gap-3.5 group shrink min-w-0">
            <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-xl bg-gradient-to-br from-[#E2BE65] to-[#C9A13B] flex items-center justify-center shadow-md group-hover:scale-105 transition-transform motion-reduce:transition-none shrink-0">
              <Sparkles className="w-4 h-4 sm:w-5 sm:h-5 text-[#08090B]" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-1.5 sm:gap-2">
                <span className="font-serif font-bold text-xs sm:text-lg lg:text-xl tracking-wider text-[#F5F3EE] group-hover:text-[#E2BE65] transition-colors truncate max-w-[130px] sm:max-w-none">
                  AMIT HOSPITALITY
                </span>
                <span className="hidden md:inline-block text-[9px] tracking-widest font-mono uppercase px-1.5 py-0.5 rounded bg-[#C9A13B]/15 text-[#C9A13B] border border-[#C9A13B]/30 shrink-0">
                  LLP • ESTD 2018
                </span>
              </div>
              <p className="text-[11px] text-[#A6ABB5] font-sans tracking-wide hidden sm:block truncate">
                Distinctive Dining &amp; Experiential Hospitality
              </p>
            </div>
          </Link>

          {/* Right Controls */}
          <div className="flex items-center gap-1.5 sm:gap-3 shrink-0">
            {/* AI Concierge */}
            <Link
              to="/concierge"
              onClick={onClose}
              title="Amit AI Concierge"
              className="flex items-center gap-1.5 px-2.5 py-1.5 sm:px-3.5 sm:py-2 rounded-xl bg-gradient-to-r from-[#C9A13B] to-[#E2BE65] text-[#08090B] font-bold text-xs shadow-md hover:brightness-110 transition active:scale-95 motion-reduce:transition-none shrink-0"
            >
              <Sparkles className="w-3.5 h-3.5 shrink-0" />
              <span className="hidden sm:inline">AI Concierge</span>
            </Link>

            {/* My Booking */}
            <Link
              to="/guest/reservations"
              onClick={onClose}
              title="Track or modify your table reservation"
              className="hidden sm:flex items-center gap-1.5 px-3 py-2 rounded-xl bg-[#111318] border border-[#232730] text-[#F5F3EE] hover:border-[#C9A13B]/50 hover:text-[#E2BE65] text-xs font-medium transition active:scale-95 motion-reduce:transition-none shrink-0"
            >
              <Calendar className="w-3.5 h-3.5 text-[#C9A13B]" />
              <span>My Booking</span>
            </Link>

            {/* User / Staff Portal */}
            {isAuthenticated ? (
              <div className="flex items-center gap-1.5 sm:gap-2 shrink-0">
                <Link
                  to="/admin/dashboard"
                  onClick={onClose}
                  className="hidden md:flex items-center gap-1.5 px-3 py-2 rounded-xl bg-[#171A20] border border-[#C9A13B]/30 text-[#E2BE65] text-xs font-medium hover:bg-[#111318] transition"
                >
                  <Shield className="w-3.5 h-3.5 text-[#C9A13B]" />
                  <span className="max-w-[100px] truncate">{user?.fullName || 'Staff Console'}</span>
                </Link>
                <button
                  onClick={handleLogout}
                  title="Sign out of staff account"
                  className="p-1.5 sm:p-2 rounded-xl text-rose-400 hover:bg-rose-950/30 transition shrink-0"
                  aria-label="Sign out"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <Link
                to="/login"
                onClick={onClose}
                title="Staff Portal Sign In"
                className="p-1.5 sm:p-2 rounded-xl bg-[#111318] border border-[#232730] text-[#A6ABB5] hover:text-[#E2BE65] hover:border-[#C9A13B]/40 transition shrink-0"
                aria-label="Staff Portal"
              >
                <User className="w-4 h-4" />
              </Link>
            )}

            {/* Close Button */}
            <button
              ref={closeButtonRef}
              onClick={onClose}
              className="flex items-center gap-1 sm:gap-1.5 px-2.5 sm:px-3 py-1.5 sm:py-2 rounded-xl bg-[#171A20] border border-[#232730] text-[#F5F3EE] hover:border-[#C9A13B]/60 hover:text-[#E2BE65] text-xs font-medium transition group focus:outline-none focus:ring-2 focus:ring-[#C9A13B]/40 shrink-0"
              aria-label="Close navigation menu"
            >
              <X className="w-4 h-4 text-[#A6ABB5] group-hover:text-[#E2BE65] group-hover:rotate-90 transition-transform duration-200 motion-reduce:transition-none" />
              <span className="hidden sm:inline font-mono uppercase tracking-wider text-[11px]">Close</span>
            </button>
          </div>
        </div>
      </header>

      {/* ========================================================================= */}
      {/* MAIN BODY: OUR BRANDS + GROUPED NAVIGATION                                */}
      {/* ========================================================================= */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-14">
          {/* --------------------------------------------------------------------- */}
          {/* PHASE 4: OUR BRANDS SECTION (7 cols on Desktop)                      */}
          {/* --------------------------------------------------------------------- */}
          <section className="lg:col-span-7">
            <div className="flex items-center justify-between mb-5 pb-3 border-b border-[#232730]">
              <div>
                <p className="text-[10px] font-mono uppercase tracking-widest text-[#C9A13B] font-semibold">
                  Portfolio Showcase
                </p>
                <h2 className="font-serif text-xl sm:text-2xl font-bold tracking-wide text-[#F5F3EE]">
                  Our Signature Brands
                </h2>
              </div>
              <span className="text-[11px] text-[#A6ABB5] font-mono hidden sm:inline">
                4 Experiential Venues
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {brands.map((brand) => (
                <Link
                  key={brand.id}
                  to={brand.path}
                  onClick={onClose}
                  className="group relative flex flex-col rounded-2xl bg-[#171A20] border border-[#232730] hover:border-[#C9A13B]/50 overflow-hidden shadow-lg transition-all duration-300 hover:-translate-y-0.5 motion-reduce:transition-none"
                >
                  {/* Image with Zoom */}
                  <div className="relative h-36 sm:h-40 w-full overflow-hidden bg-[#111318]">
                    <img
                      src={brand.image}
                      alt={brand.name}
                      className="w-full h-full object-cover object-center group-hover:scale-105 transition-transform duration-500 motion-reduce:transition-none"
                      loading="lazy"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-[#171A20] via-[#171A20]/40 to-transparent" />
                    <span className="absolute top-3 left-3 text-[9px] font-mono uppercase tracking-wider px-2 py-0.5 rounded-full bg-[#08090B]/85 text-[#E2BE65] border border-[#C9A13B]/30 backdrop-blur-sm">
                      {brand.badge}
                    </span>
                  </div>

                  {/* Card Content */}
                  <div className="p-4 flex-1 flex flex-col justify-between">
                    <div>
                      <h3 className="font-serif font-bold text-sm tracking-wide text-[#F5F3EE] group-hover:text-[#E2BE65] transition-colors">
                        {brand.name}
                      </h3>
                      <p className="text-[11px] text-[#A6ABB5] mt-1 line-clamp-2 font-sans">
                        {brand.descriptor}
                      </p>
                    </div>

                    <div className="mt-3 pt-2.5 border-t border-[#232730] flex items-center justify-between text-[10px] text-[#A6ABB5]">
                      <span className="font-mono truncate">{brand.location}</span>
                      <span className="inline-flex items-center gap-1 text-[#C9A13B] font-semibold group-hover:text-[#E2BE65] group-hover:translate-x-1 transition-transform motion-reduce:transition-none shrink-0">
                        Explore <ArrowRight className="w-3 h-3" />
                      </span>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </section>

          {/* --------------------------------------------------------------------- */}
          {/* PHASE 5: NAVIGATION GROUPS (5 cols on Desktop)                       */}
          {/* --------------------------------------------------------------------- */}
          <section className="lg:col-span-5 flex flex-col justify-between gap-8">
            {/* GROUP A: EXPLORE */}
            <div>
              <div className="mb-4 pb-2 border-b border-[#232730]">
                <p className="text-[10px] font-mono uppercase tracking-widest text-[#C9A13B] font-semibold">
                  Group A
                </p>
                <h2 className="font-serif text-lg font-bold tracking-wide text-[#F5F3EE]">
                  Explore
                </h2>
              </div>
              <div className="space-y-1.5">
                {exploreLinks.map((item) => {
                  const Icon = item.icon;
                  const active = isCurrentActive(item.path);
                  return (
                    <Link
                      key={item.label}
                      to={item.path}
                      onClick={onClose}
                      className={`group flex items-center justify-between p-3 rounded-xl border transition-all duration-200 motion-reduce:transition-none ${
                        active
                          ? 'bg-[#171A20] border-[#C9A13B]/40 text-[#E2BE65]'
                          : 'bg-[#111318]/50 border-transparent hover:bg-[#171A20] hover:border-[#232730] text-[#F5F3EE]'
                      }`}
                    >
                      <div className="flex items-center gap-3 min-w-0">
                        <div
                          className={`p-2 rounded-lg transition-colors ${
                            active
                              ? 'bg-[#C9A13B]/15 text-[#E2BE65]'
                              : 'bg-[#171A20] text-[#A6ABB5] group-hover:text-[#C9A13B]'
                          }`}
                        >
                          <Icon className="w-4 h-4" />
                        </div>
                        <div className="min-w-0">
                          <p className="text-xs font-semibold tracking-wide truncate group-hover:text-[#E2BE65] transition-colors">
                            {item.label}
                          </p>
                          <p className="text-[10px] text-[#A6ABB5] truncate hidden sm:block">
                            {item.desc}
                          </p>
                        </div>
                      </div>
                      <ArrowRight
                        className={`w-3.5 h-3.5 text-[#A6ABB5] group-hover:text-[#E2BE65] group-hover:translate-x-1 transition-all motion-reduce:transition-none ${
                          active ? 'text-[#E2BE65]' : 'opacity-0 group-hover:opacity-100'
                        }`}
                      />
                    </Link>
                  );
                })}
              </div>
            </div>

            {/* GROUP B: EXPERIENCE & CONNECT */}
            <div>
              <div className="mb-4 pb-2 border-b border-[#232730]">
                <p className="text-[10px] font-mono uppercase tracking-widest text-[#C9A13B] font-semibold">
                  Group B
                </p>
                <h2 className="font-serif text-lg font-bold tracking-wide text-[#F5F3EE]">
                  Experience &amp; Connect
                </h2>
              </div>
              <div className="space-y-1.5">
                {connectLinks.map((item) => {
                  const Icon = item.icon;
                  const active = isCurrentActive(item.path);
                  return (
                    <Link
                      key={item.label}
                      to={item.path}
                      onClick={onClose}
                      className={`group flex items-center justify-between p-3 rounded-xl border transition-all duration-200 motion-reduce:transition-none ${
                        active
                          ? 'bg-[#171A20] border-[#C9A13B]/40 text-[#E2BE65]'
                          : 'bg-[#111318]/50 border-transparent hover:bg-[#171A20] hover:border-[#232730] text-[#F5F3EE]'
                      }`}
                    >
                      <div className="flex items-center gap-3 min-w-0">
                        <div
                          className={`p-2 rounded-lg transition-colors ${
                            active
                              ? 'bg-[#C9A13B]/15 text-[#E2BE65]'
                              : 'bg-[#171A20] text-[#A6ABB5] group-hover:text-[#C9A13B]'
                          }`}
                        >
                          <Icon className="w-4 h-4" />
                        </div>
                        <div className="min-w-0">
                          <p className="text-xs font-semibold tracking-wide truncate group-hover:text-[#E2BE65] transition-colors">
                            {item.label}
                          </p>
                          <p className="text-[10px] text-[#A6ABB5] truncate hidden sm:block">
                            {item.desc}
                          </p>
                        </div>
                      </div>
                      <ArrowRight
                        className={`w-3.5 h-3.5 text-[#A6ABB5] group-hover:text-[#E2BE65] group-hover:translate-x-1 transition-all motion-reduce:transition-none ${
                          active ? 'text-[#E2BE65]' : 'opacity-0 group-hover:opacity-100'
                        }`}
                      />
                    </Link>
                  );
                })}
              </div>
            </div>
          </section>
        </div>
      </main>

      {/* ========================================================================= */}
      {/* PHASE 6: BOTTOM ACTION & REFINED FOOTER                                  */}
      {/* ========================================================================= */}
      <footer className="border-t border-[#232730] bg-[#111318]/90 py-5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4 text-xs">
          {/* Corporate Info */}
          <div className="flex flex-col sm:flex-row items-center gap-2 sm:gap-6 text-[#A6ABB5] text-center sm:text-left">
            <span className="font-serif font-bold text-[#F5F3EE]">Amit Hospitality LLP</span>
            <span className="hidden sm:inline text-[#232730]">•</span>
            <span>401 Kamalalaya Centre, 156A Lenin Sarani, Kolkata</span>
            <span className="hidden sm:inline text-[#232730]">•</span>
            <a href="tel:+919432335967" className="hover:text-[#E2BE65] transition-colors">
              +91 94323 35967
            </a>
          </div>

          {/* Quick Actions & Discreet Debug Toggle */}
          <div className="flex items-center gap-3">
            <Link
              to="/guest/reservations"
              onClick={onClose}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#171A20] border border-[#232730] hover:border-[#C9A13B]/40 text-[#F5F3EE] hover:text-[#E2BE65] text-xs font-medium transition"
            >
              <Calendar className="w-3.5 h-3.5 text-[#C9A13B]" />
              <span>Track Reservation</span>
            </Link>

            {/* Discreet Mode Indicator (Accessible for QA, not cluttering public header) */}
            <button
              onClick={() => {
                onClose();
                openSwitchModal(isDemo ? 'REAL' : 'DEMO');
              }}
              title={`Active Environment: ${environment}. Click to toggle demonstration mode.`}
              className="text-[10px] font-mono px-2 py-1 rounded bg-[#171A20] text-[#A6ABB5] hover:text-[#E2BE65] border border-[#232730] transition"
            >
              Env: <span className={isDemo ? 'text-amber-400' : 'text-emerald-400'}>{environment}</span>
            </button>
          </div>
        </div>
      </footer>
    </div>
  );

  return createPortal(content, document.body);
};
