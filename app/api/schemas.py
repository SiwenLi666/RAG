from __future__ import annotations

from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class SearchRequest(BaseModel):
    query: Optional[str] = None
    ingredients: Optional[List[str]] = None
    session_id: Optional[str] = None

    # NEW: bm25 | vector | hybrid
    retrieval_mode: Optional[str] = None


class ResultItem(BaseModel):
    id: str
    score: float
    metadata: Dict[str, Any]


class SearchResponse(BaseModel):
    results: List[ResultItem]
    total: int
