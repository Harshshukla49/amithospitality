import React, { useState, useEffect } from 'react';
import { EnvironmentProvider, useEnvironment } from './context/EnvironmentContext';
import { AuthProvider } from './context/AuthContext';
import { ChatProvider } from './context/ChatContext';
import { Header } from './components/common/Header';
import { DemoBanner } from './components/common/DemoBanner';
import { SwitchEnvironmentModal } from './components/common/SwitchEnvironmentModal';
import { Sidebar, AdminTab } from './components/admin/Sidebar';
import { ConciergePage } from './pages/customer/ConciergePage';
import { DashboardPage } from './pages/admin/DashboardPage';
import { KnowledgePage } from './pages/admin/KnowledgePage';
import { OutletsPage } from './pages/admin/OutletsPage';
import { ReservationsPage } from './pages/admin/ReservationsPage';
import { LeadsPage } from './pages/admin/LeadsPage';
import { AnalyticsPage } from './pages/admin/AnalyticsPage';
import { SettingsPage } from './pages/admin/SettingsPage';
import {
  INITIAL_RESERVATIONS,
  INITIAL_LEADS,
  INITIAL_DOCUMENTS,
} from './utils/mockData';
import { ReservationRequest, Lead, KnowledgeDocument, ReservationStatus, LeadStatus } from './types';
import { fetchReservationsApi, updateReservationStatusApi } from './api/reservations';
import { fetchLeadsApi, updateLeadStatusApi } from './api/leads';

const MainLayout: React.FC = () => {
  const { environment } = useEnvironment();
  const [currentView, setCurrentView] = useState<'CUSTOMER' | 'ADMIN'>('CUSTOMER');
  const [adminTab, setAdminTab] = useState<AdminTab>('DASHBOARD');

  // Shared application state across Concierge and Admin Console
  const [reservations, setReservations] = useState<ReservationRequest[]>(INITIAL_RESERVATIONS);
  const [leads, setLeads] = useState<Lead[]>(INITIAL_LEADS);
  const [documents, setDocuments] = useState<KnowledgeDocument[]>(INITIAL_DOCUMENTS);

  // Sync live reservations and leads from backend
  useEffect(() => {
    let isMounted = true;
    fetchReservationsApi({ environment })
      .then((data) => {
        if (isMounted && data.length > 0) setReservations(data);
      })
      .catch((e) => console.warn('Backend reservations sync notice:', e));

    fetchLeadsApi({ environment })
      .then((data) => {
        if (isMounted && data.length > 0) setLeads(data);
      })
      .catch((e) => console.warn('Backend leads sync notice:', e));

    return () => {
      isMounted = false;
    };
  }, [environment]);

  const handleAddReservation = (res: ReservationRequest) => {
    setReservations((prev) => [res, ...prev]);
  };

  const handleUpdateReservationStatus = async (id: number, status: ReservationStatus, notes?: string) => {
    setReservations((prev) =>
      prev.map((r) => (r.id === id ? { ...r, status, internalNotes: notes || r.internalNotes } : r))
    );
    try {
      await updateReservationStatusApi(id, status, notes);
    } catch (e) {
      console.warn('Backend status update error:', e);
    }
  };

  const handleAddLead = (lead: Lead) => {
    setLeads((prev) => [lead, ...prev]);
  };

  const handleUpdateLeadStatus = async (id: number, status: LeadStatus, notes?: string) => {
    setLeads((prev) =>
      prev.map((l) => (l.id === id ? { ...l, status, notes: notes || l.notes } : l))
    );
    try {
      await updateLeadStatusApi(id, status, notes);
    } catch (e) {
      console.warn('Backend lead status update error:', e);
    }
  };

  const handleAddDocument = (doc: KnowledgeDocument) => {
    setDocuments((prev) => [doc, ...prev]);
  };

  const handleDeleteDocument = (id: number) => {
    setDocuments((prev) => prev.filter((d) => d.id !== id));
  };

  return (
    <div className="min-h-screen flex flex-col bg-obsidian-950 text-slate-100 font-sans">
      {/* Prominent Demo Mode Disclaimer Banner */}
      <DemoBanner />

      {/* Global Luxury Navigation Header */}
      <Header currentView={currentView} onViewChange={setCurrentView} />

      {/* Main View Port */}
      {currentView === 'CUSTOMER' ? (
        <main className="flex-1">
          <ConciergePage
            onReservationCreated={handleAddReservation}
            onLeadCreated={handleAddLead}
          />
        </main>
      ) : (
        <div className="flex-1 flex overflow-hidden">
          <Sidebar
            activeTab={adminTab}
            onTabChange={setAdminTab}
            reservationCount={
              reservations.filter((r) => r.status === 'NEW' || r.status === 'PENDING').length
            }
            leadCount={leads.filter((l) => l.status === 'NEW').length}
          />

          <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
            <div className="max-w-7xl mx-auto">
              {adminTab === 'DASHBOARD' && (
                <DashboardPage
                  reservations={reservations}
                  leads={leads}
                  documents={documents}
                  onNavigate={setAdminTab}
                />
              )}
              {adminTab === 'KNOWLEDGE' && (
                <KnowledgePage
                  documents={documents}
                  onAddDocument={handleAddDocument}
                  onDeleteDocument={handleDeleteDocument}
                />
              )}
              {adminTab === 'OUTLETS' && <OutletsPage />}
              {adminTab === 'RESERVATIONS' && (
                <ReservationsPage
                  reservations={reservations}
                  onUpdateStatus={handleUpdateReservationStatus}
                />
              )}
              {adminTab === 'LEADS' && (
                <LeadsPage leads={leads} onUpdateStatus={handleUpdateLeadStatus} />
              )}
              {adminTab === 'ANALYTICS' && <AnalyticsPage />}
              {adminTab === 'SETTINGS' && <SettingsPage />}
            </div>
          </main>
        </div>
      )}

      {/* Confirmation Modal for Environment Switching */}
      <SwitchEnvironmentModal />
    </div>
  );
};

export function App() {
  return (
    <AuthProvider>
      <EnvironmentProvider>
        <ChatProvider>
          <MainLayout />
        </ChatProvider>
      </EnvironmentProvider>
    </AuthProvider>
  );
}

export default App;
