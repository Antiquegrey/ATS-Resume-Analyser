# database.py — make sure it looks exactly like this

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
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

# ← this must be OUTSIDE the class
Base.metadata.create_all(engine)