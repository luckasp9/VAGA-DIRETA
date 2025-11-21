import React from "react";
import { useNavigate, NavLink } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { Button } from "../ui/Button";
import logoVagaDireta from "../../assets/logo-vaga-direta.png";

export const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const handleProfile = () => {
    navigate("/profile");
  };

  return (
    <header className="bg-primary-600 text-white shadow-md sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 py-2 flex items-center justify-between gap-4">
        {/* Logo + nome */}
        <div className="flex items-center gap-2">
          <img
            src={logoVagaDireta}
            alt="Vaga Direta"
            className="h-9 w-9 rounded-full bg-white/10 object-contain"
          />
          <div className="flex flex-col leading-tight">
            <span className="font-semibold text-sm">Vaga Direta</span>
            <span className="text-[11px] text-white/80">
              Centralizador de vagas de estágio
            </span>
          </div>
        </div>

        {/* Navegação (pode crescer depois) */}
        <nav className="hidden md:flex items-center gap-4 text-xs">
          <NavLink
            to="/"
            className={({ isActive }) =>
              `uppercase tracking-wide ${
                isActive ? "font-semibold" : "text-white/80"
              }`
            }
          >
            Vagas
          </NavLink>
          <NavLink
            to="/profile"
            className={({ isActive }) =>
              `uppercase tracking-wide ${
                isActive ? "font-semibold" : "text-white/80"
              }`
            }
          >
            Perfil
          </NavLink>
        </nav>

        {/* Usuário + sair */}
        <div className="flex items-center gap-3">
          {user && (
            <button
              onClick={handleProfile}
              className="text-xs text-white hover:text-slate-100 border border-white/30 rounded-full px-3 py-1 max-w-[160px] truncate"
              title={user.fullName}
            >
              {user.fullName}
            </button>
          )}

          <Button
            variant="ghost"
            onClick={handleLogout}
            className="border border-white/40 text-xs px-3 py-1 hover:bg-white/10"
          >
            Sair
          </Button>
        </div>
      </div>
    </header>
  );
};
