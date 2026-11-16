import React from 'react';
import { Link } from 'react-router-dom';
import {
  Sparkles,
  MapPin,
  Clock,
  Award,
  Users,
  Compass,
  CheckCircle2,
  Calendar,
  ArrowRight,
  ShieldCheck,
  Building,
} from 'lucide-react';
import { COMPANY_PROFILE } from '../../utils/mockData';

export const AboutPage: React.FC = () => {
  const timelineMilestones = [
    {
      year: '2018',
      title: 'Inception of Amit Hospitality LLP',
      subtitle: 'Corporate Foundation',
      desc: 'Founded by Amit Bajoria and Vanita Bajoria in Kolkata with a mission to bring world-class experiential dining and visionary F&B concepts to Eastern India.',
      badge: 'Foundation',
    },
    {
      year: 'Dec 2019',
      title: 'Lord of the Drinks Kolkata Opens',
      subtitle: '4th Floor, South City Mall',
      desc: "Introduced Kolkata's tallest bar to southern Kolkata, featuring dramatic medieval European castle architecture, progressive mixology, and the iconic Ghost Bar.",
      badge: 'Brand Launch',
    },
    {
      year: '2021',
      title: 'Veneto Kitchen and Bar Established',
      subtitle: '4th Floor, South City Mall',
      desc: 'Unveiled an artisanal Italian kitchen and cocktail bar, bringing wood-fired Neapolitan pizzas, hand-rolled pasta, and Mediterranean culinary warmth to South City Mall.',
      badge: 'Culinary Expansion',
    },
    {
      year: 'June 2022',
      title: 'The Warehouse Cafe Opens',
      subtitle: '4th Floor, South City Mall',
      desc: 'Launched an urban industrial café and lounge concept, celebrating chef-created global comfort food, weekend live acoustics, and the popular Sunday Brunch.',
      badge: 'Lifestyle Lounge',
    },
    {
      year: '2023',
      title: 'Deliite Lifestyle Retail Launch',
      subtitle: '3rd Floor, Diamond Plaza Mall',
      desc: "Expanded into premium lifestyle beverage retail, opening Kolkata's premier boutique for curated domestic and international spirits, craft brews, and gourmet refreshments.",
      badge: 'Retail Innovation',
    },
    {
      year: '2026',
      title: 'Digital Concierge & Unified CRM',
      subtitle: 'Technological Excellence',
      desc: 'Pioneered conversational AI concierge technology and unified guest CRM self-service across all outlets, setting a new benchmark for guest convenience in hospitality.',
      badge: 'AI Innovation',
    },
  ];

  return (
    <div className="min-h-screen bg-obsidian-950 text-slate-100 font-sans pb-20">
      {/* 1. EDITORIAL HERO HEADER */}
      <section className="relative py-24 px-4 sm:px-6 lg:px-8 border-b border-slate-800/80 bg-gradient-to-b from-charcoal-900 via-obsidian-950 to-obsidian-950">
        <div className="max-w-4xl mx-auto text-center space-y-4">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-charcoal-900 border border-gold-400/40 text-gold-300 text-xs font-mono uppercase tracking-widest">
            <Sparkles className="w-3.5 h-3.5 text-gold-400" />
            <span>Know Us • Company Profile</span>
          </div>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-serif font-bold text-white tracking-tight">
            The Amit Hospitality Story
          </h1>
          <p className="text-base sm:text-lg text-slate-300 font-light max-w-2xl mx-auto leading-relaxed">
            Crafting memorable food, beverage, and experiential entertainment destinations across Kolkata since 2018.
          </p>
        </div>
      </section>

      {/* 2. CORPORATE ESSENCE & LEADERSHIP */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
          {/* Main Narrative (7 cols) */}
          <div className="lg:col-span-7 space-y-6">
            <span className="text-xs font-mono font-bold uppercase tracking-widest text-gold-400">
              Who We Are
            </span>
            <h2 className="text-3xl font-serif font-bold text-white leading-tight">
              An Enduring Commitment to Culinary Innovation and Gracious Hospitality
            </h2>

            <div className="space-y-4 text-sm text-slate-300 leading-relaxed font-light">
              <p>
                <strong>Amit Hospitality LLP</strong> is a distinguished hospitality group registered in Kolkata, India. Established in <strong>2018</strong> by entrepreneurs <strong>Amit Bajoria</strong> and <strong>Vanita Bajoria</strong>, the enterprise was created to introduce distinctive dining and nightlife concepts designed around sensory storytelling, architectural drama, and heartfelt service.
              </p>
              <p>
                Operating across premier commercial destinations—including the 4th Floor of <strong>South City Mall</strong> and the 3rd Floor of <strong>Diamond Plaza Mall</strong>—our portfolio represents the diversity of contemporary Indian hospitality. We believe that restaurants are not merely places to eat; they are social cultural hubs where people celebrate life’s milestones.
              </p>
            </div>

            {/* Core Pillars */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-4">
              <div className="p-4 rounded-2xl bg-charcoal-900 border border-slate-800">
                <Compass className="w-5 h-5 text-gold-400 mb-2" />
                <h4 className="text-sm font-serif font-bold text-white">Curated Spaces</h4>
                <p className="text-xs text-slate-400 mt-1">
                  Bespoke interior architecture from medieval castles to industrial lofts.
                </p>
              </div>
              <div className="p-4 rounded-2xl bg-charcoal-900 border border-slate-800">
                <Award className="w-5 h-5 text-gold-400 mb-2" />
                <h4 className="text-sm font-serif font-bold text-white">Culinary Passion</h4>
                <p className="text-xs text-slate-400 mt-1">
                  Wood-fired ovens, hand-rolled pasta, clay tandoors, and crafted cocktails.
                </p>
              </div>
              <div className="p-4 rounded-2xl bg-charcoal-900 border border-slate-800">
                <Users className="w-5 h-5 text-gold-400 mb-2" />
                <h4 className="text-sm font-serif font-bold text-white">Guest Focus</h4>
                <p className="text-xs text-slate-400 mt-1">
                  Personalized service touchpoints powered by modern AI and attentive front desk hosts.
                </p>
              </div>
            </div>
          </div>

          {/* Leadership & Corporate Information Card (5 cols) */}
          <div className="lg:col-span-5 rounded-3xl bg-charcoal-900/80 border border-gold-400/30 p-8 space-y-6 shadow-2xl backdrop-blur-md">
            <div>
              <span className="text-xs font-mono uppercase tracking-widest text-gold-400 font-semibold">
                Founding Leadership
              </span>
              <h3 className="text-2xl font-serif font-bold text-white mt-1">
                Amit &amp; Vanita Bajoria
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Founders &amp; Managing Partners • Amit Hospitality LLP
              </p>
            </div>

            <div className="space-y-4 pt-4 border-t border-slate-800 text-xs text-slate-300">
              <div className="space-y-1">
                <p className="font-semibold text-white">Philosophy:</p>
                <p className="text-slate-400 italic">
                  "{COMPANY_PROFILE.mission}"
                </p>
              </div>
              <div className="space-y-1">
                <p className="font-semibold text-white">Vision:</p>
                <p className="text-slate-400">
                  {COMPANY_PROFILE.vision}
                </p>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-charcoal-950 border border-slate-800 text-xs space-y-2">
              <div className="flex items-center gap-2 text-gold-300 font-semibold">
                <Building className="w-4 h-4 text-gold-400 shrink-0" />
                <span>Corporate Registration</span>
              </div>
              <p className="text-[11px] text-slate-400">
                Amit Hospitality LLP<br />
                401 Kamalalaya Centre, 156A Lenin Sarani, Kolkata - 700013
              </p>
              <p className="text-[11px] text-slate-400">
                Phone: +91 94323 35967 • Email: vanita@amithospitality.com
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 3. VISUAL COMPANY TIMELINE (2018 - 2026) */}
      <section className="py-20 bg-charcoal-900/40 border-t border-slate-800 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto space-y-12">
          <div className="text-center space-y-3">
            <span className="text-xs font-mono uppercase tracking-widest text-gold-400 font-semibold">
              The Journey
            </span>
            <h2 className="text-3xl font-serif font-bold text-white">
              Company Milestone Timeline
            </h2>
            <p className="text-xs text-slate-400 max-w-xl mx-auto">
              Key moments in the evolution of Amit Hospitality LLP from our founding in 2018 to our current multi-brand presence.
            </p>
          </div>

          <div className="relative border-l-2 border-gold-400/30 ml-4 sm:ml-8 space-y-10 pl-6 sm:pl-10">
            {timelineMilestones.map((milestone, idx) => (
              <div key={idx} className="relative group">
                {/* Node Dot */}
                <div className="absolute -left-[31px] sm:-left-[47px] top-1.5 w-4 h-4 rounded-full bg-obsidian-950 border-2 border-gold-400 group-hover:scale-125 transition-transform" />

                <div className="p-6 rounded-2xl bg-charcoal-900 border border-slate-800 group-hover:border-gold-400/40 transition shadow-lg space-y-2">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="font-mono text-sm font-bold text-gold-400">
                      {milestone.year}
                    </span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold uppercase bg-charcoal-950 text-slate-300 border border-slate-800">
                      {milestone.badge}
                    </span>
                  </div>
                  <h3 className="text-lg font-serif font-bold text-white group-hover:text-gold-200 transition-colors">
                    {milestone.title}
                  </h3>
                  <p className="text-xs text-gold-400/80 font-mono">
                    {milestone.subtitle}
                  </p>
                  <p className="text-xs text-slate-300 leading-relaxed pt-1">
                    {milestone.desc}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 4. HOSPITALITY APPROACH & VALUES */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="text-center max-w-3xl mx-auto space-y-3 mb-12">
          <span className="text-xs font-mono uppercase tracking-widest text-gold-400 font-semibold">
            Service Ethos
          </span>
          <h2 className="text-3xl font-serif font-bold text-white">
            Our Approach to Guest Experience
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="p-6 rounded-2xl bg-charcoal-900 border border-slate-800 space-y-3">
            <div className="w-10 h-10 rounded-xl bg-gold-400/10 border border-gold-400/30 flex items-center justify-center text-gold-400">
              <Sparkles className="w-5 h-5" />
            </div>
            <h4 className="text-base font-serif font-bold text-white">Sensory Dining</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Every outlet engages all five senses—custom acoustic playlists, dramatic lighting, and artisanal plate presentations.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-charcoal-900 border border-slate-800 space-y-3">
            <div className="w-10 h-10 rounded-xl bg-gold-400/10 border border-gold-400/30 flex items-center justify-center text-gold-400">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <h4 className="text-base font-serif font-bold text-white">Authentic Recipes</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              From San Marzano tomatoes and Italian olive oils to regional kasundi tikkas and hand-roasted single origin spices.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-charcoal-900 border border-slate-800 space-y-3">
            <div className="w-10 h-10 rounded-xl bg-gold-400/10 border border-gold-400/30 flex items-center justify-center text-gold-400">
              <Users className="w-5 h-5" />
            </div>
            <h4 className="text-base font-serif font-bold text-white">Teamwork &amp; Care</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Empowering our culinary brigades, sommeliers, and front desk hosts with continuous training and guest empathy.
            </p>
          </div>

          <div className="p-6 rounded-2xl bg-charcoal-900 border border-slate-800 space-y-3">
            <div className="w-10 h-10 rounded-xl bg-gold-400/10 border border-gold-400/30 flex items-center justify-center text-gold-400">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <h4 className="text-base font-serif font-bold text-white">Digital Convenience</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Empowering guests with transparent digital menus, self-service reservation management, and 24/7 AI Concierge care.
            </p>
          </div>
        </div>
      </section>

      {/* CTA Box */}
      <section className="px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto">
        <div className="rounded-3xl bg-charcoal-900 border border-gold-400/30 p-8 sm:p-10 text-center space-y-4">
          <h3 className="text-2xl font-serif font-bold text-white">
            Connect With Our Leadership &amp; Team
          </h3>
          <p className="text-xs text-slate-400 max-w-xl mx-auto leading-relaxed">
            Interested in partnerships, corporate events, or private banquets across Amit Hospitality properties?
          </p>
          <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
            <Link
              to="/enquiry"
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 font-bold text-xs hover:brightness-110 transition shadow-gold-glow"
            >
              Submit Corporate Enquiry
            </Link>
            <Link
              to="/contact"
              className="px-6 py-2.5 rounded-xl bg-charcoal-800 text-slate-200 border border-slate-700 text-xs font-semibold hover:bg-charcoal-700 transition"
            >
              View Contact Directory
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};
