import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { GuestCrmPage } from '../pages/admin/GuestCrmPage';
import { AuthProvider } from '../context/AuthContext';
import { EnvironmentProvider } from '../context/EnvironmentContext';
import * as crmApi from '../api/crm';

vi.mock('../api/crm');

const mockGuests = [
  {
    id: 1,
    guest_uuid: 'GST-AA11BB22CC',
    environment: 'DEMO',
    full_name: 'Kabir Oberoi',
    phone: '+919876543210',
    email: 'kabir.o@example.com',
    preferred_channel: 'SMS',
    dietary_preferences: 'VEGAN',
    allergies: 'Tree Nuts',
    cuisine_preferences: 'Pan-Asian',
    special_occasions: 'Anniversary: Nov 20',
    staff_notes: 'Prefers quiet booth table',
    vip_status: true,
    total_visits: 5,
    preferred_outlet_name: 'Amber Terrace Rooftop',
  },
  {
    id: 2,
    guest_uuid: 'GST-DD33EE44FF',
    environment: 'DEMO',
    full_name: 'Ananya Roy',
    phone: '+919811122233',
    email: 'ananya.r@example.com',
    preferred_channel: 'EMAIL',
    dietary_preferences: 'JAIN',
    allergies: '',
    vip_status: false,
    total_visits: 2,
    preferred_outlet_name: 'Saffron & Silk',
  },
];

const renderGuestCrm = () => {
  return render(
    <AuthProvider>
      <EnvironmentProvider>
        <GuestCrmPage />
      </EnvironmentProvider>
    </AuthProvider>
  );
};

describe('Admin Unified Guest CRM Directory & Management', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(crmApi.fetchGuestsApi).mockResolvedValue({
      guests: mockGuests,
      total: 2,
      skip: 0,
      limit: 50,
    });
    vi.mocked(crmApi.fetchModificationRequestsApi).mockResolvedValue([]);
  });

  it('renders guest directory header and list of guest profiles', async () => {
    renderGuestCrm();

    await waitFor(() => {
      expect(screen.getByText('Guest Relationship & Preferences Directory')).toBeInTheDocument();
      expect(screen.getByText('Kabir Oberoi')).toBeInTheDocument();
      expect(screen.getByText('Ananya Roy')).toBeInTheDocument();
      expect(screen.getByText('VIP')).toBeInTheDocument();
      expect(screen.getByText('VEGAN')).toBeInTheDocument();
      expect(screen.getByText('JAIN')).toBeInTheDocument();
    });
  });

  it('filters guests using search input', async () => {
    renderGuestCrm();

    await waitFor(() => {
      expect(screen.getByText('Kabir Oberoi')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText(/Search by guest name, phone, email/i);
    fireEvent.change(searchInput, { target: { value: 'Ananya' } });

    await waitFor(() => {
      expect(crmApi.fetchGuestsApi).toHaveBeenCalledWith(
        expect.objectContaining({ search: 'Ananya' })
      );
    });
  });

  it('opens guest profile modal and displays preferences and history', async () => {
    vi.mocked(crmApi.fetchGuestProfileApi).mockResolvedValueOnce({
      ...mockGuests[0],
      reservations: [
        {
          id: 101,
          reference_id: 'REF-RES-20261110-XYZ123',
          outlet_name: 'Amber Terrace Rooftop',
          outlet_id: 1,
          reservation_date: '2026-12-15',
          reservation_time: '20:00',
          guest_count: 4,
          status: 'ACCEPTED',
          seating_preference: 'ROOFTOP',
        },
      ],
      communication_logs: [
        {
          id: 501,
          channel: 'EMAIL',
          event_type: 'RESERVATION_ACCEPTED',
          status: 'SENT',
          recipient: 'kabir.o@example.com',
          reference_id: 'REF-RES-20261110-XYZ123',
        },
      ],
    });

    renderGuestCrm();

    await waitFor(() => {
      expect(screen.getByText('Kabir Oberoi')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Kabir Oberoi'));

    await waitFor(() => {
      expect(screen.getByText(/Preferences & Notes/i)).toBeInTheDocument();
      expect(screen.getByText(/Dining History \(1\)/i)).toBeInTheDocument();
      expect(screen.getByText(/Notifications & Audits \(1\)/i)).toBeInTheDocument();
      expect(screen.getByDisplayValue('Tree Nuts')).toBeInTheDocument();
    });
  });

  it('displays pending self-service modification requests banner', async () => {
    vi.mocked(crmApi.fetchModificationRequestsApi).mockResolvedValueOnce([
      {
        id: 77,
        reservation_id: 10,
        reference_id: 'REF-RES-20261110-STAGED',
        requested_by: 'GUEST',
        old_date: '2026-12-10',
        new_date: '2026-12-12',
        old_time: '20:00',
        new_time: '21:00',
        old_guest_count: 2,
        new_guest_count: 8,
        status: 'PENDING_APPROVAL',
      },
    ]);

    renderGuestCrm();

    await waitFor(() => {
      expect(screen.getByText(/Pending Guest Self-Service Modifications/i)).toBeInTheDocument();
      expect(screen.getByText('REF-RES-20261110-STAGED')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Approve Table/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Reject/i })).toBeInTheDocument();
    });
  });
});
