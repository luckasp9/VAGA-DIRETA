from fastapi import APIRouter, Depends, HTTPException
import requests
import os
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import crud
import http.client

conn = http.client.HTTPSConnection("jsearch.p.rapidapi.com")



router = APIRouter()

# API key oficial da JSearch (https://www.jsearch.io)
JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY")
JSEARCH_URL = "https://api.jsearch.io/v1/jobs"

# Dependency para a sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/linkedin-jobs")
def linkedin_jobs(query: str, page: int = 1, db: Session = Depends(get_db)):
    if not JSEARCH_API_KEY:
        raise HTTPException(status_code=500, detail="JSEARCH_API_KEY não definida no ambiente")

    headers = {
    "X-RapidAPI-Key": "8b1729c6f7msh0e6d7f53f626049p1277c8jsn21e2e8f33de1",
    "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
}

    params = {
        "query": query,
        "page": page,
        "num_pages": 1,
        "country": "br",    # Filtra Brasil
        "language": "pt"    # Filtra português
    }

    try:
        response = requests.get(JSEARCH_URL, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar a API JSearch: {e}")
    except ValueError:
        raise HTTPException(status_code=500, detail="Resposta inválida da API JSearch (não JSON)")

    conn.request("GET", "/search?query=developer%20jobs%20in%20chicago&page=1&num_pages=1&country=us&date_posted=all", headers=headers)

    res = conn.getresponse()
    data = res.read()
    
    jobs_saved = []
    for job in data.get("data", []):
        job_data = {
            "title": job.get("job_title"),
            "company": job.get("employer_name"),
            "location": job.get("job_city"),
            "description": job.get("job_description"),
            "url": job.get("job_apply_link")
        }

        # Evita duplicatas
        if job_data["url"] and not crud.get_job_by_url(db, job_data["url"]):
            crud.create_job(db, job_data)
            jobs_saved.append(job_data)




    # Retornar dados do banco
    stored_jobs = crud.get_jobs(db, skip=(page-1)*10, limit=10)
    return {
        "jobs": [
            dict(
                title=j.title,
                company=j.company,
                location=j.location,
                description=j.description,
                url=j.url
            ) for j in stored_jobs
        ],
        "saved_jobs_count": len(jobs_saved)
    }
