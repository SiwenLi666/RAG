from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from app.retrieval.tokenizer import tokenize


@dataclass
class BM25Retriever:
    index_memory: Any

    def __post_init__(self) -> None:
        self._built = False
        self._bm25 = None
        self._docs = []
        self._doc_texts = []
        self._tokenized = []

    def build(self) -> None:
        # Robust access to documents
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

        self._docs = docs
        self._doc_texts = [getattr(d, "text", "") or "" for d in docs]
        self._tokenized = [tokenize(t) for t in self._doc_texts]

        # Minimal BM25 implementation using rank_bm25 if you already had it,
        # else a fallback simple scorer.
        try:
            from rank_bm25 import BM25Okapi  # type: ignore
            self._bm25 = BM25Okapi(self._tokenized)
        except Exception:
            self._bm25 = None

        self._built = True

    def search(self, query: str, top_k: int) -> List[Dict]:
        if not self._built:
            self.build()

        q_tokens = tokenize(query or "")
        if not q_tokens:
            return []

        # rank_bm25 path
        if self._bm25 is not None:
            scores = self._bm25.get_scores(q_tokens)
            # get top_k indices
            top_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
            results: List[Dict] = []
            qset = set(q_tokens)

            for i in top_idx:
                doc = self._docs[i]
                score = float(scores[i])
                doc_tokens = set(self._tokenized[i])
                matched = sorted(list(qset.intersection(doc_tokens)))

                results.append(
                    {"document": doc, "score": score, "matched_terms": matched}
                )
            return results

        # fallback simple scoring (term overlap)
        qset = set(q_tokens)
        scored: List[Tuple[int, float]] = []
        for i, toks in enumerate(self._tokenized):
            dset = set(toks)
            overlap = len(qset.intersection(dset))
            if overlap > 0:
                scored.append((i, float(overlap)))

        scored.sort(key=lambda x: x[1], reverse=True)
        results: List[Dict] = []
        for i, score in scored[:top_k]:
            doc = self._docs[i]
            matched = sorted(list(qset.intersection(set(self._tokenized[i]))))
            results.append({"document": doc, "score": score, "matched_terms": matched})
        return results
