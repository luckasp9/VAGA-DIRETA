import type { Vacancy } from "../types/vacancy";

export type VacancyFilters = {
  keyword?: string;
  courses?: string[];
  modality?: string;
  platform?: string;
  shift?: string;
  types?: string[];
};

const API_URL = "http://localhost:3001/vacancies";

// Tenta buscar da API fake (json-server). Se falhar, usa os mocks.
async function fetchVacanciesFromApi(): Promise<Vacancy[] | null> {
  try {
    const res = await fetch(API_URL);
    if (!res.ok) throw new Error("Erro ao buscar vagas na API fake");
    const data = (await res.json()) as Vacancy[];
    return data;
  } catch (err) {
    console.error("[vacancyService] Falha ao buscar API fake:", err);
    return null;
  }
}

// Mocks usados como fallback
const mockVacancies: Vacancy[] = [
  {
    id: 1,
    code: "VD-001",
    title: "Estágio em Desenvolvimento Web",
    courses: ["Ciência da Computação", "Sistemas de Informação"],
    location: "Brasília - DF",
    modality: "Híbrido",
    platform: "LinkedIn",
    company: "Empresa Tech BR",
    stipend: "R$ 1.500,00",
    transportAllowance: true,
    type: "Estágio obrigatório",
    shift: "Tarde",
    workload: "30h semanais",
    benefits: "Vale-refeição, Day-off no aniversário",
    activities:
      "Desenvolvimento de novas funcionalidades, correção de bugs e participação em reuniões de planejamento.",
    requirements:
      "Conhecimentos básicos em HTML, CSS, JavaScript e Git. Desejável noções de React.",
    applyUrl: "https://www.linkedin.com/",
  },
  {
    id: 2,
    code: "VD-002",
    title: "Estágio em Dados",
    courses: ["Ciência da Computação", "Engenharia de Software"],
    location: "São Paulo - SP",
    modality: "Remoto",
    platform: "Catho",
    company: "Data Insights LTDA",
    stipend: "R$ 1.800,00",
    transportAllowance: false,
    type: "Sem experiência",
    shift: "Manhã",
    workload: "20h semanais",
    benefits: "Auxílio home office, acesso a cursos internos",
    activities:
      "Criação de relatórios, análises exploratórias de dados e manutenção de dashboards.",
    requirements:
      "Conhecimentos em SQL e Excel. Desejável noções de Python ou R.",
    applyUrl: "#",
  },
  {
    id: 3,
    code: "VD-003",
    title: "Estágio em UX/UI",
    courses: ["Sistemas de Informação", "Engenharia de Software"],
    location: "São Paulo - SP",
    modality: "Presencial",
    platform: "Agiel",
    company: "Agência Criativa SP",
    stipend: "R$ 1.300,00",
    transportAllowance: true,
    type: "Vaga afirmativa",
    shift: "Manhã",
    workload: "30h semanais",
    benefits: "Vale-transporte, vale-alimentação",
    activities:
      "Criação de protótipos, testes de usabilidade e documentação de fluxos.",
    requirements:
      "Conhecimentos em Figma ou similar. Desejável noções de HTML/CSS.",
    applyUrl: "#",
  },
  {
    id: 4,
    code: "VD-004",
    title: "Estágio em Suporte Técnico",
    courses: ["Ciência da Computação"],
    location: "Remoto",
    modality: "Remoto",
    platform: "Super Estágios",
    company: "Suporte Já LTDA",
    stipend: "R$ 1.200,00",
    transportAllowance: false,
    type: "Sem experiência",
    shift: "Noite",
    workload: "30h semanais",
    benefits: "Equipamentos fornecidos pela empresa",
    activities:
      "Atendimento a usuários, registro de chamados e manutenção de estações de trabalho.",
    requirements:
      "Boa comunicação e interesse em suporte de TI. Desejável noções de redes.",
    applyUrl: "#",
  },
  {
    id: 5,
    code: "VD-005",
    title: "Estágio em QA/Tester",
    courses: ["Ciência da Computação", "Engenharia de Software"],
    location: "Belo Horizonte - MG",
    modality: "Híbrido",
    platform: "LinkedIn",
    company: "Qualidade Tech",
    stipend: "R$ 1.600,00",
    transportAllowance: true,
    type: "Estágio obrigatório",
    shift: "Tarde",
    workload: "30h semanais",
    benefits: "Plano de saúde, vale-alimentação",
    activities:
      "Criação e execução de casos de teste, registro de defeitos e apoio na automação de testes.",
    requirements:
      "Noções de testes de software. Desejável conhecimento em ferramentas de automação.",
    applyUrl: "#",
  },
  {
    id: 6,
    code: "VD-006",
    title: "Estágio em Ciência de Dados",
    courses: ["Ciência da Computação"],
    location: "Curitiba - PR",
    modality: "Presencial",
    platform: "CIEE",
    company: "Analytics Corp",
    stipend: "R$ 2.000,00",
    transportAllowance: false,
    type: "Vaga afirmativa",
    shift: "Integral",
    workload: "30h semanais",
    benefits: "Estacionamento, cursos internos",
    activities:
      "Preparação de dados, criação de modelos simples e apoio em projetos de machine learning.",
    requirements:
      "Conhecimentos em Python, bibliotecas de dados (Pandas, NumPy) e SQL.",
    applyUrl: "#",
  },
];

export async function getVacancies(
  filters: VacancyFilters
): Promise<Vacancy[]> {
  const source = (await fetchVacanciesFromApi()) ?? mockVacancies;

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

    // Plataforma
    if (filters.platform && vacancy.platform !== filters.platform) {
      return false;
    }

    // Turno
    if (filters.shift && vacancy.shift !== filters.shift) {
      return false;
    }

    // Tipo (multi)
    if (filters.types && filters.types.length > 0) {
      if (!vacancy.type || !filters.types.includes(vacancy.type)) {
        return false;
      }
    }

    return true;
  });
}

export async function getVacancyById(id: number): Promise<Vacancy | null> {
  const source = (await fetchVacanciesFromApi()) ?? mockVacancies;
  const vacancy = source.find((v) => v.id === id);
  return vacancy ?? null;
}
