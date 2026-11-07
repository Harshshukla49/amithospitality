import { apiRequest } from './client';
import { Lead, LeadStatus, LeadType } from '../types';

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
}

export interface BackendLead {
  id: number;
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
  status: LeadStatus;
  assigned_staff_id?: number;
  created_at: string;
  updated_at?: string;
}

export function mapBackendLead(l: BackendLead): Lead {
  return {
    id: l.id,
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
  environment?: string;
}): Promise<Lead[]> {
  const queryParts: string[] = [];
  if (params?.outlet_id) queryParts.push(`outlet_id=${params.outlet_id}`);
  if (params?.status && params.status !== 'ALL') queryParts.push(`status=${params.status}`);
  if (params?.environment) queryParts.push(`environment=${params.environment}`);

  const qs = queryParts.length > 0 ? `?${queryParts.join('&')}` : '';
  const res = await apiRequest<BackendLead[]>(`/leads${qs}`);
  return res.map(mapBackendLead);
}

export async function updateLeadStatusApi(
  id: number,
  status: LeadStatus,
  notes?: string
): Promise<Lead> {
  const res = await apiRequest<BackendLead>(`/leads/${id}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status, notes }),
  });
  return mapBackendLead(res);
}

export async function exportLeadsCsv(environment?: string): Promise<Blob> {
  const token = localStorage.getItem('amit_access_token');
  const envParam = environment ? `?environment=${environment}` : '';
  const headers: HeadersInit = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`/api/v1/leads/export${envParam}`, { headers });
  if (!res.ok) throw new Error('Failed to export leads CSV');
  return res.blob();
}
