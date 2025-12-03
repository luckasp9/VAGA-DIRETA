from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


# ======================================================
# MODELOS DE VAGA
# ======================================================

class VagaBase(BaseModel):
    """
    Campos base da vaga. Usados tanto na criação/edição
    quanto nas respostas da API.
    """

    titulo_vaga: str
    empresa_nome: str

    # Estes campos podem ser NULL no banco, então deixamos opcionais
    descricao_vaga: Optional[str] = None
    cidade_vaga: Optional[str] = None
    estado_vaga: Optional[str] = None
    salario: Optional[str] = None
    url: Optional[str] = None

    pcd: Optional[bool] = None
    modalidade: Optional[str] = None

    # Lista de nomes de cursos vinculados à vaga
    cursos: List[str] = Field(default_factory=list)


class VagaCreate(VagaBase):
    """
    Modelo usado no POST/PUT da área administrativa.
    O formulário do Admin manda:
      - cursos: lista de nomes de cursos selecionados
      - beneficios: um benefício por linha
    """

    cursos: List[str] = Field(default_factory=list)
    beneficios: List[str] = Field(default_factory=list)


class Vaga(VagaBase):
    """
    Modelo de resposta para o frontend em:
      - GET /api/vagas
      - GET /api/vagas/{id}
      - POST/PUT /api/vagas (retorno)
    """

    id: int
    id_vaga: Optional[str] = None
    created_at: datetime

    beneficios: List[str] = Field(default_factory=list)
    cursos: List[str] = Field(default_factory=list)

    class Config:
        orm_mode = True


# ======================================================
# MODELOS DE USUÁRIO
# ======================================================

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
    tipo_usuario: por padrão 'aluno'.
    Usuário admin você configura direto no banco.
    """
    senha: str
    tipo_usuario: str = "aluno"


class UsuarioPublic(UsuarioBase):
    """
    Dados que voltam para o frontend (sem senha).
    Usado em:
      - POST /api/usuarios
      - POST /api/login
      - PUT /api/usuarios/{id}
    """
    id: int
    tipo_usuario: str

    class Config:
        orm_mode = True


class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str


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
