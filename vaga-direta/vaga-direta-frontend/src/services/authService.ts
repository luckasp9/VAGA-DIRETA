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
  password: string;
  // estado REMOVIDO por enquanto
};

/**
 * ======
 * Funções usadas pelo AuthContext
 * ======
 */

// salva usuário logado no localStorage
export function storeUser(user: User): void {
  localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(user));
}

// lê usuário salvo no localStorage (ou null)
export function getStoredUser(): User | null {
  try {
    const raw = localStorage.getItem(LOCAL_STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as User;
  } catch {
    return null;
  }
}

// remove usuário do localStorage
export function clearStoredUser(): void {
  localStorage.removeItem(LOCAL_STORAGE_KEY);
}

/**
 * ======
 * API “mockada” de autenticação
 * ======
 */

// pega usuário salvo (se existir)
export function getCurrentUser(): User | null {
  return getStoredUser();
}

export function logout(): void {
  clearStoredUser();
}

// login mockado: só verifica se email bate com o usuário salvo
export async function login(payload: LoginPayload): Promise<User> {
  await new Promise((res) => setTimeout(res, 400));

  const user = getCurrentUser();
  if (!user || user.email !== payload.email) {
    throw new Error("Credenciais inválidas ou usuário não cadastrado.");
  }

  // (por enquanto não validamos senha)
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
    // estado não é mais obrigatório; se quiser trazer de volta depois, dá pra reaproveitar
  };

  storeUser(newUser);

  return newUser;
}
