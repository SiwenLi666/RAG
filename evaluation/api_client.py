import requests
import uuid
import time

API_URL = "http://127.0.0.1:8000/search"

def call_api(query, session_id):
    payload = {
        "query": query,
        "session_id": session_id
    }

    start = time.time()
    response = requests.post(API_URL, json=payload)
    latency = time.time() - start

    response.raise_for_status()
    return response.json(), latency

def generate_session_id():
    return f"eval_{uuid.uuid4()}"
