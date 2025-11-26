import React, { useEffect, useState } from "react";
import { useNavigate, useParams, useLocation } from "react-router-dom";
import type { Vacancy } from "../types/vacancy";
import { getVacancyById } from "../services/vacancyService";
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";
import { MapPin, Building2, Monitor, ChevronLeft } from "lucide-react";

type LocationState = {
  vacancy?: Vacancy;
};

export const VacancyDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const location = useLocation();

  const state = (location.state as LocationState | null) || {};
  const vacancyFromState = state.vacancy;

  const [vacancy, setVacancy] = useState<Vacancy | null>(
    vacancyFromState ?? null
  );
  const [loading, setLoading] = useState(!vacancyFromState);

  useEffect(() => {
    // Se já veio pelo state, não precisa buscar de novo
    if (vacancyFromState) return;

    const load = async () => {
      if (!id) {
        setLoading(false);
        return;
      }

      const numericId = Number(id);
      if (Number.isNaN(numericId)) {
        console.error("ID inválido na URL:", id);
        setLoading(false);
        return;
      }

      const data = await getVacancyById(numericId);
      setVacancy(data);
      setLoading(false);
    };

    load();
  }, [id, vacancyFromState]);

  const handleBack = () => {
    navigate(-1);
  };

  const handleApply = () => {
    if (vacancy?.applyUrl) {
      window.open(vacancy.applyUrl, "_blank");
    } else {
      console.log("Aplicar na vaga:", vacancy?.id);
    }
  };

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto bg-white rounded-xl shadow-md border border-slate-200 p-6">
        <p className="text-sm text-slate-500">Carregando vaga...</p>
      </div>
    );
  }

  if (!vacancy) {
    return (
      <div className="max-w-3xl mx-auto bg-white rounded-xl shadow-md border border-slate-200 p-6 space-y-4">
        <p className="text-sm text-red-500 font-medium">
          Vaga não encontrada.
        </p>
        <Button
          variant="ghost"
          onClick={handleBack}
          className="inline-flex items-center gap-1"
        >
          <ChevronLeft className="h-4 w-4" />
          Voltar
        </Button>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto bg-white rounded-xl shadow-md border border-slate-200 p-6 space-y-5">
      <button
        onClick={handleBack}
        className="text-xs text-primary-600 hover:underline inline-flex items-center gap-1 mb-2"
      >
        <ChevronLeft className="h-3 w-3" />
        Voltar
      </button>

      <div className="flex justify-between items-start gap-3">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">
            {vacancy.title}
          </h1>
          <p className="text-sm text-slate-600 mt-1 flex items-center gap-1">
            <Building2 className="h-4 w-4" />
            {vacancy.company}
          </p>
          <p className="text-xs text-slate-500 mt-0.5">
            Código: {vacancy.code}
          </p>
        </div>
        {vacancy.type && (
          <Badge variant="info" className="self-start">
            {vacancy.type}
          </Badge>
        )}
      </div>

      <div className="flex flex-wrap gap-2">
        {vacancy.courses.map((c) => (
          <Badge key={c}>{c}</Badge>
        ))}
      </div>

      {/* Informações resumidas da vaga */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm text-slate-700">
        <p className="flex items-center gap-2">
          <MapPin className="h-4 w-4" />
          {vacancy.location}
        </p>
        <p className="flex items-center gap-2">
          <Monitor className="h-4 w-4" />
          {vacancy.modality} • {vacancy.platform}
        </p>
        <p>
          <span className="font-semibold">Bolsa: </span>
          {vacancy.stipend}
        </p>
      </div>

      {/* Descrição + benefícios */}
      <div className="border-t border-slate-200 pt-4 space-y-3 text-sm text-slate-800">
        <div>
          <h2 className="font-semibold text-slate-900 mb-1">
            Descrição da vaga
          </h2>
          <p className="text-slate-700 whitespace-pre-line">
            {vacancy.activities || vacancy.requirements || "Não informado."}
          </p>
        </div>

        {vacancy.benefits && (
          <div>
            <h2 className="font-semibold text-slate-900 mb-1">Benefícios</h2>
            <ul className="text-slate-700 space-y-1 list-disc list-inside">
              {vacancy.benefits
                .split(/[,;\n]/)            // separa por vírgula, ponto e vírgula ou quebra de linha
                .map((b) => b.trim())
                .filter(Boolean)
                .map((b, idx) => (
                  <li key={idx}>{b}</li>
                ))}
            </ul>
          </div>
        )}
      </div>

      <div className="flex justify-end gap-2 pt-2">
        <Button variant="ghost" onClick={handleBack}>
          Voltar
        </Button>
        <Button onClick={handleApply}>Inscrever-se</Button>
      </div>
    </div>
  );
};
