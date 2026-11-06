import React, { useState } from 'react';
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
} from 'lucide-react';
import { useEnvironment } from '../../context/EnvironmentContext';
import { INITIAL_OUTLETS } from '../../utils/mockData';

export const AnalyticsPage: React.FC = () => {
  const { environment, isDemo } = useEnvironment();
  const [dateRange, setDateRange] = useState('7D');
  const [selectedOutlet, setSelectedOutlet] = useState('ALL');

  const topQueries = [
    { query: 'Show me the signature chef tasting menu & prices', count: 342, category: 'MENU' },
    { query: 'What are dinner operating hours & valet parking policy?', count: 289, category: 'TIMING' },
    { query: 'Do you offer strictly Jain or vegan preparations?', count: 215, category: 'DIETARY' },
    { query: 'What is the dress code for dinner & weekend lounge?', count: 184, category: 'POLICY' },
    { query: 'Table reservation for wedding anniversary with skyline view', count: 167, category: 'BOOKING' },
    { query: 'Private dining room pricing for corporate executive dinner', count: 112, category: 'LEAD' },
  ];

  const unansweredQuestions = [
    {
      question: 'Do you allow outside birthday cakes and what is the plating fee?',
      frequency: 28,
      outlet: 'Amber Terrace Rooftop',
      suggestion: 'Upload Cake & External Food Policy doc',
    },
    {
      question: 'Are pets allowed in the outdoor garden terrace seating?',
      frequency: 19,
      outlet: 'Saffron & Silk',
      suggestion: 'Add Pet Policy FAQ',
    },
    {
      question: 'What is the corkage fee for vintage wine bottles brought by guests?',
      frequency: 14,
      outlet: 'The Velvet Cellar',
      suggestion: 'Index Sommelier Corkage Guidelines',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-[11px] font-mono uppercase tracking-wider text-gold-400 font-semibold">
              Business Intelligence
            </span>
          </div>
          <h1 className="text-2xl font-serif font-bold text-white tracking-wide">
            Guest Engagement & Inquiries Analytics
          </h1>
          <p className="text-xs text-slate-400 mt-1 max-w-xl">
            Real-time insights across customer concierge conversations, dietary preferences, peak inquiry hours, and knowledge gaps.
          </p>
        </div>

        {/* Date Filter */}
        <div className="flex items-center gap-2">
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
        </div>
      </div>

      {/* Primary Analytics KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl glass-panel border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs uppercase tracking-wider font-medium">Guest Inquiries</span>
            <MessageSquare className="w-4 h-4 text-gold-400" />
          </div>
          <div className="text-2xl font-bold font-serif text-white">1,482</div>
          <p className="text-[11px] text-emerald-400 mt-1 flex items-center gap-1">
            <TrendingUp className="w-3.5 h-3.5" /> +14.2% vs previous period
          </p>
        </div>

        <div className="p-5 rounded-2xl glass-panel border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs uppercase tracking-wider font-medium">Guest Satisfaction</span>
            <ThumbsUp className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold font-serif text-white">98.2%</div>
          <p className="text-[11px] text-slate-400 mt-1">Based on 642 guest ratings</p>
        </div>

        <div className="p-5 rounded-2xl glass-panel border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs uppercase tracking-wider font-medium">Booking Conversion</span>
            <Calendar className="w-4 h-4 text-gold-400" />
          </div>
          <div className="text-2xl font-bold font-serif text-white">24.6%</div>
          <p className="text-[11px] text-emerald-400 mt-1">Queries resulting in reservation requests</p>
        </div>

        <div className="p-5 rounded-2xl glass-panel border border-slate-800">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs uppercase tracking-wider font-medium">Knowledge Gaps</span>
            <HelpCircle className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold font-serif text-white">{unansweredQuestions.length}</div>
          <p className="text-[11px] text-amber-300 mt-1">Topics needing document indexing</p>
        </div>
      </div>

      {/* Two Column Layout: Frequent Inquiries & Outlet Interest */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Most Frequent Customer Inquiries */}
        <div className="p-5 rounded-2xl glass-panel border border-slate-800 space-y-4">
          <h3 className="font-serif font-bold text-base text-white">
            Most Frequent Guest Questions
          </h3>

          <div className="space-y-3">
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
                    <span className="text-[10px] text-slate-500 font-mono uppercase">{item.category}</span>
                  </div>
                </div>
                <span className="font-mono text-gold-400 font-semibold shrink-0">
                  {item.count} queries
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Unanswered Questions Spotlight (Actionable for Knowledge Expansion) */}
        <div className="p-5 rounded-2xl glass-panel border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-serif font-bold text-base text-white">
                Unanswered Questions & Missing Knowledge
              </h3>
              <p className="text-xs text-slate-400">
                Queries where AI grounded fallback was triggered
              </p>
            </div>
          </div>

          <div className="space-y-3">
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
                    {q.frequency} times asked
                  </span>
                </div>

                <div className="flex items-center justify-between text-[11px] pt-1 border-t border-slate-800 text-slate-400">
                  <span>Outlet: {q.outlet}</span>
                  <span className="text-gold-300 font-medium">Recommended: {q.suggestion}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
