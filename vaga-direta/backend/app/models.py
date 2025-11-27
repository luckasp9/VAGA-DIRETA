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
