import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Sparkles,
  RotateCcw,
  Headphones,
  Utensils,
  Calendar,
  Clock,
  MapPin,
  ThumbsUp,
  ThumbsDown,
  Info,
  ChevronRight,
  ExternalLink,
  ShieldCheck,
  AlertTriangle,
  Globe,
  X,
} from 'lucide-react';
import { useChat } from '../../context/ChatContext';
import { useEnvironment } from '../../context/EnvironmentContext';
import { INITIAL_OUTLETS } from '../../utils/mockData';
import { Outlet, ReservationRequest, Lead } from '../../types';
import { ReservationModal } from '../../components/customer/ReservationModal';
import { LeadModal } from '../../components/customer/LeadModal';

interface ConciergePageProps {
  onReservationCreated?: (res: ReservationRequest) => void;
  onLeadCreated?: (lead: Lead) => void;
  isEmbedded?: boolean;
}

export const ConciergePage: React.FC<ConciergePageProps> = ({
  onReservationCreated,
  onLeadCreated,
  isEmbedded = false,
}) => {
  const {
    messages,
    selectedOutlet,
    setSelectedOutlet,
    sendMessage,
    clearChat,
    isTyping,
    language,
    setLanguage,
    provideFeedback,
    requestHandover,
    handoverRequested,
  } = useChat();
  const { environment, isDemo, openSwitchModal } = useEnvironment();

  const [input, setInput] = useState('');
  const [isReservationOpen, setIsReservationOpen] = useState(false);
  const [isLeadOpen, setIsLeadOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSend = (textToSend?: string) => {
    const query = textToSend || input;
    if (!query.trim() || isTyping) return;

    const qLower = query.toLowerCase();
    if (
      qLower.includes('book') ||
      qLower.includes('reserve') ||
      qLower.includes('table') ||
      qLower.includes('table chahiye') ||
      qLower.includes('booking karni')
    ) {
      setIsReservationOpen(true);
    } else if (
      qLower.includes('party') ||
      qLower.includes('event') ||
      qLower.includes('corporate') ||
      qLower.includes('banquet') ||
      qLower.includes('wedding') ||
      qLower.includes('callback') ||
      qLower.includes('contact me') ||
      qLower.includes('call me') ||
      qLower.includes('call back') ||
      qLower.includes('private dining') ||
      qLower.includes('lead')
    ) {
      setIsLeadOpen(true);
    }

    sendMessage(query);
    if (!textToSend) setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSend();
    }
  };

  return (
    <div className={`flex flex-col lg:flex-row ${isEmbedded ? 'h-full p-2' : 'h-[calc(100vh-4rem)] max-w-7xl mx-auto px-2 sm:px-4 lg:px-6 py-4 gap-4'}`}>
      {/* Left Sidebar: Outlet Selection & Luxury Destination Highlights */}
      {!isEmbedded && (
        <div className="lg:w-80 shrink-0 flex flex-col gap-4 overflow-y-auto pr-1">
        {/* Brand Showcase Card */}
        <div className="p-4 rounded-2xl glass-panel-elevated border border-gold-400/30">
          <div className="flex items-center gap-2 text-gold-400 mb-1.5">
            <Sparkles className="w-4 h-4" />
            <span className="text-[11px] font-semibold tracking-widest uppercase">
              Curated Dining
            </span>
          </div>
          <h2 className="text-xl font-serif font-bold text-white leading-tight">
            Amit Hospitality
          </h2>
          <p className="text-xs text-slate-400 mt-1 leading-relaxed">
            Where culinary artistry meets architectural grandeur. Select a signature outlet below to converse with its dedicated AI concierge.
          </p>
        </div>

        {/* Outlet Selector */}
        <div className="space-y-2.5">
          <label className="text-[11px] font-semibold tracking-wider uppercase text-slate-400 px-1 flex items-center justify-between">
            <span>Dining Destinations</span>
            <span className="text-gold-400 font-mono text-[10px]">
              {INITIAL_OUTLETS.length} Available
            </span>
          </label>

          {INITIAL_OUTLETS.map((outlet) => {
            const isSelected = selectedOutlet.id === outlet.id;
            return (
              <button
                key={outlet.id}
                onClick={() => setSelectedOutlet(outlet)}
                className={`w-full text-left p-3.5 rounded-xl transition border relative group ${
                  isSelected
                    ? 'bg-charcoal-800/95 border-gold-400/70 shadow-gold-glow'
                    : 'glass-panel border-slate-800/80 hover:border-slate-700 text-slate-300'
                }`}
              >
                {isSelected && (
                  <span className="absolute left-0 top-3 bottom-3 w-1 bg-gradient-to-b from-gold-400 to-gold-600 rounded-r" />
                )}
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h3
                      className={`text-sm font-semibold tracking-wide ${
                        isSelected ? 'text-gold-300' : 'text-slate-200 group-hover:text-white'
                      }`}
                    >
                      {outlet.name}
                    </h3>
                    <p className="text-[11px] text-slate-400 mt-0.5">{outlet.outletType}</p>
                  </div>
                  {outlet.isPopular && (
                    <span className="text-[9px] uppercase tracking-wider font-semibold px-1.5 py-0.5 rounded bg-gold-400/15 text-gold-400 border border-gold-400/30 shrink-0">
                      Signature
                    </span>
                  )}
                </div>

                <div className="mt-2.5 pt-2 border-t border-slate-700/40 grid grid-cols-2 gap-1 text-[11px] text-slate-400">
                  <div className="flex items-center gap-1 truncate">
                    <Clock className="w-3 h-3 text-gold-400/80 shrink-0" />
                    <span>{outlet.openingTime} - {outlet.closingTime}</span>
                  </div>
                  <div className="flex items-center gap-1 truncate">
                    <MapPin className="w-3 h-3 text-gold-400/80 shrink-0" />
                    <span className="truncate">{outlet.location.split(',')[0]}</span>
                  </div>
                </div>
              </button>
            );
          })}
        </div>

        {/* Action Fast-Track Shortcuts */}
        <div className="p-3.5 rounded-xl glass-panel space-y-2 border border-slate-800">
          <p className="text-[11px] uppercase tracking-wider text-slate-400 font-semibold">
            Direct Concierge Assistance
          </p>
          <button
            onClick={() => setIsReservationOpen(true)}
            className="w-full flex items-center justify-between p-2 rounded-lg bg-charcoal-900/80 hover:bg-charcoal-800 border border-slate-700/60 text-xs text-slate-200 transition"
          >
            <span className="flex items-center gap-2">
              <Calendar className="w-3.5 h-3.5 text-gold-400" />
              <span>Book Table at {selectedOutlet.name.split(' ')[0]}</span>
            </span>
            <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
          </button>
          <button
            onClick={() => setIsLeadOpen(true)}
            className="w-full flex items-center justify-between p-2 rounded-lg bg-charcoal-900/80 hover:bg-charcoal-800 border border-slate-700/60 text-xs text-slate-200 transition"
          >
            <span className="flex items-center gap-2">
              <Utensils className="w-3.5 h-3.5 text-gold-400" />
              <span>Private Dining & Parties</span>
            </span>
            <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
          </button>
          <button
            onClick={requestHandover}
            className="w-full flex items-center justify-between p-2 rounded-lg bg-charcoal-900/80 hover:bg-charcoal-800 border border-slate-700/60 text-xs text-slate-200 transition"
          >
            <span className="flex items-center gap-2">
              <Headphones className="w-3.5 h-3.5 text-gold-400" />
              <span>Connect with Human Host</span>
            </span>
            <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
          </button>
        </div>
      </div>
      )}

      {/* Center & Right: Luxury Conversational AI Concierge Terminal */}
      <div className="flex-1 flex flex-col rounded-2xl glass-panel-elevated border border-gold-400/30 overflow-hidden shadow-luxury">
        {/* Chat Header */}
        <div className="px-4 sm:px-5 py-3 border-b border-slate-800/80 bg-charcoal-900/70 flex items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-xl bg-gradient-to-br from-gold-400 to-gold-600 flex items-center justify-center text-obsidian-950 shadow-gold-glow shrink-0">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                {isEmbedded ? (
                  <select
                    value={selectedOutlet.id}
                    onChange={(e) => {
                      const found = INITIAL_OUTLETS.find((o) => o.id === Number(e.target.value));
                      if (found) setSelectedOutlet(found);
                    }}
                    className="text-xs bg-charcoal-900 border border-gold-400/50 text-gold-300 rounded-lg px-2 py-0.5 font-serif font-bold focus:outline-none"
                  >
                    {INITIAL_OUTLETS.map((o) => (
                      <option key={o.id} value={o.id}>
                        {o.name}
                      </option>
                    ))}
                  </select>
                ) : (
                  <h3 className="text-sm font-serif font-bold text-white tracking-wide">
                    {selectedOutlet.name} Concierge
                  </h3>
                )}
                <span className="hidden sm:inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-mono uppercase bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                  Online
                </span>
              </div>
              <p className="text-[10px] text-slate-400">
                {isDemo ? 'DEMO Mode (Sample Data)' : 'REAL Verified Knowledge'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1.5 sm:gap-2">
            {/* Multilingual Selector: EN / हिन्दी */}
            <div className="flex items-center rounded-lg bg-charcoal-900 border border-slate-700/80 p-0.5 text-xs">
              <button
                type="button"
                onClick={() => setLanguage('EN')}
                className={`px-2 py-0.5 rounded font-mono text-[10px] font-bold transition ${
                  language === 'EN'
                    ? 'bg-gold-500/20 text-gold-300 border border-gold-400/40'
                    : 'text-slate-400 hover:text-white'
                }`}
                title="Converse in English"
              >
                EN
              </button>
              <button
                type="button"
                onClick={() => setLanguage('HI')}
                className={`px-2 py-0.5 rounded font-sans text-[10px] font-bold transition ${
                  language === 'HI'
                    ? 'bg-gold-500/20 text-gold-300 border border-gold-400/40'
                    : 'text-slate-400 hover:text-white'
                }`}
                title="Converse in हिन्दी / Hinglish"
              >
                हिन्दी
              </button>
            </div>

            <button
              onClick={clearChat}
              title="Clear conversation and restart"
              className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs text-slate-400 hover:text-white hover:bg-charcoal-800 transition"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span className="hidden md:inline">Reset</span>
            </button>

            {isEmbedded && (
              <button
                onClick={() => window.parent.postMessage('amit-close-widget', '*')}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-charcoal-800 transition"
                title="Close Concierge"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {/* Messages Feed Viewport */}
        <div className="flex-1 p-4 sm:p-6 overflow-y-auto space-y-4">
          {messages.map((msg) => {
            const isUser = msg.sender === 'USER';
            const isSystem = msg.sender === 'SYSTEM';

            if (isSystem) {
              return (
                <div
                  key={msg.id}
                  className="p-3 rounded-xl bg-gold-500/10 border border-gold-400/30 text-gold-300 text-xs flex items-start gap-2.5 max-w-xl mx-auto shadow-sm"
                >
                  <Headphones className="w-4 h-4 text-gold-400 shrink-0 mt-0.5" />
                  <div className="space-y-1">
                    <p className="font-semibold text-gold-200">Staff Notification Triggered</p>
                    <p className="text-slate-300">{msg.content}</p>
                  </div>
                </div>
              );
            }

            return (
              <div
                key={msg.id}
                className={`flex gap-3 max-w-2xl ${isUser ? 'ml-auto flex-row-reverse' : 'mr-auto'}`}
              >
                {!isUser && (
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-gold-400 to-gold-600 flex items-center justify-center text-obsidian-950 shrink-0 shadow-sm mt-0.5">
                    <Sparkles className="w-3.5 h-3.5" />
                  </div>
                )}

                <div
                  className={`flex flex-col space-y-2 ${
                    isUser
                      ? 'bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 font-medium rounded-2xl rounded-tr-none px-4 py-3 shadow-md'
                      : 'bg-charcoal-900/90 border border-slate-700/80 text-slate-200 rounded-2xl rounded-tl-none px-4 py-3.5 shadow-sm'
                  }`}
                >
                  {/* Environment Disclaimer Badge for Assistant Messages in Demo Mode */}
                  {!isUser && msg.environment === 'DEMO' && (
                    <div className="flex items-center gap-1.5 text-[10px] uppercase font-mono tracking-wider font-semibold text-amber-400 bg-amber-400/10 px-2 py-0.5 rounded w-fit border border-amber-400/20">
                      <AlertTriangle className="w-3 h-3" />
                      <span>DEMO DATA — Sample Content</span>
                    </div>
                  )}

                  {/* Message Content */}
                  <div className="text-xs sm:text-sm leading-relaxed whitespace-pre-line">
                    {msg.content}
                  </div>

                  {/* Citations if available */}
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="pt-2 border-t border-slate-700/60 mt-1 flex flex-wrap items-center gap-1.5 text-[10px] text-slate-400">
                      <ShieldCheck className="w-3 h-3 text-gold-400" />
                      <span>Retrieved from:</span>
                      {msg.citations.map((c, i) => (
                        <span
                          key={i}
                          className="px-2 py-0.5 rounded bg-charcoal-800 text-gold-300 font-mono border border-slate-700"
                        >
                          {c.documentTitle}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Suggested Action Chips */}
                  {msg.suggestedActions && (
                    <div className="pt-2 flex flex-wrap gap-1.5">
                      {msg.suggestedActions.map((action, i) => (
                        <button
                          key={i}
                          onClick={() => handleSend(action)}
                          className="px-2.5 py-1 rounded-full text-[11px] bg-charcoal-800 hover:bg-charcoal-700 text-gold-300 border border-gold-400/30 hover:border-gold-400 transition"
                        >
                          {action}
                        </button>
                      ))}
                    </div>
                  )}

                  {/* Message Footer: Timestamp and Feedback */}
                  <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1">
                    <span className={isUser ? 'text-obsidian-900 font-medium' : 'text-slate-500'}>
                      {msg.timestamp}
                    </span>
                    {!isUser && (
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => provideFeedback(msg.id, 'UP')}
                          className={`hover:text-gold-400 transition ${
                            msg.feedback === 'UP' ? 'text-gold-400' : 'text-slate-500'
                          }`}
                          title="Accurate & helpful"
                        >
                          <ThumbsUp className="w-3 h-3" />
                        </button>
                        <button
                          onClick={() => provideFeedback(msg.id, 'DOWN')}
                          className={`hover:text-rose-400 transition ${
                            msg.feedback === 'DOWN' ? 'text-rose-400' : 'text-slate-500'
                          }`}
                          title="Report inaccuracy"
                        >
                          <ThumbsDown className="w-3 h-3" />
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}

          {/* Typing Indicator */}
          {isTyping && (
            <div className="flex gap-3 max-w-sm mr-auto items-center">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-gold-400 to-gold-600 flex items-center justify-center text-obsidian-950 shrink-0">
                <Sparkles className="w-3.5 h-3.5 animate-spin" />
              </div>
              <div className="px-4 py-3 rounded-2xl rounded-tl-none bg-charcoal-900 border border-slate-700/80 text-xs text-slate-400 flex items-center gap-2">
                <span>Curating response from {environment} knowledge</span>
                <span className="flex gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-gold-400 animate-bounce" />
                  <span
                    className="w-1.5 h-1.5 rounded-full bg-gold-400 animate-bounce"
                    style={{ animationDelay: '0.2s' }}
                  />
                  <span
                    className="w-1.5 h-1.5 rounded-full bg-gold-400 animate-bounce"
                    style={{ animationDelay: '0.4s' }}
                  />
                </span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div className="p-3 sm:p-4 border-t border-slate-800 bg-charcoal-900/80">
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isTyping}
              placeholder={`Ask about ${selectedOutlet.name} menus, pricing, hours, or reservations...`}
              className="flex-1 px-4 py-2.5 rounded-xl bg-obsidian-900 border border-slate-700 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-gold-400 disabled:opacity-50 transition"
            />
            <button
              onClick={() => handleSend()}
              disabled={!input.trim() || isTyping}
              className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-gold-500 to-gold-600 text-obsidian-950 font-semibold hover:brightness-110 disabled:opacity-50 disabled:hover:brightness-100 shadow-gold-glow transition flex items-center gap-1.5 text-xs sm:text-sm"
            >
              <span>Send</span>
              <Send className="w-3.5 h-3.5" />
            </button>
          </div>

          <p className="text-[10px] text-slate-500 text-center mt-2 flex items-center justify-center gap-1.5">
            <Info className="w-3 h-3 text-gold-400" />
            <span>
              Amit AI Concierge responses are grounded strictly in the active{' '}
              <strong>{environment}</strong> knowledge environment.
            </span>
          </p>
        </div>
      </div>

      {/* Reservation Request Modal */}
      <ReservationModal
        isOpen={isReservationOpen}
        onClose={() => setIsReservationOpen(false)}
        outlet={selectedOutlet}
        onSuccess={(newRes) => {
          if (onReservationCreated) onReservationCreated(newRes);
        }}
      />

      {/* Lead Inquiry Modal */}
      <LeadModal
        isOpen={isLeadOpen}
        onClose={() => setIsLeadOpen(false)}
        outlet={selectedOutlet}
        onSuccess={(newLead) => {
          if (onLeadCreated) onLeadCreated(newLead);
        }}
      />
    </div>
  );
};
