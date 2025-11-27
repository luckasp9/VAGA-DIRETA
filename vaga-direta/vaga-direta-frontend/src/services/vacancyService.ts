import type { Vacancy } from "../types/vacancy";
import { getVagas, getVaga } from "./apiVagas";

export type VacancyFilters = {
  keyword?: string;
  courses?: string[];
  modality?: string;
  /** "" | "pcd" | "nao_pcd" */
  pcd?: string;
  state?: string;
  cities?: string[];
};

type ApiVaga = {
  id: number;
  id_vaga?: string | null;
  titulo_vaga: string;
  empresa_nome: string;
  descricao_vaga?: string | null;
  cidade_vaga?: string | null;
  estado_vaga?: string | null;
  salario?: string | null;
  url?: string | null;
  cursos?: string[];
  pcd?: boolean;
  modalidade?: string | null;
  beneficios?: string[];
};

const API_BASE = "http://localhost:8000/api/vagas";

export type VacancyInput = {
  titulo_vaga: string;
  empresa_nome: string;
  descricao_vaga: string;
  cidade_vaga: string;
  estado_vaga: string;
  salario: string;
  url: string;
  cursos: string[];
  pcd: boolean;
  modalidade: string;
  beneficios: string[]; // um benefício por linha no formulário
};

function mapApiVagaToVacancy(api: ApiVaga): Vacancy {
  const courses = api.cursos ?? [];
  const city = api.cidade_vaga ?? "";
  const state = api.estado_vaga ?? "";
  const location =
    city && state ? `${city} - ${state}` : city || state || "";

  return {
    id: api.id,
    code: api.id_vaga ?? `VD-${api.id}`,
    title: api.titulo_vaga,
    company: api.empresa_nome,
    courses,

    location,
    modality: api.modalidade ?? "",
    platform: "Plataforma original",

    stipend: api.salario ?? "A combinar",
    transportAllowance: false,
    type: api.pcd ? "PCD" : undefined,

    shift: "",
    workload: "",

    benefits: api.beneficios?.join(", "),
    activities: api.descricao_vaga ?? "",
    requirements: "",

    applyUrl: api.url ?? undefined,

    pcd: !!api.pcd,
    city,
    state,
  };
}

export async function getVacancies(
  filters: VacancyFilters
): Promise<Vacancy[]> {
  const apiData = (await getVagas()) as ApiVaga[];
  const source = apiData.map(mapApiVagaToVacancy);

  return source.filter((vacancy) => {
    if (filters.keyword) {
      const kw = filters.keyword.toLowerCase();
      const inTitle = vacancy.title.toLowerCase().includes(kw);
      const inActivities = vacancy.activities.toLowerCase().includes(kw);
      if (!inTitle && !inActivities) return false;
    }

    if (filters.courses && filters.courses.length > 0) {
      const hasCourse = filters.courses.some((course) =>
        vacancy.courses.includes(course)
      );
      if (!hasCourse) return false;
    }

    if (filters.modality && vacancy.modality !== filters.modality) {
      return false;
    }

    if (filters.pcd === "pcd" && !vacancy.pcd) {
      return false;
    }
    if (filters.pcd === "nao_pcd" && vacancy.pcd) {
      return false;
    }

    if (filters.state && vacancy.state && vacancy.state !== filters.state) {
      return false;
    }

    if (filters.cities && filters.cities.length > 0) {
      const city = vacancy.city ?? "";
      if (!city || !filters.cities.includes(city)) {
        return false;
      }
    }

    return true;
  });
}

export async function getVacancyById(id: number): Promise<Vacancy | null> {
  const apiData = (await getVaga(id)) as ApiVaga;
  if (!apiData) return null;
  return mapApiVagaToVacancy(apiData);
}

// ====== CRUD para área administrativa ======

async function sendVacancy(
  method: "POST" | "PUT",
  idOrBody: number | VacancyInput,
  maybeBody?: VacancyInput
): Promise<Vacancy> {
  const id = typeof idOrBody === "number" ? idOrBody : undefined;
  const body = typeof idOrBody === "number" ? maybeBody! : idOrBody;

  const url = id ? `${API_BASE}/${id}` : API_BASE;

  const res = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    throw new Error(`Erro ao salvar vaga (${method})`);
  }

  const data = (await res.json()) as ApiVaga;
  return mapApiVagaToVacancy(data);
}

export async function createVacancy(input: VacancyInput): Promise<Vacancy> {
  return sendVacancy("POST", input);
}

export async function updateVacancy(
  id: number,
  input: VacancyInput
): Promise<Vacancy> {
  return sendVacancy("PUT", id, input);
}

export async function deleteVacancy(id: number): Promise<void> {
  const res = await fetch(`${API_BASE}/${id}`, { method: "DELETE" });
  if (!res.ok) {
    throw new Error("Erro ao excluir vaga");
  }
}
