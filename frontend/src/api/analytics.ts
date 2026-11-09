import { apiRequest, API_BASE_URL } from './client';

export interface FrequentQuery {
  query: string;
  count: number;
  category: string;
}

export interface UnansweredQuestion {
  question: string;
  frequency: number;
  outlet: string;
  suggestion: string;
}

export interface DashboardKPIData {
  total_conversations: number;
  pending_reservations: number;
  total_leads: number;
  active_documents: number;
  active_environment: string;
  total_covers?: number;
  accepted_reservations?: number;
  reservation_status_breakdown?: Record<string, number>;
  lead_status_breakdown?: Record<string, number>;
  lead_type_breakdown?: Record<string, number>;
  date_range?: string;
  outlet_id?: number;
  outlet_name?: string;
  frequent_queries: FrequentQuery[];
  unanswered_questions: UnansweredQuestion[];
}

export async function fetchDashboardKPIs(params?: {
  date_range?: string;
  outlet_id?: number;
  environment?: string;
}): Promise<DashboardKPIData> {
  const queryParts: string[] = [];
  if (params?.date_range) queryParts.push(`date_range=${encodeURIComponent(params.date_range)}`);
  if (params?.outlet_id) queryParts.push(`outlet_id=${params.outlet_id}`);
  if (params?.environment) queryParts.push(`environment=${encodeURIComponent(params.environment)}`);

  const qs = queryParts.length > 0 ? `?${queryParts.join('&')}` : '';
  return apiRequest<DashboardKPIData>(`/analytics/dashboard${qs}`);
}

export async function exportAnalyticsSummaryCsv(params?: {
  date_range?: string;
  outlet_id?: number;
  environment?: string;
}): Promise<Blob> {
  const token = localStorage.getItem('amit_access_token');
  const headers: HeadersInit = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const queryParts: string[] = [];
  if (params?.date_range) queryParts.push(`date_range=${encodeURIComponent(params.date_range)}`);
  if (params?.outlet_id) queryParts.push(`outlet_id=${params.outlet_id}`);
  if (params?.environment) queryParts.push(`environment=${encodeURIComponent(params.environment)}`);

  const qs = queryParts.length > 0 ? `?${queryParts.join('&')}` : '';
  const res = await fetch(`${API_BASE_URL}/api/v1/analytics/export${qs}`, { headers });
  if (!res.ok) throw new Error('Failed to export analytics report CSV');
  return res.blob();
}
