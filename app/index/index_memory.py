from typing import List
from app.storage.models import Document


class IndexMemory:

    def __init__(self):
        self._documents: List[Document] = []

    def load_documents(self, documents: List[Document]) -> None:
        """
        Load normalized documents into memory.
        """
        self._documents = documents

    def get_all_documents(self) -> List[Document]:
        """
        Return all documents stored in memory.
        """
        return self._documents

    def __len__(self):
        return len(self._documents)
