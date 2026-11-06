import React from 'react';
import {
  LayoutDashboard,
  BookOpen,
  UtensilsCrossed,
  CalendarCheck,
  UsersRound,
  BarChart3,
  Sliders,
  Shield,
  Layers,
} from 'lucide-react';
import { useEnvironment } from '../../context/EnvironmentContext';

export type AdminTab =
  | 'DASHBOARD'
  | 'KNOWLEDGE'
  | 'OUTLETS'
  | 'RESERVATIONS'
  | 'LEADS'
  | 'ANALYTICS'
  | 'SETTINGS';

interface SidebarProps {
  activeTab: AdminTab;
  onTabChange: (tab: AdminTab) => void;
  reservationCount?: number;
  leadCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onTabChange,
  reservationCount = 0,
  leadCount = 0,
}) => {
  const { environment, isDemo, openSwitchModal } = useEnvironment();

  const navItems: { id: AdminTab; label: string; icon: React.ReactNode; badge?: number }[] = [
    {
      id: 'DASHBOARD',
      label: 'Overview & KPIs',
      icon: <LayoutDashboard className="w-4 h-4" />,
    },
    {
      id: 'KNOWLEDGE',
      label: 'Knowledge Studio',
      icon: <BookOpen className="w-4 h-4" />,
    },
    {
      id: 'OUTLETS',
      label: 'Outlets & Menus',
      icon: <UtensilsCrossed className="w-4 h-4" />,
    },
    {
      id: 'RESERVATIONS',
      label: 'Reservations',
      icon: <CalendarCheck className="w-4 h-4" />,
      badge: reservationCount,
    },
    {
      id: 'LEADS',
      label: 'Events & Leads',
      icon: <UsersRound className="w-4 h-4" />,
      badge: leadCount,
    },
    {
      id: 'ANALYTICS',
      label: 'Analytics & Insights',
      icon: <BarChart3 className="w-4 h-4" />,
    },
    {
      id: 'SETTINGS',
      label: 'Settings & Audit Log',
      icon: <Sliders className="w-4 h-4" />,
    },
  ];

  return (
    <aside className="w-64 shrink-0 flex flex-col justify-between p-4 glass-panel border-r border-gold-400/20 h-[calc(100vh-4rem)]">
      <div className="space-y-4">
        {/* Environment Status Card in Sidebar */}
        <div
          onClick={() => openSwitchModal(isDemo ? 'REAL' : 'DEMO')}
          className="p-3 rounded-xl bg-charcoal-900 border border-slate-700/80 hover:border-gold-400/50 cursor-pointer transition group"
        >
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400">Knowledge Scope</span>
            <span
              className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold tracking-wider ${
                isDemo
                  ? 'bg-amber-500/20 text-gold-300 border border-gold-400/40'
                  : 'bg-emerald-500/20 text-emerald-300 border border-emerald-400/40'
              }`}
            >
              {environment}
            </span>
          </div>
          <p className="text-[11px] text-slate-300 mt-1.5 font-medium group-hover:text-gold-300 transition flex items-center justify-between">
            <span>{isDemo ? 'Fictional Sample Data' : 'Verified Company Data'}</span>
            <Layers className="w-3.5 h-3.5 text-slate-500 group-hover:text-gold-400" />
          </p>
        </div>

        {/* Navigation Links */}
        <nav className="space-y-1">
          {navItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onTabChange(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium transition ${
                  isActive
                    ? 'bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 font-semibold shadow-gold-glow'
                    : 'text-slate-300 hover:text-white hover:bg-charcoal-800'
                }`}
              >
                <div className="flex items-center gap-2.5">
                  {item.icon}
                  <span>{item.label}</span>
                </div>
                {item.badge !== undefined && item.badge > 0 && (
                  <span
                    className={`px-1.5 py-0.5 rounded-full text-[10px] font-bold ${
                      isActive ? 'bg-obsidian-950 text-gold-300' : 'bg-gold-500/20 text-gold-400'
                    }`}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Security & System Info Footer */}
      <div className="pt-3 border-t border-slate-800 text-[11px] text-slate-500 flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <Shield className="w-3.5 h-3.5 text-gold-400" />
          <span>RBAC Protected</span>
        </div>
        <span className="font-mono text-[10px]">v1.0.0</span>
      </div>
    </aside>
  );
};
