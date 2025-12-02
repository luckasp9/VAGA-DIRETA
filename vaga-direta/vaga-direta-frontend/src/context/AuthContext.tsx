import React, { createContext, useContext, useEffect, useState } from "react";
import type { User } from "../types/user";
import {
  getStoredUser,
  storeUser,
  clearStoredUser,
} from "../services/authService";

type AuthContextValue = {
  user: User | null;
  login: (user: User) => void;
  logout: () => void;
  updateUser: (partial: Partial<User>) => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const stored = getStoredUser();
    if (stored) setUser(stored);
  }, []);

  const login = (u: User) => {
    setUser(u);
    storeUser(u);
  };

  const logout = () => {
    setUser(null);
    clearStoredUser();
  };

  const updateUser = (partial: Partial<User>) => {
    setUser((prev) => {
      if (!prev) return prev;
      const updated = { ...prev, ...partial };
      storeUser(updated);
      return updated;
    });
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, updateUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth deve ser usado dentro de AuthProvider");
  }
  return ctx;
};
