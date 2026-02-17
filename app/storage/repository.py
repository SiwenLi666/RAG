from typing import List
from app.storage.models import Document


class InMemoryRepository:
    """
    Temporary repository until index layer is added.
    """

    def __init__(self):
        self._documents: List[Document] = []

    def load(self, documents: List[Document]):
        self._documents = documents

    def get_all(self) -> List[Document]:
        return self._documents

    def count(self) -> int:
        return len(self._documents)


# Global singleton (simple for now)
repository = InMemoryRepository()
