import React from "react";
import { Header } from "./Header";

type MainLayoutProps = {
  children: React.ReactNode;
};

export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Header />

      <main className="flex-1 max-w-6xl mx-auto w-full px-4 py-6">
        {children}
      </main>

      <footer className="w-full border-t border-slate-200 bg-white mt-4">
        <div className="max-w-6xl mx-auto px-4 py-3 text-xs text-slate-400 text-center">
          Vaga Direta © 2025 – Protótipo acadêmico
        </div>
      </footer>
    </div>
  );
};
