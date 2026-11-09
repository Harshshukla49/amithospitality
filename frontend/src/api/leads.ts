import { apiRequest, API_BASE_URL } from './client';
import { Lead, LeadStatus, LeadType, LeadHistoryItem } from '../types';

export interface CreateLeadPayload {
  outlet_id: number;
  name: string;
  phone: string;
  email: string;
  enquiry_type: LeadType;
  guest_count: number;
  target_date: string;
  budget_range: string;
  notes?: string;
  internal_notes?: string;
  assigned_staff_name?: string;
  source?: string;
  conversation_id?: number;
  session_id?: string;
}

export interface BackendLead {
  id: number;
  reference_id?: string;
  environment: 'DEMO' | 'REAL';
  outlet_id: number;
  outlet_name: string;
  name: string;
  phone: string;
  email: string;
  enquiry_type: LeadType;
  guest_count: number;
  target_date: string;
  budget_range: string;
  notes?: string;
  internal_notes?: string;
  status: LeadStatus;
  assigned_staff_id?: number;
  assigned_staff_name?: string;
  source?: string;
  conversation_id?: number;
  session_id?: string;
  created_at: string;
  updated_at?: string;
}

export function mapBackendLead(l: BackendLead): Lead {
  return {
    id: l.id,
    referenceId: l.reference_id,
    environment: l.environment,
    outletId: l.outlet_id,
    outletName: l.outlet_name,
    name: l.name,
    phone: l.phone,
    email: l.email,
    enquiryType: l.enquiry_type,
    guestCount: l.guest_count,
    targetDate: l.target_date,
    budgetRange: l.budget_range,
    status: l.status,
    notes: l.notes,
    internalNotes: l.internal_notes,
    assignedStaffName: l.assigned_staff_name,
    source: l.source,
    conversationId: l.conversation_id,
    sessionId: l.session_id,
    createdAt: l.created_at,
  };
}

export async function createLeadApi(data: CreateLeadPayload): Promise<Lead> {
  const res = await apiRequest<BackendLead>('/leads', {
    method: 'POST',
    body: JSON.stringify(data),
  });
  return mapBackendLead(res);
}

export async function fetchLeadsApi(params?: {
  outlet_id?: number;
  status?: string;
  enquiry_type?: string;
  search?: string;
  environment?: string;
}): Promise<Lead[]> {
  const queryParts: string[] = [];
  if (params?.outlet_id) queryParts.push(`outlet_id=${params.outlet_id}`);
  if (params?.status && params.status !== 'ALL') queryParts.push(`status=${params.status}`);
  if (params?.enquiry_type && params.enquiry_type !== 'ALL') queryParts.push(`enquiry_type=${encodeURIComponent(params.enquiry_type)}`);
  if (params?.search) queryParts.push(`search=${encodeURIComponent(params.search)}`);
  if (params?.environment) queryParts.push(`environment=${params.environment}`);

  const qs = queryParts.length > 0 ? `?${queryParts.join('&')}` : '';
  const res = await apiRequest<BackendLead[]>(`/leads${qs}`);
  return res.map(mapBackendLead);
}

export async function updateLeadStatusApi(
  id: number,
  status: LeadStatus,
  notes?: string,
  assignedStaffName?: string
): Promise<Lead> {
  const res = await apiRequest<BackendLead>(`/leads/${id}/status`, {
    method: 'PATCH',
    body: JSON.stringify({
      status,
      notes,
      assigned_staff_name: assignedStaffName,
    }),
  });
  return mapBackendLead(res);
}

export async function fetchLeadHistoryApi(id: number): Promise<LeadHistoryItem[]> {
  const res = await apiRequest<Array<{
    id: number;
    lead_id: number;
    previous_status: string | null;
    new_status: string;
    changed_by_name: string;
    notes?: string;
    created_at: string;
  }>>(`/leads/${id}/history`);
  return res.map((item) => ({
    id: item.id,
    leadId: item.lead_id,
    previousStatus: item.previous_status,
    newStatus: item.new_status,
    changedByName: item.changed_by_name,
    notes: item.notes,
    createdAt: item.created_at,
  }));
}

export async function exportLeadsCsv(environment?: string): Promise<Blob> {
  const token = localStorage.getItem('amit_access_token');
  const envParam = environment ? `?environment=${environment}` : '';
  const headers: HeadersInit = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE_URL}/api/v1/leads/export${envParam}`, { headers });
  if (!res.ok) throw new Error('Failed to export leads CSV');
  return res.blob();
}
