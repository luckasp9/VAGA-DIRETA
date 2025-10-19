
from sqlalchemy.orm import Session
from app import models

def get_job_by_url(db: Session, url: str):
    return db.query(models.Job).filter(models.Job.url == url).first()

def create_job(db: Session, job_data: dict):
    job = models.Job(**job_data)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def get_jobs(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Job).offset(skip).limit(limit).all()
