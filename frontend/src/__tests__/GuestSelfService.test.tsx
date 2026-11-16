import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { GuestSelfServicePage } from '../pages/customer/GuestSelfServicePage';
import { EnvironmentProvider } from '../context/EnvironmentContext';
import * as guestApi from '../api/guest';

vi.mock('../api/guest');

const renderGuestSelfService = () => {
  return render(
    <EnvironmentProvider>
      <GuestSelfServicePage />
    </EnvironmentProvider>
  );
};

describe('Guest Self-Service Portal Experience', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders booking lookup form with reference and contact input fields', () => {
    renderGuestSelfService();

    expect(screen.getByText('Manage Your Reservation')).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/REF-RES-20261110-XXXXXX/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/guest@example.com/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Verify & Access Reservation/i })).toBeInTheDocument();
  });

  it('displays error message when lookup fails', async () => {
    vi.mocked(guestApi.lookupReservationApi).mockRejectedValueOnce(
      new Error('No booking found matching the provided reference and contact details.')
    );

    renderGuestSelfService();

    const refInput = screen.getByPlaceholderText(/REF-RES-20261110-XXXXXX/i);
    const contactInput = screen.getByPlaceholderText(/guest@example.com/i);
    const submitBtn = screen.getByRole('button', { name: /Verify & Access Reservation/i });

    fireEvent.change(refInput, { target: { value: 'REF-INVALID-001' } });
    fireEvent.change(contactInput, { target: { value: '+919999999999' } });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText(/No booking found matching the provided reference/i)).toBeInTheDocument();
    });
  });

  it('transitions to OTP verification step on successful lookup', async () => {
    vi.mocked(guestApi.lookupReservationApi).mockResolvedValueOnce({
      status: 'VERIFICATION_DISPATCHED',
      reference_id: 'REF-RES-20261110-ABC123',
      target_type: 'PHONE',
      target_masked: '+91 ****** 0001',
      expires_in_seconds: 600,
      demo_otp: '543210',
    });

    renderGuestSelfService();

    fireEvent.change(screen.getByPlaceholderText(/REF-RES-20261110-XXXXXX/i), {
      target: { value: 'REF-RES-20261110-ABC123' },
    });
    fireEvent.change(screen.getByPlaceholderText(/guest@example.com/i), {
      target: { value: '+919876500001' },
    });
    fireEvent.click(screen.getByRole('button', { name: /Verify & Access Reservation/i }));

    await waitFor(() => {
      expect(screen.getByText('Enter 6-Digit Verification Code')).toBeInTheDocument();
      expect(screen.getByText('+91 ****** 0001')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Confirm Verification Code/i })).toBeInTheDocument();
    });
  });

  it('verifies OTP and renders verified reservation details portal', async () => {
    vi.mocked(guestApi.lookupReservationApi).mockResolvedValueOnce({
      status: 'VERIFICATION_DISPATCHED',
      reference_id: 'REF-RES-20261110-ABC123',
      target_type: 'PHONE',
      target_masked: '+91 ****** 0001',
      expires_in_seconds: 600,
      demo_otp: '543210',
    });

    vi.mocked(guestApi.verifyOtpApi).mockResolvedValueOnce({
      access_token: 'mock-signed-guest-token',
      token_type: 'bearer',
      expires_in_seconds: 1800,
      reservation: {
        id: 10,
        reference_id: 'REF-RES-20261110-ABC123',
        outlet_name: 'Amber Terrace Rooftop',
        outlet_id: 1,
        guest_name: 'Priyanka Sen',
        guest_phone: '+919876500001',
        guest_count: 2,
        reservation_date: '2026-12-30',
        reservation_time: '20:30',
        seating_preference: 'ROOFTOP',
        special_requests: 'Anniversary celebration',
        status: 'CONFIRMED',
        can_modify: true,
        can_cancel: true,
        outlet_opening_time: '18:00',
        outlet_closing_time: '01:00',
        outlet_location: 'Level 12, Tower A',
        outlet_dress_code: 'Glamorous Evening',
      },
    });

    renderGuestSelfService();

    // 1. Lookup
    fireEvent.change(screen.getByPlaceholderText(/REF-RES-20261110-XXXXXX/i), {
      target: { value: 'REF-RES-20261110-ABC123' },
    });
    fireEvent.change(screen.getByPlaceholderText(/guest@example.com/i), {
      target: { value: '+919876500001' },
    });
    fireEvent.click(screen.getByRole('button', { name: /Verify & Access Reservation/i }));

    // 2. Verify OTP
    await waitFor(() => {
      expect(screen.getByText('Enter 6-Digit Verification Code')).toBeInTheDocument();
    });

    const verifyBtn = screen.getByRole('button', { name: /Confirm Verification Code/i });
    fireEvent.click(verifyBtn);

    // 3. Portal details rendered
    await waitFor(() => {
      expect(screen.getByText('Amber Terrace Rooftop')).toBeInTheDocument();
      expect(screen.getByText('2026-12-30')).toBeInTheDocument();
      expect(screen.getByText('20:30')).toBeInTheDocument();
      expect(screen.getByText('2 Guests')).toBeInTheDocument();
      expect(screen.getByText(/Confirmed Table/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Modify Booking/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Cancel Reservation/i })).toBeInTheDocument();
    });
  });
});
