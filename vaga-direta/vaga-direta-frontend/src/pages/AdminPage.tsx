// src/pages/AdminPage.tsx
import React, { useEffect, useState } from "react";
import {
  createVacancy,
  deleteVacancy,
  getVacancies,
  updateVacancy,
  type VacancyFilters,
  type VacancyInput,
} from "../services/vacancyService";
import type { Vacancy } from "../types/vacancy";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { Select, type Option } from "../components/ui/Select";
import { MultiSelect } from "../components/ui/MultiSelect";
import { Badge } from "../components/ui/Badge";
import { useAuth } from "../context/AuthContext";
import { fetchCourseOptions } from "../services/catalogService";

const modalityOptions: Option[] = [
  { value: "Presencial", label: "Presencial" },
  { value: "Remoto", label: "Remoto" },
  { value: "Híbrido", label: "Híbrido" },
];

const stateOptions: Option[] = [
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

type Mode = "create" | "edit";

const emptyInput: VacancyInput = {
  titulo_vaga: "",
  empresa_nome: "",
  descricao_vaga: "",
  cidade_vaga: "",
  estado_vaga: "",
  salario: "",
  url: "",
  cursos: [],
  pcd: false,
  modalidade: "",
  beneficios: [],
};

const PAGE_SIZE = 10;

export const AdminPage: React.FC = () => {
  const { user } = useAuth();

  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [loading, setLoading] = useState(false);

  // catálogo de cursos vindos do backend
  const [courseOptions, setCourseOptions] = useState<Option[]>([]);
  const [loadingCourses, setLoadingCourses] = useState(false);
  const [coursesError, setCoursesError] = useState<string | null>(null);

  const [mode, setMode] = useState<Mode>("create");
  const [editingId, setEditingId] = useState<number | null>(null);

  const [form, setForm] = useState<VacancyInput>(emptyInput);
  const [benefitsText, setBenefitsText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [searchTerm, setSearchTerm] = useState("");
  const [currentPage, setCurrentPage] = useState(1);

  // proteção simples: só admin
  if (user && user.isAdmin === false) {
    return (
      <div className="max-w-3xl mx-auto bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-800 mb-2">
          Área administrativa
        </h2>
        <p className="text-sm text-slate-600">
          Esta área é restrita a administradores.
        </p>
      </div>
    );
  }

  const loadVacancies = async () => {
    setLoading(true);
    const data = await getVacancies({} as VacancyFilters);
    setVacancies(data);
    setLoading(false);
    setCurrentPage(1);
  };

  const loadCourses = async () => {
    try {
      setLoadingCourses(true);
      setCoursesError(null);
      const options = await fetchCourseOptions();
      setCourseOptions(options);
    } catch (err) {
      console.error(err);
      setCoursesError("Não foi possível carregar a lista de cursos.");
    } finally {
      setLoadingCourses(false);
    }
  };

  useEffect(() => {
    loadVacancies();
    loadCourses();
  }, []);

  const resetForm = () => {
    setMode("create");
    setEditingId(null);
    setForm(emptyInput);
    setBenefitsText("");
  };

  const handleEdit = (vac: Vacancy) => {
    setMode("edit");
    setEditingId(vac.id);

    setForm({
      titulo_vaga: vac.title,
      empresa_nome: vac.company,
      descricao_vaga: vac.activities,
      cidade_vaga: vac.city ?? "",
      estado_vaga: vac.state ?? "",
      salario: vac.stipend,
      url: vac.applyUrl ?? "",
      cursos: vac.courses,
      pcd: !!vac.pcd,
      modalidade: vac.modality,
      beneficios: [],
    });

    const benefitsLines =
      vac.benefits
        ?.split(/[,;\n]/)
        .map((b) => b.trim())
        .filter(Boolean)
        .join("\n") ?? "";

    setBenefitsText(benefitsLines);
  };

  const handleDelete = async (vac: Vacancy) => {
    if (!window.confirm(`Tem certeza que deseja excluir a vaga "${vac.title}"?`)) {
      return;
    }

    try {
      setError(null);
      await deleteVacancy(vac.id);
      setSuccess("Vaga excluída com sucesso.");
      await loadVacancies();
    } catch (err) {
      console.error(err);
      setError("Erro ao excluir vaga.");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    const beneficios = benefitsText
      .split("\n")
      .map((b) => b.trim())
      .filter(Boolean);

    const payload: VacancyInput = {
      ...form,
      beneficios,
    };

    try {
      if (mode === "create") {
        await createVacancy(payload);
        setSuccess("Vaga criada com sucesso.");
      } else if (mode === "edit" && editingId != null) {
        await updateVacancy(editingId, payload);
        setSuccess("Vaga atualizada com sucesso.");
      }
      resetForm();
      await loadVacancies();
    } catch (err) {
      console.error(err);
      setError("Erro ao salvar vaga. Verifique o backend.");
    }
  };

  const handleChange = (field: keyof VacancyInput, value: any) => {
    setForm((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
    setCurrentPage(1);
  };

  // Filtro da busca geral
  const filteredVacancies = vacancies.filter((v) => {
    if (!searchTerm.trim()) return true;
    const q = searchTerm.toLowerCase();
    return (
      v.title.toLowerCase().includes(q) ||
      v.company.toLowerCase().includes(q) ||
      (v.location ?? "").toLowerCase().includes(q) ||
      (v.code ?? "").toLowerCase().includes(q)
    );
  });

  const totalPages = Math.max(
    1,
    Math.ceil(filteredVacancies.length / PAGE_SIZE)
  );
  const startIndex = (currentPage - 1) * PAGE_SIZE;
  const paginatedVacancies = filteredVacancies.slice(
    startIndex,
    startIndex + PAGE_SIZE
  );

  const goToPage = (page: number) => {
    if (page < 1 || page > totalPages) return;
    setCurrentPage(page);
  };

  return (
    <div className="flex flex-col gap-6">
      {/* FORMULÁRIO */}
      <div className="max-w-3xl mx-auto bg-white rounded-xl border border-slate-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-slate-800">
            Administração de vagas
          </h2>
          <Badge variant="info">
            {mode === "create" ? "Criando nova vaga" : "Editando vaga"}
          </Badge>
        </div>

        {error && (
          <p className="mb-3 text-xs text-red-600 bg-red-50 border border-red-100 rounded-md px-3 py-2">
            {error}
          </p>
        )}
        {success && (
          <p className="mb-3 text-xs text-green-600 bg-green-50 border border-green-100 rounded-md px-3 py-2">
            {success}
          </p>
        )}

        <form className="space-y-3" onSubmit={handleSubmit}>
          <Input
            label="Título da vaga"
            value={form.titulo_vaga}
            onChange={(e) => handleChange("titulo_vaga", e.target.value)}
            required
          />

          <Input
            label="Empresa"
            value={form.empresa_nome}
            onChange={(e) => handleChange("empresa_nome", e.target.value)}
            required
          />

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <Input
              label="Cidade"
              value={form.cidade_vaga}
              onChange={(e) => handleChange("cidade_vaga", e.target.value)}
            />
            <Select
              label="Estado"
              value={form.estado_vaga}
              onChange={(e) => handleChange("estado_vaga", e.target.value)}
              options={stateOptions}
              placeholder="Selecione"
            />
            <Select
              label="Modalidade"
              value={form.modalidade}
              onChange={(e) => handleChange("modalidade", e.target.value)}
              options={modalityOptions}
              placeholder="Selecione"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Input
              label="Bolsa / Salário"
              value={form.salario}
              onChange={(e) => handleChange("salario", e.target.value)}
              placeholder="Ex.: R$ 1.500,00 ou A combinar"
            />
            <Input
              label="URL da vaga (plataforma original)"
              value={form.url}
              onChange={(e) => handleChange("url", e.target.value)}
              placeholder="https://..."
            />
          </div>

          <MultiSelect
            label="Cursos"
            options={courseOptions}
            selectedValues={form.cursos}
            onChange={(values) => handleChange("cursos", values)}
            placeholder={
              loadingCourses
                ? "Carregando cursos..."
                : courseOptions.length === 0
                ? "Nenhum curso disponível"
                : "Selecione cursos"
            }
          />
          {coursesError && (
            <p className="mt-1 text-xs text-red-500">{coursesError}</p>
          )}

          <div className="flex items-center gap-2">
            <input
              id="pcd"
              type="checkbox"
              className="h-4 w-4"
              checked={form.pcd}
              onChange={(e) => handleChange("pcd", e.target.checked)}
            />
            <label
              htmlFor="pcd"
              className="text-sm text-slate-700 select-none"
            >
              Vaga exclusiva para PCD
            </label>
          </div>

          <div>
            <label className="text-sm font-medium text-slate-700">
              Descrição da vaga
            </label>
            <textarea
              className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              rows={4}
              value={form.descricao_vaga}
              onChange={(e) => handleChange("descricao_vaga", e.target.value)}
            />
          </div>

          <div>
            <label className="text-sm font-medium text-slate-700">
              Benefícios (um por linha)
            </label>
            <textarea
              className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              rows={3}
              value={benefitsText}
              onChange={(e) => setBenefitsText(e.target.value)}
            />
          </div>

          <div className="flex justify-between items-center pt-2">
            {mode === "edit" && (
              <Button
                type="button"
                variant="ghost"
                onClick={resetForm}
                className="text-xs"
              >
                Cancelar edição
              </Button>
            )}

            <Button type="submit" className="ml-auto">
              {mode === "create" ? "Cadastrar vaga" : "Salvar alterações"}
            </Button>
          </div>
        </form>
      </div>

      {/* LISTAGEM + BUSCA + PAGINAÇÃO */}
      <div className="max-w-5xl mx-auto bg-white rounded-xl border border-slate-200 p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
          <h3 className="text-md font-semibold text-slate-800">
            Vagas cadastradas
          </h3>
          <div className="flex-1">
            <Input
              value={searchTerm}
              onChange={handleSearchChange}
              placeholder="Ex.: desenvolvimento, banco de dados..."
            />
          </div>
          <span className="text-xs text-slate-500 sm:w-40 sm:text-right">
            Mostrando {filteredVacancies.length} de {vacancies.length} registro(s)
          </span>
        </div>

        {loading ? (
          <p className="text-sm text-slate-500">Carregando vagas...</p>
        ) : filteredVacancies.length === 0 ? (
          <p className="text-sm text-slate-500">
            Nenhuma vaga encontrada com os filtros atuais.
          </p>
        ) : (
          <>
            <div className="space-y-3">
              {paginatedVacancies.map((v) => (
                <div
                  key={v.id}
                  className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border border-slate-200 rounded-lg px-3 py-2"
                >
                  <div className="flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-medium text-sm text-slate-900">
                        {v.title}
                      </span>
                      <span className="text-xs text-slate-500">
                        {v.company}
                      </span>
                      {v.pcd && (
                        <Badge variant="danger" className="text-[10px]">
                          PCD
                        </Badge>
                      )}
                    </div>
                    <p className="text-xs text-slate-500">
                      {v.location} • {v.modality} • Bolsa: {v.stipend}
                    </p>
                  </div>

                  <div className="flex gap-2">
                    <Button
                      type="button"
                      variant="ghost"
                      className="text-xs px-2 py-1"
                      onClick={() => handleEdit(v)}
                    >
                      Editar
                    </Button>
                    <Button
                      type="button"
                      variant="ghost"
                      className="text-xs px-2 py-1 text-red-600 hover:bg-red-50"
                      onClick={() => handleDelete(v)}
                    >
                      Excluir
                    </Button>
                  </div>
                </div>
              ))}
            </div>

            {/* Paginação (10 por página) */}
            <div className="flex items-center justify-center gap-2 mt-4 text-xs text-slate-600">
              <Button
                type="button"
                variant="ghost"
                className="px-3 py-1"
                onClick={() => goToPage(currentPage - 1)}
                disabled={currentPage === 1}
              >
                Anterior
              </Button>

              <span>
                Página {currentPage} de {totalPages}
              </span>

              <Button
                type="button"
                variant="ghost"
                className="px-3 py-1"
                onClick={() => goToPage(currentPage + 1)}
                disabled={currentPage === totalPages}
              >
                Próxima
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
