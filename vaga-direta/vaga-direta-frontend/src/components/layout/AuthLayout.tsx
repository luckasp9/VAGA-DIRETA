import React from "react";
import logoVagaDireta from "../../assets/logo-vaga-direta.png";

type AuthLayoutProps = {
  title: string;
  children: React.ReactNode;
};

export const AuthLayout: React.FC<AuthLayoutProps> = ({ title, children }) => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100 px-4">
      <div className="w-full max-w-md bg-white shadow-lg rounded-xl p-8">
        <div className="mb-6 text-center flex flex-col items-center gap-2">
        <img
            src={logoVagaDireta}
            alt="Vaga Direta"
            className="h-12 w-12 rounded-full object-contain"
          />
          <h1 className="text-2xl font-bold text-primary-600">Vaga Direta</h1>
          <p className="mt-1 text-slate-500">{title}</p>
        </div>


        {children}

        <p className="mt-6 text-xs text-center text-slate-400">
          Vaga Direta © 2025
        </p>
        <p className="text-[10px] text-center text-slate-300">
          Protótipo acadêmico – UDF
        </p>
      </div>
    </div>
  );
};
