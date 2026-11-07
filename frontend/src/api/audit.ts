import { apiRequest } from './client';
import { AuditLog } from '../types';

export async function fetchAuditLogsApi(limit: number = 50, environment?: string): Promise<AuditLog[]> {
  const envParam = environment ? `&environment=${environment}` : '';
  const res = await apiRequest<any[]>(`/audit/logs?limit=${limit}${envParam}`);
  return res.map((l) => ({
    id: l.id,
    userName: l.userName || 'Administrator',
    userRole: l.userRole || 'ADMIN',
    action: l.action,
    entityType: l.entityType || 'SYSTEM',
    environment: l.environment,
    details: l.details,
    timestamp: l.timestamp ? l.timestamp.replace('T', ' ').substring(0, 19) : new Date().toISOString(),
  }));
}

export async function exportAuditLogsCsv(environment?: string): Promise<Blob> {
  const token = localStorage.getItem('amit_access_token');
  const envParam = environment ? `?environment=${environment}` : '';
  const headers: HeadersInit = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`/api/v1/audit/export${envParam}`, { headers });
  if (!res.ok) throw new Error('Failed to export audit logs CSV');
  return res.blob();
}
