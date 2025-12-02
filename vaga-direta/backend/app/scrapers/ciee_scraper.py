import os
import sys
import requests
import json
import locale

# ============================================================
# CONFIG — Ajustar PATH para detectar_cursos
# ============================================================

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT)

from app.utils.detectar_cursos import detectar_cursos

# ============================================================
# CONFIGURAÇÕES
# ============================================================

URL = "https://api.ciee.org.br/vagas/vitrine-vaga/publicadas"

PARAMS = {
    "page": 0,
    "size": 5000,
    "sort": "codigoVaga,desc",
    "tipoVaga": "ESTAGIO"
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

OUTPUT_JSON = os.path.join(DATA_DIR, "vagas_ciee.json")


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def safe(value):
    return str(value).strip() if value else ""


def formatar_moeda(valor):
    """Converte qualquer valor numérico para R$ X.XXX,XX"""
    if valor in (None, "", 0, "0"):
        return ""

    try:
        # tentativa 1: se já veio numérico
        num = float(valor)
    except:
        try:
            # tentativa 2: limpar strings tipo "2500.50", "2,500.00", etc.
            cleaned = (
                str(valor)
                .replace("R$", "")
                .replace(".", "")
                .replace(",", ".")
                .strip()
            )
            num = float(cleaned)
        except:
            return safe(valor)

    # formata para moeda brasileira
    return f"R$ {num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def detectar_modalidade(texto: str):
    t = texto.lower()

    remoto = ["remoto", "home office", "trabalho remoto", "teletrabalho"]
    hibrido = ["híbrido", "hibrido"]

    if any(k in t for k in hibrido):
        return "Híbrido"
    if any(k in t for k in remoto):
        return "Remoto"

    return "Presencial"


def detectar_pcd(texto: str):
    t = texto.lower()
    return (
        "pcd" in t
        or "p.c.d" in t
        or "portador de deficiência" in t
        or "pessoas com deficiência" in t
    )


# ============================================================
# NORMALIZAÇÃO
# ============================================================

def normalize(vaga):
    local = vaga.get("local") or {}

    texto_cursos = " ".join([
        safe(vaga.get("titulo")),
        safe(vaga.get("areaProfissional")),
    ])

    cursos = detectar_cursos(texto_cursos)
    descricao = safe(vaga.get("descricao"))

    bolsa_formatada = formatar_moeda(vaga.get("bolsaAuxilio"))

    return {
        "id": vaga.get("codigoVaga"),
        "titulo": vaga.get("tipoVaga"),
        "empresa": vaga.get("nomeEmpresa"),
        "descricao": descricao,
        "cidade": local.get("cidade"),
        "estado": local.get("uf"),
        "bolsa": bolsa_formatada,
        "beneficios": vaga.get("beneficios") or [],
        "logo": "",
        "pcd": detectar_pcd(descricao),
        "modalidade": detectar_modalidade(descricao),
        "cursos": cursos,
        "url": f"https://ciee.app/detalhes-vaga/{vaga.get('codigoVaga')}",
    }


# ============================================================
# FETCH
# ============================================================

def fetch_vagas():
    resp = requests.get(URL, params=PARAMS)
    resp.raise_for_status()
    data = resp.json()
    return data.get("content", [])


def save_json(vagas):
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(vagas, f, ensure_ascii=False, indent=4)

    print(f" Arquivo salvo em: {OUTPUT_JSON} — {len(vagas)} vagas")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print(" Coletando vagas do CIEE...")

    raw = fetch_vagas()
    print(f" Vagas recebidas: {len(raw)}")

    vagas = [normalize(v) for v in raw]

    save_json(vagas)

    print(" Finalizado com sucesso!")
