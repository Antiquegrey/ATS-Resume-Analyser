from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "postgresql://vijay@localhost/ats_analyzer"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True)
    resume_text = Column(String)
    job_description = Column(String)
    ats_score = Column(Integer)
    missing_keywords = Column(String)
    improvements = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


    Base.metadata.create_all(engine)