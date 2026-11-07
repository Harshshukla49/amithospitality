import { apiRequest } from './client';
import { Environment } from '../types';

export interface BackendKnowledgeDoc {
  id: number;
  environment: Environment;
  outlet_id?: number;
  title: string;
  file_name: string;
  file_type: 'PDF' | 'DOCX' | 'XLSX' | 'CSV' | 'TXT' | 'MANUAL';
  file_size_bytes: number;
  category: 'MENU' | 'POLICY' | 'TIMING' | 'EVENT' | 'GENERAL';
  verification_status: 'VERIFIED' | 'UNVERIFIED' | 'PENDING';
  verified_by?: string;
  verified_at?: string;
  chunk_count: number;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface BackendChunkDetail {
  id: number;
  chunk_index: number;
  content: string;
  is_active: boolean;
  created_at: string;
}

export interface BackendKnowledgeDocDetail extends BackendKnowledgeDoc {
  chunks: BackendChunkDetail[];
}

export interface BackendSearchHit {
  chunk_id: number;
  document_id: number;
  document_title: string;
  category: string;
  environment: Environment;
  outlet_id?: number;
  chunk_index: number;
  content: string;
  score: number;
  cosine_similarity: number;
  lexical_overlap: number;
}

export interface BackendSearchResponse {
  query: string;
  environment: Environment;
  total_hits: number;
  results: BackendSearchHit[];
}

export interface CategoryStat {
  category: string;
  count: number;
}

export interface BackendKnowledgeStats {
  active_environment: Environment;
  demo_doc_count: number;
  real_doc_count: number;
  demo_chunk_count: number;
  real_chunk_count: number;
  total_active_docs: number;
  total_inactive_docs: number;
  verified_docs_count: number;
  unverified_docs_count: number;
  categories: CategoryStat[];
}

export async function fetchDocuments(params?: {
  environment?: string;
  category?: string;
  outlet_id?: number;
  status?: string;
}): Promise<BackendKnowledgeDoc[]> {
  const queryParts: string[] = [];
  if (params?.environment) queryParts.push(`environment=${encodeURIComponent(params.environment)}`);
  if (params?.category && params.category !== 'ALL') queryParts.push(`category=${encodeURIComponent(params.category)}`);
  if (params?.outlet_id) queryParts.push(`outlet_id=${params.outlet_id}`);
  if (params?.status) queryParts.push(`status=${encodeURIComponent(params.status)}`);

  const qs = queryParts.length > 0 ? `?${queryParts.join('&')}` : '';
  return apiRequest<BackendKnowledgeDoc[]>(`/knowledge/documents${qs}`);
}

export async function fetchDocumentDetail(docId: number): Promise<BackendKnowledgeDocDetail> {
  return apiRequest<BackendKnowledgeDocDetail>(`/knowledge/documents/${docId}`);
}

export async function uploadDocument(formData: FormData): Promise<BackendKnowledgeDoc> {
  return apiRequest<BackendKnowledgeDoc>('/knowledge/upload', {
    method: 'POST',
    body: formData,
  });
}

export async function createManualKnowledge(data: {
  title: string;
  content: string;
  category: string;
  outlet_id?: number;
  environment: string;
}): Promise<BackendKnowledgeDoc> {
  return apiRequest<BackendKnowledgeDoc>('/knowledge/manual', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateDocument(
  docId: number,
  data: { title?: string; category?: string; outlet_id?: number }
): Promise<BackendKnowledgeDoc> {
  return apiRequest<BackendKnowledgeDoc>(`/knowledge/documents/${docId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function toggleDocumentStatus(docId: number, isActive: boolean): Promise<BackendKnowledgeDoc> {
  return apiRequest<BackendKnowledgeDoc>(`/knowledge/documents/${docId}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ is_active: isActive }),
  });
}

export async function reprocessDocument(docId: number): Promise<BackendKnowledgeDoc> {
  return apiRequest<BackendKnowledgeDoc>(`/knowledge/documents/${docId}/reprocess`, {
    method: 'POST',
  });
}

export async function deleteDocumentApi(docId: number): Promise<{ success: boolean; message: string }> {
  return apiRequest<{ success: boolean; message: string }>(`/knowledge/documents/${docId}`, {
    method: 'DELETE',
  });
}

export async function searchKnowledge(params: {
  q: string;
  environment?: string;
  outlet_id?: number;
  category?: string;
  top_k?: number;
}): Promise<BackendSearchResponse> {
  const queryParts = [`q=${encodeURIComponent(params.q)}`];
  if (params.environment) queryParts.push(`environment=${encodeURIComponent(params.environment)}`);
  if (params.outlet_id) queryParts.push(`outlet_id=${params.outlet_id}`);
  if (params.category && params.category !== 'ALL') queryParts.push(`category=${encodeURIComponent(params.category)}`);
  if (params.top_k) queryParts.push(`top_k=${params.top_k}`);

  return apiRequest<BackendSearchResponse>(`/knowledge/search?${queryParts.join('&')}`);
}

export async function fetchKnowledgeStats(): Promise<BackendKnowledgeStats> {
  return apiRequest<BackendKnowledgeStats>('/knowledge/stats');
}

export async function fetchActiveEnvironment(): Promise<{
  success: boolean;
  environment: Environment;
  is_demo: boolean;
  disclaimer: string;
}> {
  return apiRequest<{
    success: boolean;
    environment: Environment;
    is_demo: boolean;
    disclaimer: string;
  }>('/environment/active');
}

export async function switchEnvironmentApi(target: string, reason: string): Promise<{
  success: boolean;
  active_environment: Environment;
  switched_by: string;
  timestamp: string;
}> {
  return apiRequest('/environment/switch', {
    method: 'POST',
    body: JSON.stringify({
      target_environment: target,
      reason,
      confirm_acknowledgment: true,
    }),
  });
}
