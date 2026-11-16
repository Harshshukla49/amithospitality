import React from 'react';
import { Link } from 'react-router-dom';
import {
  Sparkles,
  MapPin,
  Phone,
  Mail,
  Clock,
  ExternalLink,
  ShieldCheck,
  Calendar,
  MessageSquare,
  ArrowUpRight,
} from 'lucide-react';
import { COMPANY_PROFILE } from '../../utils/mockData';

export const Footer: React.FC = () => {
  return (
    <footer className="w-full bg-obsidian-950 border-t border-gold-400/20 text-slate-300 pt-16 pb-12 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Top Section: Brand Statement & Contact Highlights */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-10 pb-12 border-b border-slate-800/80">
          {/* Column 1 & 2: Group Identity & Vision */}
          <div className="lg:col-span-2 space-y-4">
            <Link to="/" className="flex items-center gap-3 group inline-flex">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-gold-400 to-gold-600 flex items-center justify-center shadow-gold-glow">
                <Sparkles className="w-5 h-5 text-obsidian-950" />
              </div>
              <div>
                <span className="font-serif font-bold text-xl tracking-wider text-white group-hover:text-gold-300 transition-colors">
                  AMIT HOSPITALITY
                </span>
                <span className="block text-[10px] tracking-widest uppercase font-mono text-gold-400/80">
                  LLP • ESTABLISHED 2018
                </span>
              </div>
            </Link>

            <p className="text-sm text-slate-400 font-sans leading-relaxed max-w-md">
              {COMPANY_PROFILE.tagline} A premier hospitality conglomerate uniting Kolkata's most celebrated dining, nightlife, and lifestyle destinations under one vision of culinary innovation and heartfelt guest service.
            </p>

            <div className="pt-2 text-xs text-slate-400 space-y-1">
              <p>
                <strong className="text-gold-400">Leadership:</strong> Amit Bajoria (Founder) &amp; Vanita Bajoria (Co-Founder)
              </p>
              <p>
                <strong className="text-gold-400">Corporate HQ:</strong> {COMPANY_PROFILE.corporateOffice.address}
              </p>
            </div>

            <div className="flex flex-wrap gap-3 pt-2">
              <Link
                to="/concierge"
                className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-gold-500/20 to-gold-600/20 border border-gold-400/40 text-gold-300 text-xs font-semibold hover:brightness-125 transition"
              >
                <MessageSquare className="w-3.5 h-3.5" />
                <span>Launch AI Concierge</span>
              </Link>
              <Link
                to="/guest/reservations"
                className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-charcoal-900 border border-slate-700 hover:border-slate-600 text-slate-200 text-xs font-medium transition"
              >
                <Calendar className="w-3.5 h-3.5 text-gold-400" />
                <span>My Booking Status</span>
              </Link>
            </div>
          </div>

          {/* Column 3: The Brand Portfolio */}
          <div className="space-y-3">
            <h4 className="text-xs font-mono font-bold tracking-widest uppercase text-gold-400">
              Brand Portfolio
            </h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link
                  to="/brands/lord-of-drinks"
                  className="hover:text-gold-300 transition flex items-center justify-between group"
                >
                  <span>Lord of the Drinks</span>
                  <ArrowUpRight className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 text-gold-400 transition" />
                </Link>
              </li>
              <li>
                <Link
                  to="/brands/veneto"
                  className="hover:text-gold-300 transition flex items-center justify-between group"
                >
                  <span>Veneto Kitchen &amp; Bar</span>
                  <ArrowUpRight className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 text-gold-400 transition" />
                </Link>
              </li>
              <li>
                <Link
                  to="/brands/warehouse"
                  className="hover:text-gold-300 transition flex items-center justify-between group"
                >
                  <span>The Warehouse Cafe</span>
                  <ArrowUpRight className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 text-gold-400 transition" />
                </Link>
              </li>
              <li>
                <Link
                  to="/brands/deliite"
                  className="hover:text-gold-300 transition flex items-center justify-between group"
                >
                  <span>Deliite Lifestyle Retail</span>
                  <ArrowUpRight className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 text-gold-400 transition" />
                </Link>
              </li>
            </ul>
          </div>

          {/* Column 4: Quick Navigation */}
          <div className="space-y-3">
            <h4 className="text-xs font-mono font-bold tracking-widest uppercase text-gold-400">
              Experiences
            </h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link to="/about" className="hover:text-gold-300 transition">
                  About Us (Know Us)
                </Link>
              </li>
              <li>
                <Link to="/menus" className="hover:text-gold-300 transition">
                  Culinary &amp; Drink Menus
                </Link>
              </li>
              <li>
                <Link to="/events" className="hover:text-gold-300 transition">
                  Events &amp; Live Music
                </Link>
              </li>
              <li>
                <Link to="/media" className="hover:text-gold-300 transition">
                  Media &amp; Photo Gallery
                </Link>
              </li>
              <li>
                <Link to="/career" className="hover:text-gold-300 transition">
                  Hospitality Careers
                </Link>
              </li>
              <li>
                <Link to="/enquiry" className="hover:text-gold-300 transition">
                  Private &amp; Corporate Enquiries
                </Link>
              </li>
              <li>
                <Link to="/contact" className="hover:text-gold-300 transition">
                  Contact Directory
                </Link>
              </li>
            </ul>
          </div>

          {/* Column 5: Direct Contact Details */}
          <div className="space-y-3">
            <h4 className="text-xs font-mono font-bold tracking-widest uppercase text-gold-400">
              Direct Contact
            </h4>
            <div className="space-y-2.5 text-xs text-slate-400">
              <div className="flex items-start gap-2">
                <MapPin className="w-4 h-4 text-gold-400 shrink-0 mt-0.5" />
                <span>401 Kamalalaya Centre, 156A Lenin Sarani, Kolkata - 700013</span>
              </div>
              <div className="flex items-center gap-2">
                <Phone className="w-4 h-4 text-gold-400 shrink-0" />
                <a href="tel:+919432335967" className="hover:text-gold-300 transition">
                  +91 94323 35967
                </a>
              </div>
              <div className="flex items-center gap-2">
                <Mail className="w-4 h-4 text-gold-400 shrink-0" />
                <a href="mailto:vanita@amithospitality.com" className="hover:text-gold-300 transition">
                  vanita@amithospitality.com
                </a>
              </div>
              <div className="pt-2">
                <p className="text-[11px] font-semibold text-slate-300">Mall Destinations:</p>
                <p className="text-[11px] text-slate-400">
                  Level 4, South City Mall (LOTD, Veneto, Warehouse Cafe)
                </p>
                <p className="text-[11px] text-slate-400">
                  Level 3, Diamond Plaza Mall (Deliite)
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Bar: Copyright, Legal & Staff Link */}
        <div className="pt-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
          <p>© 2018–2026 Amit Hospitality LLP. All rights reserved. Registered under Ministry of Corporate Affairs, India.</p>
          <div className="flex items-center gap-6">
            <Link to="/contact" className="hover:text-slate-300 transition">
              Enquiry
            </Link>
            <Link to="/career" className="hover:text-slate-300 transition">
              Careers
            </Link>
            <Link to="/login" className="hover:text-gold-400 font-mono transition flex items-center gap-1">
              <span>Staff / Management Portal</span>
              <ShieldCheck className="w-3.5 h-3.5 text-gold-400" />
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
};
