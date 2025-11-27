# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models import Vaga, VagaCreate
from app import crud

app = FastAPI()

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # em produção, restringe isso
    allow_headers=["*"],
    allow_methods=["*"],
)


# =========================
# Rotas de vagas (Home + Admin)
# =========================

@app.get("/api/vagas", response_model=list[Vaga])
def listar_vagas():
    """
    Lista todas as vagas (Home / Admin).
    """
    return crud.listar_vagas()


@app.get("/api/vagas/{vaga_id}", response_model=Vaga)
def detalhar_vaga(vaga_id: int):
    """
    Detalhe de uma vaga específica (Saiba mais).
    """
    vaga = crud.obter_vaga(vaga_id)
    if not vaga:
        raise HTTPException(status_code=404, detail="Vaga não encontrada.")
    return vaga


@app.post("/api/vagas", response_model=Vaga, status_code=201)
def criar_vaga(vaga_in: VagaCreate):
    """
    Criação de vaga (Admin).
    """
    return crud.criar_vaga(vaga_in)


@app.put("/api/vagas/{vaga_id}", response_model=Vaga)
def atualizar_vaga(vaga_id: int, vaga_in: VagaCreate):
    """
    Atualização de vaga (Admin).
    """
    vaga = crud.atualizar_vaga(vaga_id, vaga_in)
    if not vaga:
        raise HTTPException(status_code=404, detail="Vaga não encontrada.")
    return vaga


@app.delete("/api/vagas/{vaga_id}", status_code=204)
def apagar_vaga(vaga_id: int):
    """
    Exclusão de vaga (Admin).
    """
    ok = crud.excluir_vaga(vaga_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Vaga não encontrada.")
    # 204 = sem conteúdo
    return
