import React from "react";
import { useNavigate } from "react-router-dom";
import type { Vacancy } from "../../types/vacancy";
import { Badge } from "../ui/Badge";
import { Button } from "../ui/Button";
import { MapPin, Building2, Monitor } from "lucide-react";

type Props = {
  vacancy: Vacancy;
};

export const VacancyCard: React.FC<Props> = ({ vacancy }) => {
  const navigate = useNavigate();

  const handleDetails = () => {
    navigate(`/vacancies/${vacancy.id}`, { state: { vacancy } });
  };

  return (
    <div className="bg-white rounded-xl shadow-md border border-slate-200 p-4 flex flex-col gap-3 transition-transform transition-shadow hover:shadow-lg hover:-translate-y-[2px]">
      <div className="flex justify-between items-start gap-2">
        <div>
          <h3 className="text-base font-semibold text-slate-800">
            {vacancy.title}
          </h3>
          <p className="text-xs text-slate-500 mt-1 flex items-center gap-1">
            <Building2 className="h-3 w-3" />
            {vacancy.company}
          </p>
        </div>
        {vacancy.type && <Badge variant="info">{vacancy.type}</Badge>}
      </div>

      <div className="flex flex-wrap gap-1">
        {vacancy.courses.map((c) => (
          <Badge key={c}>{c}</Badge>
        ))}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-1 text-xs text-slate-600">
        <p className="flex items-center gap-1">
          <MapPin className="h-3 w-3" />
          {vacancy.location}
        </p>
        <p className="flex items-center gap-1">
          <Monitor className="h-3 w-3" />
          {vacancy.modality} • {vacancy.platform}
        </p>
        <p>
          <span className="font-semibold">Bolsa: </span>
          {vacancy.stipend}
        </p>
      </div>

      <div className="mt-2">
        <Button variant="ghost" className="w-full" onClick={handleDetails}>
          Saiba mais
        </Button>
      </div>
    </div>
  );
};
