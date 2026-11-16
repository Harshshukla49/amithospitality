import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import {
  Sparkles,
  Shield,
  Layers,
  User,
  ChevronDown,
  MessageSquare,
  LayoutDashboard,
  Calendar,
  Check,
  LogOut,
  Menu as MenuIcon,
  X as CloseIcon,
  Wine,
  Utensils,
  Coffee,
  ShoppingBag,
  ArrowRight,
} from 'lucide-react';
import { useEnvironment } from '../../context/EnvironmentContext';
import { useAuth } from '../../context/AuthContext';
import { useChat } from '../../context/ChatContext';
import { UserRole } from '../../types';

interface HeaderProps {
  currentView?: 'CUSTOMER' | 'ADMIN';
  onViewChange?: (view: 'CUSTOMER' | 'ADMIN') => void;
}

export const Header: React.FC<HeaderProps> = ({ currentView, onViewChange }) => {
  const { environment, isDemo, openSwitchModal } = useEnvironment();
  const { user, switchRole, logout, isAuthenticated } = useAuth();
  const { language, setLanguage } = useChat();

  const [brandsDropdownOpen, setBrandsDropdownOpen] = useState(false);
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const brandsRef = useRef<HTMLDivElement>(null);
  const profileRef = useRef<HTMLDivElement>(null);

  const navigate = useNavigate();
  const location = useLocation();

  const isAdminRoute = location.pathname.startsWith('/admin');
  const activeView = currentView || (isAdminRoute ? 'ADMIN' : 'CUSTOMER');

  // Close dropdowns on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (brandsRef.current && !brandsRef.current.contains(event.target as Node)) {
        setBrandsDropdownOpen(false);
      }
      if (profileRef.current && !profileRef.current.contains(event.target as Node)) {
        setProfileDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false);
    setBrandsDropdownOpen(false);
  }, [location.pathname]);

  const roles: { role: UserRole; label: string }[] = [
    { role: 'SUPER_ADMIN', label: 'Super Admin (Full Access)' },
    { role: 'ADMIN', label: 'General Manager / Admin' },
    { role: 'MANAGER', label: 'F&B Outlet Manager' },
    { role: 'STAFF', label: 'Front Desk Hostess' },
  ];

  const handleNavigateView = (view: 'CUSTOMER' | 'ADMIN') => {
    if (view === 'CUSTOMER') {
      navigate('/concierge');
    } else {
      navigate('/admin/dashboard');
    }
    if (onViewChange) {
      onViewChange(view);
    }
  };

  const handleLogout = () => {
    logout();
    setProfileDropdownOpen(false);
    navigate('/login');
  };

  const brandsList = [
    {
      name: 'Lord of the Drinks',
      sub: 'Lounge, Bar & Nightlife',
      path: '/brands/lord-of-drinks',
      location: '4th Floor, South City Mall',
      icon: Wine,
      color: 'text-amber-400',
    },
    {
      name: 'Veneto Kitchen & Bar',
      sub: 'Artisanal Italian & Mediterranean',
      path: '/brands/veneto',
      location: '4th Floor, South City Mall',
      icon: Utensils,
      color: 'text-emerald-400',
    },
    {
      name: 'The Warehouse Cafe',
      sub: 'Urban Industrial Cafe & Sunday Brunch',
      path: '/brands/warehouse',
      location: '4th Floor, South City Mall',
      icon: Coffee,
      color: 'text-rose-400',
    },
    {
      name: 'Deliite',
      sub: 'Boutique Liquor & Beverage Retail',
      path: '/brands/deliite',
      location: '3rd Floor, Diamond Plaza Mall',
      icon: ShoppingBag,
      color: 'text-purple-400',
    },
  ];

  const navLinks = [
    { label: 'Home', path: '/' },
    { label: 'Know Us', path: '/about' },
    { label: 'Digital Menus', path: '/menus' },
    { label: 'Events', path: '/events' },
    { label: 'Gallery', path: '/media' },
    { label: 'Careers', path: '/career' },
    { label: 'Enquiry', path: '/enquiry' },
    { label: 'Contact', path: '/contact' },
  ];

  const isCurrentActive = (path: string) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-gold-400/20 bg-obsidian-950/95 backdrop-blur-md transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between gap-3">
        {/* Brand Group Insignia */}
        <Link to="/" className="flex items-center gap-3 shrink-0 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-gold-400 to-gold-600 flex items-center justify-center shadow-gold-glow group-hover:scale-105 transition-transform">
            <Sparkles className="w-5 h-5 text-obsidian-950" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-serif font-bold text-lg sm:text-xl tracking-wider text-white group-hover:text-gold-200 transition-colors">
                AMIT HOSPITALITY
              </span>
              <span className="hidden lg:inline-block text-[9px] tracking-widest font-mono uppercase px-1.5 py-0.5 rounded bg-gold-400/15 text-gold-400 border border-gold-400/30">
                LLP • ESTD 2018
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-sans tracking-wide hidden sm:block">
              Distinctive Dining &amp; Experiential Hospitality
            </p>
          </div>
        </Link>

        {/* Desktop Primary Navigation */}
        <nav className="hidden xl:flex items-center gap-1.5 text-xs font-medium text-slate-300">
          <Link
            to="/"
            className={`px-3 py-2 rounded-lg transition ${
              isCurrentActive('/') && location.pathname === '/'
                ? 'text-gold-300 font-semibold bg-charcoal-800/60'
                : 'hover:text-white hover:bg-charcoal-800/40'
            }`}
          >
            Home
          </Link>

          {/* Brands Mega Dropdown */}
          <div className="relative" ref={brandsRef}>
            <button
              onClick={() => setBrandsDropdownOpen(!brandsDropdownOpen)}
              className={`flex items-center gap-1 px-3 py-2 rounded-lg transition ${
                location.pathname.startsWith('/brands')
                  ? 'text-gold-300 font-semibold bg-charcoal-800/60'
                  : 'hover:text-white hover:bg-charcoal-800/40'
              }`}
            >
              <span>Our Brands</span>
              <ChevronDown
                className={`w-3.5 h-3.5 transition-transform duration-200 ${
                  brandsDropdownOpen ? 'rotate-180 text-gold-400' : 'text-slate-400'
                }`}
              />
            </button>

            {brandsDropdownOpen && (
              <div className="absolute top-full left-0 mt-2 w-80 rounded-2xl bg-charcoal-900/95 border border-gold-400/30 shadow-2xl p-3 backdrop-blur-xl animate-fade-in z-50">
                <div className="px-3 py-2 border-b border-slate-800 text-[10px] font-mono uppercase tracking-widest text-gold-400 font-semibold">
                  Portfolio Destinations
                </div>
                <div className="space-y-1 pt-2">
                  {brandsList.map((brand) => {
                    const IconComp = brand.icon;
                    return (
                      <Link
                        key={brand.name}
                        to={brand.path}
                        onClick={() => setBrandsDropdownOpen(false)}
                        className="flex items-start gap-3 p-2.5 rounded-xl hover:bg-charcoal-800/80 transition group"
                      >
                        <div className={`p-2 rounded-lg bg-charcoal-950 border border-slate-800 ${brand.color}`}>
                          <IconComp className="w-4 h-4" />
                        </div>
                        <div className="flex-1">
                          <p className="font-semibold text-white group-hover:text-gold-300 transition-colors text-xs">
                            {brand.name}
                          </p>
                          <p className="text-[11px] text-slate-400">{brand.sub}</p>
                          <p className="text-[10px] text-slate-500 font-mono mt-0.5">{brand.location}</p>
                        </div>
                      </Link>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          <Link
            to="/about"
            className={`px-3 py-2 rounded-lg transition ${
              isCurrentActive('/about') ? 'text-gold-300 font-semibold bg-charcoal-800/60' : 'hover:text-white hover:bg-charcoal-800/40'
            }`}
          >
            Know Us
          </Link>
          <Link
            to="/menus"
            className={`px-3 py-2 rounded-lg transition ${
              isCurrentActive('/menus') ? 'text-gold-300 font-semibold bg-charcoal-800/60' : 'hover:text-white hover:bg-charcoal-800/40'
            }`}
          >
            Menus
          </Link>
          <Link
            to="/events"
            className={`px-3 py-2 rounded-lg transition ${
              isCurrentActive('/events') ? 'text-gold-300 font-semibold bg-charcoal-800/60' : 'hover:text-white hover:bg-charcoal-800/40'
            }`}
          >
            Events
          </Link>
          <Link
            to="/media"
            className={`px-3 py-2 rounded-lg transition ${
              isCurrentActive('/media') ? 'text-gold-300 font-semibold bg-charcoal-800/60' : 'hover:text-white hover:bg-charcoal-800/40'
            }`}
          >
            Gallery
          </Link>
          <Link
            to="/career"
            className={`px-3 py-2 rounded-lg transition ${
              isCurrentActive('/career') ? 'text-gold-300 font-semibold bg-charcoal-800/60' : 'hover:text-white hover:bg-charcoal-800/40'
            }`}
          >
            Careers
          </Link>
          <Link
            to="/enquiry"
            className={`px-3 py-2 rounded-lg transition ${
              isCurrentActive('/enquiry') ? 'text-gold-300 font-semibold bg-charcoal-800/60' : 'hover:text-white hover:bg-charcoal-800/40'
            }`}
          >
            Enquiry
          </Link>
          <Link
            to="/contact"
            className={`px-3 py-2 rounded-lg transition ${
              isCurrentActive('/contact') ? 'text-gold-300 font-semibold bg-charcoal-800/60' : 'hover:text-white hover:bg-charcoal-800/40'
            }`}
          >
            Contact
          </Link>
        </nav>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          {/* AI Concierge Pill */}
          <Link
            to="/concierge"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 font-bold text-xs shadow-gold-glow hover:brightness-110 transition shrink-0"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">AI Concierge</span>
          </Link>

          {/* Guest Booking Lookup */}
          <Link
            to="/guest/reservations"
            title="Track or modify an existing table reservation"
            className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-charcoal-900 border border-slate-700 text-slate-200 hover:border-gold-400 text-xs font-medium transition"
          >
            <Calendar className="w-3.5 h-3.5 text-gold-400" />
            <span>My Booking</span>
          </Link>

          {/* Environment Mode Toggle */}
          <button
            onClick={() => openSwitchModal(isDemo ? 'REAL' : 'DEMO')}
            title="Click to toggle between DEMO demonstration content and REAL verified database records"
            className={`hidden sm:flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-[11px] font-semibold border transition ${
              isDemo
                ? 'bg-amber-500/15 text-gold-300 border-gold-400/40 hover:bg-amber-500/25'
                : 'bg-emerald-500/15 text-emerald-300 border-emerald-400/40 hover:bg-emerald-500/25'
            }`}
          >
            <span className={`w-1.5 h-1.5 rounded-full ${isDemo ? 'bg-gold-400 animate-pulse' : 'bg-emerald-400'}`} />
            <span className="font-mono">{environment}</span>
          </button>

          {/* Staff / Admin Console Link */}
          {isAuthenticated ? (
            <div className="relative" ref={profileRef}>
              <button
                onClick={() => setProfileDropdownOpen(!profileDropdownOpen)}
                className="flex items-center gap-1.5 p-1.5 sm:px-3 sm:py-1.5 rounded-xl bg-charcoal-800 border border-gold-400/40 text-gold-300 text-xs font-medium hover:bg-charcoal-700 transition"
              >
                <Shield className="w-3.5 h-3.5 text-gold-400" />
                <span className="hidden lg:inline">{user?.fullName || 'Staff Console'}</span>
                <ChevronDown className="w-3 h-3 text-slate-400" />
              </button>

              {profileDropdownOpen && (
                <div className="absolute right-0 mt-2 w-64 rounded-xl bg-charcoal-900 border border-slate-700 shadow-2xl p-2 z-50 animate-fade-in">
                  <div className="px-3 py-2 border-b border-slate-800">
                    <p className="text-xs font-bold text-white">{user?.fullName}</p>
                    <p className="text-[10px] font-mono text-gold-400">{user?.role}</p>
                  </div>
                  <div className="py-1">
                    <Link
                      to="/admin/dashboard"
                      onClick={() => setProfileDropdownOpen(false)}
                      className="flex items-center gap-2 px-3 py-2 text-xs text-slate-300 hover:bg-charcoal-800 rounded-lg transition"
                    >
                      <LayoutDashboard className="w-4 h-4 text-gold-400" />
                      <span>Admin Dashboard</span>
                    </Link>
                  </div>
                  <div className="border-t border-slate-800 pt-1">
                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center gap-2 px-3 py-2 text-xs text-rose-400 hover:bg-rose-950/40 rounded-lg transition"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Sign Out</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <Link
              to="/login"
              title="Staff & Management Portal"
              className="p-2 rounded-xl text-slate-400 hover:text-gold-300 hover:bg-charcoal-800/80 transition"
            >
              <User className="w-4 h-4" />
            </Link>
          )}

          {/* Mobile Menu Toggle Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="xl:hidden p-2 rounded-xl text-slate-300 hover:text-white hover:bg-charcoal-800 transition"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <CloseIcon className="w-6 h-6" /> : <MenuIcon className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Navigation Drawer */}
      {mobileMenuOpen && (
        <div className="xl:hidden bg-charcoal-950/98 border-b border-slate-800 px-4 pt-3 pb-6 space-y-4 animate-fade-in">
          {/* Brand Links Grid */}
          <div className="bg-charcoal-900 rounded-2xl p-3 border border-slate-800">
            <p className="text-[10px] font-mono uppercase tracking-widest text-gold-400 font-semibold mb-2 px-1">
              Our Brands
            </p>
            <div className="grid grid-cols-2 gap-2">
              {brandsList.map((brand) => (
                <Link
                  key={brand.name}
                  to={brand.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className="flex items-center gap-2 p-2 rounded-xl bg-charcoal-950 border border-slate-800 hover:border-gold-400/50 transition"
                >
                  <brand.icon className={`w-4 h-4 ${brand.color} shrink-0`} />
                  <span className="text-xs font-semibold text-white truncate">{brand.name}</span>
                </Link>
              ))}
            </div>
          </div>

          {/* Nav List */}
          <div className="grid grid-cols-2 gap-2 text-xs">
            {navLinks.map((link) => (
              <Link
                key={link.label}
                to={link.path}
                onClick={() => setMobileMenuOpen(false)}
                className={`px-3 py-2 rounded-xl border transition ${
                  isCurrentActive(link.path)
                    ? 'bg-charcoal-800 text-gold-300 border-gold-400/40 font-semibold'
                    : 'bg-charcoal-900/50 text-slate-300 border-slate-800 hover:text-white'
                }`}
              >
                {link.label}
              </Link>
            ))}
          </div>

          {/* Quick Actions */}
          <div className="flex items-center gap-2 pt-2 border-t border-slate-800">
            <Link
              to="/guest/reservations"
              onClick={() => setMobileMenuOpen(false)}
              className="flex-1 text-center py-2 rounded-xl bg-charcoal-800 text-slate-200 text-xs font-medium border border-slate-700"
            >
              My Booking
            </Link>
            <button
              onClick={() => {
                setMobileMenuOpen(false);
                openSwitchModal(isDemo ? 'REAL' : 'DEMO');
              }}
              className="flex-1 py-2 rounded-xl bg-charcoal-800 text-gold-300 text-xs font-mono border border-gold-400/30"
            >
              Mode: {environment}
            </button>
          </div>
        </div>
      )}
    </header>
  );
};
