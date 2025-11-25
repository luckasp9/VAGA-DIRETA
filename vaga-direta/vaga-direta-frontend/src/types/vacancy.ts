export type Vacancy = {
  id: number;
  code: string;
  title: string;
  courses: string[];
  location: string;
  modality: string; // Presencial, Remoto, Híbrido...
  platform: string; // LinkedIn, Catho, etc.
  company: string;
  stipend: string;
  transportAllowance: boolean;
  type?: string; // Vaga afirmativa, Estágio obrigatório, etc.
  shift: string; // Manhã, Tarde, Noite...
  workload: string; // ex.: "30h semanais"
  benefits?: string;
  activities: string;
  requirements: string;
  applyUrl?: string;
};
