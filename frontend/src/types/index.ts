export type Environment = 'DEMO' | 'REAL';

export type UserRole = 'SUPER_ADMIN' | 'ADMIN' | 'MANAGER' | 'STAFF';

export interface User {
  id: number;
  email: string;
  fullName: string;
  role: UserRole;
  outletId?: number;
}

export interface Outlet {
  id: number;
  name: string;
  slug: string;
  outletType: string;
  cuisineType: string;
  openingTime: string;
  closingTime: string;
  dressCode: string;
  seatingCapacity: number;
  location: string;
  description: string;
  isPopular?: boolean;
}

export type DietaryFlag = 'VEG' | 'NON_VEG' | 'VEGAN' | 'JAIN' | 'GLUTEN_FREE';

export interface MenuItem {
  id: number;
  outletId: number;
  categoryId: number;
  categoryName: string;
  name: string;
  description: string;
  price: number;
  currency: string;
  dietaryFlags: DietaryFlag[];
  isAvailable: boolean;
  isSignature: boolean;
  environment: Environment;
}

export interface MenuCategory {
  id: number;
  outletId: number;
  name: string;
  displayOrder: number;
}

export interface Citation {
  documentTitle: string;
  category: string;
  snippet?: string;
}

export interface ChatMessage {
  id: string;
  sender: 'USER' | 'ASSISTANT' | 'SYSTEM';
  content: string;
  environment: Environment;
  timestamp: string;
  citations?: Citation[];
  suggestedActions?: string[];
  feedback?: 'UP' | 'DOWN' | null;
}

export type ReservationStatus =
  | 'NEW'
  | 'PENDING'
  | 'UNDER_REVIEW'
  | 'ACCEPTED'
  | 'REJECTED'
  | 'CANCELLED';

export interface ReservationRequest {
  id: number;
  environment: Environment;
  outletId: number;
  outletName: string;
  guestName: string;
  guestPhone: string;
  guestEmail: string;
  guestCount: number;
  reservationDate: string;
  reservationTime: string;
  seatingPreference: 'INDOOR' | 'OUTDOOR' | 'ROOFTOP' | 'PRIVATE';
  specialRequests?: string;
  status: ReservationStatus;
  internalNotes?: string;
  createdAt: string;
}

export type LeadStatus = 'NEW' | 'CONTACTED' | 'QUALIFIED' | 'PROPOSAL_SENT' | 'WON' | 'LOST';

export type LeadType = 'PRIVATE_DINING' | 'CORPORATE_EVENT' | 'WEDDING' | 'BIRTHDAY' | 'CATERING';

export interface Lead {
  id: number;
  environment: Environment;
  outletId: number;
  outletName: string;
  name: string;
  phone: string;
  email: string;
  enquiryType: LeadType;
  guestCount: number;
  targetDate: string;
  budgetRange: string;
  status: LeadStatus;
  notes?: string;
  createdAt: string;
}

export interface KnowledgeDocument {
  id: number;
  environment: Environment;
  outletId?: number;
  outletName?: string;
  title: string;
  fileName: string;
  fileType: 'PDF' | 'DOCX' | 'XLSX' | 'CSV' | 'TXT' | 'MANUAL';
  fileSizeBytes: number;
  category: 'MENU' | 'POLICY' | 'TIMING' | 'EVENT' | 'GENERAL';
  verificationStatus: 'VERIFIED' | 'UNVERIFIED' | 'PENDING';
  verifiedBy?: string;
  verifiedAt?: string;
  chunkCount: number;
  isActive: boolean;
  createdAt: string;
}

export interface AuditLog {
  id: number;
  userName: string;
  userRole: string;
  action: string;
  entityType: string;
  details: string;
  environment: Environment;
  timestamp: string;
}
