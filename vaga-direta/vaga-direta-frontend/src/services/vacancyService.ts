import type { Vacancy } from "../types/vacancy";
import { getVagas, getVaga } from "./apiVagas";

export type VacancyFilters = {
  keyword?: string;
  courses?: string[];
  modality?: string;
  /** "" | "pcd" | "nao_pcd" */
  pcd?: string;
  state?: string;
  city?: string; // <--- NOVO
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
    // Palavra-chave
    if (filters.keyword) {
      const kw = filters.keyword.toLowerCase();
      const inTitle = vacancy.title.toLowerCase().includes(kw);
      const inActivities = vacancy.activities.toLowerCase().includes(kw);
      if (!inTitle && !inActivities) return false;
    }

    // Cursos (multi)
    if (filters.courses && filters.courses.length > 0) {
      const hasCourse = filters.courses.some((course) =>
        vacancy.courses.includes(course)
      );
      if (!hasCourse) return false;
    }

    // Modalidade
    if (filters.modality && vacancy.modality !== filters.modality) {
      return false;
    }

    // PCD
    if (filters.pcd === "pcd" && !vacancy.pcd) {
      return false;
    }
    if (filters.pcd === "nao_pcd" && vacancy.pcd) {
      return false;
    }

    // Estado (UF)
    if (filters.state && vacancy.state && vacancy.state !== filters.state) {
      return false;
    }

    // Cidade (dependente do estado)
    if (filters.city) {
      if (!vacancy.city || vacancy.city !== filters.city) {
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
