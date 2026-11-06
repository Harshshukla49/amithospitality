import React, { createContext, useContext, useState } from 'react';
import { ChatMessage, Outlet } from '../types';
import { INITIAL_OUTLETS, DEMO_MENU_ITEMS } from '../utils/mockData';
import { useEnvironment } from './EnvironmentContext';

interface ChatContextType {
  messages: ChatMessage[];
  selectedOutlet: Outlet;
  setSelectedOutlet: (outlet: Outlet) => void;
  sendMessage: (content: string) => Promise<void>;
  clearChat: () => void;
  isTyping: boolean;
  language: 'EN' | 'HI';
  setLanguage: (lang: 'EN' | 'HI') => void;
  provideFeedback: (id: string, feedback: 'UP' | 'DOWN') => void;
  requestHandover: () => void;
  handoverRequested: boolean;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { environment, isDemo } = useEnvironment();
  const [selectedOutlet, setSelectedOutlet] = useState<Outlet>(INITIAL_OUTLETS[0]);
  const [language, setLanguage] = useState<'EN' | 'HI'>('EN');
  const [isTyping, setIsTyping] = useState<boolean>(false);
  const [handoverRequested, setHandoverRequested] = useState<boolean>(false);

  const initialGreeting: ChatMessage = {
    id: 'msg_welcome',
    sender: 'ASSISTANT',
    environment,
    content: `Namaste and welcome to **Amit Hospitality**. I am your personal AI Concierge for **${selectedOutlet.name}**.\n\nHow may I curate your dining experience this evening? I can present our curated menus, detail private dining reservations, explain restaurant timings, or check dietary requirements.`,
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    suggestedActions: [
      'Show me the signature menu',
      'What are your timings and dress code?',
      'What is the price of Truffle Dumplings?',
      'I want to book a table for tonight',
      'I want to organize a private event',
      'Connect me with guest relations',
    ],
  };

  const [messages, setMessages] = useState<ChatMessage[]>([initialGreeting]);

  const clearChat = () => {
    setMessages([
      {
        ...initialGreeting,
        id: `msg_${Date.now()}`,
        content: `Conversation refreshed. Welcome to **${selectedOutlet.name}**. How may I assist you?`,
      },
    ]);
    setHandoverRequested(false);
  };

  const provideFeedback = (id: string, feedback: 'UP' | 'DOWN') => {
    setMessages((prev) =>
      prev.map((msg) => (msg.id === id ? { ...msg, feedback } : msg))
    );
  };

  const requestHandover = () => {
    setHandoverRequested(true);
    const handoverNotice: ChatMessage = {
      id: `msg_${Date.now()}`,
      sender: 'SYSTEM',
      environment,
      content: `A priority notification has been dispatched to the Guest Relations Desk at **${selectedOutlet.name}**. A concierge team member will connect with you shortly. You may also reach our concierge desk directly at +91 11 4050 9900.`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
    setMessages((prev) => [...prev, handoverNotice]);
  };

  const sendMessage = async (userText: string) => {
    if (!userText.trim()) return;

    const userMsg: ChatMessage = {
      id: `user_${Date.now()}`,
      sender: 'USER',
      environment,
      content: userText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsTyping(true);

    // Simulate luxury AI response processing
    setTimeout(() => {
      let replyContent = '';
      let citations = undefined;
      let suggestedActions = undefined;

      const lower = userText.toLowerCase();

      // STRICT GROUNDING EVALUATION:
      if (!isDemo) {
        // REAL MODE BEHAVIOR: Real knowledge base currently empty or requires verified docs
        replyContent = `[REAL MODE - VERIFIED KNOWLEDGE REQUIRED]\n\nI do not currently have verified corporate documentation loaded for this inquiry at **${selectedOutlet.name}**.\n\nTo ensure complete accuracy, I only provide verified information. Please contact our Guest Relations Concierge directly at guestrelations@amithospitality.com or ask an administrator to upload verified documents in the Admin Portal.`;
        suggestedActions = ['Connect me with guest relations', 'Switch to DEMO mode to test sample data'];
      } else {
        // DEMO MODE BEHAVIOR:
        if (lower.includes('menu') || lower.includes('dishes') || lower.includes('food')) {
          const outletItems = DEMO_MENU_ITEMS.filter((i) => i.outletId === selectedOutlet.id);
          const itemList = outletItems
            .map(
              (item) =>
                `• **${item.name}** (₹${item.price.toLocaleString('en-IN')}) — *${item.description}* [${item.dietaryFlags.join(', ')}]`
            )
            .join('\n');

          replyContent = `Here is a curated selection from the menu at **${selectedOutlet.name}**:\n\n${itemList}\n\n*Note: All menu items and prices shown are sample DEMO data for illustrative purposes.*`;
          citations = [{ documentTitle: `${selectedOutlet.name} Sample Menu Roster`, category: 'MENU' }];
          suggestedActions = [
            'What is the price of the Sea Bass?',
            'Do you have vegetarian options?',
            'I want to reserve a table',
          ];
        } else if (lower.includes('timing') || lower.includes('hours') || lower.includes('open') || lower.includes('dress code')) {
          replyContent = `**Timings & Policies for ${selectedOutlet.name}**:\n\n• **Operating Hours:** ${selectedOutlet.openingTime} to ${selectedOutlet.closingTime} (Daily)\n• **Cuisine:** ${selectedOutlet.cuisineType}\n• **Dress Code:** ${selectedOutlet.dressCode}\n• **Valet Parking:** Complimentary valet parking is available at the main entrance porte-cochère.\n\n*All timings and policies are currently operating under DEMO mode.*`;
          citations = [{ documentTitle: 'Amber Terrace Operating Policies (Sample)', category: 'POLICY' }];
          suggestedActions = ['Book a table', 'Show me the cocktail menu'];
        } else if (lower.includes('price') || lower.includes('cost') || lower.includes('truffle') || lower.includes('sea bass') || lower.includes('dal')) {
          const matched = DEMO_MENU_ITEMS.find((i) =>
            lower.includes(i.name.toLowerCase().split(' ')[0]) || lower.includes('truffle')
          );
          if (matched) {
            replyContent = `The **${matched.name}** is priced at **₹${matched.price.toLocaleString('en-IN')}**.\n\n*Preparation:* ${matched.description}\n*Dietary:* ${matched.dietaryFlags.join(', ')}\n\n*Price is illustrative sample DEMO data.*`;
          } else {
            replyContent = `Our signature dishes range between ₹595 and ₹1,250. For example, our **Truffle Edamame Dumplings** are ₹695, and our **Glazed Chilean Sea Bass** is ₹1,250.\n\n*Sample DEMO pricing.*`;
          }
          suggestedActions = ['I want to book a table', 'View full menu'];
        } else if (lower.includes('book') || lower.includes('reserve') || lower.includes('table')) {
          replyContent = `I would be delighted to assist you with a table reservation at **${selectedOutlet.name}**.\n\nPlease select your preferred date, time, and guest count using the reservation drawer below, or let me know if you have a special occasion to celebrate!`;
          suggestedActions = ['Open reservation form', 'Do you have outdoor seating?'];
        } else if (lower.includes('private') || lower.includes('party') || lower.includes('event') || lower.includes('wedding')) {
          replyContent = `At **${selectedOutlet.name}**, we host bespoke private celebrations, corporate executive dinners, and cocktail receptions with seating capacity up to ${selectedOutlet.seatingCapacity} guests.\n\nWould you like me to connect you with our Events & Banquets Director or capture your event details for a personalized proposal?`;
          suggestedActions = ['Submit private dining enquiry', 'Contact Events Team'];
        } else if (lower.includes('connect') || lower.includes('team') || lower.includes('human') || lower.includes('speak')) {
          replyContent = `Certainly. I am initiating a priority request to our Guest Relations Concierge team. You can also contact us directly at +91 11 4050 9900 or reservations@amithospitality.com.`;
          requestHandover();
          setIsTyping(false);
          return;
        } else {
          replyContent = `Thank you for your inquiry regarding **${selectedOutlet.name}**.\n\nAs your luxury AI Concierge, I can assist you with:\n1. Exploring our curated culinary & cocktail menus.\n2. Inquiring about dietary accommodations (Vegetarian, Jain, Vegan, Gluten-Free).\n3. Table reservations and dress code policies.\n4. Private dining, corporate gatherings, and celebrations.\n\nHow may I tailor your experience?`;
          suggestedActions = [
            'Show me the signature menu',
            'What are your timings and dress code?',
            'I want to book a table for tonight',
          ];
        }
      }

      const assistantMsg: ChatMessage = {
        id: `assist_${Date.now()}`,
        sender: 'ASSISTANT',
        environment,
        content: replyContent,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        citations,
        suggestedActions,
      };

      setMessages((prev) => [...prev, assistantMsg]);
      setIsTyping(false);
    }, 700);
  };

  return (
    <ChatContext.Provider
      value={{
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
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};
