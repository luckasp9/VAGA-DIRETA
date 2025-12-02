import type { User } from "../types/user";

const LOCAL_STORAGE_KEY = "vaga-direta:user";
const API_BASE = "http://localhost:8000/api"; // ajuste se o backend estiver em outra porta

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

export type UpdateProfilePayload = {
  fullName?: string;
  phone?: string;
  course?: string;
  semester?: number;
  state?: string;
};

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
  return {
    id: api.id,
    fullName: api.nome,
    email: api.email,
    course: api.curso ?? undefined,
    semester: api.semestre ?? undefined,
    phone: api.telefone ?? undefined,
    state: api.estado ?? undefined,
    userType: api.tipo_usuario,
    isAdmin: api.tipo_usuario === "admin",
  };
}

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

// pega usuário salvo (se existir)
export function getCurrentUser(): User | null {
  return getStoredUser();
}

export function logout(): void {
  clearStoredUser();
}

/**
 * ======
 * APIs reais de autenticação (backend FastAPI)
 * ======
 */

export async function login(payload: LoginPayload): Promise<User> {
  const res = await fetch(`${API_BASE}/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email: payload.email,
      senha: payload.password, // backend espera 'senha'
    }),
  });

  if (!res.ok) {
    let msg = "Não foi possível realizar o login.";
    try {
      const data = await res.json();
      if (data?.detail) msg = data.detail;
    } catch {
      // ignore
    }
    throw new Error(msg);
  }

  const apiUser = (await res.json()) as ApiUser;
  const user = mapApiUserToUser(apiUser);
  storeUser(user);
  return user;
}

export async function register(payload: RegisterPayload): Promise<User> {
  const res = await fetch(`${API_BASE}/usuarios`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      nome: payload.fullName,
      email: payload.email,
      telefone: payload.phone ?? null,
      curso: payload.course,
      semestre: payload.semester,
      estado: payload.state,
      senha: payload.password,
      tipo_usuario: "aluno", // padrão
    }),
  });

  if (!res.ok) {
    let msg = "Não foi possível finalizar o cadastro.";
    try {
      const data = await res.json();
      if (data?.detail) msg = data.detail;
    } catch {
      // ignore
    }
    throw new Error(msg);
  }

  
  const apiUser = (await res.json()) as ApiUser;
  const user = mapApiUserToUser(apiUser);

  // mantém o comportamento antigo: salvar no localStorage,
  // embora o usuário só vá logar de fato depois.
  storeUser(user);

  return user;
}

  export async function updateProfile(
    userId: number,
    payload: UpdateProfilePayload
  ): Promise<User> {
    const body: any = {};

    if (payload.fullName !== undefined) body.nome = payload.fullName;
    if (payload.phone !== undefined) body.telefone = payload.phone;
    if (payload.course !== undefined) body.curso = payload.course;
    if (payload.semester !== undefined) body.semestre = payload.semester;
    if (payload.state !== undefined) body.estado = payload.state;

    const res = await fetch(`${API_BASE}/usuarios/${userId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      let msg = "Não foi possível atualizar o perfil.";
      try {
        const data = await res.json();
        if (data?.detail) msg = data.detail;
      } catch {
        // ignore
      }
      throw new Error(msg);
    }

    const apiUser = (await res.json()) as ApiUser;
    const user = mapApiUserToUser(apiUser);
    storeUser(user); // mantém user atualizado no localStorage
    return user;
  }
