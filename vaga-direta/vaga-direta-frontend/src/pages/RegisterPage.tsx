import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Input } from "../components/ui/Input";
import { Select } from "../components/ui/Select";
import { Button } from "../components/ui/Button";
import {
  register as registerService,
  type RegisterPayload,
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

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [course, setCourse] = useState("");
  const [semester, setSemester] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);

    if (!fullName || !email || !course || !semester) {
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
      password,
      // estado REMOVIDO
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
