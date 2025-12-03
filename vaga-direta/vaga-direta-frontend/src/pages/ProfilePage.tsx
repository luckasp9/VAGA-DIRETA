import React, { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { Input } from "../components/ui/Input";
import { Select } from "../components/ui/Select";
import { Button } from "../components/ui/Button";
import { formatPhone } from "../utils/phone";

type Option = {
  value: string;
  label: string;
};

const semesterOptions: Option[] = Array.from({ length: 10 }).map(
  (_, index) => ({
    value: String(index + 1),
    label: `${index + 1}º semestre`,
  })
);

const stateOptions: Option[] = [
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

const COURSES_API_URL = "http://localhost:8000/api/cursos";

export const ProfilePage: React.FC = () => {
  const { user, updateUser } = useAuth();

const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  const formatted = formatPhone(e.target.value);
  setPhone(formatted);
};



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

  // cursos vindos do backend
  const [courseOptions, setCourseOptions] = useState<Option[]>([]);
  const [loadingCourses, setLoadingCourses] = useState(false);
  const [coursesError, setCoursesError] = useState<string | null>(null);

  useEffect(() => {
    const loadCourses = async () => {
      setLoadingCourses(true);
      setCoursesError(null);

      try {
        const res = await fetch(COURSES_API_URL);
        if (!res.ok) {
          throw new Error("Erro ao buscar cursos");
        }

        const data = await res.json();

        // Aceita tanto string[] quanto array de objetos { nome / curso / nome_curso }
        const names: string[] = Array.isArray(data)
          ? data
              .map((item: any) => {
                if (typeof item === "string") return item;
                return (
                  item.nome ??
                  item.curso ??
                  item.nome_curso ??
                  "" // ignora se não conseguir mapear
                );
              })
              .filter((n: string) => !!n)
          : [];

        let options: Option[] = names.map((n) => ({
          value: n,
          label: n,
        }));

        // garante que o curso atual do usuário aparece na lista
        if (user?.course && !options.some((o) => o.value === user.course)) {
          options = [
            { value: user.course, label: user.course },
            ...options,
          ];
        }

        setCourseOptions(options);
      } catch (err) {
        console.error(err);
        setCoursesError("Não foi possível carregar a lista de cursos.");
        // fallback: pelo menos o curso atual
        if (user?.course) {
          setCourseOptions([
            { value: user.course, label: user.course },
          ]);
        }
      } finally {
        setLoadingCourses(false);
      }
    };

    loadCourses();
  }, [user?.course]);

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
    setSaving(true);

    try {
      await updateUser({
        fullName,
        phone,
        course,
        semester: Number(semester),
        state,
      });

      setMessage("Dados atualizados com sucesso.");
    } catch (err) {
      console.error(err);
      setMessage("Não foi possível atualizar os dados. Tente novamente.");
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
        Aqui você pode atualizar algumas informações do seu cadastro.
      </p>

      {message && (
        <p
          className={`mb-3 text-xs rounded-md px-3 py-2 ${
            message.startsWith("Não foi")
              ? "text-red-600 bg-red-50 border border-red-100"
              : "text-green-600 bg-green-50 border border-green-100"
          }`}
        >
          {message}
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
          onChange={handlePhoneChange}
          placeholder="(99) 99999-9999"
          inputMode="numeric"
          maxLength={15}
        />

        <div className="flex flex-col gap-1">
          <Select
            label="Curso"
            value={course}
            onChange={(e) => setCourse(e.target.value)}
            options={courseOptions}
            required
            placeholder={
              loadingCourses
                ? "Carregando cursos..."
                : "Selecione um curso"
            }
          />
          {coursesError && (
            <span className="text-xs text-red-500">{coursesError}</span>
          )}
        </div>

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
