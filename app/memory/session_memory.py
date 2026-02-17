from typing import Dict, List


class SessionMemory:
    """
    Lightweight session-based memory.
    Stores query history and extracted terms.
    """

    def __init__(self):
        self._queries: Dict[str, List[str]] = {}
        self._terms: Dict[str, List[str]] = {}

    # ---------------------------------------
    # Query Storage
    # ---------------------------------------

    def store_query(self, session_id: str, query: str) -> None:
        self._queries.setdefault(session_id, []).append(query)

    # ---------------------------------------
    # Term Storage
    # ---------------------------------------

    def store_terms(self, session_id: str, terms: List[str]) -> None:
        self._terms.setdefault(session_id, [])

        for term in terms:
            if term not in self._terms[session_id]:
                self._terms[session_id].append(term)

    # ---------------------------------------
    # Retrieval
    # ---------------------------------------

    def get_all_terms(self, session_id: str) -> List[str]:
        return self._terms.get(session_id, [])

    # ---------------------------------------
    # Query Enhancement
    # ---------------------------------------

    def build_enhanced_query(self, session_id: str, current_query: str) -> str:
        terms = self.get_all_terms(session_id)

        if not terms:
            return current_query

        combined = list(set(current_query.split() + terms))
        return " ".join(combined)
