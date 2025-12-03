# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models import Vaga, VagaCreate
from app import crud

from app.models import UsuarioCreate, UsuarioPublic, UsuarioLogin, UsuarioUpdate
from app import users_crud
from app.security import verify_password

import psycopg2
import psycopg2.extras

app = FastAPI()

origins = [
    "http://localhost:5173",  # Vite
    "http://127.0.0.1:5173",
]

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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



# =========================
# ENDPOINTS DE USUÁRIO
# =========================

@app.post("/api/usuarios", response_model=UsuarioPublic, status_code=201)
def registrar_usuario(usuario_in: UsuarioCreate):
    """
    Cadastro de usuário:
      - recebe nome, email, senha etc.
      - gera hash Argon2
      - insere em tcc.usuario
      - retorna dados públicos (sem senha)
    """
    try:
        usuario = users_crud.criar_usuario(usuario_in)
        return usuario
    except psycopg2.IntegrityError:
        # e-mail já cadastrado (violação de UNIQUE)
        raise HTTPException(
            status_code=400,
            detail="Já existe um usuário cadastrado com este e-mail.",
        )


@app.post("/api/login", response_model=UsuarioPublic)
def login(dados: UsuarioLogin):
    """
    Login básico:
      - busca usuário pelo e-mail
      - verifica a senha com Argon2
      - retorna dados públicos
    """
    row = users_crud.obter_usuario_por_email(dados.email)
    if not row:
        raise HTTPException(status_code=400, detail="Credenciais inválidas.")

    # coluna 'senha' guarda o HASH
    if not verify_password(dados.senha, row["senha"]):
        raise HTTPException(status_code=400, detail="Credenciais inválidas.")

    usuario_public = UsuarioPublic(
        id=row["id"],
        nome=row["nome"],
        email=row["email"],
        tipo_usuario=row["tipo_usuario"],
        telefone=row.get("telefone"),
        curso=row.get("curso"),
        semestre=row.get("semestre"),
        estado=row.get("estado"),
    )

    return usuario_public


# =========================
# USUÁRIO PERFIL
# =========================

@app.put("/api/usuarios/{user_id}", response_model=UsuarioPublic)
def atualizar_usuario(user_id: int, usuario_in: UsuarioUpdate):
    """
    Atualiza dados de perfil do usuário.
    O front vai mandar os campos que podem mudar:
      - nome
      - telefone
      - curso
      - semestre
      - estado
    """
    usuario = users_crud.atualizar_usuario(user_id, usuario_in)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return usuario

# =========================
# CURSOS / PLATAFORMAS
# =========================

@app.get("/api/cursos", response_model=list[str])
def listar_cursos():
    """
    Retorna lista de nomes de cursos distintos
    a partir da tabela tcc.curso.
    """
    # reaproveitando a conexão do users_crud
    con = users_crud.get_connection()
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

    try:
        cur.execute("""
            SELECT DISTINCT curso
            FROM tcc.curso
            WHERE curso IS NOT NULL
            ORDER BY curso;
        """)
        rows = cur.fetchall()
        return [row["curso"] for row in rows]
    finally:
        con.close()


@app.get("/api/plataformas", response_model=list[str])
def listar_plataformas():
    """
    Retorna lista de plataformas cadastradas.
    """
    con = users_crud.get_connection()
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

    try:
        cur.execute("""
            SELECT nome_plataforma
            FROM tcc.plataforma
            WHERE nome_plataforma IS NOT NULL
            ORDER BY nome_plataforma;
        """)
        rows = cur.fetchall()
        return [row["nome_plataforma"] for row in rows]
    finally:
        con.close()
