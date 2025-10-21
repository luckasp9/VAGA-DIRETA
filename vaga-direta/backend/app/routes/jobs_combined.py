from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from app.database import SessionLocal
from app import models
from app.routes.jooble_api import get_vagas_jooble
from app.routes.adzuna_api import get_vagas_adzuna
from app.scrapers.nube_scraper import get_nube_vagas
from app.scrapers.ciee_scraper import get_ciee_vagas

router = APIRouter()

# Cache em memória (dura 6 horas)
CACHE = {"vagas": [], "ultima_atualizacao": None}

# Regras de categorização por curso
curso_keywords = {
    "Administração": ["administração", "gestão", "financeiro", "contabilidade", "empreendedorismo"],
    "TI": ["programação", "desenvolvimento", "software", "sistemas", "informática", "tecnologia", "computação", "backend", "frontend"],
    "Marketing": ["marketing", "publicidade", "propaganda", "comunicação", "vendas", "branding", "mídias sociais"],
    "Recursos Humanos": ["recursos humanos", "rh", "recrutamento", "seleção", "treinamento", "folha de pagamento"],
    "Direito": ["advocacia", "jurídico", "direito", "legislação", "contratos"],
    "Engenharia": ["engenharia", "projetos", "construção", "elétrica", "civil", "produção", "mecânica"],
    "Design": ["design", "ux", "ui", "ilustração", "gráfico", "photoshop", "figma"],
    "Educação": ["ensino", "professor", "pedagogia", "educação", "licenciatura"],
    "Saúde": ["enfermagem", "hospital", "médico", "farmácia", "fisioterapia", "nutrição"]
}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def categorizar_vaga(vaga):
    """Retorna lista de cursos relacionados à vaga"""
    texto = ((vaga.get("job_title") or "") + " " + (vaga.get("job_description") or "")).lower()
    cursos = [curso for curso, kws in curso_keywords.items() if any(kw in texto for kw in kws)]
    return cursos or ["Outros"]


def salvar_vagas_no_banco(vagas, db: Session):
    """Insere as vagas no banco, evitando duplicadas"""
    inseridas = 0
    for v in vagas:
        if not v.get("job_id"):
            continue
        if db.query(models.Vaga).filter_by(job_id=v["job_id"]).first():
            continue

        vaga = models.Vaga(
            job_id=v["job_id"],
            job_title=v.get("job_title"),
            employer_name=v.get("employer_name"),
            job_publisher=v.get("job_publisher"),
            job_country=v.get("job_country", "Brasil"),
            job_employment_type=v.get("job_employment_type"),
            job_city=v.get("job_city"),
            job_state=v.get("job_state"),
            job_description=v.get("job_description"),
            job_apply_link=v.get("job_apply_link"),
            job_salary=v.get("job_salary"),
            job_benefits=v.get("job_benefits")
        )

        try:
            db.add(vaga)
            db.commit()
            db.refresh(vaga)
            inseridas += 1
        except IntegrityError:
            db.rollback()
            continue

        cursos = categorizar_vaga(v)
        for nome_curso in cursos:
            curso = db.query(models.Curso).filter_by(nome=nome_curso).first()
            if not curso:
                curso = models.Curso(nome=nome_curso)
                db.add(curso)
                db.commit()
                db.refresh(curso)

            db.execute(
                f"""
                INSERT INTO tcc.vaga_curso (vaga_id, curso_id)
                VALUES ({vaga.id}, {curso.id})
                ON CONFLICT DO NOTHING;
                """
            )
            db.commit()

    return inseridas


@router.get("/vagas/todas")
def obter_todas_vagas(limit: int = 30, db: Session = Depends(get_db)):
    """
    Coleta vagas de Jooble, Adzuna, Nube e CIEE.
    Salva novas no banco e usa cache de 6 horas.
    """
    agora = datetime.utcnow()
    if CACHE["ultima_atualizacao"] and (agora - CACHE["ultima_atualizacao"]) < timedelta(hours=6):
        print("⚡ Retornando vagas do cache")
        return {
            "cache": True,
            "ultima_atualizacao": CACHE["ultima_atualizacao"],
            "total_vagas": len(CACHE["vagas"]),
            "vagas": CACHE["vagas"]
        }

    fontes = {
        "Jooble": get_vagas_jooble,
        "Adzuna": get_vagas_adzuna,
        "Nube": get_nube_vagas,
        "CIEE": get_ciee_vagas
    }

    vagas_total = []
    erros = {}

    for nome, func in fontes.items():
        try:
            print(f"🔍 Buscando vagas em {nome}...")
            vagas = func(limit=limit)
            print(f"✅ {len(vagas)} vagas de {nome}")
            vagas_total.extend(vagas)
        except Exception as e:
            erros[nome] = str(e)
            print(f"❌ Erro em {nome}: {e}")

    if not vagas_total:
        raise HTTPException(status_code=500, detail="Nenhuma vaga encontrada em nenhuma fonte")

    inseridas = salvar_vagas_no_banco(vagas_total, db)

    CACHE["vagas"] = vagas_total
    CACHE["ultima_atualizacao"] = agora

    return {
        "cache": False,
        "ultima_atualizacao": agora,
        "total_vagas": len(vagas_total),
        "novas_inseridas": inseridas,
        "fontes_com_erro": erros,
        "vagas": vagas_total
    }
