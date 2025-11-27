import type { User } from "../types/user";

const LOCAL_STORAGE_KEY = "vaga-direta:user";

export type LoginPayload = {
  email: string;
  password: string;
};

export type RegisterPayload = {
  fullName: string;
  email: string;
  phone?: string;
  course: string;
  semester: number;
  state: string;
  password: string;
};

/**
 * ======
 * Funções usadas pelo AuthContext
 * ======
 */

export function storeUser(user: User): void {
  localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(user));
}

export function getStoredUser(): User | null {
  try {
    const raw = localStorage.getItem(LOCAL_STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as User;
  } catch {
    return null;
  }
}

export function clearStoredUser(): void {
  localStorage.removeItem(LOCAL_STORAGE_KEY);
}

/**
 * ======
 * API “mockada” de autenticação
 * ======
 */

export function getCurrentUser(): User | null {
  return getStoredUser();
}

export function logout(): void {
  clearStoredUser();
}

export async function login(payload: LoginPayload): Promise<User> {
  await new Promise((res) => setTimeout(res, 400));

  const user = getCurrentUser();
  if (!user || user.email !== payload.email) {
    throw new Error("Credenciais inválidas ou usuário não cadastrado.");
  }

  return user;
}

export async function register(payload: RegisterPayload): Promise<User> {
  await new Promise((res) => setTimeout(res, 500));

  const newUser: User = {
    id: Date.now(),
    fullName: payload.fullName,
    email: payload.email,
    phone: payload.phone,
    course: payload.course,
    semester: payload.semester,
    state: payload.state,
    // para testes: se quiser um admin, cadastre com esse e-mail
    isAdmin: payload.email === "admin@admin.com",
  };

  storeUser(newUser);
  return newUser;
}
