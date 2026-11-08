import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  TrendingUp,
  MessageSquare,
  ThumbsUp,
  ThumbsDown,
  HelpCircle,
  Calendar,
  AlertCircle,
  Download,
  Filter,
  UsersRound,
  CheckCircle2,
  Clock,
  Layers,
  Utensils,
} from 'lucide-react';
import { useEnvironment } from '../../context/EnvironmentContext';
import { INITIAL_OUTLETS } from '../../utils/mockData';
import {
  fetchDashboardKPIs,
  exportAnalyticsSummaryCsv,
  DashboardKPIData,
} from '../../api/analytics';

export const AnalyticsPage: React.FC = () => {
  const { environment, isDemo } = useEnvironment();
  const [dateRange, setDateRange] = useState('7D');
  const [selectedOutlet, setSelectedOutlet] = useState('ALL');
  const [kpiData, setKpiData] = useState<DashboardKPIData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);

  const loadAnalytics = () => {
    setLoading(true);
    setError(null);
    const outletParam = selectedOutlet === 'ALL' ? undefined : Number(selectedOutlet);
    fetchDashboardKPIs({
      date_range: dateRange,
      outlet_id: outletParam,
      environment,
    })
      .then((data) => {
        setKpiData(data);
      })
      .catch((err) => {
        console.warn('Could not load live analytics:', err);
        setError('Failed to sync live analytics from server.');
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadAnalytics();
  }, [environment, dateRange, selectedOutlet]);

  const handleExportReport = async () => {
    try {
      setExporting(true);
      const outletParam = selectedOutlet === 'ALL' ? undefined : Number(selectedOutlet);
      const blob = await exportAnalyticsSummaryCsv({
        date_range: dateRange,
        outlet_id: outletParam,
        environment,
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `amit_hospitality_analytics_${environment.toLowerCase()}_${dateRange.toLowerCase()}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to export analytics report', err);
    } finally {
      setExporting(false);
    }
  };

  const topQueries = kpiData?.frequent_queries || [];
  const unansweredQuestions = kpiData?.unanswered_questions || [];
  const resBreakdown = kpiData?.reservation_status_breakdown || {};
  const leadBreakdown = kpiData?.lead_status_breakdown || {};

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[11px] font-mono uppercase tracking-wider text-gold-400 font-semibold">
              Business Intelligence & Analytics
            </span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-charcoal-800 text-slate-400 border border-slate-700">
              Scope: {environment}
            </span>
          </div>
          <h1 className="text-2xl font-serif font-bold text-white tracking-wide">
            Guest Engagement & Operations Analytics
          </h1>
          <p className="text-xs text-slate-400 mt-1 max-w-xl">
            Live database intelligence across customer concierge conversations, table reservations, banquet lead pipelines, and knowledge coverage.
          </p>
        </div>

        {/* Date Filter, Outlet Filter & Export */}
        <div className="flex flex-wrap items-center gap-2 self-start md:self-auto">
          {/* Outlet Filter */}
          <select
            value={selectedOutlet}
            onChange={(e) => setSelectedOutlet(e.target.value)}
            className="px-3 py-1.5 text-xs rounded-xl bg-charcoal-900 border border-slate-700 text-slate-300 focus:outline-none focus:border-gold-400"
          >
            <option value="ALL">All Outlets</option>
            {INITIAL_OUTLETS.map((o) => (
              <option key={o.id} value={o.id}>
                {o.name}
              </option>
            ))}
          </select>

          {/* Date Range Selector */}
          <div className="flex items-center p-1 rounded-xl bg-charcoal-900 border border-slate-700/80 text-xs">
            {['24H', '7D', '30D', 'ALL'].map((range) => (
              <button
                key={range}
                onClick={() => setDateRange(range)}
                className={`px-3 py-1 rounded-lg font-medium transition ${
                  dateRange === range
                    ? 'bg-gold-500/20 text-gold-300 font-semibold'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {range}
              </button>
            ))}
          </div>

          {/* Export Report Button */}
          <button
            onClick={handleExportReport}
            disabled={exporting}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-charcoal-800 hover:bg-charcoal-700 text-gold-300 border border-slate-700 text-xs font-medium transition disabled:opacity-50 shadow-sm"
            title="Download executive analytics CSV report"
          >
            <Download className="w-3.5 h-3.5" />
            <span>{exporting ? 'Exporting...' : 'Export Report'}</span>
          </button>
        </div>
      </div>

      {error && (
        <div className="p-3 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center justify-between">
          <span>{error}</span>
          <button onClick={loadAnalytics} className="underline text-rose-200 ml-2">
            Retry
          </button>
        </div>
      )}

      {/* Primary Analytics KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* 1. Guest Conversations */}
        <div className="p-5 rounded-2xl glass-panel border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs uppercase tracking-wider font-medium">Guest Inquiries</span>
            <div className="w-7 h-7 rounded-lg bg-gold-400/15 text-gold-400 flex items-center justify-center">
              <MessageSquare className="w-3.5 h-3.5" />
            </div>
          </div>
          <div className="text-2xl font-bold font-serif text-white">
            {loading ? '...' : (kpiData?.total_conversations ?? 0).toLocaleString('en-IN')}
          </div>
          <p className="text-[11px] text-slate-400 mt-1">
            Window: {dateRange} {selectedOutlet !== 'ALL' ? `• Outlet #${selectedOutlet}` : ''}
          </p>
        </div>

        {/* 2. Pending Reservations */}
        <div className="p-5 rounded-2xl glass-panel border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs uppercase tracking-wider font-medium">Pending Bookings</span>
            <div className="w-7 h-7 rounded-lg bg-amber-400/15 text-amber-400 flex items-center justify-center">
              <Calendar className="w-3.5 h-3.5" />
            </div>
          </div>
          <div className="text-2xl font-bold font-serif text-white">
            {loading ? '...' : kpiData?.pending_reservations ?? 0}
          </div>
          <p className="text-[11px] text-amber-300 mt-1">
            {kpiData?.total_covers ?? 0} covers expected
          </p>
        </div>

        {/* 3. Event & Banquet Leads */}
        <div className="p-5 rounded-2xl glass-panel border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs uppercase tracking-wider font-medium">Event Leads</span>
            <div className="w-7 h-7 rounded-lg bg-sky-400/15 text-sky-400 flex items-center justify-center">
              <TrendingUp className="w-3.5 h-3.5" />
            </div>
          </div>
          <div className="text-2xl font-bold font-serif text-white">
            {loading ? '...' : kpiData?.total_leads ?? 0}
          </div>
          <p className="text-[11px] text-emerald-400 mt-1">Banquets & private dining</p>
        </div>

        {/* 4. Active Knowledge Coverage */}
        <div className="p-5 rounded-2xl glass-panel border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs uppercase tracking-wider font-medium">Active Documents</span>
            <div className="w-7 h-7 rounded-lg bg-emerald-400/15 text-emerald-400 flex items-center justify-center">
              <Layers className="w-3.5 h-3.5" />
            </div>
          </div>
          <div className="text-2xl font-bold font-serif text-white">
            {loading ? '...' : kpiData?.active_documents ?? 0}
          </div>
          <p className="text-[11px] text-slate-400 mt-1">Indexed in {environment}</p>
        </div>
      </div>

      {/* Operational Breakdowns: Reservation Status & Lead Pipeline */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Reservation Status Distribution */}
        <div className="p-5 rounded-2xl glass-panel border border-slate-800 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <h3 className="font-serif font-bold text-sm text-white">
              Reservation Status Distribution
            </h3>
            <span className="text-[11px] text-slate-400 font-mono">
              Total Covers: {kpiData?.total_covers ?? 0}
            </span>
          </div>

          {Object.keys(resBreakdown).length > 0 ? (
            <div className="space-y-2 pt-1 text-xs">
              {Object.entries(resBreakdown).map(([status, count]) => {
                const total = Object.values(resBreakdown).reduce((a, b) => a + b, 0);
                const pct = total > 0 ? Math.round((count / total) * 100) : 0;
                return (
                  <div key={status} className="space-y-1">
                    <div className="flex justify-between text-slate-300">
                      <span className="font-mono text-[11px] uppercase">{status.replace('_', ' ')}</span>
                      <span className="font-mono font-semibold text-gold-300">{count} ({pct}%)</span>
                    </div>
                    <div className="w-full h-1.5 rounded-full bg-charcoal-800 overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          status === 'ACCEPTED'
                            ? 'bg-emerald-400'
                            : status === 'UNDER_REVIEW'
                            ? 'bg-sky-400'
                            : status === 'PENDING'
                            ? 'bg-amber-400'
                            : status === 'COMPLETED'
                            ? 'bg-teal-400'
                            : 'bg-slate-500'
                        }`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-slate-500 text-xs italic py-4">
              No reservation requests logged for the selected period.
            </p>
          )}
        </div>

        {/* Lead Pipeline Funnel */}
        <div className="p-5 rounded-2xl glass-panel border border-slate-800 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <h3 className="font-serif font-bold text-sm text-white">
              Event Leads Pipeline Funnel
            </h3>
            <span className="text-[11px] text-slate-400 font-mono">
              Total Inquiries: {kpiData?.total_leads ?? 0}
            </span>
          </div>

          {Object.keys(leadBreakdown).length > 0 ? (
            <div className="space-y-2 pt-1 text-xs">
              {Object.entries(leadBreakdown).map(([stage, count]) => {
                const total = Object.values(leadBreakdown).reduce((a, b) => a + b, 0);
                const pct = total > 0 ? Math.round((count / total) * 100) : 0;
                return (
                  <div key={stage} className="space-y-1">
                    <div className="flex justify-between text-slate-300">
                      <span className="font-mono text-[11px] uppercase">{stage.replace('_', ' ')}</span>
                      <span className="font-mono font-semibold text-gold-300">{count} ({pct}%)</span>
                    </div>
                    <div className="w-full h-1.5 rounded-full bg-charcoal-800 overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          stage === 'CONVERTED' || stage === 'WON'
                            ? 'bg-emerald-400'
                            : stage === 'QUALIFIED'
                            ? 'bg-gold-400'
                            : stage === 'FOLLOW_UP_REQUIRED'
                            ? 'bg-orange-400'
                            : 'bg-sky-400'
                        }`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-slate-500 text-xs italic py-4">
              No event or private dining leads logged for the selected period.
            </p>
          )}
        </div>
      </div>

      {/* Two Column Layout: Frequent Inquiries & Knowledge Gaps */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Most Frequent Customer Inquiries */}
        <div className="p-5 rounded-2xl glass-panel border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-serif font-bold text-base text-white">
              Top Frequent Guest Questions
            </h3>
            <span className="text-xs text-slate-400">Direct Message Analytics</span>
          </div>

          {topQueries.length > 0 ? (
            <div className="space-y-2.5">
              {topQueries.map((item, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-xl bg-charcoal-900/80 border border-slate-700/60 flex items-center justify-between text-xs"
                >
                  <div className="flex items-center gap-3">
                    <span className="w-5 h-5 rounded-full bg-charcoal-800 text-gold-400 font-mono text-[10px] flex items-center justify-center shrink-0">
                      {idx + 1}
                    </span>
                    <div>
                      <p className="font-medium text-slate-200">"{item.query}"</p>
                      <span className="text-[10px] text-slate-500 font-mono uppercase">
                        {item.category}
                      </span>
                    </div>
                  </div>
                  <span className="font-mono text-gold-400 font-semibold shrink-0">
                    {item.count} {item.count === 1 ? 'query' : 'queries'}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-8 text-center text-slate-500 text-xs">
              <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-40" />
              <p>No customer queries recorded for this time window.</p>
            </div>
          )}
        </div>

        {/* Unanswered Questions Spotlight (Actionable for Knowledge Expansion) */}
        <div className="p-5 rounded-2xl glass-panel border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-serif font-bold text-base text-white">
                Unanswered Questions & Missing Knowledge
              </h3>
              <p className="text-xs text-slate-400">
                Queries triggering grounded fallbacks or unindexed topics
              </p>
            </div>
          </div>

          {unansweredQuestions.length > 0 ? (
            <div className="space-y-2.5">
              {unansweredQuestions.map((q, idx) => (
                <div
                  key={idx}
                  className="p-3.5 rounded-xl bg-charcoal-900/90 border border-amber-500/30 text-xs space-y-2"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
                      <span className="font-semibold text-slate-200">"{q.question}"</span>
                    </div>
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-charcoal-800 text-amber-400 shrink-0">
                      {q.frequency}x asked
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-[11px] pt-1 border-t border-slate-800 text-slate-400">
                    <span>Outlet: {q.outlet}</span>
                    <span className="text-gold-300 font-medium">Recommended: {q.suggestion}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="py-8 text-center text-emerald-400/80 text-xs">
              <CheckCircle2 className="w-8 h-8 mx-auto mb-2 text-emerald-400 opacity-60" />
              <p>All inquiries in this period were successfully grounded in verified knowledge.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
