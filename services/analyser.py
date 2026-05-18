# services/analyzer.py
from groq import Groq
from services.cache import get_cached, set_cache
import os
import json

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def call_groq(resume_text: str, job_desc: str) -> dict:
    """
    All Groq logic lives here.
    Moved out of main.py so worker + API can both use it.
    """
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
                Resume: {resume_text}
                Job Description: {job_desc}

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

    raw = response.choices[0].message.content
    clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(clean)


def analyze_resume(resume_text: str, job_desc: str) -> dict:
    """
    Entry point for analysis.
    Checks cache first — only calls Groq on a cache miss.
    """
    # Check cache first
    cached = get_cached(resume_text, job_desc)
    if cached:
        print("✅ Cache HIT — skipping Groq call")
        return cached

    # Cache miss — call Groq
    print("❌ Cache MISS — calling Groq")
    result = call_groq(resume_text, job_desc)

    # Store for next time
    set_cache(resume_text, job_desc, result)

    return result