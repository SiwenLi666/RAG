from __future__ import annotations

from typing import List
from app.api.schemas import SearchRequest, ResultItem
import app.core.container as container
from app.core.config import TOP_K


class SearchService:

    def search(self, request: SearchRequest) -> List[ResultItem]:
        query_text = self._build_query_text(request)
        if not query_text:
            return []

        session_id = request.session_id or "default"

        # 1) translate (translator must be strict translator; you required fail-fast)
        translated_query = container.translator.translate(query_text)

        # 2) store in memory
        container.memory.store_query(session_id, translated_query)

        # automatically treat query words as terms
        terms = translated_query.split()
        container.memory.store_terms(session_id, terms)



        # 3) enhanced query
        enhanced_query = container.memory.build_enhanced_query(session_id, translated_query)

        # 4) retrieval mode switch (optional override)
        mode = None
        if request.retrieval_mode:
            mode = request.retrieval_mode.strip().lower()

        # Router will fall back to its default_mode if mode is None
        search_results = container.retriever.search(enhanced_query, TOP_K, mode=mode)


        results: List[ResultItem] = []
        for item in search_results:
            doc = item["document"]
            score = item["score"]
            matched_terms = item.get("matched_terms", [])

            results.append(
                ResultItem(
                    id=doc.id,
                    score=round(float(score), 4),
                    metadata={
                        "name": doc.metadata.get("name"),
                        "matched_terms": matched_terms,
                        "enhanced_query": enhanced_query,
                        "preview": (doc.text or "")[:200],
                        "retrieval_mode": mode,
                    },
                )
            )

        return results

    def _build_query_text(self, request: SearchRequest) -> str:
        if request.query:
            return request.query.strip()
        if request.ingredients:
            return " ".join(request.ingredients)
        return ""
