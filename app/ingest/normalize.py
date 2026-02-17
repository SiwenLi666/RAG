from typing import List
from app.storage.models import Document
from app.domain.base import DomainAdapter


def normalize_documents(raw_data: List[dict], adapter: DomainAdapter) -> List[Document]:

    documents = []

    for raw in raw_data:
        try:
            document = adapter.normalize(raw)
            documents.append(document)
        except Exception:
            continue

    return documents
