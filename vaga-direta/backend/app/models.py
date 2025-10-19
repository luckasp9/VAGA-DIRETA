from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ARRAY
from sqlalchemy.sql import func
from app.database import Base  # ou declarative_base()

class Vaga(Base):
    __tablename__ = "vaga"
    __table_args__ = {"schema": "tcc"}

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, nullable=False)
    job_title = Column(Text)
    employer_name = Column(Text)
    employer_logo = Column(Text)
    employer_website = Column(Text)
    job_publisher = Column(Text)
    job_employment_type = Column(Text)
    job_employment_types = Column(ARRAY(String))
    job_apply_link = Column(Text)
    job_apply_is_direct = Column(Boolean)
    job_description = Column(Text)
    job_is_remote = Column(Boolean)
    job_posted_at = Column(Text)
    job_posted_at_timestamp = Column(DateTime, nullable=True)
    job_posted_at_datetime_utc = Column(DateTime, nullable=True)
    job_location = Column(Text)
    job_city = Column(Text)
    job_state = Column(Text)
    job_country = Column(Text)
    job_latitude = Column(Float)
    job_longitude = Column(Float)
    job_benefits = Column(Text)
    job_google_link = Column(Text)
    job_salary = Column(Text)
    job_min_salary = Column(Float, nullable=True)
    job_max_salary = Column(Float, nullable=True)
    job_salary_period = Column(Text)
    job_onet_soc = Column(String)
    job_onet_job_zone = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
