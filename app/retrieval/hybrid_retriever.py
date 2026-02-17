from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Any, Tuple

from app.retrieval.bm25_retriever import BM25Retriever
from app.retrieval.vector_retriever import VectorRetriever


@dataclass
class HybridRetriever:
    bm25: BM25Retriever
    vector: VectorRetriever
    bm25_weight: float = 0.6
    vector_weight: float = 0.4

    def search(self, query: str, top_k: int) -> List[Dict]:
        # Pull more candidates to make hybrid meaningful
        widen = max(top_k * 5, top_k)

        bm25_hits = self.bm25.search(query, widen)   # list[{document,score,matched_terms}]
        vec_hits = self.vector.search(query, widen)  # list[{document,score,matched_terms=[]}]

        # Normalize BM25 by max
        bm25_max = max([h["score"] for h in bm25_hits], default=0.0) or 1.0

        # Vector scores are cosine-ish; map to [0,1]
        def vec_norm(s: float) -> float:
            return (s + 1.0) / 2.0

        # Merge by doc.id
        merged: Dict[str, Dict] = {}

        for h in bm25_hits:
            doc = h["document"]
            doc_id = str(doc.id)
            merged.setdefault(
                doc_id,
                {"document": doc, "bm25": 0.0, "vec": 0.0, "matched_terms": set()},
            )
            merged[doc_id]["bm25"] = float(h["score"]) / bm25_max
            for t in (h.get("matched_terms") or []):
                merged[doc_id]["matched_terms"].add(t)

        for h in vec_hits:
            doc = h["document"]
            doc_id = str(doc.id)
            merged.setdefault(
                doc_id,
                {"document": doc, "bm25": 0.0, "vec": 0.0, "matched_terms": set()},
            )
            merged[doc_id]["vec"] = vec_norm(float(h["score"]))

        # Final scoring
        out: List[Dict] = []
        for doc_id, row in merged.items():
            final = self.bm25_weight * row["bm25"] + self.vector_weight * row["vec"]
            out.append(
                {
                    "document": row["document"],
                    "score": float(final),
                    "matched_terms": sorted(list(row["matched_terms"])),
                }
            )

        out.sort(key=lambda x: x["score"], reverse=True)
        return out[:top_k]
