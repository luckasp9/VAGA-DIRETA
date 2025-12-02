import os
import json
import subprocess
import psycopg2
from time import sleep

# ---------------------------
# Configurações
# ---------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRAPERS_DIR = os.path.join(os.path.dirname(BASE_DIR), "scrapers")
DATA_DIR = os.path.join(SCRAPERS_DIR, "data")

PLATAFORMA_MAP = {
    "ciee": 1,
    "nube": 2,
    "catho": 3,
    "empregare": 4
}

# ---------------------------
# Conexão com o banco
# ---------------------------
def connect():
    return psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="1234"
    )

# ---------------------------
# Reset tabelas
# ---------------------------
def reset_tables():
    sql = """
    DROP TABLE IF EXISTS tcc.beneficio CASCADE;
    DROP TABLE IF EXISTS tcc.curso CASCADE;
    DROP TABLE IF EXISTS tcc.vaga CASCADE;

    CREATE TABLE tcc.vaga (
        id SERIAL PRIMARY KEY,
        id_vaga VARCHAR UNIQUE,
        titulo_vaga VARCHAR(255),
        empresa_nome VARCHAR(255),
        descricao_vaga TEXT,
        cidade_vaga VARCHAR(100),
        estado_vaga VARCHAR(100),
        salario VARCHAR(255),
        url VARCHAR(255),
        pcd BOOLEAN,
        modalidade VARCHAR(255),
        id_plataforma INTEGER,
        created_at TIMESTAMP DEFAULT NOW()
    );

    CREATE TABLE tcc.curso (
        id SERIAL PRIMARY KEY,
        vaga_id INT REFERENCES tcc.vaga(id) ON DELETE CASCADE,
        curso TEXT
    );

    CREATE TABLE tcc.beneficio (
        id SERIAL PRIMARY KEY,
        vaga_id INT REFERENCES tcc.vaga(id) ON DELETE CASCADE,
        beneficio TEXT NOT NULL
    );
    """
    conn = connect()
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Tabelas tcc.vaga, tcc.curso e tcc.beneficio resetadas.")

# ---------------------------
# Load JSON
# ---------------------------
def load_json(nome):
    path = os.path.join(DATA_DIR, nome)
    if not os.path.exists(path):
        print(f"⚠ Arquivo {nome} não encontrado.")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ---------------------------
# Insert vagas
# ---------------------------
def insert_vagas(vagas, id_plataforma):
    if not vagas:
        return

    # Remove duplicatas pelo id da vaga
    unique_vagas = {v["id"]: v for v in vagas if v.get("id")}.values()

    conn = connect()
    cur = conn.cursor()

    sql_vaga = """
    INSERT INTO tcc.vaga (
        id_vaga, titulo_vaga, empresa_nome, descricao_vaga,
        cidade_vaga, estado_vaga, salario, url, pcd, modalidade, id_plataforma
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ON CONFLICT (id_vaga) DO NOTHING
    RETURNING id;
    """

    sql_curso = "INSERT INTO tcc.curso (vaga_id, curso) VALUES (%s,%s);"
    sql_beneficio = "INSERT INTO tcc.beneficio (vaga_id, beneficio) VALUES (%s,%s);"

    for v in unique_vagas:
        cur.execute(sql_vaga, (
            v.get("id"),
            v.get("titulo"),
            v.get("empresa"),
            v.get("descricao"),
            v.get("cidade"),
            v.get("estado"),
            v.get("bolsa") or "",
            v.get("url"),
            v.get("pcd"),
            v.get("modalidade"),
            id_plataforma
        ))
        vaga_id = cur.fetchone()[0]

        # Cursos
        for c in v.get("cursos", []):
            cur.execute(sql_curso, (vaga_id, str(c)))

        beneficios = v.get("beneficios") or v.get("beneficio") or []
        for b in beneficios:
            # Se for dict, pega só o campo 'beneficio'
            if isinstance(b, dict):
                benef_text = b.get("beneficio", "")
            else:
                benef_text = str(b)
            if benef_text:
                cur.execute(sql_beneficio, (vaga_id, benef_text))


    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Inseridas {len(unique_vagas)} vagas da plataforma {id_plataforma}")

# ---------------------------
# Rodar scraper
# ---------------------------
def run_scraper(path):
    print(f"🚀 Rodando scraper: {path}")
    result = subprocess.run(
        ["python", path],
        cwd=SCRAPERS_DIR,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"❌ Erro no scraper {path}:\n", result.stderr)
    else:
        print(f"✅ Scraper finalizado: {path}")

# ---------------------------
# Main
# ---------------------------
if __name__ == "__main__":
    print("🔄 Iniciando processo completo: scraping + insert")
    reset_tables()

    # Rodar todos os scrapers
    scrapers = ["ciee_scraper.py"#, "nube_scraper.py"
                , "catho_scraper.py", "empregare_scraper.py"]
    for s in scrapers:
        run_scraper(os.path.join(SCRAPERS_DIR, s))
        sleep(1)  # evita sobrecarga / problemas de I/O

    # Inserir no banco
    for nome, plataforma_id in PLATAFORMA_MAP.items():
        arquivo = f"vagas_{nome}.json"
        vagas = load_json(arquivo)
        insert_vagas(vagas, plataforma_id)

    print("✨ Processo completo finalizado!")
