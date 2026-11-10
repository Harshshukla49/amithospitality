import React, { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import {
  Sparkles,
  Shield,
  Layers,
  User,
  ChevronDown,
  Globe,
  MessageSquare,
  LayoutDashboard,
  Check,
  LogOut,
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
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const isAdminRoute = location.pathname.startsWith('/admin');
  const activeView = currentView || (isAdminRoute ? 'ADMIN' : 'CUSTOMER');

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

  return (
    <header className="sticky top-0 z-40 w-full border-b border-gold-400/20 bg-obsidian-950/90 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Brand Logo & Name */}
        <Link to="/concierge" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-gold-400 to-gold-600 flex items-center justify-center shadow-gold-glow group-hover:scale-105 transition-transform">
            <Sparkles className="w-5 h-5 text-obsidian-950" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-serif font-bold text-lg tracking-wide text-white group-hover:text-gold-200 transition-colors">
                AMIT HOSPITALITY
              </span>
              <span className="hidden sm:inline-block text-[10px] tracking-widest font-semibold px-1.5 py-0.5 rounded bg-gold-400/15 text-gold-400 border border-gold-400/30">
                AI CONCIERGE
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-sans tracking-wider hidden md:block">
              Luxury Dining & Private Event Experience Platform
            </p>
          </div>
        </Link>

        {/* View Switcher: Customer Concierge vs Admin Console */}
        <div className="hidden sm:flex items-center p-1 rounded-xl bg-charcoal-900 border border-slate-700/80">
          <button
            onClick={() => handleNavigateView('CUSTOMER')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition ${
              activeView === 'CUSTOMER'
                ? 'bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 font-semibold shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>Customer Concierge</span>
          </button>
          <button
            onClick={() => handleNavigateView('ADMIN')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition ${
              activeView === 'ADMIN'
                ? 'bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 font-semibold shadow-sm'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <LayoutDashboard className="w-3.5 h-3.5" />
            <span>Admin Console</span>
          </button>
        </div>

        {/* Action Controls: Environment Pill, Language, Profile */}
        <div className="flex items-center gap-2.5">
          {/* Environment Mode Indicator & Quick Switch */}
          <button
            onClick={() => openSwitchModal(isDemo ? 'REAL' : 'DEMO')}
            title="Click to toggle between DEMO sample data and REAL verified knowledge"
            className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold border transition ${
              isDemo
                ? 'bg-amber-500/15 text-gold-300 border-gold-400/40 hover:bg-amber-500/25 shadow-sm'
                : 'bg-emerald-500/15 text-emerald-300 border-emerald-400/40 hover:bg-emerald-500/25'
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full ${
                isDemo ? 'bg-gold-400 animate-pulse' : 'bg-emerald-400'
              }`}
            />
            <span className="tracking-wide uppercase font-mono">{environment} MODE</span>
            <Layers className="w-3 h-3 text-slate-400" />
          </button>

          {/* Language Toggle (EN / HI) */}
          <div className="flex items-center bg-charcoal-900 border border-slate-700/80 rounded-lg p-0.5 text-xs">
            <button
              onClick={() => setLanguage('EN')}
              className={`px-2 py-1 rounded font-medium transition ${
                language === 'EN'
                  ? 'bg-gold-500/20 text-gold-300 font-semibold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              EN
            </button>
            <button
              onClick={() => setLanguage('HI')}
              className={`px-2 py-1 rounded font-medium transition ${
                language === 'HI'
                  ? 'bg-gold-500/20 text-gold-300 font-semibold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              हिं
            </button>
          </div>

          {/* Profile / Role Selector Dropdown */}
          <div className="relative">
            {isAuthenticated && user ? (
              <button
                onClick={() => setProfileDropdownOpen(!profileDropdownOpen)}
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-charcoal-900 border border-slate-700/80 hover:border-gold-400/40 text-xs text-slate-200 transition"
              >
                <div className="w-5 h-5 rounded-full bg-gold-400/20 flex items-center justify-center text-gold-400 font-semibold">
                  {user.fullName.charAt(0) || 'A'}
                </div>
                <span className="hidden md:inline-block max-w-[100px] truncate">{user.fullName}</span>
                <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
              </button>
            ) : (
              <Link
                to="/login"
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gold-500/20 border border-gold-400/40 text-gold-300 text-xs font-semibold hover:bg-gold-500/30 transition"
              >
                <User className="w-3.5 h-3.5" />
                <span>Sign In</span>
              </Link>
            )}

            {profileDropdownOpen && user && (
              <div className="absolute right-0 mt-2 w-64 rounded-xl glass-panel-elevated p-2 shadow-luxury border border-gold-400/30 text-xs z-50 animate-fade-in">
                <div className="p-2 border-b border-slate-700 mb-1">
                  <p className="font-semibold text-white">{user.fullName}</p>
                  <p className="text-[11px] text-gold-400 font-mono">{user.role}</p>
                  <p className="text-[11px] text-slate-400 truncate">{user.email}</p>
                </div>

                <div className="py-1">
                  <p className="px-2 py-1 text-[10px] uppercase tracking-wider text-slate-400 font-semibold">
                    Simulate Role (Testing):
                  </p>
                  {roles.map((r) => (
                    <button
                      key={r.role}
                      onClick={() => {
                        switchRole(r.role);
                        setProfileDropdownOpen(false);
                      }}
                      className={`w-full flex items-center justify-between px-2 py-1.5 rounded text-left transition ${
                        user.role === r.role
                          ? 'bg-gold-500/20 text-gold-300 font-medium'
                          : 'text-slate-300 hover:bg-charcoal-800'
                      }`}
                    >
                      <span>{r.label}</span>
                      {user.role === r.role && <Check className="w-3.5 h-3.5 text-gold-400" />}
                    </button>
                  ))}
                </div>

                {/* Sign Out Button */}
                <div className="pt-1 border-t border-slate-700 mt-1">
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center gap-2 px-2 py-1.5 rounded text-left text-rose-400 hover:bg-rose-950/40 transition"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                    <span>Sign Out</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
