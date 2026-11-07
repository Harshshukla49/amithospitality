import { apiRequest } from './client';

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
  frequent_queries: FrequentQuery[];
  unanswered_questions: UnansweredQuestion[];
}

export async function fetchDashboardKPIs(): Promise<DashboardKPIData> {
  return apiRequest<DashboardKPIData>('/analytics/dashboard');
}

export async function exportAnalyticsSummaryCsv(): Promise<Blob> {
  const token = localStorage.getItem('amit_access_token');
  const headers: HeadersInit = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch('/api/v1/analytics/export', { headers });
  if (!res.ok) throw new Error('Failed to export analytics report CSV');
  return res.blob();
}
