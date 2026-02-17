from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from app.retrieval.bm25_retriever import BM25Retriever
from app.retrieval.vector_retriever import VectorRetriever
from app.retrieval.hybrid_retriever import HybridRetriever


@dataclass
class RouterRetriever:
    bm25: BM25Retriever
    vector: VectorRetriever
    hybrid: HybridRetriever
    default_mode: str = "hybrid"  # bm25|vector|hybrid

    def search(self, query: str, top_k: int, mode: Optional[str] = None) -> List[Dict]:
        mode = (mode or self.default_mode or "hybrid").strip().lower()

        if mode == "bm25":
            return self.bm25.search(query, top_k)
        if mode == "vector":
            return self.vector.search(query, top_k)
        if mode == "hybrid":
            return self.hybrid.search(query, top_k)

        raise ValueError(f"Unknown retrieval mode: {mode}. Use bm25|vector|hybrid.")
