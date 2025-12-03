// src/services/authService.ts
import type { User } from "../types/user";

const LOCAL_STORAGE_KEY = "vaga-direta:user";
const API_BASE = "http://localhost:8000/api";

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

// formato que o backend (UsuarioPublic) devolve
type ApiUser = {
  id: number;
  nome: string;
  email: string;
  tipo_usuario: string;
  telefone?: string | null;
  curso?: string | null;
  semestre?: number | null;
  estado?: string | null;
};

function mapApiUserToUser(api: ApiUser): User {
  const isAdmin = api.tipo_usuario === "admin";

  return {
    id: api.id,
    fullName: api.nome,
    email: api.email,
    course: api.curso ?? "",
    semester: api.semestre ?? 0,
    phone: api.telefone ?? undefined,
    state: api.estado ?? undefined,
    userType: api.tipo_usuario,
    isAdmin,
  };
}
/* ========== LocalStorage helpers ========== */

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

/* ========== Auth com backend ========== */

export async function login(payload: LoginPayload): Promise<User> {
  const res = await fetch(`${API_BASE}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: payload.email,
      senha: payload.password,
    }),
  });

  if (!res.ok) {
    throw new Error("Credenciais inválidas.");
  }

  const data = (await res.json()) as ApiUser;
  const user = mapApiUserToUser(data);
  storeUser(user);
  return user;
}

export async function register(payload: RegisterPayload): Promise<User> {
  const res = await fetch(`${API_BASE}/usuarios`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      nome: payload.fullName,
      email: payload.email,
      telefone: payload.phone ?? null,
      curso: payload.course,
      semestre: payload.semester,
      estado: payload.state,
      senha: payload.password,
      tipo_usuario: "aluno",
    }),
  });

  if (!res.ok) {
    throw new Error("Erro ao cadastrar usuário");
  }

  const data = (await res.json()) as ApiUser;
  const user = mapApiUserToUser(data);

  // se preferir só logar depois do login, pode tirar esse storeUser
  storeUser(user);
  return user;
}

/* ========== Update de perfil ========== */

export type UpdateUserPayload = {
  fullName?: string;
  phone?: string;
  course?: string;
  semester?: number;
  state?: string;
};

export async function updateUserProfile(
  id: number,
  patch: UpdateUserPayload
): Promise<User> {
  const body: any = {};

  if (patch.fullName !== undefined) body.nome = patch.fullName;
  if (patch.phone !== undefined) body.telefone = patch.phone;
  if (patch.course !== undefined) body.curso = patch.course;
  if (patch.semester !== undefined) body.semestre = patch.semester;
  if (patch.state !== undefined) body.estado = patch.state;

  const res = await fetch(`${API_BASE}/usuarios/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    throw new Error("Erro ao atualizar usuário");
  }

  const data = (await res.json()) as ApiUser;
  const user = mapApiUserToUser(data);
  storeUser(user);
  return user;
}
