import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { AppContent } from '../App';
import { AuthProvider } from '../context/AuthContext';
import { EnvironmentProvider } from '../context/EnvironmentContext';
import { ChatProvider } from '../context/ChatContext';

// Mock API calls made on mount
vi.mock('../api/reservations', () => ({
  fetchReservationsApi: vi.fn().mockResolvedValue([]),
  updateReservationStatusApi: vi.fn().mockResolvedValue({}),
}));

vi.mock('../api/leads', () => ({
  fetchLeadsApi: vi.fn().mockResolvedValue([]),
  updateLeadStatusApi: vi.fn().mockResolvedValue({}),
}));

const renderWithProviders = (initialRoute: string) => {
  return render(
    <AuthProvider>
      <EnvironmentProvider>
        <ChatProvider>
          <MemoryRouter initialEntries={[initialRoute]}>
            <AppContent />
          </MemoryRouter>
        </ChatProvider>
      </EnvironmentProvider>
    </AuthProvider>
  );
};

describe('React Router & Role-Based Navigation System', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  it('renders public login page at /login with credentials form and brand header', async () => {
    renderWithProviders('/login');

    expect(screen.getAllByText('AMIT HOSPITALITY').length).toBeGreaterThan(0);
    expect(screen.getByPlaceholderText('name@amithospitality.com')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Sign In to Admin Portal/i })).toBeInTheDocument();
  });

  it('renders 404 page for non-existent routes', async () => {
    renderWithProviders('/non-existent-luxury-suite');

    expect(screen.getByText('404')).toBeInTheDocument();
    expect(screen.getByText('Dining Destination Not Found')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Return to Concierge/i })).toBeInTheDocument();
  });

  it('renders 403 Forbidden page at /unauthorized', async () => {
    renderWithProviders('/unauthorized');

    expect(screen.getByText('403 Forbidden')).toBeInTheDocument();
    expect(screen.getByText('Access Restricted')).toBeInTheDocument();
  });

  it('redirects unauthenticated user from protected /admin/dashboard to /login', async () => {
    // Explicitly flag as logged out
    localStorage.setItem('amit_concierge_logged_out', 'true');

    renderWithProviders('/admin/dashboard');

    await waitFor(() => {
      expect(screen.getAllByText('AMIT HOSPITALITY').length).toBeGreaterThan(0);
      expect(screen.getByRole('button', { name: /Sign In to Admin Portal/i })).toBeInTheDocument();
    });
  });

  it('allows authenticated SUPER_ADMIN to access /admin/dashboard', async () => {
    localStorage.setItem(
      'amit_concierge_user',
      JSON.stringify({
        id: 1,
        email: 'admin@amithospitality.com',
        fullName: 'Vikram Sharma',
        role: 'SUPER_ADMIN',
      })
    );

    renderWithProviders('/admin/dashboard');

    await waitFor(() => {
      expect(screen.getByText('Hospitality Intelligence & Operations')).toBeInTheDocument();
    });
  });

  it('redirects STAFF role to /unauthorized when attempting to access /admin/settings', async () => {
    localStorage.setItem(
      'amit_concierge_user',
      JSON.stringify({
        id: 4,
        email: 'staff@amithospitality.com',
        fullName: 'Priya Nair',
        role: 'STAFF',
        outletId: 1,
      })
    );

    renderWithProviders('/admin/settings');

    await waitFor(() => {
      expect(screen.getByText('403 Forbidden')).toBeInTheDocument();
      expect(screen.getByText('Access Restricted')).toBeInTheDocument();
    });
  });
});
