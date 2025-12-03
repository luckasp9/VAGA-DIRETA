// src/context/AuthContext.tsx
import React, {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";
import type { User } from "../types/user";
import {
  getStoredUser,
  storeUser,
  clearStoredUser,
  updateUserProfile,
} from "../services/authService";

type UpdateUserPatch = {
  fullName?: string;
  phone?: string;
  course?: string;
  semester?: number;
  state?: string;
};

type AuthContextValue = {
  user: User | null;
  login: (user: User) => void;
  logout: () => void;
  updateUser: (patch: UpdateUserPatch) => Promise<void>;
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

  const updateUser = async (patch: UpdateUserPatch) => {
    if (!user) return;

    const updated = await updateUserProfile(user.id, patch);
    setUser(updated);
    // storeUser já é chamado dentro de updateUserProfile,
    // mas não custa garantir:
    storeUser(updated);
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
