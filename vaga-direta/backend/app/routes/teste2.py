from fastapi import APIRouter, HTTPException
import requests
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import SessionLocal
from app.models import Vaga  # seu model SQLAlchemy

load_dotenv()  # carrega variáveis do .env

router = APIRouter()

JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY")
JSEARCH_URL = "https://jsearch.p.rapidapi.com/search"

@router.get("/vagas/teste")
def get_vagas(query: str = "estagio", page: int = 4):
    headers = {
        "x-rapidapi-key": JSEARCH_API_KEY,
        "x-rapidapi-host": "jsearch.p.rapidapi.com"
    }

    params = {
        "query": query,
        "page": page,
        "num_pages": 10,
        "country": "br",
        "date_posted": "all",
        "job_employment_type": "Estágio",
    }

    try:
        response = requests.get(JSEARCH_URL, headers=headers, params=params)
        response.raise_for_status()
        vagas_json = response.json().get("data", [])

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Inserir no banco
    session: Session = SessionLocal()
    inseridas = 0

    for vaga_data in vagas_json:
        # Evita duplicata pelo job_id
        if session.query(Vaga).filter_by(job_id=vaga_data.get("job_id")).first():
            continue

        vaga = Vaga(
            job_id=vaga_data.get("job_id"),
            job_title=vaga_data.get("job_title"),
            employer_name=vaga_data.get("employer_name"),
            employer_logo=vaga_data.get("employer_logo"),
            employer_website=vaga_data.get("employer_website"),
            job_publisher=vaga_data.get("job_publisher"),
            job_employment_type=vaga_data.get("job_employment_type"),
            job_employment_types=vaga_data.get("job_employment_types"),
            job_apply_link=vaga_data.get("job_apply_link"),
            job_apply_is_direct=vaga_data.get("job_apply_is_direct"),
            job_description=vaga_data.get("job_description"),
            job_is_remote=vaga_data.get("job_is_remote"),
            job_posted_at=vaga_data.get("job_posted_at"),
            job_location=vaga_data.get("job_location"),
            job_city=vaga_data.get("job_city"),
            job_state=vaga_data.get("job_state"),
            job_country=vaga_data.get("job_country"),
            job_latitude=vaga_data.get("job_latitude"),
            job_longitude=vaga_data.get("job_longitude"),
            job_google_link=vaga_data.get("job_google_link"),
            job_salary=vaga_data.get("job_salary"),
            job_min_salary=vaga_data.get("job_min_salary"),
            job_max_salary=vaga_data.get("job_max_salary"),
            job_salary_period=vaga_data.get("job_salary_period"),
            job_onet_soc=vaga_data.get("job_onet_soc"),
            job_onet_job_zone=vaga_data.get("job_onet_job_zone")
        )
        session.add(vaga)
        try:
            session.commit()
            inseridas += 1
        except IntegrityError:
            session.rollback()  # ignora duplicata
        except Exception:
            session.rollback()

    session.close()

    return {
        "message": f"{inseridas} novas vagas inseridas",
        "vagas": vagas_json
    }
