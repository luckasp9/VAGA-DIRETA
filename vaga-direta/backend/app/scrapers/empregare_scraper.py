import json
import requests
import os
from utils.curso_map import CURSO_MAP


BASE_URL = "https://www.empregare.com/api/pt-br/vagas/buscar-novo"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.empregare.com/vagas",
    "Origin": "https://www.empregare.com",
    "X-Requested-With": "XMLHttpRequest"
}

OUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vagas_empregare.json")


# ==========================================================
# Curso via dicionário
# ==========================================================
def detect_curso(texto: str) -> str:
    if not texto:
        return CURSO_MAP["__default__"]

    txt = texto.lower()

    for key, curso in CURSO_MAP.items():
        if key != "__default__" and key in txt:
            return curso

    return CURSO_MAP["__default__"]


# ==========================================================
# Modalidade → remoto / presencial / híbrido
# ==========================================================
def detect_modalidade(vaga):
    remoto = (vaga.get("trabalhoRemoto") or "").lower()
    cidade = vaga.get("cidades") or []

    if remoto in ["totalmenteremoto", "true", "remoto"]:
        return "remoto"

    if remoto in ["hibrido", "parcialmente_remoto", "parcial"]:
        return "hibrido"

    if cidade and "remoto" in cidade[0].lower():
        return "remoto"

    return "presencial"


# ==========================================================
# Extrair cidade e estado
# ==========================================================
def extract_city_state(vaga):
    cidades = vaga.get("cidades")

    if not cidades or not isinstance(cidades, list):
        return "", ""

    # Exemplo de retorno:
    # ["Brasília - DF"]  ou  ["São Paulo / SP"] ou ["Totalmente Remoto"]
    loc = cidades[0]

    if "remoto" in loc.lower():
        return "Remoto", ""

    # Normalização comum: "Brasília - DF" ou "São Paulo/SP"
    cleaned = loc.replace(" / ", "-").replace("/", "-")

    if "-" in cleaned:
        partes = cleaned.split("-")
        cidade = partes[0].strip()
        estado = partes[-1].strip()
        return cidade, estado

    return cleaned, ""


# ==========================================================
# Normalizador padrão
# ==========================================================
def normalize(v):
    cidade, estado = extract_city_state(v)
    modalidade = detect_modalidade(v)
    curso = detect_curso(v.get("titulo") or v.get("chamada") or "")

    return {
        "id": v.get("id"),
        "url": f"https://www.empregare.com/{v.get('url')}",
        "titulo": v.get("titulo") or "",
        "empresa": v.get("empresa") or "",
        "descricao": v.get("chamada") or "",
        "cidade": cidade,
        "estado": estado,
        "bolsa_valor": v.get("salario") or "",
        "beneficio": [],  # empregare não fornece
        "logo": v.get("logoThumb") or "",
        "curso": curso,
        "modalidade": modalidade,
        "pcd": bool(v.get("pcd"))
    }


# ==========================================================
# Buscar vagas bruto
# ==========================================================
def buscar_vagas_empregare(pagina: int = 1, itens: int = 9999, nivel: str = "Estágio"):
    params = {
        "pagina": pagina,
        "itensPagina": itens,
        "nivel": nivel
    }

    resp = requests.get(BASE_URL, headers=HEADERS, params=params)
    resp.raise_for_status()
    return resp.json()


# ==========================================================
# Salvar normalizado
# ==========================================================
def salvar_vagas_json():
    print("🔎 Buscando vagas Empregare…")

    data = buscar_vagas_empregare()
    vagas_raw = data.get("vagas", []) or data

    vagas = [normalize(v) for v in vagas_raw]

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(vagas, f, ensure_ascii=False, indent=4)

    print(f"✔ Arquivo salvo: {OUT_FILE} ({len(vagas)} vagas)")


if __name__ == "__main__":
    salvar_vagas_json()
