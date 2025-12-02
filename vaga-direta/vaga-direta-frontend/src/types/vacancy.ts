// src/types/vacancy.ts
export type Vacancy = {
  id: number;
  code: string;
  title: string;
  courses: string[];
  location: string;
  modality: string;
  platform: string;
  company: string;
  stipend: string;
  transportAllowance: boolean;
  type?: string;
  shift: string;
  workload: string;
  benefits?: string;
  activities: string;
  requirements: string;
  applyUrl?: string;
  pcd?: boolean;
  city?: string;
  state?: string;
};
