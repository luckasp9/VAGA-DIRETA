import React, { useEffect, useState } from "react";
import type { Vacancy } from "../types/vacancy";
import {
  getVacancies,
  type VacancyFilters,
} from "../services/vacancyService";
import VacancyFiltersBar from "../components/vacancies/VacancyFilters";
import { VacancyCard } from "../components/vacancies/VacancyCard";
import { VacancySkeleton } from "../components/vacancies/VacancySkeleton";
import { Button } from "../components/ui/Button";
import { useAuth } from "../context/AuthContext";

const PAGE_SIZE = 6;
const FILTERS_STORAGE_KEY = "vaga-direta:vacancy-filters";

export const HomePage: React.FC = () => {
  const { user } = useAuth();

  const [filters, setFilters] = useState<VacancyFilters>(() => ({
    keyword: "",
    courses: user?.course ? [user.course] : [],
    modality: "",
    pcd: "",
    state: user?.state ?? "",
    city: "",
  }));

  const [allVacancies, setAllVacancies] = useState<Vacancy[]>([]);
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);

  const totalPages = Math.max(1, Math.ceil(vacancies.length / PAGE_SIZE));
  const startIndex = (currentPage - 1) * PAGE_SIZE;
  const paginatedVacancies = vacancies.slice(
    startIndex,
    startIndex + PAGE_SIZE
  );

  const loadVacancies = async (currentFilters: VacancyFilters) => {
    setLoading(true);
    setCurrentPage(1);

    const { city, ...rest } = currentFilters;

    const [all, filtered] = await Promise.all([
      getVacancies({ ...rest, city: "" }),
      getVacancies(currentFilters),
    ]);

    setAllVacancies(all);
    setVacancies(filtered);
    setLoading(false);
  };

  // Ao montar, tenta recuperar filtros salvos.
  useEffect(() => {
    const stored = localStorage.getItem(FILTERS_STORAGE_KEY);

    if (stored) {
      try {
        const parsed = JSON.parse(stored) as VacancyFilters;

        const effective: VacancyFilters = {
          keyword: parsed.keyword ?? "",
          courses:
            parsed.courses && parsed.courses.length > 0
              ? parsed.courses
              : user?.course
              ? [user.course]
              : [],
          modality: parsed.modality ?? "",
          pcd: parsed.pcd ?? "",
          state: parsed.state ?? user?.state ?? "",
          city: parsed.city ?? "",
        };

        setFilters(effective);
        loadVacancies(effective);
        return;
      } catch (e) {
        console.warn("Não foi possível ler filtros salvos:", e);
      }
    }

    // Se não tem nada salvo, usa os filtros padrão (com curso/estado do usuário)
    loadVacancies(filters);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  const handleFiltersChange = (next: VacancyFilters) => {
      setFilters(next);
      localStorage.setItem(FILTERS_STORAGE_KEY, JSON.stringify(next));
  };

  const handleApplyFilters = () => {
    localStorage.setItem(FILTERS_STORAGE_KEY, JSON.stringify(filters));
    loadVacancies(filters);
  };

  const handleClearFilters = () => {
    const cleared: VacancyFilters = {
      keyword: "",
      courses: filters.courses ?? [], // mantém curso
      modality: "",
      pcd: "",
      state: filters.state ?? "", // mantém estado
      city: "", // limpa cidade
    };

    setFilters(cleared);
    localStorage.setItem(FILTERS_STORAGE_KEY, JSON.stringify(cleared));
    loadVacancies(cleared);
  };

  const goToPage = (page: number) => {
    if (page < 1 || page > totalPages) return;
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  // cidades disponíveis (já respeitando o estado)
  const cityOptions = Array.from(
    new Set(
      allVacancies
        .filter((v) =>
          filters.state && v.state ? v.state === filters.state : true
        )
        .map((v) => v.city)
        .filter((c): c is string => !!c)
    )
  ).sort();

  return (
    <div className="flex flex-col gap-4">
      <VacancyFiltersBar
        filters={filters}
        onChange={handleFiltersChange}
        onApply={handleApplyFilters}
        onClear={handleClearFilters}
        loading={loading}
        cityOptions={cityOptions}
      />

      {loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Array.from({ length: PAGE_SIZE }).map((_, idx) => (
            <VacancySkeleton key={idx} />
          ))}
        </div>
      )}

      {!loading && paginatedVacancies.length === 0 && (
        <p className="text-sm text-slate-500">
          Nenhuma vaga encontrada. Tente ajustar os filtros.
        </p>
      )}

      {!loading && paginatedVacancies.length > 0 && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {paginatedVacancies.map((vacancy) => (
              <VacancyCard key={vacancy.id} vacancy={vacancy} />
            ))}
          </div>

          <div className="flex flex-col items-center gap-2 mt-6 text-xs text-slate-600">
            <div className="flex items-center gap-2">
              <Button
                type="button"
                variant="ghost"
                className="px-3 py-1"
                onClick={() => goToPage(currentPage - 1)}
                disabled={currentPage === 1}
              >
                Anterior
              </Button>

            {Array.from({ length: totalPages }).map((_, index) => {
              const page = index + 1;
              const isActive = page === currentPage;
              return (
                <button
                  key={page}
                  onClick={() => goToPage(page)}
                  className={`h-8 w-8 rounded-md text-xs font-medium transition ${
                    isActive
                      ? "bg-primary-600 text-white"
                      : "bg-white border border-slate-300 text-slate-700 hover:bg-slate-100"
                  }`}
                >
                  {page}
                </button>
              );
            })}

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

            <span className="opacity-80">
              Página {currentPage} de {totalPages} • {vacancies.length} vagas
              encontradas
            </span>
          </div>
        </>
      )}
    </div>
  );
};
