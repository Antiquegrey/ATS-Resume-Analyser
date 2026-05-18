# services/cache.py
import redis
import hashlib
import json

# connect to Redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def make_key(resume_text: str, job_desc: str) -> str:
    """
    Creates a unique fingerprint from resume + job.
    Same inputs = same key = cache hit.
    """
    combined = f"{resume_text}{job_desc}"
    return "ats:" + hashlib.md5(combined.encode()).hexdigest()


def get_cached(resume_text: str, job_desc: str):
    key = make_key(resume_text, job_desc)
    result = r.get(key)
    
    if result:
        print("✅ Cache HIT — skipping Groq call")
        return json.loads(result)
    
    print("❌ Cache MISS — calling Groq")
    return None


def set_cache(resume_text: str, job_desc: str, result: dict):
    key = make_key(resume_text, job_desc)
    r.setex(
        key,        # the key
        3600,       # TTL — expires after 1 hour
        json.dumps(result)  # Redis only stores strings, so convert dict
    )