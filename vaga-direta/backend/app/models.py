from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Vaga(BaseModel):
    id: int
    id_vaga: Optional[str]
    titulo_vaga: str
    empresa_nome: str
    descricao_vaga: str
    cidade_vaga: str
    estado_vaga: str
    salario: str
    url: str
    cursos: List[str] = []
    pcd: bool
    modalidade: str
    created_at: datetime
    beneficios: List[str] = []
    plataforma: str
    
