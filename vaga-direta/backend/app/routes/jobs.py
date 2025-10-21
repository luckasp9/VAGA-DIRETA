from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import SessionLocal
from app import models
from app.routes.adzuna_api import fetch_adzuna_vagas
from app.routes.jooble_api import fetch_jooble_vagas

router = APIRouter()

# Dependência para abrir/fechar sessão do banco automaticamente
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/vagas")
def coletar_vagas(db: Session = Depends(get_db)):
    """
    Coleta vagas das APIs Adzuna e Jooble, salva no banco (se não existir),
    e retorna a lista consolidada em formato JSON padronizado.
    """
    inseridas = 0
    vagas_json = []

    try:
        print("🔹 Coletando vagas do Adzuna...")
        adzuna_vagas = fetch_adzuna_vagas()
        vagas_json.extend(adzuna_vagas)
        print(f"✅ Adzuna retornou {len(adzuna_vagas)} vagas.")

        print("🔹 Coletando vagas do Jooble...")
        jooble_vagas = fetch_jooble_vagas()
        vagas_json.extend(jooble_vagas)
        print(f"✅ Jooble retornou {len(jooble_vagas)} vagas.")

    except Exception as e:
        return {"erro": f"Falha ao buscar vagas: {str(e)}"}

    # Inserir no banco de dados (evita duplicatas pelo job_id)
    for v in vagas_json:
        vaga = models.Vaga(
            job_id=v.get("job_id"),
            job_title=v.get("job_title"),
            employer_name=v.get("employer_name"),
            job_description=v.get("job_description"),
            job_city=v.get("job_city"),
            job_state=v.get("job_state"),
            job_country=v.get("job_country"),
            job_employment_type=v.get("job_employment_type"),
            job_apply_link=v.get("job_apply_link"),
            job_salary=v.get("job_salary"),
            job_benefits=v.get("job_benefits")
        )

        try:
            db.add(vaga)
            db.commit()
            inseridas += 1
        except IntegrityError:
            db.rollback()  # Já existe no banco
            continue

    return {
        "total_vagas_coletadas": len(vagas_json),
        "novas_vagas_inseridas": inseridas,
        "fonte": ["Adzuna", "Jooble"]
    }
