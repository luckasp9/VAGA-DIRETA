import React, { useEffect, useState } from "react";
import type { Vacancy } from "../types/vacancy";
//import { getVagas } from "../services/apiVagas";
import {
  getVacancies,
  type VacancyFilters,
} from "../services/vacancyService";
import VacancyFiltersBar from "../components/vacancies/VacancyFilters";
import { VacancyCard } from "../components/vacancies/VacancyCard";
import { VacancySkeleton } from "../components/vacancies/VacancySkeleton";
import { Button } from "../components/ui/Button";



const PAGE_SIZE = 6;

export const HomePage: React.FC = () => {
  const [filters, setFilters] = useState<VacancyFilters>({
    keyword: "",
    courses: [],
    modality: "",
    platform: "",
    shift: "",
    types: [],
  });

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
    const data = await getVacancies(currentFilters);
    setVacancies(data);
    setLoading(false);
  };

  useEffect(() => {
    loadVacancies(filters);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleApplyFilters = () => {
    loadVacancies(filters);
  };

  const handleClearFilters = () => {
    const cleared: VacancyFilters = {
      keyword: "",
      courses: [],
      modality: "",
      platform: "",
      shift: "",
      types: [],
    };
    setFilters(cleared);
    loadVacancies(cleared);
  };

  const goToPage = (page: number) => {
    if (page < 1 || page > totalPages) return;
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="flex flex-col gap-4">
      <VacancyFiltersBar
        filters={filters}
        onChange={setFilters}
        onApply={handleApplyFilters}
        onClear={handleClearFilters}
        loading={loading}
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

          {/* Paginação centralizada */}
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
