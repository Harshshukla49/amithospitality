import React, { createContext, useContext, useState, useEffect } from 'react';
import { ChatMessage, Outlet } from '../types';
import { INITIAL_OUTLETS } from '../utils/mockData';
import { useEnvironment } from './EnvironmentContext';
import { apiRequest } from '../api/client';

interface BackendChatResponse {
  reply: string;
  environment: 'DEMO' | 'REAL';
  is_demo: boolean;
  detected_intent?: string;
  citations?: Array<{
    document_title: string;
    category: string;
    snippet?: string;
  }>;
  suggested_actions?: string[];
}

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

  // Persistent Session ID
  const [sessionId] = useState<string>(() => {
    let s = sessionStorage.getItem('amit_chat_session_id');
    if (!s) {
      s = `sess_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
      sessionStorage.setItem('amit_chat_session_id', s);
    }
    return s;
  });

  const getGreeting = (outlet: Outlet): ChatMessage => ({
    id: `msg_welcome_${outlet.id}`,
    sender: 'ASSISTANT',
    environment,
    content: `Namaste and welcome to **Amit Hospitality**. I am your personal AI Concierge for **${outlet.name}** (${outlet.outletType}).\n\nHow may I curate your dining experience this evening? I can present our curated menus, detail private dining reservations, explain restaurant timings, or check dietary requirements.`,
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    suggestedActions: [
      'Show me the signature menu',
      'What are your timings and dress code?',
      'What is the price of Truffle Dumplings?',
      'I want to book a table for tonight',
      'I want to organize a private event',
      'Connect me with guest relations',
    ],
  });

  const [messages, setMessages] = useState<ChatMessage[]>([getGreeting(INITIAL_OUTLETS[0])]);

  // Handle switching outlet: update welcome context
  const handleOutletChange = (newOutlet: Outlet) => {
    setSelectedOutlet(newOutlet);
    const switchNotice: ChatMessage = {
      id: `notice_${Date.now()}`,
      sender: 'SYSTEM',
      environment,
      content: `Concierge context updated to **${newOutlet.name}** (${newOutlet.cuisineType}). How may I assist your experience here?`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      suggestedActions: [
        'Show me the signature menu',
        'What are your timings and dress code?',
        'Book a table for tonight',
      ],
    };
    setMessages((prev) => [...prev, switchNotice]);
  };

  const clearChat = () => {
    setMessages([
      {
        ...getGreeting(selectedOutlet),
        id: `msg_${Date.now()}`,
        content: `Conversation refreshed. Welcome to **${selectedOutlet.name}**. How may I assist you this evening?`,
      },
    ]);
    setHandoverRequested(false);
  };

  const provideFeedback = async (id: string, feedback: 'UP' | 'DOWN') => {
    setMessages((prev) =>
      prev.map((msg) => (msg.id === id ? { ...msg, feedback } : msg))
    );
    try {
      await apiRequest('/chat/feedback', {
        method: 'POST',
        body: JSON.stringify({ message_id: id, rating: feedback }),
      });
    } catch (e) {
      console.warn('Feedback recording skipped:', e);
    }
  };

  const requestHandover = async () => {
    setHandoverRequested(true);
    const handoverNotice: ChatMessage = {
      id: `msg_${Date.now()}`,
      sender: 'SYSTEM',
      environment,
      content: `A priority notification has been dispatched to the Guest Relations Desk at **${selectedOutlet.name}**. A concierge team member will connect with you shortly. You may also reach our concierge desk directly at **+91 11 4050 9900** or **guestrelations@amithospitality.com**.`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
    setMessages((prev) => [...prev, handoverNotice]);

    try {
      await apiRequest('/chat/handover', {
        method: 'POST',
        body: JSON.stringify({ outlet_id: selectedOutlet.id }),
      });
    } catch (e) {
      console.warn('Handover notification recorded locally.');
    }
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

    try {
      // Real API Call to RAG backend
      const res = await apiRequest<BackendChatResponse>('/chat/messages', {
        method: 'POST',
        body: JSON.stringify({
          session_id: sessionId,
          outlet_id: selectedOutlet.id,
          message: userText,
          language,
        }),
      });

      const assistantMsg: ChatMessage = {
        id: `assist_${Date.now()}`,
        sender: 'ASSISTANT',
        environment: res.environment,
        content: res.reply,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        citations: res.citations?.map((c) => ({
          documentTitle: c.document_title,
          category: c.category,
          snippet: c.snippet,
        })),
        suggestedActions: res.suggested_actions,
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      console.error('Chat API error:', err);
      const errorMsg: ChatMessage = {
        id: `assist_err_${Date.now()}`,
        sender: 'ASSISTANT',
        environment,
        content: `I apologize for the brief pause. Our luxury concierge service is momentarily reconnecting. Please feel free to retry your inquiry, or connect with our Guest Relations Desk directly at **+91 11 4050 9900**.`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        suggestedActions: ['Retry inquiry', 'Connect me with guest relations'],
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <ChatContext.Provider
      value={{
        messages,
        selectedOutlet,
        setSelectedOutlet: handleOutletChange,
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
