import { apiRequest } from './client';
import { Outlet, MenuItem, DietaryFlag, Environment } from '../types';

export interface BackendOutlet {
  id: number;
  name: string;
  slug: string;
  outlet_type: string;
  cuisine_type: string;
  opening_time: string;
  closing_time: string;
  dress_code: string;
  seating_capacity: number;
  location?: string;
  description?: string;
  is_popular: boolean;
  is_active: boolean;
}

export interface BackendMenuItem {
  id: number;
  outlet_id: number;
  category_id?: number;
  category_name?: string;
  name: string;
  description?: string;
  price: number;
  currency: string;
  dietary_flags: string;
  is_available: boolean;
  is_signature: boolean;
  environment: Environment;
  created_at: string;
}

export function transformBackendOutlet(o: BackendOutlet): Outlet {
  return {
    id: o.id,
    name: o.name,
    slug: o.slug,
    outletType: o.outlet_type,
    cuisineType: o.cuisine_type,
    openingTime: o.opening_time,
    closingTime: o.closing_time,
    dressCode: o.dress_code,
    seatingCapacity: o.seating_capacity,
    location: o.location || 'Amit Hospitality Complex, New Delhi',
    description: o.description || '',
    isPopular: o.is_popular,
  };
}

export function transformBackendMenuItem(m: BackendMenuItem): MenuItem {
  const flags = m.dietary_flags
    ? (m.dietary_flags.split(',').map((f) => f.trim().toUpperCase()) as DietaryFlag[])
    : (['VEG'] as DietaryFlag[]);

  return {
    id: m.id,
    outletId: m.outlet_id,
    categoryId: m.category_id || 1,
    categoryName: m.category_name || 'Signature Specialties',
    name: m.name,
    description: m.description || '',
    price: m.price,
    currency: m.currency || 'INR',
    dietaryFlags: flags,
    isAvailable: m.is_available,
    isSignature: m.is_signature,
    environment: m.environment,
  };
}

export async function fetchOutletsApi(): Promise<Outlet[]> {
  const raw = await apiRequest<BackendOutlet[]>('/outlets');
  return raw.map(transformBackendOutlet);
}

export async function fetchOutletDetailApi(outletId: number): Promise<Outlet> {
  const raw = await apiRequest<BackendOutlet>(`/outlets/${outletId}`);
  return transformBackendOutlet(raw);
}

export async function updateOutletApi(
  outletId: number,
  updates: Partial<{
    name: string;
    outlet_type: string;
    cuisine_type: string;
    opening_time: string;
    closing_time: string;
    dress_code: string;
    seating_capacity: number;
    location: string;
    description: string;
  }>
): Promise<Outlet> {
  const raw = await apiRequest<BackendOutlet>(`/outlets/${outletId}`, {
    method: 'PUT',
    body: JSON.stringify(updates),
  });
  return transformBackendOutlet(raw);
}

export async function fetchMenuItemsApi(params?: {
  outlet_id?: number;
  environment?: string;
}): Promise<MenuItem[]> {
  const parts: string[] = [];
  if (params?.outlet_id) parts.push(`outlet_id=${params.outlet_id}`);
  if (params?.environment) parts.push(`environment=${encodeURIComponent(params.environment)}`);
  const qs = parts.length > 0 ? `?${parts.join('&')}` : '';

  const raw = await apiRequest<BackendMenuItem[]>(`/menus${qs}`);
  return raw.map(transformBackendMenuItem);
}

export async function createMenuItemApi(data: {
  outlet_id: number;
  name: string;
  description: string;
  price: number;
  dietary_flags: string;
  category_id?: number;
  environment?: string;
  is_signature?: boolean;
}): Promise<MenuItem> {
  const raw = await apiRequest<BackendMenuItem>('/menus/items', {
    method: 'POST',
    body: JSON.stringify(data),
  });
  return transformBackendMenuItem(raw);
}

export async function updateMenuItemApi(
  itemId: number,
  updates: {
    price?: number;
    is_available?: boolean;
    description?: string;
    name?: string;
  }
): Promise<MenuItem> {
  const raw = await apiRequest<BackendMenuItem>(`/menus/items/${itemId}`, {
    method: 'PUT',
    body: JSON.stringify(updates),
  });
  return transformBackendMenuItem(raw);
}

export async function deleteMenuItemApi(itemId: number): Promise<{ success: boolean }> {
  return await apiRequest<{ success: boolean }>(`/menus/items/${itemId}`, {
    method: 'DELETE',
  });
}
