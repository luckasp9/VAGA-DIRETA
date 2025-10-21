import os
import requests
from dotenv import load_dotenv

load_dotenv()

JOOBLE_API_KEY = os.getenv("JOOBLE_API_KEY")
JOOBLE_URL = f"https://jooble.org/api/{JOOBLE_API_KEY}"

def fetch_jooble_vagas():
    """
    Busca vagas de estágio no Jooble e retorna no formato padronizado.
    """
    body = {
        "keywords": "estágio",
        "location": "Brasil",
        "page": 1
    }

    response = requests.get(JOOBLE_URL, json=body)
    if response.status_code != 200:
        raise Exception(f"Erro na API Jooble: {response.status_code} - {response.text}")

    data = response.json()
    vagas_formatadas = []

    for v in data.get("jobs", []):
        vaga = {
            "job_id": f"jooble_{v.get('id') or hash(v.get('link'))}",
            "job_title": v.get("title"),
            "employer_name": v.get("company"),
            "job_description": v.get("snippet"),
            "job_city": v.get("location"),
            "job_state": None,
            "job_country": "BR",
            "job_employment_type": v.get("type") or "Não informado",
            "job_apply_link": v.get("link"),
            "job_salary": v.get("salary"),
            "job_benefits": v.get("benefits")
        }
        vagas_formatadas.append(vaga)

    return vagas_formatadas
