import React from "react";
import { Input } from "../ui/Input";
import { Select, type Option } from "../ui/Select";
import { Button } from "../ui/Button";
import { MultiSelect } from "../ui/MultiSelect";
import type { VacancyFilters } from "../../services/vacancyService";

const courseOptions: Option[] = [
  { value: "Ciência da Computação", label: "Ciência da Computação" },
  { value: "Sistemas de Informação", label: "Sistemas de Informação" },
  { value: "Engenharia de Software", label: "Engenharia de Software" },
  { value: "Engenharia da Computação", label: "Engenharia da Computação" },
  {
    value: "Análise e Desenvolvimento de Sistemas",
    label: "Análise e Desenvolvimento de Sistemas",
  },
];

const modalityOptions: Option[] = [
  { value: "Presencial", label: "Presencial" },
  { value: "Remoto", label: "Remoto" },
  { value: "Híbrido", label: "Híbrido" },
];

const platformOptions: Option[] = [
  { value: "LinkedIn", label: "LinkedIn" },
  { value: "Catho", label: "Catho" },
  { value: "Agiel", label: "Agiel" },
  { value: "Super Estágios", label: "Super Estágios" },
  { value: "CIEE", label: "CIEE" },
  { value: "Nube", label: "Nube" },
  { value: "Outro", label: "Outros" },
];

const shiftOptions: Option[] = [
  { value: "Manhã", label: "Manhã" },
  { value: "Tarde", label: "Tarde" },
  { value: "Noite", label: "Noite" },
  { value: "Integral", label: "Integral" },
];

const typeOptions: Option[] = [
  { value: "Vaga afirmativa", label: "Vaga afirmativa" },
  { value: "Sem experiência", label: "Sem experiência" },
  { value: "Estágio obrigatório", label: "Estágio obrigatório" },
];

type Props = {
  filters: VacancyFilters;
  onChange: (filters: VacancyFilters) => void;
  onApply: () => void;
  onClear: () => void;
  loading?: boolean;
};

export const VacancyFiltersBar: React.FC<Props> = ({
  filters,
  onChange,
  onApply,
  onClear,
  loading,
}) => {
  const setField = (field: keyof VacancyFilters, value: any) => {
    onChange({ ...filters, [field]: value });
  };

  const handleCoursesChange = (values: string[]) => {
    onChange({
      ...filters,
      courses: values,
    });
  };

  const handleTypesChange = (values: string[]) => {
    onChange({
      ...filters,
      types: values,
    });
  };

  return (
    <div className="bg-white border border-primary-100 rounded-xl shadow-md p-4 mb-4">
      <div className="flex flex-wrap gap-4 items-end">
        {/* Palavra-chave */}
        <div className="flex-1 min-w-[220px]">
          <Input
            label="Palavra-chave"
            placeholder="Ex.: desenvolvimento, dados..."
            value={filters.keyword ?? ""}
            onChange={(e) => setField("keyword", e.target.value)}
          />
        </div>

        {/* Cursos - MultiSelect */}
        <div className="w-[260px]">
          <MultiSelect
            label="Cursos"
            options={courseOptions}
            selectedValues={filters.courses ?? []}
            onChange={handleCoursesChange}
            placeholder="Todos os cursos"
          />
        </div>

        {/* Modalidade */}
        <div className="w-40">
          <Select
            label="Modalidade"
            value={filters.modality ?? ""}
            onChange={(e) => setField("modality", e.target.value)}
            options={modalityOptions}
            placeholder="Todas"
          />
        </div>

        {/* Plataforma */}
        <div className="w-44">
          <Select
            label="Plataforma"
            value={filters.platform ?? ""}
            onChange={(e) => setField("platform", e.target.value)}
            options={platformOptions}
            placeholder="Todas"
          />
        </div>

        {/* Turno */}
        <div className="w-36">
          <Select
            label="Turno"
            value={filters.shift ?? ""}
            onChange={(e) => setField("shift", e.target.value)}
            options={shiftOptions}
            placeholder="Todos"
          />
        </div>

        {/* Tipo de vaga - MultiSelect */}
        <div className="w-[260px]">
          <MultiSelect
            label="Tipo de vaga"
            options={typeOptions}
            selectedValues={filters.types ?? []}
            onChange={handleTypesChange}
            placeholder="Todos os tipos"
          />
        </div>

        {/* Botões */}
        <div className="flex gap-2 ml-auto">
          <Button
            type="button"
            variant="secondary"
            onClick={onApply}
            disabled={loading}
          >
            {loading ? "Filtrando..." : "Aplicar filtros"}
          </Button>

          <Button type="button" variant="ghost" onClick={onClear}>
            Limpar
          </Button>
        </div>
      </div>
    </div>
  );
};

// Default export para compatibilidade com import default
export default VacancyFiltersBar;
