import { apiRequest } from './client';

export interface GuestProfileSummary {
  id: number;
  guest_uuid: string;
  environment: string;
  full_name: string;
  phone: string;
  email?: string;
  preferred_channel: string;
  dietary_preferences: string;
  allergies?: string;
  cuisine_preferences?: string;
  special_occasions?: string;
  accessibility_requirements?: string;
  staff_notes?: string;
  vip_status: boolean;
  total_visits: number;
  total_spend?: number;
  preferred_outlet_id?: number;
  preferred_outlet_name?: string;
  created_at?: string;
  updated_at?: string;
}

export interface GuestProfileDetail extends GuestProfileSummary {
  reservations: {
    id: number;
    reference_id: string;
    outlet_name: string;
    outlet_id: number;
    reservation_date: string;
    reservation_time: string;
    guest_count: number;
    status: string;
    seating_preference: string;
    special_requests?: string;
    created_at?: string;
  }[];
  communication_logs: {
    id: number;
    channel: string;
    event_type: string;
    status: string;
    recipient: string;
    reference_id?: string;
    created_at?: string;
  }[];
}

export interface ModificationRequestItem {
  id: number;
  reservation_id: number;
  reference_id: string;
  requested_by: string;
  old_date: string;
  new_date: string;
  old_time: string;
  new_time: string;
  old_guest_count: number;
  new_guest_count: number;
  old_special_requests?: string;
  new_special_requests?: string;
  status: string;
  review_notes?: string;
  reviewed_by_name?: string;
  created_at?: string;
}

export async function fetchGuestsApi(params?: {
  outlet_id?: number;
  search?: string;
  vip_only?: boolean;
  dietary?: string;
  environment?: string;
  skip?: number;
  limit?: number;
}): Promise<{ guests: GuestProfileSummary[]; total: number; skip: number; limit: number }> {
  const query = new URLSearchParams();
  if (params?.outlet_id) query.set('outlet_id', params.outlet_id.toString());
  if (params?.search) query.set('search', params.search);
  if (params?.vip_only) query.set('vip_only', 'true');
  if (params?.dietary) query.set('dietary', params.dietary);
  if (params?.environment) query.set('environment', params.environment);
  if (params?.skip) query.set('skip', params.skip.toString());
  if (params?.limit) query.set('limit', params.limit.toString());

  const qs = query.toString() ? `?${query.toString()}` : '';
  return apiRequest(`/crm/guests${qs}`, { method: 'GET' });
}

export async function fetchGuestProfileApi(guestId: number): Promise<GuestProfileDetail> {
  return apiRequest<GuestProfileDetail>(`/crm/guests/${guestId}`, { method: 'GET' });
}

export async function updateGuestProfileApi(
  guestId: number,
  data: Partial<GuestProfileSummary>
): Promise<GuestProfileDetail> {
  return apiRequest<GuestProfileDetail>(`/crm/guests/${guestId}`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function fetchModificationRequestsApi(
  status?: string
): Promise<ModificationRequestItem[]> {
  const qs = status ? `?status=${status}` : '';
  return apiRequest<ModificationRequestItem[]>(`/crm/modification-requests${qs}`, {
    method: 'GET',
  });
}

export async function reviewModificationRequestApi(
  requestId: number,
  action: 'APPROVE' | 'REJECT',
  reviewNotes?: string
): Promise<{ status: string; message: string; request_id: number }> {
  return apiRequest(`/crm/modification-requests/${requestId}/review`, {
    method: 'POST',
    body: JSON.stringify({ action, review_notes: reviewNotes }),
  });
}
