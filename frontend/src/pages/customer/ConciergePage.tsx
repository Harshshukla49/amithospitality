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
  MessageSquare,
  Compass,
} from 'lucide-react';
import { useChat } from '../../context/ChatContext';
import { useEnvironment } from '../../context/EnvironmentContext';
import { INITIAL_OUTLETS } from '../../utils/mockData';
import { Outlet, ReservationRequest, Lead } from '../../types';
import { ReservationModal } from '../../components/customer/ReservationModal';
import { LeadModal } from '../../components/customer/LeadModal';
import { MenuModal } from '../../components/customer/MenuModal';
import { OutletCard } from '../../components/customer/OutletCard';

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
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [menuOutlet, setMenuOutlet] = useState<Outlet>(selectedOutlet);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatTerminalRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const scrollToChat = () => {
    if (!isEmbedded && chatTerminalRef.current) {
      chatTerminalRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
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

  const handleCardSelect = (outlet: Outlet) => {
    setSelectedOutlet(outlet);
    scrollToChat();
  };

  const handleCardViewMenu = (outlet: Outlet) => {
    setMenuOutlet(outlet);
    setIsMenuOpen(true);
  };

  const handleCardBookTable = (outlet: Outlet) => {
    setSelectedOutlet(outlet);
    setIsReservationOpen(true);
  };

  return (
    <div
      className={
        isEmbedded
          ? 'h-full p-2 flex flex-col'
          : 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-8 animate-fade-in'
      }
    >
      {/* SECTION 1: LUXURY SIGNATURE OUTLET CARDS GALLERY (Only in full customer view) */}
      {!isEmbedded && (
        <section aria-labelledby="signature-destinations-heading" className="space-y-6">
          {/* Header Section */}
          <div className="text-center space-y-2.5 max-w-3xl mx-auto">
            <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-gold-500/10 border border-gold-400/30 text-gold-400 text-xs font-semibold uppercase tracking-widest shadow-sm">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Curated Five-Star Gastronomy</span>
            </div>
            <h1
              id="signature-destinations-heading"
              className="text-2xl sm:text-3xl lg:text-4xl font-serif font-bold text-transparent bg-clip-text bg-gradient-to-r from-white via-gold-200 to-gold-400 tracking-tight"
            >
              Discover Our Signature Dining Destinations
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 leading-relaxed max-w-2xl mx-auto">
              Explore exceptional dining experiences, thoughtfully curated for every occasion.
            </p>
          </div>

          {/* 3-Column Responsive Grid: Desktop 3 / Tablet 2 / Mobile 1 */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {INITIAL_OUTLETS.map((outlet) => (
              <OutletCard
                key={outlet.id}
                outlet={outlet}
                isSelected={selectedOutlet.id === outlet.id}
                onSelect={handleCardSelect}
                onViewMenu={handleCardViewMenu}
                onBookTable={handleCardBookTable}
              />
            ))}
          </div>
        </section>
      )}

      {/* SECTION 2: LUXURY CONVERSATIONAL AI CONCIERGE TERMINAL */}
      <section
        ref={chatTerminalRef}
        aria-label="AI Concierge Terminal"
        className={`flex flex-col rounded-2xl glass-panel-elevated border border-gold-400/30 overflow-hidden shadow-luxury ${
          isEmbedded ? 'h-full' : 'h-[620px] sm:h-[660px]'
        }`}
      >
        {/* Chat Terminal Header */}
        <div className="px-4 sm:px-6 py-3.5 border-b border-slate-800/80 bg-charcoal-900/80 backdrop-blur-md flex items-center justify-between gap-3 shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-gradient-to-br from-gold-400 to-gold-600 flex items-center justify-center text-obsidian-950 shadow-gold-glow shrink-0">
              <Sparkles className="w-4 h-4 sm:w-5 sm:h-5" />
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
                    className="text-xs bg-charcoal-900 border border-gold-400/50 text-gold-300 rounded-lg px-2.5 py-1 font-serif font-bold focus:outline-none"
                  >
                    {INITIAL_OUTLETS.map((o) => (
                      <option key={o.id} value={o.id}>
                        {o.name}
                      </option>
                    ))}
                  </select>
                ) : (
                  <div className="flex items-center gap-2">
                    <h2 className="text-sm sm:text-base font-serif font-bold text-white tracking-wide">
                      {selectedOutlet.name} Concierge
                    </h2>
                    <span className="hidden md:inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-gold-500/10 text-gold-300 border border-gold-400/30">
                      {selectedOutlet.outletType.split('&')[0]}
                    </span>
                  </div>
                )}
                <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-mono uppercase bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  Online
                </span>
              </div>
              <p className="text-[10px] text-slate-400">
                {isDemo ? 'DEMO Mode (Interactive Sample Knowledge)' : 'REAL Verified Knowledge Base'}
              </p>
            </div>
          </div>

          {/* Controls: Outlet Switcher Pill (compact), Language Selector, Reset */}
          <div className="flex items-center gap-1.5 sm:gap-2.5">
            {/* Quick Outlet Selector Chips for Desktop */}
            {!isEmbedded && (
              <div className="hidden lg:flex items-center rounded-xl bg-obsidian-900 border border-slate-800 p-0.5 text-xs">
                {INITIAL_OUTLETS.map((o) => {
                  const isCur = selectedOutlet.id === o.id;
                  return (
                    <button
                      key={o.id}
                      type="button"
                      onClick={() => setSelectedOutlet(o)}
                      className={`px-2.5 py-1 rounded-lg text-[11px] font-medium transition ${
                        isCur
                          ? 'bg-gold-500/20 text-gold-300 font-bold border border-gold-400/40'
                          : 'text-slate-400 hover:text-slate-200'
                      }`}
                    >
                      {o.name.split(' ')[0]}
                    </button>
                  );
                })}
              </div>
            )}

            {/* Multilingual Selector: EN / हिन्दी */}
            <div className="flex items-center rounded-lg bg-obsidian-900 border border-slate-700/80 p-0.5 text-xs">
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

            {/* Reset Button */}
            <button
              onClick={clearChat}
              title="Clear conversation and restart"
              className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs text-slate-400 hover:text-white hover:bg-charcoal-800 transition border border-transparent hover:border-slate-700"
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

        {/* Action Fast-Track Shortcuts Bar */}
        <div className="px-4 sm:px-6 py-2 bg-obsidian-950/60 border-b border-slate-800/80 flex items-center gap-2 overflow-x-auto scrollbar-thin text-xs shrink-0">
          <span className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold mr-1 shrink-0 flex items-center gap-1">
            <Compass className="w-3 h-3 text-gold-400" />
            Fast-Track:
          </span>
          <button
            onClick={() => handleCardViewMenu(selectedOutlet)}
            className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-charcoal-900 hover:bg-charcoal-800 border border-slate-700 hover:border-gold-400/40 text-slate-200 hover:text-gold-300 transition shrink-0 whitespace-nowrap text-[11px]"
          >
            <Utensils className="w-3 h-3 text-gold-400" />
            <span>View {selectedOutlet.name.split(' ')[0]} Menu</span>
          </button>
          <button
            onClick={() => setIsReservationOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-charcoal-900 hover:bg-charcoal-800 border border-slate-700 hover:border-gold-400/40 text-slate-200 hover:text-gold-300 transition shrink-0 whitespace-nowrap text-[11px]"
          >
            <Calendar className="w-3 h-3 text-gold-400" />
            <span>Book Table</span>
          </button>
          <button
            onClick={() => setIsLeadOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-charcoal-900 hover:bg-charcoal-800 border border-slate-700 hover:border-gold-400/40 text-slate-200 hover:text-gold-300 transition shrink-0 whitespace-nowrap text-[11px]"
          >
            <Sparkles className="w-3 h-3 text-gold-400" />
            <span>Private Dining & Parties</span>
          </button>
          <button
            onClick={requestHandover}
            className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-charcoal-900 hover:bg-charcoal-800 border border-slate-700 hover:border-gold-400/40 text-slate-200 hover:text-gold-300 transition shrink-0 whitespace-nowrap text-[11px]"
          >
            <Headphones className="w-3 h-3 text-gold-400" />
            <span>Connect with Human Host</span>
          </button>
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
                  className="p-3.5 rounded-xl bg-gold-500/10 border border-gold-400/30 text-gold-300 text-xs flex items-start gap-2.5 max-w-xl mx-auto shadow-sm"
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
        <div className="p-3 sm:p-4 border-t border-slate-800 bg-charcoal-900/90 shrink-0">
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isTyping}
              placeholder={`Ask about ${selectedOutlet.name} menus, pricing, dress code, hours, or reservations...`}
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
              <strong className="text-slate-300">{environment}</strong> verified hospitality knowledge.
            </span>
          </p>
        </div>
      </section>

      {/* Menu Preview Modal */}
      <MenuModal
        isOpen={isMenuOpen}
        onClose={() => setIsMenuOpen(false)}
        outlet={menuOutlet}
        onBookTable={(outlet) => {
          setSelectedOutlet(outlet);
          setIsReservationOpen(true);
        }}
        onAskConcierge={(query) => {
          handleSend(query);
          scrollToChat();
        }}
      />

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
