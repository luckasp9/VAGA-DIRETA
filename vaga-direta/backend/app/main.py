from fastapi import FastAPI
from app import models
from app.database import engine
from fastapi import FastAPI
from app.routes import jobs 
from app.routes import teste2
from app.routes import jobs_combined

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Plataforma de Vagas de Estágio")

app.include_router(jobs.router, prefix="/api", tags=["Vagas"])
app.include_router(teste2.router, prefix="/api", tags=["Vagas"])
app.include_router(jobs_combined.router, prefix="/api", tags=["Vagas"])