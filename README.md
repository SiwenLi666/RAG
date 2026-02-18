
Recipe Search API
RAG + Hybrid Retrieval + Multilingual Support

Overview
This project implements a REST-based recipe search API built with:
- FastAPI
- BM25 keyword retrieval
- FAISS semantic vector search
- Hybrid ranking (BM25 + semantic)
- Ollama local LLM integration
- Multilingual translation layer

The project fulfills the job requirement:
"Build a REST-based API that can search recipes given ingredients or a description."

In addition, it includes:
- Multilingual support
- Semantic search
- Hybrid ranking
- Modular architecture
- Internal evaluation framework


Quick Start

1) Install Dependencies

python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install faiss-cpu

2) Install and Run Ollama

Download from:
https://ollama.com

Start Ollama:
ollama serve

Pull required models:
ollama pull nomic-embed-text
ollama pull gemma3:4b

3) Start the API

uvicorn app.main:app --reload

Swagger UI:
http://127.0.0.1:8000/docs


How to Use

Basic Search (Swagger JSON):
{
  "query": "chicken coconut garlic",
  "session_id": "user1"
}

Multilingual Search Example:
{
  "query": "kyckling med kokos och vitlök",
  "session_id": "user1"
}

Multi-Step Contextual Search:
Step 1:
{
  "query": "coconut chicken",
  "session_id": "demo_session"
}

Step 2:
{
  "query": "add garlic",
  "session_id": "demo_session"
}

The same session_id allows contextual refinement.


Dataset

data/20170107-061401-recipeitems.json


Vector Cache

Stored under data/:
- embeddings.npy
- faiss.index
- id_map.json

Delete these files to rebuild embeddings.


Project Structure

app/
 ├── ai/
 ├── api/
 ├── core/
 ├── domain/
 ├── index/
 ├── ingest/
 ├── memory/
 ├── retrieval/
 └── main.py


Architecture Summary

1. Incoming request
2. Translation layer (Ollama)
3. Session memory enhancement
4. Hybrid retrieval (BM25 + FAISS)
5. Ranked results returned


Evaluation Framework

Generate Tests:
python evaluation/generate_tests.py

Run Evaluation:
python evaluation/runner.py

Evaluation Strategy:

1) Immediate Success:
If expected recipe ID appears in Top-5 results at any refinement step → Score = 100

2) Ingredient Overlap Scoring:
If no ID match is found:
- Compare query tokens
- Compare matched terms from best result
- Score proportional to overlap ratio

This simulates realistic interactive refinement instead of strict one-shot testing.


Technologies Used

- FastAPI
- FAISS (CPU)
- BM25
- Ollama
- nomic-embed-text
- gemma3:4b
- Python 3.13


Notes

- Semantic index is cached under /data
- Delete cache to rebuild embeddings
- Translation layer is restricted to translation only
- Architecture is designed for future extension into full RAG / agentic system
