import os
import requests
from dotenv import load_dotenv

load_dotenv()

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

ADZUNA_URL = "https://api.adzuna.com/v1/api/jobs/br/search/1"

def fetch_adzuna_vagas():
    """
    Busca vagas de estágio no Adzuna e retorna em formato padronizado.
    """
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": 50,
        "what": "estágio",
        "content-type": "application/json"
    }

    response = requests.get(ADZUNA_URL, params=params)
    if response.status_code != 200:
        raise Exception(f"Erro na API Adzuna: {response.status_code} - {response.text}")

    data = response.json()
    vagas_formatadas = []

    for v in data.get("results", []):
        vaga = {
            "job_id": f"adzuna_{v.get('id')}",
            "job_title": v.get("title"),
            "employer_name": v.get("company", {}).get("display_name"),
            "job_description": v.get("description"),
            "job_city": v.get("location", {}).get("area", ["", ""])[-1],
            "job_state": v.get("location", {}).get("area", ["", ""])[-2] if len(v.get("location", {}).get("area", [])) > 1 else None,
            "job_country": "BR",
            "job_employment_type": v.get("contract_type") or "Não informado",
            "job_apply_link": v.get("redirect_url"),
            "job_salary": f"R$ {v.get('salary_min', 0):,.2f} - R$ {v.get('salary_max', 0):,.2f}" if v.get("salary_min") else None,
            "job_benefits": None  # Adzuna geralmente não traz benefícios
        }
        vagas_formatadas.append(vaga)

    return vagas_formatadas
