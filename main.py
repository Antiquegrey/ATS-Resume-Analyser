# main.py

from fastapi import FastAPI, Depends
from pydantic import BaseModel
from groq import Groq
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from database import SessionLocal, Analysis
import os
import json

load_dotenv()

app = FastAPI()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class ResumeInput(BaseModel):
    resume_text: str
    job_description: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"message": "welcome to ats analyser"}

@app.post("/analyse")
def analyse(data: ResumeInput, db: Session = Depends(get_db)):
    response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "system",
            "content": "You are an ATS resume analyzer. You ONLY respond with valid raw JSON. No markdown, no explanation, no code blocks."
        },
        {
            "role": "user",
            "content": f"""
            Resume: {data.resume_text}
            Job Description: {data.job_description}

            Return exactly this JSON structure:
            {{
                "ats_score": <number out of 100>,
                "missing_keywords": ["keyword1", "keyword2", "keyword3"],
                "improvements": ["improvement1", "improvement2", "improvement3"]
            }}
            """
        }
    ]
)
        
       
    
    result_text = response.choices[0].message.content
    print("RAW RESPONSE:", repr(result_text))  # add this line
    clean_text = result_text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    parsed = json.loads(clean_text)
    record = Analysis(
        resume_text=data.resume_text,
        job_description=data.job_description,
        ats_score=parsed["ats_score"],
        missing_keywords=str(parsed["missing_keywords"]),
        improvements=str(parsed["improvements"])
    )   
    db.add(record)
    db.commit()
    db.refresh(record)

    return {"id": record.id, "analysis": result_text}

@app.get("/analyses")
def get_all(db: Session = Depends(get_db)):
    return db.query(Analysis).all()