from fastapi import FastAPI
from app.APIs.rotas.vagas_router import router as vagas_router

app = FastAPI()

app.include_router(vagas_router)
