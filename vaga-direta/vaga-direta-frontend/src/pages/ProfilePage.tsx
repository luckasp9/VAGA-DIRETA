import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { Input } from "../components/ui/Input";
import { Select } from "../components/ui/Select";
import { Button } from "../components/ui/Button";
import {
  updateProfile,
  type UpdateProfilePayload,
} from "../services/authService";

const courseOptions = [
  { value: "Ciência da Computação", label: "Ciência da Computação" },
  { value: "Sistemas de Informação", label: "Sistemas de Informação" },
  { value: "Engenharia de Software", label: "Engenharia de Software" },
];

const semesterOptions = Array.from({ length: 10 }).map((_, index) => ({
  value: String(index + 1),
  label: `${index + 1}º semestre`,
}));

const stateOptions = [
  { value: "AC", label: "Acre (AC)" },
  { value: "AL", label: "Alagoas (AL)" },
  { value: "AP", label: "Amapá (AP)" },
  { value: "AM", label: "Amazonas (AM)" },
  { value: "BA", label: "Bahia (BA)" },
  { value: "CE", label: "Ceará (CE)" },
  { value: "DF", label: "Distrito Federal (DF)" },
  { value: "ES", label: "Espírito Santo (ES)" },
  { value: "GO", label: "Goiás (GO)" },
  { value: "MA", label: "Maranhão (MA)" },
  { value: "MT", label: "Mato Grosso (MT)" },
  { value: "MS", label: "Mato Grosso do Sul (MS)" },
  { value: "MG", label: "Minas Gerais (MG)" },
  { value: "PA", label: "Pará (PA)" },
  { value: "PB", label: "Paraíba (PB)" },
  { value: "PR", label: "Paraná (PR)" },
  { value: "PE", label: "Pernambuco (PE)" },
  { value: "PI", label: "Piauí (PI)" },
  { value: "RJ", label: "Rio de Janeiro (RJ)" },
  { value: "RN", label: "Rio Grande do Norte (RN)" },
  { value: "RS", label: "Rio Grande do Sul (RS)" },
  { value: "RO", label: "Rondônia (RO)" },
  { value: "RR", label: "Roraima (RR)" },
  { value: "SC", label: "Santa Catarina (SC)" },
  { value: "SP", label: "São Paulo (SP)" },
  { value: "SE", label: "Sergipe (SE)" },
  { value: "TO", label: "Tocantins (TO)" },
];

export const ProfilePage: React.FC = () => {
  const { user, updateUser } = useAuth();

  const [fullName, setFullName] = useState(user?.fullName ?? "");
  const [email] = useState(user?.email ?? "");
  const [phone, setPhone] = useState(user?.phone ?? "");
  const [course, setCourse] = useState(user?.course ?? "");
  const [semester, setSemester] = useState(
    user?.semester ? String(user.semester) : ""
  );
  const [state, setState] = useState(user?.state ?? "");

  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!user) {
    return (
      <div className="max-w-lg mx-auto bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <p className="text-sm text-slate-600">
          É necessário estar autenticado para acessar o perfil.
        </p>
      </div>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);
    setError(null);
    setSaving(true);

    const payload: UpdateProfilePayload = {
      fullName,
      phone,
      course,
      semester: semester ? Number(semester) : undefined,
      state,
    };

    try {
      // Atualiza no backend (FastAPI + banco)
      await updateProfile(user.id, payload);

      // Atualiza no contexto/localStorage com os mesmos dados
      updateUser({
        fullName,
        phone,
        course,
        semester: semester ? Number(semester) : undefined,
        state,
      });

      setMessage("Dados atualizados com sucesso.");
    } catch (err) {
      console.error(err);
      setError("Não foi possível atualizar os dados. Tente novamente.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-lg mx-auto bg-white rounded-xl shadow-sm border border-slate-200 p-6">
      <h2 className="text-lg font-semibold text-slate-800 mb-2">
        Meu Perfil
      </h2>
      <p className="text-xs text-slate-500 mb-4">
        Aqui você pode atualizar algumas informações do seu cadastro. As
        alterações são salvas na sua conta e refletidas nos filtros da
        plataforma.
      </p>

      {message && (
        <p className="mb-3 text-xs text-green-600 bg-green-50 border border-green-100 rounded-md px-3 py-2">
          {message}
        </p>
      )}

      {error && (
        <p className="mb-3 text-xs text-red-600 bg-red-50 border border-red-100 rounded-md px-3 py-2">
          {error}
        </p>
      )}

      <form className="space-y-3" onSubmit={handleSubmit}>
        <Input
          label="Nome completo"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          required
        />

        <Input
          label="E-mail"
          type="email"
          value={email}
          disabled
          className="bg-slate-50"
        />

        <Input
          label="Telefone"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          placeholder="(99) 99999-9999"
        />

        <Select
          label="Curso"
          value={course}
          onChange={(e) => setCourse(e.target.value)}
          options={courseOptions}
          required
          placeholder="Selecione um curso"
        />

        <Select
          label="Semestre atual"
          value={semester}
          onChange={(e) => setSemester(e.target.value)}
          options={semesterOptions}
          required
          placeholder="Selecione o semestre"
        />

        <Select
          label="Estado (UF)"
          value={state}
          onChange={(e) => setState(e.target.value)}
          options={stateOptions}
          required
          placeholder="Selecione o estado"
        />

        <Button type="submit" className="w-full" disabled={saving}>
          {saving ? "Salvando..." : "Salvar alterações"}
        </Button>
      </form>
    </div>
  );
};
