import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { EnvironmentProvider, useEnvironment } from './context/EnvironmentContext';
import { AuthProvider } from './context/AuthContext';
import { ChatProvider } from './context/ChatContext';
import { Header } from './components/common/Header';
import { DemoBanner } from './components/common/DemoBanner';
import { SwitchEnvironmentModal } from './components/common/SwitchEnvironmentModal';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { ProtectedRoute } from './components/common/ProtectedRoute';
import { Sidebar } from './components/admin/Sidebar';
import { ConciergePage } from './pages/customer/ConciergePage';
import { DashboardPage } from './pages/admin/DashboardPage';
import { KnowledgePage } from './pages/admin/KnowledgePage';
import { OutletsPage } from './pages/admin/OutletsPage';
import { ReservationsPage } from './pages/admin/ReservationsPage';
import { LeadsPage } from './pages/admin/LeadsPage';
import { AnalyticsPage } from './pages/admin/AnalyticsPage';
import { IntegrationsPage } from './pages/admin/IntegrationsPage';
import { SettingsPage } from './pages/admin/SettingsPage';
import { GuestCrmPage } from './pages/admin/GuestCrmPage';
import { GuestSelfServicePage } from './pages/customer/GuestSelfServicePage';
import { LoginPage } from './pages/auth/LoginPage';
import { NotFoundPage } from './pages/common/NotFoundPage';
import { UnauthorizedPage } from './pages/common/UnauthorizedPage';
import {
  INITIAL_RESERVATIONS,
  INITIAL_LEADS,
  INITIAL_DOCUMENTS,
} from './utils/mockData';
import { ReservationRequest, Lead, KnowledgeDocument, ReservationStatus, LeadStatus } from './types';
import { fetchReservationsApi, updateReservationStatusApi } from './api/reservations';
import { fetchLeadsApi, updateLeadStatusApi } from './api/leads';

interface AdminLayoutWrapperProps {
  reservations: ReservationRequest[];
  leads: Lead[];
  children: React.ReactNode;
}

const AdminLayoutWrapper: React.FC<AdminLayoutWrapperProps> = ({ reservations, leads, children }) => {
  return (
    <div className="flex-1 flex overflow-hidden">
      <Sidebar
        reservationCount={
          reservations.filter((r) => r.status === 'NEW' || r.status === 'PENDING').length
        }
        leadCount={leads.filter((l) => l.status === 'NEW').length}
      />
      <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
        <div className="max-w-7xl mx-auto">{children}</div>
      </main>
    </div>
  );
};

export const AppContent: React.FC = () => {
  const { environment } = useEnvironment();
  const location = useLocation();

  const [reservations, setReservations] = useState<ReservationRequest[]>(INITIAL_RESERVATIONS);
  const [leads, setLeads] = useState<Lead[]>(INITIAL_LEADS);
  const [documents, setDocuments] = useState<KnowledgeDocument[]>(INITIAL_DOCUMENTS);

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

  const handleUpdateReservationStatus = async (
    id: number,
    status: ReservationStatus,
    notes?: string,
    assignedStaffName?: string
  ) => {
    setReservations((prev) =>
      prev.map((r) =>
        r.id === id
          ? {
              ...r,
              status,
              internalNotes: notes || r.internalNotes,
              assignedStaffName: assignedStaffName || r.assignedStaffName,
            }
          : r
      )
    );
    try {
      await updateReservationStatusApi(id, status, notes, assignedStaffName);
    } catch (e) {
      console.warn('Backend status update error:', e);
    }
  };

  const handleAddLead = (lead: Lead) => {
    setLeads((prev) => [lead, ...prev]);
  };

  const handleUpdateLeadStatus = async (
    id: number,
    status: LeadStatus,
    notes?: string,
    assignedStaffName?: string
  ) => {
    setLeads((prev) =>
      prev.map((l) =>
        l.id === id
          ? {
              ...l,
              status,
              notes: notes || l.notes,
              internalNotes: notes || l.internalNotes,
              assignedStaffName: assignedStaffName || l.assignedStaffName,
            }
          : l
      )
    );
    try {
      await updateLeadStatusApi(id, status, notes, assignedStaffName);
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

  const isEmbedded = typeof window !== 'undefined' && (
    window.location.search.includes('embed=true') ||
    window.self !== window.top
  );

  const isLoginPage = location.pathname === '/login';
  const isUnauthorizedPage = location.pathname === '/unauthorized';

  return (
    <div className="min-h-screen flex flex-col bg-obsidian-950 text-slate-100 font-sans">
      {/* Prominent Demo Mode Disclaimer Banner */}
      {!isEmbedded && !isLoginPage && <DemoBanner />}

      {/* Global Luxury Navigation Header */}
      {!isEmbedded && !isLoginPage && !isUnauthorizedPage && <Header />}

      {/* Routes Viewport */}
      <Routes>
        {/* Customer Concierge Routes */}
        <Route path="/" element={<Navigate to={`/concierge${location.search}`} replace />} />
        <Route
          path="/concierge"
          element={
            <main className="flex-1">
              <ConciergePage
                onReservationCreated={handleAddReservation}
                onLeadCreated={handleAddLead}
                isEmbedded={isEmbedded}
              />
            </main>
          }
        />
        <Route
          path="/guest/reservations"
          element={
            <main className="flex-1">
              <GuestSelfServicePage />
            </main>
          }
        />

        {/* Auth Route */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/unauthorized" element={<UnauthorizedPage />} />

        {/* Protected Enterprise Admin Routes */}
        <Route
          path="/admin"
          element={<Navigate to="/admin/dashboard" replace />}
        />
        <Route
          path="/admin/dashboard"
          element={
            <ProtectedRoute allowedRoles={['SUPER_ADMIN', 'ADMIN', 'MANAGER', 'STAFF']}>
              <AdminLayoutWrapper reservations={reservations} leads={leads}>
                <DashboardPage
                  reservations={reservations}
                  leads={leads}
                  documents={documents}
                  onNavigate={() => {}}
                />
              </AdminLayoutWrapper>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/knowledge"
          element={
            <ProtectedRoute allowedRoles={['SUPER_ADMIN', 'ADMIN']}>
              <AdminLayoutWrapper reservations={reservations} leads={leads}>
                <KnowledgePage
                  documents={documents}
                  onAddDocument={handleAddDocument}
                  onDeleteDocument={handleDeleteDocument}
                />
              </AdminLayoutWrapper>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/outlets"
          element={
            <ProtectedRoute allowedRoles={['SUPER_ADMIN', 'ADMIN', 'MANAGER']}>
              <AdminLayoutWrapper reservations={reservations} leads={leads}>
                <OutletsPage />
              </AdminLayoutWrapper>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/guests"
          element={
            <ProtectedRoute allowedRoles={['SUPER_ADMIN', 'ADMIN', 'MANAGER', 'STAFF']}>
              <AdminLayoutWrapper reservations={reservations} leads={leads}>
                <GuestCrmPage />
              </AdminLayoutWrapper>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/reservations"
          element={
            <ProtectedRoute allowedRoles={['SUPER_ADMIN', 'ADMIN', 'MANAGER', 'STAFF']}>
              <AdminLayoutWrapper reservations={reservations} leads={leads}>
                <ReservationsPage
                  reservations={reservations}
                  onUpdateStatus={handleUpdateReservationStatus}
                />
              </AdminLayoutWrapper>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/leads"
          element={
            <ProtectedRoute allowedRoles={['SUPER_ADMIN', 'ADMIN', 'MANAGER', 'STAFF']}>
              <AdminLayoutWrapper reservations={reservations} leads={leads}>
                <LeadsPage
                  leads={leads}
                  onUpdateStatus={handleUpdateLeadStatus}
                  onAddLead={handleAddLead}
                />
              </AdminLayoutWrapper>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/analytics"
          element={
            <ProtectedRoute allowedRoles={['SUPER_ADMIN', 'ADMIN', 'MANAGER', 'STAFF']}>
              <AdminLayoutWrapper reservations={reservations} leads={leads}>
                <AnalyticsPage />
              </AdminLayoutWrapper>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/integrations"
          element={
            <ProtectedRoute allowedRoles={['SUPER_ADMIN', 'ADMIN']}>
              <AdminLayoutWrapper reservations={reservations} leads={leads}>
                <IntegrationsPage />
              </AdminLayoutWrapper>
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin/settings"
          element={
            <ProtectedRoute allowedRoles={['SUPER_ADMIN', 'ADMIN']}>
              <AdminLayoutWrapper reservations={reservations} leads={leads}>
                <SettingsPage />
              </AdminLayoutWrapper>
            </ProtectedRoute>
          }
        />

        {/* 404 Catch-All */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>

      {/* Confirmation Modal for Environment Switching */}
      <SwitchEnvironmentModal />
    </div>
  );
};

export function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <EnvironmentProvider>
          <ChatProvider>
            <BrowserRouter>
              <AppContent />
            </BrowserRouter>
          </ChatProvider>
        </EnvironmentProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
