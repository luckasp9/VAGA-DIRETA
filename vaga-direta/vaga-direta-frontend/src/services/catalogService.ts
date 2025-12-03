// src/services/catalogService.ts
import type { Option } from "../components/ui/Select";

const API_BASE = "http://localhost:8000/api";

export async function fetchCourseOptions(): Promise<Option[]> {
  const res = await fetch(`${API_BASE}/cursos`);
  if (!res.ok) {
    throw new Error("Erro ao buscar cursos.");
  }

  const data = (await res.json()) as string[];
  return data.map((curso) => ({
    value: curso,
    label: curso,
  }));
}

export async function fetchPlatformOptions(): Promise<Option[]> {
  const res = await fetch(`${API_BASE}/plataformas`);
  if (!res.ok) {
    throw new Error("Erro ao buscar plataformas.");
  }

  const data = (await res.json()) as string[];
  return data.map((nome) => ({
    value: nome,
    label: nome,
  }));
}
