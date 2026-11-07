import { apiRequest } from './client';
import { ReservationRequest, ReservationStatus } from '../types';

export interface CreateReservationPayload {
  outlet_id: number;
  guest_name: string;
  guest_phone: string;
  guest_email?: string;
  guest_count: number;
  reservation_date: string;
  reservation_time: string;
  seating_preference: string;
  special_requests?: string;
}

export interface BackendReservation {
  id: number;
  environment: 'DEMO' | 'REAL';
  outlet_id: number;
  outlet_name: string;
  guest_name: string;
  guest_phone: string;
  guest_email?: string;
  guest_count: number;
  reservation_date: string;
  reservation_time: string;
  seating_preference: 'INDOOR' | 'OUTDOOR' | 'ROOFTOP' | 'PRIVATE';
  special_requests?: string;
  status: ReservationStatus;
  internal_notes?: string;
  assigned_staff_id?: number;
  created_at: string;
  updated_at?: string;
}

export function mapBackendReservation(r: BackendReservation): ReservationRequest {
  return {
    id: r.id,
    environment: r.environment,
    outletId: r.outlet_id,
    outletName: r.outlet_name,
    guestName: r.guest_name,
    guestPhone: r.guest_phone,
    guestEmail: r.guest_email || '',
    guestCount: r.guest_count,
    reservationDate: r.reservation_date,
    reservationTime: r.reservation_time,
    seatingPreference: r.seating_preference,
    specialRequests: r.special_requests,
    status: r.status,
    internalNotes: r.internal_notes,
    createdAt: r.created_at,
  };
}

export async function createReservationApi(data: CreateReservationPayload): Promise<ReservationRequest> {
  const res = await apiRequest<BackendReservation>('/reservations', {
    method: 'POST',
    body: JSON.stringify(data),
  });
  return mapBackendReservation(res);
}

export async function fetchReservationsApi(params?: {
  outlet_id?: number;
  status?: string;
  environment?: string;
}): Promise<ReservationRequest[]> {
  const queryParts: string[] = [];
  if (params?.outlet_id) queryParts.push(`outlet_id=${params.outlet_id}`);
  if (params?.status && params.status !== 'ALL') queryParts.push(`status=${params.status}`);
  if (params?.environment) queryParts.push(`environment=${params.environment}`);

  const qs = queryParts.length > 0 ? `?${queryParts.join('&')}` : '';
  const res = await apiRequest<BackendReservation[]>(`/reservations${qs}`);
  return res.map(mapBackendReservation);
}

export async function updateReservationStatusApi(
  id: number,
  status: ReservationStatus,
  internalNotes?: string
): Promise<ReservationRequest> {
  const res = await apiRequest<BackendReservation>(`/reservations/${id}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status, internal_notes: internalNotes }),
  });
  return mapBackendReservation(res);
}

export async function exportReservationsCsv(environment?: string): Promise<Blob> {
  const token = localStorage.getItem('amit_access_token');
  const envParam = environment ? `?environment=${environment}` : '';
  const headers: HeadersInit = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`/api/v1/reservations/export${envParam}`, { headers });
  if (!res.ok) throw new Error('Failed to export CSV');
  return res.blob();
}
