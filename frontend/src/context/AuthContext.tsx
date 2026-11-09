import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, UserRole } from '../types';
import { API_BASE_URL } from '../api/client';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, role?: UserRole) => void;
  logout: () => void;
  switchRole: (role: UserRole) => void;
  canManageEnvironment: boolean;
  canManageKnowledge: boolean;
  canManageUsers: boolean;
}

const DEFAULT_ADMIN: User = {
  id: 1,
  email: 'admin@amithospitality.com',
  fullName: 'Vikram Sharma',
  role: 'SUPER_ADMIN',
};

const ROLE_CREDENTIALS: Record<string, { email: string; pass: string; fullName: string; outletId?: number }> = {
  SUPER_ADMIN: { email: 'admin@amithospitality.com', pass: 'AmitConcierge2026!Secure', fullName: 'Vikram Sharma' },
  ADMIN: { email: 'admin@amithospitality.com', pass: 'AmitConcierge2026!Secure', fullName: 'Vikram Sharma' },
  MANAGER: { email: 'manager@amithospitality.com', pass: 'Manager2026!', fullName: 'Arjun Kapoor', outletId: 1 },
  STAFF: { email: 'staff@amithospitality.com', pass: 'Staff2026!', fullName: 'Priya Nair', outletId: 1 },
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('amit_concierge_user');
    return saved ? JSON.parse(saved) : DEFAULT_ADMIN;
  });

  const syncBackendToken = async (role: UserRole, email?: string) => {
    const creds = ROLE_CREDENTIALS[role] || ROLE_CREDENTIALS.SUPER_ADMIN;
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: email || creds.email,
          password: creds.pass,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        if (data.access_token) {
          localStorage.setItem('amit_access_token', data.access_token);
        }
      }
    } catch {
      // Quiet failover if backend is initializing or disconnected
    }
  };

  useEffect(() => {
    const token = localStorage.getItem('amit_access_token');
    if (!token && user) {
      syncBackendToken(user.role, user.email);
    }
  }, []);

  const login = (email: string, role: UserRole = 'ADMIN') => {
    const creds = ROLE_CREDENTIALS[role];
    const newUser: User = {
      id: Date.now(),
      email,
      fullName: creds?.fullName || email.split('@')[0].replace('.', ' ').toUpperCase(),
      role,
      outletId: creds?.outletId,
    };
    setUser(newUser);
    localStorage.setItem('amit_concierge_user', JSON.stringify(newUser));
    syncBackendToken(role, email);
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('amit_concierge_user');
    localStorage.removeItem('amit_access_token');
  };

  const switchRole = (role: UserRole) => {
    const creds = ROLE_CREDENTIALS[role] || ROLE_CREDENTIALS.SUPER_ADMIN;
    const updated: User = {
      ...(user || DEFAULT_ADMIN),
      role,
      email: creds.email,
      fullName: creds.fullName,
      outletId: creds.outletId,
    };
    setUser(updated);
    localStorage.setItem('amit_concierge_user', JSON.stringify(updated));
    syncBackendToken(role, creds.email);
  };

  const canManageEnvironment = user?.role === 'SUPER_ADMIN' || user?.role === 'ADMIN';
  const canManageKnowledge = user?.role === 'SUPER_ADMIN' || user?.role === 'ADMIN';
  const canManageUsers = user?.role === 'SUPER_ADMIN';

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        login,
        logout,
        switchRole,
        canManageEnvironment,
        canManageKnowledge,
        canManageUsers,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
