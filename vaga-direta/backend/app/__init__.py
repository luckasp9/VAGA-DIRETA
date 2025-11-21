import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("JSEARCH_API_KEY")

BASE_URL = "https://jsearch.p.rapidapi.com/search"

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "jsearch.p.rapidapi.com"
}


def buscar_vagas_jsearch(query: str = "estágio", paginas: int = 1):
    params = {
        "query": f"{query} Brazil",
        "num_pages": paginas
    }

    resp = requests.get(BASE_URL, headers=HEADERS, params=params)
    resp.raise_for_status()
    data = resp.json()

    vagas = []

    for item in data.get("data", []):
        vagas.append({
            "titulo": item.get("job_title"),
            "empresa": item.get("employer_name"),
            "cidade": item.get("job_city"),
            "descricao": item.get("job_description"),
            "link": item.get("job_apply_link"),
            "salario": item.get("job_min_salary"),
            "publicado_em": item.get("job_posted_at")
        })

    return vagas
