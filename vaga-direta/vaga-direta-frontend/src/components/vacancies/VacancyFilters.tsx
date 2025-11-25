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

const stateOptions: Option[] = [
  { value: "", label: "Todos os estados" },
  { value: "AC", label: "Acre (AC)" },
  { value: "AL", label: "Alagoas (AL)" },
  { value: "AP", label: "Amapá (AP)" },
  { value: "AM", label: "Amazonas (AM)" },
  { value: "BA", label: "Bahia (BA)" },
  { value: "CE", label: "Ceará (CE)" },
  { value: "DF", label: "Distrito Federal (DF)" },
  { value: "ES", label: "Espírito Santo (ES)" },
  { value: "GO", label: "Goiás (GO)" },
  { value: "MA", label: "Maranhão (MA)" },
  { value: "MT", label: "Mato Grosso (MT)" },
  { value: "MS", label: "Mato Grosso do Sul (MS)" },
  { value: "MG", label: "Minas Gerais (MG)" },
  { value: "PA", label: "Pará (PA)" },
  { value: "PB", label: "Paraíba (PB)" },
  { value: "PR", label: "Paraná (PR)" },
  { value: "PE", label: "Pernambuco (PE)" },
  { value: "PI", label: "Piauí (PI)" },
  { value: "RJ", label: "Rio de Janeiro (RJ)" },
  { value: "RN", label: "Rio Grande do Norte (RN)" },
  { value: "RS", label: "Rio Grande do Sul (RS)" },
  { value: "RO", label: "Rondônia (RO)" },
  { value: "RR", label: "Roraima (RR)" },
  { value: "SC", label: "Santa Catarina (SC)" },
  { value: "SP", label: "São Paulo (SP)" },
  { value: "SE", label: "Sergipe (SE)" },
  { value: "TO", label: "Tocantins (TO)" },
];

const pcdOptions: Option[] = [
  { value: "", label: "Todas as vagas" },
  { value: "pcd", label: "Vagas para PCD" },
  { value: "nao_pcd", label: "Demais vagas" },
];

type Props = {
  filters: VacancyFilters;
  onChange: (filters: VacancyFilters) => void;
  onApply: () => void;
  onClear: () => void;
  loading?: boolean;

  // NOVO: cidades disponíveis (vêm do HomePage a partir do banco)
  cityOptions: string[];
};

export const VacancyFiltersBar: React.FC<Props> = ({
  filters,
  onChange,
  onApply,
  onClear,
  loading,
  cityOptions,
}) => {
  const setField = (field: keyof VacancyFilters, value: any) => {
    const updated: VacancyFilters = { ...filters, [field]: value };

    // Se o estado mudar, limpamos a cidade para evitar cidade "inválida".
    if (field === "state") {
      updated.city = "";
    }

    onChange(updated);
  };

  const handleCoursesChange = (values: string[]) => {
    onChange({
      ...filters,
      courses: values,
    });
  };

  const citySelectOptions: Option[] = [
    { value: "", label: "Todas as cidades" },
    ...cityOptions.map((c) => ({ value: c, label: c })),
  ];

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

        {/* Estado */}
        <div className="w-48">
          <Select
            label="Estado"
            value={filters.state ?? ""}
            onChange={(e) => setField("state", e.target.value)}
            options={stateOptions}
          />
        </div>

        {/* Cidade (dependente do estado) */}
        <div className="w-56">
          <Select
            label="Cidade"
            value={filters.city ?? ""}
            onChange={(e) => setField("city", e.target.value)}
            options={citySelectOptions}
            // Se quiser travar quando não tiver estado:
            // disabled={!filters.state}
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

        {/* PCD */}
        <div className="w-48">
          <Select
            label="PCD"
            value={filters.pcd ?? ""}
            onChange={(e) => setField("pcd", e.target.value)}
            options={pcdOptions}
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

export default VacancyFiltersBar;
