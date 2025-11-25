import React from "react";

export const VacancySkeleton: React.FC = () => {
  return (
    <div className="bg-white rounded-xl shadow-md border border-slate-200 p-4 animate-pulse space-y-3">
      <div className="flex justify-between items-start gap-2">
        <div className="h-4 bg-slate-200 rounded w-2/3" />
        <div className="h-4 bg-slate-200 rounded w-16" />
      </div>

      <div className="flex gap-2">
        <div className="h-4 bg-slate-200 rounded-full w-20" />
        <div className="h-4 bg-slate-200 rounded-full w-24" />
      </div>

      <div className="grid grid-cols-2 gap-2">
        <div className="h-3 bg-slate-200 rounded" />
        <div className="h-3 bg-slate-200 rounded" />
        <div className="h-3 bg-slate-200 rounded" />
        <div className="h-3 bg-slate-200 rounded" />
      </div>

      <div className="h-8 bg-slate-200 rounded-md" />
    </div>
  );
};
