from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Campos base que tanto o create/update quanto a resposta usam
class VagaBase(BaseModel):
    titulo_vaga: str
    empresa_nome: str
    descricao_vaga: str
    cidade_vaga: str
    estado_vaga: str
    salario: str
    url: str
    pcd: bool
    modalidade: str


# ====== Modelo usado no POST/PUT (Admin) ======
class VagaCreate(VagaBase):
    # O que o frontend do Admin já está mandando:
    cursos: List[str] = []        # Multi-select de cursos
    beneficios: List[str] = []    # Um por linha no formulário


# ====== Modelo de resposta para o frontend (/api/vagas, /api/vagas/{id}) ======
class Vaga(VagaBase):
    id: int
    id_vaga: Optional[str]
    curso_id: str                 # **campo da tabela tcc.vaga, mantido**
    created_at: datetime

    # Campos “derivados” que não estão diretamente em tcc.vaga,
    # mas vêm de tcc.beneficio e tcc.vaga_curso/tcc.cursos:
    beneficios: List[str] = []
    cursos: List[str] = []        # Lista dos nomes de cursos ligados à vaga

    class Config:
        orm_mode = True

































































































































































from pydantic import BaseModel, EmailStr
from typing import Optional


# =========================
# Modelos de USUÁRIO
# =========================

class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr
    telefone: Optional[str] = None
    curso: Optional[str] = None
    semestre: Optional[int] = None
    estado: Optional[str] = None


class UsuarioCreate(UsuarioBase):
    """
    Dados que vêm do cadastro (inclui senha em texto).
    tipo_usuario: por padrão 'aluno'. Admin você pode setar direto no BD.
    """
    senha: str
    tipo_usuario: str = "aluno"


class UsuarioPublic(UsuarioBase):
    """
    Dados que voltam para o frontend (sem senha).
    """
    id: int
    tipo_usuario: str

    class Config:
        orm_mode = True


class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str

# =========================
# USUÁRIO PERFIL 
# =========================

class UsuarioUpdate(BaseModel):
    """
    Campos que o usuário pode alterar no perfil.
    Todos opcionais para permitir update parcial.
    """
    nome: Optional[str] = None
    telefone: Optional[str] = None
    curso: Optional[str] = None
    semestre: Optional[int] = None
    estado: Optional[str] = None