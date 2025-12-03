#!/usr/bin/env python3
# backend/app/scrapers/empregare_scraper.py

import json
import requests
import os
import sys
from typing import Optional, List, Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ---------------------------
# PATH FIX (garante import utils/)
# ---------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))        # .../app/scrapers
APP_DIR = os.path.dirname(CURRENT_DIR)                         # .../app
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

# importa mapa de cursos
try:
    from utils.curso_map import CURSO_MAP
    from utils.detectar_cursos import detectar_cursos
except Exception as e:
    CURSO_MAP = {"__default__": "Outros"}
    print(" Aviso: não encontrou utils. Usando fallback. Erro:", e)

# ---------------------------
# SALVAR EM /data
# ---------------------------
DATA_DIR = os.path.join(CURRENT_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

OUT_FILE = os.path.join(DATA_DIR, "vagas_empregare.json")
DEBUG_FILE = os.path.join(DATA_DIR, "empregare_debug.json")

# ---------------------------
# CONFIG
# ---------------------------
BASE_URL = "https://www.empregare.com/api/pt-br/vagas/buscar-novo"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.empregare.com/vagas",
    "Origin": "https://www.empregare.com",
    "X-Requested-With": "XMLHttpRequest"
}


# ---------------------------
# session com retry
# ---------------------------
def make_session(retries: int = 3, backoff: float = 0.3) -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=frozenset(["GET"])
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update(HEADERS)
    return session


# ---------------------------
# modalidade
# ---------------------------
def detect_modalidade(vaga: Dict[str, Any]) -> str:
    remoto = (vaga.get("trabalhoRemoto") or "").lower()
    cidades = vaga.get("cidades") or []
    txt = " ".join([
        str(vaga.get("titulo", "")),
        str(vaga.get("chamada", "")),
        str(vaga.get("trabalhoRemotoTexto", ""))
    ]).lower()

    hibrido_kw = ["híbrido", "hibrido", "modelo híbrido", "modelo hibrido"]
    remoto_kw = ["home office", "home-office", "remoto", "remota", "teletrabalho"]
    presencial_kw = ["presencial", "no local", "no escritório"]

    if any(k in txt for k in hibrido_kw) or remoto in ["hibrido", "parcialmente_remoto"]:
        return "Híbrido"
    if any(k in txt for k in remoto_kw) or (cidades and isinstance(cidades[0], str) and "remoto" in cidades[0].lower()):
        return "Remoto"
    if any(k in txt for k in presencial_kw):
        return "Presencial"

    if remoto in ["totalmenteremoto", "true", "remoto"]:
        return "Remoto"

    return "Presencial"


# ---------------------------
# extrair cidade/estado
# ---------------------------
def extract_city_state(vaga: Dict[str, Any]) -> (str, str):
    cidades = vaga.get("cidades")

    if not cidades:
        return "", ""

    loc = cidades[0] if isinstance(cidades, list) else cidades

    if isinstance(loc, dict):
        loc = loc.get("descricao") or loc.get("nome") or ""

    if not isinstance(loc, str):
        return "", ""

    loc = loc.strip()

    # remoto
    if "remoto" in loc.lower():
        return "Remoto", "Remoto"

    # formato "Cidade, UF, BR"
    if "," in loc:
        partes = [p.strip() for p in loc.split(",")]

        if len(partes) >= 2:
            cidade = partes[0]
            estado = partes[1]
            return cidade, estado

    # formato "Cidade - UF"
    cleaned = loc.replace(" / ", "-").replace("/", "-")
    if "-" in cleaned:
        parts = [p.strip() for p in cleaned.split("-") if p.strip()]
        if len(parts) >= 2:
            return parts[0], parts[1]

    return loc, ""


# ---------------------------
# normalize
# ---------------------------
def normalize(v: Dict[str, Any]) -> Dict[str, Any]:
    cidade, estado = extract_city_state(v)
    modalidade = detect_modalidade(v)

    texto_curso = " ".join([
        v.get("titulo", ""),
    ])

    cursos = detectar_cursos(texto_curso)

    return {
        "id": v.get("id"),
        "titulo": v.get("titulo") or "",
        "empresa": v.get("empresa") or "",
        "descricao": (v.get("chamada") or "").strip() + "...",
        "cidade": cidade,
        "estado": estado,
        "bolsa": v.get("salario") or "",
        "beneficios": [],
        "logo": v.get("logoThumb") or "",
        "pcd": bool(v.get("pcd")),
        "modalidade": modalidade,
        "cursos": cursos,
        "url": f"https://www.empregare.com/{v.get('url') or ''}",
    }


# ---------------------------
# fetch vagas
# ---------------------------
def buscar_vagas_empregare(session: requests.Session, pagina: int = 1, itens: int = 9999, nivel: str = "Estágio") -> Dict[str, Any]:
    params = {"pagina": pagina, "itensPagina": itens, "nivel": nivel}
    r = session.get(BASE_URL, params=params, timeout=20)
    r.raise_for_status()
    return r.json()


# ---------------------------
# múltiplas estruturas possíveis
# ---------------------------
def extract_vagas_from_response(data: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    candidates = [
        lambda d: d.get("data", {}).get("vagas"),
        lambda d: d.get("vagas"),
        lambda d: d.get("dados"),
        lambda d: d.get("dados", {}).get("vagas"),
        lambda d: d.get("model", {}).get("dados"),
        lambda d: d.get("result", {}).get("vagas")
    ]
    for c in candidates:
        try:
            val = c(data)
        except Exception:
            val = None

        if isinstance(val, list):
            return val

        if isinstance(val, dict):
            if all(isinstance(v, dict) for v in val.values()):
                return list(val.values())

    return None


# ---------------------------
# salvar debug
# ---------------------------
def save_debug(data: Any):
    try:
        with open(DEBUG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f" Debug salvo em {DEBUG_FILE}")
    except:
        pass


# ---------------------------
# MAIN
# ---------------------------
def main():
    print(" Buscando vagas Empregare…")
    session = make_session()

    try:
        data = buscar_vagas_empregare(session)
    except Exception as e:
        print(" Erro na requisição:", e)
        with open(OUT_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False)
        return

    if not isinstance(data, dict):
        print(" Resposta inesperada. Salvando debug.")
        save_debug(data)
        with open(OUT_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False)
        return

    vagas_raw = extract_vagas_from_response(data)

    if not vagas_raw:
        print(" Nenhuma vaga encontrada. Salvando debug.")
        save_debug(data)
        with open(OUT_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False)
        return

    print(f" Vagas encontradas: {len(vagas_raw)} — normalizando...")

    vagas = [normalize(v) for v in vagas_raw]

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(vagas, f, ensure_ascii=False, indent=2)

    print(f" Arquivo salvo em: {OUT_FILE} ({len(vagas)} vagas)")


if __name__ == "__main__":
    main()
