#!/usr/bin/env python3
# catho_scraper.py
# Scraper Catho (estágio) — automático, robusto e pronto para 549 páginas
# Uso principal: python catho_scraper.py --pages 549 --delay 0.3
# Teste com JSON salvo: python catho_scraper.py --test-json /path/to/response.json
# Teste extraindo buildId de HTML salvo: python catho_scraper.py --test-html /path/to/page.html

import re
import requests
import json
import time
import os
import argparse
from typing import List, Dict, Any, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUT = os.path.join(BASE_DIR, "vagas_catho.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://www.catho.com.br/vagas/estagio"
}

TOTAL_PAGES = 3  # conforme informado


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
        allowed_methods=frozenset(["GET", "POST"])
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update(HEADERS)
    return session


# -------------------------
# Extrair buildId do HTML (ou de arquivo local)
# -------------------------
def extract_buildid_from_html_text(html: str) -> Optional[str]:
    # tentativa 1: padrão _next/static/{buildId}/_buildManifest.js
    m = re.search(r"/_next/static/([A-Za-z0-9_-]+)/_buildManifest\.js", html)
    if m:
        return m.group(1)

    # tentativa 2: padrão /_next/data/{buildId}/estagio.json
    m = re.search(r"/_next/data/([A-Za-z0-9_-]+)/estagio\.json", html)
    if m:
        return m.group(1)

    # tentativa 3: buildId em scripts (outro possível formato)
    m = re.search(r"buildId\"?:\s*\"([A-Za-z0-9_-]+)\"", html)
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
        raise RuntimeError("Não encontrei buildId no HTML da página (regex falhou).")
    print("✅ buildId encontrado:", bid)
    return bid


def get_build_id_from_file(path: str) -> str:
    # tenta abrir arquivo como texto (html). Se for PDF, não vai funcionar sem conversão.
    if not os.path.exists(path):
        raise FileNotFoundError(f"Arquivo de teste não encontrado: {path}")
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()
    bid = extract_buildid_from_html_text(html)
    if not bid:
        raise RuntimeError("Não encontrei buildId no arquivo de teste (regex falhou).")
    print("✅ buildId extraído do arquivo de teste:", bid)
    return bid


# -------------------------
# Buscar página JSON no Next data
# -------------------------
def fetch_page(session: requests.Session, build_id: str, page: int) -> Dict[str, Any]:
    url = f"https://www.catho.com.br/vagas/_next/data/{build_id}/estagio.json?page={page}&slug=estagio"
    r = session.get(url, timeout=30)
    r.raise_for_status()
    return r.json()


# -------------------------
# Normalização (Catho -> formato unificado)
# -------------------------
def normalize_job(job_item: Dict[str, Any]) -> Dict[str, Any]:
    # job_item dentro de jobs -> possui job_customized_data
    jd = job_item.get("job_customized_data") or job_item.get("jobCustomizedData") or {}
    job_id = jd.get("id") or job_item.get("job_id") or ""

    cidade = ""
    estado = ""
    vagas_loc = jd.get("vagas") or []
    if isinstance(vagas_loc, list) and len(vagas_loc) > 0 and isinstance(vagas_loc[0], dict):
        cidade = vagas_loc[0].get("cidade", "") or ""
        estado = vagas_loc[0].get("uf", "") or vagas_loc[0].get("estado", "") or ""

    salario = jd.get("salario")
    faixa = jd.get("faixaSalarial") or ""
    if salario is None or salario == 0:
        bolsa_valor = faixa
    else:
        bolsa_valor = salario

    beneficios = jd.get("benef") or []
    empresa = (jd.get("anunciante") or {}).get("nome") or (jd.get("contratante") or {}).get("nome") or ""
    curso = (jd.get("ppdInfo") or {}).get("curso") or ""

    descricao = jd.get("descricao", "") or ""
    titulo = jd.get("titulo", "") or job_item.get("job_id", "")

    return {
        "id": job_id,
        "url": f"https://www.catho.com.br/vagas/{job_id}",
        "titulo": titulo,
        "bolsa_valor": bolsa_valor,
        "cidade": cidade,
        "estado": estado,
        "beneficio": beneficios,
        "logo": "",
        "empresa": empresa,
        "descricao": descricao,
        "curso": curso or ""
    }


# -------------------------
# Fluxo principal de scraping
# -------------------------
def scrape_catho(pages: int = 549, delay: float = 0.3, test_json: Optional[str] = None,
                 test_html: Optional[str] = None, out_file: str = DEFAULT_OUT) -> List[Dict[str, Any]]:
    session = make_session()
    results: List[Dict[str, Any]] = []

    if test_json:
        # ler JSON local (formato Next data)
        print("🔁 Modo TEST JSON — carregando arquivo:", test_json)
        with open(test_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        jobs = data.get("pageProps", {}).get("jobSearch", {}).get("jobSearchResult", {}).get("data", {}).get("jobs", [])
        print(f"🔍 Jobs lidos do arquivo de teste: {len(jobs)}")
        for job in jobs:
            results.append(normalize_job(job))
        return results

    # se fornecido test_html, extrai o buildId do arquivo (útil para debugging offline)
    if test_html:
        print("🔁 Modo TEST HTML — extraindo buildId de arquivo:", test_html)
        build_id = get_build_id_from_file(test_html)
    else:
        build_id = get_build_id_from_network(session)

    print(f"🚀 Iniciando coleta: pages={pages}, delay={delay}s, build_id={build_id}")

    for p in range(1, pages + 1):
        try:
            data = fetch_page(session, build_id, p)
        except Exception as e:
            print(f"❌ Erro ao buscar página {p}: {e} — pulando e continuando")
            time.sleep(delay)
            continue

        jobs = data.get("pageProps", {}).get("jobSearch", {}).get("jobSearchResult", {}).get("data", {}).get("jobs", [])

        if not isinstance(jobs, list) or len(jobs) == 0:
            print(f"⚠️ Página {p} retornou 0 jobs — interrompendo varredura.")
            break

        print(f"📄 Página {p}: {len(jobs)} vagas brutas")
        for job_item in jobs:
            normalized = normalize_job(job_item)
            results.append(normalized)

        time.sleep(delay)

    # salvar arquivo
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

    print(f"✅ Salvo {len(results)} vagas em: {out_file}")
    return results


# -------------------------
# CLI
# -------------------------
def main():
    parser = argparse.ArgumentParser(description="Scraper Catho (estágio) — coleta e normaliza vagas")
    parser.add_argument("--pages", "-p", type=int, default=TOTAL_PAGES, help="Páginas a puxar (default 549)")
    parser.add_argument("--delay", "-d", type=float, default=0.3, help="Delay entre requisições (segundos)")
    parser.add_argument("--test-json", type=str, default="", help="Arquivo JSON local para teste (ex: /mnt/data/response.json)")
    parser.add_argument("--test-html", type=str, default="", help="Arquivo HTML local para extrair buildId (ex: /mnt/data/page.html)")
    parser.add_argument("--out", "-o", type=str, default=DEFAULT_OUT, help="Arquivo de saída JSON")
    args = parser.parse_args()

    test_json = args.test_json or None
    test_html = args.test_html or None

    print(f"▶️ Inicializando Catho scraper — pages={args.pages}, delay={args.delay}, test_json={test_json}, test_html={test_html}")
    scrape_catho(pages=args.pages, delay=args.delay, test_json=test_json, test_html=test_html, out_file=args.out)


if __name__ == "__main__":
    main()
