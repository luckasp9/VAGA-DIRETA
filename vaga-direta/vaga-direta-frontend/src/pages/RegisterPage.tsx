import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Input } from "../components/ui/Input";
import { Select } from "../components/ui/Select";
import type { Option } from "../components/ui/Select";
import { Button } from "../components/ui/Button";
import {
  register as registerService,
  type RegisterPayload,
} from "../services/authService";
import { fetchCourseOptions } from "../services/catalogService";
import { formatPhone } from "../utils/phone";

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

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();

  const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatPhone(e.target.value);
    setPhone(formatted);
  };

  const [courseOptions, setCourseOptions] = useState<Option[]>([]); // NOVO

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [course, setCourse] = useState("");
  const [semester, setSemester] = useState("");
  const [state, setState] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Carregar cursos do backend
  useEffect(() => {
    async function loadCourses() {
      try {
        const options = await fetchCourseOptions();
        setCourseOptions(options);
      } catch (err) {
        console.error("Erro ao carregar cursos:", err);
      }
    }

    loadCourses();
  }, []);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);

    if (!fullName || !email || !course || !semester || !state) {
      setError("Preencha todos os campos obrigatórios.");
      return;
    }

    if (password !== confirmPassword) {
      setError("As senhas não conferem.");
      return;
    }

    const payload: RegisterPayload = {
      fullName,
      email,
      phone: phone || undefined,
      course,
      semester: Number(semester),
      state,
      password,
    };

    try {
      setLoading(true);
      await registerService(payload);
      navigate("/login");
    } catch (err) {
      console.error(err);
      setError("Não foi possível finalizar o cadastro. Tente novamente.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form
      className="w-full max-w-md mx-auto bg-white rounded-xl shadow-md border border-slate-200 p-6 space-y-4"
      onSubmit={handleSubmit}
    >
      <h1 className="text-xl font-semibold text-slate-900 text-center mb-2">
        Cadastro de Usuário
      </h1>

      {error && (
        <p className="text-sm text-red-600 bg-red-50 border border-red-100 rounded-md px-3 py-2">
          {error}
        </p>
      )}

      <Input
        label="Nome completo"
        value={fullName}
        onChange={(e) => setFullName(e.target.value)}
        required
        placeholder="Digite seu nome"
      />

      <Input
        label="E-mail"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
        placeholder="seuemail@exemplo.com"
      />

      <Input
        label="Telefone (opcional)"
        value={phone}
        onChange={handlePhoneChange}
        placeholder="(99) 99999-9999"
        inputMode="numeric"
        maxLength={15}
      />

      <Select
        label="Curso"
        value={course}
        onChange={(e) => setCourse(e.target.value)}
        options={courseOptions}
        required
        placeholder={
          courseOptions.length === 0
            ? "Carregando cursos..."
            : "Selecione um curso"
        }
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
        label="Estado"
        value={state}
        onChange={(e) => setState(e.target.value)}
        options={stateOptions}
        required
        placeholder="Selecione o estado"
      />

      <Input
        label="Senha"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
        placeholder="Digite uma senha"
      />

      <Input
        label="Confirmar senha"
        type="password"
        value={confirmPassword}
        onChange={(e) => setConfirmPassword(e.target.value)}
        required
        placeholder="Repita a senha"
      />

      <Button type="submit" className="w-full" disabled={loading}>
        {loading ? "Finalizando..." : "Finalizar Cadastro"}
      </Button>

      <p className="mt-2 text-sm text-center text-slate-600">
        Já tem conta?{" "}
        <Link to="/login" className="text-primary-600 hover:underline">
          Clique aqui para entrar
        </Link>
      </p>
    </form>
  );
};
