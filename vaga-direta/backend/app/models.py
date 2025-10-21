from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base 

class Vaga(Base):
    __tablename__ = "vaga"
    __table_args__ = {"schema": "tcc"}

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True)
    job_title = Column(String)
    employer_name = Column(String)
    job_description = Column(Text)
    job_city = Column(String)
    job_state = Column(String)
    job_country = Column(String)
    job_employment_type = Column(String)
    job_apply_link = Column(Text)
    job_salary = Column(String, nullable=True)
    job_benefits = Column(Text, nullable=True)

class Curso(Base):
    __tablename__ = "curso"
    __table_args__ = {"schema": "tcc"}

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True)