from abc import ABC, abstractmethod
from typing import List
from app.storage.models import Document


class BaseRetriever(ABC):
    """
    Abstract retriever interface.
    """

    @abstractmethod
    def search(self, query: str, top_k: int) -> List[Document]:
        pass
