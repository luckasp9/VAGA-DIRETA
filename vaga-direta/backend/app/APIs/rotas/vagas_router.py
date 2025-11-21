from fastapi import APIRouter
from app.APIs.api_jsearch import buscar_vagas_jsearch
from app.APIs.api_adzuna import buscar_vagas_adzuna
from app.APIs.api_super_estagios import buscar_vagas_super_estagios

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

@router.get("/super-estagios")
def vagas_super_estagios(
    id_estado: int = 7,
    id_nivel_ensino: int = 2,
    id_curso: int = 7,
    id_cidade: str = "",
    limite: int = 0
):
    """Rota que retorna vagas do Super Estágios."""
    return buscar_vagas_super_estagios(
        id_estado=id_estado,
        id_nivel_ensino=id_nivel_ensino,
        id_curso=id_curso,
        id_cidade=id_cidade,
        limite=limite
    )