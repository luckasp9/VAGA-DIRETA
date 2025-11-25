import React from "react";
import { cn } from "../../utils/cn"; // se não tiver esse util, te passo já já

type BadgeProps = {
  children: React.ReactNode;
  variant?: "default" | "info" | "success" | "danger";
  className?: string; // <-- ADICIONADO
};

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = "default",
  className,
}) => {
  const base =
    "inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium";

  const variants = {
    default: "bg-slate-200 text-slate-700",
    info: "bg-blue-100 text-blue-700 border border-blue-200",
    success: "bg-green-100 text-green-700 border border-green-200",
    danger: "bg-red-100 text-red-700 border border-red-200",
  };

  return (
    <span className={cn(base, variants[variant], className)}>
      {children}
    </span>
  );
};
