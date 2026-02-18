from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from app.retrieval.bm25_retriever import BM25Retriever
from app.retrieval.vector_retriever import VectorRetriever
from app.retrieval.hybrid_retriever import HybridRetriever


_ALLOWED_MODES = {"bm25", "vector", "hybrid"}


@dataclass
class RouterRetriever:
    bm25: BM25Retriever
    vector: VectorRetriever
    hybrid: HybridRetriever
    default_mode: str = field(default="hybrid")

    def __post_init__(self):
        mode = (self.default_mode or "hybrid").strip().lower()
        if mode not in _ALLOWED_MODES:
            raise ValueError(
                f"Invalid default_mode '{self.default_mode}'. "
                f"Allowed: bm25 | vector | hybrid."
            )
        self.default_mode = mode

    def search(
        self,
        query: str,
        top_k: int,
        mode: Optional[str] = None
    ) -> List[Dict]:

        selected_mode = (mode or self.default_mode).strip().lower()

        if selected_mode not in _ALLOWED_MODES:
            raise ValueError(
                f"Unknown retrieval mode: {selected_mode}. "
                f"Use bm25 | vector | hybrid."
            )

        if selected_mode == "bm25":
            return self.bm25.search(query, top_k)

        if selected_mode == "vector":
            return self.vector.search(query, top_k)

        # hybrid
        return self.hybrid.search(query, top_k)
