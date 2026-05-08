from fastapi import FastAPI
from pydantic import BaseModel
from groq import Groq
import json
from dotenv import load_dotenv

app=FastAPI()

@app.get("/")
def home():
    return {"message": "welcome to ats analyser"}



class ResumeInput(BaseModel):
    resume_text: str
    job_description: str


import os

load_dotenv()
client = os.getenv("GROQ_API_KEY")

@app.post("/analyse")
def analyse(data: ResumeInput):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": f"""
            You are an ATS resume analyzer.
            Resume: {data.resume_text}
            Job Description: {data.job_description}
            Give me:
            1. ATS match score out of 100
            2. Top 3 missing keywords
            3. Top 3 specific improvements
            """
        }]
    )
    return {"analysis": response.choices[0].message.content}