import { apiRequest } from './client';

export interface GuestLookupResult {
  status: string;
  reference_id: string;
  target_type: 'PHONE' | 'EMAIL';
  target_masked: string;
  expires_in_seconds: number;
  demo_otp?: string;
}

export interface GuestVerifyOtpResult {
  access_token: string;
  token_type: string;
  expires_in_seconds: number;
  reservation: GuestReservationDetails;
}

export interface GuestReservationDetails {
  id: number;
  reference_id: string;
  outlet_name: string;
  outlet_id: number;
  guest_name: string;
  guest_phone: string;
  guest_email?: string;
  guest_count: number;
  reservation_date: string;
  reservation_time: string;
  seating_preference: string;
  special_requests?: string;
  status: string;
  can_modify: boolean;
  can_cancel: boolean;
  outlet_opening_time: string;
  outlet_closing_time: string;
  outlet_location: string;
  outlet_dress_code: string;
  created_at?: string;
  updated_at?: string;
}

export async function lookupReservationApi(
  reference_id: string,
  contact: string
): Promise<GuestLookupResult> {
  return apiRequest<GuestLookupResult>('/guest/reservations/lookup', {
    method: 'POST',
    body: JSON.stringify({ reference_id, contact }),
  });
}

export async function verifyOtpApi(
  reference_id: string,
  otp: string
): Promise<GuestVerifyOtpResult> {
  return apiRequest<GuestVerifyOtpResult>('/guest/reservations/verify-otp', {
    method: 'POST',
    body: JSON.stringify({ reference_id, otp }),
  });
}

export async function getGuestReservationApi(
  reference_id: string,
  guestToken: string
): Promise<GuestReservationDetails> {
  return apiRequest<GuestReservationDetails>(`/guest/reservations/${reference_id}`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${guestToken}`,
    },
  });
}

export async function modifyGuestReservationApi(
  reference_id: string,
  guestToken: string,
  data: {
    reservation_date?: string;
    reservation_time?: string;
    guest_count?: number;
    special_requests?: string;
  }
): Promise<{ status: string; message: string; reservation: GuestReservationDetails }> {
  return apiRequest(`/guest/reservations/${reference_id}/modify`, {
    method: 'PATCH',
    headers: {
      Authorization: `Bearer ${guestToken}`,
    },
    body: JSON.stringify(data),
  });
}

export async function cancelGuestReservationApi(
  reference_id: string,
  guestToken: string,
  reason: string
): Promise<{ status: string; message: string; reservation: GuestReservationDetails }> {
  return apiRequest(`/guest/reservations/${reference_id}/cancel`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${guestToken}`,
    },
    body: JSON.stringify({ cancellation_reason: reason }),
  });
}
