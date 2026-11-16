import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { AppContent } from '../App';
import { AuthProvider } from '../context/AuthContext';
import { EnvironmentProvider } from '../context/EnvironmentContext';
import { ChatProvider } from '../context/ChatContext';

vi.mock('../api/reservations', () => ({
  fetchReservationsApi: vi.fn().mockResolvedValue([]),
  createReservationApi: vi.fn().mockResolvedValue({ referenceId: 'RES-TEST-123456' }),
  updateReservationStatusApi: vi.fn().mockResolvedValue({}),
}));

vi.mock('../api/leads', () => ({
  fetchLeadsApi: vi.fn().mockResolvedValue([]),
  createLeadApi: vi.fn().mockResolvedValue({ referenceId: 'REF-LEAD-TEST-123' }),
  updateLeadStatusApi: vi.fn().mockResolvedValue({}),
}));

vi.mock('../api/audit', () => ({
  fetchAuditLogsApi: vi.fn().mockResolvedValue([]),
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

describe('Amit Hospitality — Public Website Brand & Experience Pages', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  it('renders Homepage with cinematic hero, company intro, and brand portfolio', async () => {
    renderWithProviders('/');

    expect(screen.getAllByText(/Creating Experiences/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Crafting Memories/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Amit Hospitality/i).length).toBeGreaterThan(0);

    // Verify all 4 brand cards are rendered on the homepage
    expect(screen.getAllByText('Lord of the Drinks').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Veneto Kitchen and Bar').length).toBeGreaterThan(0);
    expect(screen.getAllByText('The Warehouse Cafe').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Deliite').length).toBeGreaterThan(0);
  });

  it('renders Know Us / About Us page with founders and milestone timeline', async () => {
    renderWithProviders('/about');

    expect(screen.getAllByText(/The Amit Hospitality Story/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Amit & Vanita Bajoria/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/Inception of Amit Hospitality LLP/i)).toBeInTheDocument();
    expect(screen.getByText(/Lord of the Drinks Kolkata Opens/i)).toBeInTheDocument();
    expect(screen.getByText(/The Warehouse Cafe Opens/i)).toBeInTheDocument();
  });

  it('renders Lord of the Drinks brand page with Ghost Bar and South City Mall details', async () => {
    renderWithProviders('/brands/lord-of-drinks');

    expect(screen.getAllByText('Lord of the Drinks').length).toBeGreaterThan(0);
    expect(screen.getByText(/Kolkata's Tallest Bar/i)).toBeInTheDocument();
    expect(screen.getAllByText(/South City Mall/i).length).toBeGreaterThan(0);
    expect(screen.getByText('+91 9831568080')).toBeInTheDocument();
    expect(screen.getByText('gm@lodkolkata.com')).toBeInTheDocument();
  });

  it('renders Veneto Kitchen and Bar brand page with Italian cuisine and contacts', async () => {
    renderWithProviders('/brands/veneto');

    expect(screen.getAllByText('Veneto Kitchen & Bar').length).toBeGreaterThan(0);
    expect(screen.getByText(/Artisanal Italian Gastronomy/i)).toBeInTheDocument();
    expect(screen.getByText('+91 9831939515')).toBeInTheDocument();
    expect(screen.getByText('gm.veneto@amithospitality.com')).toBeInTheDocument();
  });

  it('renders The Warehouse Cafe page with Sunday Brunch and flagged numbers', async () => {
    renderWithProviders('/brands/warehouse');

    expect(screen.getAllByText('The Warehouse Cafe').length).toBeGreaterThan(0);
    expect(screen.getByText(/The Legendary Sunday Grand Brunch/i)).toBeInTheDocument();
    expect(screen.getByText('₹999')).toBeInTheDocument();
    expect(screen.getByText('+91 9830434580')).toBeInTheDocument();
    expect(screen.getByText(/Historical listing also referenced alternate number/i)).toBeInTheDocument();
  });

  it('renders Deliite brand page with Diamond Plaza Mall details and retail catalogue', async () => {
    renderWithProviders('/brands/deliite');

    expect(screen.getAllByText('Deliite').length).toBeGreaterThan(0);
    expect(screen.getByText(/Diamond Plaza Mall • Level 3/i)).toBeInTheDocument();
    expect(screen.getByText(/Data & Purchase Policy/i)).toBeInTheDocument();
  });

  it('renders Events page with historical concerts including Usha Uthup and S Factor', async () => {
    renderWithProviders('/events');

    expect(screen.getByText(/Events & Stage Experiences/i)).toBeInTheDocument();
    expect(screen.getByText(/S Factor Live at The Warehouse/i)).toBeInTheDocument();
    expect(screen.getByText(/Legendary Evening with Usha Uthup/i)).toBeInTheDocument();
    expect(screen.getByText(/Acoustic Soul by Kaushik Roy Chowdhury/i)).toBeInTheDocument();
  });

  it('renders Media & Gallery page with brand filter controls', async () => {
    renderWithProviders('/media');

    expect(screen.getByText(/Sensory Moments & Ambiance/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Lord of the Drinks/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Veneto Kitchen & Bar/i })).toBeInTheDocument();
  });

  it('renders Careers page with department choices and application form', async () => {
    renderWithProviders('/career');

    expect(screen.getByText(/Build Your Career in Premier Hospitality/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Candidate Name')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Submit Career Application/i })).toBeInTheDocument();
  });

  it('renders Contact directory page with corporate HQ and interactive maps', async () => {
    renderWithProviders('/contact');

    expect(screen.getByText(/Connect With Amit Hospitality/i)).toBeInTheDocument();
    expect(screen.getAllByText(/401 Kamalalaya Centre, 156A Lenin Sarani/i).length).toBeGreaterThan(0);
    expect(screen.getAllByText('vanita@amithospitality.com').length).toBeGreaterThan(0);
  });
});
