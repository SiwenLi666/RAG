from abc import ABC, abstractmethod
from app.storage.models import Document


class DomainAdapter(ABC):
    """
    Converts raw dataset records into engine Documents.
    Engine should not know any domain-specific structure.
    """

    @abstractmethod
    def normalize(self, raw_record: dict) -> Document:
        pass
