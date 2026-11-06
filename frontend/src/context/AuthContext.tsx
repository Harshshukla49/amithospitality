import React, { createContext, useContext, useState } from 'react';
import { User, UserRole } from '../types';

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

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('amit_concierge_user');
    return saved ? JSON.parse(saved) : DEFAULT_ADMIN;
  });

  const login = (email: string, role: UserRole = 'ADMIN') => {
    const newUser: User = {
      id: Date.now(),
      email,
      fullName: email.split('@')[0].replace('.', ' ').toUpperCase(),
      role,
    };
    setUser(newUser);
    localStorage.setItem('amit_concierge_user', JSON.stringify(newUser));
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('amit_concierge_user');
  };

  const switchRole = (role: UserRole) => {
    if (!user) return;
    const updated = { ...user, role };
    setUser(updated);
    localStorage.setItem('amit_concierge_user', JSON.stringify(updated));
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
