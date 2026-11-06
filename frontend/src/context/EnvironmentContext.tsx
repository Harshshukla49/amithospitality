import React, { createContext, useContext, useState, useEffect } from 'react';
import { Environment, AuditLog } from '../types';
import { INITIAL_AUDIT_LOGS } from '../utils/mockData';

interface EnvironmentContextType {
  environment: Environment;
  isDemo: boolean;
  auditLogs: AuditLog[];
  switchEnvironment: (target: Environment, reason: string, adminName: string) => void;
  pendingSwitch: { target: Environment; isOpen: boolean } | null;
  openSwitchModal: (target: Environment) => void;
  closeSwitchModal: () => void;
}

const EnvironmentContext = createContext<EnvironmentContextType | undefined>(undefined);

export const EnvironmentProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [environment, setEnvironment] = useState<Environment>(() => {
    const saved = localStorage.getItem('amit_concierge_env');
    return (saved as Environment) || 'DEMO';
  });

  const [auditLogs, setAuditLogs] = useState<AuditLog[]>(INITIAL_AUDIT_LOGS);
  const [pendingSwitch, setPendingSwitch] = useState<{ target: Environment; isOpen: boolean } | null>(null);

  useEffect(() => {
    localStorage.setItem('amit_concierge_env', environment);
  }, [environment]);

  const openSwitchModal = (target: Environment) => {
    setPendingSwitch({ target, isOpen: true });
  };

  const closeSwitchModal = () => {
    setPendingSwitch(null);
  };

  const switchEnvironment = (target: Environment, reason: string, adminName: string) => {
    const newLog: AuditLog = {
      id: Date.now(),
      userName: adminName,
      userRole: 'ADMIN',
      action: 'ENVIRONMENT_SWITCH',
      entityType: 'ENVIRONMENT_SETTINGS',
      details: `Switched mode from ${environment} to ${target}. Reason: ${reason}`,
      environment: target,
      timestamp: new Date().toISOString().replace('T', ' ').substring(0, 19),
    };

    setEnvironment(target);
    setAuditLogs((prev) => [newLog, ...prev]);
    closeSwitchModal();
  };

  return (
    <EnvironmentContext.Provider
      value={{
        environment,
        isDemo: environment === 'DEMO',
        auditLogs,
        switchEnvironment,
        pendingSwitch,
        openSwitchModal,
        closeSwitchModal,
      }}
    >
      {children}
    </EnvironmentContext.Provider>
  );
};

export const useEnvironment = () => {
  const context = useContext(EnvironmentContext);
  if (!context) {
    throw new Error('useEnvironment must be used within an EnvironmentProvider');
  }
  return context;
};
