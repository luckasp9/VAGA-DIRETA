import requests
import os

SERPER_API_KEY = "a614fa3f71204a6b070d7be32e0f3954d7082e11"

BASE_URL = "https://google.serper.dev/jobs"


def buscar_vagas_linkedin(query: str, location: str = "Brazil"):
    """
    Busca vagas do LinkedIn via Serper.dev Jobs API.
    O resultado inclui vagas do LinkedIn + Glassdoor + ZipRecruiter + Indeed.
    """

    payload = {
        "q": f"{query} {location}",
        "location": location
    }

    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(BASE_URL, json=payload, headers=headers)

    if response.status_code != 200:
        return {
            "status": "error",
            "status_code": response.status_code,
            "response": response.text
        }

    data = response.json()

    # Serper retorna vagas em "jobs"
    return data.get("jobs", [])
