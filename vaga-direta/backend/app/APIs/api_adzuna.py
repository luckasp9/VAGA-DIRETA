import os
import requests
from dotenv import load_dotenv

load_dotenv()

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

BASE_URL = "https://api.adzuna.com/v1/api/jobs/br/search/{page}"


def buscar_vagas_adzuna(query: str, page: int = 1, results: int = 50):
    """
    Retorna o JSON COMPLETO do Adzuna sem filtrar nada.
    """

    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        raise RuntimeError("ADZUNA_APP_ID ou ADZUNA_APP_KEY não configurados")

    url = BASE_URL.format(page=page)

    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": results,
        "what": query,
        "content-type": "application/json",
    }

    resp = requests.get(url, params=params)
    resp.raise_for_status()

    return resp.json()
