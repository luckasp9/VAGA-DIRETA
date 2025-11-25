from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import psycopg2.extras
from app.models import Vaga


app = FastAPI()

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"]
)

# --- Conexão ---
def conn():
    return psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="1234"
    )

# --- ENDPOINT /api/vagas ---
@app.get("/api/vagas", response_model=list[Vaga])
def listar_vagas():
    con = conn()
    cur = con.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Buscar vagas
    cur.execute("SELECT * FROM tcc.vaga;")
    vagas = cur.fetchall()

    resultado = []

    for vaga in vagas:
        vaga_dict = dict(vaga)

        # Buscar benefícios da vaga
        cur.execute("""
            SELECT beneficio 
            FROM tcc.beneficio 
            WHERE vaga_id = %s;
        """, (vaga["id"],))

        beneficios_rows = cur.fetchall()
        beneficios = [row["beneficio"] for row in beneficios_rows]

        vaga_dict["beneficios"] = beneficios
        resultado.append(vaga_dict)

    con.close()
    return resultado
