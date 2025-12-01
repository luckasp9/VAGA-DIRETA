import os
import sys

# Garante que o Python encontre o módulo utils
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT)

from app.utils.detectar_cursos import detectar_cursos
import requests
import json

# ============================================================
# CONFIGURAÇÕES
# ============================================================

URL = "https://api.ciee.org.br/vagas/vitrine-vaga/publicadas"

PARAMS = {
    "page": 0,
    "size": 5000,  # pega todas as vagas
    "sort": "codigoVaga,desc",
    "tipoVaga": "ESTAGIO"
}

OUTPUT_JSON = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "vagas_ciee.json"
)


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def safe(value):
    """Evita erro de NoneType ao concatenar textos."""
    return str(value).strip() if value else ""


def detectar_modalidade(texto: str):
    """Detecta se é remoto/presencial/híbrido com base no texto da vaga."""
    t = texto.lower()

    if "home office" in t or "remoto" in t:
        return "Remoto"
    if "híbrido" in t or "hibrido" in t:
        return "Híbrido"

    return "Presencial"


def detectar_pcd(texto: str):
    """Detecta se a vaga é para PCD."""
    t = texto.lower()
    return (
        "pcd" in t or
        "p.c.d" in t or
        "portador de deficiência" in t or
        "pessoas com deficiência" in t
    )


# ============================================================
# NORMALIZADOR
# ============================================================

def normalize(vaga):
    """Transforma o objeto crú do CIEE em um modelo padrão do sistema."""

    local = vaga.get("local") or {}

    texto_para_cursos = " ".join([
        safe(vaga.get("titulo")),
        safe(vaga.get("areaProfissional")),
        safe(vaga.get("atividades")),
        safe(vaga.get("descricao"))
    ])

    cursos = detectar_cursos(texto_para_cursos)

    descricao = safe(vaga.get("descricao"))

    return {
        "id": vaga.get("codigoVaga"),
        "titulo": vaga.get("tipoVaga"),
        "empresa": vaga.get("nomeEmpresa"),
        "descricao": descricao,
        "cidade": local.get("cidade"),
        "estado": local.get("uf"),
        "bolsa": vaga.get("bolsaAuxilio"),
        "beneficios": vaga.get("beneficios") or [],
        "pcd": detectar_pcd(descricao),
        "modalidade": detectar_modalidade(descricao),
        "cursos": cursos,
        "url": f"https://ciee.app/detalhes-vaga/{vaga.get('codigoVaga')}",
    }


# ============================================================
# COLETA
# ============================================================

def fetch_vagas():
    """Busca todas as vagas de estágio no CIEE."""
    resp = requests.get(URL, params=PARAMS)
    resp.raise_for_status()
    data = resp.json()
    return data.get("content", [])


def save_json(vagas):
    """Salva o JSON final normalizado."""
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(vagas, f, ensure_ascii=False, indent=4)

    print(f"💾 Arquivo salvo: {OUTPUT_JSON} ({len(vagas)} vagas)")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("🔍 Coletando vagas do CIEE...")

    raw = fetch_vagas()
    print(f"📥 Vagas recebidas: {len(raw)}")

    vagas = [normalize(v) for v in raw]

    save_json(vagas)

    print("✅ Finalizado com sucesso!")
