#!/usr/bin/env python3
# catho_scraper.py — versão ajustada com curso, pcd, modalidade, normalização padronizada

import os
import sys
import re
import requests
import json
import time
import argparse
from typing import List, Dict, Any, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# -----------------------------------------------------------
# Ajuste do PATH — permite importar utils.detectar_cursos
# -----------------------------------------------------------
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(ROOT)

from app.utils.detectar_cursos import detectar_cursos  # <-- AGORA FUNCIONA


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.path.join(BASE_DIR, "vagas_catho.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://www.catho.com.br/vagas/estagio"
}

TOTAL_PAGES = 3


# -------------------------
# HTTP session com retry
# -------------------------
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


# -------------------------
# Extrair buildId
# -------------------------
def extract_buildid_from_html_text(html: str) -> Optional[str]:
    patterns = [
        r"/_next/static/([A-Za-z0-9_-]+)/_buildManifest\.js",
        r"/_next/data/([A-Za-z0-9_-]+)/estagio\.json",
        r"buildId\"?:\s*\"([A-Za-z0-9_-]+)\""
    ]
    for pat in patterns:
        m = re.search(pat, html)
        if m:
            return m.group(1)
    return None


def get_build_id_from_network(session: requests.Session) -> str:
    url = "https://www.catho.com.br/vagas/estagio"
    print("🔎 Buscando buildId na página:", url)
    r = session.get(url, timeout=20)
    r.raise_for_status()
    html = r.text
    bid = extract_buildid_from_html_text(html)
    if not bid:
        raise RuntimeError("Não encontrei buildId no HTML.")
    print("✅ buildId encontrado:", bid)
    return bid


# -------------------------
# Buscar pagina Next/Data
# -------------------------
def fetch_page(session: requests.Session, build_id: str, page: int):
    url = f"https://www.catho.com.br/vagas/_next/data/{build_id}/estagio.json?page={page}&slug=estagio"
    r = session.get(url, timeout=30)
    r.raise_for_status()
    return r.json()


# -------------------------
# Normalização padronizada (Catho)
# -------------------------
def normalize_job(job_item: Dict[str, Any]) -> Dict[str, Any]:
    # Foco na estrutura da Catho
    jd = job_item.get("job_customized_data") or job_item.get("jobCustomizedData") or {}
    job_id = jd.get("id") or job_item.get("job_id") or ""

    # Local
    cidade = ""
    estado = ""
    vagas_loc = jd.get("vagas") or []
    if isinstance(vagas_loc, list) and vagas_loc and isinstance(vagas_loc[0], dict):
        cidade = vagas_loc[0].get("cidade", "") or ""
        estado = vagas_loc[0].get("uf", "") or vagas_loc[0].get("estado", "") or ""

    # Bolsa
    salario = jd.get("salario")
    bolsa_valor = salario if salario not in (None, 0) else "A combinar"

    beneficios = jd.get("benef") or []

    empresa = (jd.get("anunciante") or {}).get("nome") or \
              (jd.get("contratante") or {}).get("nome") or ""

    descricao = jd.get("descricao", "") or ""
    titulo = jd.get("titulo", "") or f"Vaga {job_id}"

    # URL final
    url = f"https://www.catho.com.br/vagas/{titulo.replace(' ', '-').lower()}/{job_id}"

    # -------------------------
    # Modalidade (melhorada)
    # -------------------------
    modalidade = ""
    txt = f"{titulo} {descricao} {json.dumps(jd).lower()}"

    remoto_keywords = [
        "home office", "home-office", "remoto", "remota",
        "teletrabalho", "totalmente remoto", "100% remoto"
    ]

    hibrido_keywords = [
        "híbrido", "hibrido", "modelo híbrido", "modelo hibrido"
    ]

    # ordem importa — híbrido antes de remoto/presencial
    if any(k in txt for k in hibrido_keywords):
        modalidade = "Híbrido"
    elif any(k in txt for k in remoto_keywords):
        modalidade = "Remoto"
    else:
        modalidade = "Presencial"

    # PCD — Catho raramente envia, mas tentamos identificar
    pcd = False
    if "pcd" in titulo.lower() or "pcd" in descricao.lower():
        pcd = True

    # Cursos (detectar dentro de título + descrição)
    cursos_texto = f"{titulo}"
    cursos = detectar_cursos(cursos_texto)

    return {
        "id": str(job_id),
        "titulo": titulo,
        "descricao": descricao,
        "empresa_nome": empresa,
        "cidade": cidade,
        "estado": estado,
        "salario": bolsa_valor,
        "beneficios": beneficios,
        "url": url,
        "pcd": pcd,
        "modalidade": modalidade,
        "cursos": cursos,
    }


# -------------------------
# Fluxo principal
# -------------------------
def scrape_catho(pages=549, delay=0.3, test_json=None, test_html=None, out_file=DEFAULT_OUT):
    session = make_session()
    results = []

    # modo teste com json local
    if test_json:
        print("🧪 Test JSON:", test_json)
        with open(test_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        jobs = data.get("pageProps", {}).get("jobSearch", {}).get("jobSearchResult", {}).get("data", {}).get("jobs", [])
        for j in jobs:
            results.append(normalize_job(j))
        return results

    # buildId
    if test_html:
        print("🧪 Test HTML (ignorado aqui)")
        raise NotImplementedError()

    build_id = get_build_id_from_network(session)
    print(f"🚀 Iniciando scraping — {pages} páginas, delay={delay}s")

    for p in range(1, pages + 1):
        try:
            data = fetch_page(session, build_id, p)
        except Exception as e:
            print(f"❌ Erro página {p}: {e}")
            time.sleep(delay)
            continue

        jobs = data.get("pageProps", {}).get("jobSearch", {}).get("jobSearchResult", {}).get("data", {}).get("jobs", [])
        if not jobs:
            print(f"⚠ Página {p} sem jobs — encerrando.")
            break

        print(f"📄 Página {p}: {len(jobs)} vagas")

        for job_item in jobs:
            results.append(normalize_job(job_item))

        time.sleep(delay)

    # salvar
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print(f"✅ Salvo {len(results)} vagas em {out_file}")
    return results


# -------------------------
# CLI
# -------------------------
def main():
    parser = argparse.ArgumentParser(description="Scraper Catho")
    parser.add_argument("--pages", "-p", type=int, default=TOTAL_PAGES)
    parser.add_argument("--delay", "-d", type=float, default=0.3)
    parser.add_argument("--out", "-o", type=str, default=DEFAULT_OUT)
    args = parser.parse_args()

    scrape_catho(pages=args.pages, delay=args.delay, out_file=args.out)


if __name__ == "__main__":
    main()
