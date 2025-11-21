from fastapi import APIRouter
from app.APIs.api_jsearch import buscar_vagas_jsearch
from app.APIs.api_adzuna import buscar_vagas_adzuna
from app.APIs.api_empregare import buscar_vagas_empregare
router = APIRouter(prefix="/vagas", tags=["Vagas API"])

# --------------------- JSEARCH ---------------------
@router.get("/jsearch")
def vagas_jsearch(query: str = "estágio", paginas: int = 1):
    """Rota que retorna o JSON completo do JSearch."""
    return buscar_vagas_jsearch(query, paginas)

# --------------------- ADZUNA ----------------------
@router.get("/adzuna")
def vagas_adzuna(query: str = "estágio", paginas: int = 1):
    """Rota que retorna o JSON completo do Adzuna."""
    return buscar_vagas_adzuna(query, paginas)

    
@router.get("/empregare")
def vagas_empregare(nivel: str = "Estágio", pagina: int = 1, itens: int = 9999):
    """Retorna vagas diretamente da API do Empregare."""
    return buscar_vagas_empregare(pagina=pagina, itens_por_pagina=itens, nivel=nivel)