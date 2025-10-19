from fastapi import APIRouter, HTTPException
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # carrega as variáveis do .env

router = APIRouter()

JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY")
JSEARCH_URL = "https://jsearch.p.rapidapi.com/search"

@router.get("/vagas")
def get_vagas(query: str = "estagio", page: int = 1):
    headers = {
        "x-rapidapi-key": JSEARCH_API_KEY,
        "x-rapidapi-host": "jsearch.p.rapidapi.com"
    }

    params = {
        "query": query,
        "page": page,
        "num_pages": 1,
        "country": "br",
        "date_posted": "all"
    }

    try:
        response = requests.get(JSEARCH_URL, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))
