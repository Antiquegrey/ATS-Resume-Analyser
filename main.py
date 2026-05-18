# main.py
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from database import SessionLocal, Analysis
from services.analyser import analyze_resume
from services.parser import extract_text
import os

load_dotenv()

app = FastAPI()

# --- DB dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Routes ---

@app.get("/")
def home():
    return {"message": "Welcome to ATS Analyser"}


@app.post("/resume/upload")
async def upload_and_analyse(
    file: UploadFile = File(...),
    job_description: str = Form(...),  # job description sent alongside file
    db: Session = Depends(get_db)
):
    """
    Accepts a real PDF/DOCX file + job description.
    Extracts text → runs analysis (with caching) → saves to DB.
    """
    # Validate file type
    allowed = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword"
    ]
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Only PDF or DOCX files allowed")

    # Read file bytes and extract text
    file_bytes = await file.read()
    resume_text = extract_text(file_bytes, file.content_type)

    # Analyze — uses cache if same resume+job was seen before
    result = analyze_resume(resume_text, job_description)

    # Save to DB
    record = Analysis(
        resume_text=resume_text,
        job_description=job_description,
        ats_score=result["ats_score"],
        missing_keywords=str(result["missing_keywords"]),
        improvements=str(result["improvements"])
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "id": record.id,
        "analysis": result
    }


@app.post("/analyse")
def analyse_text(
    resume_text: str = Form(...),
    job_description: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Kept for testing — accepts raw text instead of file.
    Useful for Postman/Swagger testing without needing a real PDF.
    """
    result = analyze_resume(resume_text, job_description)

    record = Analysis(
        resume_text=resume_text,
        job_description=job_description,
        ats_score=result["ats_score"],
        missing_keywords=str(result["missing_keywords"]),
        improvements=str(result["improvements"])
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "id": record.id,
        "analysis": result
    }


@app.get("/analyses")
def get_all(db: Session = Depends(get_db)):
    return db.query(Analysis).all() 