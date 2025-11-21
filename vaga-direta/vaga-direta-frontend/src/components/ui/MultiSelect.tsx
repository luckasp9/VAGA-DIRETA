import React from "react";
import type { Option } from "./Select";
import { ChevronDown, ChevronUp } from "lucide-react";

type MultiSelectProps = {
  label?: string;
  options: Option[];
  selectedValues: string[];
  onChange: (values: string[]) => void;
  placeholder?: string;
};

export const MultiSelect: React.FC<MultiSelectProps> = ({
  label,
  options,
  selectedValues,
  onChange,
  placeholder = "Selecione...",
}) => {
  const [isOpen, setIsOpen] = React.useState(false);
  const [search, setSearch] = React.useState("");

  const containerRef = React.useRef<HTMLDivElement | null>(null);

  // Fecha ao clicar fora
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () =>
      document.removeEventListener("mousedown", handleClickOutside);
  }, [isOpen]);

  const toggleValue = (value: string) => {
    if (selectedValues.includes(value)) {
      onChange(selectedValues.filter((v) => v !== value));
    } else {
      onChange([...selectedValues, value]);
    }
  };

  const filteredOptions = options.filter((opt) =>
    opt.label.toLowerCase().includes(search.toLowerCase())
  );

  const summaryLabel =
    selectedValues.length === 0
      ? placeholder
      : selectedValues.length === 1
      ? options.find((o) => o.value === selectedValues[0])?.label ??
        placeholder
      : `${selectedValues.length} selecionados`;

  return (
    <div
      className="flex flex-col gap-1 relative"
      ref={containerRef}
    >
      {label && (
        <label className="text-sm font-medium text-slate-700 mb-[1px]">
          {label}
        </label>
      )}

      {/* Botão do dropdown */}
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        className="w-full flex items-center justify-between rounded-md border border-slate-300 bg-white px-3 py-2 text-sm shadow-sm hover:border-primary-500 focus:ring-2 focus:ring-primary-500"
      >
        <span
          className={
            selectedValues.length === 0
              ? "text-slate-400"
              : "text-slate-700"
          }
        >
          {summaryLabel}
        </span>

        {isOpen ? (
          <ChevronUp className="h-4 w-4 text-slate-500" />
        ) : (
          <ChevronDown className="h-4 w-4 text-slate-500" />
        )}
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute left-0 top-full mt-1 w-full rounded-md border border-slate-200 bg-white shadow-lg z-50">
          {/* Busca */}
          <div className="p-2 border-b border-slate-200 bg-slate-50">
            <input
              type="text"
              placeholder="Buscar..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full rounded-md border border-slate-300 px-2 py-1 text-sm focus:ring-1 focus:ring-primary-500"
            />
          </div>

          {/* Lista */}
          <div className="max-h-52 overflow-y-auto p-2 flex flex-col gap-1 text-sm">
            {filteredOptions.length === 0 && (
              <span className="text-slate-400 text-xs">
                Nenhum item encontrado
              </span>
            )}

            {filteredOptions.map((opt) => (
              <label
                key={opt.value}
                className="flex items-center gap-2 rounded-md px-2 py-1 cursor-pointer hover:bg-slate-50"
              >
                <input
                  type="checkbox"
                  className="h-4 w-4"
                  checked={selectedValues.includes(opt.value)}
                  onChange={() => toggleValue(opt.value)}
                />
                <span className="text-slate-700">{opt.label}</span>
              </label>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
