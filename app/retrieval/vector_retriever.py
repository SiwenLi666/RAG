from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Any

from app.retrieval.vector_index import VectorIndex


@dataclass
class VectorRetriever:
    index_memory: Any
    vector_index: VectorIndex

    def search(self, query: str, top_k: int) -> List[Dict]:
        hits = self.vector_index.search(query, top_k)

        # Map id -> doc
        doc_map = self._doc_map_by_id()

        results: List[Dict] = []
        for doc_id, score in hits:
            doc = doc_map.get(doc_id)
            if not doc:
                continue
            results.append(
                {
                    "document": doc,
                    "score": score,
                    "matched_terms": [],  # semantic doesn't do token matches
                }
            )
        return results

    def _doc_map_by_id(self) -> Dict[str, Any]:
        # Robust: support index_memory.documents, index_memory._documents, or iterator
        docs = []
        if hasattr(self.index_memory, "documents"):
            docs = getattr(self.index_memory, "documents") or []
        elif hasattr(self.index_memory, "_documents"):
            docs = getattr(self.index_memory, "_documents") or []
        elif hasattr(self.index_memory, "get_documents"):
            docs = self.index_memory.get_documents()
        elif hasattr(self.index_memory, "all"):
            docs = self.index_memory.all()
        else:
            raise RuntimeError("IndexMemory does not expose documents (documents/_documents/get_documents/all).")

        out: Dict[str, Any] = {}
        for d in docs:
            out[str(getattr(d, "id", None))] = d
        return out
