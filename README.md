
# Recipe Search API
### RAG + Hybrid Retrieval + Multilingual Support

A REST-based recipe search API built with:

- FastAPI
- BM25 keyword retrieval
- FAISS semantic vector search
- Hybrid ranking (BM25 + semantic)
- Ollama local LLM integration
- Strict translation layer for multilingual support

---

## Overview

This project fulfills the job test requirement:

> Build a REST-based API that can search recipes given ingredients or a description.

In addition, it includes:

- Multilingual support
- Semantic search
- Hybrid ranking
- Modular architecture

---

## Quick Start

### 1) Install dependencies

Create and activate virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

Install requirements:

```bash
pip install -r requirements.txt
pip install faiss-cpu
```

---

### 2) Install and run Ollama

Download Ollama from:
https://ollama.com

Start Ollama:

```bash
ollama serve
```

Pull required models:

```bash
ollama pull nomic-embed-text
ollama pull gemma3:4b
```

---

### 3) Start the API

```bash
uvicorn app.main:app --reload
```

Swagger UI:

http://127.0.0.1:8000/docs

---
## How to Use

---

### Basic Search

**Swagger (Raw JSON for /docs)**

```json
{
  "query": "chicken coconut garlic",
  "session_id": "user1"
}
```

**curl (Windows CMD)**

```bash
curl -X POST "http://127.0.0.1:8000/search" ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"chicken coconut garlic\",\"session_id\":\"user1\"}"
```

---

### Multilingual Search (Swedish)

**Swagger**

```json
{
  "query": "kyckling med kokos och vitlök",
  "session_id": "user1"
}
```

**curl**

```bash
curl -X POST "http://127.0.0.1:8000/search" ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"kyckling med kokos och vitlök\",\"session_id\":\"user1\"}"
```

---

### Ingredient-Driven Search

**Swagger**

```json
{
  "query": "ingredients: chicken, coconut milk, garlic",
  "session_id": "user1"
}
```

**curl**

```bash
curl -X POST "http://127.0.0.1:8000/search" ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"ingredients: chicken, coconut milk, garlic\",\"session_id\":\"user1\"}"
```

The system detects ingredient-style queries and routes them through the hybrid retrieval pipeline (BM25 + vector similarity).

---

### Multi-Step / Contextual Search (Session Memory)

Use the same session_id for follow-up queries.

#### Step 1 — Initial Query

**Swagger**

```json
{
  "query": "coconut chicken",
  "session_id": "demo_session"
}
```

**curl**

```bash
curl -X POST "http://127.0.0.1:8000/search" ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"coconut chicken\",\"session_id\":\"demo_session\"}"

```

---

#### Step 2 — Follow-up Refinement

**Swagger**

```json
{
  "query": "add garlic",
  "session_id": "demo_session"
}

```

**curl**

```bash
curl -X POST "http://127.0.0.1:8000/search" ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"add garlic\",\"session_id\":\"demo_session\"}"

```

The system uses session memory to refine the search context and dynamically re-route retrieval.


---

## Dataset

Input file:

data/20170107-061401-recipeitems.json

---

## Vector Cache (Readable files only)

Stored under:

data/
 ├── embeddings.npy
 ├── faiss.index
 └── id_map.json

Delete these files to force a rebuild.

---

## Project Structure

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

---

## Architecture Summary

1. Incoming request
2. Translation layer (Ollama)
3. Session memory enhancement
4. Hybrid retrieval (BM25 + FAISS)
5. Ranked results returned

---

## Technologies Used

- FastAPI
- FAISS (CPU)
- Ollama
- nomic-embed-text (embeddings)
- gemma3:4b (translator)
- Python 3.13

---

## Notes

- Semantic index is cached under /data
- Delete cached files to rebuild embeddings
- Translation layer is strictly limited to translation only
- Designed for extension into full RAG / agentic system
