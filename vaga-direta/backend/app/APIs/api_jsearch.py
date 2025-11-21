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
    """Busca vagas completas da API JSearch sem filtrar nada."""

    params = {
        "query": f"{query} Brazil",
        "num_pages": paginas
    }

    response = requests.get(BASE_URL, headers=HEADERS, params=params)
    response.raise_for_status()

    # 🔥 retorno cru, do jeitinho que vem da API
    return response.json()
